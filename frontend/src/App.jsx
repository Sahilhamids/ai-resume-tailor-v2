import { BrowserRouter, Routes, Route, Navigate, NavLink } from "react-router-dom";
import { AuthProvider, useAuth } from "./AuthContext";
import AuthPage from "./pages/AuthPage";
import Dashboard from "./pages/Dashboard";
import Builder from "./pages/Builder";
import Auditor from "./pages/Auditor";

function ProtectedLayout({ children }) {
  const { isAuthenticated, logout } = useAuth();
  if (!isAuthenticated) return <Navigate to="/login" replace />;

  return (
    <div className="container">
      <h1>🚀 Career Intelligence Platform</h1>
      <nav>
        <NavLink to="/dashboard" className={({ isActive }) => (isActive ? "active" : "")}>My Profile</NavLink>
        <NavLink to="/builder" className={({ isActive }) => (isActive ? "active" : "")}>Build Resume</NavLink>
        <NavLink to="/auditor" className={({ isActive }) => (isActive ? "active" : "")}>Audit PDF</NavLink>
        <button className="secondary" onClick={logout}>Log Out</button>
      </nav>
      {children}
    </div>
  );
}

function AppRoutes() {
  const { isAuthenticated } = useAuth();

  return (
    <Routes>
      <Route path="/login" element={isAuthenticated ? <Navigate to="/dashboard" replace /> : <AuthPage />} />
      <Route path="/dashboard" element={<ProtectedLayout><Dashboard /></ProtectedLayout>} />
      <Route path="/builder" element={<ProtectedLayout><Builder /></ProtectedLayout>} />
      <Route path="/auditor" element={<ProtectedLayout><Auditor /></ProtectedLayout>} />
      <Route path="*" element={<Navigate to={isAuthenticated ? "/dashboard" : "/login"} replace />} />
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
