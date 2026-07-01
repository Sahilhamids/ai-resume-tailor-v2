import { createContext, useContext, useState, useEffect, useCallback } from "react";

const ThemeContext = createContext(null);

const MODE_KEY = "theme_mode";
const ACCENT_KEY = "theme_accent";
const VALID_MODES = ["light", "dark", "night", "system"];
const VALID_ACCENTS = ["indigo", "blue", "green", "rose", "amber"];

function resolveSystemMode() {
  return window.matchMedia && window.matchMedia("(prefers-color-scheme: light)").matches ? "light" : "dark";
}

function applyTheme(mode, accent) {
  const resolvedMode = mode === "system" ? resolveSystemMode() : mode;
  document.documentElement.setAttribute("data-mode", resolvedMode);
  if (accent === "indigo") {
    document.documentElement.removeAttribute("data-accent");
  } else {
    document.documentElement.setAttribute("data-accent", accent);
  }
}

export function ThemeProvider({ children }) {
  const [mode, setModeState] = useState(() => {
    const saved = localStorage.getItem(MODE_KEY);
    return VALID_MODES.includes(saved) ? saved : "dark";
  });
  const [accent, setAccentState] = useState(() => {
    const saved = localStorage.getItem(ACCENT_KEY);
    return VALID_ACCENTS.includes(saved) ? saved : "indigo";
  });

  useEffect(() => {
    applyTheme(mode, accent);
  }, [mode, accent]);

  useEffect(() => {
    if (mode !== "system" || !window.matchMedia) return;
    const mq = window.matchMedia("(prefers-color-scheme: light)");
    const handler = () => applyTheme(mode, accent);
    mq.addEventListener("change", handler);
    return () => mq.removeEventListener("change", handler);
  }, [mode, accent]);

  const setMode = useCallback((newMode) => {
    setModeState(newMode);
    localStorage.setItem(MODE_KEY, newMode);
  }, []);

  const setAccent = useCallback((newAccent) => {
    setAccentState(newAccent);
    localStorage.setItem(ACCENT_KEY, newAccent);
  }, []);

  return (
    <ThemeContext.Provider value={{ mode, accent, setMode, setAccent, VALID_MODES, VALID_ACCENTS }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  return useContext(ThemeContext);
}
