import { useEffect, useState } from "react";
import * as api from "../api";
import ErrorBanner from "../components/ErrorBanner";

export default function Builder() {
  const [jd, setJd] = useState("");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [isBuilding, setIsBuilding] = useState(false);
  const [isExporting, setIsExporting] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [templates, setTemplates] = useState(["modern", "classic", "minimal"]);
  const [template, setTemplate] = useState("modern");
  const [previewHtml, setPreviewHtml] = useState("");
  const [saveTitle, setSaveTitle] = useState("");
  const [saved, setSaved] = useState(false);
  const [savedResumes, setSavedResumes] = useState([]);

  function loadSavedResumes() {
    api.listSavedResumes().then(setSavedResumes).catch((e) => setError(e.message));
  }

  useEffect(() => {
    api.getResumeTemplates().then((r) => setTemplates(r.templates)).catch(() => {});
    loadSavedResumes();
  }, []);

  useEffect(() => {
    if (!result) return;
    api.previewResume(result, template).then(setPreviewHtml).catch((e) => setError(e.message));
  }, [result, template]);

  async function handleBuild() {
    if (!jd.trim()) return setError("Paste a job description first.");
    setIsBuilding(true);
    setSaved(false);
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

  async function handleExport(format) {
    if (!result) return setError("Generate a resume first.");
    setIsExporting(true);
    try {
      const res = format === "pdf" ? await api.exportPdf(result, template) : await api.exportDocx(result, template);
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `tailored_resume.${format}`;
      a.click();
    } catch (e) {
      setError(e.message);
    } finally {
      setIsExporting(false);
    }
  }

  async function handleSave() {
    if (!result) return setError("Generate a resume first.");
    if (!saveTitle.trim()) return setError("Give this resume version a name first.");
    setIsSaving(true);
    try {
      await api.saveResume(saveTitle, jd, template, result);
      setSaved(true);
      setError("");
      loadSavedResumes();
    } catch (e) {
      setError(e.message);
    } finally {
      setIsSaving(false);
    }
  }

  async function handleLoadSaved(id) {
    try {
      const r = await api.getSavedResume(id);
      setResult(r.result);
      setJd(r.job_description || "");
      setTemplate(r.template || "modern");
      setSaved(true);
      setError("");
    } catch (e) {
      setError(e.message);
    }
  }

  async function handleDeleteSaved(id) {
    try {
      await api.deleteSavedResume(id);
      loadSavedResumes();
    } catch (e) {
      setError(e.message);
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

          <label className="muted">Template</label>
          <select value={template} onChange={(e) => setTemplate(e.target.value)}>
            {templates.map((t) => <option key={t} value={t}>{t[0].toUpperCase() + t.slice(1)}</option>)}
          </select>

          {previewHtml && (
            <iframe
              title="Resume preview"
              srcDoc={previewHtml}
              style={{ width: "100%", height: "600px", border: "1px solid #334155", borderRadius: "8px", marginTop: "10px", background: "#fff" }}
            />
          )}

          <div style={{ display: "flex", gap: "8px", flexWrap: "wrap", marginTop: "12px" }}>
            <button onClick={() => handleExport("pdf")} disabled={isExporting}>
              {isExporting ? "Exporting…" : "Export as PDF"}
            </button>
            <button onClick={() => handleExport("docx")} disabled={isExporting} className="secondary">
              {isExporting ? "Exporting…" : "Export as Word (.docx)"}
            </button>
          </div>

          <div style={{ marginTop: "12px" }}>
            <input placeholder="Name this resume version (e.g. 'Acme Corp - Backend SDE')" value={saveTitle} onChange={(e) => setSaveTitle(e.target.value)} />
            <button onClick={handleSave} disabled={isSaving}>
              {isSaving ? "Saving…" : saved ? "Saved ✓" : "Save This Version"}
            </button>
          </div>
        </div>
      )}

      <div className="card">
        <h3>Saved Versions</h3>
        {savedResumes.length === 0 && <p className="muted">No saved resume versions yet.</p>}
        {savedResumes.map((r) => (
          <div className="row" key={r.id}>
            <span>{r.title} <span className="muted">({r.template}, {new Date(r.created_at).toLocaleDateString()})</span></span>
            <span>
              <button className="secondary" onClick={() => handleLoadSaved(r.id)}>Load</button>{" "}
              <button className="danger" onClick={() => window.confirm(`Delete saved resume "${r.title}"?`) && handleDeleteSaved(r.id)}>Delete</button>
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
