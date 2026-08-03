import React, { useState } from 'react';
import { ClassBadge } from '../ui/Badge';
import { getRiskColor, formatRelativeTime } from '../../utils/formatters';
import { FileText, FileSpreadsheet, File, Image, Eye, Lock, Trash2, ChevronRight } from 'lucide-react';

const EXT_ICONS = {
  pdf:  { Icon: FileText,       color: '#EF4444' },
  docx: { Icon: FileText,       color: '#3B82F6' },
  xlsx: { Icon: FileSpreadsheet, color: '#22C55E' },
  csv:  { Icon: FileSpreadsheet, color: '#22C55E' },
  json: { Icon: File,           color: '#F59E0B' },
  png:  { Icon: Image,          color: '#A855F7' },
  jpg:  { Icon: Image,          color: '#A855F7' },
};

export const RecentDocuments = ({ documents = [], onAction }) => {
  return (
    <div className="recent-docs-section">
      <div style={{ display: 'flex', alignItems: 'center', justifycontent: 'space-between', marginBottom: 16 }}>
        <div>
          <div className="chart-title">Recent Documents</div>
          <div className="chart-subtitle">Latest uploads · hover to reveal actions</div>
        </div>
      </div>

      <div className="doc-cards-scroll">
        {documents.map(doc => {
          const ext = doc.name ? doc.name.split('.').pop().toLowerCase() : 'pdf';
          const def = EXT_ICONS[ext] || { Icon: File, color: 'var(--text-muted)' };
          const { Icon, color } = def;
          const riskColor = getRiskColor(doc.riskScore);

          return (
            <div key={doc.id} className="doc-card">
              <div style={{
                width: 40,
                height: 40,
                borderRadius: 'var(--radius-md)',
                background: `${color}18`,
                border: `1px solid ${color}30`,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                marginBottom: 12,
                color,
              }}>
                <Icon size={20} />
              </div>

              <div
                className="truncate"
                style={{
                  fontSize: '0.78rem',
                  fontWeight: 600,
                  color: 'var(--text-primary)',
                  marginBottom: 6,
                }}
                title={doc.name}
              >
                {doc.name}
              </div>

              <div style={{ marginBottom: 8 }}>
                <ClassBadge label={doc.label} />
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: 5, marginBottom: 4 }}>
                <span style={{
                  width: 7,
                  height: 7,
                  borderRadius: '50%',
                  background: riskColor,
                  display: 'inline-block',
                }} />
                <span style={{ fontSize: '0.73rem', fontWeight: 600, color: riskColor, fontFamily: 'var(--font-mono)' }}>
                  {doc.riskScore}
                </span>
                <span style={{ fontSize: '0.68rem', color: 'var(--text-muted)' }}>risk</span>
              </div>

              <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)' }}>
                {doc.size || '1.2 MB'} · {formatRelativeTime(doc.uploadedAt)}
              </div>

              <div className="doc-card-actions">
                <button className="doc-action-btn" onClick={() => onAction && onAction('view', doc)}>
                  View
                </button>
                {doc.label !== 'Public' && (
                  <button className="doc-action-btn" onClick={() => onAction && onAction('encrypt', doc)}>
                    Encrypt
                  </button>
                )}
                {doc.label !== 'Public' && (
                  <button className="doc-action-btn" onClick={() => onAction && onAction('mask', doc)}>
                    Mask
                  </button>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default RecentDocuments;
