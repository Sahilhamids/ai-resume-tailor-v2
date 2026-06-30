import { createContext, useContext, useState, useCallback, useEffect, useRef } from "react";
import { getToken, setToken, clearToken, createAnonymousSession } from "./api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [isReady, setIsReady] = useState(false);
  const [error, setError] = useState("");
  const bootstrapping = useRef(false);

  const bootstrapSession = useCallback(async () => {
    if (bootstrapping.current) return;
    bootstrapping.current = true;
    try {
      const data = await createAnonymousSession();
      setToken(data.access_token);
      setError("");
    } catch {
      setError("Couldn't start a session. Please refresh the page.");
    } finally {
      bootstrapping.current = false;
      setIsReady(true);
    }
  }, []);

  useEffect(() => {
    if (getToken()) {
      setIsReady(true);
    } else {
      bootstrapSession();
    }
  }, [bootstrapSession]);

  const resetSession = useCallback(async () => {
    clearToken();
    setIsReady(false);
    await bootstrapSession();
  }, [bootstrapSession]);

  return (
    <AuthContext.Provider value={{ isReady, error, resetSession }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
