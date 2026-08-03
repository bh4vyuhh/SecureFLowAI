import React from 'react';
import { useToast } from '../../contexts/ToastContext';
import { X, CheckCircle, AlertTriangle, AlertOctagon, Info } from 'lucide-react';

export const Toast = ({ id, type, title, message }) => {
  const { toasts } = useToast();
  
  const icons = {
    success: <CheckCircle size={16} color="var(--success)" />,
    warning: <AlertTriangle size={16} color="var(--warning)" />,
    danger: <AlertOctagon size={16} color="var(--danger)" />,
    info: <Info size={16} color="var(--blue-ai)" />,
  };

  const borderColors = {
    success: 'var(--success-border)',
    warning: 'var(--warning-border)',
    danger: 'var(--danger-border)',
    info: 'var(--blue-ai-border)',
  };

  return (
    <div style={{
      display: 'flex',
      alignItems: 'flex-start',
      gap: 12,
      background: 'var(--bg-surface)',
      border: `1px solid ${borderColors[type] || 'var(--border)'}`,
      borderRadius: 'var(--radius-md)',
      padding: '14px 18px',
      boxShadow: 'var(--shadow-lg)',
      width: 320,
      pointerEvents: 'auto',
      animation: 'fadeInUp var(--duration-base) ease-out both'
    }}>
      <div style={{ marginTop: 2 }}>{icons[type]}</div>
      <div style={{ flex: 1 }}>
        <div style={{ fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-primary)' }}>{title}</div>
        <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: 2 }}>{message}</div>
      </div>
    </div>
  );
};

export const ToastContainer = () => {
  const { toasts } = useToast();

  return (
    <div style={{
      position: 'fixed',
      bottom: 24,
      right: 24,
      zIndex: 9999,
      display: 'flex',
      flexDirection: 'column',
      gap: 10,
      pointerEvents: 'none'
    }}>
      {toasts.map((t) => (
        <Toast key={t.id} {...t} />
      ))}
    </div>
  );
};

export default ToastContainer;
