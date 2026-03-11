import os
from sqlalchemy import (
    Column,
    String,
    Integer,
    DateTime,
    ForeignKey,
    Text,
    func,
    create_engine,
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

# Resolve DATABASE_URL with auto‑fixes
raw_url = os.getenv(
    "DATABASE_URL", os.getenv("POSTGRES_URL", "sqlite:///./app.db")
)
if raw_url.startswith("postgresql+asyncpg://"):
    raw_url = raw_url.replace("postgresql+asyncpg://", "postgresql+psycopg://")
elif raw_url.startswith("postgres://"):
    raw_url = raw_url.replace("postgres://", "postgresql+psycopg://")

# Add SSL args for non‑localhost Postgres
connect_args = {}
if not raw_url.startswith("sqlite") and "localhost" not in raw_url and "127.0.0.1" not in raw_url:
    connect_args["sslmode"] = "require"

engine = create_engine(raw_url, connect_args=connect_args, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

Base = declarative_base()

TABLE_PREFIX = "medflash_197218_"

class User(Base):
    __tablename__ = f"{TABLE_PREFIX}users"
    id = Column(String, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    decks = relationship("Deck", back_populates="owner")
    progress = relationship("CardProgress", back_populates="user")

class Deck(Base):
    __tablename__ = f"{TABLE_PREFIX}decks"
    id = Column(String, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    category = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    user_id = Column(String, ForeignKey(f"{TABLE_PREFIX}users.id", ondelete="CASCADE"))
    owner = relationship("User", back_populates="decks")
    cards = relationship("Card", back_populates="deck", cascade="all, delete-orphan")

class Card(Base):
    __tablename__ = f"{TABLE_PREFIX}cards"
    id = Column(String, primary_key=True, index=True)
    deck_id = Column(String, ForeignKey(f"{TABLE_PREFIX}decks.id", ondelete="CASCADE"))
    term = Column(Text, nullable=False)
    definition = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    deck = relationship("Deck", back_populates="cards")
    progresses = relationship("CardProgress", back_populates="card", cascade="all, delete-orphan")

class CardProgress(Base):
    __tablename__ = f"{TABLE_PREFIX}card_progress"
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey(f"{TABLE_PREFIX}users.id", ondelete="CASCADE"))
    card_id = Column(String, ForeignKey(f"{TABLE_PREFIX}cards.id", ondelete="CASCADE"))
    next_review_at = Column(DateTime(timezone=True))
    difficulty_level = Column(Integer, default=1)
    correct_answers_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    user = relationship("User", back_populates="progress")
    card = relationship("Card", back_populates="progresses")
