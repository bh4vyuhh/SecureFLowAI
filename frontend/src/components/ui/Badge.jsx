import React from 'react';

export const Badge = ({ variant = 'default', children, dot = false }) => {
  const styles = {
    default: { background: 'var(--bg-surface-2)', color: 'var(--text-secondary)', border: '1px solid var(--border)' },
    success: { background: 'var(--success-dim)', color: 'var(--success-light)', border: '1px solid var(--success-border)' },
    info: { background: 'var(--blue-ai-dim)', color: 'var(--blue-ai-light)', border: '1px solid var(--blue-ai-border)' },
    warning: { background: 'var(--warning-dim)', color: 'var(--warning-light)', border: '1px solid var(--warning-border)' },
    danger: { background: 'var(--danger-dim)', color: 'var(--danger-light)', border: '1px solid var(--danger-border)' },
  };

  const current = styles[variant] || styles.default;

  return (
    <span style={{
      display: 'inline-flex',
      alignItems: 'center',
      gap: '6px',
      padding: '3px 8px',
      borderRadius: 'var(--radius-full)',
      fontSize: '0.72rem',
      fontWeight: 600,
      background: current.background,
      color: current.color,
      border: current.border,
      whiteSpace: 'nowrap'
    }}>
      {dot && (
        <span style={{
          width: 6,
          height: 6,
          borderRadius: '50%',
          background: 'currentColor'
        }} />
      )}
      {children}
    </span>
  );
};

export const ClassBadge = ({ label }) => {
  const map = {
    'Public': 'success',
    'Internal': 'info',
    'Confidential': 'warning',
    'Highly Confidential': 'danger'
  };
  return <Badge variant={map[label] || 'default'} dot>{label}</Badge>;
};

export const SeverityBadge = ({ severity }) => {
  const map = { high: 'danger', medium: 'warning', low: 'success' };
  return <Badge variant={map[severity] || 'default'}>{severity}</Badge>;
};

export default Badge;
