/**
 * Authentication Context
 * Manages user authentication state and provides auth utilities
 */
import React, { createContext, useContext, useState, useEffect, useCallback, ReactNode } from 'react';

interface User {
  user_id: string;
  email: string;
  username: string;
  first_name?: string;
  last_name?: string;
  is_active: boolean;
  is_superuser: boolean;
  roles: string[];
  permissions: string[];
}

interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

interface AuthContextType {
  user: User | null;
  tokens: AuthTokens | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  refreshToken: () => Promise<boolean>;
  hasPermission: (permission: string) => boolean;
  hasAnyPermission: (permissions: string[]) => boolean;
  hasRole: (role: string) => boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const TOKEN_STORAGE_KEY = 'gps_cdm_tokens';
const USER_STORAGE_KEY = 'gps_cdm_user';

// Decode JWT payload without library
function decodeJWT(token: string): any {
  try {
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split('')
        .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    );
    return JSON.parse(jsonPayload);
  } catch {
    return null;
  }
}

// Check if token is expired
function isTokenExpired(token: string): boolean {
  const payload = decodeJWT(token);
  if (!payload || !payload.exp) return true;
  return Date.now() >= payload.exp * 1000;
}

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [tokens, setTokens] = useState<AuthTokens | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Load stored auth on mount
  useEffect(() => {
    const storedTokens = localStorage.getItem(TOKEN_STORAGE_KEY);
    const storedUser = localStorage.getItem(USER_STORAGE_KEY);

    if (storedTokens && storedUser) {
      const parsedTokens = JSON.parse(storedTokens);

      // Check if access token is expired
      if (!isTokenExpired(parsedTokens.access_token)) {
        setTokens(parsedTokens);
        setUser(JSON.parse(storedUser));
      } else {
        // Clear expired tokens
        localStorage.removeItem(TOKEN_STORAGE_KEY);
        localStorage.removeItem(USER_STORAGE_KEY);
      }
    }

    setIsLoading(false);
  }, []);

  const login = useCallback(async (username: string, password: string) => {
    const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

    const response = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: new URLSearchParams({ username, password }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Login failed');
    }

    const authTokens: AuthTokens = await response.json();

    // Decode user info from token
    const payload = decodeJWT(authTokens.access_token);
    const userData: User = {
      user_id: payload.sub,
      email: payload.email,
      username: payload.username,
      is_active: true,
      is_superuser: payload.is_superuser,
      roles: payload.roles || [],
      permissions: payload.permissions || [],
    };

    // Store in state and localStorage
    setTokens(authTokens);
    setUser(userData);
    localStorage.setItem(TOKEN_STORAGE_KEY, JSON.stringify(authTokens));
    localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(userData));
  }, []);

  const logout = useCallback(() => {
    setUser(null);
    setTokens(null);
    localStorage.removeItem(TOKEN_STORAGE_KEY);
    localStorage.removeItem(USER_STORAGE_KEY);
  }, []);

  const refreshToken = useCallback(async (): Promise<boolean> => {
    if (!tokens?.refresh_token) return false;

    try {
      const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

      const response = await fetch(`${API_BASE}/auth/refresh`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ refresh_token: tokens.refresh_token }),
      });

      if (!response.ok) {
        logout();
        return false;
      }

      const newTokens: AuthTokens = await response.json();

      // Decode user info from new token
      const payload = decodeJWT(newTokens.access_token);
      const userData: User = {
        user_id: payload.sub,
        email: payload.email,
        username: payload.username,
        is_active: true,
        is_superuser: payload.is_superuser,
        roles: payload.roles || [],
        permissions: payload.permissions || [],
      };

      setTokens(newTokens);
      setUser(userData);
      localStorage.setItem(TOKEN_STORAGE_KEY, JSON.stringify(newTokens));
      localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(userData));

      return true;
    } catch {
      logout();
      return false;
    }
  }, [tokens, logout]);

  const hasPermission = useCallback((permission: string): boolean => {
    if (!user) return false;
    if (user.is_superuser) return true;
    return user.permissions.includes(permission);
  }, [user]);

  const hasAnyPermission = useCallback((permissions: string[]): boolean => {
    if (!user) return false;
    if (user.is_superuser) return true;
    return permissions.some(p => user.permissions.includes(p));
  }, [user]);

  const hasRole = useCallback((role: string): boolean => {
    if (!user) return false;
    if (user.is_superuser) return true;
    return user.roles.includes(role);
  }, [user]);

  const value: AuthContextType = {
    user,
    tokens,
    isAuthenticated: !!user && !!tokens,
    isLoading,
    login,
    logout,
    refreshToken,
    hasPermission,
    hasAnyPermission,
    hasRole,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export default AuthContext;
