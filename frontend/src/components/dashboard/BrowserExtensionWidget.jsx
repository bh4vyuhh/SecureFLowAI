import React from 'react';
import { BROWSER_EXT_STATS } from '../../utils/mockData';
import { Puzzle, Users, Clipboard, ShieldOff, Clock } from 'lucide-react';
import { formatRelativeTime } from '../../utils/formatters';

export const BrowserExtensionWidget = () => {
  const { status, activeUsers, clipboardIntercepts, blockedUploads, lastEventAt, version } = BROWSER_EXT_STATS;
  const connected = status === 'connected';

  const stats = [
    { icon: Users, label: 'Monitored Users', value: activeUsers, color: 'var(--blue-ai-light)' },
    { icon: Clipboard, label: 'Clipboard Checks', value: clipboardIntercepts, color: 'var(--warning)' },
    { icon: ShieldOff, label: 'Blocked Uploads', value: blockedUploads, color: 'var(--danger-light)' },
  ];

  return (
    <div className="browser-ext-widget">
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <div style={{
            width: 32,
            height: 32,
            borderRadius: 'var(--radius-md)',
            background: connected ? 'var(--success-dim)' : 'var(--danger-dim)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: connected ? 'var(--success-light)' : 'var(--danger-light)',
          }}>
            <Puzzle size={15} />
          </div>
          <div>
            <div className="chart-title">Browser Ext</div>
            <div className="chart-subtitle">v{version}</div>
          </div>
        </div>
        <span className={`ext-status-badge ${connected ? 'connected' : 'disconnected'}`}>
          <span style={{
            width: 6,
            height: 6,
            borderRadius: '50%',
            background: connected ? 'var(--success)' : 'var(--danger)',
          }} />
          {connected ? 'Active' : 'Offline'}
        </span>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column' }}>
        {stats.map(({ icon: Icon, label, value, color }) => (
          <div key={label} className="ext-stat-row">
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <Icon size={12} color={color} />
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{label}</span>
            </div>
            <span style={{ fontSize: '0.85rem', fontWeight: 700, color, fontFamily: 'var(--font-mono)' }}>{value}</span>
          </div>
        ))}
      </div>

      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: 6,
        marginTop: 14,
        padding: '6px 10px',
        background: 'var(--bg-surface-2)',
        borderRadius: 'var(--radius-md)',
        fontSize: '0.7rem',
        color: 'var(--text-muted)'
      }}>
        <Clock size={11} />
        <span>Last event {formatRelativeTime(lastEventAt)}</span>
      </div>
    </div>
  );
};

export default BrowserExtensionWidget;
