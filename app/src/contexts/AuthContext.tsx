"use client";

import { createContext, useCallback, useContext, useEffect, useState } from "react";
import { getStoredToken, setStoredToken } from "../lib/auth";
import { getApiUrl } from "../lib/api";
import type { User } from "../lib/auth";

interface AuthState {
  token: string | null;
  user: User | null;
  loading: boolean;
}

interface AuthContextValue extends AuthState {
  setToken: (token: string | null) => void;
  logout: () => void;
  refetchUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [token, setTokenState] = useState<string | null>(null);
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  const setToken = useCallback((t: string | null) => {
    setStoredToken(t);
    setTokenState(t);
    if (!t) setUser(null);
  }, []);

  const refetchUser = useCallback(async () => {
    const t = getStoredToken();
    if (!t) {
      setUser(null);
      return;
    }
    try {
      const res = await fetch(getApiUrl("/api/auth/me"), {
        headers: { Authorization: `Bearer ${t}` },
      });
      if (res.ok) {
        const u = await res.json();
        setUser(u);
      } else {
        setToken(null);
      }
    } catch {
      setToken(null);
    }
  }, [setToken]);

  useEffect(() => {
    const t = getStoredToken();
    setTokenState(t);
    if (t) {
      refetchUser().finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, [refetchUser]);

  const logout = useCallback(() => {
    setToken(null);
  }, [setToken]);

  const value: AuthContextValue = {
    token,
    user,
    loading,
    setToken,
    logout,
    refetchUser,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
