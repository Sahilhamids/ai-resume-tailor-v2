import { useEffect, useState } from "react";
import * as api from "../api";
import ErrorBanner from "../components/ErrorBanner";

const STATUSES = ["applied", "interviewing", "offer", "rejected"];
const STATUS_LABELS = { applied: "Applied", interviewing: "Interviewing", offer: "Offer", rejected: "Rejected" };

export default function JobTracker() {
  const [jobs, setJobs] = useState([]);
  const [error, setError] = useState("");
  const [form, setForm] = useState({ company: "", role: "", notes: "" });
  const [isAdding, setIsAdding] = useState(false);

  function loadJobs() {
    api.listJobApplications().then(setJobs).catch((e) => setError(e.message));
  }

  useEffect(() => { loadJobs(); }, []);

  async function handleAdd() {
    if (!form.company.trim() || !form.role.trim()) {
      return setError("Company and role are required.");
    }
    setIsAdding(true);
    try {
      await api.createJobApplication({ ...form, status: "applied" });
      setForm({ company: "", role: "", notes: "" });
      loadJobs();
    } catch (e) {
      setError(e.message);
    } finally {
      setIsAdding(false);
    }
  }

  async function handleStatusChange(id, status) {
    try {
      await api.updateJobStatus(id, status);
      loadJobs();
    } catch (e) {
      setError(e.message);
    }
  }

  async function handleDelete(id) {
    try {
      await api.deleteJobApplication(id);
      loadJobs();
    } catch (e) {
      setError(e.message);
    }
  }

  return (
    <div>
      <ErrorBanner message={error} />

      <div className="card">
        <h3>Add an Application</h3>
        <input placeholder="Company" value={form.company} onChange={(e) => setForm({ ...form, company: e.target.value })} disabled={isAdding} />
        <input placeholder="Role" value={form.role} onChange={(e) => setForm({ ...form, role: e.target.value })} disabled={isAdding} />
        <textarea placeholder="Notes (optional)" value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })} disabled={isAdding} />
        <button onClick={handleAdd} disabled={isAdding}>{isAdding ? "Adding…" : "Add Application"}</button>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "12px" }}>
        {STATUSES.map((status) => (
          <div className="card" key={status}>
            <h3>{STATUS_LABELS[status]} ({jobs.filter((j) => j.status === status).length})</h3>
            {jobs.filter((j) => j.status === status).map((j) => (
              <div key={j.id} style={{ background: "#0f172a", borderRadius: "8px", padding: "10px", marginBottom: "8px" }}>
                <div><b>{j.role}</b></div>
                <div className="muted">{j.company}</div>
                {j.notes && <p className="muted" style={{ fontSize: "12px" }}>{j.notes}</p>}
                <select value={j.status} onChange={(e) => handleStatusChange(j.id, e.target.value)} style={{ marginTop: "6px" }}>
                  {STATUSES.map((s) => <option key={s} value={s}>{STATUS_LABELS[s]}</option>)}
                </select>
                <button className="danger" onClick={() => handleDelete(j.id)} style={{ marginTop: "6px", width: "100%" }}>
                  Delete
                </button>
              </div>
            ))}
            {jobs.filter((j) => j.status === status).length === 0 && <p className="muted">Nothing here yet.</p>}
          </div>
        ))}
      </div>
    </div>
  );
}
