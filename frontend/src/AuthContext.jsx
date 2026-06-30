import { createContext, useContext, useState, useCallback } from "react";
import { getToken, setToken, clearToken, signup as apiSignup, login as apiLogin } from "./api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [isAuthenticated, setIsAuthenticated] = useState(!!getToken());

  const signup = useCallback(async (email, password) => {
    const data = await apiSignup(email, password);
    setToken(data.access_token);
    setIsAuthenticated(true);
  }, []);

  const login = useCallback(async (email, password) => {
    const data = await apiLogin(email, password);
    setToken(data.access_token);
    setIsAuthenticated(true);
  }, []);

  const logout = useCallback(() => {
    clearToken();
    setIsAuthenticated(false);
  }, []);

  return (
    <AuthContext.Provider value={{ isAuthenticated, signup, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
