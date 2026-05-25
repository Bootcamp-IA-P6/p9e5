import { motion, AnimatePresence } from "framer-motion";
import {
  Box, Card, CardContent, Typography, Button, Chip, Divider,
} from "@mui/material";
import {
  DeleteOutlined as DeleteOutlineIcon,
  FileDownload as FileDownloadIcon,
  CheckCircle as CheckCircleIcon,
  WarningAmber as WarningAmberIcon,
  History as HistoryIcon,
} from "@mui/icons-material";

export default function HistoryTab({ history, onClear }) {
  if (!history.length) {
    return (
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
        <Box sx={{ display: "flex", flexDirection: "column", alignItems: "center",
          justifyContent: "center", minHeight: 320, gap: 2 }}>
          <HistoryIcon sx={{ fontSize: 64, color: "#dadce0" }} />
          <Typography variant="h6" color="text.secondary">Sin análisis todavía</Typography>
          <Typography variant="body2" color="text.disabled" textAlign="center" maxWidth={320}>
            Ve a la pestaña <strong>Análisis</strong> y analiza tu primer comentario para verlo aquí.
          </Typography>
        </Box>
      </motion.div>
    );
  }

  function exportCSV() {
    const header = "Nº,Comentario,Resultado,Tipo,Confianza\n";
    const rows   = [...history].reverse()
      .map((r, i) => `${i + 1},"${r.comment.replace(/"/g, '""')}","${r.resultado}","${r.tipo}","${r.confianza}"`)
      .join("\n");
    const blob = new Blob([header + rows], { type: "text/csv;charset=utf-8;" });
    const a    = document.createElement("a");
    a.href     = URL.createObjectURL(blob);
    a.download = "historico_analisis.csv";
    a.click();
    URL.revokeObjectURL(a.href);
  }

  const reversed = [...history].reverse();

  return (
    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.25 }}>
      <Box sx={{ display: "flex", alignItems: "center", justifyContent: "space-between", mb: 2.5 }}>
        <Box>
          <Typography variant="h6" fontWeight={700}>Histórico de análisis</Typography>
          <Typography variant="caption" color="text.secondary">{history.length} entradas</Typography>
        </Box>
        <Box sx={{ display: "flex", gap: 1 }}>
          <Button size="small" variant="outlined" color="primary"
            startIcon={<FileDownloadIcon />} onClick={exportCSV} sx={{ borderRadius: 100 }}>
            Exportar CSV
          </Button>
          <Button size="small" variant="outlined" color="error"
            startIcon={<DeleteOutlineIcon />} onClick={onClear} sx={{ borderRadius: 100 }}>
            Limpiar
          </Button>
        </Box>
      </Box>

      <Box sx={{ display: "flex", flexDirection: "column", gap: 1.5 }}>
        <AnimatePresence>
          {reversed.map((row, i) => {
            const isToxic = row.label === 1;
            return (
              <motion.div key={history.length - i}
                initial={{ opacity: 0, x: -16 }} animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 16 }} transition={{ duration: 0.18, delay: i * 0.025 }}>
                <Card elevation={0} sx={{
                  borderLeft: `4px solid ${isToxic ? "#ea4335" : "#34a853"}`,
                  bgcolor: isToxic ? "#fce8e6" : "#e6f4ea",
                  "&:hover": { bgcolor: isToxic ? "#fad2cf" : "#ceead6" },
                  transition: "background 0.2s",
                }}>
                  <CardContent sx={{ py: 1.5, px: 2, display: "flex", alignItems: "center",
                    gap: 2, "&:last-child": { pb: 1.5 } }}>
                    <Typography variant="caption" color="text.disabled" sx={{ minWidth: 24, fontWeight: 700 }}>
                      #{history.length - i}
                    </Typography>
                    {isToxic
                      ? <WarningAmberIcon sx={{ color: "error.main", flexShrink: 0 }} />
                      : <CheckCircleIcon sx={{ color: "success.main", flexShrink: 0 }} />
                    }
                    <Typography variant="body2" sx={{ flex: 1, color: "text.primary", lineHeight: 1.4 }}>
                      {row.comment}
                    </Typography>
                    <Chip label={row.resultado} size="small"
                      color={isToxic ? "error" : "success"} variant="outlined"
                      sx={{ fontWeight: 700, fontSize: "0.72rem" }} />
                    <Typography variant="caption" color="text.secondary" sx={{ minWidth: 120, textAlign: "center" }}>
                      {row.tipo}
                    </Typography>
                    <Typography variant="caption" fontWeight={700} color="text.secondary"
                      sx={{ minWidth: 40, textAlign: "right" }}>
                      {row.confianza}
                    </Typography>
                  </CardContent>
                </Card>
              </motion.div>
            );
          })}
        </AnimatePresence>
      </Box>
    </motion.div>
  );
}
