import React, { useState } from 'react';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

export const StatCard = ({
  label, value, sub, delta, deltaType = 'neutral',
  icon: Icon, variant = 'accent', style: extraStyle = {},
}) => {
  const [hovered, setHovered] = useState(false);
  const DeltaIcon = deltaType === 'up' ? TrendingUp : deltaType === 'down' ? TrendingDown : Minus;

  const glowMap = {
    accent: 'rgba(124, 92, 252, 0.12)',
    danger: 'rgba(239, 68, 68, 0.1)',
    warning: 'rgba(245, 158, 11, 0.1)',
    success: 'rgba(34, 197, 94, 0.1)',
    purple: 'rgba(168, 85, 247, 0.1)',
    blue: 'rgba(59, 130, 246, 0.1)',
  };

  return (
    <div className={`stat-card ${variant} animate-fade-in`}>
      <div className="stat-card-top">
        {delta !== undefined && (
          <span className={`stat-delta ${deltaType}`}>
            {delta}
          </span>
        )}
      </div>
      <div>
        <div className="stat-value">{value}</div>
        <div className="stat-label">{label}</div>
        {sub && <div className="stat-sub">{sub}</div>}
      </div>
    </div>
  );
};

export default StatCard;
