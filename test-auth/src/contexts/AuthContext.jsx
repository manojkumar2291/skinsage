import { createContext, useContext, useState, useEffect } from 'react';
import { getCurrentUser, logout as logoutService, isAuthenticated } from '../api/authService';

const AuthContext = createContext(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isAuth, setIsAuth] = useState(false);

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    if (isAuthenticated()) {
      try {
        const userData = await getCurrentUser();

        setUser(userData);
        console.log('Authenticated user:', userData);
        setIsAuth(true);
      } catch (error) {
        console.error('Auth check failed:', error);
        setUser(null);
        setIsAuth(false);
      }
    }
    setLoading(false);
  };

  const login = (userData) => {
    setUser(userData);
    setIsAuth(true);
  };

  const logout = () => {
    logoutService();
    setUser(null);
    setIsAuth(false);
  };

  const updateUser = (userData) => {
    setUser(prev => ({ ...prev, ...userData }));
  };

  const value = {
    user,
    loading,
    isAuthenticated: isAuth,
    login,
    logout,
    updateUser,
    refreshUser: checkAuth,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};