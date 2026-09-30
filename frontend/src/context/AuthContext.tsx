import { createContext, useContext, useState, ReactNode, useCallback } from 'react';
import type { AuthState } from '../types';

interface AuthContextType {
  auth: AuthState;
  setAuth: (auth: AuthState) => void;
  logout: () => void;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [auth, setAuth] = useState<AuthState>({
    token: null,
    email: null,
    name: null,
    organizationId: null,
  });

  const logout = useCallback(() => {
    setAuth({ token: null, email: null, name: null, organizationId: null });
  }, []);

  const value: AuthContextType = {
    auth,
    setAuth,
    logout,
    isAuthenticated: !!auth.token,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}
