import { useState } from "react";
import { motion } from "framer-motion";
import { Box, Typography } from "@mui/material";
import AutoAwesomeIcon from "@mui/icons-material/AutoAwesome";
import { supabase } from "./supabaseClient";

// ── Local design tokens (mirrors App.jsx C) ────────────────────────────────
const C = {
  bg:          "#0A0A0A",
  surface:     "#111111",
  border:      "#222222",
  borderHi:    "#333333",
  neon:        "#39FF14",
  neonDim:     "rgba(57,255,20,0.12)",
  neonGlow:    "rgba(57,255,20,0.25)",
  textPri:     "#F2F2F2",
  textSec:     "#888888",
  textMuted:   "#444444",
  error:       "#FF4444",
  fontDisplay: "'Syne', sans-serif",
  fontUI:      "'DM Sans', 'Segoe UI', sans-serif",
  fontMono:    "'JetBrains Mono', monospace",
};

// ── Google "G" logo SVG ────────────────────────────────────────────────────
function GoogleG() {
  return (
    <svg width="17" height="17" viewBox="0 0 17 17" fill="none">
      <path d="M16.3 8.7c0-.57-.05-1.12-.14-1.65H8.5v3.12h4.38a3.74 3.74 0 01-1.62 2.46v2.04h2.63C15.44 13.22 16.3 11.13 16.3 8.7z" fill="#4285F4" />
      <path d="M8.5 16.5c2.2 0 4.05-.73 5.4-1.97l-2.63-2.04c-.73.49-1.67.78-2.77.78-2.13 0-3.93-1.44-4.57-3.37H1.22v2.1A8.5 8.5 0 008.5 16.5z" fill="#34A853" />
      <path d="M3.93 9.9a5.07 5.07 0 01-.27-1.6c0-.56.1-1.1.27-1.6V4.6H1.22A8.5 8.5 0 000 8.3c0 1.37.33 2.66.9 3.7l3.03-2.1z" fill="#FBBC05" />
      <path d="M8.5 3.3c1.2 0 2.28.41 3.13 1.22l2.35-2.35A8.5 8.5 0 008.5.5 8.5 8.5 0 001.22 4.6L4.25 6.7C4.89 4.77 6.69 3.3 8.5 3.3z" fill="#EA4335" />
    </svg>
  );
}

// Use motion.create() to avoid deprecation warning (motion() is deprecated in newer Framer Motion)
const MotionDiv  = typeof motion.create === "function" ? motion.create("div") : motion.div;
const MotionBox  = typeof motion.create === "function" ? motion.create(Box) : motion(Box);

const card = {
  hidden:  { opacity: 0, y: 28, scale: 0.97 },
  visible: { opacity: 1, y: 0,  scale: 1, transition: { duration: 0.5, ease: [0.22, 1, 0.36, 1] } },
};

export default function LoginScreen() {
  const [loading, setLoading] = useState(false);
  const [error,   setError]   = useState(null);

  const handleGoogleLogin = async () => {
    setLoading(true);
    setError(null);
    const { error: oauthErr } = await supabase.auth.signInWithOAuth({
      provider: "google",
      options:  { redirectTo: window.location.origin },
    });
    if (oauthErr) {
      setError(oauthErr.message);
      setLoading(false);
    }
    // on success the browser redirects — no further action needed here
  };

  return (
    <Box sx={{
      minHeight: "100vh",
      background: [
        `radial-gradient(ellipse 70% 50% at 0% 0%,   rgba(57,255,20,0.08) 0%, transparent 60%)`,
        `radial-gradient(ellipse 55% 60% at 100% 100%, rgba(57,255,20,0.05) 0%, transparent 60%)`,
        C.bg,
      ].join(","),
      display: "flex", alignItems: "center", justifyContent: "center",
      overflow: "hidden", position: "relative",
    }}>

      {/* Faint grid */}
      <Box sx={{
        position: "fixed", inset: 0, pointerEvents: "none", opacity: 0.025,
        backgroundImage: [
          "linear-gradient(rgba(57,255,20,1) 1px, transparent 1px)",
          "linear-gradient(90deg, rgba(57,255,20,1) 1px, transparent 1px)",
        ].join(","),
        backgroundSize: "44px 44px",
      }} />

      {/* Scanline */}
      <Box sx={{
        position: "fixed", inset: 0, pointerEvents: "none", opacity: 0.015,
        backgroundImage: "repeating-linear-gradient(0deg, #fff 0px, #fff 1px, transparent 1px, transparent 4px)",
      }} />

      {/* Card */}
      <MotionDiv initial="hidden" animate="visible" variants={card}>
        <Box sx={{
          width: "100%", maxWidth: 380, mx: { xs: 2, sm: 3 }, p: { xs: 2.5, sm: 4 },
          background: C.surface,
          border: `1px solid ${C.border}`,
          borderRadius: "12px",
          position: "relative", zIndex: 1,
          boxSizing: "border-box",
        }}>

          {/* Logo */}
          <Box sx={{ display: "flex", justifyContent: "center", mb: 3 }}>
            <Box sx={{
              width: 46, height: 46, borderRadius: "9px",
              background: "#0D0D0D", border: `1px solid ${C.border}`,
              display: "flex", alignItems: "center", justifyContent: "center",
            }}>
              <AutoAwesomeIcon sx={{ fontSize: 22, color: C.neon }} />
            </Box>
          </Box>

          {/* Title */}
          <Typography sx={{
            fontFamily: C.fontDisplay, fontWeight: 800, fontSize: "1.55rem",
            letterSpacing: "-0.03em", color: C.textPri, textAlign: "center", mb: 0.6,
          }}>
            Morning Planner
          </Typography>
          <Typography sx={{
            fontFamily: C.fontUI, fontSize: "0.68rem", color: C.textMuted,
            textAlign: "center", letterSpacing: "0.14em", textTransform: "uppercase", mb: 3.5,
          }}>
            Autonomous Multi-Agent System
          </Typography>

          {/* Divider */}
          <Box sx={{ height: "1px", background: "#1A1A1A", mb: 3.5 }} />

          {/* Google button */}
          <MotionBox
            component="button"
            onClick={handleGoogleLogin}
            disabled={loading}
            whileHover={loading ? {} : { scale: 1.025, boxShadow: `0 0 20px ${C.neonGlow}` }}
            whileTap={loading   ? {} : { scale: 0.975 }}
            transition={{ type: "spring", stiffness: 400, damping: 18 }}
            sx={{
              width: "100%",
              display: "flex", alignItems: "center", justifyContent: "center", gap: 1.5,
              py: 1.35, px: 2,
              background: "#0D0D0D",
              border: `1px solid ${C.borderHi}`,
              borderRadius: "7px",
              cursor: loading ? "not-allowed" : "pointer",
              opacity: loading ? 0.55 : 1,
              outline: "none",
              transition: "border-color 0.2s",
              "&:hover:not(:disabled)": { borderColor: "rgba(57,255,20,0.45)" },
            }}
          >
            {loading ? (
              <Box sx={{
                width: 16, height: 16,
                border: `2px solid ${C.border}`,
                borderTopColor: C.neon,
                borderRadius: "50%",
                flexShrink: 0,
                animation: "ls-spin 0.65s linear infinite",
                "@keyframes ls-spin": { "100%": { transform: "rotate(360deg)" } },
              }} />
            ) : <GoogleG />}
            <Typography sx={{
              fontFamily: C.fontUI, fontWeight: 600, fontSize: "0.875rem", color: C.textPri,
            }}>
              {loading ? "Redirecting to Google…" : "Continue with Google"}
            </Typography>
          </MotionBox>

          {/* Error */}
          {error && (
            <Typography sx={{
              mt: 2, fontFamily: C.fontMono, fontSize: "0.7rem",
              color: C.error, textAlign: "center", lineHeight: 1.55,
            }}>
              {error}
            </Typography>
          )}

          {/* Footer note */}
          <Typography sx={{
            mt: 3.5, fontFamily: C.fontUI, fontSize: "0.67rem", color: "#2A2A2A", textAlign: "center",
          }}>
            Your email is stored securely via Supabase Auth
          </Typography>
        </Box>
      </MotionDiv>
    </Box>
  );
}
