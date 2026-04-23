import { useState, useCallback, useEffect, createContext, useContext } from "react";
import API from "../services/api.js";

const TOKEN_KEY = "moodly_token";
const USER_KEY  = "moodly_user";

export const AuthContext = createContext(null);

export function useAuth() {
  return useContext(AuthContext);
}

export function AuthProvider({ children }) {
  const [user,     setUser]     = useState(() => {
    try { return JSON.parse(localStorage.getItem(USER_KEY)); } catch { return null; }
  });
  const [loading,  setLoading]  = useState(false);
  const [error,    setError]    = useState(null);
  const [onLoginCb, setOnLoginCb] = useState(null); // callback after login state settles

  // Attach token on mount
  useEffect(() => {
    const token = localStorage.getItem(TOKEN_KEY);
    if (token) API.defaults.headers.common["Authorization"] = `Bearer ${token}`;
  }, []);

  // Fire callback AFTER user state has actually updated
  useEffect(() => {
    if (user && onLoginCb) {
      onLoginCb();
      setOnLoginCb(null);
    }
  }, [user, onLoginCb]);

  const _saveAuth = (token, userData) => {
    localStorage.setItem(TOKEN_KEY, token);
    localStorage.setItem(USER_KEY, JSON.stringify(userData));
    API.defaults.headers.common["Authorization"] = `Bearer ${token}`;
    setUser(userData);
  };

  const register = useCallback(async (username, email, password) => {
    setLoading(true); setError(null);
    try {
      // Register only — do NOT auto-login, user must sign in manually
      await API.post("/auth/register", { username, email, password });
      return { success: true };
    } catch (e) {
      const msg = e?.response?.data?.error || "Registration failed";
      setError(msg);
      return { success: false, error: msg };
    } finally { setLoading(false); }
  }, []);

  const login = useCallback(async (email, password, cb) => {
    setLoading(true); setError(null);
    try {
      const { data } = await API.post("/auth/login", { email, password });
      _saveAuth(data.token, data.user);
      if (cb) setOnLoginCb(() => cb);
      return { success: true };
    } catch (e) {
      const msg = e?.response?.data?.error || "Login failed";
      setError(msg);
      return { success: false, error: msg };
    } finally { setLoading(false); }
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
    delete API.defaults.headers.common["Authorization"];
    setUser(null);
    setError(null);
  }, []);

  const clearError = useCallback(() => setError(null), []);

  return (
    <AuthContext.Provider value={{
      user, loading, error,
      register, login, logout, clearError,
      isLoggedIn: !!user,
    }}>
      {children}
    </AuthContext.Provider>
  );
}