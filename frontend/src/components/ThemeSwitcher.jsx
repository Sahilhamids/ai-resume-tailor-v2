import { useTheme } from "../ThemeContext";

const ACCENT_COLORS = {
  indigo: "#6366f1",
  blue: "#3b82f6",
  green: "#22c55e",
  rose: "#f43f5e",
  amber: "#f59e0b",
};

const MODE_LABELS = {
  light: "☀️ Light",
  dark: "🌙 Dark",
  night: "⚫ Night",
  system: "💻 System",
};

export default function ThemeSwitcher() {
  const { mode, accent, setMode, setAccent, VALID_MODES, VALID_ACCENTS } = useTheme();

  return (
    <div className="theme-switcher">
      <select value={mode} onChange={(e) => setMode(e.target.value)} title="Color mode" aria-label="Color mode">
        {VALID_MODES.map((m) => <option key={m} value={m}>{MODE_LABELS[m]}</option>)}
      </select>
      {VALID_ACCENTS.map((a) => (
        <button
          key={a}
          type="button"
          className={`accent-dot${accent === a ? " active" : ""}`}
          style={{ background: ACCENT_COLORS[a] }}
          onClick={() => setAccent(a)}
          title={`${a[0].toUpperCase() + a.slice(1)} accent`}
          aria-label={`${a} accent color`}
        />
      ))}
    </div>
  );
}
