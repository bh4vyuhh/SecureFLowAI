import React from 'react';
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from 'recharts';
import { CLASSIFICATION_DIST } from '../../utils/mockData';

const CustomLabel = ({ cx, cy, midAngle, innerRadius, outerRadius, percent }) => {
  if (percent < 0.06) return null;
  const r = innerRadius + (outerRadius - innerRadius) * 0.5;
  const rad = (midAngle * Math.PI) / 180;
  const x = cx + r * Math.cos(-rad);
  const y = cy + r * Math.sin(-rad);
  return (
    <text x={x} y={y} fill="#fff" textAnchor="middle" dominantBaseline="central" fontSize={11} fontWeight={600}>
      {`${(percent * 100).toFixed(0)}%`}
    </text>
  );
};

export const ClassificationDonut = () => {
  const total = CLASSIFICATION_DIST.reduce((s, d) => s + d.value, 0);

  return (
    <div className="chart-card" style={{ display: 'flex', flexDirection: 'column' }}>
      <div className="chart-header">
        <div>
          <div className="chart-title">Classification Breakdown</div>
          <div className="chart-subtitle">Total monitored assets</div>
        </div>
      </div>
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        <ResponsiveContainer width="100%" height={180}>
          <PieChart>
            <Pie
              data={CLASSIFICATION_DIST}
              cx="50%"
              cy="50%"
              innerRadius={55}
              outerRadius={80}
              paddingAngle={4}
              dataKey="value"
              labelLine={false}
              label={<CustomLabel />}
              animationBegin={0}
              animationDuration={900}
            >
              {CLASSIFICATION_DIST.map((entry, i) => (
                <Cell key={i} fill={entry.fill} stroke="var(--bg-surface)" strokeWidth={2} />
              ))}
            </Pie>
            <Tooltip
              formatter={(v) => [`${v}%`]}
              contentStyle={{
                background: 'var(--bg-surface-2)',
                border: '1px solid var(--border-strong)',
                borderRadius: 'var(--radius-md)',
                fontSize: '0.8125rem',
              }}
            />
          </PieChart>
        </ResponsiveContainer>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10, width: '100%', padding: '10px 8px 0' }}>
          {CLASSIFICATION_DIST.map(d => (
            <div key={d.name} style={{
              display: 'flex',
              flexDirection: 'column',
              padding: '8px 12px',
              background: 'var(--bg-surface-2)',
              border: '1px solid var(--border)',
              borderRadius: 'var(--radius-md)',
              gap: 4
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                <div style={{ width: 8, height: 8, borderRadius: '50%', background: d.fill, flexShrink: 0 }} />
                <span style={{ fontSize: '0.73rem', color: 'var(--text-muted)', fontWeight: 500 }}>{d.name}</span>
              </div>
              <span style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-primary)', fontFamily: 'var(--font-mono)' }}>
                {d.value}%
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default ClassificationDonut;
