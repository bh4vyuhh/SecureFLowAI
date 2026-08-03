import React, { useState } from 'react';
import { ALERTS } from '../../utils/mockData';
import { formatRelativeTime } from '../../utils/formatters';
import { Bell, ChevronRight, Check } from 'lucide-react';
import { NavLink } from 'react-router-dom';

export const RecentAlertsWidget = () => {
  const [resolved, setResolvedLocal] = useState([]);

  const recent = ALERTS
    .filter(a => !a.resolved)
    .slice(0, 6);

  return (
    <div className="alerts-widget">
      <div className="activity-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <div style={{
            width: 28,
            height: 28,
            borderRadius: 'var(--radius-sm)',
            background: 'var(--danger-dim)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'var(--danger-light)',
          }}>
            <Bell size={14} />
          </div>
          <div>
            <div className="chart-title">Recent Alerts</div>
          </div>
          <span style={{
            fontSize: '0.68rem',
            fontWeight: 700,
            padding: '2px 8px',
            borderRadius: 'var(--radius-full)',
            background: 'var(--danger-dim)',
            color: 'var(--danger-light)',
            border: '1px solid var(--danger-border)',
          }}>{recent.length} active</span>
        </div>
        <NavLink to="/notifications" style={{ display: 'flex', alignItems: 'center', gap: 3 }} className="view-all-btn">
          View all <ChevronRight size={13} />
        </NavLink>
      </div>

      {recent.map(alert => {
        const isResolved = resolved.includes(alert.id);
        return (
          <div
            key={alert.id}
            className="alert-row"
            style={{ opacity: isResolved ? 0.4 : 1, transition: 'opacity 300ms ease' }}
          >
            <span className={`alert-dot ${alert.severity}`} />
            <div style={{ flex: 1, minWidth: 0 }}>
              <div className="alert-title" style={{
                textDecoration: isResolved ? 'line-through' : 'none',
                color: isResolved ? 'var(--text-muted)' : 'var(--text-primary)',
              }}>
                {alert.title}
              </div>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: 2, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                {alert.user} · {alert.fileName}
              </div>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: 4, flexShrink: 0 }}>
              <span className="alert-time">{formatRelativeTime(alert.timestamp)}</span>
              {!isResolved && (
                <button
                  onClick={() => setResolvedLocal(r => [...r, alert.id])}
                  style={{
                    background: 'var(--success-dim)',
                    border: '1px solid var(--success-border)',
                    borderRadius: 'var(--radius-sm)',
                    color: 'var(--success-light)',
                    fontSize: '0.68rem',
                    fontWeight: 600,
                    padding: '2px 7px',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: 3,
                    fontFamily: 'var(--font-sans)',
                  }}
                >
                  <Check size={10} /> Resolve
                </button>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default RecentAlertsWidget;
