"""
app.py - App Streamlit para detección de mensajes de odio en comentarios de YouTube.
Proyecto: NLP - Análisis de Sentimientos / Hate Speech Detection

Modelos disponibles:
  - Clásico: TF-IDF + RandomForest (src/model.joblib)
  - Transformer: DistilBERT fine-tuned (sólo en esta app Streamlit)
"""

import os
import math
import io
import joblib
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import sys
sys.path.insert(0, os.path.dirname(__file__))
from utils import clean_text, classify_toxicity_type

# ── HuggingFace model ID for the transformer ─────────────────────────────────
# DistilBERT fine-tuned específicamente para detección de toxicidad en comentarios.
# Etiquetas del modelo: "toxic" / "non-toxic"
HF_MODEL_ID = "martin-ha/toxic-comment-model"

@st.cache_resource(show_spinner=False)
def load_transformer():
    try:
        from transformers import AutoTokenizer, AutoModelForSequenceClassification, TextClassificationPipeline
        tokenizer = AutoTokenizer.from_pretrained(HF_MODEL_ID)
        model_hf  = AutoModelForSequenceClassification.from_pretrained(HF_MODEL_ID)
        classifier = TextClassificationPipeline(model=model_hf, tokenizer=tokenizer, truncation=True, max_length=512)
        return classifier
    except Exception as e:
        return None


def predict_transformer(text: str, classifier) -> tuple[int, float]:
    """Devuelve (label, confidence): label=1 tóxico, label=0 no tóxico."""
    result    = classifier(text[:512])[0]
    label_str = result["label"].lower()   # "toxic" o "non-toxic"
    score     = float(result["score"])
    label     = 1 if label_str == "toxic" else 0
    return label, score

# ── Configuración de la página ────────────────────────────────────────────────
st.set_page_config(
    page_title="Hate Speech Detector",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Rutas ─────────────────────────────────────────────────────────────────────
BASE_DIR        = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH      = os.path.join(BASE_DIR, "src", "model.joblib")
VECTORIZER_PATH = os.path.join(BASE_DIR, "src", "vectorizer.joblib")


# ── Carga del modelo ──────────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def load_artifacts():
    if not os.path.exists(MODEL_PATH) or not os.path.exists(VECTORIZER_PATH):
        return None, None
    return joblib.load(MODEL_PATH), joblib.load(VECTORIZER_PATH)


def predict(text: str, model, vectorizer):
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
    return label, confidence


# ── Session state init ────────────────────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state["history"] = []
if "input_text" not in st.session_state:
    st.session_state["input_text"] = ""


# ── CSS personalizado ─────────────────────────────────────────────────────────
st.markdown("""
<style>
    html, body, [class*="css"] { font-family: 'Segoe UI', sans-serif; }

    .toxic-box {
        background: linear-gradient(135deg, #ff4b4b18, #ff4b4b35);
        border-left: 5px solid #ff4b4b;
        border-radius: 10px;
        padding: 20px 24px;
        margin: 12px 0 8px 0;
    }
    .safe-box {
        background: linear-gradient(135deg, #00c85318, #00c85335);
        border-left: 5px solid #00c853;
        border-radius: 10px;
        padding: 20px 24px;
        margin: 12px 0 8px 0;
    }
    .type-badge { border-radius: 10px; padding: 14px 18px; margin-top: 10px; }
    .conf-bar-track {
        background: #2a2a3e; border-radius: 8px;
        height: 14px; margin-top: 4px; overflow: hidden;
    }
    .conf-bar-fill { height: 14px; border-radius: 8px; }
    .hist-row {
        border-radius: 8px; padding: 10px 14px;
        margin-bottom: 6px; font-size: 14px;
    }
    .tile {
        background: #1a1a2e; border-radius: 12px;
        padding: 18px 12px; text-align: center;
        border: 1px solid #ffffff12;
    }
    .tile h1 { margin: 0; font-size: 2.2rem; }
    .tile p  { margin: 4px 0 0 0; color: #aaa; font-size: 13px; }
    section[data-testid="stSidebar"] { background: #0f0f1a; }
    .stTextArea textarea { font-size: 15px; border-radius: 8px; }
    div.stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #7c3aed, #4f46e5);
        border: none; border-radius: 8px;
        font-weight: 600; letter-spacing: 0.5px;
    }
    div.stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #6d28d9, #4338ca);
        transform: translateY(-1px);
        box-shadow: 0 4px 15px #7c3aed55;
    }
</style>
""", unsafe_allow_html=True)


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        '<div style="text-align:center;padding:10px 0 6px 0;">'
        '<span style="font-size:3rem;">🛡️</span></div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<h2 style="text-align:center;margin:0;color:#a78bfa;">Hate Speech<br>Detector</h2>',
        unsafe_allow_html=True,
    )
    st.markdown("---")
    st.markdown("### 🔍 ¿Cómo funciona?")
    st.markdown("""
1. Escribe un comentario de YouTube.  
2. El modelo TF-IDF + Logistic Regression lo clasifica.  
3. El clasificador ML detecta el **tipo** de toxicidad.
    """)
    st.markdown("---")
    st.markdown("### 🧠 Modelo")
    model_choice = st.radio(
        "Elige el motor de predicción:",
        ["🤖 Clásico (TF-IDF + RF)", "🔬 Transformer (DistilBERT)"],
        index=0,
        key="model_choice",
    )
    if "Transformer" in model_choice:
        st.markdown("""
| Campo | Valor |
|---|---|
| Modelo | DistilBERT multilingüe |
| Tipo | Transformer (HuggingFace) |
| Uso | Solo en esta app Streamlit |
        """)
    else:
        st.markdown("""
| Campo | Valor |
|---|---|
| Vectorización | TF-IDF (1-2 gramas) |
| Clasificador | Random Forest |
| Tipo | ML Clásico |
| Dataset | YouToxic bilingüe |
        """)
    st.markdown("---")
    st.markdown("### 🏷️ Etiquetas")
    st.markdown("""
| | Significado |
|---|---|
| ✅ | Comentario seguro |
| 🚨 | Contiene odio/abuso |
| ⚧️ | Machista |
| 🌍 | Racista |
| 🔞 | Sexual |
| 💢 | Insulto |
| 💬 | Lenguaje cotidiano |
    """)
    st.markdown("---")
    st.caption("Proyecto académico · NLP · 2025")


# ── Cabecera ──────────────────────────────────────────────────────────────────
st.markdown("""
<div style="
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 60%, #0f3460 100%);
    border-radius: 16px; padding: 32px 36px; margin-bottom: 28px;
    border: 1px solid #ffffff10;
">
    <h1 style="margin:0;color:#a78bfa;font-size:2.2rem;">
        🛡️ Detector de Mensajes de Odio en YouTube
    </h1>
    <p style="margin:10px 0 0 0;color:#94a3b8;font-size:16px;">
        Analiza comentarios y detecta lenguaje tóxico usando
        <strong style="color:#a78bfa;">Machine Learning</strong> —
        TF-IDF + Logistic Regression + clasificador de tipo multiclase.
    </p>
</div>
""", unsafe_allow_html=True)

# ── Carga modelo ──────────────────────────────────────────────────────────────
model_choice = st.session_state.get("model_choice", "🤖 Clásico (TF-IDF + RF)")
use_transformer = "Transformer" in model_choice

with st.spinner("Cargando modelo..."):
    if use_transformer:
        transformer_clf = load_transformer()
        model = vectorizer = None
        if transformer_clf is None:
            st.error("⚠️ No se pudo cargar el modelo Transformer. Verifica tu conexión y que `transformers` esté instalado.")
            st.stop()
    else:
        model, vectorizer = load_artifacts()
        transformer_clf = None
        if model is None:
            st.error(
                "⚠️ No se encontraron los artefactos del modelo en `src/`. "
                "Ejecuta primero `train_model.py`."
            )
            st.stop()

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab_analyze, tab_history, tab_stats = st.tabs([
    "🔍 Análisis Individual",
    "📋 Histórico",
    "📊 Estadísticas",
])

TYPE_CONFIG = {
    "machista":           {"icon": "⚧️",  "color": "#e040fb", "label": "Machista"},
    "racista":            {"icon": "🌍",  "color": "#ff6d00", "label": "Racista"},
    "sexual":             {"icon": "🔞",  "color": "#f50057", "label": "Sexual"},
    "insulto":            {"icon": "💢",  "color": "#ff4b4b", "label": "Insulto"},
    "lenguaje cotidiano": {"icon": "💬",  "color": "#90a4ae", "label": "Lenguaje cotidiano"},
}

# ════════════════════════════════════════════════════════════════════════════════
# TAB 1 — Análisis Individual
# ════════════════════════════════════════════════════════════════════════════════
with tab_analyze:
    col_input, col_result = st.columns([1.2, 1], gap="large")

    with col_input:
        st.subheader("✍️ Introduce un comentario")

        ex1, ex2 = st.columns(2)
        with ex1:
            if st.button("💬 Ejemplo seguro", use_container_width=True):
                st.session_state["textarea_input"] = "This video is amazing! Really well explained, thank you so much."
                st.rerun()
        with ex2:
            if st.button("⚠️ Ejemplo tóxico", use_container_width=True):
                st.session_state["textarea_input"] = "You are so stupid and ugly, nobody wants to see your disgusting face."
                st.rerun()

        user_text = st.text_area(
            label="Comentario",
            placeholder="Escribe aquí el comentario de YouTube que quieres analizar...",
            height=190,
            label_visibility="collapsed",
            key="textarea_input",
        )

        analyze_btn = st.button(
            "🔍 Analizar comentario", type="primary", use_container_width=True
        )

    with col_result:
        st.subheader("📊 Resultado")

        if analyze_btn:
            if not user_text.strip():
                st.warning("Por favor, introduce un comentario antes de analizar.")
            else:
                with st.spinner("Analizando..."):
                    if use_transformer and transformer_clf is not None:
                        label, confidence = predict_transformer(user_text, transformer_clf)
                    else:
                        label, confidence = predict(user_text, model, vectorizer)
                    tox_type = classify_toxicity_type(user_text)

                if label == 1:
                    st.markdown(
                        '<div class="toxic-box">'
                        '<h2 style="color:#ff4b4b;margin:0;">🚨 TÓXICO</h2>'
                        '<p style="font-size:15px;margin:8px 0 0 0;">Este comentario ha sido '
                        'clasificado como <b>tóxico o con lenguaje de odio</b>.</p>'
                        '</div>', unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        '<div class="safe-box">'
                        '<h2 style="color:#00c853;margin:0;">✅ NO TÓXICO</h2>'
                        '<p style="font-size:15px;margin:8px 0 0 0;">Este comentario parece '
                        '<b>seguro y sin lenguaje ofensivo</b>.</p>'
                        '</div>', unsafe_allow_html=True,
                    )

                pct = int(confidence * 100)
                bar_color = "#ff4b4b" if label == 1 else "#00c853"
                st.markdown(f"""
                <div style="margin-top:12px;">
                    <div style="display:flex;justify-content:space-between;
                                font-size:13px;color:#aaa;">
                        <span>Confianza del modelo</span>
                        <span style="color:{bar_color};font-weight:700;">{pct}%</span>
                    </div>
                    <div class="conf-bar-track">
                        <div class="conf-bar-fill"
                             style="width:{pct}%;background:{bar_color};"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                cfg = TYPE_CONFIG[tox_type]
                st.markdown(f"""
                <div class="type-badge"
                     style="background:{cfg['color']}18;border-left:5px solid {cfg['color']};">
                    <p style="margin:0;font-size:11px;color:{cfg['color']};
                              font-weight:700;text-transform:uppercase;letter-spacing:1px;">
                        Tipo de contenido detectado (ML)
                    </p>
                    <h3 style="margin:4px 0 0 0;color:{cfg['color']};">
                        {cfg['icon']} {cfg['label']}
                    </h3>
                </div>
                """, unsafe_allow_html=True)

                st.session_state["history"].append({
                    "Comentario": user_text[:120] + ("…" if len(user_text) > 120 else ""),
                    "Resultado":  "🚨 Tóxico" if label == 1 else "✅ No tóxico",
                    "Tipo":       f"{cfg['icon']} {cfg['label']}",
                    "Confianza":  f"{pct}%",
                    "_label":     label,
                    "_type":      tox_type,
                })

                with st.expander("ℹ️ ¿Qué significa cada tipo?"):
                    st.markdown("""
| Tipo | Descripción |
|---|---|
| ⚧️ **Machista** | Lenguaje sexista o discriminatorio hacia la mujer |
| 🌍 **Racista** | Contenido basado en raza, etnia o nacionalidad |
| 🔞 **Sexual** | Contenido sexual explícito o acoso sexual |
| 💢 **Insulto** | Insultos directos, amenazas o lenguaje agresivo |
| 💬 **Lenguaje cotidiano** | Sin categoría específica clara |
                    """)

                with st.expander("🔬 Ver texto preprocesado"):
                    cleaned = clean_text(user_text)
                    st.code(
                        cleaned if cleaned else "(texto vacío tras preprocesamiento)",
                        language=None,
                    )

# ════════════════════════════════════════════════════════════════════════════════
# TAB 2 — Histórico
# ════════════════════════════════════════════════════════════════════════════════
with tab_history:
    history = st.session_state["history"]

    if not history:
        st.info("🕐 Aún no has analizado ningún comentario. Ve a **Análisis Individual** para empezar.")
    else:
        col_clear, col_export, _ = st.columns([1, 1, 4])
        with col_clear:
            if st.button("🗑️ Limpiar histórico", use_container_width=True):
                st.session_state["history"] = []
                st.rerun()
        with col_export:
            df_hist = pd.DataFrame([
                {"Comentario": r["Comentario"], "Resultado": r["Resultado"],
                 "Tipo": r["Tipo"], "Confianza": r["Confianza"]}
                for r in history
            ])
            csv_buf = io.StringIO()
            df_hist.to_csv(csv_buf, index=False, encoding="utf-8-sig")
            st.download_button(
                label="⬇️ Exportar CSV",
                data=csv_buf.getvalue().encode("utf-8-sig"),
                file_name="historico_analisis.csv",
                mime="text/csv",
                use_container_width=True,
            )

        st.markdown("---")
        for row in reversed(history):
            bg     = "#ff4b4b12" if row["_label"] == 1 else "#00c85312"
            border = "#ff4b4b"   if row["_label"] == 1 else "#00c853"
            st.markdown(f"""
            <div class="hist-row" style="background:{bg};border-left:4px solid {border};">
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <span style="color:#e2e8f0;flex:3;">{row['Comentario']}</span>
                    <span style="flex:1;text-align:center;">{row['Resultado']}</span>
                    <span style="flex:1;text-align:center;">{row['Tipo']}</span>
                    <span style="flex:0.7;text-align:right;color:#94a3b8;">{row['Confianza']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════════
# TAB 3 — Estadísticas
# ════════════════════════════════════════════════════════════════════════════════
with tab_stats:
    history = st.session_state["history"]

    if not history:
        st.info("📊 Analiza al menos un comentario para ver las estadísticas.")
    else:
        total     = len(history)
        n_toxic   = sum(1 for r in history if r["_label"] == 1)
        n_safe    = total - n_toxic
        pct_toxic = int(n_toxic / total * 100) if total else 0

        st.markdown("### 📈 Resumen")
        m1, m2, m3, m4 = st.columns(4)
        for col, val, lbl, color in [
            (m1, str(total),      "Analizados",       "#a78bfa"),
            (m2, str(n_toxic),    "Tóxicos 🚨",       "#ff4b4b"),
            (m3, str(n_safe),     "No tóxicos ✅",     "#00c853"),
            (m4, f"{pct_toxic}%", "Tasa de toxicidad", "#fbbf24"),
        ]:
            with col:
                st.markdown(f"""
                <div class="tile">
                    <h1 style="color:{color};">{val}</h1>
                    <p>{lbl}</p>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        g1, g2 = st.columns(2)

        with g1:
            st.markdown("#### 🥧 Tóxico vs No tóxico")
            fig1, ax1 = plt.subplots(figsize=(4, 4), facecolor="#0f0f1a")
            ax1.set_facecolor("#0f0f1a")
            sizes = [n_toxic, n_safe] if n_safe > 0 else [n_toxic, 0.0001]
            ax1.pie(
                sizes, labels=["Tóxico", "No tóxico"],
                colors=["#ff4b4b", "#00c853"], autopct="%1.0f%%", startangle=140,
                wedgeprops={"linewidth": 2, "edgecolor": "#0f0f1a"},
                textprops={"color": "#e2e8f0", "fontsize": 12},
            )
            ax1.set_title("Distribución general", color="#a78bfa", pad=14)
            st.pyplot(fig1, use_container_width=True)
            plt.close(fig1)

        with g2:
            st.markdown("#### 📊 Tipos de toxicidad")
            type_counts = {}
            for r in history:
                t = r["_type"]
                type_counts[t] = type_counts.get(t, 0) + 1
            type_labels = list(type_counts.keys())
            type_vals   = list(type_counts.values())
            type_colors = [TYPE_CONFIG.get(t, {}).get("color", "#888") for t in type_labels]
            display_labels = [
                f"{TYPE_CONFIG.get(t,{}).get('icon','')} {TYPE_CONFIG.get(t,{}).get('label',t)}"
                for t in type_labels
            ]
            fig2, ax2 = plt.subplots(figsize=(5, 4), facecolor="#0f0f1a")
            ax2.set_facecolor("#0f0f1a")
            bars = ax2.bar(display_labels, type_vals, color=type_colors,
                           width=0.5, edgecolor="#0f0f1a", linewidth=1.5)
            ax2.set_ylabel("Cantidad", color="#94a3b8")
            ax2.set_title("Comentarios por tipo", color="#a78bfa", pad=14)
            ax2.tick_params(colors="#94a3b8", rotation=20)
            ax2.spines[:].set_color("#333355")
            for bar, val in zip(bars, type_vals):
                ax2.text(
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + 0.05, str(val),
                    ha="center", va="bottom",
                    color="#e2e8f0", fontsize=11, fontweight="bold",
                )
            plt.tight_layout()
            st.pyplot(fig2, use_container_width=True)
            plt.close(fig2)

        st.markdown("#### 📉 Evolución de confianza por análisis")
        conf_vals   = [int(r["Confianza"].replace("%", "")) for r in history]
        colors_line = ["#ff4b4b" if r["_label"] == 1 else "#00c853" for r in history]
        xs = list(range(1, len(conf_vals) + 1))
        fig3, ax3 = plt.subplots(figsize=(10, 3), facecolor="#0f0f1a")
        ax3.set_facecolor("#0f0f1a")
        ax3.plot(xs, conf_vals, color="#a78bfa", linewidth=2, zorder=1)
        ax3.scatter(xs, conf_vals, c=colors_line, s=70, zorder=2, edgecolors="#0f0f1a")
        ax3.axhline(50, color="#555577", linestyle="--", linewidth=1)
        ax3.set_ylim(0, 105)
        ax3.set_xlabel("Nº análisis", color="#94a3b8")
        ax3.set_ylabel("Confianza (%)", color="#94a3b8")
        ax3.set_title("Confianza por análisis  (🔴 Tóxico · 🟢 No tóxico)",
                      color="#a78bfa", pad=10)
        ax3.tick_params(colors="#94a3b8")
        ax3.spines[:].set_color("#333355")
        ax3.legend(
            handles=[mpatches.Patch(color="#ff4b4b", label="Tóxico"),
                     mpatches.Patch(color="#00c853", label="No tóxico")],
            facecolor="#1a1a2e", edgecolor="#555577", labelcolor="#e2e8f0",
        )
        plt.tight_layout()
        st.pyplot(fig3, use_container_width=True)
        plt.close(fig3)

        st.markdown("---")
        summary_df = pd.DataFrame({
            "Métrica": ["Total analizados", "Tóxicos", "No tóxicos", "Tasa toxicidad (%)"],
            "Valor":   [total, n_toxic, n_safe, pct_toxic],
        })
        st.download_button(
            label="⬇️ Exportar estadísticas CSV",
            data=summary_df.to_csv(index=False).encode("utf-8-sig"),
            file_name="estadisticas_analisis.csv",
            mime="text/csv",
        )
