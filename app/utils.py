"""
utils.py - Funciones de preprocesamiento para la app Streamlit.
Deben ser idénticas a las usadas durante el entrenamiento del modelo.
"""

import os
import re
import joblib
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# Descargar recursos necesarios (solo la primera vez)
for resource in ["stopwords", "wordnet", "omw-1.4"]:
    try:
        nltk.data.find(f"corpora/{resource}")
    except LookupError:
        nltk.download(resource, quiet=True)

STOP_WORDS = set(stopwords.words("english"))
lemmatizer = WordNetLemmatizer()

# ── ML-based type classifier ───────────────────────────────────────────────────
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_TYPE_MODEL_PATH = os.path.join(_BASE_DIR, "models", "type_classifier.pkl")
_type_pipeline = None

def _load_type_pipeline():
    global _type_pipeline
    if _type_pipeline is None and os.path.exists(_TYPE_MODEL_PATH):
        _type_pipeline = joblib.load(_TYPE_MODEL_PATH)
    return _type_pipeline


def clean_text(text: str) -> str:
    """
    Limpia y normaliza el texto de entrada.
    Pipeline: minúsculas → sin URLs → sin menciones → sin HTML
              → solo letras → sin stopwords → lematización.
    """
    if not isinstance(text, str):
        return ""

    # Minúsculas
    text = text.lower()
    # Eliminar URLs
    text = re.sub(r"http\S+|www\.\S+", "", text)
    # Eliminar menciones @usuario
    text = re.sub(r"@\w+", "", text)
    # Eliminar etiquetas HTML
    text = re.sub(r"<.*?>", "", text)
    # Eliminar caracteres especiales y números, mantener solo letras y espacios
    text = re.sub(r"[^a-z\s]", "", text)
    # Eliminar espacios múltiples
    text = re.sub(r"\s+", " ", text).strip()

    # Tokenización simple, eliminar stopwords y lematizar
    tokens = [
        lemmatizer.lemmatize(word)
        for word in text.split()
        if word not in STOP_WORDS and len(word) > 2
    ]

    return " ".join(tokens)


# ── Clasificador de tipo de toxicidad (ML) ────────────────────────────────────
_KEYWORDS = {
    "machista": [
        "mujer", "mujeres", "hembra", "feminista", "cocina", "femenino", "fregona",
        "puta", "zorra", "perra", "sumisa", "callar", "inferior", "menor",
        "women", "female", "feminist", "kitchen", "bitch", "slut", "whore",
        "sexist", "inferior", "obey", "shut up woman",
    ],
    "racista": [
        "raza", "racista", "negro", "moro", "sudaca", "inmigrante", "extranjero",
        "deportar", "deported", "plaga", "inferior", "etnia", "gitano",
        "racist", "race", "monkey", "deportar", "deport", "immigrant", "ethnic",
        "nationality", "nationalist", "skin", "white", "black people",
    ],
    "sexual": [
        "sexo", "sexual", "porno", "desnudo", "genitales", "masturbacion",
        "violacion", "abusar", "acoso", "toquetear",
        "sex", "sexual", "porn", "naked", "rape", "molest", "harass",
        "genitals", "nude", "explicit",
    ],
    "insulto": [
        "idiota", "imbecil", "estupido", "inutil", "basura", "mierda",
        "asco", "muerto", "suicida", "desgraciado", "cerdo", "animal",
        "miserable", "gusano", "escoria",
        "idiot", "moron", "stupid", "dumb", "garbage", "trash", "loser",
        "freak", "pathetic", "worthless", "die", "kill", "hate", "disgusting",
        "shut up", "fool", "scum",
    ],
}


def classify_toxicity_type(text: str) -> str:
    """
    Classifies the toxicity type using an ML pipeline when available,
    falling back to keyword matching.
    Returns: 'machista', 'racista', 'sexual', 'insulto' or 'lenguaje cotidiano'.
    """
    pipeline = _load_type_pipeline()
    if pipeline is not None:
        pred = pipeline.predict([text])[0]
        if pred == "normal":
            return "lenguaje cotidiano"
        return pred

    # ── Keyword fallback ───────────────────────────────────────────────────────
    text_lower = text.lower()
    scores = {cat: 0 for cat in _KEYWORDS}
    for cat, keywords in _KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                scores[cat] += 1
    best_cat = max(scores, key=scores.get)
    return best_cat if scores[best_cat] > 0 else "lenguaje cotidiano"
