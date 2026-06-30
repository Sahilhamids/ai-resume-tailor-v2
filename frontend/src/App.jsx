import { BrowserRouter, Routes, Route, Navigate, NavLink } from "react-router-dom";
import { AuthProvider, useAuth } from "./AuthContext";
import Dashboard from "./pages/Dashboard";
import Builder from "./pages/Builder";
import Auditor from "./pages/Auditor";
import CoverLetter from "./pages/CoverLetter";
import JobTracker from "./pages/JobTracker";
import Account from "./pages/Account";
import About from "./pages/About";

function Layout({ children }) {
  const { resetSession } = useAuth();

  function handleResetSession() {
    if (window.confirm("This permanently deletes your profile, saved resumes, cover letters, and job tracker data on this browser. Continue?")) {
      resetSession();
    }
  }

  return (
    <div className="container">
      <h1>🚀 Career Intelligence Platform</h1>
      <nav>
        <NavLink to="/dashboard" className={({ isActive }) => (isActive ? "active" : "")}>My Profile</NavLink>
        <NavLink to="/builder" className={({ isActive }) => (isActive ? "active" : "")}>Build Resume</NavLink>
        <NavLink to="/auditor" className={({ isActive }) => (isActive ? "active" : "")}>Audit PDF</NavLink>
        <NavLink to="/cover-letter" className={({ isActive }) => (isActive ? "active" : "")}>Cover Letter</NavLink>
        <NavLink to="/jobs" className={({ isActive }) => (isActive ? "active" : "")}>Job Tracker</NavLink>
        <NavLink to="/account" className={({ isActive }) => (isActive ? "active" : "")}>Account</NavLink>
        <NavLink to="/about" className={({ isActive }) => (isActive ? "active" : "")}>About</NavLink>
        <button className="secondary" onClick={handleResetSession} title="Permanently deletes your data on this browser and starts fresh">
          Start New Session
        </button>
      </nav>
      {children}
    </div>
  );
}

function AppRoutes() {
  const { isReady, error } = useAuth();

  if (!isReady) {
    return (
      <div className="container">
        <h1>🚀 Career Intelligence Platform</h1>
        {error ? <div className="error-banner">{error}</div> : <p className="muted">Starting your session…</p>}
      </div>
    );
  }

  return (
    <Routes>
      <Route path="/dashboard" element={<Layout><Dashboard /></Layout>} />
      <Route path="/builder" element={<Layout><Builder /></Layout>} />
      <Route path="/auditor" element={<Layout><Auditor /></Layout>} />
      <Route path="/cover-letter" element={<Layout><CoverLetter /></Layout>} />
      <Route path="/jobs" element={<Layout><JobTracker /></Layout>} />
      <Route path="/account" element={<Layout><Account /></Layout>} />
      <Route path="/about" element={<Layout><About /></Layout>} />
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </BrowserRouter>
  );
}
