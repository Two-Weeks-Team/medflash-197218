import uuid
import random
from fastapi import APIRouter, HTTPException, Depends, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from models import SessionLocal, User, Deck, Card, CardProgress
from ai_service import generate_card, recommend_decks

router = APIRouter()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Simple auth stub – in a real app replace with JWT verification
def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")
    token = auth.split(" ")[1]
    # Dummy lookup: token is user id for demo purposes
    user = db.query(User).filter(User.id == token).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return user

# Pydantic schemas
class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=20)
    email: str = Field(..., max_length=100)
    password: str = Field(..., min_length=8)

class RegisterResponse(BaseModel):
    user_id: str
    username: str
    email: str
    token: str

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    user_id: str
    username: str
    token: str

class DeckCreateRequest(BaseModel):
    title: str = Field(..., min_length=3, max_length=50)
    description: str | None = None
    category: str | None = None

class DeckResponse(BaseModel):
    deck_id: str
    title: str
    description: str | None = None
    category: str | None = None

class CardCreateRequest(BaseModel):
    deck_id: str
    term: str
    definition: str

class CardResponse(BaseModel):
    card_id: str
    term: str
    definition: str

class StudyAnswerRequest(BaseModel):
    difficulty: str = Field(..., regex="^(easy|medium|hard)$")

class StudyCard(BaseModel):
    term: str
    definition: str

class StudyStartResponse(BaseModel):
    session_id: str
    card: StudyCard

class StudyNextResponse(BaseModel):
    next_card: StudyCard

class ProgressResponse(BaseModel):
    total_cards: int
    correct_answers: int
    progress_percent: float

class GenerateCardRequest(BaseModel):
    term: str

# In‑memory study sessions (demo only)
study_sessions: dict[str, list[Card]] = {}

# Auth endpoints
@router.post("/auth/register", response_model=RegisterResponse)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    # Simple uniqueness checks
    if db.query(User).filter(User.username == req.username).first():
        raise HTTPException(status_code=400, detail="Username already exists")
    if db.query(User).filter(User.email == req.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    user_id = str(uuid.uuid4())
    # Very naive password hash (DO NOT use in prod)
    pwd_hash = req.password.encode("utf-8").hex()
    user = User(id=user_id, username=req.username, email=req.email, password_hash=pwd_hash)
    db.add(user)
    db.commit()
    token = user_id  # token stub
    return RegisterResponse(user_id=user_id, username=req.username, email=req.email, token=token)

@router.post("/auth/login", response_model=LoginResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == req.username).first()
    if not user or user.password_hash != req.password.encode("utf-8").hex():
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = user.id
    return LoginResponse(user_id=user.id, username=user.username, token=token)

# Deck endpoints
@router.get("/decks", response_model=list[DeckResponse])
def list_decks(db: Session = Depends(get_db)):
    decks = db.query(Deck).all()
    return [DeckResponse(deck_id=d.id, title=d.title, description=d.description, category=d.category) for d in decks]

@router.post("/decks", response_model=DeckResponse)
def create_deck(req: DeckCreateRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    deck_id = str(uuid.uuid4())
    deck = Deck(id=deck_id, title=req.title, description=req.description, category=req.category, user_id=user.id)
    db.add(deck)
    db.commit()
    return DeckResponse(deck_id=deck_id, title=req.title, description=req.description, category=req.category)

@router.get("/decks/{deck_id}/cards", response_model=list[CardResponse])
def get_deck_cards(deck_id: str, db: Session = Depends(get_db)):
    cards = db.query(Card).filter(Card.deck_id == deck_id).all()
    return [CardResponse(card_id=c.id, term=c.term, definition=c.definition) for c in cards]

# Card endpoint
@router.post("/cards", response_model=CardResponse)
def create_card(req: CardCreateRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    deck = db.query(Deck).filter(Deck.id == req.deck_id, Deck.user_id == user.id).first()
    if not deck:
        raise HTTPException(status_code=404, detail="Deck not found or not owned")
    card_id = str(uuid.uuid4())
    card = Card(id=card_id, deck_id=req.deck_id, term=req.term, definition=req.definition)
    db.add(card)
    db.commit()
    return CardResponse(card_id=card_id, term=req.term, definition=req.definition)

# Study session start
@router.get("/study", response_model=StudyStartResponse)
def start_study(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Pull a random card from any of the user's decks
    cards = db.query(Card).join(Deck).filter(Deck.user_id == user.id).all()
    if not cards:
        raise HTTPException(status_code=404, detail="No cards available for study")
    random.shuffle(cards)
    session_id = str(uuid.uuid4())
    study_sessions[session_id] = cards
    first = cards.pop()
    return StudyStartResponse(session_id=session_id, card=StudyCard(term=first.term, definition=first.definition))

# Submit answer
@router.post("/study/{session_id}/answer", response_model=StudyNextResponse)
def submit_answer(session_id: str, req: StudyAnswerRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if session_id not in study_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    # In a real app, update CardProgress based on difficulty here
    remaining = study_sessions[session_id]
    if not remaining:
        # Session completed – clean up
        del study_sessions[session_id]
        raise HTTPException(status_code=200, detail="Study session completed")
    next_card = remaining.pop()
    return StudyNextResponse(next_card=StudyCard(term=next_card.term, definition=next_card.definition))

# Progress endpoint (simple summary)
@router.get("/progress", response_model=ProgressResponse)
def get_progress(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    total = db.query(Card).join(Deck).filter(Deck.user_id == user.id).count()
    correct = db.query(CardProgress).filter(CardProgress.user_id == user.id, CardProgress.correct_answers_count > 0).count()
    percent = (correct / total * 100) if total else 0.0
    return ProgressResponse(total_cards=total, correct_answers=correct, progress_percent=percent)

# AI powered endpoints
@router.post("/ai/generate-card")
async def ai_generate_card(req: GenerateCardRequest, user: User = Depends(get_current_user)):
    result = await generate_card(req.term)
    return JSONResponse(content=result)

@router.post("/ai/recommend-decks")
async def ai_recommend_decks(user: User = Depends(get_current_user)):
    result = await recommend_decks()
    return JSONResponse(content=result)
