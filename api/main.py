"""
api/main.py - FastAPI backend para el detector de hate speech.
Expone los modelos ML entrenados via REST API.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib, os, math, sys
from typing import List

# ── Allow imports from app/utils.py ─────────────────────────────────────────
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "app"))
from utils import clean_text, classify_toxicity_type  # noqa: E402

# ── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR        = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH      = os.path.join(BASE_DIR, "src", "model.joblib")
VECTORIZER_PATH = os.path.join(BASE_DIR, "src", "vectorizer.joblib")

# ── Load models once at startup ──────────────────────────────────────────────
model      = joblib.load(MODEL_PATH)
vectorizer = joblib.load(VECTORIZER_PATH)

# ── App ──────────────────────────────────────────────────────────────────────
app = FastAPI(title="Hate Speech Detector API", version="1.0.0")

# CORS: permite localhost en dev + cualquier dominio Vercel/Render en producción
_extra = os.getenv("ALLOWED_ORIGINS", "")
_origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    *[o.strip() for o in _extra.split(",") if o.strip()],
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_origin_regex=r"https://.*\.vercel\.app",  # todas las preview URLs de Vercel
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Schemas ──────────────────────────────────────────────────────────────────
class AnalyzeRequest(BaseModel):
    text: str


class AnalyzeResponse(BaseModel):
    label: int          # 0 = seguro, 1 = tóxico
    toxic: bool
    confidence: float   # 0.0 – 1.0
    confidence_pct: int # 0 – 100
    toxicity_type: str  # machista | racista | sexual | insulto | homofobo | politico | lenguaje cotidiano
    cleaned_text: str


class UrlRequest(BaseModel):
    url: str
    limit: int = 50


class CommentResult(BaseModel):
    text: str
    label: int
    toxic: bool
    confidence_pct: int
    toxicity_type: str


class UrlAnalysisResponse(BaseModel):
    url: str
    total: int
    toxic_count: int
    safe_count: int
    toxic_pct: int
    comments: List[CommentResult]


# ── Helper ───────────────────────────────────────────────────────────────────
def _predict_one(text: str):
    cleaned   = clean_text(text)
    X         = vectorizer.transform([cleaned])
    label     = int(model.predict(X)[0])
    if hasattr(model, "predict_proba"):
        proba      = model.predict_proba(X)[0]
        confidence = float(proba[1] if label == 1 else proba[0])
    else:
        score      = model.decision_function(X)[0]
        confidence = float(
            1 / (1 + math.exp(-score)) if label == 1 else 1 / (1 + math.exp(score))
        )
    return label, confidence, cleaned


# ── Routes ───────────────────────────────────────────────────────────────────
@app.get("/")
def root():
    return {"status": "ok", "message": "Hate Speech Detector API"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(req: AnalyzeRequest):
    text = req.text.strip()
    if not text:
        return AnalyzeResponse(
            label=0, toxic=False, confidence=0.0, confidence_pct=0,
            toxicity_type="lenguaje cotidiano", cleaned_text="",
        )

    label, confidence, cleaned = _predict_one(text)
    tox_type = classify_toxicity_type(text)

    return AnalyzeResponse(
        label=label,
        toxic=label == 1,
        confidence=round(confidence, 4),
        confidence_pct=int(confidence * 100),
        toxicity_type=tox_type,
        cleaned_text=cleaned,
    )


@app.post("/analyze-url", response_model=UrlAnalysisResponse)
def analyze_url(req: UrlRequest):
    """Descarga comentarios de un video de YouTube y los clasifica (Nivel Medio)."""
    try:
        from youtube_comment_downloader import YoutubeCommentDownloader, SORT_BY_RECENT
    except ImportError:
        raise HTTPException(status_code=500, detail="youtube-comment-downloader no instalado")

    url   = req.url.strip()
    limit = max(1, min(req.limit, 200))

    try:
        downloader   = YoutubeCommentDownloader()
        generator    = downloader.get_comments_from_url(url, sort_by=SORT_BY_RECENT)
        raw_comments = []
        for c in generator:
            raw_comments.append(c.get("text", ""))
            if len(raw_comments) >= limit:
                break
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"No se pudieron obtener comentarios: {str(e)}")

    if not raw_comments:
        raise HTTPException(status_code=404, detail="No se encontraron comentarios en este video.")

    results = []
    for text in raw_comments:
        if not text.strip():
            continue
        label, confidence, _ = _predict_one(text)
        tox_type = classify_toxicity_type(text)
        results.append(CommentResult(
            text=text[:200],
            label=label,
            toxic=label == 1,
            confidence_pct=int(confidence * 100),
            toxicity_type=tox_type,
        ))

    toxic_count = sum(1 for r in results if r.toxic)
    total       = len(results)

    return UrlAnalysisResponse(
        url=url,
        total=total,
        toxic_count=toxic_count,
        safe_count=total - toxic_count,
        toxic_pct=int(toxic_count / total * 100) if total else 0,
        comments=results,
    )
