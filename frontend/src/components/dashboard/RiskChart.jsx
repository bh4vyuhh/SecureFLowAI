import React, { useState } from 'react';
import {
  ResponsiveContainer, XAxis, YAxis, CartesianGrid,
  Tooltip, Area, AreaChart,
} from 'recharts';
import { RISK_TREND } from '../../utils/mockData';

const TIME_FILTERS = ['7D', '14D', '30D'];

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div style={{
      background: 'rgba(23, 24, 28, 0.95)',
      border: '1px solid var(--border-strong)',
      borderRadius: 'var(--radius-md)',
      padding: '10px 14px',
      fontSize: '0.78rem',
      boxShadow: 'var(--shadow-lg)',
      backdropFilter: 'blur(8px)'
    }}>
      <div style={{ color: 'var(--text-muted)', marginBottom: 6, fontSize: '0.75rem', fontWeight: 600 }}>{label}</div>
      {payload.map(p => (
        <div key={p.name} style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 2 }}>
          <span style={{ width: 6, height: 6, borderRadius: '50%', background: p.color }} />
          <span style={{ color: 'var(--text-secondary)' }}>{p.name}:</span>
          <strong style={{ color: 'var(--text-primary)' }}>{p.value}</strong>
        </div>
      ))}
    </div>
  );
};

export const RiskChart = () => {
  const [activeFilter, setActiveFilter] = useState('14D');

  const data = activeFilter === '7D'
    ? RISK_TREND.slice(-7)
    : activeFilter === '30D'
      ? [...RISK_TREND, ...RISK_TREND.slice(0, 16)]
      : RISK_TREND;

  return (
    <div className="chart-card">
      <div className="chart-header">
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
            <div className="chart-title">AI Risk Timeline</div>
            <span className="ai-badge">
              <span className="ai-badge-dot" />
              Live
            </span>
          </div>
          <div className="chart-subtitle">Average risk score &amp; high-risk event volume over time</div>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
          <div className="chart-legend">
            <div className="chart-legend-item">
              <div className="chart-legend-dot" style={{ background: '#7C5CFC' }} />
              Avg Risk
            </div>
            <div className="chart-legend-item">
              <div className="chart-legend-dot" style={{ background: '#EF4444' }} />
              High Risk
            </div>
          </div>
          <div className="time-filter-pills">
            {TIME_FILTERS.map(f => (
              <button
                key={f}
                className={`time-pill ${activeFilter === f ? 'active' : ''}`}
                onClick={() => setActiveFilter(f)}
              >
                {f}
              </button>
            ))}
          </div>
        </div>
      </div>

      <ResponsiveContainer width="100%" height={260}>
        <AreaChart data={data} margin={{ top: 8, right: 4, left: -20, bottom: 0 }}>
          <defs>
            <pattern id="diagonalStripes" width="10" height="10" patternTransform="rotate(45 0 0)" patternUnits="userSpaceOnUse">
              <line x1="0" y1="0" x2="0" y2="10" stroke="rgba(124, 92, 252, 0.08)" strokeWidth="2.5" />
            </pattern>
            <pattern id="diagonalStripesDanger" width="10" height="10" patternTransform="rotate(45 0 0)" patternUnits="userSpaceOnUse">
              <line x1="0" y1="0" x2="0" y2="10" stroke="rgba(239, 68, 68, 0.06)" strokeWidth="2" />
            </pattern>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.03)" vertical={false} />
          <XAxis
            dataKey="date"
            tick={{ fill: 'var(--text-muted)', fontSize: 10, fontFamily: 'var(--font-sans)' }}
            axisLine={false}
            tickLine={false}
          />
          <YAxis
            tick={{ fill: 'var(--text-muted)', fontSize: 10, fontFamily: 'var(--font-sans)' }}
            axisLine={false}
            tickLine={false}
          />
          <Tooltip content={<CustomTooltip />} />
          <Area
            type="monotone"
            dataKey="avgRisk"
            name="Avg Risk"
            stroke="#7C5CFC"
            strokeWidth={3}
            fill="url(#diagonalStripes)"
            dot={false}
            activeDot={{ r: 4, fill: '#7C5CFC', stroke: '#0B0B0D', strokeWidth: 2 }}
          />
          <Area
            type="monotone"
            dataKey="highRiskCount"
            name="High Risk"
            stroke="#EF4444"
            strokeWidth={2}
            fill="url(#diagonalStripesDanger)"
            dot={false}
            activeDot={{ r: 4, fill: '#EF4444', stroke: '#0B0B0D', strokeWidth: 2 }}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
};

export default RiskChart;
