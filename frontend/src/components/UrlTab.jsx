import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Box, Card, CardContent, Typography, TextField, Button,
  LinearProgress, Chip, Alert, Slider, Divider,
  CircularProgress,
} from "@mui/material";
import {
  YouTube as YouTubeIcon,
  WarningAmber as WarningAmberIcon,
  CheckCircle as CheckCircleIcon,
  Search as SearchIcon,
  FileDownload as FileDownloadIcon,
} from "@mui/icons-material";
import { analyzeUrl } from "../api";
import { TYPE_CONFIG } from "../constants";

const G_RED   = "#ea4335";
const G_GREEN = "#34a853";
const G_BLUE  = "#1a73e8";

export default function UrlTab() {
  const [url,     setUrl]     = useState("");
  const [limit,   setLimit]   = useState(50);
  const [loading, setLoading] = useState(false);
  const [result,  setResult]  = useState(null);
  const [error,   setError]   = useState(null);

  async function handleAnalyze() {
    if (!url.trim() || !url.includes("youtube")) {
      setError("Introduce una URL válida de YouTube (ej: https://www.youtube.com/watch?v=...)");
      return;
    }
    setError(null);
    setLoading(true);
    setResult(null);
    try {
      const data = await analyzeUrl(url.trim(), limit);
      setResult(data);
    } catch (e) {
      setError(e.message || "No se pudo analizar el video. Comprueba la URL e inténtalo de nuevo.");
    } finally {
      setLoading(false);
    }
  }

  function exportCSV() {
    if (!result) return;
    const header = "Comentario,Tóxico,Tipo,Confianza\n";
    const rows = result.comments.map(c =>
      `"${c.text.replace(/"/g, '""')}","${c.toxic ? "Sí" : "No"}","${c.toxicity_type}","${c.confidence_pct}%"`
    ).join("\n");
    const blob = new Blob([header + rows], { type: "text/csv;charset=utf-8;" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = "analisis_video.csv";
    a.click();
  }

  return (
    <Box sx={{ display: "flex", flexDirection: "column", gap: 3 }}>

      {/* ── Input card ── */}
      <Card elevation={0}>
        <CardContent sx={{ p: 3 }}>
          <Box sx={{ display: "flex", alignItems: "center", gap: 1.5, mb: 2 }}>
            <Box sx={{
              width: 44, height: 44, borderRadius: 2, bgcolor: "#fce8e6",
              display: "flex", alignItems: "center", justifyContent: "center",
            }}>
              <YouTubeIcon sx={{ color: G_RED, fontSize: "1.5rem" }} />
            </Box>
            <Box>
              <Typography variant="subtitle1" fontWeight={700}>Analizar vídeo de YouTube</Typography>
              <Typography variant="caption" color="text.secondary">
                Introduce la URL de un vídeo y analizaremos sus comentarios en masa
              </Typography>
            </Box>
          </Box>

          <TextField
            fullWidth
            variant="outlined"
            placeholder="https://www.youtube.com/watch?v=..."
            value={url}
            onChange={e => { setUrl(e.target.value); setError(null); }}
            InputProps={{
              startAdornment: (
                <YouTubeIcon sx={{ color: G_RED, mr: 1, flexShrink: 0 }} />
              ),
            }}
            sx={{ mb: 2.5 }}
          />

          <Box sx={{ mb: 2.5 }}>
            <Typography variant="caption" color="text.secondary" sx={{ mb: 1, display: "block" }}>
              Número máximo de comentarios a analizar: <strong>{limit}</strong>
            </Typography>
            <Slider
              value={limit}
              onChange={(_, v) => setLimit(v)}
              min={10} max={200} step={10}
              marks={[
                { value: 10,  label: "10"  },
                { value: 50,  label: "50"  },
                { value: 100, label: "100" },
                { value: 200, label: "200" },
              ]}
              valueLabelDisplay="auto"
              color="primary"
            />
          </Box>

          {error && (
            <Alert severity="warning" sx={{ mb: 2, borderRadius: 3 }} onClose={() => setError(null)}>
              {error}
            </Alert>
          )}

          <Button
            variant="contained" color="primary" fullWidth size="large"
            startIcon={loading ? <CircularProgress size={18} color="inherit" /> : <SearchIcon />}
            onClick={handleAnalyze}
            disabled={loading || !url.trim()}
            sx={{ py: 1.4, fontSize: "1rem" }}>
            {loading ? `Analizando comentarios…` : "Analizar vídeo"}
          </Button>
          {loading && <LinearProgress sx={{ mt: 1, borderRadius: 100 }} />}

          <Box sx={{ mt: 2, p: 1.5, borderRadius: 3, bgcolor: "#fef7e0", border: "1px solid #fdd663" }}>
            <Typography variant="caption" color="text.secondary" lineHeight={1.5}>
              ⚠️ <strong style={{ color: "#e37400" }}>Nota:</strong> El análisis puede tardar
              unos segundos dependiendo del número de comentarios y la velocidad de la conexión.
              Algunos vídeos con comentarios desactivados no pueden analizarse.
            </Typography>
          </Box>
        </CardContent>
      </Card>

      {/* ── Results ── */}
      <AnimatePresence>
        {result && (
          <motion.div key="result"
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.3 }}>

            {/* Summary bar */}
            <Card elevation={0} sx={{ mb: 2.5 }}>
              <CardContent sx={{ p: 3 }}>
                <Box sx={{ display: "flex", alignItems: "center", justifyContent: "space-between", mb: 2 }}>
                  <Typography variant="h6" fontWeight={700}>
                    📊 Resumen del análisis
                  </Typography>
                  <Button variant="outlined" color="primary" size="small"
                    startIcon={<FileDownloadIcon />} onClick={exportCSV}
                    sx={{ borderRadius: 100 }}>
                    Exportar CSV
                  </Button>
                </Box>

                <Box sx={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 2, mb: 2.5 }}>
                  {[
                    { val: result.total,      lbl: "Analizados",  color: G_BLUE,  bg: "#e8f0fe" },
                    { val: result.toxic_count, lbl: "Tóxicos",    color: G_RED,   bg: "#fce8e6" },
                    { val: result.safe_count,  lbl: "Seguros",    color: G_GREEN, bg: "#e6f4ea" },
                    { val: `${result.toxic_pct}%`, lbl: "Tasa tóxica", color: "#e37400", bg: "#fef7e0" },
                  ].map(({ val, lbl, color, bg }) => (
                    <Box key={lbl} sx={{
                      bgcolor: bg, borderRadius: 3, px: 2, py: 1.5, textAlign: "center",
                      border: `1px solid ${color}30`,
                    }}>
                      <Typography variant="h5" fontWeight={800} sx={{ color }}>{val}</Typography>
                      <Typography variant="caption" color="text.secondary">{lbl}</Typography>
                    </Box>
                  ))}
                </Box>

                {/* Toxic rate bar */}
                <Box>
                  <Box sx={{ display: "flex", justifyContent: "space-between", mb: 0.5 }}>
                    <Typography variant="caption" color="text.secondary">Tasa de toxicidad en el vídeo</Typography>
                    <Typography variant="caption" fontWeight={700}
                      sx={{ color: result.toxic_pct > 30 ? G_RED : G_GREEN }}>
                      {result.toxic_pct}%
                    </Typography>
                  </Box>
                  <LinearProgress variant="determinate" value={result.toxic_pct}
                    sx={{
                      height: 8, borderRadius: 100,
                      bgcolor: "#e6f4ea",
                      "& .MuiLinearProgress-bar": {
                        background: result.toxic_pct > 30
                          ? `linear-gradient(90deg, ${G_RED}, #ff6d00)`
                          : `linear-gradient(90deg, ${G_GREEN}, #1e8e3e)`,
                      },
                    }} />
                </Box>
              </CardContent>
            </Card>

            {/* Comment list */}
            <Card elevation={0}>
              <CardContent sx={{ p: 3 }}>
                <Typography variant="subtitle1" fontWeight={700} sx={{ mb: 2 }}>
                  💬 Comentarios analizados
                </Typography>
                <Box sx={{ display: "flex", flexDirection: "column", gap: 1 }}>
                  {result.comments.map((c, i) => {
                    const cfg = TYPE_CONFIG[c.toxicity_type] ?? TYPE_CONFIG["lenguaje cotidiano"];
                    return (
                      <motion.div key={i}
                        initial={{ opacity: 0, x: -8 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: i * 0.02, duration: 0.15 }}>
                        <Box sx={{
                          p: 1.5, borderRadius: 2.5,
                          bgcolor: c.toxic ? "#fce8e6" : "#f8f9fa",
                          borderLeft: `3px solid ${c.toxic ? G_RED : "#dadce0"}`,
                          display: "flex", alignItems: "flex-start", gap: 1.5,
                          "&:hover": { bgcolor: c.toxic ? "#fad2cf" : "#f1f3f4" },
                          transition: "background 0.15s",
                        }}>
                          {c.toxic
                            ? <WarningAmberIcon sx={{ color: G_RED, flexShrink: 0, mt: 0.2, fontSize: "1rem" }} />
                            : <CheckCircleIcon sx={{ color: G_GREEN, flexShrink: 0, mt: 0.2, fontSize: "1rem" }} />
                          }
                          <Typography variant="body2" sx={{ flex: 1, lineHeight: 1.5, color: "text.primary" }}>
                            {c.text}
                          </Typography>
                          <Box sx={{ display: "flex", flexDirection: "column", alignItems: "flex-end", gap: 0.4, flexShrink: 0 }}>
                            <Chip label={cfg.label} size="small"
                              sx={{ bgcolor: `${cfg.color}15`, color: cfg.color,
                                    fontWeight: 700, fontSize: "0.65rem", height: 20 }} />
                            <Typography variant="caption" color="text.disabled">
                              {c.confidence_pct}%
                            </Typography>
                          </Box>
                        </Box>
                      </motion.div>
                    );
                  })}
                </Box>
              </CardContent>
            </Card>
          </motion.div>
        )}
      </AnimatePresence>
    </Box>
  );
}
