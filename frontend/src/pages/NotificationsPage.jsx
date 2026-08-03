import React from 'react';
import AppLayout from '../components/layout/AppLayout';

export const NotificationsPage = () => {
  return (
    <AppLayout>
      <div className="page-content" style={{ maxWidth: 800 }}>
        <div className="page-header">
          <h2 className="page-title">Notifications &amp; Alerts</h2>
          <p className="page-subtitle">Historical log of active warnings and alerts</p>
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          <div style={{
            background: 'var(--bg-surface)',
            border: '1px solid var(--danger-border)',
            borderRadius: 'var(--radius-lg)',
            padding: 16
          }}>
            <div style={{ fontWeight: 600, color: 'var(--danger-light)' }}>High Risk Alert - Ingestion Gateway</div>
            <div style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', marginTop: 4 }}>
              Employee_Records_2024.xlsx contains clear SSN matching patterns (Score: 91). Auto-encryption triggered.
            </div>
          </div>
          <div style={{
            background: 'var(--bg-surface)',
            border: '1px solid var(--warning-border)',
            borderRadius: 'var(--radius-lg)',
            padding: 16
          }}>
            <div style={{ fontWeight: 600, color: 'var(--warning-light)' }}>Medium Risk Warning - Browser Extension</div>
            <div style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', marginTop: 4 }}>
              Bulk clipboard text paste containing sensitive credit card patterns detected on form fields.
            </div>
          </div>
        </div>
      </div>
    </AppLayout>
  );
};

export default NotificationsPage;
