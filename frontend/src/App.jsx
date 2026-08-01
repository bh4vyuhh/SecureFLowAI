import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { ToastProvider } from './contexts/ToastContext';

import { LoginPage }         from './pages/auth/LoginPage';
import { RegisterPage }      from './pages/auth/RegisterPage';
import { DashboardPage }     from './pages/DashboardPage';
import { NotificationsPage } from './pages/NotificationsPage';
import { ProfilePage }       from './pages/ProfilePage';
import { AppLayout }         from './components/layout/AppLayout';

const Protected = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();
  if (loading) {
    return (
      <div style={{
        minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center',
        background: 'var(--bg-primary)',
      }}>
        <div style={{
          width: 44, height: 44,
          border: '3px solid var(--border)',
          borderTopColor: 'var(--accent)',
          borderRadius: '50%',
          animation: 'spin 0.8s linear infinite',
        }} />
      </div>
    );
  }
  return isAuthenticated ? children : <Navigate to="/login" replace />;
};

const PublicOnly = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();
  if (loading) return null;
  return isAuthenticated ? <Navigate to="/dashboard" replace /> : children;
};

const Placeholder = ({ title }) => {
  return (
    <div style={{ padding: '40px 32px', textAlign: 'center' }}>
      <div style={{ fontSize: '2rem', marginBottom: 12 }}>🚧</div>
      <h2 style={{ color: 'var(--text-primary)', fontFamily: 'var(--font-display)', marginBottom: 8 }}>{title}</h2>
      <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>This page is coming in the next sprint</p>
    </div>
  );
};

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <ToastProvider>
          <Routes>
            <Route path="/login"    element={<PublicOnly><LoginPage /></PublicOnly>} />
            <Route path="/register" element={<PublicOnly><RegisterPage /></PublicOnly>} />

            <Route path="/dashboard"     element={<Protected><DashboardPage /></Protected>} />
            <Route path="/notifications" element={<Protected><NotificationsPage /></Protected>} />
            <Route path="/profile"       element={<Protected><ProfilePage /></Protected>} />

            <Route path="/upload"    element={<Protected><AppLayout><Placeholder title="Document Upload" /></AppLayout></Protected>} />
            <Route path="/documents" element={<Protected><AppLayout><Placeholder title="Document Library" /></AppLayout></Protected>} />
            <Route path="/history"   element={<Protected><AppLayout><Placeholder title="Audit History" /></AppLayout></Protected>} />

            <Route path="*" element={<Navigate to="/dashboard" replace />} />
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </ToastProvider>
      </AuthProvider>
    </BrowserRouter>
  );
}
