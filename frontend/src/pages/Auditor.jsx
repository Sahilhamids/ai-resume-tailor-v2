import { useEffect, useState } from "react";
import * as api from "../api";
import ErrorBanner from "../components/ErrorBanner";

export default function Auditor() {
  const [file, setFile] = useState(null);
  const [role, setRole] = useState("");
  const [jd, setJd] = useState("");
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);
  const [error, setError] = useState("");

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
    try {
      const r = await api.auditResume(file, jd, role);
      setResult(r);
      setError("");
      await loadHistory();
    } catch (e) {
      setError(e.message);
    }
  }

  return (
    <div>
      <ErrorBanner message={error} />

      <div className="card">
        <h3>ATS Audit</h3>
        <input type="file" accept=".pdf" onChange={(e) => setFile(e.target.files[0])} />
        <input placeholder="Target Role Level (e.g. Mid-level SDE)" value={role} onChange={(e) => setRole(e.target.value)} />
        <textarea rows={6} placeholder="Paste the job description here..." value={jd} onChange={(e) => setJd(e.target.value)} />
        <button onClick={handleAudit}>Run Audit</button>
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
        {history.length === 0 && <p className="muted">No audits yet.</p>}
        {history.map((h, i) => (
          <div className="row" key={i}>
            <span>{new Date(h.timestamp).toLocaleDateString()} - {h.target_role}</span>
            <b>{h.score}</b>
          </div>
        ))}
      </div>
    </div>
  );
}
