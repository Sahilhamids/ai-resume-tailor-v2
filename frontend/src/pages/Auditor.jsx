import { useEffect, useState } from "react";
import * as api from "../api";
import ErrorBanner from "../components/ErrorBanner";
import ScoreChart from "../components/ScoreChart";

const AUDIT_STEPS = [
  "Extracting text from your PDF…",
  "Scrubbing personal details before sending to AI…",
  "Comparing your resume against the job description…",
  "Scoring keyword coverage and identifying gaps…",
  "Verifying the AI's keyword claims against your actual resume…",
  "Preparing your results…",
];

function useStepProgress(steps, active) {
  const [stepIndex, setStepIndex] = useState(0);

  useEffect(() => {
    if (!active) { setStepIndex(0); return; }
    setStepIndex(0);
    let i = 0;
    const interval = setInterval(() => {
      i += 1;
      if (i < steps.length - 1) setStepIndex(i);
      else clearInterval(interval);
    }, 2200);
    return () => clearInterval(interval);
  }, [active]);

  return steps[stepIndex];
}

export default function Auditor() {
  const [file, setFile] = useState(null);
  const [role, setRole] = useState("");
  const [jd, setJd] = useState("");
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);
  const [error, setError] = useState("");
  const [isAuditing, setIsAuditing] = useState(false);
  const [previousScore, setPreviousScore] = useState(null);

  const auditStatus = useStepProgress(AUDIT_STEPS, isAuditing);

  async function loadHistory() {
    try {
      setHistory(await api.getHistory());
    } catch (e) {
      setError(e.message);
    }
  }

  useEffect(() => { loadHistory(); }, []);

  async function handleAudit() {
    if (!file || !jd.trim() || !role.trim()) {
      return setError("File, role, and job description are all required.");
    }
    setIsAuditing(true);
    const priorForRole = [...history].reverse().find((h) => h.target_role === role);
    setPreviousScore(priorForRole ? priorForRole.score : null);
    try {
      const r = await api.auditResume(file, jd, role);
      setResult(r);
      setError("");
      await loadHistory();
    } catch (e) {
      setError(e.message);
    } finally {
      setIsAuditing(false);
    }
  }

  return (
    <div>
      <ErrorBanner message={error} />

      <div className="card">
        <h3>ATS Audit</h3>
        <input type="file" accept=".pdf" onChange={(e) => setFile(e.target.files[0])} disabled={isAuditing} />
        <input placeholder="Target Role Level (e.g. Mid-level SDE)" value={role} onChange={(e) => setRole(e.target.value)} disabled={isAuditing} />
        <textarea rows={6} placeholder="Paste the job description here..." value={jd} onChange={(e) => setJd(e.target.value)} disabled={isAuditing} />
        <button onClick={handleAudit} disabled={isAuditing}>
          {isAuditing ? "Running…" : "Run ATS Audit"}
        </button>
        {isAuditing && (
          <p className="muted" style={{ marginTop: "10px", fontStyle: "italic" }}>
            ⏳ {auditStatus}
          </p>
        )}
      </div>

      {result && (
        <div className="card">
          <h3>Audit Result</h3>
          <div style={{ display: "flex", alignItems: "baseline", gap: "16px" }}>
            <div className="score">{result.analysis.ats_score}/100</div>
            {previousScore !== null && (
              <span style={{
                color: result.analysis.ats_score > previousScore ? "#22c55e" : result.analysis.ats_score < previousScore ? "#ef4444" : "#94a3b8",
                fontWeight: "bold",
              }}>
                {result.analysis.ats_score > previousScore && "▲ "}
                {result.analysis.ats_score < previousScore && "▼ "}
                {result.analysis.ats_score === previousScore ? "No change" : `${Math.abs(result.analysis.ats_score - previousScore)} pts vs last audit for this role (${previousScore})`}
              </span>
            )}
          </div>
          <h4>Strengths</h4>
          <ul>{(result.analysis.strengths || []).map((s, i) => <li key={i}>{s}</li>)}</ul>
          <h4>Weaknesses</h4>
          <ul>{(result.analysis.weaknesses || []).map((s, i) => <li key={i}>{s}</li>)}</ul>
          <h4>Missing Keywords</h4>
          <ul>{(result.keyword_validation.truly_missing || []).map((s, i) => <li key={i}>{s}</li>)}</ul>
          <h4>Suggestions</h4>
          {(result.analysis.paraphrasing_suggestions || []).map((s, i) => (
            <p key={i}><i>{s.original}</i> &rarr; <b>{s.suggested}</b></p>
          ))}
        </div>
      )}

      <div className="card">
        <h3>Score History</h3>
        <ScoreChart history={history} />
      </div>
    </div>
  );
}
