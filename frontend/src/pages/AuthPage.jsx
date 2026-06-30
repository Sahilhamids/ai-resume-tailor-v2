import { useState } from "react";
import { useAuth } from "../AuthContext";
import ErrorBanner from "../components/ErrorBanner";

export default function AuthPage() {
  const { signup, login } = useAuth();
  const [isSignup, setIsSignup] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  async function handleSubmit(e) {
    e.preventDefault();
    if (!email || !password) return setError("Email and password are required.");
    try {
      if (isSignup) {
        await signup(email, password);
      } else {
        await login(email, password);
      }
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="container">
      <h1>🚀 Career Intelligence Platform</h1>
      <ErrorBanner message={error} />
      <form className="card" onSubmit={handleSubmit}>
        <h2>{isSignup ? "Sign Up" : "Log In"}</h2>
        <input type="email" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} />
        <input type="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} />
        <button type="submit">{isSignup ? "Sign Up" : "Log In"}</button>
        <p className="muted">
          {isSignup ? "Already have an account?" : "Don't have an account?"}{" "}
          <a href="#" onClick={(e) => { e.preventDefault(); setIsSignup(!isSignup); setError(""); }}>
            {isSignup ? "Log in" : "Sign up"}
          </a>
        </p>
      </form>
    </div>
  );
}
