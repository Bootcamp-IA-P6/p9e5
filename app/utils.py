"""
app/utils.py - Funciones de preprocesamiento compartidas entre Streamlit y FastAPI.
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

STOP_WORDS  = set(stopwords.words("english")) | set(stopwords.words("spanish"))
lemmatizer  = WordNetLemmatizer()

# ── ML-based type classifier ─────────────────────────────────────────────────
_BASE_DIR        = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_TYPE_MODEL_PATH = os.path.join(_BASE_DIR, "src", "type_classifier.pkl")
_type_pipeline   = None


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

    text = text.lower()
    text = re.sub(r"http\S+|www\.\S+", "", text)
    text = re.sub(r"@\w+", "", text)
    text = re.sub(r"<.*?>", "", text)
    text = re.sub(r"[^a-z\s]", "", text)
    text = re.sub(r"\s+", " ", text).strip()

    tokens = [
        lemmatizer.lemmatize(word)
        for word in text.split()
        if word not in STOP_WORDS and len(word) > 2
    ]

    return " ".join(tokens)


# ── Keyword fallback ──────────────────────────────────────────────────────────
_KEYWORDS = {
    "machista": [
        "mujer", "mujeres", "hembra", "feminista", "cocina", "femenino",
        "puta", "zorra", "perra", "sumisa", "callar", "inferior",
        "women", "female", "feminist", "kitchen", "bitch", "slut", "whore",
        "sexist", "obey", "shut up woman",
    ],
    "racista": [
        "raza", "racista", "negro", "moro", "sudaca", "inmigrante", "extranjero",
        "deportar", "plaga", "etnia", "gitano",
        "racist", "race", "monkey", "deport", "immigrant", "ethnic",
        "nationality", "nationalist", "skin", "white", "black people",
    ],
    "sexual": [
        "sexo", "sexual", "porno", "desnudo", "genitales", "masturbacion",
        "violacion", "abusar", "acoso",
        "sex", "porn", "naked", "rape", "molest", "harass",
        "genitals", "nude", "explicit",
    ],
    "insulto": [
        "idiota", "imbecil", "estupido", "inutil", "basura", "mierda",
        "asco", "muerto", "suicida", "desgraciado", "cerdo", "escoria",
        "idiot", "moron", "stupid", "dumb", "garbage", "trash", "loser",
        "freak", "pathetic", "worthless", "die", "kill", "hate", "disgusting",
        "shut up", "fool", "scum",
    ],
    "homofobo": [
        "gay", "homosexual", "maricón", "marica", "maricon", "lesbiana",
        "travesti", "transexual", "trans", "lgbtq",
        "queer", "faggot", "dyke", "homo", "tranny", "perverted",
        "unnatural", "deviant", "abomination",
    ],
    "politico": [
        "fascista", "comunista", "dictadura", "golpista", "traidor", "corrupto",
        "tirano", "socialismo", "extremista", "terrorista",
        "fascism", "communist", "dictator", "traitor", "corrupt government",
        "propaganda", "extremist", "radical", "coup", "tyrant",
    ],
}


def classify_toxicity_type(text: str) -> str:
    """
    Clasifica el tipo de toxicidad usando un pipeline ML si está disponible,
    con fallback a keyword matching.
    Devuelve: 'machista', 'racista', 'sexual', 'insulto', 'homofobo', 'politico' o 'lenguaje cotidiano'.
    """
    pipeline = _load_type_pipeline()
    if pipeline is not None:
        pred = pipeline.predict([text])[0]
        return "lenguaje cotidiano" if pred == "normal" else pred

    # Keyword fallback
    text_lower = text.lower()
    scores     = {cat: 0 for cat in _KEYWORDS}
    for cat, keywords in _KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                scores[cat] += 1
    best_cat = max(scores, key=scores.get)
    return best_cat if scores[best_cat] > 0 else "lenguaje cotidiano"
