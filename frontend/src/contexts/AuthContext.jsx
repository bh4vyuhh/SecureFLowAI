import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(true);

  useEffect(() => {
    setUser({
      id: 'usr-0988',
      name: 'Amy Chen',
      email: 'a.chen@secureflow.corp',
      role: 'Ops Lead',
      department: 'SecOps',
      lastLogin: new Date().toISOString()
    });
    setIsAuthenticated(true);
  }, []);

  const login = async (email, password) => {
    setLoading(true);
    try {
      setUser({
        id: 'usr-0988',
        name: 'Amy Chen',
        email: email || 'a.chen@secureflow.corp',
        role: 'Ops Lead',
        department: 'SecOps',
        lastLogin: new Date().toISOString()
      });
      setIsAuthenticated(true);
      return true;
    } finally {
      setLoading(false);
    }
  };

  const register = async (name, email, password) => {
    setLoading(true);
    try {
      setUser({
        id: 'usr-0988',
        name: name || 'Amy Chen',
        email: email || 'a.chen@secureflow.corp',
        role: 'Ops Lead',
        department: 'SecOps',
        lastLogin: new Date().toISOString()
      });
      setIsAuthenticated(true);
      return true;
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    setUser(null);
    setIsAuthenticated(false);
  };

  return (
    <AuthContext.Provider value={{ user, loading, isAuthenticated, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
export default AuthContext;
