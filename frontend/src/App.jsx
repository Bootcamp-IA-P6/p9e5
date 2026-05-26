import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Box, AppBar, Toolbar, Tabs, Tab, Typography,
  Chip, Container, Snackbar, Alert, Stack,
} from '@mui/material';
import {
  Shield as ShieldIcon,
  Search as SearchIcon,
  History as HistoryIcon,
  BarChart as BarChartIcon,
  SmartToy as SmartToyIcon,
  YouTube as YouTubeIcon,
  Slideshow as SlideshowIcon,
} from '@mui/icons-material';
import { analyzeComment } from './api';
import { TYPE_CONFIG }    from './constants';
import AnalyzeTab         from './components/AnalyzeTab';
import HistoryTab         from './components/HistoryTab';
import StatsTab           from './components/StatsTab';
import UrlTab             from './components/UrlTab';
import PresentationTab    from './components/PresentationTab';

const G_BLUE   = '#1a73e8';
const G_RED    = '#ea4335';
const G_YELLOW = '#fbbc04';
const G_GREEN  = '#34a853';
const G_DOTS   = [G_BLUE, G_RED, G_YELLOW, G_GREEN];

const HERO_CHIPS = [
  { emoji: '⚡', label: 'Análisis instantáneo', color: G_BLUE   },
  { emoji: '🌍', label: 'Bilingüe ES / EN',      color: G_GREEN  },
  { emoji: '🧠', label: 'ML Multiclase',         color: G_RED    },
  { emoji: '📂', label: '7 tipos detectados',    color: G_YELLOW },
];

function GDots() {
  return (
    <Stack direction="row" spacing={0.6} sx={{ mb: 2 }}>
      {G_DOTS.map((c, i) => (
        <Box key={i} sx={{ width: 12, height: 12, borderRadius: '50%', bgcolor: c }} />
      ))}
    </Stack>
  );
}

export default function App() {
  const [tab,     setTab]     = useState(0);
  const [history, setHistory] = useState([]);
  const [snack,   setSnack]   = useState(null);

  async function handleAnalyze(text) {
    const data = await analyzeComment(text);
    const cfg  = TYPE_CONFIG[data.toxicity_type] ?? TYPE_CONFIG['lenguaje cotidiano'];
    setSnack(data.toxic
      ? { severity: 'error',   msg: `Tóxico — ${cfg.label} · ${data.confidence_pct}% confianza` }
      : { severity: 'success', msg: `Comentario seguro · confianza ${data.confidence_pct}%` }
    );
    setHistory(prev => [...prev, {
      comment:   text.slice(0, 120) + (text.length > 120 ? '…' : ''),
      resultado: data.toxic ? 'Tóxico' : 'No tóxico',
      tipo:      `${cfg.icon} ${cfg.label}`,
      confianza: `${data.confidence_pct}%`,
      label:     data.label,
      type:      data.toxicity_type,
      raw:       data,
    }]);
    return data;
  }

  const nToxic = history.filter(h => h.label === 1).length;
  const nSafe  = history.filter(h => h.label === 0).length;

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: '#f8f9fa', display: 'flex', flexDirection: 'column' }}>
      {/* ── AppBar ── */}
      <AppBar position="sticky" elevation={0}>
        <Toolbar sx={{ gap: 1.5, px: { xs: 2, md: 4 } }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.2, mr: 1 }}>
            <Box sx={{
              width: 36, height: 36, borderRadius: '50%',
              background: `linear-gradient(135deg, ${G_BLUE}, ${G_GREEN})`,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
            }}>
              <ShieldIcon sx={{ fontSize: 20, color: '#fff' }} />
            </Box>
            <Typography fontWeight={700} fontSize="1.05rem" color="text.primary" letterSpacing={-0.2}>
              Hate<span style={{ color: G_BLUE }}>Guard</span>
            </Typography>
          </Box>
          <Tabs value={tab} onChange={(_, v) => setTab(v)} sx={{ flex: 1 }}
            variant="scrollable" scrollButtons="auto">
            <Tab icon={<SearchIcon fontSize="small" />} iconPosition="start" label="Análisis" />
            <Tab
              icon={<HistoryIcon fontSize="small" />}
              iconPosition="start"
              label={
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.7 }}>
                  Histórico
                  {history.length > 0 && (
                    <Chip label={history.length} size="small" color="primary"
                      sx={{ height: 18, fontSize: '0.65rem', '.MuiChip-label': { px: 0.8 } }} />
                  )}
                </Box>
              }
            />
            <Tab icon={<BarChartIcon fontSize="small" />} iconPosition="start" label="Estadísticas" />
            <Tab icon={<YouTubeIcon fontSize="small" />} iconPosition="start" label="Por vídeo" />
            <Tab icon={<SlideshowIcon fontSize="small" />} iconPosition="start" label="Presentación" />
          </Tabs>
          <Chip
            icon={<SmartToyIcon sx={{ fontSize: '1rem !important' }} />}
            label="ML · FastAPI"
            variant="outlined"
            size="small"
            sx={{ borderColor: '#dadce0', color: '#5f6368', display: { xs: 'none', sm: 'flex' } }}
          />
        </Toolbar>
      </AppBar>

      {/* ── Hero banner ── */}
      <AnimatePresence>
        {tab === 0 && (
          <motion.div key="hero"
            initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }} transition={{ duration: 0.25 }}>
            <Box sx={{
              background: 'linear-gradient(135deg, #e8f0fe 0%, #f8f9ff 40%, #e6f4ea 100%)',
              borderBottom: '1px solid #e8eaed',
              py: { xs: 4, md: 5 }, px: { xs: 2, md: 4 },
            }}>
              <Container maxWidth="lg">
                <Stack direction={{ xs: 'column', md: 'row' }}
                  alignItems={{ md: 'center' }} justifyContent="space-between" gap={3}>
                  <Box>
                    <GDots />
                    <Typography variant="h4" color="text.primary" sx={{ mb: 0.5 }}>
                      Detector de Mensajes de Odio
                    </Typography>
                    <Typography variant="h6" fontWeight={400} color="text.secondary" sx={{ mb: 2.5 }}>
                      Análisis inteligente de comentarios de YouTube
                    </Typography>
                    <Stack direction="row" gap={1} flexWrap="wrap">
                      {HERO_CHIPS.map(({ emoji, label }) => (
                        <Chip key={label}
                          label={`${emoji}  ${label}`}
                          size="small"
                          sx={{
                            bgcolor: '#fff', border: '1px solid #e8eaed',
                            color: '#5f6368', fontWeight: 500,
                            boxShadow: '0 1px 3px rgba(60,64,67,0.08)',
                          }}
                        />
                      ))}
                    </Stack>
                  </Box>
                  <Stack direction="row" gap={1.5} flexShrink={0}>
                    {[
                      { val: history.length, lbl: 'Analizados', color: G_BLUE  },
                      { val: nToxic,         lbl: 'Tóxicos',    color: G_RED   },
                      { val: nSafe,          lbl: 'Seguros',     color: G_GREEN },
                    ].map(({ val, lbl, color }) => (
                      <Box key={lbl} sx={{
                        bgcolor: '#fff', border: '1px solid #e8eaed', borderRadius: 3,
                        px: 2.5, py: 1.5, textAlign: 'center', minWidth: 80,
                        boxShadow: '0 1px 3px rgba(60,64,67,0.08)',
                      }}>
                        <Typography variant="h5" fontWeight={800} sx={{ color }}>{val}</Typography>
                        <Typography variant="caption" color="text.secondary">{lbl}</Typography>
                      </Box>
                    ))}
                  </Stack>
                </Stack>
              </Container>
            </Box>
          </motion.div>
        )}
      </AnimatePresence>

      {/* ── Content ── */}
      <Box sx={{ flexGrow: 1, py: 3, px: { xs: 2, md: 4 } }}>
        <Container maxWidth="lg">
          <AnimatePresence mode="wait">
            <motion.div key={tab}
              initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -6 }} transition={{ duration: 0.2 }}>
              {tab === 0 && <AnalyzeTab onAnalyze={handleAnalyze} />}
              {tab === 1 && (
                <HistoryTab history={history}
                  onClear={() => { setHistory([]); setSnack({ severity: 'info', msg: 'Histórico limpiado' }); }} />
              )}
              {tab === 2 && <StatsTab history={history} />}
              {tab === 3 && <UrlTab />}
              {tab === 4 && <PresentationTab />}
            </motion.div>
          </AnimatePresence>
        </Container>
      </Box>

      {/* ── Footer ── */}
      <Box component="footer" sx={{
        borderTop: '1px solid #e8eaed', py: 2, px: 4, bgcolor: '#fff',
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
      }}>
        <Typography variant="caption" color="text.disabled">Proyecto académico · NLP · 2025</Typography>
        <Stack direction="row" spacing={0.5}>
          {G_DOTS.map((c, i) => (
            <Box key={i} sx={{ width: 8, height: 8, borderRadius: '50%', bgcolor: c }} />
          ))}
        </Stack>
        <Typography variant="caption" color="text.disabled">React + FastAPI · TF-IDF + Logistic Regression</Typography>
      </Box>

      {/* ── Snackbar ── */}
      <Snackbar open={!!snack} autoHideDuration={4500} onClose={() => setSnack(null)}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}>
        <Alert onClose={() => setSnack(null)} severity={snack?.severity ?? 'info'}
          variant="standard" sx={{ minWidth: 320, boxShadow: 4 }}>
          {snack?.msg}
        </Alert>
      </Snackbar>
    </Box>
  );
}
