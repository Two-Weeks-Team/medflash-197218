import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from routes import router
from models import engine, Base

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

app = FastAPI(title="MedFlash API", version="0.1.0")

@app.middleware("http")
async def normalize_api_prefix(request: Request, call_next):
    if request.scope.get("path", "").startswith("/api/"):
        request.scope["path"] = request.scope["path"][4:] or "/"
    return await call_next(request)

app.include_router(router)

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.get("/", response_class=HTMLResponse)
async def root():
    html = """
    <html>
      <head>
        <title>MedFlash API</title>
        <style>
          body {background-color:#1a202c;color:#e2e8f0;font-family:Arial,Helvetica,sans-serif;margin:0;padding:2rem;}
          h1 {color:#63b3ed;}
          a {color:#90cdf4;}
          .endpoint {margin-bottom:1rem;}
          .endpoint code {background:#2d3748;padding:2px 4px;border-radius:4px;}
        </style>
      </head>
      <body>
        <h1>MedFlash API</h1>
        <p>Effortlessly master medical terminology with specialized spaced repetition and expert‑endorsed content.</p>
        <h2>Available Endpoints</h2>
        <div class="endpoint"><code>GET /health</code> – health check</div>
        <div class="endpoint"><code>GET /decks</code> – list public decks</div>
        <div class="endpoint"><code>POST /decks</code> – create a new deck</div>
        <div class="endpoint"><code>GET /decks/{deck_id}/cards</code> – list cards in a deck</div>
        <div class="endpoint"><code>POST /cards</code> – add a card to a deck</div>
        <div class="endpoint"><code>GET /study</code> – start a study session</div>
        <div class="endpoint"><code>POST /study/{session_id}/answer</code> – submit answer & get next card</div>
        <div class="endpoint"><code>GET /progress</code> – retrieve user progress</div>
        <div class="endpoint"><code>POST /ai/generate-card</code> – AI‑generated flashcard</div>
        <div class="endpoint"><code>POST /ai/recommend-decks</code> – AI‑based deck recommendations</div>
        <h2>Documentation</h2>
        <p><a href="/docs">Swagger UI</a> | <a href="/redoc">ReDoc</a></p>
        <h2>Tech Stack</h2>
        <ul>
          <li>FastAPI 0.115.0</li>
          <li>PostgreSQL via SQLAlchemy 2.0.35</li>
          <li>DigitalOcean Serverless Inference (openai‑gpt‑oss‑120b)</li>
          <li>Python 3.12+</li>
        </ul>
      </body>
    </html>
    """
    return HTMLResponse(content=html, status_code=200)
