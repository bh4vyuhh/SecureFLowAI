import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import {
  LayoutDashboard, FileText, Activity, Brain, ShieldAlert,
  ScrollText, BarChart3, Puzzle, Settings, LogOut, Shield, HelpCircle
} from 'lucide-react';

const NAV_ITEMS = [
  { label: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
  { label: 'Documents', path: '/documents', icon: FileText },
  { label: 'Analytics', path: '/ai-analysis', icon: Brain },
];

const TRADING_ITEMS = [
  { label: 'Live Monitor', path: '/live-monitor', icon: Activity },
  { label: 'Risk Center', path: '/risk-center', icon: ShieldAlert },
  { label: 'Audit Logs', path: '/audit-logs', icon: ScrollText },
  { label: 'Reports', path: '/reports', icon: BarChart3 },
  { label: 'Browser Extension', path: '/browser-ext', icon: Puzzle },
];

const SYSTEM_ITEMS = [
  { label: 'Settings', path: '/settings', icon: Settings },
];

const NavItem = ({ label, path, icon: Icon }) => (
  <NavLink
    to={path}
    style={({ isActive }) => ({
      display: 'flex',
      alignItems: 'center',
      gap: 12,
      padding: '9px 14px',
      borderRadius: 10,
      fontSize: '0.84rem',
      fontWeight: isActive ? 600 : 450,
      color: isActive ? '#fff' : 'rgba(255,255,255,0.4)',
      background: isActive ? 'rgba(255,255,255,0.06)' : 'transparent',
      textDecoration: 'none',
      marginBottom: 2,
      transition: 'all 0.15s ease',
    })}
  >
    <Icon size={16} style={{ opacity: 0.85 }} />
    {label}
  </NavLink>
);

const SectionLabel = ({ children }) => (
  <div style={{
    fontSize: '0.65rem',
    fontWeight: 700,
    letterSpacing: '0.1em',
    color: 'rgba(255,255,255,0.2)',
    padding: '18px 14px 6px',
    textTransform: 'uppercase',
  }}>
    {children}
  </div>
);

export const Sidebar = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const initials = user?.name?.split(' ').map(n => n[0]).join('').slice(0, 2).toUpperCase() || 'SF';

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <aside style={{
      display: 'flex',
      flexDirection: 'column',
      height: '100%',
      padding: '0 14px',
    }}>

      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: 10,
        padding: '22px 10px 20px',
      }}>
     
        <div>
          <div style={{ fontSize: '1rem', fontWeight: 700, color: '#fff', letterSpacing: '-0.02em', lineHeight: 1.1 }}>
            SecureFlow
          </div>

        </div>
      </div>

      <nav style={{ flex: 1, overflowY: 'auto', paddingBottom: 16 }}>
        {NAV_ITEMS.map(item => <NavItem key={item.path} {...item} />)}

        <SectionLabel>Monitoring</SectionLabel>
        {TRADING_ITEMS.map(item => <NavItem key={item.path} {...item} />)}

        <SectionLabel>System</SectionLabel>
        {SYSTEM_ITEMS.map(item => <NavItem key={item.path} {...item} />)}
      </nav>

      <div style={{
        borderTop: '1px solid rgba(255,255,255,0.05)',
        padding: '12px 8px',
      }}>
        <div style={{
          display: 'flex', alignItems: 'center', gap: 10,
          padding: '8px 8px',
          borderRadius: 10,
        }}>
          <div style={{
            width: 30, height: 30, borderRadius: '50%',
            background: 'linear-gradient(135deg, #E55720, #8B5CF6)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: '0.68rem', fontWeight: 700, color: '#fff', flexShrink: 0,
          }}>
            {initials}
          </div>
          <div style={{ flex: 1, minWidth: 0 }}>
            <div style={{ fontSize: '0.78rem', fontWeight: 600, color: '#fff', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
              {user?.name || 'Amy Chen'}
            </div>
          </div>
          <button
            onClick={handleLogout}
            style={{
              background: 'none', border: 'none',
              color: 'rgba(255,255,255,0.3)', cursor: 'pointer',
              padding: 4, display: 'flex', alignItems: 'center',
            }}
          >
            <LogOut size={14} />
          </button>
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;
