import { useEffect, useState } from "react";
import { motion, AnimatePresence, useMotionValue, useSpring } from "framer-motion";
import {
  ThemeProvider, createTheme, CssBaseline,
  Box, Card, CardContent, Typography, TextField,
  Button, Chip, Stepper, Step, StepLabel,
  LinearProgress, CircularProgress, Alert,
  Accordion, AccordionSummary, AccordionDetails,
  Divider, Tooltip,
} from "@mui/material";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import AutoAwesomeIcon from "@mui/icons-material/AutoAwesome";
import RestaurantIcon from "@mui/icons-material/Restaurant";
import DirectionsIcon from "@mui/icons-material/Directions";
import FlagIcon from "@mui/icons-material/Flag";
import PsychologyIcon from "@mui/icons-material/Psychology";
import MemoryIcon from "@mui/icons-material/Memory";
import HistoryIcon from "@mui/icons-material/History";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import ReplayIcon from "@mui/icons-material/Replay";
import SaveIcon from "@mui/icons-material/Save";
import BoltIcon from "@mui/icons-material/Bolt";
import AccountTreeIcon from "@mui/icons-material/AccountTree";
import ScheduleIcon from "@mui/icons-material/Schedule";
import TuneIcon from "@mui/icons-material/Tune";

const BASE = "http://localhost:8000";

// ─── Design tokens ───────────────────────────────────────────────────────────
const C = {
  bg:       "#0A0A0A",
  surface:  "#111111",
  surfaceHover: "#161616",
  border:   "#222222",
  borderHi: "#333333",
  neon:     "#39FF14",
  neonDim:  "rgba(57,255,20,0.12)",
  neonGlow: "rgba(57,255,20,0.25)",
  textPri:  "#F2F2F2",
  textSec:  "#888888",
  textMuted:"#444444",
  warning:  "#F5A623",
  error:    "#FF4444",
  // font stacks
  fontDisplay: "'Syne', sans-serif",
  fontUI:      "'DM Sans', 'Segoe UI', sans-serif",
  fontMono:    "'JetBrains Mono', 'Fira Code', monospace",
};

// ─── Theme ────────────────────────────────────────────────────────────────────
const theme = createTheme({
  palette: {
    mode: "dark",
    primary:    { main: C.neon, contrastText: "#000" },
    secondary:  { main: C.textSec },
    background: { default: C.bg, paper: C.surface },
    success:    { main: C.neon },
    warning:    { main: C.warning },
    error:      { main: C.error },
    text:       { primary: C.textPri, secondary: C.textSec },
  },
  typography: {
    fontFamily: C.fontUI,
    // Display headings — Syne
    h3: { fontFamily: C.fontDisplay, fontWeight: 800, letterSpacing: "-0.03em" },
    h4: { fontFamily: C.fontDisplay, fontWeight: 800, letterSpacing: "-0.03em" },
    h5: { fontFamily: C.fontDisplay, fontWeight: 700, letterSpacing: "-0.02em" },
    h6: { fontFamily: C.fontDisplay, fontWeight: 700, letterSpacing: "-0.015em" },
    // UI text — DM Sans
    subtitle1: { fontFamily: C.fontUI, fontWeight: 600 },
    subtitle2: { fontFamily: C.fontUI, fontWeight: 600 },
    body1:     { fontFamily: C.fontUI, fontWeight: 400, lineHeight: 1.65 },
    body2:     { fontFamily: C.fontUI, fontWeight: 400, lineHeight: 1.65 },
    button:    { fontFamily: C.fontUI, fontWeight: 600, letterSpacing: "0.01em" },
    // Small labels — DM Sans
    caption:   { fontFamily: C.fontUI, fontWeight: 500, lineHeight: 1.4 },
    overline:  { fontFamily: C.fontUI, fontWeight: 700, letterSpacing: "0.12em" },
  },
  shape: { borderRadius: 8 },
  components: {
    MuiCard: {
      styleOverrides: {
        root: {
          backgroundImage: "none",
          background: C.surface,
          border: `1px solid ${C.border}`,
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 6,
          textTransform: "none",
          fontWeight: 600,
          fontSize: "0.875rem",
          letterSpacing: "0.01em",
        },
        containedPrimary: {
          background: C.neon,
          color: "#000",
          boxShadow: "none",
          "&:hover": { background: "#50FF2A", boxShadow: `0 0 16px ${C.neonGlow}` },
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          "& .MuiOutlinedInput-root": {
            borderRadius: 6,
            background: "#0D0D0D",
            "& fieldset": { borderColor: C.border },
            "&:hover fieldset": { borderColor: C.borderHi },
            "&.Mui-focused fieldset": { borderColor: C.neon, borderWidth: "1px" },
          },
          "& .MuiInputLabel-root.Mui-focused": { color: C.neon },
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: { borderRadius: 4, fontWeight: 600, fontSize: "0.7rem", letterSpacing: "0.04em" },
      },
    },
    MuiLinearProgress: {
      styleOverrides: { root: { borderRadius: 2, height: 4, background: "#1A1A1A" } },
    },
    MuiAccordion: {
      styleOverrides: {
        root: {
          backgroundImage: "none",
          background: C.surface,
          border: `1px solid ${C.border}`,
          "&:before": { display: "none" },
          "&.Mui-expanded": { borderColor: C.borderHi },
        },
      },
    },
    MuiAccordionSummary: {
      styleOverrides: {
        root: { "&:hover": { background: C.surfaceHover } },
      },
    },
    MuiStepIcon: {
      styleOverrides: {
        root: { color: C.border, "&.Mui-active": { color: C.neon }, "&.Mui-completed": { color: C.neon } },
      },
    },
    MuiDivider: {
      styleOverrides: { root: { borderColor: C.border } },
    },
  },
});

// ─── Animation Variants ───────────────────────────────────────────────────────
const fadeUp = {
  hidden:  { opacity: 0, y: 24 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.45, ease: "easeOut" } },
};
const stagger = {
  visible: { transition: { staggerChildren: 0.1 } },
};
const scaleIn = {
  hidden:  { opacity: 0, scale: 0.93 },
  visible: { opacity: 1, scale: 1, transition: { duration: 0.35, ease: "easeOut" } },
};

// Animated MUI Button
const MotionButton = motion(Button);
const btnSpring    = { type: "spring", stiffness: 420, damping: 18 };

// ─── Cursor spotlight ────────────────────────────────────────────────────────
function CursorSpotlight() {
  const rawX = useMotionValue(-600);
  const rawY = useMotionValue(-600);
  const x = useSpring(rawX, { stiffness: 80, damping: 22, mass: 0.6 });
  const y = useSpring(rawY, { stiffness: 80, damping: 22, mass: 0.6 });

  useEffect(() => {
    const move = (e) => { rawX.set(e.clientX); rawY.set(e.clientY); };
    window.addEventListener("pointermove", move);
    return () => window.removeEventListener("pointermove", move);
  }, [rawX, rawY]);

  return (
    <motion.div
      style={{
        position: "fixed",
        top: 0, left: 0,
        x, y,
        translateX: "-50%",
        translateY: "-50%",
        width: 520,
        height: 520,
        borderRadius: "50%",
        background: "radial-gradient(circle, rgba(57,255,20,0.09) 0%, rgba(57,255,20,0.03) 35%, transparent 70%)",
        filter: "blur(28px)",
        pointerEvents: "none",
        zIndex: 1,
        willChange: "transform",
      }}
    />
  );
}

function generateUUID() {
  if (typeof crypto !== "undefined" && crypto.randomUUID) return crypto.randomUUID();
  return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0;
    const v = c === "x" ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
}

function getUserId() {
  let uid = localStorage.getItem("user_id");
  if (!uid) {
    uid = generateUUID();
    localStorage.setItem("user_id", uid);
  }
  return uid;
}

// ─── PlanCard ─────────────────────────────────────────────────────────────────
const CARD_META = {
  Meal:     { icon: <RestaurantIcon fontSize="small" />, label: "Meal" },
  Route:    { icon: <DirectionsIcon fontSize="small" />, label: "Route" },
  Priority: { icon: <FlagIcon fontSize="small" />,       label: "Priority" },
};

function PlanCard({ label, value, agent, model }) {
  const meta = CARD_META[label] || {};
  const bullets = value.split(".").map(s => s.trim()).filter(Boolean).slice(0, 3);
  return (
    <motion.div variants={fadeUp}>
      <Card>
        <CardContent sx={{ p: 3 }}>
          <Box sx={{ display: "flex", alignItems: "center", gap: 1.5, mb: 2.5 }}>
            <Box sx={{
              display: "flex", alignItems: "center", justifyContent: "center",
              width: 32, height: 32, borderRadius: "6px",
              background: "#1A1A1A", color: C.neon, border: `1px solid ${C.border}`,
            }}>
              {meta.icon}
            </Box>
            <Typography variant="subtitle2" sx={{ color: C.neon, fontWeight: 700, letterSpacing: "0.1em", textTransform: "uppercase", fontSize: "0.68rem" }}>
              {label}
            </Typography>
          </Box>
          <Box component="ul" sx={{ m: 0, p: 0, listStyle: "none", mb: 2.5 }}>
            {bullets.map((b, i) => (
              <Box component="li" key={i} sx={{ display: "flex", gap: 1.5, mb: 1, alignItems: "flex-start" }}>
                <Box sx={{ mt: "7px", width: 4, height: 4, borderRadius: "1px", background: C.neon, flexShrink: 0, transform: "rotate(45deg)" }} />
                <Typography variant="body2" sx={{ color: C.textPri, lineHeight: 1.65, fontSize: "0.85rem" }}>{b}</Typography>
              </Box>
            ))}
          </Box>
          <Typography variant="caption" sx={{ color: C.textMuted, fontFamily: C.fontMono, fontSize: "0.68rem" }}>
            {agent}{model ? ` · ${model}` : ""}
          </Typography>
        </CardContent>
      </Card>
    </motion.div>
  );
}

const DEFAULT_FORM = {
  diet: "",
  commute_mode: "",
  wake_time: "",
  focus_goal: "",
  event_text: "",
};

export default function App() {
  const [form, setForm]       = useState(DEFAULT_FORM);
  const [plan, setPlan]       = useState(null);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving]   = useState(false);
  const [error, setError]     = useState(null);
  const [logsOpen, setLogsOpen] = useState(false);
  const [savedProfile, setSavedProfile] = useState(null);
  const [recentPlans, setRecentPlans] = useState([]);
  const [expandedPlan, setExpandedPlan] = useState(null);
  const [showMemory, setShowMemory] = useState(false);
  const [showRecent, setShowRecent] = useState(false);
  const [reasoningOpen, setReasoningOpen] = useState(false);
  const [pipelineStep, setPipelineStep] = useState(0);
  const [memoryContent, setMemoryContent] = useState("");
  const [memorySaving, setMemorySaving] = useState(false);
  const [memoryMessage, setMemoryMessage] = useState(null);

  // On first load: ensure user_id exists (generate once, reuse everywhere)
  useEffect(() => {
    let cancelled = false;
    const userId = getUserId();
    console.log("Using user_id:", userId);
    (async () => {
      try {
        const profile = await fetchProfile(userId);
        if (cancelled) return;
        if (profile) {
          fetchPlan(userId);
          fetchRecentPlans(userId);
        }
      } catch (_) {}
    })();
    return () => { cancelled = true; };
  }, []);

  const fetchProfile = async (uid) => {
    try {
      const res = await fetch(`${BASE}/get-profile?user_id=${uid}`);
      if (res.status === 404 || !res.ok) {
        setSavedProfile(null);
        return null;
      }
      const data = await res.json();
      if (data == null) {
        setSavedProfile(null);
        return null;
      }
      setSavedProfile(data);
      return data;
    } catch (err) {
      console.error("Failed to fetch profile:", err);
      setSavedProfile(null);
      return null;
    }
  };

  const fetchRecentPlans = async (uid) => {
    try {
      const res = await fetch(`${BASE}/plans?user_id=${uid}`);
      if (res.ok) {
        const data = await res.json();
        setRecentPlans(data);
      }
    } catch (err) {
      console.error("Failed to fetch recent plans:", err);
    }
  };

  const handleChange = (e) =>
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));

  const handleSaveAndGenerate = async () => {
    if (!form.diet || !form.commute_mode || !form.wake_time || !form.focus_goal) {
      setError("Please fill in all profile fields.");
      return;
    }
    const userId = getUserId();
    console.log("Using user_id:", userId);
    setSaving(true);
    setError(null);
    setPlan(null);
    setPipelineStep(0);

    try {
      setPipelineStep(1);
      const userRes = await fetch(`${BASE}/create-user`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_id:      userId,
          diet:         form.diet,
          commute_mode: form.commute_mode,
          wake_time:    form.wake_time,
          focus_goal:   form.focus_goal,
        }),
      });
      if (!userRes.ok) throw new Error("Failed to create user profile.");
      await userRes.json(); // same user_id returned; we keep using userId from getUserId()

      if (form.event_text.trim()) {
        await fetch(`${BASE}/add-event`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ user_id: userId, event_text: form.event_text }),
        });
      }

      await fetchProfile(userId);
      setPipelineStep(2);
      await new Promise(r => setTimeout(r, 300));
      setPipelineStep(3);
      await fetchPlan(userId);
      setPipelineStep(4);
      await fetchRecentPlans(userId);
    } catch (err) {
      setError(err.message);
      setPipelineStep(0);
    } finally {
      setSaving(false);
    }
  };

  const fetchPlan = async (uid) => {
    console.log("Using user_id:", uid);
    setLoading(true);
    setError(null);
    setLogsOpen(false);
    try {
      const res = await fetch(`${BASE}/morning-plan?user_id=${uid}`);
      if (!res.ok) throw new Error("Failed to fetch morning plan.");
      const data = await res.json();
      setPlan(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleRegenerate = async () => {
    const uid = getUserId();
    await fetchPlan(uid);
    await fetchRecentPlans(uid);
  };

  const handleSaveMemory = async () => {
    const content = memoryContent.trim();
    if (!content) return;
    const uid = getUserId();
    console.log("Using user_id:", uid);
    setMemorySaving(true);
    setMemoryMessage(null);
    try {
      const res = await fetch(`${BASE}/add-memory`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: uid, content }),
      });
      if (!res.ok) throw new Error("Failed to save memory");
      setMemoryContent("");
      setMemoryMessage("Memory saved");
    } catch (err) {
      setMemoryMessage(err.message || "Failed to save memory");
    } finally {
      setMemorySaving(false);
    }
  };

  const agentLogs = plan ? [
    { agent: "ScheduleAgent",   message: plan.agent_logs?.schedule   ?? "—" },
    { agent: "LogisticsAgent",  message: plan.agent_logs?.logistics   ?? "—" },
    { agent: "PreferenceAgent", message: plan.agent_logs?.preference  ?? "—" },
    { agent: "SupervisorAgent", message: "Aggregated agent outputs and calculated confidence." },
  ] : [];

  const pipelineSteps = ["User Profile", "Agents Running", "Supervisor", "Execution"];
  const confPct     = plan ? Math.round(plan.confidence * 100) : 0;
  const isHighConf  = plan && plan.confidence >= 0.7;

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />

      {/* Cursor spotlight */}
      <CursorSpotlight />

      {/* Gradient background — radial neon glows */}
      <Box sx={{ position: "fixed", inset: 0, pointerEvents: "none", zIndex: 0,
        background: [
          `radial-gradient(ellipse 65% 45% at 2% 0%,   rgba(57,255,20,0.07) 0%, transparent 60%)`,
          `radial-gradient(ellipse 50% 55% at 98% 100%, rgba(57,255,20,0.05) 0%, transparent 60%)`,
          `radial-gradient(ellipse 35% 30% at 98% 2%,  rgba(57,255,20,0.03) 0%, transparent 55%)`,
          C.bg,
        ].join(","),
      }} />

      {/* Faint grid */}
      <Box sx={{ position: "fixed", inset: 0, pointerEvents: "none", zIndex: 0, opacity: 0.028,
        backgroundImage: [
          "linear-gradient(rgba(57,255,20,1) 1px, transparent 1px)",
          "linear-gradient(90deg, rgba(57,255,20,1) 1px, transparent 1px)",
        ].join(","),
        backgroundSize: "44px 44px",
      }} />

      {/* Scanline texture */}
      <Box sx={{ position: "fixed", inset: 0, pointerEvents: "none", zIndex: 0, opacity: 0.018,
        backgroundImage: "repeating-linear-gradient(0deg, #fff 0px, #fff 1px, transparent 1px, transparent 4px)",
      }} />

      <Box sx={{ minHeight: "100vh", position: "relative", zIndex: 1, px: { xs: 2, sm: 4 }, py: 6 }}>
        <Box sx={{ maxWidth: 560, mx: "auto" }}>
          <motion.div initial="hidden" animate="visible" variants={stagger}>

            {/* ── Header ── */}
            <motion.div variants={fadeUp}>
              <Box sx={{ textAlign: "center", mb: 4, position: "relative" }}>
                <Tooltip title="Agents Online" arrow>
                  <Box sx={{
                    position: "absolute", top: 0, right: 0,
                    display: "flex", alignItems: "center", gap: 0.8,
                    px: 1.5, py: 0.6, borderRadius: "4px",
                    background: C.neonDim, border: `1px solid rgba(57,255,20,0.3)`,
                  }}>
                    <Box sx={{
                      width: 6, height: 6, borderRadius: "50%", background: C.neon,
                      animation: "pulse 2s infinite",
                      "@keyframes pulse": {
                        "0%,100%": { opacity: 1 },
                        "50%": { opacity: 0.3 },
                      },
                    }} />
                    <Typography variant="caption" sx={{ color: C.neon, fontWeight: 700, letterSpacing: "0.08em", fontSize: "0.65rem" }}>
                      ONLINE
                    </Typography>
                  </Box>
                </Tooltip>

                <Box sx={{ display: "flex", justifyContent: "center", mb: 2 }}>
                  <Box sx={{
                    width: 48, height: 48, borderRadius: "8px",
                    background: "#111",
                    border: `1px solid ${C.border}`,
                    display: "flex", alignItems: "center", justifyContent: "center",
                  }}>
                    <AutoAwesomeIcon sx={{ fontSize: 22, color: C.neon }} />
                  </Box>
                </Box>

                <Typography variant="h4" sx={{ fontWeight: 700, color: C.textPri, letterSpacing: "-0.025em" }}>
                  Morning Planner
                </Typography>
                <Typography variant="body2" sx={{ color: C.textMuted, mt: 0.75, letterSpacing: "0.12em", textTransform: "uppercase", fontSize: "0.65rem" }}>
                  Autonomous Multi-Agent System
                </Typography>
              </Box>
            </motion.div>

            {/* ── Agent Chips ── */}
            <motion.div variants={fadeUp}>
              <Box sx={{ display: "flex", justifyContent: "center", flexWrap: "wrap", gap: 1, mb: 3 }}>
                {[
                  { label: "Supervisor", icon: <AccountTreeIcon sx={{ fontSize: 12 }} /> },
                  { label: "Schedule",   icon: <ScheduleIcon    sx={{ fontSize: 12 }} /> },
                  { label: "Logistics",  icon: <DirectionsIcon  sx={{ fontSize: 12 }} /> },
                  { label: "Preference", icon: <TuneIcon        sx={{ fontSize: 12 }} /> },
                  { label: "Execution",  icon: <BoltIcon        sx={{ fontSize: 12 }} /> },
                ].map(({ label, icon }) => (
                  <Chip key={label} icon={icon} label={label} size="small" variant="outlined"
                    sx={{
                      borderColor: C.border, color: C.textSec,
                      "& .MuiChip-icon": { ml: "6px", color: C.textMuted },
                      "&:hover": { borderColor: C.neon, color: C.neon, "& .MuiChip-icon": { color: C.neon } },
                      transition: "all 0.2s",
                    }}
                  />
                ))}
              </Box>
            </motion.div>

            {/* ── Pipeline Stepper ── */}
            <motion.div variants={fadeUp}>
              <Box sx={{ mb: 3 }}>
                <Stepper activeStep={pipelineStep - 1} alternativeLabel
                  sx={{
                    "& .MuiStepConnector-line": { borderColor: C.border },
                    "& .MuiStepIcon-root":               { color: "#1A1A1A" },
                    "& .MuiStepIcon-root.Mui-active":    { color: C.neon, filter: `drop-shadow(0 0 4px ${C.neon})` },
                    "& .MuiStepIcon-root.Mui-completed": { color: C.neon },
                    "& .MuiStepIcon-text": { fill: "#000" },
                    "& .MuiStepLabel-label": { fontSize: "0.68rem", color: C.textMuted },
                    "& .MuiStepLabel-label.Mui-active":    { color: C.neon },
                    "& .MuiStepLabel-label.Mui-completed": { color: C.textSec },
                  }}
                >
                  {pipelineSteps.map((label) => (
                    <Step key={label}><StepLabel>{label}</StepLabel></Step>
                  ))}
                </Stepper>
              </Box>
            </motion.div>

            {/* ── Profile Form ── */}
            <motion.div variants={fadeUp}>
              <Card sx={{ mb: 2.5 }}>
                <CardContent sx={{ p: 3 }}>
                  <Box sx={{ display: "flex", alignItems: "center", gap: 1, mb: 2.5, pb: 2, borderBottom: `1px solid ${C.border}` }}>
                    <PsychologyIcon sx={{ color: C.neon, fontSize: 16 }} />
                    <Typography variant="caption" sx={{ color: C.textSec, fontWeight: 700, letterSpacing: "0.12em", textTransform: "uppercase", fontSize: "0.65rem" }}>
                      Your Profile
                    </Typography>
                  </Box>
                  <Box sx={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 2, mb: 2 }}>
                    {[
                      { label: "Diet",         name: "diet",         placeholder: "e.g. Vegan" },
                      { label: "Commute Mode", name: "commute_mode", placeholder: "e.g. Bus" },
                      { label: "Wake Time",    name: "wake_time",    placeholder: "e.g. 7:00 AM" },
                      { label: "Focus Goal",   name: "focus_goal",   placeholder: "e.g. Study" },
                    ].map(({ label, name, placeholder }) => (
                      <TextField key={name} label={label} name={name} value={form[name]}
                        onChange={handleChange} placeholder={placeholder}
                        size="small" fullWidth
                        InputLabelProps={{ sx: { fontSize: "0.82rem" } }}
                      />
                    ))}
                  </Box>
                  <TextField
                    label="Today's Events" name="event_text" value={form.event_text}
                    onChange={handleChange} multiline rows={2} fullWidth
                    placeholder="e.g. 9 AM lecture, 12 PM assignment deadline"
                    sx={{ mb: 2.5 }}
                  />
                  <MotionButton fullWidth variant="contained" color="primary"
                    onClick={handleSaveAndGenerate} disabled={saving}
                    sx={{ py: 1.4, fontSize: "0.85rem" }}
                    startIcon={saving ? <CircularProgress size={14} sx={{ color: "#000" }} /> : <AutoAwesomeIcon sx={{ fontSize: 16 }} />}
                    whileHover={saving ? {} : { scale: 1.025, boxShadow: "0 0 22px rgba(57,255,20,0.4)" }}
                    whileTap={saving ? {} : { scale: 0.97 }}
                    transition={btnSpring}
                  >
                    {saving ? "Saving & Generating…" : "Save Profile & Generate Plan"}
                  </MotionButton>
                </CardContent>
              </Card>
            </motion.div>

            {/* ── Personal Memory ── */}
            <motion.div variants={fadeUp}>
              <Card sx={{ mb: 2.5 }}>
                <CardContent sx={{ p: 3 }}>
                  <Box sx={{ display: "flex", alignItems: "center", gap: 1, mb: 2, pb: 2, borderBottom: `1px solid ${C.border}` }}>
                    <MemoryIcon sx={{ color: C.neon, fontSize: 16 }} />
                    <Typography variant="caption" sx={{ color: C.textSec, fontWeight: 700, letterSpacing: "0.12em", textTransform: "uppercase", fontSize: "0.65rem" }}>
                      Personal Memory
                    </Typography>
                  </Box>
                  <TextField
                    value={memoryContent} onChange={(e) => setMemoryContent(e.target.value)}
                    placeholder="e.g. I prefer black coffee before gym"
                    multiline rows={2} fullWidth sx={{ mb: 2 }}
                  />
                  <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
                    <MotionButton variant="outlined"
                      onClick={handleSaveMemory}
                      disabled={!memoryContent.trim() || memorySaving}
                      startIcon={memorySaving ? <CircularProgress size={14} color="inherit" /> : <SaveIcon sx={{ fontSize: 14 }} />}
                      sx={{ borderColor: C.border, color: C.textSec, "&:hover": { borderColor: C.neon, color: C.neon } }}
                      whileHover={{ scale: 1.04 }}
                      whileTap={{ scale: 0.96 }}
                      transition={btnSpring}
                    >
                      {memorySaving ? "Saving…" : "Save Memory"}
                    </MotionButton>
                    <AnimatePresence>
                      {memoryMessage && (
                        <motion.div initial={{ opacity: 0, x: -8 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0 }}>
                          <Typography variant="caption" sx={{ color: memoryMessage === "Memory saved" ? C.neon : C.error, fontWeight: 600, fontFamily: C.fontMono, fontSize: "0.72rem" }}>
                            {memoryMessage}
                          </Typography>
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </Box>
                </CardContent>
              </Card>
            </motion.div>

            {/* ── Loaded From Memory ── */}
            <AnimatePresence>
              {savedProfile && showMemory && (
                <motion.div key="mem" variants={scaleIn} initial="hidden" animate="visible" exit={{ opacity: 0, scale: 0.95 }}>
                  <Card sx={{ mb: 2.5, borderColor: C.borderHi }}>
                    <CardContent sx={{ p: 3 }}>
                      <Typography variant="caption" sx={{ color: C.neon, fontWeight: 700, letterSpacing: "0.12em", textTransform: "uppercase", fontSize: "0.65rem" }}>
                        ▸ Loaded From Memory
                      </Typography>
                      <Box sx={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 2, mt: 2 }}>
                        {[
                          { label: "Diet",         val: savedProfile.diet },
                          { label: "Commute Mode", val: savedProfile.commute_mode },
                          { label: "Wake Time",    val: savedProfile.wake_time },
                          { label: "Focus Goal",   val: savedProfile.focus_goal },
                        ].map(({ label, val }) => (
                          <Box key={label}>
                            <Typography variant="caption" sx={{ color: C.textMuted, display: "block", mb: 0.3, fontFamily: C.fontMono, fontSize: "0.65rem" }}>{label}</Typography>
                            <Typography variant="body2" sx={{ fontWeight: 600, color: C.textPri, fontSize: "0.85rem" }}>{val}</Typography>
                          </Box>
                        ))}
                      </Box>
                    </CardContent>
                  </Card>
                </motion.div>
              )}
            </AnimatePresence>
            {savedProfile && !showMemory && (
              <motion.div variants={fadeUp}>
                <Box sx={{ textAlign: "center", mb: 2 }}>
                  <MotionButton size="small" variant="text" onClick={() => setShowMemory(true)}
                    sx={{ color: C.textMuted, "&:hover": { color: C.neon } }}
                    whileHover={{ y: -2 }}
                    whileTap={{ scale: 0.95 }}
                    transition={btnSpring}
                  >
                    Show Loaded Profile
                  </MotionButton>
                </Box>
              </motion.div>
            )}

            {/* ── Error ── */}
            <AnimatePresence>
              {error && (
                <motion.div key="err" initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}>
                  <Alert severity="error" sx={{ mb: 2.5, borderRadius: 3 }}>{error}</Alert>
                </motion.div>
              )}
            </AnimatePresence>

            {/* ── Loading ── */}
            <AnimatePresence>
              {loading && (
                <motion.div key="load" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                  <Box sx={{ textAlign: "center", py: 6 }}>
                    <CircularProgress size={32} sx={{ color: C.neon, mb: 2 }} thickness={2} />
                    <Typography variant="body2" sx={{ color: C.textMuted, letterSpacing: "0.1em", fontFamily: C.fontMono, fontSize: "0.75rem" }}>
                      AGENTS PROCESSING…
                    </Typography>
                  </Box>
                </motion.div>
              )}
            </AnimatePresence>

            {/* ── Plan ── */}
            <AnimatePresence>
              {plan && !loading && (
                <motion.div key="plan" initial="hidden" animate="visible" variants={stagger}>

                  {plan.needs_human && (
                    <motion.div variants={fadeUp}>
                      <Alert severity="warning" sx={{ mb: 2.5, borderRadius: 3 }}>
                        Supervisor requests human confirmation
                      </Alert>
                    </motion.div>
                  )}

                  <PlanCard label="Meal"     value={plan.meal}     agent="PreferenceAgent" model={plan.models?.preference} />
                  <Box sx={{ mb: 2 }} />
                  <PlanCard label="Route"    value={plan.route}    agent="LogisticsAgent"  model={plan.models?.logistics} />
                  <Box sx={{ mb: 2 }} />
                  <PlanCard label="Priority" value={plan.priority} agent="ScheduleAgent"   model={plan.models?.schedule} />
                  <Box sx={{ mb: 2 }} />

                  {/* Confidence */}
                  <motion.div variants={fadeUp}>
                    <Card sx={{ mb: 2.5 }}>
                      <CardContent sx={{ p: 3 }}>
                        <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", mb: 2 }}>
                          <Typography variant="caption" sx={{ color: C.textSec, fontWeight: 700, letterSpacing: "0.12em", textTransform: "uppercase", fontSize: "0.65rem" }}>
                            Confidence Score
                          </Typography>
                          <Chip
                            label={isHighConf ? "AUTONOMOUS" : "NEEDS REVIEW"}
                            size="small"
                            variant="outlined"
                            sx={{ borderColor: isHighConf ? C.neon : C.warning, color: isHighConf ? C.neon : C.warning, fontSize: "0.62rem", fontFamily: C.fontMono }}
                          />
                        </Box>
                        <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
                          <Box sx={{ flex: 1 }}>
                            <LinearProgress
                              variant="determinate" value={confPct}
                              sx={{
                                "& .MuiLinearProgress-bar": {
                                  background: isHighConf ? C.neon : C.warning,
                                  boxShadow: isHighConf ? `0 0 8px ${C.neonGlow}` : "none",
                                },
                              }}
                            />
                          </Box>
                          <Typography variant="subtitle2" sx={{ fontWeight: 700, minWidth: 40, textAlign: "right", color: isHighConf ? C.neon : C.warning, fontFamily: C.fontMono, fontSize: "0.85rem" }}>
                            {confPct}%
                          </Typography>
                        </Box>
                      </CardContent>
                    </Card>
                  </motion.div>

                  {/* Execution Status */}
                  {plan.execution && (
                    <motion.div variants={fadeUp}>
                      <Card sx={{ mb: 2.5 }}>
                        <CardContent sx={{ p: 3 }}>
                          <Box sx={{ display: "flex", alignItems: "center", gap: 1, mb: 2 }}>
                            <BoltIcon sx={{ color: C.neon, fontSize: 16 }} />
                            <Typography variant="caption" sx={{ color: C.textSec, fontWeight: 700, letterSpacing: "0.12em", textTransform: "uppercase", fontSize: "0.65rem" }}>
                              Actions Taken
                            </Typography>
                          </Box>
                          <Box sx={{ display: "flex", flexDirection: "column", gap: 1 }}>
                            {plan.execution.ride && (
                              <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                                <CheckCircleIcon sx={{ color: C.neon, fontSize: 15 }} />
                                <Typography variant="body2" sx={{ color: C.textPri, fontSize: "0.85rem" }}>
                                  {plan.execution.ride.provider} booked — ETA {plan.execution.ride.eta}
                                </Typography>
                              </Box>
                            )}
                            {plan.execution.meal && (
                              <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                                <CheckCircleIcon sx={{ color: C.neon, fontSize: 15 }} />
                                <Typography variant="body2" sx={{ color: C.textPri, fontSize: "0.85rem" }}>
                                  {plan.execution.meal.provider} meal scheduled
                                </Typography>
                              </Box>
                            )}
                          </Box>
                        </CardContent>
                      </Card>
                    </motion.div>
                  )}

                  {/* Why this plan? */}
                  <motion.div variants={fadeUp}>
                    <Accordion
                      expanded={reasoningOpen} onChange={() => setReasoningOpen(p => !p)}
                      sx={{ mb: 2.5, borderRadius: "16px !important", overflow: "hidden" }}
                    >
                      <AccordionSummary expandIcon={<ExpandMoreIcon sx={{ color: C.textMuted, fontSize: 18 }} />}>
                        <Typography variant="caption" sx={{ color: C.textSec, fontWeight: 700, letterSpacing: "0.12em", textTransform: "uppercase", fontSize: "0.65rem" }}>
                          Why this plan?
                        </Typography>
                      </AccordionSummary>
                      <AccordionDetails sx={{ p: 3, borderTop: `1px solid ${C.border}` }}>
                        {plan.reasoning && (
                          <Box sx={{ mb: 2.5 }}>
                            <Typography variant="caption" sx={{ color: C.neon, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.1em", fontSize: "0.65rem", display: "block", mb: 1 }}>
                              Supervisor Reasoning
                            </Typography>
                            <Typography variant="body2" sx={{ color: C.textSec, lineHeight: 1.75, fontSize: "0.85rem" }}>
                              {plan.reasoning}
                            </Typography>
                          </Box>
                        )}
                        <Divider sx={{ mb: 2.5 }} />
                        <Typography variant="caption" sx={{ color: C.neon, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.1em", fontSize: "0.65rem", display: "block", mb: 1.5 }}>
                          Agent Outputs
                        </Typography>
                        <Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
                          {agentLogs.map(({ agent, message }) => (
                            <Box key={agent} sx={{ borderLeft: `2px solid ${C.border}`, pl: 1.5 }}>
                              <Typography variant="caption" sx={{ fontFamily: C.fontMono, color: C.neon, fontWeight: 700, fontSize: "0.7rem" }}>
                                {agent}
                              </Typography>
                              <Typography variant="body2" sx={{ fontFamily: C.fontMono, color: C.textSec, mt: 0.3, fontSize: "0.78rem", lineHeight: 1.6 }}>
                                › {message}
                              </Typography>
                            </Box>
                          ))}
                        </Box>
                      </AccordionDetails>
                    </Accordion>
                  </motion.div>

                  {/* Action Buttons */}
                  <motion.div variants={fadeUp}>
                    <Box sx={{ display: "flex", gap: 2, mb: 1 }}>
                      <MotionButton fullWidth variant="contained" color="primary"
                        onClick={() => alert("Morning plan approved and executing")}
                        startIcon={<CheckCircleIcon sx={{ fontSize: 16 }} />}
                        sx={{ py: 1.4 }}
                        whileHover={{ scale: 1.03, boxShadow: "0 0 22px rgba(57,255,20,0.45)" }}
                        whileTap={{ scale: 0.97 }}
                        transition={btnSpring}
                      >
                        Approve Plan
                      </MotionButton>
                      <MotionButton fullWidth variant="outlined"
                        onClick={handleRegenerate}
                        startIcon={<ReplayIcon sx={{ fontSize: 16 }} />}
                        sx={{ py: 1.4, borderColor: C.border, color: C.textSec, "&:hover": { borderColor: C.neon, color: C.neon, background: C.neonDim } }}
                        whileHover={{ scale: 1.03 }}
                        whileTap={{ scale: 0.97, rotate: -3 }}
                        transition={btnSpring}
                      >
                        Regenerate
                      </MotionButton>
                    </Box>
                  </motion.div>

                </motion.div>
              )}
            </AnimatePresence>

            {/* ── Recent Plans ── */}
            <AnimatePresence>
              {recentPlans.length > 0 && showRecent && (
                <motion.div key="recent" initial="hidden" animate="visible" variants={stagger}>
                  <motion.div variants={fadeUp}>
                    <Box sx={{ display: "flex", alignItems: "center", gap: 1, mb: 2, mt: 1 }}>
                      <HistoryIcon sx={{ fontSize: 15, color: C.textMuted }} />
                      <Typography variant="caption" sx={{ color: C.textMuted, fontWeight: 700, letterSpacing: "0.12em", textTransform: "uppercase", fontSize: "0.65rem" }}>
                        Recent Plans
                      </Typography>
                    </Box>
                  </motion.div>
                  {recentPlans.map((item) => {
                    const planData  = item.plan;
                    const timestamp = new Date(item.created_at).toLocaleString();
                    const summary   = planData.reasoning
                      ? planData.reasoning.slice(0, 120) + (planData.reasoning.length > 120 ? "…" : "")
                      : "No summary available";
                    const isExp = expandedPlan === item.id;
                    return (
                      <motion.div key={item.id} variants={fadeUp}>
                        <Accordion expanded={isExp} onChange={() => setExpandedPlan(isExp ? null : item.id)}
                          sx={{ mb: 1.5, borderRadius: "14px !important", overflow: "hidden" }}
                        >
                          <AccordionSummary expandIcon={<ExpandMoreIcon sx={{ color: C.textMuted, fontSize: 18 }} />}>
                            <Box sx={{ flex: 1, minWidth: 0 }}>
                              <Typography variant="caption" sx={{ color: C.textMuted, display: "block", mb: 0.3, fontFamily: C.fontMono, fontSize: "0.65rem" }}>{timestamp}</Typography>
                              <Typography variant="body2" sx={{ color: C.textSec, pr: 2, fontSize: "0.83rem" }} noWrap>{summary}</Typography>
                            </Box>
                            <Chip label={`${Math.round(planData.confidence * 100)}%`} size="small" variant="outlined"
                              sx={{ mr: 1, alignSelf: "center", borderColor: planData.confidence >= 0.7 ? C.neon : C.warning, color: planData.confidence >= 0.7 ? C.neon : C.warning, fontSize: "0.62rem", fontFamily: C.fontMono }}
                            />
                          </AccordionSummary>
                          <AccordionDetails sx={{ p: 2.5, borderTop: `1px solid ${C.border}` }}>
                            {[
                              { label: "Meal",     val: planData.meal },
                              { label: "Route",    val: planData.route },
                              { label: "Priority", val: planData.priority },
                            ].map(({ label, val }) => (
                              <Box key={label} sx={{ mb: 1.5 }}>
                                <Typography variant="caption" sx={{ color: C.textMuted, display: "block", mb: 0.2, fontFamily: C.fontMono, fontSize: "0.65rem", textTransform: "uppercase", letterSpacing: "0.08em" }}>{label}</Typography>
                                <Typography variant="body2" sx={{ color: C.textSec, fontSize: "0.83rem" }}>{val}</Typography>
                              </Box>
                            ))}
                          </AccordionDetails>
                        </Accordion>
                      </motion.div>
                    );
                  })}
                </motion.div>
              )}
            </AnimatePresence>

            {recentPlans.length > 0 && !showRecent && (
              <motion.div variants={fadeUp}>
                <Box sx={{ textAlign: "center", mt: 1 }}>
                  <MotionButton size="small" variant="text"
                    startIcon={<HistoryIcon sx={{ fontSize: 14 }} />} onClick={() => setShowRecent(true)}
                    sx={{ color: C.textMuted, "&:hover": { color: C.neon } }}
                    whileHover={{ y: -2 }}
                    whileTap={{ scale: 0.95 }}
                    transition={btnSpring}
                  >
                    Show Recent Plans
                  </MotionButton>
                </Box>
              </motion.div>
            )}

          </motion.div>
        </Box>
      </Box>
    </ThemeProvider>
  );
}
