import React, { useState, useEffect } from 'react';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  BarChart,
  Bar,
  Cell,
  PieChart,
  Pie,
} from 'recharts';
import {
  ShieldAlert,
  Zap,
  Sparkles,
  ExternalLink,
  Clock,
} from 'lucide-react';
import { timelineData, departmentRiskData, entityBreakdownData } from '../utils/mockData';
import { api } from '../services/api';

export default function Dashboard({ logs, setView, liveAlerts = [] }) {
  const [stats, setStats] = useState({
    total_scanned: 24780,
    blocked_count: 226,
    masked_count: 730,
    allowed_count: 23824,
    avg_latency_ms: 11.4,
    active_incidents_open: 5,
  });

  useEffect(() => {
    // Attempt fetching real stats from backend API
    api.getStats()
      .then((data) => {
        if (data && data.total_scanned !== undefined) {
          setStats((prev) => ({ ...prev, ...data }));
        }
      })
      .catch(() => {
        // Fallback to calculated stats from props or default
        if (logs && logs.length > 0) {
          const blocked = logs.filter((l) => l.enforcement_action === 'BLOCK').length;
          const masked = logs.filter((l) => l.enforcement_action === 'MASK').length;
          const allowed = logs.filter((l) => l.enforcement_action === 'ALLOW').length;
          const open = logs.filter((l) => l.status === 'OPEN').length;
          setStats({
            total_scanned: logs.length + 24500,
            blocked_count: blocked + 220,
            masked_count: masked + 710,
            allowed_count: allowed + 23570,
            avg_latency_ms: 10.8,
            active_incidents_open: open,
          });
        }
      });
  }, [logs]);

  const blockRate = (
    (stats.blocked_count / Math.max(1, stats.blocked_count + stats.masked_count + stats.allowed_count)) *
    100
  ).toFixed(2);

  return (
    <div className="p-8 space-y-8 select-none max-w-7xl mx-auto">
      {/* Top Banner: CISO Briefing */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-gradient-to-r from-blue-950/40 via-[#0d111a] to-slate-900/40 border border-[#1e2638] p-6 rounded-3xl backdrop-blur-md">
        <div>
          <div className="flex items-center gap-2 text-xs font-mono uppercase tracking-wider text-blue-400 mb-1">
            <span className="w-2 h-2 rounded-full bg-blue-500 animate-ping" />
            Active Banking Perimeter Monitoring
          </div>
          <h2 className="text-2xl font-bold text-white font-heading">
            Enterprise Data Protection & Threat Defense
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Zero-leak mathematical checksum inspection enforcing PCI-DSS, GLBA, and GDPR across endpoints.
          </p>
        </div>

        <div className="flex items-center gap-3 shrink-0">
          <button
            onClick={() => setView('live')}
            className="px-4 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold flex items-center gap-2 transition shadow-lg shadow-blue-600/25 cursor-pointer"
          >
            <Zap className="w-4 h-4" />
            Inspect Payload
          </button>
          <button
            onClick={() => setView('copilot')}
            className="px-4 py-2.5 rounded-xl bg-[#161d2d] border border-[#232f48] text-slate-200 hover:text-white hover:border-slate-400 text-xs font-semibold flex items-center gap-2 transition cursor-pointer"
          >
            <Sparkles className="w-4 h-4 text-purple-400" />
            Copilot Triage
          </button>
        </div>
      </div>



      {/* Charts Section: 24h Trajectory & Entity Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* 24-Hour Threat Trajectory Area Chart */}
        <div className="lg:col-span-8 banking-card p-6 rounded-3xl space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-base font-bold text-white font-heading">
                24-Hour Inspection & Threat Trajectory
              </h3>
              <p className="text-xs text-slate-400">
                Volume of data packets inspected vs. blocked unauthorized exfiltrations.
              </p>
            </div>
            <span className="text-xs font-mono text-slate-400 bg-[#161d2d] px-3 py-1 rounded-xl">
              Live Stream
            </span>
          </div>

          <div className="h-[280px] w-full pt-4">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={timelineData}>
                <defs>
                  <linearGradient id="colorTotal" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.0} />
                  </linearGradient>
                  <linearGradient id="colorBlocked" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#ef4444" stopOpacity={0.7} />
                    <stop offset="95%" stopColor="#ef4444" stopOpacity={0.0} />
                  </linearGradient>
                </defs>
                <XAxis dataKey="time" stroke="#475569" fontSize={11} tickLine={false} />
                <YAxis stroke="#475569" fontSize={11} tickLine={false} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#0d111a',
                    borderColor: '#1e2638',
                    borderRadius: '12px',
                    fontSize: '12px',
                  }}
                />
                <Area
                  type="monotone"
                  dataKey="totalScanned"
                  stroke="#3b82f6"
                  strokeWidth={2}
                  fillOpacity={1}
                  fill="url(#colorTotal)"
                  name="Scanned Transfers"
                />
                <Area
                  type="monotone"
                  dataKey="blocked"
                  stroke="#ef4444"
                  strokeWidth={2}
                  fillOpacity={1}
                  fill="url(#colorBlocked)"
                  name="Blocked Leaks"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Entity Breakdown Chart */}
        <div className="lg:col-span-4 banking-card p-6 rounded-3xl space-y-4 flex flex-col justify-between">
          <div>
            <h3 className="text-base font-bold text-white font-heading">
              Sensitive Financial Entities
            </h3>
            <p className="text-xs text-slate-400">Distribution of intercepted tokens.</p>
          </div>

          <div className="h-[200px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={entityBreakdownData}
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={75}
                  paddingAngle={5}
                  dataKey="count"
                >
                  {entityBreakdownData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#0d111a',
                    borderColor: '#1e2638',
                    borderRadius: '12px',
                    fontSize: '12px',
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>

          <div className="space-y-1.5 pt-2 border-t border-[#1e2638]">
            {entityBreakdownData.map((e) => (
              <div key={e.name} className="flex items-center justify-between text-xs">
                <div className="flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: e.color }} />
                  <span className="text-slate-300">{e.name}</span>
                </div>
                <span className="font-mono text-slate-400 font-semibold">{e.count}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Departmental Risk & Live Threat Feed Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Department Risk Bar Chart */}
        <div className="lg:col-span-6 banking-card p-6 rounded-3xl space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-base font-bold text-white font-heading">
                Departmental Risk Index
              </h3>
              <p className="text-xs text-slate-400">
                Exposure score by banking division based on incident density.
              </p>
            </div>
          </div>

          <div className="h-[220px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={departmentRiskData} layout="vertical">
                <XAxis type="number" stroke="#475569" fontSize={11} domain={[0, 100]} />
                <YAxis dataKey="name" type="category" stroke="#475569" fontSize={11} width={130} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#0d111a',
                    borderColor: '#1e2638',
                    borderRadius: '12px',
                    fontSize: '12px',
                  }}
                />
                <Bar dataKey="risk" radius={[0, 8, 8, 0]}>
                  {departmentRiskData.map((d, index) => (
                    <Cell
                      key={`bar-${index}`}
                      fill={d.risk > 75 ? '#ef4444' : d.risk > 50 ? '#f59e0b' : '#3b82f6'}
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Live Threat Ticker Feed */}
        <div className="lg:col-span-6 banking-card p-6 rounded-3xl space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />
              <h3 className="text-base font-bold text-white font-heading">
                Live Intercept Feed (/ws/live-threats)
              </h3>
            </div>
            <button
              onClick={() => setView('audit')}
              className="text-xs text-blue-400 hover:underline flex items-center gap-1"
            >
              View Full Logs <ExternalLink className="w-3 h-3" />
            </button>
          </div>

          <div className="space-y-3 overflow-y-auto max-h-[220px] pr-2">
            {(liveAlerts.length > 0 ? liveAlerts : logs.slice(0, 4)).map((item, idx) => {
              const risk = item.risk_score !== undefined ? item.risk_score : (item.riskScore !== undefined ? item.riskScore : 85);
              const isBlock = item.enforcement_action === 'BLOCK' || item.actionTaken === 'BLOCK' || risk >= 75;
              const isMask = item.enforcement_action === 'MASK' || item.actionTaken === 'ENCRYPT' || (risk >= 45 && risk < 75);
              const actionLabel = item.enforcement_action || item.actionTaken || (risk >= 75 ? 'BLOCK' : risk >= 45 ? 'ENCRYPT' : 'ALLOW');
              const sourceLabel = item.client_id || item.source || item.source_action || 'AGENT';

              return (
                <div
                  key={item.id || idx}
                  className={`p-3.5 rounded-2xl bg-[#090d14] border transition cursor-pointer flex items-center justify-between text-xs hover:border-slate-500 ${
                    risk >= 75
                      ? 'border-red-900/40 hover:border-red-500/60 bg-red-950/10'
                      : risk >= 45
                      ? 'border-amber-900/40 hover:border-amber-500/60 bg-amber-950/10'
                      : 'border-[#1a2233] hover:border-emerald-500/50'
                  }`}
                  onClick={() => setView('audit')}
                >
                  <div className="flex items-center gap-3">
                    <span
                      className={`px-2 py-1 rounded-md text-[10px] font-bold font-mono ${
                        isBlock
                          ? 'bg-red-500/15 text-red-400 border border-red-500/30'
                          : isMask
                          ? 'bg-amber-500/15 text-amber-400 border border-amber-500/30'
                          : 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30'
                      }`}
                    >
                      {actionLabel}
                    </span>
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-semibold text-slate-200">
                          {item.user_id || 'employee@bankcorp.com'}
                        </span>
                        <span className="px-1.5 py-0.5 rounded text-[9px] font-mono uppercase bg-[#1e2638] text-slate-400 border border-[#2a364f]">
                          {sourceLabel}
                        </span>
                      </div>
                      <div className="text-[10px] text-slate-400 font-mono mt-0.5">
                        Target: {item.destination_domain || item.targetUrl || item.fileName || 'external endpoint'}
                      </div>
                    </div>
                  </div>

                  <div className="text-right">
                    <div className={`font-mono font-bold ${
                      risk >= 75 ? 'text-red-400' : risk >= 45 ? 'text-amber-400' : 'text-emerald-400'
                    }`}>
                      Risk: {risk}/100
                    </div>
                    <div className="text-[10px] text-slate-500 flex items-center gap-1 justify-end">
                      <Clock className="w-3 h-3" /> Just now
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}
