"""
train_model.py - Entrena el modelo clásico de p9e5 y guarda los artefactos en src/
Basado en el notebook 03_modeling.ipynb
"""
import os, random
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
import joblib

# ── 1. Cargar dataset procesado ───────────────────────────────────────────────
BASE = os.path.dirname(os.path.abspath(__file__))
df = pd.read_csv(os.path.join(BASE, "data", "processed", "youtoxic_processed.csv"))
df["text_clean"] = df["text_clean"].fillna("").astype(str)
print(f"Dataset cargado: {df.shape}")

X = df["text_clean"]
y = df["IsToxic"].astype(int)

# ── 2. Split ──────────────────────────────────────────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
print(f"Train: {len(X_train)} | Test: {len(X_test)}")

# ── 3. Vectorización TF-IDF ───────────────────────────────────────────────────
vectorizer = TfidfVectorizer(max_features=500, ngram_range=(1, 2))
X_train_tfidf = vectorizer.fit_transform(X_train)
X_test_tfidf  = vectorizer.transform(X_test)

# ── 4. Data augmentation con sinónimos (ambas clases) ─────────────────────────
try:
    import nltk
    from nltk.corpus import wordnet
    nltk.download("wordnet", quiet=True)
    nltk.download("omw-1.4", quiet=True)

    def synonym_replacement(text, n=2):
        words = text.split()
        candidates = [w for w in words if len(w) > 2 and wordnet.synsets(w)]
        random.shuffle(candidates)
        new_words = words.copy()
        replaced = 0
        for word in candidates:
            synsets = wordnet.synsets(word)
            if not synsets:
                continue
            synonym = synsets[0].lemmas()[0].name().replace("_", " ")
            if synonym.lower() != word.lower():
                new_words = [synonym if w == word else w for w in new_words]
                replaced += 1
            if replaced >= n:
                break
        return " ".join(new_words)

    random.seed(42)
    train_df = pd.DataFrame({"text": X_train, "label": y_train})
    toxic_train     = train_df[train_df["label"] == 1]
    non_toxic_train = train_df[train_df["label"] == 0]

    aug_toxic     = toxic_train["text"].apply(lambda x: synonym_replacement(x, n=2))
    aug_non_toxic = non_toxic_train["text"].apply(lambda x: synonym_replacement(x, n=2))

    X_train_aug = pd.concat([train_df["text"], aug_toxic, aug_non_toxic], ignore_index=True)
    y_train_aug = pd.concat([train_df["label"], toxic_train["label"], non_toxic_train["label"]], ignore_index=True)

    vectorizer_aug = TfidfVectorizer(max_features=500, ngram_range=(1, 2))
    X_train_aug_tfidf = vectorizer_aug.fit_transform(X_train_aug)
    X_test_aug_tfidf  = vectorizer_aug.transform(X_test)
    print(f"Train aumentado: {len(X_train_aug)} muestras")
    use_aug = True
except Exception as e:
    print(f"Augmentation no disponible: {e}. Usando datos originales.")
    use_aug = False

# ── 5. Modelo final ───────────────────────────────────────────────────────────
model = RandomForestClassifier(
    n_estimators=200,
    max_depth=12,
    min_samples_leaf=4,
    max_features="sqrt",
    class_weight="balanced",   # corrige desequilibrio tóxico/no-tóxico
    random_state=42,
    n_jobs=-1,
)

if use_aug:
    model.fit(X_train_aug_tfidf, y_train_aug)
    X_te = X_test_aug_tfidf
    vec_final = vectorizer_aug
else:
    model.fit(X_train_tfidf, y_train)
    X_te = X_test_tfidf
    vec_final = vectorizer

# ── 6. Evaluación ─────────────────────────────────────────────────────────────
y_pred = model.predict(X_te)
train_pred = model.predict(X_train_aug_tfidf if use_aug else X_train_tfidf)
train_acc = accuracy_score(y_train_aug if use_aug else y_train, train_pred) * 100
test_acc  = accuracy_score(y_test, y_pred) * 100
print(f"\nAccuracy train: {train_acc:.1f}% | test: {test_acc:.1f}% | gap: {train_acc-test_acc:.1f}pp")
print(classification_report(y_test, y_pred, target_names=["No toxico", "Toxico"]))

# ── 7. Guardar artefactos en src/ ─────────────────────────────────────────────
os.makedirs(os.path.join(BASE, "src"), exist_ok=True)
joblib.dump(model,     os.path.join(BASE, "src", "model.joblib"))
joblib.dump(vec_final, os.path.join(BASE, "src", "vectorizer.joblib"))
print("\n✅ Artefactos guardados:")
print(f"   {BASE}/src/model.joblib")
print(f"   {BASE}/src/vectorizer.joblib")
