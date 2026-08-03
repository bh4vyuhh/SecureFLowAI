import React from 'react';
import { AUDIT_LOG } from '../../utils/mockData';
import { formatRelativeTime } from '../../utils/formatters';
import { NavLink } from 'react-router-dom';
import { ScrollText, Lock, Shield, CheckCircle, ChevronRight } from 'lucide-react';

const ACTION_MAP = {
  'Tier Match':  { icon: Shield,      bg: 'var(--blue-ai-dim)',   color: 'var(--blue-ai-light)' },
  'Crypto Lock': { icon: Lock,        bg: 'var(--purple-dim)',    color: 'var(--purple-light)'  },
  'Gateway Auth':{ icon: CheckCircle, bg: 'var(--success-dim)',   color: 'var(--success-light)' },
};

export const AuditTrailPreview = () => {
  const preview = AUDIT_LOG.slice(0, 6);

  return (
    <div className="audit-preview-widget">
      <div className="activity-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <div style={{
            width: 28,
            height: 28,
            borderRadius: 'var(--radius-sm)',
            background: 'var(--accent-dim)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'var(--accent-light)',
          }}>
            <ScrollText size={14} />
          </div>
          <div className="chart-title">Audit Trail</div>
        </div>
        <NavLink to="/audit-logs" className="view-all-btn" style={{ display: 'flex', alignItems: 'center', gap: 3 }}>
          Log <ChevronRight size={13} />
        </NavLink>
      </div>

      {preview.map(entry => {
        const def = ACTION_MAP[entry.action] || {
          icon: CheckCircle,
          bg: 'var(--bg-surface-2)',
          color: 'var(--text-muted)',
        };
        const Icon = def.icon;
        return (
          <div key={entry.id} className="audit-row">
            <div className="audit-action-icon" style={{ background: def.bg, color: def.color, display: 'flex', alignItems: 'center', justifyContent: 'center', borderRadius: 4 }}>
              <Icon size={12} />
            </div>

            <div style={{ minWidth: 0 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 2 }}>
                <span style={{ fontSize: '0.78rem', fontWeight: 600, color: 'var(--text-primary)' }}>{entry.action}</span>
                <span style={{
                  fontSize: '0.65rem',
                  padding: '1px 6px',
                  borderRadius: 'var(--radius-full)',
                  background: 'var(--success-dim)',
                  color: 'var(--success-light)',
                  border: '1px solid var(--success-border)',
                  fontWeight: 600,
                }}>
                  {entry.result}
                </span>
              </div>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                <span style={{ color: 'var(--text-secondary)' }}>{entry.actor}</span>
                {' · '}
                {entry.resource}
              </div>
            </div>

            <span style={{ fontSize: '0.68rem', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)', textAlign: 'right', alignSelf: 'center' }}>
              {formatRelativeTime(entry.timestamp)}
            </span>
          </div>
        );
      })}
    </div>
  );
};

export default AuditTrailPreview;
