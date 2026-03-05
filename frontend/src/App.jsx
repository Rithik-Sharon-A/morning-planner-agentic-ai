import { useEffect, useState } from "react";
import { motion, AnimatePresence, useMotionValue, useSpring } from "framer-motion";
import {
  ThemeProvider, createTheme, CssBaseline,
  Box, Card, CardContent, Typography, TextField,
  Button, Chip, Stepper, Step, StepLabel,
  LinearProgress, CircularProgress, Alert,
  Accordion, AccordionSummary, AccordionDetails,
  Divider, Tooltip, Dialog, DialogTitle, DialogContent, DialogContentText, DialogActions,
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
import LogoutIcon from "@mui/icons-material/Logout";
import EventNoteIcon from "@mui/icons-material/EventNote";
import DeleteForeverIcon from "@mui/icons-material/DeleteForever";
import CalendarMonthIcon from "@mui/icons-material/CalendarMonth";
import { supabase } from "./supabaseClient";
import LoginScreen from "./LoginScreen";

const BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

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

// Use motion.create() to avoid deprecation warning (motion() is deprecated in newer Framer Motion)
const MotionDiv    = typeof motion.create === "function" ? motion.create("div") : motion.div;
const MotionButton = typeof motion.create === "function" ? motion.create(Button) : motion(Button);
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
    <MotionDiv
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

// Auth user id is sourced from Supabase session (user.id)

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
    <MotionDiv variants={fadeUp}>
      <Card>
        <CardContent sx={{ p: { xs: 2, sm: 3 } }}>
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
    </MotionDiv>
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
  const [user, setUser]               = useState(null);
  const [authLoading, setAuthLoading] = useState(true);
  const [resetDialogOpen, setResetDialogOpen] = useState(false);
  const [resetDeleting, setResetDeleting] = useState(false);
  const [calendarConnecting, setCalendarConnecting] = useState(false);
  const [calendarMessage, setCalendarMessage] = useState(null); // "success" | "error" message text

  // ── Auth: centralized authentication state management ──────────────
  useEffect(() => {
    let mounted = true;

    // Initialize auth state once on mount
    const initAuth = async () => {
      try {
        const { data: { session }, error } = await supabase.auth.getSession();
        if (error) throw error;
        
        if (mounted) {
          setUser(session?.user || null);
          setAuthLoading(false);
        }
      } catch (error) {
        console.error("Auth initialization error:", error);
        if (mounted) {
          setUser(null);
          setAuthLoading(false);
        }
      }
    };

    initAuth();

    // Listen for auth changes (login, logout, token refresh)
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      (_event, session) => {
        if (!mounted) return;

        if (!session?.user) {
          // User logged out
          setUser(null);
          setPlan(null);
          setSavedProfile(null);
          setRecentPlans([]);
          setPipelineStep(0);
          setError(null);
        } else {
          // User logged in or session refreshed
          setUser(session.user);
        }
      }
    );

    return () => {
      mounted = false;
      subscription.unsubscribe();
    };
  }, []);

  // ── Bootstrap: sync user_profile with id + email from Supabase Auth ────────
  useEffect(() => {
    if (!user?.id) return;
    let cancelled = false;
    (async () => {
      try {
        const emailFromAuth = (user.email != null && user.email !== "") ? String(user.email) : "";
        const payload = { user_id: user.id, email: emailFromAuth };
        if (!emailFromAuth) console.warn("[auth] No email on user object — ensure Google provider returns email in Supabase Auth");
        const res = await fetch(`${BASE}/upsert-auth-user`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
        if (!res.ok) {
          const err = await res.json().catch(() => ({}));
          console.warn("upsert-auth-user failed", res.status, err);
        }
        const profile = await fetchProfile(user.id);
        if (cancelled) return;
        if (profile) {
          // Do not run agents on login. Only fetch recent plan history (no agent run).
          fetchRecentPlans(user.id);
        }
      } catch (e) {
        console.warn("Bootstrap error", e);
      }
    })();
    return () => { cancelled = true; };
  }, [user?.id]); // Only depend on user.id to prevent infinite loops

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
    
    // Guard: prevent multiple simultaneous saves
    if (saving) {
      console.warn("[handleSaveAndGenerate] Already saving, skipping duplicate request");
      return;
    }
    
    const userId = user.id;
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
          email:        user?.email ?? "",
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
    
    // Guard: prevent multiple simultaneous requests
    if (loading) {
      console.warn("[fetchPlan] Already loading, skipping duplicate request");
      return;
    }
    
    setLoading(true);
    setError(null);
    setLogsOpen(false);
    
    // Timeout protection: abort after 60 seconds
    const controller = new AbortController();
    const timeoutId = setTimeout(() => {
      controller.abort();
      console.error("[fetchPlan] Request timed out after 60s");
    }, 60000);
    
    try {
      const res = await fetch(`${BASE}/morning-plan?user_id=${uid}`, {
        signal: controller.signal,
      });
      clearTimeout(timeoutId);
      
      if (!res.ok) throw new Error("Failed to fetch morning plan.");
      const data = await res.json();
      setPlan(data);
    } catch (err) {
      clearTimeout(timeoutId);
      if (err.name === 'AbortError') {
        setError("Request timed out. The AI agents may be taking too long. Please try again.");
      } else {
        setError(err.message);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleRegenerate = async () => {
    // Guard: prevent regenerate while already loading
    if (loading) {
      console.warn("[handleRegenerate] Already loading, skipping");
      return;
    }
    
    const uid = user.id;
    await fetchPlan(uid);
    await fetchRecentPlans(uid);
  };

  const handleSaveMemory = async () => {
    const content = memoryContent.trim();
    if (!content) return;
    const uid = user.id;
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

  const handleLogout = async () => {
    try {
      // Sign out from Supabase
      await supabase.auth.signOut();
      // Clear all local storage
      localStorage.clear();
      // Reset all state
      setUser(null);
      setPlan(null);
      setSavedProfile(null);
      setRecentPlans([]);
      setPipelineStep(0);
      setError(null);
      // Auth listener will handle redirect to login screen
    } catch (error) {
      console.error("Logout failed:", error);
      setError("Failed to sign out. Please try again.");
    }
  };

  // Load Google Identity Services script once for Calendar OAuth
  const loadGsiScript = () => {
    if (window.google?.accounts?.oauth2) return Promise.resolve();
    return new Promise((resolve, reject) => {
      const id = "gsi-oauth-script";
      if (document.getElementById(id)) {
        if (window.google?.accounts?.oauth2) resolve();
        else window.addEventListener("load", () => (window.google?.accounts?.oauth2 ? resolve() : reject(new Error("GIS not available"))));
        return;
      }
      const script = document.createElement("script");
      script.id = id;
      script.src = "https://accounts.google.com/gsi/client";
      script.async = true;
      script.onload = () => resolve();
      script.onerror = () => reject(new Error("Failed to load Google Identity Services"));
      document.head.appendChild(script);
    });
  };

  const handleConnectCalendar = async () => {
    const clientId = import.meta.env.VITE_GOOGLE_CLIENT_ID;
    if (!clientId?.trim()) {
      setCalendarMessage("Failed to connect Google Calendar. (Google Client ID not configured.)");
      return;
    }
    if (!user?.id) {
      setCalendarMessage("Failed to connect Google Calendar. (Not signed in.)");
      return;
    }
    setCalendarConnecting(true);
    setCalendarMessage(null);
    try {
      await loadGsiScript();
      const tokenClient = window.google.accounts.oauth2.initTokenClient({
        client_id: clientId.trim(),
        scope: "https://www.googleapis.com/auth/calendar.events",
        callback: async (tokenResponse) => {
          if (!tokenResponse?.access_token) {
            setCalendarMessage("Failed to connect Google Calendar.");
            setCalendarConnecting(false);
            return;
          }
          try {
            const res = await fetch(`${BASE}/api/store-google-token`, {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({
                user_id: user.id,
                access_token: tokenResponse.access_token,
              }),
            });
            const data = await res.json().catch(() => ({}));
            if (!res.ok) {
              setCalendarMessage(data.detail || "Failed to connect Google Calendar.");
              return;
            }
            setCalendarMessage("Google Calendar connected successfully.");
            await fetchProfile(user.id);
          } catch (e) {
            setCalendarMessage("Failed to connect Google Calendar.");
          } finally {
            setCalendarConnecting(false);
          }
        },
      });
      tokenClient.requestAccessToken();
      // If popup is closed without granting, we never get callback; reset loading after a timeout
      setTimeout(() => setCalendarConnecting((prev) => (prev ? false : prev)), 60000);
    } catch (e) {
      setCalendarMessage(e?.message || "Failed to connect Google Calendar.");
      setCalendarConnecting(false);
    }
  };

  // ── Auth gates ────────────────────────────────────────────────────────────

  const handleResetDataConfirm = async () => {
    if (!user?.id) return;
    setResetDeleting(true);
    setError(null);
    try {
      // Backend expects user_id as query param (DELETE /api/delete-user-data?user_id=...)
      const url = `${BASE}/api/delete-user-data?user_id=${encodeURIComponent(user.id)}`;
      const res = await fetch(url, { method: "DELETE" });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(data.detail || "Failed to delete user data");
      setResetDialogOpen(false);
      localStorage.clear();
      await supabase.auth.signOut();
    } catch (err) {
      console.error("Delete user data failed:", err);
      setError(err.message || "Failed to reset data");
    } finally {
      setResetDeleting(false);
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

  // ── Auth gates ────────────────────────────────────────────────────────────
  if (authLoading) return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ height: "100vh", display: "flex", alignItems: "center", justifyContent: "center", background: C.bg }}>
        <CircularProgress size={22} thickness={2} sx={{ color: C.neon }} />
      </Box>
    </ThemeProvider>
  );

  if (!user) return <LoginScreen />;

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
        <Box sx={{ maxWidth: 560, mx: "auto", px: { xs: 2, sm: 3 }, boxSizing: "border-box" }}>
          <MotionDiv initial="hidden" animate="visible" variants={stagger}>

            {/* ── Header ── */}
            <MotionDiv variants={fadeUp}>
              <Box sx={{ textAlign: "center", mb: 4, position: "relative" }}>

                {/* ── User info + logout ── */}
                <Box sx={{
                  position: "absolute", top: 0, left: 0,
                  display: "flex", alignItems: "center", gap: { xs: 0.75, sm: 1.25 },
                  flexWrap: "wrap", maxWidth: "min(100%, 280px)",
                }}>
                  <Box sx={{
                    width: 32, height: 32, borderRadius: "6px",
                    background: C.neon, color: "#000",
                    display: "flex", alignItems: "center", justifyContent: "center",
                    fontFamily: C.fontUI, fontWeight: 800, fontSize: "0.9rem", flexShrink: 0,
                  }}>
                    {user.email?.[0]?.toUpperCase() ?? "U"}
                  </Box>
                  <Typography variant="body2" sx={{
                    color: C.textSec, fontFamily: C.fontUI, fontSize: { xs: "0.8rem", sm: "0.9rem" }, fontWeight: 500,
                    maxWidth: { xs: 120, sm: 200 }, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap",
                  }}>
                    {user.email}
                  </Typography>
                  <Tooltip title="Sign out" arrow>
                    <Box component="button" onClick={handleLogout} sx={{
                      background: "none", border: "none", cursor: "pointer", p: 0.75,
                      color: C.textMuted, display: "flex", alignItems: "center", justifyContent: "center",
                      "&:hover": { color: C.neon }, transition: "color 0.2s",
                      borderRadius: "6px", minWidth: 36, minHeight: 36, ml: -0.5,
                    }}>
                      <LogoutIcon sx={{ fontSize: 22 }} />
                    </Box>
                  </Tooltip>
                </Box>

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
            </MotionDiv>

            {/* ── Agent Chips ── */}
            <MotionDiv variants={fadeUp}>
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
            </MotionDiv>

            {/* ── Pipeline Stepper ── */}
            <MotionDiv variants={fadeUp}>
              <Box sx={{ mb: 3, overflowX: "auto", pb: 0.5 }}>
                <Stepper activeStep={pipelineStep - 1} alternativeLabel
                  sx={{
                    minWidth: { xs: 320, sm: "auto" },
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
            </MotionDiv>

            {/* ── Profile Form ── */}
            <MotionDiv variants={fadeUp}>
              <Card sx={{ mb: 2.5 }}>
                <CardContent sx={{ p: { xs: 2, sm: 3 } }}>
                  <Box sx={{ display: "flex", alignItems: "center", gap: 1, mb: 2.5, pb: 2, borderBottom: `1px solid ${C.border}` }}>
                    <PsychologyIcon sx={{ color: C.neon, fontSize: 16 }} />
                    <Typography variant="caption" sx={{ color: C.textSec, fontWeight: 700, letterSpacing: "0.12em", textTransform: "uppercase", fontSize: "0.65rem" }}>
                      Your Profile
                    </Typography>
                  </Box>
                  <Box sx={{ display: "grid", gridTemplateColumns: { xs: "1fr", sm: "1fr 1fr" }, gap: 2, mb: 2 }}>
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
            </MotionDiv>

            {/* ── Personal Memory ── */}
            <MotionDiv variants={fadeUp}>
              <Card sx={{ mb: 2.5 }}>
                <CardContent sx={{ p: { xs: 2, sm: 3 } }}>
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
                        <MotionDiv initial={{ opacity: 0, x: -8 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0 }}>
                          <Typography variant="caption" sx={{ color: memoryMessage === "Memory saved" ? C.neon : C.error, fontWeight: 600, fontFamily: C.fontMono, fontSize: "0.72rem" }}>
                            {memoryMessage}
                          </Typography>
                        </MotionDiv>
                      )}
                    </AnimatePresence>
                  </Box>
                </CardContent>
              </Card>
            </MotionDiv>

            {/* ── Google Calendar ── */}
            <MotionDiv variants={fadeUp}>
              <Card sx={{ mb: 2.5, borderColor: C.border }}>
                <CardContent sx={{ p: { xs: 2, sm: 3 } }}>
                  <Box sx={{ display: "flex", alignItems: "center", gap: 1, mb: 2, pb: 2, borderBottom: `1px solid ${C.border}` }}>
                    <CalendarMonthIcon sx={{ color: C.textMuted, fontSize: 18 }} />
                    <Typography variant="caption" sx={{ color: C.textSec, fontWeight: 700, letterSpacing: "0.12em", textTransform: "uppercase", fontSize: "0.65rem" }}>
                      Google Calendar
                    </Typography>
                  </Box>
                  {savedProfile?.calendar_connected ? (
                    <Box sx={{ display: "flex", alignItems: "center", gap: 1.5 }}>
                      <CheckCircleIcon sx={{ color: C.neon, fontSize: 22 }} />
                      <Typography variant="body2" sx={{ color: C.neon, fontWeight: 600, fontSize: "0.9rem" }}>
                        Google Calendar Connected
                      </Typography>
                    </Box>
                  ) : (
                    <>
                      <Typography variant="body2" sx={{ color: C.textSec, mb: 2, fontSize: "0.85rem" }}>
                        Connect your Google account so approved daily plans can be added to your calendar.
                      </Typography>
                      <Button
                        variant="outlined"
                        onClick={handleConnectCalendar}
                        disabled={calendarConnecting}
                        startIcon={calendarConnecting ? <CircularProgress size={16} color="inherit" /> : <CalendarMonthIcon sx={{ fontSize: 18 }} />}
                        sx={{
                          borderColor: C.border,
                          color: C.textSec,
                          textTransform: "none",
                          fontWeight: 600,
                          fontSize: "0.875rem",
                          "&:hover": { borderColor: C.neon, color: C.neon },
                        }}
                      >
                        {calendarConnecting ? "Connecting…" : "Connect Google Calendar"}
                      </Button>
                      <AnimatePresence>
                        {calendarMessage && (
                          <MotionDiv initial={{ opacity: 0, y: -4 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} sx={{ mt: 2 }}>
                            <Typography
                              variant="body2"
                              sx={{
                                color: calendarMessage.includes("successfully") ? C.neon : C.error,
                                fontWeight: 500,
                                fontSize: "0.85rem",
                              }}
                            >
                              {calendarMessage}
                            </Typography>
                          </MotionDiv>
                        )}
                      </AnimatePresence>
                    </>
                  )}
                </CardContent>
              </Card>
            </MotionDiv>

            {/* ── Account: Reset My Data ── */}
            <MotionDiv variants={fadeUp}>
              <Card sx={{ mb: 2.5, borderColor: C.border }}>
                <CardContent sx={{ p: { xs: 2, sm: 3 } }}>
                  <Box sx={{ display: "flex", alignItems: "center", gap: 1, mb: 2, pb: 2, borderBottom: `1px solid ${C.border}` }}>
                    <DeleteForeverIcon sx={{ color: C.textMuted, fontSize: 18 }} />
                    <Typography variant="caption" sx={{ color: C.textSec, fontWeight: 700, letterSpacing: "0.12em", textTransform: "uppercase", fontSize: "0.65rem" }}>
                      Account
                    </Typography>
                  </Box>
                  <Typography variant="body2" sx={{ color: C.textSec, mb: 2, fontSize: "0.85rem" }}>
                    Permanently delete your profile, plans, and memories. You will be signed out.
                  </Typography>
                  <Button
                    variant="contained"
                    onClick={() => setResetDialogOpen(true)}
                    disabled={resetDeleting}
                    startIcon={resetDeleting ? <CircularProgress size={14} sx={{ color: "#fff" }} /> : <DeleteForeverIcon sx={{ fontSize: 18 }} />}
                    sx={{
                      bgcolor: "#d32f2f",
                      color: "#fff",
                      px: 2,
                      py: 1.25,
                      borderRadius: "6px",
                      textTransform: "none",
                      fontWeight: 600,
                      fontSize: "0.875rem",
                      "&:hover": { bgcolor: "#b71c1c" },
                    }}
                  >
                    {resetDeleting ? "Deleting…" : "Reset My Data"}
                  </Button>
                </CardContent>
              </Card>
            </MotionDiv>

            {/* ── Reset data confirmation dialog ── */}
            <Dialog
              open={resetDialogOpen}
              onClose={() => !resetDeleting && setResetDialogOpen(false)}
              disableScrollLock
              disableEnforceFocus={false}
              PaperProps={{
                sx: {
                  bgcolor: C.surface,
                  border: `1px solid ${C.border}`,
                  borderRadius: 2,
                },
              }}
              slotProps={{ root: { "aria-hidden": false } }}
            >
              <DialogTitle sx={{ color: C.textPri, fontFamily: C.fontDisplay, fontWeight: 700 }}>
                Reset My Data
              </DialogTitle>
              <DialogContent>
                <DialogContentText sx={{ color: C.textSec, fontSize: "0.9rem" }}>
                  Are you sure you want to delete all your data? This action cannot be undone.
                </DialogContentText>
              </DialogContent>
              <DialogActions sx={{ px: 3, pb: 2, gap: 1 }}>
                <Button
                  onClick={() => setResetDialogOpen(false)}
                  disabled={resetDeleting}
                  sx={{ color: C.textSec, textTransform: "none" }}
                >
                  Cancel
                </Button>
                <Button
                  variant="contained"
                  onClick={handleResetDataConfirm}
                  disabled={resetDeleting}
                  sx={{
                    bgcolor: "#d32f2f",
                    color: "#fff",
                    textTransform: "none",
                    fontWeight: 600,
                    "&:hover": { bgcolor: "#b71c1c" },
                  }}
                >
                  {resetDeleting ? "Deleting…" : "Delete My Data"}
                </Button>
              </DialogActions>
            </Dialog>

            {/* ── Loaded From Memory ── */}
            <AnimatePresence>
              {savedProfile && showMemory && (
                <MotionDiv key="mem" variants={scaleIn} initial="hidden" animate="visible" exit={{ opacity: 0, scale: 0.95 }}>
                  <Card sx={{ mb: 2.5, borderColor: C.borderHi }}>
                    <CardContent sx={{ p: { xs: 2, sm: 3 } }}>
                      <Typography variant="caption" sx={{ color: C.neon, fontWeight: 700, letterSpacing: "0.12em", textTransform: "uppercase", fontSize: "0.65rem" }}>
                        ▸ Loaded From Memory
                      </Typography>
                      <Box sx={{ display: "grid", gridTemplateColumns: { xs: "1fr", sm: "1fr 1fr" }, gap: 2, mt: 2 }}>
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
                </MotionDiv>
              )}
            </AnimatePresence>
            {savedProfile && !showMemory && (
              <MotionDiv variants={fadeUp}>
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
              </MotionDiv>
            )}

            {/* ── Error ── */}
            <AnimatePresence>
              {error && (
                <MotionDiv key="err" initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}>
                  <Alert severity="error" sx={{ mb: 2.5, borderRadius: 3 }}>{error}</Alert>
                </MotionDiv>
              )}
            </AnimatePresence>

            {/* ── Loading ── */}
            <AnimatePresence>
              {loading && (
                <MotionDiv key="load" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                  <Box sx={{ textAlign: "center", py: 6 }}>
                    <CircularProgress size={32} sx={{ color: C.neon, mb: 2 }} thickness={2} />
                    <Typography variant="body2" sx={{ color: C.textMuted, letterSpacing: "0.1em", fontFamily: C.fontMono, fontSize: "0.75rem" }}>
                      AGENTS PROCESSING…
                    </Typography>
                  </Box>
                </MotionDiv>
              )}
            </AnimatePresence>

            {/* ── Plan ── */}
            <AnimatePresence>
              {plan && !loading && (
                <MotionDiv key="plan" initial="hidden" animate="visible" variants={stagger}>

                  {plan.needs_human && (
                    <MotionDiv variants={fadeUp}>
                      <Alert severity="warning" sx={{ mb: 2.5, borderRadius: 3 }}>
                        Supervisor requests human confirmation
                      </Alert>
                    </MotionDiv>
                  )}

                  <PlanCard label="Meal"     value={plan.meal}     agent="PreferenceAgent" model={plan.models?.preference} />
                  <Box sx={{ mb: 2 }} />
                  <PlanCard label="Route"    value={plan.route}    agent="LogisticsAgent"  model={plan.models?.logistics} />
                  <Box sx={{ mb: 2 }} />
                  <PlanCard label="Priority" value={plan.priority} agent="ScheduleAgent"   model={plan.models?.schedule} />
                  <Box sx={{ mb: 2 }} />

                  {/* Daily Life Plan — full-day timeline */}
                  <MotionDiv variants={fadeUp}>
                    <Card sx={{ mb: 2.5 }}>
                      <CardContent sx={{ p: { xs: 2, sm: 3 } }}>
                        <Box sx={{ display: "flex", alignItems: "center", gap: 1, mb: 2, pb: 2, borderBottom: `1px solid ${C.border}` }}>
                          <EventNoteIcon sx={{ color: C.neon, fontSize: 18 }} />
                          <Typography variant="caption" sx={{ color: C.textSec, fontWeight: 700, letterSpacing: "0.12em", textTransform: "uppercase", fontSize: "0.65rem" }}>
                            Daily Life Plan
                          </Typography>
                        </Box>
                        {plan.daily_plan && plan.daily_plan.length > 0 ? (
                          <Box
                            sx={{
                              position: "relative",
                              pl: 2,
                              "&::before": {
                                content: '""',
                                position: "absolute",
                                left: 5,
                                top: 8,
                                bottom: 8,
                                width: 2,
                                background: `linear-gradient(to bottom, ${C.neon}40, ${C.border})`,
                                borderRadius: 1,
                              },
                            }}
                          >
                            {plan.daily_plan.map((item, idx) => (
                              <Box
                                key={idx}
                                sx={{
                                  position: "relative",
                                  display: "flex",
                                  alignItems: "center",
                                  gap: 2,
                                  py: 1,
                                  pl: 2.5,
                                  borderBottom: idx < plan.daily_plan.length - 1 ? `1px solid ${C.border}` : "none",
                                }}
                              >
                                <Box
                                  sx={{
                                    position: "absolute",
                                    left: 4,
                                    top: "50%",
                                    transform: "translateY(-50%)",
                                    width: 10,
                                    height: 10,
                                    borderRadius: "50%",
                                    bgcolor: C.neon,
                                    boxShadow: `0 0 8px ${C.neonGlow}`,
                                    flexShrink: 0,
                                  }}
                                />
                                <Typography
                                  variant="caption"
                                  sx={{
                                    minWidth: 88,
                                    fontFamily: C.fontMono,
                                    color: C.neon,
                                    fontWeight: 600,
                                    fontSize: "0.85rem",
                                    flexShrink: 0,
                                  }}
                                >
                                  {item.time}
                                </Typography>
                                <Typography variant="body2" sx={{ color: C.textPri, fontSize: "0.875rem", lineHeight: 1.5 }}>
                                  {item.activity}
                                </Typography>
                              </Box>
                            ))}
                          </Box>
                        ) : (
                          <Typography variant="body2" sx={{ color: C.textMuted, fontStyle: "italic", fontSize: "0.85rem" }}>
                            No daily plan generated yet. Save profile and generate to see your full-day timeline.
                          </Typography>
                        )}
                      </CardContent>
                    </Card>
                  </MotionDiv>

                  {/* Confidence */}
                  <MotionDiv variants={fadeUp}>
                    <Card sx={{ mb: 2.5 }}>
                      <CardContent sx={{ p: { xs: 2, sm: 3 } }}>
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
                  </MotionDiv>

                  {/* Execution Status */}
                  {plan.execution && (
                    <MotionDiv variants={fadeUp}>
                      <Card sx={{ mb: 2.5 }}>
                        <CardContent sx={{ p: { xs: 2, sm: 3 } }}>
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
                            {plan.execution.calendar && plan.execution.calendar.status === "success" && (
                              <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                                <CheckCircleIcon sx={{ color: C.neon, fontSize: 15 }} />
                                <Typography variant="body2" sx={{ color: C.textPri, fontSize: "0.85rem" }}>
                                  {plan.execution.calendar.events_created} event{plan.execution.calendar.events_created !== 1 ? "s" : ""} added to Google Calendar
                                </Typography>
                              </Box>
                            )}
                            {plan.execution.calendar && plan.execution.calendar.status === "error" && (
                              <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                                <Typography variant="body2" sx={{ color: C.error, fontSize: "0.85rem" }}>
                                  Calendar: {plan.execution.calendar.message || "Failed to create events"}
                                </Typography>
                              </Box>
                            )}
                          </Box>
                        </CardContent>
                      </Card>
                    </MotionDiv>
                  )}

                  {/* Why this plan? */}
                  <MotionDiv variants={fadeUp}>
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
                  </MotionDiv>

                  {/* Action Buttons */}
                  <MotionDiv variants={fadeUp}>
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
                  </MotionDiv>

                </MotionDiv>
              )}
            </AnimatePresence>

            {/* ── Recent Plans ── */}
            <AnimatePresence>
              {recentPlans.length > 0 && showRecent && (
                <MotionDiv key="recent" initial="hidden" animate="visible" variants={stagger}>
                  <MotionDiv variants={fadeUp}>
                    <Box sx={{ display: "flex", alignItems: "center", gap: 1, mb: 2, mt: 1 }}>
                      <HistoryIcon sx={{ fontSize: 15, color: C.textMuted }} />
                      <Typography variant="caption" sx={{ color: C.textMuted, fontWeight: 700, letterSpacing: "0.12em", textTransform: "uppercase", fontSize: "0.65rem" }}>
                        Recent Plans
                      </Typography>
                    </Box>
                  </MotionDiv>
                  {recentPlans.map((item) => {
                    const planData  = item.plan;
                    const timestamp = new Date(item.created_at).toLocaleString();
                    const summary   = planData.reasoning
                      ? planData.reasoning.slice(0, 120) + (planData.reasoning.length > 120 ? "…" : "")
                      : "No summary available";
                    const isExp = expandedPlan === item.id;
                    return (
                      <MotionDiv key={item.id} variants={fadeUp}>
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
                      </MotionDiv>
                    );
                  })}
                </MotionDiv>
              )}
            </AnimatePresence>

            {recentPlans.length > 0 && !showRecent && (
              <MotionDiv variants={fadeUp}>
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
              </MotionDiv>
            )}

          </MotionDiv>
        </Box>
      </Box>
    </ThemeProvider>
  );
}
