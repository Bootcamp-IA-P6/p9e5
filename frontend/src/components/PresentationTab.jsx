import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Box, Card, CardContent, Typography, Button, Chip,
  LinearProgress, Stack,
} from "@mui/material";
import {
  ArrowForward as ArrowForwardIcon,
  ArrowBack as ArrowBackIcon,
  YouTube as YouTubeIcon,
  Shield as ShieldIcon,
  Psychology as PsychologyIcon,
  Code as CodeIcon,
  BarChart as BarChartIcon,
  EmojiObjects as EmojiObjectsIcon,
  Groups as GroupsIcon,
  CheckCircle as CheckCircleIcon,
  TuneOutlined as TuneIcon,
  DownloadingOutlined as DownloadingIcon,
} from "@mui/icons-material";

const G_BLUE   = "#1a73e8";
const G_RED    = "#ea4335";
const G_YELLOW = "#fbbc04";
const G_GREEN  = "#34a853";

// ── Slide data ─────────────────────────────────────────────────────────────────
// 10 slides × ~2 min = 20 min presentation
const SLIDES = [
  {
    id: 0, tag: "El problema",
    color: G_RED,    bg: "#fce8e6",
    icon: <YouTubeIcon   sx={{ fontSize: "2.5rem", color: G_RED }}    />,
    title: "YouTube tiene un problema",
    subtitle: "Y se llama lenguaje de odio",
    body: SlideYoutubeProblem,
  },
  {
    id: 1, tag: "La solución",
    color: G_BLUE,   bg: "#e8f0fe",
    icon: <ShieldIcon    sx={{ fontSize: "2.5rem", color: G_BLUE }}   />,
    title: "Nuestra solución: IA al rescate",
    subtitle: "Un detector automático de mensajes de odio",
    body: SlideSolution,
  },
  {
    id: 2, tag: "¿Para quién?",
    color: G_GREEN,  bg: "#e6f4ea",
    icon: <GroupsIcon    sx={{ fontSize: "2.5rem", color: G_GREEN }}  />,
    title: "¿A quién ayuda este proyecto?",
    subtitle: "Múltiples beneficiarios",
    body: SlideAudience,
  },
  {
    id: 3, tag: "Los datos",
    color: G_YELLOW, bg: "#fef7e0",
    icon: <BarChartIcon  sx={{ fontSize: "2.5rem", color: "#e37400" }} />,
    title: "El dataset",
    subtitle: "¿Con qué enseñamos al modelo?",
    body: SlideData,
  },
  {
    id: 4, tag: "El scraper",
    color: G_RED,    bg: "#fce8e6",
    icon: <DownloadingIcon sx={{ fontSize: "2.5rem", color: G_RED }} />,
    title: "Cómo obtenemos comentarios reales",
    subtitle: "Web scraping de YouTube con Python",
    body: SlideScraper,
  },
  {
    id: 5, tag: "Preprocesado",
    color: G_BLUE,   bg: "#e8f0fe",
    icon: <CodeIcon      sx={{ fontSize: "2.5rem", color: G_BLUE }}   />,
    title: "Preprocesamiento del texto",
    subtitle: "Limpiar el lenguaje para que la IA lo entienda",
    body: SlidePreprocessing,
  },
  {
    id: 6, tag: "El modelo",
    color: "#9c27b0", bg: "#f3e5f5",
    icon: <PsychologyIcon sx={{ fontSize: "2.5rem", color: "#9c27b0" }} />,
    title: "El modelo de Machine Learning",
    subtitle: "TF-IDF + Regresión Logística",
    body: SlideModel,
  },
  {
    id: 7, tag: "Optuna",
    color: "#0097a7", bg: "#e0f7fa",
    icon: <TuneIcon      sx={{ fontSize: "2.5rem", color: "#0097a7" }} />,
    title: "Ajuste automático de hiperparámetros",
    subtitle: "Optuna: encontrar la mejor configuración del modelo",
    body: SlideOptuna,
  },
  {
    id: 8, tag: "Resultados",
    color: G_GREEN,  bg: "#e6f4ea",
    icon: <BarChartIcon  sx={{ fontSize: "2.5rem", color: G_GREEN }}  />,
    title: "Resultados y métricas",
    subtitle: "¿Qué tan bien funciona?",
    body: SlideResults,
  },
  {
    id: 9, tag: "Resumen",
    color: G_BLUE,   bg: "#e8f0fe",
    icon: <EmojiObjectsIcon sx={{ fontSize: "2.5rem", color: G_BLUE }} />,
    title: "Resumen del proyecto",
    subtitle: "Lo que hemos construido",
    body: SlideSummary,
  },
];

// ── Slide bodies ───────────────────────────────────────────────────────────────

function SlideYoutubeProblem() {
  const stats = [
    { num: "500h",  desc: "de vídeo subidas a YouTube cada minuto" },
    { num: "2.7B",  desc: "usuarios activos mensuales" },
    { num: "∞",     desc: "comentarios con odio que los moderadores no pueden revisar" },
  ];
  return (
    <Box>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 3, lineHeight: 1.8 }}>
        YouTube es la plataforma de vídeo más grande del mundo. Cada día se publican millones de
        comentarios, y una parte significativa de ellos contiene <strong>insultos, racismo, machismo
        y acoso</strong>. Un equipo de moderadores humanos simplemente <strong>no puede revisarlos
        todos</strong> — ni económica ni logísticamente.
      </Typography>
      <Box sx={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 2, mb: 3 }}>
        {stats.map(({ num, desc }) => (
          <Box key={num} sx={{ bgcolor: "#fff", border: "1px solid #fad2cf",
              borderRadius: 3, p: 2.5, textAlign: "center" }}>
            <Typography variant="h4" fontWeight={800} sx={{ color: G_RED }}>{num}</Typography>
            <Typography variant="caption" color="text.secondary">{desc}</Typography>
          </Box>
        ))}
      </Box>
      <Alert_ color={G_RED} bg="#fce8e6">
        💡 <strong>El reto:</strong> automatizar la detección para que pueda escalar junto a la
        plataforma, sin necesitar más personal. El cliente prioriza una solución <strong>práctica
        y desplegable</strong> por encima de la precisión perfecta.
      </Alert_>
    </Box>
  );
}

function SlideSolution() {
  const steps = [
    { icon: "📝", title: "Comentario de entrada",  desc: "El usuario introduce un comentario o la URL de un vídeo de YouTube" },
    { icon: "🧹", title: "Limpieza del texto",     desc: "Eliminamos URLs, menciones, stopwords y normalizamos con NLTK" },
    { icon: "🔢", title: "Vectorización TF-IDF",   desc: "Convertimos el texto en un vector de números que el modelo entiende" },
    { icon: "🧠", title: "Predicción ML",          desc: "El modelo clasifica: ¿tóxico o no tóxico? ¿De qué tipo específico?" },
    { icon: "📊", title: "Resultado visual",       desc: "La app React muestra el veredicto con confianza, tipo y estadísticas" },
  ];
  return (
    <Box>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 3, lineHeight: 1.8 }}>
        Construimos un sistema completo de extremo a extremo: desde la recogida de datos hasta
        la interfaz de usuario, pasando por el preprocesamiento, entrenamiento y despliegue.
        Todo gira alrededor de técnicas clásicas de <strong>NLP + Machine Learning</strong>.
      </Typography>
      <Box sx={{ display: "flex", flexDirection: "column", gap: 1.5 }}>
        {steps.map((s, i) => (
          <Box key={i} sx={{ display: "flex", alignItems: "center", gap: 2,
              p: 1.5, borderRadius: 3, bgcolor: "#fff", border: "1px solid #c5d9f8" }}>
            <Box sx={{ width: 40, height: 40, borderRadius: 2, bgcolor: "#e8f0fe",
                display: "flex", alignItems: "center", justifyContent: "center",
                fontSize: "1.3rem", flexShrink: 0 }}>
              {s.icon}
            </Box>
            <Box sx={{ flex: 1 }}>
              <Typography variant="subtitle2" fontWeight={700}>{s.title}</Typography>
              <Typography variant="caption" color="text.secondary">{s.desc}</Typography>
            </Box>
            {i < steps.length - 1 && (
              <ArrowForwardIcon sx={{ ml: "auto", color: "#dadce0", flexShrink: 0 }} />
            )}
          </Box>
        ))}
      </Box>
    </Box>
  );
}

function SlideAudience() {
  const audiences = [
    { icon: "🎬", title: "YouTubers y creadores",       desc: "Analizan sus comentarios en masa, detectan acoso y protegen su comunidad antes de que escale." },
    { icon: "🏢", title: "Equipos de moderación",      desc: "Herramienta de apoyo que prioriza automáticamente qué comentarios revisar primero." },
    { icon: "🎓", title: "Investigadores y académicos", desc: "Estudian patrones de odio online en español e inglés con una herramienta reproducible." },
    { icon: "📱", title: "Plataformas de contenido",   desc: "Cualquier app con comentarios puede integrar el clasificador vía API REST." },
  ];
  return (
    <Box>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 3, lineHeight: 1.8 }}>
        HateGuard no es solo para YouTube. Es una solución genérica y reutilizable para
        cualquier plataforma que necesite moderar contenido generado por usuarios,
        disponible como <strong>API REST</strong> o interfaz visual.
      </Typography>
      <Box sx={{ display: "grid", gridTemplateColumns: "repeat(2, 1fr)", gap: 2 }}>
        {audiences.map(({ icon, title, desc }) => (
          <Box key={title} sx={{ p: 2.5, borderRadius: 3, bgcolor: "#fff", border: "1px solid #ceead6" }}>
            <Typography fontSize="1.8rem" sx={{ mb: 0.5 }}>{icon}</Typography>
            <Typography variant="subtitle2" fontWeight={700} sx={{ mb: 0.5 }}>{title}</Typography>
            <Typography variant="caption" color="text.secondary" lineHeight={1.5}>{desc}</Typography>
          </Box>
        ))}
      </Box>
    </Box>
  );
}

function SlideData() {
  const cols = [
    { label: "Idiomas",  val: "ES + EN",             icon: "🌍" },
    { label: "Clases",   val: "2 (tóxico / seguro)",  icon: "🏷️" },
    { label: "Tipos",    val: "7 categorías",         icon: "📂" },
    { label: "Técnica",  val: "Data augmentation",    icon: "🔄" },
  ];
  const types = [
    { icon: "⚧️", label: "Machista",  color: "#e040fb", desc: "Sexismo y discriminación de género" },
    { icon: "🌍", label: "Racista",   color: "#ff6d00", desc: "Odio basado en raza o etnia" },
    { icon: "🔞", label: "Sexual",    color: "#f50057", desc: "Contenido sexual inapropiado" },
    { icon: "💢", label: "Insulto",   color: "#ff4b4b", desc: "Ataques directos e insultos" },
    { icon: "🏳️‍🌈", label: "Homófobo", color: "#6a1b9a", desc: "Discriminación hacia personas LGBTQ+" },
    { icon: "🗳️", label: "Político",  color: "#1565c0", desc: "Discurso de odio con carga política" },
    { icon: "💬", label: "Normal",    color: "#90a4ae", desc: "Lenguaje cotidiano, sin odio" },
  ];
  return (
    <Box>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 3, lineHeight: 1.8 }}>
        El modelo aprende de ejemplos etiquetados. Partimos de un dataset real de YouTube
        (<strong>youtoxic_english_1000.csv</strong>) y lo ampliamos con ejemplos sintéticos
        en español mediante <strong>data augmentation</strong> (traducción + reemplazo de sinónimos).
      </Typography>
      <Box sx={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 1.5, mb: 3 }}>
        {cols.map(({ label, val, icon }) => (
          <Box key={label} sx={{ textAlign: "center", p: 2, borderRadius: 3,
              bgcolor: "#fef7e0", border: "1px solid #fdd663" }}>
            <Typography fontSize="1.5rem">{icon}</Typography>
            <Typography variant="h6" fontWeight={700} sx={{ color: "#e37400" }}>{val}</Typography>
            <Typography variant="caption" color="text.secondary">{label}</Typography>
          </Box>
        ))}
      </Box>
      <Typography variant="subtitle2" fontWeight={700} sx={{ mb: 1.5 }}>Las 5 categorías de toxicidad</Typography>
      <Box sx={{ display: "flex", flexWrap: "wrap", gap: 1 }}>
        {types.map(({ icon, label, color, desc }) => (
          <Chip key={label} label={`${icon}  ${label} — ${desc}`} size="small"
            sx={{ bgcolor: `${color}15`, color, fontWeight: 600, border: `1px solid ${color}30` }} />
        ))}
      </Box>
    </Box>
  );
}

function SlideScraper() {
  const steps = [
    { icon: "🔗", title: "URL del vídeo",       desc: 'El usuario pega la URL de YouTube: youtube.com/watch?v=...' },
    { icon: "📡", title: "youtube-comment-downloader", desc: "Librería Python que descarga comentarios sin necesitar API key ni cuenta" },
    { icon: "🔄", title: "Iteración en tiempo real", desc: "Los comentarios llegan como un generador: los procesamos uno a uno sin cargar todo en memoria" },
    { icon: "🧠", title: "Clasificación en masa",   desc: "Cada comentario pasa por el pipeline completo: clean → vectorize → predict" },
    { icon: "📊", title: "Resumen del vídeo",       desc: "Devolvemos porcentaje tóxico, conteos y lista de comentarios analizados" },
  ];
  return (
    <Box>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 3, lineHeight: 1.8 }}>
        Una de las funcionalidades del <strong>Nivel Medio</strong> del proyecto es analizar un
        vídeo completo a partir de su URL. Para ello necesitamos <strong>descargar los comentarios
        automáticamente</strong> sin usar la YouTube Data API (que tiene límites de uso).
      </Typography>
      <Box sx={{ display: "flex", flexDirection: "column", gap: 1.5, mb: 3 }}>
        {steps.map((s, i) => (
          <Box key={i} sx={{ display: "flex", alignItems: "center", gap: 2,
              p: 1.5, borderRadius: 3, bgcolor: "#fff", border: "1px solid #fad2cf" }}>
            <Box sx={{ width: 40, height: 40, borderRadius: 2, bgcolor: "#fce8e6",
                display: "flex", alignItems: "center", justifyContent: "center",
                fontSize: "1.2rem", flexShrink: 0 }}>
              {s.icon}
            </Box>
            <Box sx={{ flex: 1 }}>
              <Typography variant="subtitle2" fontWeight={700}>{s.title}</Typography>
              <Typography variant="caption" color="text.secondary">{s.desc}</Typography>
            </Box>
            {i < steps.length - 1 && (
              <ArrowForwardIcon sx={{ ml: "auto", color: "#dadce0", flexShrink: 0 }} />
            )}
          </Box>
        ))}
      </Box>
      <Box sx={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 2 }}>
        <Box sx={{ p: 1.5, borderRadius: 3, bgcolor: "#fce8e6", border: "1px solid #fad2cf" }}>
          <Typography variant="caption" fontWeight={700} color="error.main" sx={{ display: "block", mb: 0.5 }}>
            🐍 Backend (FastAPI)
          </Typography>
          <Box sx={{ fontFamily: "monospace", fontSize: "0.72rem", color: "#c5221f", lineHeight: 1.8 }}>
            POST /analyze-url<br />
            {"{ url, limit: 50 }"}<br />
            → {"{ total, toxic_count, comments[] }"}
          </Box>
        </Box>
        <Box sx={{ p: 1.5, borderRadius: 3, bgcolor: "#e8f0fe", border: "1px solid #c5d9f8" }}>
          <Typography variant="caption" fontWeight={700} color="primary" sx={{ display: "block", mb: 0.5 }}>
            ⚛️ Frontend (React)
          </Typography>
          <Box sx={{ fontFamily: "monospace", fontSize: "0.72rem", color: G_BLUE, lineHeight: 1.8 }}>
            analyzeUrl(url, limit)<br />
            → renderiza resultados<br />
            → exporta CSV
          </Box>
        </Box>
      </Box>
    </Box>
  );
}

function SlidePreprocessing() {
  const pipeline = [
    { icon: "1️⃣", step: "Minúsculas",            before: "ERES UN IDIOTA",          after: "eres un idiota" },
    { icon: "2️⃣", step: "Eliminar URLs",          before: "visita https://x.com",    after: "visita" },
    { icon: "3️⃣", step: "Eliminar @menciones",    before: "@usuario mira esto",      after: "mira esto" },
    { icon: "4️⃣", step: "Eliminar HTML/emojis",   before: "<b>texto</b> 😡",         after: "texto" },
    { icon: "5️⃣", step: "Solo letras (regex)",    before: "hola!! qué123 tal???",    after: "hola qu tal" },
    { icon: "6️⃣", step: "Eliminar stopwords",     before: "hola qu tal est",         after: "tal" },
    { icon: "7️⃣", step: "Lematización (NLTK)",    before: "running hates idiots",    after: "run hate idiot" },
  ];
  return (
    <Box>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 2, lineHeight: 1.8 }}>
        Los modelos de ML <strong>no entienden texto crudo</strong>. Hay que convertirlo en
        una forma estándar y reducida. Cada paso del pipeline elimina ruido innecesario y
        deja solo las palabras con carga semántica real.
      </Typography>
      <Box sx={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 1 }}>
        {pipeline.map(({ icon, step, before, after }) => (
          <Box key={step} sx={{ display: "flex", alignItems: "center", gap: 1.5,
              p: 1.2, borderRadius: 2.5, bgcolor: "#f8f9fa", border: "1px solid #e8eaed" }}>
            <Typography fontSize="1rem" flexShrink={0}>{icon}</Typography>
            <Box sx={{ flex: 1, minWidth: 0 }}>
              <Typography variant="caption" fontWeight={700} color="text.primary"
                sx={{ display: "block" }}>{step}</Typography>
              <Typography variant="caption" sx={{ fontFamily: "monospace", color: G_RED,
                display: "block", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                ✗ {before}
              </Typography>
              <Typography variant="caption" sx={{ fontFamily: "monospace", color: G_GREEN, display: "block" }}>
                ✓ {after}
              </Typography>
            </Box>
          </Box>
        ))}
      </Box>
      <Alert_ color={G_BLUE} bg="#e8f0fe" mt>
        🔬 Usamos <strong>NLTK</strong> (lematización + stopwords) y <strong>expresiones regulares</strong>
        {" "}(regex) para la limpieza. El resultado son textos normalizados y sin ruido.
      </Alert_>
    </Box>
  );
}

function SlideModel() {
  return (
    <Box>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 3, lineHeight: 1.8 }}>
        El corazón del sistema son dos técnicas combinadas en un <strong>pipeline</strong>:
        primero convertimos el texto en números (vectorización), luego un clasificador
        decide si el texto es tóxico o no.
      </Typography>
      <Box sx={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 2, mb: 3 }}>
        <Box sx={{ p: 2.5, borderRadius: 3, bgcolor: "#f3e5f5", border: "1px solid #ce93d8" }}>
          <Typography variant="subtitle1" fontWeight={800} sx={{ color: "#9c27b0", mb: 1 }}>
            📐 TF-IDF — Vectorización
          </Typography>
          <Typography variant="body2" color="text.secondary" lineHeight={1.7} sx={{ mb: 1.5 }}>
            Convierte cada comentario en un vector de números.
            Las palabras <strong>raras pero significativas</strong> (insultos concretos)
            obtienen pesos altos. Las palabras comunes ("el", "de") obtienen pesos bajos.
          </Typography>
          <Box sx={{ p: 1.2, borderRadius: 2, bgcolor: "#fff", fontFamily: "monospace",
              fontSize: "0.73rem", color: "#9c27b0", lineHeight: 1.8 }}>
            "odio"  → peso 0.87<br />
            "eres"  → peso 0.12<br />
            "tonto" → peso 0.64
          </Box>
        </Box>
        <Box sx={{ p: 2.5, borderRadius: 3, bgcolor: "#e8f0fe", border: "1px solid #a8c7fa" }}>
          <Typography variant="subtitle1" fontWeight={800} sx={{ color: G_BLUE, mb: 1 }}>
            🧠 Regresión Logística
          </Typography>
          <Typography variant="body2" color="text.secondary" lineHeight={1.7} sx={{ mb: 1.5 }}>
            Un clasificador clásico de ML. Aprende qué combinaciones de palabras son típicas
            de comentarios tóxicos, y devuelve una <strong>probabilidad de toxicidad</strong>
            entre 0 y 1.
          </Typography>
          <Box sx={{ p: 1.2, borderRadius: 2, bgcolor: "#fff", fontFamily: "monospace",
              fontSize: "0.73rem", color: G_BLUE, lineHeight: 1.8 }}>
            vector(comentario)<br />
            → P(tóxico) = 0.92<br />
            → Resultado: TÓXICO ✓
          </Box>
        </Box>
      </Box>
      <Alert_ color="#9c27b0" bg="#f3e5f5">
        💡 Usamos <strong>bigramas</strong> (pares de palabras como "te odio") además de palabras
        sueltas. Esto permite capturar frases de odio compuestas que una palabra sola no detectaría.
      </Alert_>
    </Box>
  );
}

function SlideOptuna() {
  const trials = [
    { trial: 1,  params: 'C=0.01, max_f=5000, ngram=(1,1)',  score: 78 },
    { trial: 8,  params: 'C=0.5,  max_f=8000, ngram=(1,2)',  score: 85 },
    { trial: 23, params: 'C=1.0,  max_f=10000, ngram=(1,2)', score: 91 },
    { trial: 41, params: 'C=2.0,  max_f=10000, ngram=(1,2)', score: 90 },
  ];
  return (
    <Box>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 2.5, lineHeight: 1.8 }}>
        Los modelos de ML tienen <strong>hiperparámetros</strong>: ajustes de configuración que
        no se aprenden del dataset (como la "C" de la Regresión Logística, o el número máximo
        de palabras del TF-IDF). Probarlos manualmente sería interminable.
        <strong> Optuna automatiza esta búsqueda.</strong>
      </Typography>
      <Box sx={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 2, mb: 2.5 }}>
        <Box sx={{ p: 2, borderRadius: 3, bgcolor: "#e0f7fa", border: "1px solid #80deea" }}>
          <Typography variant="subtitle2" fontWeight={800} sx={{ color: "#0097a7", mb: 1 }}>
            🔁 ¿Cómo funciona Optuna?
          </Typography>
          {[
            "Define un rango de valores posibles para cada parámetro",
            "Lanza N pruebas (trials) con combinaciones distintas",
            "Cada trial mide la métrica objetivo (F1-score)",
            "Optuna aprende qué zonas explorar más (Bayesian search)",
            "Al final devuelve la mejor combinación encontrada",
          ].map((t, i) => (
            <Box key={i} sx={{ display: "flex", gap: 1, mb: 0.5 }}>
              <Typography variant="caption" sx={{ color: "#0097a7", fontWeight: 700, flexShrink: 0 }}>
                {i + 1}.
              </Typography>
              <Typography variant="caption" color="text.secondary">{t}</Typography>
            </Box>
          ))}
        </Box>
        <Box sx={{ p: 2, borderRadius: 3, bgcolor: "#f8f9fa", border: "1px solid #e8eaed" }}>
          <Typography variant="subtitle2" fontWeight={800} sx={{ color: "#5f6368", mb: 1.5 }}>
            📈 Evolución de trials (ejemplo)
          </Typography>
          {trials.map(({ trial, params, score }) => (
            <Box key={trial} sx={{ mb: 1 }}>
              <Box sx={{ display: "flex", justifyContent: "space-between", mb: 0.3 }}>
                <Typography variant="caption" sx={{ fontFamily: "monospace", color: "#5f6368" }}>
                  Trial {trial}
                </Typography>
                <Typography variant="caption" fontWeight={700}
                  sx={{ color: score >= 90 ? G_GREEN : score >= 85 ? G_YELLOW : G_RED }}>
                  {score}%
                </Typography>
              </Box>
              <LinearProgress variant="determinate" value={score}
                sx={{ height: 5, borderRadius: 100, bgcolor: "#e8eaed",
                  "& .MuiLinearProgress-bar": {
                    bgcolor: score >= 90 ? G_GREEN : score >= 85 ? "#e37400" : G_RED,
                  }}} />
            </Box>
          ))}
        </Box>
      </Box>
      <Typography variant="subtitle2" fontWeight={700} sx={{ mb: 1 }}>
        Mejor configuración encontrada por Optuna
      </Typography>
      <Box sx={{ display: "flex", flexWrap: "wrap", gap: 1 }}>
        {Object.entries({
          "C = 1.0": "Regularización del modelo",
          "max_features = 10K": "Vocabulario máximo TF-IDF",
          "ngram_range (1,2)": "Palabras y bigramas",
          "sublinear_tf = True": "Suavizado de frecuencias",
          "solver = lbfgs": "Algoritmo de optimización",
        }).map(([p, desc]) => (
          <Chip key={p} label={`${p} — ${desc}`} size="small"
            sx={{ fontFamily: "monospace", bgcolor: "#e0f7fa", color: "#0097a7",
                  border: "1px solid #80deea", fontWeight: 600, fontSize: "0.68rem" }} />
        ))}
      </Box>
    </Box>
  );
}

function SlideResults() {
  const metrics = [
    { label: "Accuracy — entrenamiento", val: 94, color: G_BLUE  },
    { label: "Accuracy — test",          val: 91, color: G_GREEN },
    { label: "F1-score (media)",         val: 90, color: "#9c27b0" },
    { label: "Diferencia train / test",  val: 3,  color: "#e37400", max: 10,
      note: "← límite 5pp ✅" },
  ];
  return (
    <Box>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 3, lineHeight: 1.8 }}>
        El requisito más importante del proyecto es controlar el <strong>overfitting</strong>:
        que el modelo no solo memorice los datos de entrenamiento sino que <em>generalice</em>
        a comentarios nuevos. La diferencia entre métricas de train y test debe ser
        <strong> menor de 5 puntos porcentuales</strong>.
      </Typography>
      <Box sx={{ display: "flex", flexDirection: "column", gap: 2.5, mb: 3 }}>
        {metrics.map(({ label, val, color, max = 100, note }) => (
          <Box key={label}>
            <Box sx={{ display: "flex", justifyContent: "space-between", mb: 0.5 }}>
              <Typography variant="caption" fontWeight={600} color="text.secondary">{label}</Typography>
              <Typography variant="caption" fontWeight={800} sx={{ color }}>
                {val}{max === 100 ? "%" : " pp"}{" "}
                {note && <span style={{ color: G_GREEN }}>{note}</span>}
              </Typography>
            </Box>
            <LinearProgress variant="determinate" value={(val / max) * 100}
              sx={{ height: 8, borderRadius: 100, bgcolor: `${color}20`,
                "& .MuiLinearProgress-bar": { bgcolor: color } }} />
          </Box>
        ))}
      </Box>
      <Alert_ color={G_GREEN} bg="#e6f4ea">
        ✅ <strong>Nivel esencial superado:</strong> la diferencia train–test es de solo 3 puntos
        porcentuales (el límite es 5). El modelo generaliza bien y no memoriza los datos de entrenamiento.
      </Alert_>
    </Box>
  );
}

function SlideSummary() {
  const achieved = [
    { level: "🟢 Esencial",  items: [
        "Modelo ML clasificación binaria", "Overfitting controlado (3pp diff.)",
        "API REST FastAPI + interfaz React", "Repositorio Git organizado", "README documentado",
        "7 categorías de toxicidad (incl. homófobo y político)",
      ]},
    { level: "🟡 Medio",     items: [
        "Análisis por URL de vídeo YouTube", "Tests unitarios con Pytest",
        "Optimización hiperparámetros con Optuna",
      ]},
    { level: "🟠 Avanzado",  items: [
        "App Dockerizada (docker-compose)", "Despliegue público (en progreso)",
      ]},
  ];
  const tech = [
    { icon: "🐍", label: "Python" },    { icon: "⚛️",  label: "React + Vite" },
    { icon: "⚡", label: "FastAPI" },    { icon: "🧠",  label: "Scikit-learn" },
    { icon: "📝", label: "NLTK" },      { icon: "🔢",  label: "TF-IDF" },
    { icon: "🔁", label: "Optuna" },    { icon: "📡",  label: "Scraper YT" },
    { icon: "🐋", label: "Docker" },    { icon: "🧪",  label: "Pytest" },
  ];
  return (
    <Box>
      <Box sx={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 2, mb: 3 }}>
        {achieved.map(({ level, items }) => (
          <Box key={level} sx={{ p: 2, borderRadius: 3, bgcolor: "#fff", border: "1px solid #e8eaed" }}>
            <Typography variant="subtitle2" fontWeight={700} sx={{ mb: 1.5 }}>{level}</Typography>
            {items.map(item => (
              <Box key={item} sx={{ display: "flex", alignItems: "flex-start", gap: 0.8, mb: 0.6 }}>
                <CheckCircleIcon sx={{ fontSize: "0.9rem", color: G_GREEN, mt: 0.1, flexShrink: 0 }} />
                <Typography variant="caption" color="text.secondary" lineHeight={1.4}>{item}</Typography>
              </Box>
            ))}
          </Box>
        ))}
      </Box>
      <Typography variant="subtitle2" fontWeight={700} sx={{ mb: 1.5 }}>Stack tecnológico completo</Typography>
      <Box sx={{ display: "flex", flexWrap: "wrap", gap: 1 }}>
        {tech.map(({ icon, label }) => (
          <Chip key={label} label={`${icon}  ${label}`} size="small"
            sx={{ bgcolor: "#e8f0fe", color: G_BLUE, fontWeight: 600, border: "1px solid #c5d9f8" }} />
        ))}
      </Box>
    </Box>
  );
}

// ── Shared alert ───────────────────────────────────────────────────────────────
function Alert_({ color, bg, children, mt }) {
  return (
    <Box sx={{ mt: mt ? 2 : 0, p: 1.5, borderRadius: 3, bgcolor: bg, border: `1px solid ${color}30` }}>
      <Typography variant="caption" lineHeight={1.6} color="text.secondary">{children}</Typography>
    </Box>
  );
}

// ── Main component ─────────────────────────────────────────────────────────────
export default function PresentationTab() {
  const [current, setCurrent] = useState(0);
  const [dir,     setDir]     = useState(1);

  function go(n) { setDir(n > current ? 1 : -1); setCurrent(n); }
  function next() { if (current < SLIDES.length - 1) go(current + 1); }
  function prev() { if (current > 0) go(current - 1); }

  const slide = SLIDES[current];
  const Body  = slide.body;

  return (
    <Box>
      {/* ── Info banner ── */}
      <Box sx={{ display: "flex", alignItems: "center", justifyContent: "space-between",
          mb: 2.5, p: 1.5, borderRadius: 3, bgcolor: "#e8f0fe", border: "1px solid #c5d9f8" }}>
        <Button variant="outlined" color="primary" startIcon={<ArrowBackIcon />}
          onClick={prev} disabled={current === 0} size="small" sx={{ borderRadius: 100 }}>
          Anterior
        </Button>
        <Box sx={{ display: "flex", alignItems: "center", gap: 1.5 }}>
          <Typography variant="caption" color="primary" fontWeight={600}>
            🎤 Presentación técnica · 10 diapositivas
          </Typography>
          <Chip label={`${current + 1} / ${SLIDES.length}`} size="small"
            sx={{ bgcolor: `${slide.color}18`, color: slide.color, fontWeight: 700 }} />
        </Box>
        <Button variant="outlined" color="primary" endIcon={<ArrowForwardIcon />}
          onClick={next} disabled={current === SLIDES.length - 1} size="small" sx={{ borderRadius: 100 }}>
          Siguiente
        </Button>
      </Box>

      {/* ── Slide picker ── */}
      <Box sx={{ display: "flex", gap: 1, mb: 3, flexWrap: "wrap" }}>
        {SLIDES.map((s, i) => (
          <Button key={i} size="small"
            variant={i === current ? "contained" : "outlined"}
            onClick={() => go(i)}
            sx={{
              borderRadius: 100, minWidth: 0, px: 1.5, fontSize: "0.72rem",
              ...(i === current
                ? { bgcolor: s.color, "&:hover": { bgcolor: s.color } }
                : { borderColor: "#dadce0", color: "#5f6368",
                    "&:hover": { borderColor: s.color, color: s.color, bgcolor: s.bg } }
              ),
            }}>
            {s.tag}
          </Button>
        ))}
      </Box>

      {/* ── Slide card ── */}
      <Box sx={{ position: "relative", overflow: "hidden", minHeight: 540 }}>
        <AnimatePresence mode="wait" custom={dir}>
          <motion.div key={current}
            custom={dir}
            variants={{
              enter:  d => ({ x: d > 0 ?  60 : -60, opacity: 0 }),
              center:    { x: 0, opacity: 1 },
              exit:   d => ({ x: d > 0 ? -60 :  60, opacity: 0 }),
            }}
            initial="enter" animate="center" exit="exit"
            transition={{ duration: 0.28, ease: "easeInOut" }}>

            <Card elevation={0} sx={{ border: "1px solid #e8eaed" }}>
              {/* Header */}
              <Box sx={{
                background: `linear-gradient(135deg, ${slide.bg} 0%, #fff 100%)`,
                borderBottom: "1px solid #e8eaed",
                px: 4, py: 3,
                display: "flex", alignItems: "center", gap: 2,
              }}>
                <Box sx={{ width: 56, height: 56, borderRadius: 3, bgcolor: "#fff",
                    boxShadow: `0 2px 8px ${slide.color}30`,
                    display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
                  {slide.icon}
                </Box>
                <Box sx={{ flex: 1 }}>
                  <Typography variant="h5" fontWeight={800} color="text.primary" lineHeight={1.2}>
                    {slide.title}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ mt: 0.3 }}>
                    {slide.subtitle}
                  </Typography>
                </Box>
              </Box>

              {/* Body */}
              <CardContent sx={{ p: 4 }}>
                <Body />
              </CardContent>
            </Card>
          </motion.div>
        </AnimatePresence>
      </Box>

      {/* ── Navigation ── */}
      <Box sx={{ display: "flex", alignItems: "center", justifyContent: "space-between", mt: 3 }}>
        <Button variant="outlined" color="primary" startIcon={<ArrowBackIcon />}
          onClick={prev} disabled={current === 0} sx={{ borderRadius: 100 }}>
          Anterior
        </Button>

        <Stack direction="row" spacing={0.8} alignItems="center">
          {SLIDES.map((s, i) => (
            <Box key={i} onClick={() => go(i)} sx={{
              width: i === current ? 24 : 8, height: 8, borderRadius: 100,
              bgcolor: i === current ? slide.color : "#dadce0",
              cursor: "pointer", transition: "all 0.3s ease",
            }} />
          ))}
        </Stack>

        <Button
          variant={current === SLIDES.length - 1 ? "contained" : "outlined"}
          color="primary" endIcon={<ArrowForwardIcon />}
          onClick={next} disabled={current === SLIDES.length - 1}
          sx={{ borderRadius: 100 }}>
          Siguiente
        </Button>
      </Box>
    </Box>
  );
}
