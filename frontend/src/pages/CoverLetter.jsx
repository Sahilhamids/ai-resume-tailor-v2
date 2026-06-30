import { useEffect, useState } from "react";
import * as api from "../api";
import ErrorBanner from "../components/ErrorBanner";

export default function CoverLetter() {
  const [jd, setJd] = useState("");
  const [company, setCompany] = useState("");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [letters, setLetters] = useState([]);

  function loadLetters() {
    api.listCoverLetters().then(setLetters).catch((e) => setError(e.message));
  }

  useEffect(() => { loadLetters(); }, []);

  async function handleGenerate() {
    if (!jd.trim()) return setError("Paste a job description first.");
    setIsGenerating(true);
    setSaved(false);
    try {
      const r = await api.generateCoverLetter(jd, company);
      setResult(r);
      setError("");
    } catch (e) {
      setError(e.message);
    } finally {
      setIsGenerating(false);
    }
  }

  async function handleSave() {
    if (!result) return;
    setIsSaving(true);
    try {
      await api.saveCoverLetter(result.subject_line || "Cover Letter", company, result.body, null);
      setSaved(true);
      loadLetters();
    } catch (e) {
      setError(e.message);
    } finally {
      setIsSaving(false);
    }
  }

  async function handleDelete(id) {
    try {
      await api.deleteCoverLetter(id);
      loadLetters();
    } catch (e) {
      setError(e.message);
    }
  }

  return (
    <div>
      <ErrorBanner message={error} />

      <div className="card">
        <h3>Generate a Cover Letter</h3>
        <input placeholder="Company Name (optional)" value={company} onChange={(e) => setCompany(e.target.value)} disabled={isGenerating} />
        <textarea rows={6} placeholder="Paste the job description here..." value={jd} onChange={(e) => setJd(e.target.value)} disabled={isGenerating} />
        <button onClick={handleGenerate} disabled={isGenerating}>
          {isGenerating ? "Generating…" : "Generate Cover Letter"}
        </button>
      </div>

      {result && (
        <div className="card">
          <h3>{result.subject_line}</h3>
          <p style={{ whiteSpace: "pre-wrap" }}>{result.body}</p>
          <button onClick={handleSave} disabled={isSaving}>
            {isSaving ? "Saving…" : saved ? "Saved ✓" : "Save This Letter"}
          </button>
        </div>
      )}

      <div className="card">
        <h3>Saved Cover Letters</h3>
        {letters.length === 0 && <p className="muted">No saved cover letters yet.</p>}
        {letters.map((l) => (
          <div className="row" key={l.id}>
            <span>{l.title} {l.company_name && <span className="muted">— {l.company_name}</span>}</span>
            <button className="danger" onClick={() => handleDelete(l.id)}>Delete</button>
          </div>
        ))}
      </div>
    </div>
  );
}
