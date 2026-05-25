import streamlit as st
import joblib
import re
import nltk
import pandas as pd

from pathlib import Path
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

nltk.download('stopwords', quiet=True)
nltk.download('wordnet', quiet=True)
nltk.download('omw-1.4', quiet=True)

BASE_DIR = Path(__file__).resolve().parent.parent

model = joblib.load(BASE_DIR / "src" / "model.joblib")
vectorizer = joblib.load(BASE_DIR / "src" / "vectorizer.joblib")

stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()

def preprocess(text):
    text = str(text).lower()
    text = re.sub(r'http\S+|www\S+', '', text)
    text = re.sub(r'@\w+', '', text)
    text = re.sub(r'#\w+', '', text)
    text = re.sub(r'\d+', '', text)
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    text = ' '.join([word for word in text.split() if word not in stop_words])
    text = ' '.join([lemmatizer.lemmatize(word) for word in text.split()])
    return text

# ======================
# PAGE CONFIG
# ======================

st.set_page_config(
    page_title="Hate Speech Detector",
    page_icon="",
    layout="wide"
)

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .block-container { padding-top: 2rem; }
    .metric-card {
        background-color: #1e2130;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# ======================
# HEADER
# ======================

st.title("YouTube Hate Speech Detector")
st.markdown("""
YouTube recibe millones de comentarios al día. Este sistema actúa como
**primer filtro automático** para detectar contenido explícitamente ofensivo,
permitiendo a los moderadores humanos centrarse en los casos ambiguos.
""")

st.divider()

# ======================
# ANALYZER
# ======================

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Analizador de comentarios")
    user_input = st.text_area("Introduce un comentario", height=150, placeholder="Type a YouTube comment here...")

    if st.button("Analizar", type="primary"):
        if user_input.strip() == "":
            st.warning("Por favor introduce un comentario.")
        else:
            processed = preprocess(user_input)
            vectorized = vectorizer.transform([processed])
            probability = model.predict_proba(vectorized)[0]
            prediction = 1 if probability[1] >= 0.5 else 0
            confidence = probability[1] if prediction == 1 else probability[0]

            st.divider()

            if prediction == 1:
                st.error(f"TOXICO — Confianza: {confidence*100:.1f}%")
            else:
                st.success(f"NO TOXICO — Confianza: {confidence*100:.1f}%")

            st.progress(float(probability[1]), text=f"Probabilidad de toxicidad: {probability[1]*100:.1f}%")

            with st.expander("Ver texto procesado"):
                st.code(processed)

with col2:
    st.subheader("Modelo")
    st.metric("Accuracy", "59.5%")
    st.metric("Overfitting", "3.63pp")
    st.metric("Precision toxicos", "76%")

st.divider()

# ======================
# HOW IT WORKS
# ======================

st.subheader("Como funciona")

col3, col4 = st.columns(2)

with col3:
    st.markdown("""
    **El modelo como detector de palabras**

    Este sistema funciona como un detector de patrones lingüísticos,
    no como un lector de contexto. Analiza qué palabras aparecen
    en el comentario y las compara con los patrones aprendidos
    durante el entrenamiento.

    Es como un filtro de correo spam — muy efectivo para contenido
    explícitamente ofensivo, pero no infalible con casos ambiguos.
    """)

with col4:
    st.markdown("""
    **Limitacion conocida**

    La frase *"I hate racist people"* podria clasificarse como toxica
    porque contiene *"hate"*, cuando en realidad es anti-racista.

    El modelo no entiende el contexto completo de una frase,
    solo el peso estadistico de cada palabra. Para resolver esto
    seria necesario un modelo basado en transformers como BERT.

    Por eso este sistema es un **primer filtro**, no un juez final.
    """)

st.divider()

# ======================
# MODEL COMPARISON
# ======================

st.subheader("Evolucion del modelo")

results_data = {
    'Modelo': [
        'Logistic Regression',
        'Logistic Regression Regularized',
        'Random Forest',
        'Random Forest Regularized',
        'Random Forest Optuna',
        'RF Final Production'
    ],
    'Accuracy Test': ['72.5%', '57.0%', '69.5%', '66.5%', '62.5%', '59.5%'],
    'Diferencia Train/Test': ['23.4pp', '3.5pp', '30.1pp', '9.6pp', '4.0pp', '3.6pp'],
    'Estado': [
        'OVERFITTING',
        'OK',
        'OVERFITTING',
        'OVERFITTING',
        'OK',
        'OK'
    ]
}

df_results = pd.DataFrame(results_data)
st.dataframe(df_results, use_container_width=True)

st.divider()

# ======================
# EXAMPLES
# ======================

st.subheader("Casos de prueba")

examples = [
    {
        "comment": "i fucking hate you",
        "result": "No toxico",
        "explanation": "Odio directo no detectado. El modelo no asigna peso suficiente a estas palabras porque aparecen en contextos variados en el dataset."
    },
    {
        "comment": "this video is amazing",
        "result": "No toxico",
        "explanation": "Comentario neutro clasificado correctamente."
    },
    {
        "comment": "you are a stupid racist idiot",
        "result": "Toxico",
        "explanation": "Lenguaje racista explicito detectado correctamente. El modelo identifica bien patrones de odio sistematico."
    }
]

for ex in examples:
    with st.expander(f'"{ex["comment"]}" — {ex["result"]}'):
        st.write(ex["explanation"])