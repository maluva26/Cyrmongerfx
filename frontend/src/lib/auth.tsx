"use client";

import { createContext, useCallback, useContext, useEffect, useState } from "react";
import { restoreSession, subscribeToSession, type ApiUser } from "@/lib/api";

export type User = ApiUser;
export type AuthStatus = "loading" | "authenticated" | "anonymous";

type AuthContextValue = {
  user: User | null;
  token: string | null;
  status: AuthStatus;
  setAuth: (user: User, token: string) => void;
  clear: () => void;
};

const AuthContext = createContext<AuthContextValue>({
  user: null,
  token: null,
  status: "loading",
  setAuth: () => {},
  clear: () => {},
});

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [status, setStatus] = useState<AuthStatus>("loading");

  const applySession = useCallback((session: { access: string; user: User } | null) => {
    if (session) {
      setUser(session.user);
      setToken(session.access);
      setStatus("authenticated");
      return;
    }
    setUser(null);
    setToken(null);
    setStatus("anonymous");
  }, []);

  const setAuth = useCallback((nextUser: User, nextToken: string) => {
    setUser(nextUser);
    setToken(nextToken);
    setStatus("authenticated");
  }, []);

  const clear = useCallback(() => applySession(null), [applySession]);

  useEffect(() => {
    let active = true;
    const unsubscribe = subscribeToSession((session) => {
      if (active) applySession(session);
    });

    void restoreSession().then((session) => {
      if (active) applySession(session);
    }).catch(() => {
      if (active) applySession(null);
    });

    return () => {
      active = false;
      unsubscribe();
    };
  }, [applySession]);

  return (
    <AuthContext.Provider value={{ user, token, status, setAuth, clear }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
