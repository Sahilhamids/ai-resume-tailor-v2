export default function ScoreChart({ history }) {
  if (!history || history.length === 0) {
    return <p className="muted">No audits yet.</p>;
  }

  const width = 800;
  const height = 220;
  const padding = 32;
  const maxScore = 100;
  const minScore = 0;

  const points = history.map((h, i) => {
    const x = history.length === 1
      ? width / 2
      : padding + (i / (history.length - 1)) * (width - padding * 2);
    const y = height - padding - ((h.score - minScore) / (maxScore - minScore)) * (height - padding * 2);
    return { x, y, score: h.score, timestamp: h.timestamp, role: h.target_role };
  });

  const path = points.map((p, i) => `${i === 0 ? "M" : "L"} ${p.x} ${p.y}`).join(" ");

  return (
    <svg viewBox={`0 0 ${width} ${height}`} style={{ width: "100%", height: "auto" }}>
      {[0, 25, 50, 75, 100].map((tick) => {
        const y = height - padding - (tick / 100) * (height - padding * 2);
        return (
          <g key={tick}>
            <line x1={padding} y1={y} x2={width - padding} y2={y} stroke="#334155" strokeWidth="1" />
            <text x={4} y={y + 4} fill="#94a3b8" fontSize="11">{tick}</text>
          </g>
        );
      })}

      <path d={path} fill="none" stroke="#6366f1" strokeWidth="2.5" />

      {points.map((p, i) => (
        <g key={i}>
          <circle cx={p.x} cy={p.y} r="4" fill="#6366f1" />
          <title>{`${new Date(p.timestamp).toLocaleDateString()} - ${p.role}: ${p.score}`}</title>
        </g>
      ))}
    </svg>
  );
}
