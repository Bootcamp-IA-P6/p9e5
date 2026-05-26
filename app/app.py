import streamlit as st
import joblib
import re
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# ── Descarga silenciosa de recursos NLTK ─────────────────────────────────────
for resource in ["stopwords", "wordnet", "omw-1.4"]:
    try:
        nltk.data.find(f"corpora/{resource}")
    except LookupError:
        nltk.download(resource, quiet=True)

# ── Configuración de página ───────────────────────────────────────────────────
st.set_page_config(
    page_title="ToxiGuard · Detector de Toxicidad",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS personalizado ─────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    .stApp { background-color: #0f1117; }
    .result-card {
        border-radius: 16px; padding: 28px 32px; margin: 16px 0;
        font-size: 1.1rem; line-height: 1.7;
    }
    .toxic { background: linear-gradient(135deg,#3d0b0b,#6b1a1a); border-left: 6px solid #e05050; }
    .safe  { background: linear-gradient(135deg,#0b2d1a,#155a30); border-left: 6px solid #4caf50; }
    .big-metric { font-size: 3.2rem; font-weight: 700; }
    .label-txt  { font-size: 0.85rem; color: #aaa; letter-spacing: .08em; }
    .gauge-bg   { background:#1e2130; border-radius:999px; height:18px; width:100%; }
    .gauge-fill-toxic { background:linear-gradient(90deg,#e05050,#ff8080); border-radius:999px; height:18px; }
    .gauge-fill-safe  { background:linear-gradient(90deg,#4caf50,#80e080); border-radius:999px; height:18px; }
    section[data-testid="stSidebar"] { background-color: #161b27; }
    .stButton>button {
        background: linear-gradient(135deg,#5b6ef5,#9b59b6);
        color: white; border: none; border-radius: 10px;
        padding: 10px 24px; font-size: 1rem; font-weight: 600;
        transition: opacity .2s;
    }
    .stButton>button:hover { opacity: .85; }
    textarea { background-color:#1e2130 !important; color:#f0f0f0 !important; border-radius:10px !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Carga del modelo ──────────────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "..", "src", "model.joblib")
VEC_PATH   = os.path.join(BASE_DIR, "..", "src", "vectorizer.joblib")

@st.cache_resource(show_spinner="Cargando modelo…")
def load_artifacts():
    model      = joblib.load(MODEL_PATH)
    vectorizer = joblib.load(VEC_PATH)
    return model, vectorizer

model, vectorizer = load_artifacts()

# ── Pipeline de limpieza ──────────────────────────────────────────────────────
_stop_words = set(stopwords.words("english"))
_lemmatizer = WordNetLemmatizer()

def preprocess(text: str) -> str:
    text = str(text).lower()
    text = re.sub(r"http\S+|www\S+", "", text)
    text = re.sub(r"@\w+", "", text)
    text = re.sub(r"#\w+", "", text)
    text = re.sub(r"\d+", "", text)
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    text = " ".join(w for w in text.split() if w not in _stop_words)
    text = " ".join(_lemmatizer.lemmatize(w) for w in text.split())
    return text

def predict(text: str):
    clean = preprocess(text)
    vec   = vectorizer.transform([clean])
    label = int(model.predict(vec)[0])
    proba = model.predict_proba(vec)[0]
    return label, proba, clean

# ── Historial ────────────────────────────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🛡️ ToxiGuard")
    st.markdown("Detector de toxicidad en comentarios de YouTube basado en **Random Forest + TF-IDF**.")
    st.divider()

    st.markdown("### ⚙️ Ajustes")
    threshold = st.slider(
        "Umbral de toxicidad",
        min_value=0.10, max_value=0.90, value=0.50, step=0.05,
        help="Si la probabilidad de toxicidad supera este umbral se clasifica como tóxico.",
    )
    show_clean     = st.toggle("Mostrar texto preprocesado", value=False)
    show_top_words = st.toggle("Mostrar palabras clave del modelo", value=True)

    st.divider()
    st.markdown("### 📊 Sesión actual")
    total   = len(st.session_state.history)
    toxic_n = sum(1 for h in st.session_state.history if h["label"] == 1)
    safe_n  = total - toxic_n
    col1, col2, col3 = st.columns(3)
    col1.metric("Total", total)
    col2.metric("🔴 Tóxicos", toxic_n)
    col3.metric("🟢 Seguros", safe_n)

    if total > 0 and st.button("🗑️ Limpiar historial"):
        st.session_state.history = []
        st.rerun()

    st.divider()
    st.caption("Modelo entrenado con [YouToxic 1k](https://www.kaggle.com/code/agabrielahernandezb/p-g-p9e5) · Proyecto P9E5")

# ── TÍTULO ────────────────────────────────────────────────────────────────────
st.markdown("# 🛡️ ToxiGuard — Detector de Toxicidad")
st.markdown("Analiza comentarios de YouTube y determina si contienen lenguaje tóxico.")
st.divider()

# ── TABS ──────────────────────────────────────────────────────────────────────
tab_single, tab_batch, tab_history, tab_info = st.tabs(
    ["🔍 Análisis individual", "📋 Análisis por lotes", "📜 Historial", "ℹ️ Sobre el modelo"]
)

# ════════════════════════════════════════════════════════
# TAB 1 · Análisis individual
# ════════════════════════════════════════════════════════
with tab_single:
    st.markdown("### Introduce un comentario")

    examples = {
        "🤬 Odio explícito":   "you are a stupid racist idiot and nobody likes you",
        "😊 Comentario positivo": "This video is absolutely amazing, great work!",
        "😐 Neutro ambiguo":   "I hate when people don't understand the basics",
        "🌍 Político":         "This politician is destroying the country with terrible decisions",
    }
    chosen = st.selectbox("O elige un ejemplo rápido:", ["— escribe el tuyo —"] + list(examples.keys()))
    default_text = examples[chosen] if chosen != "— escribe el tuyo —" else ""

    user_input = st.text_area(
        "Texto a analizar",
        value=default_text,
        height=130,
        placeholder="Escribe o pega aquí un comentario en inglés…",
        label_visibility="collapsed",
    )

    analyze_btn = st.button("🔍 Analizar", use_container_width=False)

    if analyze_btn and user_input.strip():
        label, proba, clean_text = predict(user_input)
        toxic_prob      = proba[1]
        effective_label = 1 if toxic_prob >= threshold else 0

        st.markdown("---")
        c1, c2, c3 = st.columns([1, 1, 2])

        with c1:
            if effective_label == 1:
                st.markdown(
                    '<p class="label-txt">RESULTADO</p>'
                    '<p class="big-metric" style="color:#e05050">🔴 TÓXICO</p>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    '<p class="label-txt">RESULTADO</p>'
                    '<p class="big-metric" style="color:#4caf50">🟢 SEGURO</p>',
                    unsafe_allow_html=True,
                )

        with c2:
            color = "#e05050" if effective_label == 1 else "#4caf50"
            st.markdown(
                f'<p class="label-txt">PROBABILIDAD TOXICIDAD</p>'
                f'<p class="big-metric" style="color:{color}">{toxic_prob*100:.1f}%</p>',
                unsafe_allow_html=True,
            )

        with c3:
            st.markdown('<p class="label-txt">BARRA DE CONFIANZA</p>', unsafe_allow_html=True)
            fill_pct = int(toxic_prob * 100)
            fill_cls = "gauge-fill-toxic" if effective_label == 1 else "gauge-fill-safe"
            st.markdown(
                f'<div class="gauge-bg"><div class="{fill_cls}" style="width:{fill_pct}%"></div></div>'
                f'<small style="color:#aaa">Umbral actual: {threshold*100:.0f}%</small>',
                unsafe_allow_html=True,
            )

        # Tarjeta descriptiva
        if effective_label == 1:
            st.markdown(
                f'<div class="result-card toxic">⚠️ <strong>Clasificado como TÓXICO</strong> con una confianza del '
                f'<strong>{toxic_prob*100:.1f}%</strong>.<br>'
                f'Contiene patrones de lenguaje asociados con odio, insultos o contenido dañino.</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<div class="result-card safe">✅ <strong>Parece SEGURO</strong> con una confianza del '
                f'<strong>{(1-toxic_prob)*100:.1f}%</strong>.<br>'
                f'No se detectaron patrones claros de lenguaje tóxico.</div>',
                unsafe_allow_html=True,
            )

        # Distribución de probabilidades
        with st.expander("📊 Distribución de probabilidades", expanded=True):
            fig, ax = plt.subplots(figsize=(5, 2.5), facecolor="#0f1117")
            ax.set_facecolor("#0f1117")
            bars = ax.barh(["No tóxico", "Tóxico"], [proba[0]*100, proba[1]*100],
                           color=["#4caf50", "#e05050"], height=0.45)
            for bar, val in zip(bars, [proba[0]*100, proba[1]*100]):
                ax.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2,
                        f"{val:.1f}%", va="center", color="white", fontsize=11)
            ax.set_xlim(0, 115)
            ax.tick_params(colors="white")
            ax.axvline(threshold*100, color="#ffcc00", linestyle="--", linewidth=1.5,
                       label=f"Umbral ({threshold*100:.0f}%)")
            ax.legend(facecolor="#1e2130", labelcolor="white", fontsize=9)
            for spine in ax.spines.values():
                spine.set_visible(False)
            st.pyplot(fig, use_container_width=False)

        # Texto preprocesado
        if show_clean:
            with st.expander("🔧 Texto preprocesado"):
                st.code(clean_text or "(texto vacío tras limpieza)", language="text")

        # Top palabras influyentes
        if show_top_words:
            with st.expander("🔑 Palabras más influyentes del comentario"):
                try:
                    feature_names = vectorizer.get_feature_names_out()
                    vec_arr       = vectorizer.transform([clean_text]).toarray()[0]
                    importances   = model.feature_importances_
                    scores        = vec_arr * importances
                    top_idx       = np.argsort(scores)[::-1][:10]
                    top_words     = [(feature_names[i], scores[i]) for i in top_idx if scores[i] > 0]

                    if top_words:
                        tw_df = pd.DataFrame(top_words, columns=["Palabra / n-grama", "Peso"])
                        fig2, ax2 = plt.subplots(figsize=(6, 3), facecolor="#0f1117")
                        ax2.set_facecolor("#0f1117")
                        bar_color = "#e05050" if effective_label == 1 else "#4caf50"
                        ax2.barh(tw_df["Palabra / n-grama"][::-1], tw_df["Peso"][::-1], color=bar_color)
                        ax2.tick_params(colors="white", labelsize=9)
                        for spine in ax2.spines.values():
                            spine.set_visible(False)
                        ax2.set_title("Palabras que más aportaron a la clasificación", color="white", fontsize=10)
                        st.pyplot(fig2, use_container_width=False)
                    else:
                        st.info("Ninguna palabra figura entre las características del modelo.")
                except Exception:
                    st.info("No se pudo calcular la importancia de palabras para este texto.")

        # Guardar en historial
        st.session_state.history.append({
            "text":  user_input[:120] + ("…" if len(user_input) > 120 else ""),
            "label": effective_label,
            "prob":  toxic_prob,
            "clean": clean_text,
        })

    elif analyze_btn:
        st.warning("Introduce un comentario para analizar.")

# ════════════════════════════════════════════════════════
# TAB 2 · Análisis por lotes
# ════════════════════════════════════════════════════════
with tab_batch:
    st.markdown("### Analiza múltiples comentarios a la vez")

    # ── Archivos de ejemplo descargables ─────────────────
    SAMPLES_DIR = os.path.join(BASE_DIR, "samples")
    with st.expander("📥 Descargar archivos de ejemplo", expanded=False):
        st.markdown("Descarga un archivo de muestra para ver el formato esperado:")
        ec1, ec2 = st.columns(2)
        with ec1:
            txt_path = os.path.join(SAMPLES_DIR, "sample_comments.txt")
            with open(txt_path, "rb") as f:
                st.download_button(
                    "📄 Descargar ejemplo .txt",
                    f.read(), "sample_comments.txt", "text/plain",
                    use_container_width=True,
                )
            st.caption("Un comentario por línea, texto plano.")
        with ec2:
            csv_path = os.path.join(SAMPLES_DIR, "sample_comments.csv")
            with open(csv_path, "rb") as f:
                st.download_button(
                    "📊 Descargar ejemplo .csv",
                    f.read(), "sample_comments.csv", "text/csv",
                    use_container_width=True,
                )
            st.caption("CSV con columna `comment` (puedes elegir la columna al subir).")

    st.markdown("---")
    st.markdown("**Introduce comentarios manualmente** o **sube un archivo** `.txt` / `.csv`:")

    upload = st.file_uploader(
        "Arrastra aquí tu archivo o haz clic para buscarlo",
        type=["txt", "csv"],
        help="Formatos aceptados: .txt (un comentario por línea) o .csv (elige la columna de texto).",
    )

    if upload:
        if upload.name.endswith(".csv"):
            df_up   = pd.read_csv(upload)
            col_sel = st.selectbox("Columna de texto:", df_up.columns.tolist())
            batch_text = "\n".join(df_up[col_sel].fillna("").astype(str).tolist())
            st.success(f"✅ CSV cargado — {len(df_up)} filas detectadas.")
        else:
            batch_text = upload.read().decode("utf-8")
            n_lines = len([l for l in batch_text.splitlines() if l.strip()])
            st.success(f"✅ Archivo .txt cargado — {n_lines} comentarios detectados.")
    else:
        batch_text = st.text_area(
            "Comentarios (uno por línea):",
            height=180,
            placeholder="This video is amazing!\nYou are an idiot.\nGreat explanation, thanks!\n…",
            label_visibility="collapsed",
        )

    if st.button("🚀 Analizar todos", use_container_width=False):
        lines = [l.strip() for l in batch_text.splitlines() if l.strip()]
        if not lines:
            st.warning("No hay texto para analizar.")
        else:
            results = []
            prog = st.progress(0, text="Analizando…")
            for i, line in enumerate(lines):
                lbl, prb, _ = predict(line)
                eff = 1 if prb[1] >= threshold else 0
                results.append({
                    "Comentario": line[:100],
                    "Resultado":  "🔴 Tóxico" if eff == 1 else "🟢 Seguro",
                    "P(Tóxico)%": round(prb[1]*100, 1),
                })
                prog.progress((i+1)/len(lines), text=f"Analizando {i+1}/{len(lines)}…")
            prog.empty()

            df_res  = pd.DataFrame(results)
            n_toxic = (df_res["Resultado"] == "🔴 Tóxico").sum()
            n_safe  = len(df_res) - n_toxic

            k1, k2, k3 = st.columns(3)
            k1.metric("Total analizados", len(df_res))
            k2.metric("🔴 Tóxicos", n_toxic)
            k3.metric("🟢 Seguros", n_safe)

            fig3, ax3 = plt.subplots(figsize=(4, 4), facecolor="#0f1117")
            ax3.set_facecolor("#0f1117")
            ax3.pie(
                [n_safe, n_toxic],
                labels=["Seguros", "Tóxicos"],
                colors=["#4caf50", "#e05050"],
                autopct="%1.1f%%", startangle=90,
                wedgeprops=dict(width=0.5),
                textprops=dict(color="white"),
            )
            ax3.set_title("Distribución de resultados", color="white")
            st.pyplot(fig3, use_container_width=False)

            st.dataframe(df_res, use_container_width=True, hide_index=True)
            csv = df_res.to_csv(index=False).encode("utf-8")
            st.download_button("⬇️ Descargar resultados CSV", csv, "toxiguard_results.csv", "text/csv")

# ════════════════════════════════════════════════════════
# TAB 3 · Historial
# ════════════════════════════════════════════════════════
with tab_history:
    st.markdown("### 📜 Historial de análisis de esta sesión")
    if not st.session_state.history:
        st.markdown(
            """
            <div style="text-align:center; padding:48px 0; color:#888;">
                <p style="font-size:3rem">📭</p>
                <p style="font-size:1.1rem">Aún no has analizado ningún comentario.</p>
                <p>Ve a la pestaña <strong>🔍 Análisis individual</strong> para empezar.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        df_hist = pd.DataFrame(st.session_state.history)
        df_hist["Resultado"]  = df_hist["label"].map({0: "🟢 Seguro", 1: "🔴 Tóxico"})
        df_hist["P(Tóxico)%"] = (df_hist["prob"] * 100).round(1)
        df_hist = df_hist.rename(columns={"text": "Comentario"})

        # KPIs rápidos en la cabecera del historial
        total_h  = len(df_hist)
        toxic_h  = (df_hist["label"] == 1).sum()
        safe_h   = total_h - toxic_h
        hk1, hk2, hk3, hk4 = st.columns(4)
        hk1.metric("Total analizados", total_h)
        hk2.metric("🔴 Tóxicos", toxic_h)
        hk3.metric("🟢 Seguros", safe_h)
        hk4.metric("% Toxicidad media", f"{df_hist['P(Tóxico)%'].mean():.1f}%")

        st.divider()

        # Tabla + descarga
        st.dataframe(df_hist[["Comentario", "Resultado", "P(Tóxico)%"]],
                     use_container_width=True, hide_index=True)
        csv_hist = df_hist[["Comentario", "Resultado", "P(Tóxico)%"]].to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Exportar historial CSV", csv_hist, "historial_toxiguard.csv", "text/csv")

        st.divider()

        # ── Gráficos lado a lado ──────────────────────────
        gc1, gc2 = st.columns(2)

        # 1) Gráfico de línea temporal
        with gc1:
            st.markdown("##### 📈 Evolución temporal")
            if total_h > 1:
                fig4, ax4 = plt.subplots(figsize=(6, 3), facecolor="#0f1117")
                ax4.set_facecolor("#0f1117")
                colors_dot = ["#e05050" if l == 1 else "#4caf50" for l in df_hist["label"]]
                ax4.plot(range(total_h), df_hist["P(Tóxico)%"],
                         color="#5b6ef5", linewidth=1.8, zorder=1)
                ax4.scatter(range(total_h), df_hist["P(Tóxico)%"],
                            c=colors_dot, s=60, zorder=2)
                ax4.axhline(threshold*100, color="#ffcc00", linestyle="--", linewidth=1.2,
                            label=f"Umbral {threshold*100:.0f}%")
                ax4.fill_between(range(total_h), df_hist["P(Tóxico)%"], alpha=0.12, color="#5b6ef5")
                ax4.set_xlabel("Nº análisis", color="white", fontsize=9)
                ax4.set_ylabel("P(Tóxico) %", color="white", fontsize=9)
                ax4.tick_params(colors="white", labelsize=8)
                ax4.legend(facecolor="#1e2130", labelcolor="white", fontsize=8)
                for spine in ax4.spines.values():
                    spine.set_visible(False)
                st.pyplot(fig4, use_container_width=True)
            else:
                st.info("Se necesitan al menos 2 análisis para mostrar la evolución.")

        # 2) Gráfico de tarta con efecto 3D (explode)
        with gc2:
            st.markdown("##### 🥧 Distribución global")
            if safe_h == 0 and toxic_h == 0:
                st.info("Sin datos suficientes.")
            else:
                sizes   = [safe_h, toxic_h]
                labels  = [f"Seguros\n{safe_h}", f"Tóxicos\n{toxic_h}"]
                colors  = ["#4caf50", "#e05050"]
                explode = (0.0, 0.08) if toxic_h > 0 else (0.0, 0.0)

                fig5, ax5 = plt.subplots(figsize=(5, 4), facecolor="#0f1117")
                ax5.set_facecolor("#0f1117")
                wedges, texts, autotexts = ax5.pie(
                    sizes,
                    labels=labels,
                    colors=colors,
                    explode=explode,
                    autopct="%1.1f%%",
                    startangle=140,
                    shadow=True,
                    wedgeprops=dict(edgecolor="#0f1117", linewidth=2),
                    textprops=dict(color="white", fontsize=10),
                )
                for at in autotexts:
                    at.set_fontsize(11)
                    at.set_fontweight("bold")
                    at.set_color("white")
                ax5.set_title("Comentarios analizados", color="white", fontsize=11, pad=12)

                # Leyenda externa con porcentaje
                pct_toxic = toxic_h / total_h * 100 if total_h > 0 else 0
                pct_safe  = safe_h  / total_h * 100 if total_h > 0 else 0
                legend_labels = [
                    f"🟢 Seguros  — {safe_h} ({pct_safe:.1f}%)",
                    f"🔴 Tóxicos — {toxic_h} ({pct_toxic:.1f}%)",
                ]
                import matplotlib.patches as _mp
                patches = [
                    _mp.Patch(color="#4caf50", label=legend_labels[0]),
                    _mp.Patch(color="#e05050", label=legend_labels[1]),
                ]
                ax5.legend(handles=patches, loc="lower center", bbox_to_anchor=(0.5, -0.18),
                           ncol=1, facecolor="#1e2130", labelcolor="white", fontsize=9,
                           framealpha=0.8, edgecolor="#333")
                fig5.tight_layout()
                st.pyplot(fig5, use_container_width=True)

# ════════════════════════════════════════════════════════
# TAB 4 · Sobre el modelo
# ════════════════════════════════════════════════════════
with tab_info:
    st.markdown("### ℹ️ Sobre el modelo y el proyecto")
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown(
            """
            #### 🧠 Arquitectura
            | Componente | Detalle |
            |---|---|
            | **Algoritmo** | Random Forest (scikit-learn) |
            | **Vectorización** | TF-IDF (500 features, 1-2 gramas) |
            | **Optimización** | Optuna (50 trials) |
            | **Dataset** | YouToxic English 1 000 comentarios |
            | **División** | 80% train / 20% test |

            #### ⚙️ Preprocesamiento
            1. Conversión a minúsculas
            2. Eliminación de URLs, menciones, hashtags
            3. Eliminación de números y puntuación
            4. Eliminación de *stopwords* (inglés)
            5. Lematización (WordNet)
            """
        )

    with col_b:
        st.markdown(
            """
            #### 📈 Métricas del modelo final
            | Métrica | Valor |
            |---|---|
            | **Accuracy test** | ~64.5% |
            | **Overfitting Δ** | < 5 pp ✅ |
            | **AUC-ROC** | ~0.70 |
            | **Recall tóxicos** | ~0.26 |

            #### ⚠️ Limitaciones
            - TF-IDF no entiende contexto (sarcasmo, ironía).
            - Dataset pequeño (800 muestras de entrenamiento).
            - Falla con odio implícito o contextual.

            #### 🔗 Referencias
            - [Notebook en Kaggle](https://www.kaggle.com/code/agabrielahernandezb/p-g-p9e5)
            - Repositorio: `Bootcamp-IA-P6/p9e5`
            """
        )

    st.divider()
    st.info(
        "💡 Para mejorar los resultados se requeriría un modelo basado en transformers (BERT/DistilBERT) "
        "capaz de capturar contexto semántico, junto con un dataset de al menos 10 000 muestras."
    )
