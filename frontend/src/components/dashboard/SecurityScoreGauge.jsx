import React, { useEffect, useState } from 'react';
import { SECURITY_SCORE } from '../../utils/mockData';
import { getRiskLabel } from '../../utils/formatters';
import { TrendingUp } from 'lucide-react';

function describeArc(cx, cy, r, startAngle, endAngle) {
  const start = polarToCartesian(cx, cy, r, endAngle);
  const end   = polarToCartesian(cx, cy, r, startAngle);
  return `M ${start.x} ${start.y} A ${r} ${r} 0 1 0 ${end.x} ${end.y}`;
}
function polarToCartesian(cx, cy, r, angle) {
  const rad = (angle * Math.PI) / 180;
  return { x: cx + r * Math.cos(rad), y: cy + r * Math.sin(rad) };
}

export const SecurityScoreGauge = () => {
  const { score, trend, trendUp, breakdown } = SECURITY_SCORE;
  const [displayed, setDisplayed] = useState(0);

  useEffect(() => {
    let start = Date.now();
    const duration = 1000;
    const step = () => {
      const elapsed = Date.now() - start;
      const progress = Math.min(elapsed / duration, 1);
      setDisplayed(Math.round(score * progress));
      if (progress < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  }, [score]);

  const size = 160;
  const radius = (size - 24) / 2;
  const circumference = Math.PI * radius;
  const color = score >= 80 ? 'var(--success)' : score >= 60 ? 'var(--warning)' : 'var(--danger)';
  const offset = circumference - (displayed / 100) * circumference;

  return (
    <div className="security-score-widget">
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', width: '100%', marginBottom: 12 }}>
        <div>
          <div className="chart-title">Security Score</div>
          <div className="chart-subtitle">Overall posture</div>
        </div>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: 4,
          fontSize: '0.72rem',
          fontWeight: 600,
          padding: '2px 8px',
          borderRadius: 'var(--radius-full)',
          background: trendUp ? 'var(--success-dim)' : 'var(--danger-dim)',
          color: trendUp ? 'var(--success-light)' : 'var(--danger-light)',
        }}>
          <TrendingUp size={11} />
          {trend}
        </div>
      </div>

      <svg width={size} height={size / 2 + 20} style={{ overflow: 'visible' }}>
        <path
          d={describeArc(size / 2, size / 2, radius, -180, 0)}
          fill="none"
          stroke="var(--border)"
          strokeWidth={12}
          strokeLinecap="round"
        />
        <path
          d={describeArc(size / 2, size / 2, radius, -180, 0)}
          fill="none"
          stroke={color}
          strokeWidth={12}
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          style={{
            transition: 'stroke-dashoffset 0.8s ease-out',
          }}
        />
        <text x={size / 2} y={size / 2 + 2} textAnchor="middle" fill="var(--text-primary)" fontSize={32} fontWeight="800">
          {displayed}
        </text>
        <text x={size / 2} y={size / 2 + 18} textAnchor="middle" fill={color} fontSize={11} fontWeight="700" letterSpacing="0.05em">
          {getRiskLabel(100 - score).toUpperCase()}
        </text>
      </svg>

      <div style={{ width: '100%', display: 'flex', flexDirection: 'column', gap: 6, marginTop: 14 }}>
        {breakdown.map(item => (
          <div key={item.label}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 2 }}>
              <span style={{ fontSize: '0.72rem', color: 'var(--text-secondary)' }}>{item.label}</span>
              <span style={{ fontSize: '0.72rem', fontWeight: 600, color: 'var(--text-primary)', fontFamily: 'var(--font-mono)' }}>
                {item.value}%
              </span>
            </div>
            <div style={{ height: 4, background: 'var(--bg-surface-3)', borderRadius: 'var(--radius-full)', overflow: 'hidden' }}>
              <div style={{
                height: '100%',
                width: `${item.value}%`,
                background: item.value >= 80 ? 'var(--success)' : item.value >= 60 ? 'var(--warning)' : 'var(--danger)',
                transition: 'width 0.8s ease-out',
              }} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default SecurityScoreGauge;
