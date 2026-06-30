import { useEffect, useState } from "react";
import * as api from "../api";
import { useAuth } from "../AuthContext";
import ErrorBanner from "../components/ErrorBanner";

export default function Account() {
  const { login, resetSession } = useAuth();
  const [status, setStatus] = useState(null);
  const [error, setError] = useState("");
  const [info, setInfo] = useState("");

  const [linkEmail, setLinkEmail] = useState("");
  const [linkPassword, setLinkPassword] = useState("");
  const [isLinking, setIsLinking] = useState(false);

  const [loginEmail, setLoginEmail] = useState("");
  const [loginPassword, setLoginPassword] = useState("");
  const [isLoggingIn, setIsLoggingIn] = useState(false);

  const [isDeleting, setIsDeleting] = useState(false);

  function loadStatus() {
    api.getAccountStatus().then(setStatus).catch((e) => setError(e.message));
  }

  useEffect(() => { loadStatus(); }, []);

  async function handleLinkAccount() {
    if (!linkEmail.trim() || linkPassword.length < 6) {
      return setError("Enter an email and a password of at least 6 characters.");
    }
    setIsLinking(true);
    try {
      await api.linkAccount(linkEmail, linkPassword);
      setInfo("Account linked. You can now log in with this email/password on any device.");
      setError("");
      loadStatus();
    } catch (e) {
      setError(e.message);
    } finally {
      setIsLinking(false);
    }
  }

  async function handleLogin() {
    if (!loginEmail.trim() || !loginPassword) {
      return setError("Enter your email and password.");
    }
    setIsLoggingIn(true);
    try {
      await login(loginEmail, loginPassword);
      setInfo("Logged in.");
      setError("");
      window.location.reload();
    } catch (e) {
      setError(e.message);
    } finally {
      setIsLoggingIn(false);
    }
  }

  async function handleDeleteAccount() {
    const confirmed = window.confirm(
      "This permanently deletes your account and ALL data — profile, saved resumes, cover letters, job tracker, audit history. This cannot be undone. Continue?"
    );
    if (!confirmed) return;
    setIsDeleting(true);
    try {
      await api.deleteAccount();
      await resetSession();
      window.location.href = "/dashboard";
    } catch (e) {
      setError(e.message);
      setIsDeleting(false);
    }
  }

  return (
    <div>
      <ErrorBanner message={error} />
      {info && <div className="card" style={{ borderLeft: "4px solid #22c55e" }}><p>{info}</p></div>}

      <div className="card">
        <h3>Session Status</h3>
        {status && (
          status.is_anonymous
            ? <p className="muted">This session has no email linked — it only exists on this browser. Link an email below to access it from other devices.</p>
            : <p>Linked to <b>{status.email}</b> — you can log in with this email from any device.</p>
        )}
      </div>

      {status?.is_anonymous && (
        <div className="card">
          <h3>Access From Other Devices</h3>
          <p className="muted">Link an email and password to this session so you can log in from your phone, another browser, etc.</p>
          <input type="email" placeholder="Email" value={linkEmail} onChange={(e) => setLinkEmail(e.target.value)} disabled={isLinking} />
          <input type="password" placeholder="Password (min 6 characters)" value={linkPassword} onChange={(e) => setLinkPassword(e.target.value)} disabled={isLinking} />
          <button onClick={handleLinkAccount} disabled={isLinking}>{isLinking ? "Linking…" : "Link Account"}</button>
        </div>
      )}

      <div className="card">
        <h3>Log Into a Different Account</h3>
        <p className="muted">Already linked an account on another device? Log in here to switch to it (this replaces your current session).</p>
        <input type="email" placeholder="Email" value={loginEmail} onChange={(e) => setLoginEmail(e.target.value)} disabled={isLoggingIn} />
        <input type="password" placeholder="Password" value={loginPassword} onChange={(e) => setLoginPassword(e.target.value)} disabled={isLoggingIn} />
        <button onClick={handleLogin} disabled={isLoggingIn}>{isLoggingIn ? "Logging in…" : "Log In"}</button>
      </div>

      <div className="card" style={{ borderLeft: "4px solid #ef4444" }}>
        <h3>Delete Account</h3>
        <p className="muted">Permanently deletes your account and everything tied to it. This cannot be undone.</p>
        <button className="danger" onClick={handleDeleteAccount} disabled={isDeleting}>
          {isDeleting ? "Deleting…" : "Delete My Account"}
        </button>
      </div>
    </div>
  );
}
