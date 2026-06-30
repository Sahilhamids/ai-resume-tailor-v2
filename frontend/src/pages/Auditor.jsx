import { useEffect, useState } from "react";
import * as api from "../api";
import ErrorBanner from "../components/ErrorBanner";
import ScoreChart from "../components/ScoreChart";

export default function Auditor() {
  const [file, setFile] = useState(null);
  const [role, setRole] = useState("");
  const [jd, setJd] = useState("");
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);
  const [error, setError] = useState("");
  const [isAuditing, setIsAuditing] = useState(false);

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
          {isAuditing ? "Running Audit…" : "Run Audit"}
        </button>
      </div>

      {result && (
        <div className="card">
          <h3>Audit Result</h3>
          <div className="score">{result.analysis.ats_score}/100</div>
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
