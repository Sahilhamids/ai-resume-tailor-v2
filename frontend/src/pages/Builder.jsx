import { useState } from "react";
import * as api from "../api";
import ErrorBanner from "../components/ErrorBanner";

export default function Builder() {
  const [jd, setJd] = useState("");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [isBuilding, setIsBuilding] = useState(false);
  const [isExporting, setIsExporting] = useState(false);

  async function handleBuild() {
    if (!jd.trim()) return setError("Paste a job description first.");
    setIsBuilding(true);
    try {
      const r = await api.buildResume(jd);
      setResult(r);
      setError("");
    } catch (e) {
      setError(e.message);
    } finally {
      setIsBuilding(false);
    }
  }

  async function handleExport() {
    if (!result) return setError("Generate a resume first.");
    setIsExporting(true);
    try {
      const res = await api.exportPdf(result);
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "tailored_resume.pdf";
      a.click();
    } catch (e) {
      setError(e.message);
    } finally {
      setIsExporting(false);
    }
  }

  return (
    <div>
      <ErrorBanner message={error} />
      <div className="card">
        <h3>Build a Tailored Resume</h3>
        <textarea rows={6} placeholder="Paste the job description here..." value={jd} onChange={(e) => setJd(e.target.value)} disabled={isBuilding} />
        <button onClick={handleBuild} disabled={isBuilding}>
          {isBuilding ? "Generating…" : "Generate Tailored Resume"}
        </button>
      </div>

      {result && (
        <div className="card">
          <h3>Result</h3>
          <h4>Professional Summary</h4>
          <p>{result.professional_summary}</p>

          <h4>Tailored Employment</h4>
          {(result.tailored_employment || []).map((j, i) => (
            <div key={i}>
              <p><b>{j.title}</b> @ {j.company} ({j.duration})</p>
              <ul>{(j.optimized_bullets || []).map((b, bi) => <li key={bi}>{b}</li>)}</ul>
            </div>
          ))}

          <h4>Tailored Projects</h4>
          {(result.tailored_projects || []).map((p, i) => (
            <p key={i}><b>{p.name}</b>: {p.optimized_description}</p>
          ))}

          <h4>Top Relevant Skills</h4>
          <p>{(result.top_relevant_skills || []).join(", ")}</p>

          <button onClick={handleExport} disabled={isExporting}>
            {isExporting ? "Exporting…" : "Export as PDF"}
          </button>
        </div>
      )}
    </div>
  );
}
