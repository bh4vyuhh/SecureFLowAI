import React, { useState } from 'react';
import { ANOMALY_EVENTS } from '../../utils/mockData';
import { ShieldAlert, AlertTriangle, ShieldCheck } from 'lucide-react';

export const AnomalyTimeline = () => {
  const [hovered, setHovered] = useState(null);

  const getSeverityConfig = (sev) => {
    switch (sev) {
      case 'high':
        return { color: 'var(--danger)', bg: 'rgba(239, 68, 68, 0.15)', icon: ShieldAlert, label: 'Critical' };
      case 'medium':
        return { color: 'var(--warning)', bg: 'rgba(245, 158, 11, 0.15)', icon: AlertTriangle, label: 'Medium' };
      default:
        return { color: 'var(--success)', bg: 'rgba(34, 197, 94, 0.15)', icon: ShieldCheck, label: 'Safe' };
    }
  };

  return (
    <div className="anomaly-section">
      <div className="chart-header">
        <div>
          <div className="chart-title">System Anomalies &amp; Events</div>
          <div className="chart-subtitle">Event severity distribution timeline</div>
        </div>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 14, padding: '10px 0' }}>
        {['high', 'medium', 'low'].map(sev => {
          const cfg = getSeverityConfig(sev);
          const Icon = cfg.icon;
          const filtered = ANOMALY_EVENTS.filter(e => e.severity === sev);

          return (
            <div key={sev} style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
              <div style={{
                width: 80,
                display: 'flex',
                alignItems: 'center',
                gap: 6,
                fontSize: '0.75rem',
                fontWeight: 600,
                color: cfg.color
              }}>
                <Icon size={12} />
                {cfg.label}
              </div>

              <div style={{
                flex: 1,
                height: 36,
                background: 'var(--bg-surface-2)',
                borderRadius: 'var(--radius-md)',
                position: 'relative',
                border: '1px solid var(--border)',
                overflow: 'visible'
              }}>
                {filtered.map(ev => (
                  <div
                    key={ev.id}
                    className="timeline-event"
                    style={{
                      left: `${ev.dayOffset * 90 + 5}%`,
                      top: '50%',
                      transform: 'translate(-50%, -50%)',
                      position: 'absolute',
                      zIndex: hovered === ev.id ? 10 : 2
                    }}
                    onMouseEnter={() => setHovered(ev.id)}
                    onMouseLeave={() => setHovered(null)}
                  >
                    <div
                      className={`timeline-dot ${ev.severity}`}
                      style={{
                        width: 14,
                        height: 14,
                        borderRadius: '50%',
                        background: cfg.color,
                        boxShadow: `0 0 10px ${cfg.color}`,
                        border: '2px solid var(--bg-surface-2)',
                        transition: 'transform 0.2s ease',
                        transform: hovered === ev.id ? 'scale(1.3)' : 'scale(1)'
                      }}
                    />
                    {hovered === ev.id && (
                      <div className="timeline-label" style={{ opacity: 1, bottom: 'calc(100% + 8px)' }}>
                        <div style={{ fontWeight: 600, color: 'var(--text-primary)', marginBottom: 2 }}>{ev.label}</div>
                        <div style={{ color: 'var(--text-muted)', fontSize: '0.65rem' }}>Severity: {ev.severity.toUpperCase()}</div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default AnomalyTimeline;
