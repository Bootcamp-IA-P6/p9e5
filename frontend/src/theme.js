import { createTheme } from "@mui/material/styles";

const theme = createTheme({
  palette: {
    mode: "light",
    primary:    { main: "#1a73e8", light: "#4285f4", dark: "#0d47a1", contrastText: "#fff" },
    secondary:  { main: "#ea4335", light: "#f28b82", dark: "#b31412", contrastText: "#fff" },
    success:    { main: "#137333", light: "#34a853", dark: "#0a5227", contrastText: "#fff" },
    error:      { main: "#c5221f", light: "#ea4335", dark: "#7f0000", contrastText: "#fff" },
    warning:    { main: "#e37400", light: "#fbbc04", dark: "#a05000" },
    info:       { main: "#1a73e8" },
    background: { default: "#f8f9fa", paper: "#ffffff" },
    text:       { primary: "#202124", secondary: "#5f6368", disabled: "#9aa0a6" },
    divider:    "rgba(0,0,0,0.08)",
  },
  typography: {
    fontFamily: "'Google Sans', 'Roboto', sans-serif",
    h4: { fontWeight: 700, letterSpacing: -0.3 },
    h5: { fontWeight: 700 },
    h6: { fontWeight: 600 },
    subtitle1: { fontWeight: 500 },
    button: { fontWeight: 600, textTransform: "none", letterSpacing: 0.2 },
  },
  shape: { borderRadius: 12 },
  components: {
    MuiCssBaseline: {
      styleOverrides: {
        body: { background: "#f8f9fa", minHeight: "100vh" },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundColor: "#ffffff",
          color: "#202124",
          borderBottom: "1px solid #e8eaed",
          backgroundImage: "none",
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          backgroundImage: "none",
          boxShadow: "0 1px 3px rgba(60,64,67,0.08), 0 1px 2px rgba(60,64,67,0.1)",
          border: "1px solid #e8eaed",
          "&:hover": { boxShadow: "0 4px 12px rgba(60,64,67,0.12)" },
          transition: "box-shadow 0.2s ease",
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: { borderRadius: 100, textTransform: "none", fontWeight: 600 },
        containedPrimary: {
          background: "#1a73e8",
          boxShadow: "0 2px 6px rgba(26,115,232,0.3)",
          "&:hover": { background: "#1557b0" },
          "&:disabled": { background: "#e8eaed", color: "#9aa0a6", boxShadow: "none" },
        },
        outlinedPrimary: {
          borderColor: "#dadce0",
          color: "#1a73e8",
          "&:hover": { background: "#e8f0fe", borderColor: "#1a73e8" },
        },
      },
    },
    MuiTab: {
      styleOverrides: {
        root: {
          textTransform: "none",
          fontWeight: 500,
          color: "#5f6368",
          minHeight: 48,
          "&.Mui-selected": { color: "#1a73e8", fontWeight: 600 },
        },
      },
    },
    MuiTabs: {
      styleOverrides: {
        indicator: { backgroundColor: "#1a73e8", height: 3, borderRadius: "3px 3px 0 0" },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          "& .MuiOutlinedInput-root": {
            borderRadius: 12,
            backgroundColor: "#f8f9fa",
            "& fieldset": { borderColor: "#e8eaed" },
            "&:hover fieldset": { borderColor: "#9aa0a6" },
            "&.Mui-focused fieldset": { borderColor: "#1a73e8", borderWidth: 2 },
            "&.Mui-focused": { backgroundColor: "#fff" },
          },
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: { fontWeight: 500, borderRadius: 8 },
        colorPrimary: { backgroundColor: "#e8f0fe", color: "#1a73e8" },
        colorError:   { backgroundColor: "#fce8e6", color: "#ea4335" },
        colorSuccess: { backgroundColor: "#e6f4ea", color: "#137333" },
      },
    },
    MuiLinearProgress: {
      styleOverrides: {
        root: { borderRadius: 100, height: 8, backgroundColor: "#e8eaed" },
        bar:  { borderRadius: 100 },
      },
    },
    MuiAlert: {
      styleOverrides: {
        root:            { borderRadius: 12 },
        standardError:   { backgroundColor: "#fce8e6", color: "#c5221f" },
        standardSuccess: { backgroundColor: "#e6f4ea", color: "#137333" },
        standardWarning: { backgroundColor: "#fef9e3", color: "#e37400" },
        standardInfo:    { backgroundColor: "#e8f0fe", color: "#1a73e8" },
      },
    },
  },
});

export default theme;
