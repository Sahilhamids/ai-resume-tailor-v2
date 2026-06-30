import { createContext, useContext, useState, useCallback, useEffect, useRef } from "react";
import { getToken, setToken, clearToken, createAnonymousSession, login as apiLogin } from "./api";

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

  const login = useCallback(async (email, password) => {
    const data = await apiLogin(email, password);
    setToken(data.access_token);
  }, []);

  return (
    <AuthContext.Provider value={{ isReady, error, resetSession, login }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
