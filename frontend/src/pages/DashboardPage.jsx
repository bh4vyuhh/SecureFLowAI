import React from 'react';
import {
  ResponsiveContainer, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip,
  PieChart, Pie, Cell
} from 'recharts';
import {
  FileText, Lock, ShieldAlert, Cpu, Bell, TrendingUp, TrendingDown,
  ArrowUpRight, ChevronRight, Upload, Clock, CheckCircle, AlertTriangle,
  Shield, Eye, Zap
} from 'lucide-react';
import AppLayout from '../components/layout/AppLayout';
import '../styles/dashboard.css';

const riskTrendData = [
  { date: 'Jul 20', score: 32, events: 4 },
  { date: 'Jul 21', score: 28, events: 2 },
  { date: 'Jul 22', score: 45, events: 7 },
  { date: 'Jul 23', score: 38, events: 5 },
  { date: 'Jul 24', score: 52, events: 8 },
  { date: 'Jul 25', score: 41, events: 3 },
  { date: 'Jul 26', score: 55, events: 9 },
  { date: 'Jul 27', score: 48, events: 6 },
  { date: 'Jul 28', score: 62, events: 11 },
  { date: 'Jul 29', score: 44, events: 5 },
  { date: 'Jul 30', score: 39, events: 4 },
  { date: 'Jul 31', score: 47, events: 6 },
  { date: 'Aug 01', score: 51, events: 7 },
  { date: 'Aug 02', score: 43, events: 5 },
];

const classificationData = [
  { name: 'Public', value: 142, color: '#10B981' },
  { name: 'Internal', value: 89, color: '#3B82F6' },
  { name: 'Confidential', value: 47, color: '#F59E0B' },
  { name: 'Highly Confidential', value: 18, color: '#EF4444' },
];

const recentActivity = [
  { id: 1, file: 'Q4_Financial_Report.pdf', user: 'm.vasquez', dept: 'Finance', label: 'Highly Confidential', risk: 91, action: 'Auto-encrypted', time: '4 min ago', status: 'critical' },
  { id: 2, file: 'employee_roster_2025.xlsx', user: 'a.patel', dept: 'HR', label: 'Confidential', risk: 73, action: 'PII masked', time: '12 min ago', status: 'warning' },
  { id: 3, file: 'product_roadmap_v3.docx', user: 's.obrien', dept: 'Engineering', label: 'Internal', risk: 34, action: 'Logged', time: '28 min ago', status: 'safe' },
  { id: 4, file: 'vendor_contract_NDA.pdf', user: 'j.hargreaves', dept: 'Legal', label: 'Confidential', risk: 68, action: 'Flagged for review', time: '41 min ago', status: 'warning' },
  { id: 5, file: 'press_release_draft.docx', user: 'k.tanaka', dept: 'Marketing', label: 'Public', risk: 12, action: 'Logged', time: '1h ago', status: 'safe' },
  { id: 6, file: 'api_credentials_staging.json', user: 's.obrien', dept: 'Engineering', label: 'Highly Confidential', risk: 88, action: 'Auto-encrypted', time: '1h ago', status: 'critical' },
];

const activeAlerts = [
  { id: 1, title: 'SSN pattern detected in uploaded spreadsheet', severity: 'critical', user: 'a.patel', time: '4 min ago' },
  { id: 2, title: 'Bulk download of confidential files detected', severity: 'critical', user: 'm.vasquez', time: '18 min ago' },
  { id: 3, title: 'Clipboard paste with API key on external form', severity: 'warning', user: 's.obrien', time: '32 min ago' },
  { id: 4, title: 'Off-hours access to restricted directory', severity: 'warning', user: 'e.dubois', time: '1h ago' },
];

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div style={{
      background: 'rgba(19, 20, 25, 0.95)',
      border: '1px solid rgba(255,255,255,0.08)',
      borderRadius: 10,
      padding: '10px 14px',
      fontSize: '0.78rem',
      backdropFilter: 'blur(8px)',
    }}>
      <div style={{ color: 'var(--text-muted)', marginBottom: 6, fontSize: '0.72rem', fontWeight: 600 }}>{label}</div>
      {payload.map(p => (
        <div key={p.name} style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 2 }}>
          <span style={{ width: 6, height: 6, borderRadius: '50%', background: p.color }} />
          <span style={{ color: 'var(--text-secondary)' }}>{p.name}:</span>
          <strong style={{ color: '#fff' }}>{p.value}</strong>
        </div>
      ))}
    </div>
  );
};

const StatCard = ({ label, value, sub, delta, deltaUp, icon: Icon, iconClass }) => (
  <div className="stat-card animate-fade-up">
    <div className="stat-card-top">

      {delta && (
        <span className={`stat-delta ${deltaUp ? 'up' : deltaUp === false ? 'down' : 'neutral'}`}>
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

const getLabelChip = (label) => {
  const map = {
    'Highly Confidential': 'critical',
    'Confidential': 'warning',
    'Internal': 'info',
    'Public': 'safe',
  };
  return <span className={`chip ${map[label] || 'info'}`}>{label}</span>;
};

export const DashboardPage = () => {
  const totalClassified = classificationData.reduce((s, c) => s + c.value, 0);

  return (
    <AppLayout>
      <div className="page-content">
        <div className="page-header" style={{ display: 'flex', alignItems: 'flex-end', justifyContent: 'space-between', flexWrap: 'wrap', gap: 12 }}>
          <div>
            <h1 className="page-title">Security Overview</h1>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <button className="btn-secondary" style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
              <Upload size={14} /> Upload Document
            </button>
          </div>
        </div>

        <div className="stats-grid stagger" style={{ marginBottom: 24 }}>
          <StatCard label="Documents Scanned" value="2,847" sub="All sources" delta="+12.3%" deltaUp={true} />
          <StatCard label="Critical Risks" value="3" sub="Score > 80" delta="+1 new" deltaUp={false} />
          <StatCard label="AI Analyses Today" value="156" sub="Avg confidence 94%" delta="+23%" deltaUp={true}  />
          <StatCard label="Active Alerts" value="4" sub="Pending review" delta="2 critical"  />
        </div>

        <div className="dashboard-row row-8-4" style={{ marginBottom: 16 }}>
          <div className="chart-card">
            <div className="chart-header">
              <div>
                <div className="chart-title">Risk Score Trend</div>
                <div className="chart-subtitle">14-day average risk score and high-risk event volume</div>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                  <span style={{ width: 8, height: 3, borderRadius: 2, background: '#E55720' }} /> Risk Score
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                  <span style={{ width: 8, height: 3, borderRadius: 2, background: '#8B5CF6' }} /> Events
                </div>
              </div>
            </div>
            <ResponsiveContainer width="100%" height={240}>
              <AreaChart data={riskTrendData} margin={{ top: 8, right: 8, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="riskGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#E55720" stopOpacity={0.15} />
                    <stop offset="95%" stopColor="#E55720" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="eventGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#8B5CF6" stopOpacity={0.1} />
                    <stop offset="95%" stopColor="#8B5CF6" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.03)" vertical={false} />
                <XAxis dataKey="date" tick={{ fill: '#475569', fontSize: 10 }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fill: '#475569', fontSize: 10 }} axisLine={false} tickLine={false} />
                <Tooltip content={<CustomTooltip />} />
                <Area type="monotone" dataKey="score" name="Risk Score" stroke="#E55720" strokeWidth={2} fill="url(#riskGrad)" dot={false} activeDot={{ r: 4, fill: '#E55720', stroke: '#090A0C', strokeWidth: 2 }} />
                <Area type="monotone" dataKey="events" name="Events" stroke="#8B5CF6" strokeWidth={1.5} fill="url(#eventGrad)" dot={false} activeDot={{ r: 3, fill: '#8B5CF6', stroke: '#090A0C', strokeWidth: 2 }} />
              </AreaChart>
            </ResponsiveContainer>
          </div>

          <div className="chart-card" style={{ display: 'flex', flexDirection: 'column' }}>
            <div className="chart-header" style={{ marginBottom: 0 }}>
              <div>
                <div className="chart-title">Classification</div>
                <div className="chart-subtitle">{totalClassified} documents total</div>
              </div>
            </div>
            <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <ResponsiveContainer width="100%" height={160}>
                <PieChart>
                  <Pie data={classificationData} cx="50%" cy="50%" innerRadius={45} outerRadius={65} dataKey="value" strokeWidth={0}>
                    {classificationData.map((entry, i) => (
                      <Cell key={i} fill={entry.color} />
                    ))}
                  </Pie>
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8, marginTop: 8 }}>
              {classificationData.map(c => (
                <div key={c.name} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <span style={{ width: 8, height: 8, borderRadius: 2, background: c.color }} />
                    <span style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>{c.name}</span>
                  </div>
                  <span style={{ fontSize: '0.78rem', fontWeight: 600, color: 'var(--text-primary)', fontFamily: 'var(--font-mono)' }}>{c.value}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="section-panel" style={{ marginBottom: 16 }}>
          <div className="section-panel-header">
            <div>
              <div className="chart-title">Recent Activity</div>
              <div className="chart-subtitle">Latest document scans across all ingestion sources</div>
            </div>
            <a href="/documents" className="view-all-link">
              View all <ChevronRight size={14} />
            </a>
          </div>
          <div className="section-panel-body">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Document</th>
                  <th>User</th>
                  <th>Classification</th>
                  <th>Risk</th>
                  <th>Action</th>
                  <th>Time</th>
                </tr>
              </thead>
              <tbody>
                {recentActivity.map(row => (
                  <tr key={row.id}>
                    <td>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                        <div style={{
                          width: 30, height: 30, borderRadius: 8,
                          background: 'rgba(255,255,255,0.03)',
                          border: '1px solid var(--border)',
                          display: 'flex', alignItems: 'center', justifyContent: 'center'
                        }}>
                          <FileText size={14} color="var(--text-muted)" />
                        </div>
                        <div>
                          <div style={{ fontSize: '0.82rem', fontWeight: 500, color: 'var(--text-primary)' }}>{row.file}</div>
                          <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>{row.dept}</div>
                        </div>
                      </div>
                    </td>
                    <td style={{ fontFamily: 'var(--font-mono)', fontSize: '0.78rem' }}>{row.user}</td>
                    <td>{getLabelChip(row.label)}</td>
                    <td>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                        <span className={`status-dot ${row.status}`} />
                        <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 600, color: row.risk >= 80 ? 'var(--danger-light)' : row.risk >= 50 ? 'var(--warning-light)' : 'var(--success-light)' }}>
                          {row.risk}
                        </span>
                      </div>
                    </td>
                    <td>
                      <span style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>{row.action}</span>
                    </td>
                    <td>
                      <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: 4 }}>
                        <Clock size={11} /> {row.time}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </AppLayout>
  );
};

export default DashboardPage;
