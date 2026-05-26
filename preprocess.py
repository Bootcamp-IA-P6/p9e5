"""
preprocess.py - Genera data/processed/youtoxic_processed.csv desde el raw.
Basado en el notebook 02_preprocessing.ipynb de p9e5.
"""
import os
import re
import pandas as pd
import nltk

for res in ["stopwords", "wordnet", "omw-1.4"]:
    nltk.download(res, quiet=True)

from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

STOP_WORDS = set(stopwords.words("english"))
lemmatizer = WordNetLemmatizer()

BASE = os.path.dirname(os.path.abspath(__file__))
RAW  = os.path.join(BASE, "data", "raw",       "youtoxic_english_1000.csv")
OUT  = os.path.join(BASE, "data", "processed", "youtoxic_processed.csv")

df = pd.read_csv(RAW)
print(f"Dataset cargado: {df.shape}")

def clean_text(text: str) -> str:
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r"http\S+|www\.\S+", "", text)
    text = re.sub(r"@\w+", "", text)
    text = re.sub(r"<.*?>", "", text)
    text = re.sub(r"[^a-z\s]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    tokens = [
        lemmatizer.lemmatize(w)
        for w in text.split()
        if w not in STOP_WORDS and len(w) > 2
    ]
    return " ".join(tokens)

df["text_clean"] = df["Text"].apply(clean_text)
df["IsToxic"]    = df["IsToxic"].map({"TRUE": 1, "FALSE": 0, True: 1, False: 0}).fillna(0).astype(int)

os.makedirs(os.path.dirname(OUT), exist_ok=True)
df[["text_clean", "IsToxic"]].to_csv(OUT, index=False)
print(f"✅ Dataset procesado guardado: {OUT}")
print(f"   Filas: {len(df)} | Tóxicos: {df['IsToxic'].sum()} | No tóxicos: {(df['IsToxic']==0).sum()}")
