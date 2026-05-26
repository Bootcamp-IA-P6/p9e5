import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Box, Card, CardContent, Typography, TextField, Button,
  ButtonGroup, LinearProgress, Chip, Alert, AlertTitle,
  Collapse, Divider,
} from "@mui/material";
import {
  Search as SearchIcon,
  CheckCircle as CheckCircleIcon,
  WarningAmber as WarningAmberIcon,
  InfoOutlined as InfoOutlinedIcon,
  Code as CodeIcon,
  ExpandMore as ExpandMoreIcon,
  LightbulbOutlined as LightbulbOutlinedIcon,
} from "@mui/icons-material";
import { TYPE_CONFIG, EXAMPLES } from "../constants";

const TYPE_DESCRIPTIONS = {
  machista:             "Lenguaje sexista o discriminatorio hacia la mujer",
  racista:              "Contenido basado en raza, etnia o nacionalidad",
  sexual:               "Contenido sexual explícito o acoso sexual",
  insulto:              "Insultos directos, amenazas o lenguaje agresivo",
  homofobo:             "Odio o discriminación hacia personas LGBTQ+",
  politico:             "Discurso de odio con motivación o contenido político",
  "lenguaje cotidiano": "Sin categoría tóxica específica detectada",
};

export default function AnalyzeTab({ onAnalyze }) {
  const [text,     setText]     = useState("");
  const [loading,  setLoading]  = useState(false);
  const [result,   setResult]   = useState(null);
  const [showType, setShowType] = useState(false);
  const [showCode, setShowCode] = useState(false);
  const [error,    setError]    = useState(null);

  async function handleSubmit() {
    if (!text.trim()) { setError("Escribe un comentario antes de analizar."); return; }
    setError(null);
    setLoading(true);
    try {
      const data = await onAnalyze(text);
      setResult(data);
      setShowType(false);
      setShowCode(false);
    } catch {
      setError("No se pudo conectar con la API. ¿Está corriendo el backend en :8000?");
    } finally {
      setLoading(false);
    }
  }

  function loadExample(type) {
    setText(EXAMPLES[type]);
    setResult(null);
    setError(null);
  }

  const cfg = result ? (TYPE_CONFIG[result.toxicity_type] ?? TYPE_CONFIG["lenguaje cotidiano"]) : null;

  return (
    <Box sx={{ display: "grid", gridTemplateColumns: { md: "1.15fr 1fr" }, gap: 3 }}>
      {/* ── Input Card ── */}
      <Card elevation={0}>
        <CardContent sx={{ p: 3 }}>
          <Typography variant="overline" color="text.secondary" sx={{ letterSpacing: 1.5 }}>
            ✍️ Introduce un comentario
          </Typography>
          <TextField
            multiline minRows={7} fullWidth
            variant="outlined"
            placeholder="Pega aquí el comentario de YouTube que quieres analizar…"
            value={text}
            onChange={e => setText(e.target.value)}
            inputProps={{ maxLength: 1000 }}
            sx={{ mt: 1.5, mb: 0.5 }}
            helperText={`${text.length} / 1000 caracteres`}
          />
          <ButtonGroup fullWidth size="small" variant="outlined" sx={{ mb: 2 }}>
            <Button color="success" startIcon={<CheckCircleIcon />}
              onClick={() => loadExample("safe")}
              sx={{ borderRadius: "12px 0 0 12px !important" }}>
              Ejemplo seguro
            </Button>
            <Button color="error" startIcon={<WarningAmberIcon />}
              onClick={() => loadExample("toxic")}
              sx={{ borderRadius: "0 12px 12px 0 !important" }}>
              Ejemplo tóxico
            </Button>
          </ButtonGroup>
          <Collapse in={!!error}>
            <Alert severity="warning" sx={{ mb: 2, borderRadius: 3 }} onClose={() => setError(null)}>
              {error}
            </Alert>
          </Collapse>
          <Button
            variant="contained" color="primary" fullWidth size="large"
            startIcon={loading ? undefined : <SearchIcon />}
            onClick={handleSubmit}
            disabled={loading || !text.trim()}
            sx={{ py: 1.4, fontSize: "1rem" }}>
            {loading ? "Analizando…" : "Analizar comentario"}
          </Button>
          {loading && <LinearProgress sx={{ mt: 1, borderRadius: 100 }} />}
          <Box sx={{
            display: "flex", alignItems: "flex-start", gap: 1, mt: 2,
            p: 1.5, borderRadius: 3, bgcolor: "#e8f0fe", border: "1px solid #c5d9f8",
          }}>
            <LightbulbOutlinedIcon sx={{ fontSize: "1.1rem", color: "primary.main", mt: 0.1 }} />
            <Typography variant="caption" color="text.secondary" lineHeight={1.5}>
              <strong style={{ color: "#1a73e8" }}>Tip:</strong> Funciona en inglés y español.
              El modelo detecta 7 tipos de toxicidad distintos.
            </Typography>
          </Box>
        </CardContent>
      </Card>

      {/* ── Result Card ── */}
      <Card elevation={0}>
        <CardContent sx={{ p: 3 }}>
          <Typography variant="overline" color="text.secondary" sx={{ letterSpacing: 1.5 }}>
            📊 Resultado del análisis
          </Typography>
          <AnimatePresence mode="wait">
            {!result && !loading && (
              <motion.div key="empty"
                initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                <Box sx={{
                  display: "flex", flexDirection: "column", alignItems: "center",
                  justifyContent: "center", minHeight: 260, gap: 2, color: "text.secondary",
                }}>
                  <Box sx={{
                    width: 72, height: 72, borderRadius: "50%",
                    bgcolor: "#e8f0fe", border: "1px solid #c5d9f8",
                    display: "flex", alignItems: "center", justifyContent: "center",
                    fontSize: "2rem",
                  }}>
                    🔍
                  </Box>
                  <Typography variant="body2" textAlign="center" color="text.secondary">
                    Introduce un comentario<br />y pulsa <strong>Analizar</strong>
                  </Typography>
                </Box>
              </motion.div>
            )}
            {result && (
              <motion.div key="result"
                initial={{ opacity: 0, y: 16 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -8 }}
                transition={{ duration: 0.3 }}>
                <Alert
                  severity={result.toxic ? "error" : "success"}
                  variant="outlined"
                  icon={result.toxic ? <WarningAmberIcon /> : <CheckCircleIcon />}
                  sx={{ mb: 2, borderRadius: 3, alignItems: "flex-start" }}>
                  <AlertTitle sx={{ fontWeight: 800, letterSpacing: 0.5 }}>
                    {result.toxic ? "CONTENIDO TÓXICO" : "COMENTARIO SEGURO"}
                  </AlertTitle>
                  <Typography variant="body2">
                    {result.toxic
                      ? "Este comentario contiene lenguaje tóxico detectado por el modelo."
                      : "Este comentario parece seguro. No se detectó lenguaje ofensivo."}
                  </Typography>
                </Alert>
                <Box sx={{ mb: 2 }}>
                  <Box sx={{ display: "flex", justifyContent: "space-between", mb: 0.8 }}>
                    <Typography variant="caption" color="text.secondary">Confianza del modelo</Typography>
                    <Typography variant="caption" fontWeight={700}
                      sx={{ color: result.toxic ? "error.main" : "success.main" }}>
                      {result.confidence_pct}%
                    </Typography>
                  </Box>
                  <LinearProgress variant="determinate" value={result.confidence_pct}
                    sx={{
                      "& .MuiLinearProgress-bar": {
                        background: result.toxic
                          ? "linear-gradient(90deg, #c5221f, #ea4335)"
                          : "linear-gradient(90deg, #137333, #34a853)",
                      },
                    }} />
                </Box>
                <Box sx={{
                  mb: 2, p: 1.8, borderRadius: 3,
                  bgcolor: `${cfg.color}12`, border: `1px solid ${cfg.color}30`,
                  display: "flex", alignItems: "center", gap: 1.5,
                }}>
                  <Box sx={{
                    width: 44, height: 44, borderRadius: 2.5,
                    bgcolor: `${cfg.color}20`,
                    display: "flex", alignItems: "center", justifyContent: "center",
                    fontSize: "1.4rem", flexShrink: 0,
                  }}>
                    {cfg.icon}
                  </Box>
                  <Box>
                    <Typography variant="caption" fontWeight={700} sx={{
                      color: cfg.color, textTransform: "uppercase", letterSpacing: 1.5,
                    }}>
                      Tipo detectado · ML Multiclase
                    </Typography>
                    <Typography variant="subtitle2" fontWeight={700} sx={{ color: cfg.color }}>
                      {cfg.label}
                    </Typography>
                  </Box>
                </Box>
                <Divider sx={{ mb: 1.5 }} />
                <Box sx={{ display: "flex", flexDirection: "column", gap: 1 }}>
                  <Button fullWidth variant="outlined" size="small" color="primary"
                    startIcon={<InfoOutlinedIcon />}
                    endIcon={<ExpandMoreIcon sx={{
                      transform: showType ? "rotate(180deg)" : "none",
                      transition: "transform 0.2s",
                    }} />}
                    onClick={() => setShowType(v => !v)}
                    sx={{ justifyContent: "space-between", borderRadius: 2.5, px: 1.5 }}>
                    ¿Qué significa cada tipo?
                  </Button>
                  <Collapse in={showType}>
                    <Box sx={{
                      mt: 1, p: 1.5, borderRadius: 3,
                      bgcolor: "#f8f9fa", border: "1px solid #e8eaed",
                    }}>
                      {Object.entries(TYPE_CONFIG).map(([k, v]) => (
                        <Box key={k} sx={{ display: "flex", alignItems: "center", gap: 1.5, py: 0.7 }}>
                          <Typography fontSize="1.1rem">{v.icon}</Typography>
                          <Typography variant="body2" fontWeight={700}
                            sx={{ color: v.color, minWidth: 100 }}>
                            {v.label}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {TYPE_DESCRIPTIONS[k]}
                          </Typography>
                        </Box>
                      ))}
                    </Box>
                  </Collapse>
                  <Button fullWidth variant="outlined" size="small" color="primary"
                    startIcon={<CodeIcon />}
                    endIcon={<ExpandMoreIcon sx={{
                      transform: showCode ? "rotate(180deg)" : "none",
                      transition: "transform 0.2s",
                    }} />}
                    onClick={() => setShowCode(v => !v)}
                    sx={{ justifyContent: "space-between", borderRadius: 2.5, px: 1.5 }}>
                    Ver texto preprocesado
                  </Button>
                  <Collapse in={showCode}>
                    <Box sx={{
                      mt: 1, p: 1.5, borderRadius: 3,
                      bgcolor: "#f1f3f4", border: "1px solid #e8eaed",
                      fontFamily: "'Courier New', monospace", fontSize: "0.8rem",
                      color: "#202124", wordBreak: "break-all", lineHeight: 1.6,
                    }}>
                      {result.cleaned_text || "(texto vacío tras preprocesamiento)"}
                    </Box>
                  </Collapse>
                </Box>
              </motion.div>
            )}
          </AnimatePresence>
        </CardContent>
      </Card>
    </Box>
  );
}
