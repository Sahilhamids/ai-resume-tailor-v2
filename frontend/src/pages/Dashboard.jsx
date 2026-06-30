import { useEffect, useState } from "react";
import * as api from "../api";
import ErrorBanner from "../components/ErrorBanner";

export default function Dashboard() {
  const [error, setError] = useState("");
  const [profile, setProfile] = useState(null);
  const [form, setForm] = useState({ full_name: "", phone: "", linkedin: "", github: "", target_role: "" });
  const [newSkill, setNewSkill] = useState("");
  const [emp, setEmp] = useState({ company: "", role: "", start_date: "", end_date: "", responsibilities: "" });
  const [proj, setProj] = useState({ name: "", description: "", link: "" });
  const [isOnboarding, setIsOnboarding] = useState(false);

  async function loadProfile() {
    try {
      const p = await api.getProfile();
      setProfile(p);
      setForm({
        full_name: p.full_name || "",
        phone: p.phone || "",
        linkedin: p.linkedin || "",
        github: p.github || "",
        target_role: p.target_role || "",
      });
    } catch (e) {
      setError(e.message);
    }
  }

  useEffect(() => { loadProfile(); }, []);

  async function handleAction(fn) {
    try {
      await fn();
      await loadProfile();
    } catch (e) {
      setError(e.message);
    }
  }

  async function onboardFromPdf(e) {
    const file = e.target.files[0];
    if (!file) return;
    setIsOnboarding(true);
    try {
      await handleAction(() => api.onboardFromPdf(file));
    } finally {
      setIsOnboarding(false);
      e.target.value = "";
    }
  }

  if (!profile) return <ErrorBanner message={error} />;

  const isFirstTime = !profile.full_name && profile.skills.length === 0 && profile.employment.length === 0 && profile.projects.length === 0;

  return (
    <div>
      <ErrorBanner message={error} />

      {isFirstTime && (
        <div className="card" style={{ borderLeft: "4px solid #6366f1" }}>
          <h3>Welcome 👋</h3>
          <p className="muted">
            No account needed — your profile and history are saved to this browser automatically.
            Get started by uploading an existing resume below (AI auto-fills everything), or fill in
            your basic info manually. Once your profile has at least one skill or job, head to
            <b> Build Resume</b> to generate a tailored version for a specific job posting.
          </p>
        </div>
      )}

      <div className="card">
        <h3>AI Onboarding</h3>
        <p className="muted">Upload an existing resume PDF to auto-fill your profile.</p>
        <input type="file" accept=".pdf" onChange={onboardFromPdf} disabled={isOnboarding} />
        {isOnboarding && <p className="muted">Extracting and filling your profile…</p>}
      </div>

      <div className="card">
        <h3>Basic Info</h3>
        <input placeholder="Full Name" value={form.full_name} onChange={(e) => setForm({ ...form, full_name: e.target.value })} />
        <input placeholder="Phone" value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} />
        <input placeholder="LinkedIn URL" value={form.linkedin} onChange={(e) => setForm({ ...form, linkedin: e.target.value })} />
        <input placeholder="GitHub URL" value={form.github} onChange={(e) => setForm({ ...form, github: e.target.value })} />
        <input placeholder="Target Role" value={form.target_role} onChange={(e) => setForm({ ...form, target_role: e.target.value })} />
        <button onClick={() => handleAction(() => api.updateProfile(form))}>Save Profile</button>
      </div>

      <div className="card">
        <h3>Skills</h3>
        {profile.skills.length === 0 && <p className="muted">No skills yet.</p>}
        {profile.skills.map(([id, name]) => (
          <div className="row" key={id}>
            <span>{name}</span>
            <button className="danger" onClick={() => handleAction(() => api.deleteSkill(id))}>Remove</button>
          </div>
        ))}
        <input placeholder="Add a skill" value={newSkill} onChange={(e) => setNewSkill(e.target.value)} />
        <button onClick={() => handleAction(async () => { await api.addSkill(newSkill); setNewSkill(""); })}>Add Skill</button>
      </div>

      <div className="card">
        <h3>Employment History</h3>
        {profile.employment.length === 0 && <p className="muted">No employment history yet.</p>}
        {profile.employment.map(([id, company, role, start, end]) => (
          <div className="row" key={id}>
            <span><b>{role}</b> @ {company} ({start} - {end})</span>
            <button className="danger" onClick={() => handleAction(() => api.deleteEmployment(id))}>Remove</button>
          </div>
        ))}
        <input placeholder="Company" value={emp.company} onChange={(e) => setEmp({ ...emp, company: e.target.value })} />
        <input placeholder="Role Title" value={emp.role} onChange={(e) => setEmp({ ...emp, role: e.target.value })} />
        <input placeholder="Start Date" value={emp.start_date} onChange={(e) => setEmp({ ...emp, start_date: e.target.value })} />
        <input placeholder="End Date" value={emp.end_date} onChange={(e) => setEmp({ ...emp, end_date: e.target.value })} />
        <textarea placeholder="Responsibilities" value={emp.responsibilities} onChange={(e) => setEmp({ ...emp, responsibilities: e.target.value })} />
        <button onClick={() => handleAction(async () => { await api.addEmployment(emp); setEmp({ company: "", role: "", start_date: "", end_date: "", responsibilities: "" }); })}>Add Job</button>
      </div>

      <div className="card">
        <h3>Projects</h3>
        {profile.projects.length === 0 && <p className="muted">No projects yet.</p>}
        {profile.projects.map(([id, name, description]) => (
          <div className="row" key={id}>
            <span><b>{name}</b> - {description}</span>
            <button className="danger" onClick={() => handleAction(() => api.deleteProject(id))}>Remove</button>
          </div>
        ))}
        <input placeholder="Project Name" value={proj.name} onChange={(e) => setProj({ ...proj, name: e.target.value })} />
        <textarea placeholder="Description" value={proj.description} onChange={(e) => setProj({ ...proj, description: e.target.value })} />
        <input placeholder="Link" value={proj.link} onChange={(e) => setProj({ ...proj, link: e.target.value })} />
        <button onClick={() => handleAction(async () => { await api.addProject(proj); setProj({ name: "", description: "", link: "" }); })}>Add Project</button>
      </div>
    </div>
  );
}
