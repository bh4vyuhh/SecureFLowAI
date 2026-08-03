import React, { useState } from 'react';
import { ClassBadge } from '../ui/Badge';
import { getRiskColor, formatRelativeTime, getFileExtension } from '../../utils/formatters';
import { FileText, File, FileSpreadsheet, Image, ChevronRight } from 'lucide-react';

const FILE_ICONS = {
  pdf: { Icon: FileText, color: '#EF4444' },
  docx: { Icon: FileText, color: '#3B82F6' },
  xlsx: { Icon: FileSpreadsheet, color: '#22C55E' },
  csv: { Icon: FileSpreadsheet, color: '#22C55E' },
  png: { Icon: Image, color: '#A855F7' },
  jpg: { Icon: Image, color: '#A855F7' },
};

const getFileIcon = (name) => {
  const ext = getFileExtension(name);
  return FILE_ICONS[ext] || { Icon: File, color: 'var(--text-muted)' };
};

export const ActivityFeed = ({ events = [], limit = 10 }) => {
  const [showAll, setShowAll] = useState(false);
  const displayed = showAll ? events : events.slice(0, limit);

  return (
    <div className="activity-section">
      <div className="activity-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <span className="chart-title">Live Classification Feed</span>
          <span className="live-badge">
            Live
          </span>
        </div>
        <button className="view-all-btn" onClick={() => setShowAll(v => !v)}>
          {showAll ? 'Show less' : 'View all'} <ChevronRight size={14} />
        </button>
      </div>

      <div style={{ overflowX: 'auto' }}>
        <table className="activity-table">
          <thead>
            <tr>
              <th>File</th>
              <th>Classification</th>
              <th>Risk</th>
              <th>Source</th>
              <th>User</th>
              <th>Action</th>
              <th>Time</th>
            </tr>
          </thead>
          <tbody>
            {displayed.map((ev) => {
              const { Icon, color } = getFileIcon(ev.fileName);
              return (
                <tr key={ev.id}>
                  <td>
                    <div className="activity-file">
                      <div className="activity-file-icon" style={{ color }}>
                        <Icon size={15} />
                      </div>
                      <span className="truncate" style={{ maxWidth: 180 }} title={ev.fileName}>
                        {ev.fileName}
                      </span>
                    </div>
                  </td>
                  <td><ClassBadge label={ev.label} /></td>
                  <td>
                    <span className="risk-score" style={{ color: getRiskColor(ev.riskScore) }}>
                      {ev.riskScore}
                    </span>
                  </td>
                  <td>{ev.source}</td>
                  <td>{ev.user}</td>
                  <td>
                    <span style={{
                      fontSize: '0.75rem', fontWeight: 600, padding: '2px 8px',
                      background: 'var(--bg-surface-2)', border: '1px solid var(--border)',
                      borderRadius: 'var(--radius-full)', color: 'var(--text-secondary)',
                      textTransform: 'capitalize',
                    }}>
                      {ev.action}
                    </span>
                  </td>
                  <td style={{ color: 'var(--text-muted)', whiteSpace: 'nowrap' }}>
                    {formatRelativeTime(ev.timestamp)}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default ActivityFeed;
