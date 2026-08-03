import React, { useState } from 'react';
import { AI_RECOMMENDATIONS } from '../../utils/mockData';
import { ShieldAlert, Eye, Cpu, FileCheck, Brain, ChevronRight } from 'lucide-react';

const ICON_MAP = {
  'shield-alert': ShieldAlert,
  'eye': Eye,
  'cpu': Cpu,
  'file-check': FileCheck,
};

const SEVERITY_STYLE = {
  high: { bg: 'var(--danger-dim)', color: 'var(--danger-light)', border: 'var(--danger-border)', iconBg: 'var(--danger-dim)', iconColor: 'var(--danger-light)' },
  medium: { bg: 'var(--warning-dim)', color: 'var(--warning-light)', border: 'var(--warning-border)', iconBg: 'var(--warning-dim)', iconColor: 'var(--warning-light)' },
  low: { bg: 'var(--blue-ai-dim)', color: 'var(--blue-ai-light)', border: 'var(--blue-ai-border)', iconBg: 'var(--blue-ai-dim)', iconColor: 'var(--blue-ai-light)' },
};

export const AIRecommendationPanel = () => {
  const [dismissed, setDismissed] = useState([]);
  const visible = AI_RECOMMENDATIONS.filter(r => !dismissed.includes(r.id));

  return (
    <div className="ai-reco-panel">
      <div style={{
        padding: '16px 20px',
        borderBottom: '1px solid var(--border)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <div style={{
            width: 30,
            height: 30,
            borderRadius: 'var(--radius-md)',
            background: 'var(--blue-ai-dim)',
            border: '1px solid var(--blue-ai-border)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'var(--blue-ai-light)',
          }}>
            <Brain size={14} />
          </div>
          <div>
            <div className="chart-title">AI Recommendations</div>
            <div className="chart-subtitle">{visible.length} actions pending</div>
          </div>
        </div>
        <span className="ai-badge">
          <span className="ai-badge-dot" />
          AI Engine
        </span>
      </div>

      {visible.length === 0 ? (
        <div style={{ padding: '32px 20px', textAlign: 'center' }}>
          <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>All recommendations addressed</div>
        </div>
      ) : (
        visible.map(rec => {
          const Icon = ICON_MAP[rec.icon] || ShieldAlert;
          const s = SEVERITY_STYLE[rec.severity] || SEVERITY_STYLE.low;
          return (
            <div key={rec.id} className="ai-reco-item">
              <div className="ai-reco-icon" style={{ background: s.iconBg, color: s.iconColor }}>
                <Icon size={15} />
              </div>
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 7, marginBottom: 3 }}>
                  <span
                    style={{
                      fontSize: '0.65rem',
                      fontWeight: 700,
                      padding: '2px 6px',
                      borderRadius: 'var(--radius-full)',
                      background: s.bg,
                      color: s.color,
                      border: `1px solid ${s.border}`,
                      textTransform: 'capitalize',
                      letterSpacing: '0.04em',
                    }}
                  >
                    {rec.severity}
                  </span>
                </div>
                <div className="ai-reco-title">{rec.title}</div>
                <div className="ai-reco-desc">{rec.description}</div>
                <div style={{ display: 'flex', gap: 8, marginTop: 8 }}>
                  <button className="apply-fix-btn">
                    {rec.actionLabel} <ChevronRight size={11} style={{ display: 'inline', verticalAlign: 'middle' }} />
                  </button>
                  <button
                    className="apply-fix-btn"
                    onClick={() => setDismissed(d => [...d, rec.id])}
                    style={{ color: 'var(--text-muted)', borderColor: 'transparent' }}
                  >
                    Dismiss
                  </button>
                </div>
              </div>
            </div>
          );
        })
      )}
    </div>
  );
};

export default AIRecommendationPanel;
