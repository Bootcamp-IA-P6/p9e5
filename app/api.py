"""
api.py - FastAPI backend para la app React de detección de hate speech.
Carga el modelo clásico (TF-IDF + RandomForest) desde src/ y expone:
  POST /analyze       → analiza un solo comentario
  POST /analyze-url   → obtiene comentarios de YouTube y los analiza en masa
"""

import os
import math
import joblib
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys

# ── path setup ────────────────────────────────────────────────────────────────
APP_DIR  = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(APP_DIR)
sys.path.insert(0, APP_DIR)

from utils import clean_text, classify_toxicity_type

# ── load model artifacts ──────────────────────────────────────────────────────
MODEL_PATH      = os.path.join(BASE_DIR, "src", "model.joblib")
VECTORIZER_PATH = os.path.join(BASE_DIR, "src", "vectorizer.joblib")

model      = joblib.load(MODEL_PATH)
vectorizer = joblib.load(VECTORIZER_PATH)

# ── FastAPI app ───────────────────────────────────────────────────────────────
app = FastAPI(title="Hate Speech Detector API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── helpers ───────────────────────────────────────────────────────────────────
def _predict_one(text: str) -> dict:
    cleaned = clean_text(text)
    X = vectorizer.transform([cleaned])
    label = int(model.predict(X)[0])
    if hasattr(model, "predict_proba"):
        proba = model.predict_proba(X)[0]
        confidence = float(proba[1] if label == 1 else proba[0])
    else:
        score = model.decision_function(X)[0]
        confidence = float(
            1 / (1 + math.exp(-score)) if label == 1 else 1 / (1 + math.exp(score))
        )
    toxicity_type = classify_toxicity_type(text) if label == 1 else "lenguaje cotidiano"
    return {
        "toxic":          bool(label),
        "confidence_pct": round(confidence * 100),
        "toxicity_type":  toxicity_type,
        "cleaned_text":   cleaned,
    }


# ── schemas ───────────────────────────────────────────────────────────────────
class TextRequest(BaseModel):
    text: str

class UrlRequest(BaseModel):
    url: str
    limit: int = 50


# ── endpoints ─────────────────────────────────────────────────────────────────
@app.get("/")
def root():
    return {"status": "ok", "message": "Hate Speech Detector API"}


@app.post("/analyze")
def analyze(req: TextRequest):
    return _predict_one(req.text)


@app.post("/analyze-url")
def analyze_url(req: UrlRequest):
    comments = _fetch_youtube_comments(req.url, req.limit)
    if not comments:
        from fastapi import HTTPException
        raise HTTPException(status_code=422, detail="No se pudieron obtener comentarios del vídeo. Comprueba la URL y que el vídeo tenga comentarios habilitados.")

    results = []
    for c in comments:
        pred = _predict_one(c)
        results.append({
            "text":           c,
            "toxic":          pred["toxic"],
            "toxicity_type":  pred["toxicity_type"],
            "confidence_pct": pred["confidence_pct"],
        })

    toxic_count = sum(1 for r in results if r["toxic"])
    safe_count  = len(results) - toxic_count
    toxic_pct   = round(toxic_count / len(results) * 100) if results else 0

    return {
        "total":       len(results),
        "toxic_count": toxic_count,
        "safe_count":  safe_count,
        "toxic_pct":   toxic_pct,
        "comments":    results,
    }


# ── YouTube comment fetcher ───────────────────────────────────────────────────
def _fetch_youtube_comments(url: str, limit: int) -> list[str]:
    """
    Intenta obtener comentarios reales de YouTube usando youtube-comment-downloader.
    Si no está disponible, usa yt-dlp como fallback.
    """
    try:
        from youtube_comment_downloader import YoutubeCommentDownloader, SORT_BY_POPULAR
        downloader = YoutubeCommentDownloader()
        comments = []
        for comment in downloader.get_comments_from_url(url, sort_by=SORT_BY_POPULAR):
            text = comment.get("text", "").strip()
            if text:
                comments.append(text)
            if len(comments) >= limit:
                break
        return comments
    except Exception:
        pass

    # fallback: yt-dlp
    try:
        import yt_dlp
        import json
        ydl_opts = {
            "quiet":           True,
            "extract_flat":    False,
            "getcomments":     True,
            "writecomments":   True,
            "skip_download":   True,
            "extractor_args":  {"youtube": {"max_comments": [str(limit)]}},
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
        raw = info.get("comments") or []
        return [c.get("text", "").strip() for c in raw[:limit] if c.get("text", "").strip()]
    except Exception:
        pass

    return []
