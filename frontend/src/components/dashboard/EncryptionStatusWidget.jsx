import React, { useEffect, useState } from 'react';
import { ENCRYPTION_STATS } from '../../utils/mockData';
import { Lock, Clock, CheckCircle } from 'lucide-react';
import { formatRelativeTime } from '../../utils/formatters';

export const EncryptionStatusWidget = () => {
  const { encrypted, unencrypted, total, lastEncrypted, algorithm, autoEncryptOn } = ENCRYPTION_STATS;
  const pct = Math.round((encrypted / total) * 100);
  const [w, setW] = useState(0);

  useEffect(() => {
    setW(pct);
  }, [pct]);

  return (
    <div className="encryption-widget">
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: 16 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <div style={{
            width: 32,
            height: 32,
            borderRadius: 'var(--radius-md)',
            background: 'var(--purple-dim)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'var(--purple-light)',
          }}>
            <Lock size={15} />
          </div>
          <div className="chart-title">Encryption</div>
        </div>
        <span style={{
          fontSize: '0.65rem',
          fontWeight: 750,
          padding: '2px 6px',
          borderRadius: 'var(--radius-full)',
          background: 'var(--purple-dim)',
          color: 'var(--purple-light)',
          fontFamily: 'var(--font-mono)',
        }}>
          {algorithm}
        </span>
      </div>

      <div style={{ display: 'flex', alignItems: 'baseline', gap: 6, marginBottom: 4 }}>
        <span style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--text-primary)', letterSpacing: '-0.02em' }}>{pct}%</span>
        <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>encrypted</span>
      </div>

      <div className="enc-bar-track">
        <div className="enc-bar-fill" style={{ width: `${w}%`, transition: 'width 0.8s ease-out' }} />
      </div>

      <div style={{ display: 'flex', justifyContent: 'space-between', margin: '14px 0' }}>
        <div>
          <div style={{ fontSize: '0.9rem', fontWeight: 700 }}>{encrypted}</div>
          <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>Protected</div>
        </div>
        <div>
          <div style={{ fontSize: '0.9rem', fontWeight: 700 }}>{unencrypted}</div>
          <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>Queue</div>
        </div>
        <div>
          <div style={{ fontSize: '0.9rem', fontWeight: 700 }}>{total}</div>
          <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>Total</div>
        </div>
      </div>

      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: 6,
        padding: '6px 10px',
        background: 'var(--bg-surface-2)',
        borderRadius: 'var(--radius-md)',
        fontSize: '0.7rem',
        color: 'var(--text-muted)'
      }}>
        <Clock size={11} />
        <span>Sync {formatRelativeTime(lastEncrypted)}</span>
        {autoEncryptOn && (
          <span style={{ marginLeft: 'auto', color: 'var(--success-light)', display: 'flex', alignItems: 'center', gap: 2 }}>
            <CheckCircle size={10} /> Auto
          </span>
        )}
      </div>
    </div>
  );
};

export default EncryptionStatusWidget;
