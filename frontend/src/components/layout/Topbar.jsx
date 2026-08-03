import React, { useState, useRef, useEffect } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { Search, Bell, ChevronDown, User, LogOut, Settings, Sun, Moon } from 'lucide-react';

export const Topbar = ({ onToggleMenu }) => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const initials = user?.name?.split(' ').map(n => n[0]).join('').slice(0, 2).toUpperCase() || 'AC';

  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const [isDarkMode, setIsDarkMode] = useState(true);
  const userMenuRef = useRef(null);

  useEffect(() => {
    const handler = (e) => {
      if (userMenuRef.current && !userMenuRef.current.contains(e.target)) {
        setUserMenuOpen(false);
      }
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <header style={{
      height: 'var(--topbar-height)',
      background: 'rgba(9, 10, 12, 0.85)',
      backdropFilter: 'blur(16px)',
      WebkitBackdropFilter: 'blur(16px)',
      borderBottom: '1px solid var(--border)',
      display: 'flex',
      alignItems: 'center',
      padding: '0 32px',
      gap: 20,
    }}>
      {/* Search Input matching CoinSphere reference */}
      <div style={{ flex: 1, display: 'flex', alignItems: 'center' }}>
        <div style={{
          position: 'relative',
          width: '100%',
          maxWidth: 380,
        }}>
          <span style={{
            position: 'absolute',
            left: 14,
            top: '50%',
            transform: 'translateY(-50%)',
            color: 'rgba(255, 255, 255, 0.3)',
            display: 'flex',
            alignItems: 'center'
          }}>
            <Search size={16} />
          </span>
          <input
            type="text"
            placeholder="Search..."
            style={{
              width: '100%',
              background: 'rgba(255, 255, 255, 0.03)',
              border: '1px solid rgba(255, 255, 255, 0.06)',
              borderRadius: 'var(--radius-md)',
              padding: '10px 16px 10px 42px',
              fontSize: '0.85rem',
              color: '#fff',
              outline: 'none',
              transition: 'border-color 0.2s',
            }}
            onFocus={(e) => e.target.style.borderColor = 'rgba(255, 255, 255, 0.15)'}
            onBlur={(e) => e.target.style.borderColor = 'rgba(255, 255, 255, 0.06)'}
          />
        </div>
      </div>

      {/* Right side controls matching reference layout */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
        
        {/* Toggle dark/light switch */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          background: 'rgba(255, 255, 255, 0.04)',
          border: '1px solid rgba(255, 255, 255, 0.06)',
          borderRadius: 'var(--radius-full)',
          padding: 2,
          gap: 2
        }}>
          <button
            onClick={() => setIsDarkMode(true)}
            style={{
              background: isDarkMode ? '#fff' : 'transparent',
              color: isDarkMode ? '#111' : 'rgba(255,255,255,0.4)',
              border: 'none',
              borderRadius: '50%',
              width: 26,
              height: 26,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              cursor: 'pointer',
              transition: 'all 0.15s'
            }}
          >
            <Moon size={13} />
          </button>
          <button
            onClick={() => setIsDarkMode(false)}
            style={{
              background: !isDarkMode ? '#fff' : 'transparent',
              color: !isDarkMode ? '#111' : 'rgba(255,255,255,0.4)',
              border: 'none',
              borderRadius: '50%',
              width: 26,
              height: 26,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              cursor: 'pointer',
              transition: 'all 0.15s'
            }}
          >
            <Sun size={13} />
          </button>
        </div>

        {/* Bell Alert circle */}
        <button
          onClick={() => navigate('/notifications')}
          style={{
            width: 38,
            height: 38,
            borderRadius: '50%',
            background: 'transparent',
            border: '1px solid rgba(255, 255, 255, 0.08)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'rgba(255, 255, 255, 0.75)',
            cursor: 'pointer',
            position: 'relative'
          }}
        >
          <Bell size={16} />
          <span style={{
            position: 'absolute',
            top: 10,
            right: 10,
            width: 4,
            height: 4,
            borderRadius: '50%',
            background: '#E55720',
          }} />
        </button>

        {/* User Avatar & Menu */}
        <div ref={userMenuRef} style={{ position: 'relative' }}>
          <button
            onClick={() => setUserMenuOpen(v => !v)}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 8,
              background: 'transparent',
              border: 'none',
              cursor: 'pointer',
            }}
          >
            <div style={{
              width: 38,
              height: 38,
              borderRadius: '50%',
              background: 'linear-gradient(135deg, var(--accent) 0%, var(--purple) 100%)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '0.8rem',
              fontWeight: 700,
              color: '#fff',
              border: '2px solid rgba(255, 255, 255, 0.1)'
            }}>{initials}</div>
          </button>

          {userMenuOpen && (
            <div style={{
              position: 'absolute',
              top: 'calc(100% + 8px)',
              right: 0,
              width: 200,
              background: 'var(--bg-surface-2)',
              border: '1px solid var(--border-strong)',
              borderRadius: 'var(--radius-md)',
              boxShadow: 'var(--shadow-lg)',
              overflow: 'hidden',
              zIndex: 200,
            }}>
              <div style={{ padding: '12px 14px', borderBottom: '1px solid var(--border)' }}>
                <div style={{ fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-primary)' }}>{user?.name || 'Amy Chen'}</div>
                <div style={{ fontSize: '0.73rem', color: 'var(--text-muted)', marginTop: 2 }}>{user?.email || 'a.chen@secureflow.corp'}</div>
              </div>
              {[
                { icon: User, label: 'Profile', path: '/profile' },
                { icon: Settings, label: 'Settings', path: '/settings' },
              ].map(({ icon: Icon, label, path }) => (
                <NavLink
                  key={path}
                  to={path}
                  onClick={() => setUserMenuOpen(false)}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 10,
                    padding: '10px 14px',
                    fontSize: '0.82rem',
                    color: 'var(--text-secondary)',
                    textDecoration: 'none'
                  }}
                >
                  <Icon size={14} />{label}
                </NavLink>
              ))}
              <div style={{ borderTop: '1px solid var(--border)' }}>
                <button
                  onClick={handleLogout}
                  style={{
                    width: '100%',
                    display: 'flex',
                    alignItems: 'center',
                    gap: 10,
                    padding: '10px 14px',
                    background: 'none',
                    border: 'none',
                    color: 'var(--danger-light)',
                    fontSize: '0.82rem',
                    cursor: 'pointer',
                    fontFamily: 'var(--font-sans)',
                  }}
                >
                  <LogOut size={14} /> Sign Out
                </button>
              </div>
            </div>
          )}
        </div>

      </div>
    </header>
  );
};

export default Topbar;
