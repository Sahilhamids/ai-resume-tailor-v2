import { BrowserRouter, Routes, Route, Navigate, NavLink } from "react-router-dom";
import { AuthProvider, useAuth } from "./AuthContext";
import Dashboard from "./pages/Dashboard";
import Builder from "./pages/Builder";
import Auditor from "./pages/Auditor";

function Layout({ children }) {
  const { resetSession } = useAuth();

  return (
    <div className="container">
      <h1>🚀 Career Intelligence Platform</h1>
      <nav>
        <NavLink to="/dashboard" className={({ isActive }) => (isActive ? "active" : "")}>My Profile</NavLink>
        <NavLink to="/builder" className={({ isActive }) => (isActive ? "active" : "")}>Build Resume</NavLink>
        <NavLink to="/auditor" className={({ isActive }) => (isActive ? "active" : "")}>Audit PDF</NavLink>
        <button className="secondary" onClick={resetSession} title="Clears your saved profile/history and starts fresh">
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
