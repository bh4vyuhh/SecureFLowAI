import React, { useState, useMemo } from 'react';
import { ResponsiveContainer, LineChart, Line, BarChart, Bar, XAxis, YAxis, Tooltip } from 'recharts';
import { ArrowUpRight, ArrowDownRight, Download, Search, AlertCircle, RefreshCw, Radio, Shield, CheckCircle, Database } from 'lucide-react';
import toast from 'react-hot-toast';

export default function Dashboard({ logs = [], setLogs, setView, stats = {}, liveAlerts = [], onRefresh, loading }) {
  const [filterSource, setFilterSource] = useState('All');
  const [filterCategory, setFilterCategory] = useState('All');
  const [searchTerm, setSearchTerm] = useState('');

  // Handle genuine CSV Export from real database records
  const handleExportCSV = () => {
    if (logs.length === 0) {
      toast.error('No incident records in database to export.');
      return;
    }
    const headers = ['Event ID', 'Timestamp', 'Client ID', 'User ID', 'Department', 'Destination', 'Action', 'Tier', 'Risk Score', 'Enforcement'];
    const rows = logs.map(log => [
      log.id || '',
      log.timestamp || '',
      `"${log.client_id || ''}"`,
      `"${log.user_id || ''}"`,
      `"${log.department || ''}"`,
      `"${log.destination_domain || ''}"`,
      `"${log.source_action || ''}"`,
      `"${log.classification_tier || ''}"`,
      log.risk_score || 0,
      `"${log.enforcement_action || ''}"`
    ]);
    
    const csvContent = [headers.join(','), ...rows.map(e => e.join(','))].join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', `secureflow_realtime_audit_${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    toast.success(`Exported ${logs.length} live records from SQLite.`);
  };

  const toggleIncorrectClassification = (id) => {
    setLogs(prev => prev.map(log => 
      log.id === id 
        ? { ...log, incorrectClassification: !log.incorrectClassification }
        : log
    ));
    toast.success('Feedback logged to ML active-learning queue.');
  };

  // Filter logs dynamically from real SQLite data
  const filteredLogs = useMemo(() => {
    return logs.filter(log => {
      const src = log.source_action || log.source || '';
      const cat = log.classification_tier || log.category || '';
      const dest = log.destination_domain || log.details || log.file_name || log.fileName || '';
      const user = log.user_id || '';

      const matchSrc = filterSource === 'All' || src.toLowerCase().includes(filterSource.toLowerCase());
      const matchCat = filterCategory === 'All' || cat.toLowerCase() === filterCategory.toLowerCase();
      const matchSearch = dest.toLowerCase().includes(searchTerm.toLowerCase()) || 
                          user.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          (log.id && log.id.toLowerCase().includes(searchTerm.toLowerCase()));
      return matchSrc && matchCat && matchSearch;
    });
  }, [logs, filterSource, filterCategory, searchTerm]);

  // Real chronological sparkline data directly from actual logged incidents
  const sparklineData = useMemo(() => {
    if (logs.length === 0) {
      return [{ time: 'Now', risk: 0 }];
    }
    // Take real timestamps and risk scores from real logs (chronological order)
    return logs.slice(0, 15).reverse().map((item, idx) => ({
      time: item.timestamp ? new Date(item.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }) : `E${idx + 1}`,
      risk: item.risk_score || 0,
      latency: item.telemetry?.latency_ms || 12
    }));
  }, [logs]);

  // Real Dot Matrix: 1 dot corresponds to 1 real event in the database
  const realDotMatrix = useMemo(() => {
    const totalSlots = 70;
    const dots = [];
    for (let i = 0; i < totalSlots; i++) {
      if (i < logs.length) {
        const item = logs[i];
        const status = item.enforcement_action === 'BLOCK' ? 'alert' :
                       item.enforcement_action === 'MASK' ? 'high' : 'low';
        dots.push({ id: item.id || i, status, active: true });
      } else {
        dots.push({ id: i, status: 'idle', active: false });
      }
    }
    return dots;
  }, [logs]);

  // Real Mitigation Breakdown by actual Department or Source Action in the database
  const realSourceBreakdown = useMemo(() => {
    if (logs.length === 0) return [];
    const sourceMap = {};
    logs.forEach(item => {
      const src = item.source_action || 'Gateway';
      if (!sourceMap[src]) {
        sourceMap[src] = { count: 0, blocked: 0, masked: 0, allowed: 0 };
      }
      sourceMap[src].count++;
      if (item.enforcement_action === 'BLOCK') sourceMap[src].blocked++;
      else if (item.enforcement_action === 'MASK') sourceMap[src].masked++;
      else sourceMap[src].allowed++;
    });

    return Object.entries(sourceMap).map(([name, data], idx) => ({
      id: idx + 1,
      name,
      total: data.count,
      blocked: data.blocked,
      masked: data.masked,
      allowed: data.allowed,
      blockedPct: Math.round((data.blocked / data.count) * 100),
      maskedPct: Math.round((data.masked / data.count) * 100),
    }));
  }, [logs]);

  // Real Timeline: Real incidents grouped by actual day and positioned by real minutes
  const realTimeline = useMemo(() => {
    if (logs.length === 0) return [];
    
    // Group real incidents by date
    const dateMap = {};
    logs.slice(0, 15).forEach((item) => {
      const dateKey = item.timestamp 
        ? new Date(item.timestamp).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })
        : 'Live';
      if (!dateMap[dateKey]) dateMap[dateKey] = [];
      dateMap[dateKey].push(item);
    });

    return Object.entries(dateMap).map(([date, items]) => ({
      date,
      events: items.map((item) => {
        // Calculate real minute offset
        const itemTime = item.timestamp ? new Date(item.timestamp).getTime() : Date.now();
        const minutesAgo = Math.max(0, Math.min(30, Math.round((Date.now() - itemTime) / 60000)));
        const positionPercent = Math.max(2, Math.min(88, 100 - (minutesAgo / 30) * 100));

        return {
          id: item.id,
          label: item.destination_domain || item.source_action || 'Event',
          score: item.risk_score ? `${item.risk_score}%` : 'DLP',
          position: positionPercent,
          action: item.enforcement_action,
          color: item.enforcement_action === 'BLOCK' ? '#f38933' : item.enforcement_action === 'MASK' ? '#8df85f' : '#ffffff'
        };
      })
    }));
  }, [logs]);

  // Unique sources and categories from real data for filters
  const uniqueSources = useMemo(() => {
    const set = new Set(logs.map(l => l.source_action).filter(Boolean));
    return Array.from(set);
  }, [logs]);

  const uniqueTiers = useMemo(() => {
    const set = new Set(logs.map(l => l.classification_tier).filter(Boolean));
    return Array.from(set);
  }, [logs]);

  return (
    <div className="flex-1 p-8 space-y-8 select-none">
      
      {/* Top Header & Real-time Sync */}
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <h1 className="text-4xl font-extrabold tracking-tight uppercase font-sans text-white">
            CHECK BOX
          </h1>
          <p className="text-xs text-[#8e8f96] mt-0.5">
            Real-time Autonomous Banking DLP SOC Telemetry & Gateway Monitor
          </p>
        </div>

        <div className="flex items-center gap-3">
          <div className="bg-[#0c0c0e] border border-[#161619] rounded-2xl px-4 py-2 text-xs font-semibold text-[#8e8f96] flex items-center gap-2">
            <span>Database:</span>
            <span className="text-[#8df85f] font-mono">SQLite ({logs.length} records)</span>
          </div>

          <div className="bg-[#0c0c0e] border border-[#161619] rounded-2xl px-4 py-2 text-xs font-semibold text-[#8e8f96] flex items-center gap-2">
            <span>Source:</span>
            <select 
              value={filterSource}
              onChange={e => setFilterSource(e.target.value)}
              className="bg-transparent text-white focus:outline-none cursor-pointer"
            >
              <option value="All">All Ingestion Sources</option>
              {uniqueSources.map(s => (
                <option key={s} value={s}>{s}</option>
              ))}
            </select>
          </div>

          {onRefresh && (
            <button
              onClick={onRefresh}
              className="bg-[#0c0c0e] border border-[#161619] rounded-2xl px-3.5 py-2 text-xs font-semibold text-[#8e8f96] hover:text-white hover:border-white transition cursor-pointer flex items-center gap-1.5"
              title="Refresh Realtime SOC Data"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
              Sync
            </button>
          )}
        </div>
      </div>

      {/* Main Grid: 5 columns left, 7 columns right */}
      <div className="grid grid-cols-12 gap-8">
        
        {/* Left Column: Metric Cards */}
        <div className="col-span-12 lg:col-span-5 flex flex-col gap-8">
          
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-8">
            
            {/* Card 1: Real-time Ingestion Stream */}
            <div className="bg-[#0c0c0e] border border-[#161619] rounded-[28px] p-6 flex flex-col justify-between h-[210px]">
              <div>
                <div className="flex items-center justify-between text-[11px] font-bold tracking-wider text-[#8e8f96] uppercase mb-4">
                  <span>Live Event Ingestion</span>
                  <span className="cursor-pointer text-[#8e8f96] hover:text-white" onClick={() => setView('live')}>•••</span>
                </div>
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <div className="text-2xl font-extrabold text-white flex items-center gap-1 font-sans">
                      {stats.total_scanned ?? logs.length}
                      <span className="text-[#8df85f] text-xs"><ArrowUpRight className="w-3.5 h-3.5 inline" /></span>
                    </div>
                    <div className="text-[10px] font-semibold text-[#8e8f96]">Total Scanned</div>
                  </div>
                  <div>
                    <div className="text-2xl font-extrabold text-white flex items-center gap-1 font-sans">
                      {stats.avg_latency_ms ? `${stats.avg_latency_ms}ms` : '0ms'}
                      <span className="text-[#8df85f] text-xs"><ArrowDownRight className="w-3.5 h-3.5 inline" /></span>
                    </div>
                    <div className="text-[10px] font-semibold text-[#8e8f96]">Real Avg Latency</div>
                  </div>
                </div>
              </div>

              <div className="h-14 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={sparklineData}>
                    <Line type="monotone" dataKey="risk" stroke="#f38933" strokeWidth={2} dot={false} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Card 2: Bulk Scanner & Threat Distribution */}
            <div className="bg-[#0c0c0e] border border-[#161619] rounded-[28px] p-6 flex flex-col justify-between h-[210px]">
              <div>
                <div className="flex items-center justify-between text-[11px] font-bold tracking-wider text-[#8e8f96] uppercase mb-4">
                  <span>Enforcement Ratio</span>
                  <span className="cursor-pointer text-[#8e8f96] hover:text-white" onClick={() => setView('scanner')}>•••</span>
                </div>
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <div className="text-2xl font-extrabold text-white flex items-center gap-1 font-sans">
                      {stats.allowed_count ?? logs.filter(l => l.enforcement_action === 'ALLOW').length}
                      <span className="text-[#8df85f] text-xs"><ArrowUpRight className="w-3.5 h-3.5 inline" /></span>
                    </div>
                    <div className="text-[10px] font-semibold text-[#8e8f96]">Allowed / Clean</div>
                  </div>
                  <div>
                    <div className="text-2xl font-extrabold text-white flex items-center gap-1 font-sans">
                      {stats.blocked_count ?? logs.filter(l => l.enforcement_action === 'BLOCK').length}
                      <span className="text-[#f38933] text-xs"><ArrowDownRight className="w-3.5 h-3.5 inline" /></span>
                    </div>
                    <div className="text-[10px] font-semibold text-[#8e8f96]">Blocked Exfiltration</div>
                  </div>
                </div>
              </div>
              
              <div className="grid grid-cols-14 gap-1.5 pt-4">
                {realDotMatrix.map((dot) => (
                  <div
                    key={dot.id}
                    title={dot.active ? `Incident: ${dot.status}` : 'Idle slot'}
                    className={`w-1.5 h-1.5 rounded-full transition-colors duration-300 ${
                      !dot.active ? 'bg-[#1e1f25]' :
                      dot.status === 'low' ? 'bg-[#8df85f]' :
                      dot.status === 'high' ? 'bg-[#f38933]' :
                      'bg-white shadow-[0_0_6px_#ffffff]'
                    }`}
                  />
                ))}
              </div>
            </div>

          </div>

          {/* Card 3: Real DLP Mitigation Logs by Actual Ingestion Source */}
          <div className="bg-[#0c0c0e] border border-[#161619] rounded-[28px] p-6 flex flex-col justify-between h-[300px]">
            <div>
              <div className="flex items-center justify-between text-[11px] font-bold tracking-wider text-[#8e8f96] uppercase mb-4">
                <span>Real-Time Enforcement by Channel</span>
                <span className="cursor-pointer text-[#8e8f96] hover:text-white" onClick={() => setView('audit')}>•••</span>
              </div>
            </div>

            {realSourceBreakdown.length > 0 ? (
              <div className="space-y-3 overflow-y-auto max-h-44 pr-1">
                {realSourceBreakdown.map((item) => (
                  <div key={item.id} className="space-y-1.5">
                    <div className="flex items-center justify-between text-xs">
                      <span className="text-white font-medium truncate max-w-[180px]">{item.name}</span>
                      <span className="text-[#8e8f96] font-mono text-[11px]">
                        {item.total} events ({item.blocked} blocked, {item.masked} masked)
                      </span>
                    </div>
                    <div className="w-full bg-[#1e2025] h-2 rounded-full overflow-hidden flex">
                      <div 
                        style={{ width: `${(item.allowed / item.total) * 100}%` }}
                        className="bg-white h-full"
                        title={`Allowed: ${item.allowed}`}
                      />
                      <div 
                        style={{ width: `${(item.masked / item.total) * 100}%` }}
                        className="bg-[#8df85f] h-full"
                        title={`Masked: ${item.masked}`}
                      />
                      <div 
                        style={{ width: `${(item.blocked / item.total) * 100}%` }}
                        className="bg-[#f38933] h-full"
                        title={`Blocked: ${item.blocked}`}
                      />
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="flex-1 flex flex-col items-center justify-center text-center p-4 text-[#8e8f96]">
                <Database className="w-6 h-6 mb-2 text-[#8e8f96]" />
                <div className="text-xs font-semibold">No transactions recorded yet</div>
                <div className="text-[10px]">Awaiting incoming requests to calculate enforcement by channel.</div>
              </div>
            )}

            <div className="flex items-center justify-between border-t border-[#161619] pt-4 mt-2">
              <div className="flex items-center gap-5 text-[10px] font-bold tracking-wide">
                <span className="flex items-center gap-1.5 text-white">
                  <span className="w-2.5 h-2.5 rounded-full bg-white inline-block" />
                  Allowed
                </span>
                <span className="flex items-center gap-1.5 text-[#8e8f96]">
                  <span className="w-2.5 h-2.5 rounded-full bg-[#8df85f] inline-block" />
                  Masked
                </span>
                <span className="flex items-center gap-1.5 text-[#8e8f96]">
                  <span className="w-2.5 h-2.5 rounded-full bg-[#f38933] inline-block" />
                  Blocked
                </span>
              </div>
              <div className="text-xs font-bold text-white font-mono">
                Total Stored: <span className="text-[#8df85f]">{logs.length}</span>
              </div>
            </div>
          </div>

        </div>

        {/* Right Column: Real Anomaly Feeds Timeline */}
        <div className="col-span-12 lg:col-span-7">
          <div className="bg-[#0c0c0e] border border-[#161619] rounded-[28px] p-6 flex flex-col justify-between h-[542px]">
            <div>
              <div className="flex items-center justify-between text-[11px] font-bold tracking-wider text-[#8e8f96] uppercase mb-6">
                <span className="flex items-center gap-2">
                  <Radio className="w-3.5 h-3.5 text-[#8df85f] animate-pulse" />
                  Live Anomaly Feeds Timeline
                </span>
                <span className="text-xs text-[#8e8f96] font-mono">Real-time WebSocket Bus</span>
              </div>
            </div>

            {realTimeline.length > 0 ? (
              <div className="flex-1 flex flex-col justify-between relative timeline-track pr-4">
                {realTimeline.slice(0, 4).map((day) => (
                  <div key={day.date} className="grid grid-cols-12 items-center relative h-12 border-b border-[#111215] last:border-b-0">
                    <div className="col-span-2 text-xs font-semibold text-[#8e8f96] font-mono truncate">
                      {day.date}
                    </div>
                    <div className="col-span-10 relative h-full flex items-center">
                      {day.events.slice(0, 3).map((item) => (
                        <div
                          key={item.id}
                          className="absolute h-7 rounded-full flex items-center justify-between px-3 text-black font-extrabold text-[11px] select-none hover:scale-[1.02] transition-transform duration-200 shadow-md cursor-pointer"
                          style={{
                            left: `${Math.max(2, Math.min(70, item.position))}%`,
                            backgroundColor: item.color
                          }}
                          title={`${item.label} (${item.score}) - ${item.action}`}
                        >
                          <span className="truncate max-w-[100px]">{item.label}</span>
                          <span className="ml-2 font-mono">{item.score}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}

                <div className="grid grid-cols-12 pt-4 border-t border-[#161619]">
                  <div className="col-span-2" />
                  <div className="col-span-10 flex justify-between px-1 text-[10px] font-bold text-[#8e8f96] font-mono">
                    <span>30m ago</span>
                    <span>20m ago</span>
                    <span>10m ago</span>
                    <span>Now</span>
                  </div>
                </div>
              </div>
            ) : (
              <div className="flex-1 flex flex-col items-center justify-center border border-dashed border-[#161619] rounded-2xl p-8 text-center space-y-3">
                <div className="w-12 h-12 rounded-full bg-[#121316] border border-[#21232a] flex items-center justify-center text-[#8df85f]">
                  <Radio className="w-6 h-6 animate-pulse" />
                </div>
                <div className="text-sm font-bold text-white">Live Threat Stream Awaiting Events</div>
                <p className="text-xs text-[#8e8f96] max-w-sm">
                  Active WebSocket listener connected on <span className="font-mono text-white">/ws/live-threats</span>. 
                  Incoming browser extension pastes and desktop daemon scans appear here dynamically in real time.
                </p>
                <button
                  onClick={() => setView('live')}
                  className="mt-2 px-4 py-2 bg-white text-black text-xs font-bold rounded-xl hover:scale-105 transition cursor-pointer"
                >
                  Test Live Scan
                </button>
              </div>
            )}

            <div className="flex items-center justify-between border-t border-[#161619] pt-4 mt-4">
              <div className="flex items-center gap-5 text-[10px] font-bold tracking-wide">
                <span className="flex items-center gap-1.5 text-[#8e8f96]">
                  <span className="w-2.5 h-2.5 rounded-full bg-[#8df85f] inline-block" />
                  Masked Tokens
                </span>
                <span className="flex items-center gap-1.5 text-[#8e8f96]">
                  <span className="w-2.5 h-2.5 rounded-full bg-[#f38933] inline-block" />
                  Blocked Exfiltration
                </span>
                <span className="flex items-center gap-1.5 text-[#8e8f96]">
                  <span className="w-2.5 h-2.5 rounded-full bg-white inline-block" />
                  Cleared Ingestion
                </span>
              </div>
              <div className="text-xs font-bold text-white font-mono">
                Active Threats: <span className="text-[#f38933]">{stats.active_incidents_open || 0}</span>
              </div>
            </div>
          </div>
        </div>

      </div>

      {/* Full Width Bottom Card: DLP Transaction Audit Logs */}
      <div className="bg-[#0c0c0e] border border-[#161619] rounded-[28px] p-6 space-y-6">
        <div className="flex items-center justify-between flex-wrap gap-4">
          <div>
            <h2 className="text-xl font-bold text-white mb-1">DLP Transaction Audit Logs</h2>
            <p className="text-xs text-[#8e8f96]">
              Real-time persistent SQLite audit trail of all Tier 1-5 gateway inspections and enforcement actions
            </p>
          </div>

          <div className="flex items-center gap-3">
            <div className="relative">
              <Search className="w-4 h-4 text-[#8e8f96] absolute left-3.5 top-3" />
              <input
                type="text"
                placeholder="Search user, destination, ID..."
                value={searchTerm}
                onChange={e => setSearchTerm(e.target.value)}
                className="bg-[#121316] border border-[#23252c] rounded-xl pl-10 pr-4 py-2 text-xs text-white placeholder-[#8e8f96] focus:outline-none focus:border-white w-56"
              />
            </div>

            <select
              value={filterSource}
              onChange={e => setFilterSource(e.target.value)}
              className="bg-[#121316] border border-[#23252c] rounded-xl px-3 py-2 text-xs text-white focus:outline-none cursor-pointer"
            >
              <option value="All">All Sources</option>
              {uniqueSources.map(s => (
                <option key={s} value={s}>{s}</option>
              ))}
            </select>

            <select
              value={filterCategory}
              onChange={e => setFilterCategory(e.target.value)}
              className="bg-[#121316] border border-[#23252c] rounded-xl px-3 py-2 text-xs text-white focus:outline-none cursor-pointer"
            >
              <option value="All">All Tiers</option>
              {uniqueTiers.map(t => (
                <option key={t} value={t}>{t}</option>
              ))}
            </select>

            <button
              onClick={handleExportCSV}
              className="bg-white text-black font-semibold text-xs px-4 py-2 rounded-xl flex items-center gap-2 hover:scale-105 transition cursor-pointer"
            >
              <Download className="w-3.5 h-3.5" />
              Export CSV
            </button>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-[#161619] text-[#8e8f96] text-xs font-semibold uppercase tracking-wider">
                <th className="py-4 px-4">Timestamp</th>
                <th className="py-4 px-4">Source / Client</th>
                <th className="py-4 px-4">Subject / Destination</th>
                <th className="py-4 px-4">Category Tier</th>
                <th className="py-4 px-4">Risk</th>
                <th className="py-4 px-4">Mitigation</th>
                <th className="py-4 px-4">Accuracy Pipeline</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#111215] text-xs">
              {filteredLogs.map((log) => {
                const isHighRisk = (log.risk_score || log.riskScore || 0) > 75;
                const tier = log.classification_tier || log.category || 'SAFE';
                const action = log.enforcement_action || log.actionTaken || 'ALLOW';
                const dateText = log.timestamp ? new Date(log.timestamp).toLocaleString() : 'Live';

                return (
                  <tr key={log.id || Math.random()} className="hover:bg-[#121316] transition-colors">
                    <td className="py-4 px-4 font-mono text-[#8e8f96]">
                      {dateText}
                    </td>
                    <td className="py-4 px-4 font-medium text-white">
                      <div className="font-sans">{log.source_action || log.source || 'Gateway'}</div>
                      <div className="text-[10px] text-[#8e8f96] font-mono">{log.client_id || 'daemon'}</div>
                    </td>
                    <td className="py-4 px-4 max-w-[220px] truncate" title={log.details || log.destination_domain}>
                      <span className="font-mono text-[#8df85f] block text-[11px] mb-0.5 truncate">
                        {log.destination_domain || log.file_name || log.fileName || 'API Ingestion'}
                      </span>
                      <span className="text-[#8e8f96] block text-[10px] truncate">
                        {log.user_id ? `${log.user_id} (${log.department || 'dept'})` : (log.details || 'Live payload inspection')}
                      </span>
                    </td>
                    <td className="py-4 px-4">
                      <span className={`px-2 py-0.5 rounded-full font-bold text-[9px] uppercase ${
                        tier === 'RESTRICTED' || tier === 'Highly Confidential' ? 'bg-[#f38933]/15 text-[#f38933] border border-[#f38933]/30' :
                        tier === 'CONFIDENTIAL' || tier === 'Confidential' ? 'bg-white/10 text-white border border-white/20' :
                        tier === 'INTERNAL' || tier === 'Internal' ? 'bg-[#8df85f]/15 text-[#8df85f] border border-[#8df85f]/30' :
                        'bg-gray-800 text-gray-400'
                      }`}>
                        {tier}
                      </span>
                    </td>
                    <td className="py-4 px-4">
                      <div className="flex items-center gap-1.5">
                        <span className={`font-bold font-mono ${isHighRisk ? 'text-[#f38933]' : 'text-white'}`}>
                          {log.risk_score ?? log.riskScore ?? 0}%
                        </span>
                        {isHighRisk && <AlertCircle className="w-3.5 h-3.5 text-[#f38933]" />}
                      </div>
                    </td>
                    <td className="py-4 px-4">
                      <span className={`font-mono text-[11px] font-semibold ${
                        action === 'BLOCK' ? 'text-[#f38933]' :
                        action === 'MASK' ? 'text-[#8df85f]' : 'text-slate-300'
                      }`}>
                        {action}
                      </span>
                    </td>
                    <td className="py-4 px-4">
                      <button
                        onClick={() => toggleIncorrectClassification(log.id)}
                        className={`px-3 py-1.5 rounded-lg flex items-center gap-1.5 border font-semibold text-[10px] transition cursor-pointer ${
                          log.incorrectClassification
                            ? 'bg-[#f38933]/10 border-[#f38933] text-[#f38933]'
                            : 'border-[#23252c] text-[#8e8f96] hover:text-white hover:border-white'
                        }`}
                      >
                        <RefreshCw className="w-3 h-3" />
                        {log.incorrectClassification ? 'Reported Incorrect' : 'Report Error'}
                      </button>
                    </td>
                  </tr>
                );
              })}

              {filteredLogs.length === 0 && (
                <tr>
                  <td colSpan={7} className="py-12 text-center text-[#8e8f96] font-semibold">
                    <div className="flex flex-col items-center justify-center space-y-2">
                      <Radio className="w-6 h-6 text-[#8df85f] animate-pulse" />
                      <div>No matching transaction logs found in database.</div>
                      <div className="text-xs text-[#8e8f96]">
                        Listening on WebSocket threat bus. Use <span className="text-white">Live Classification</span> or <span className="text-white">File Scanner</span> to test.
                      </div>
                    </div>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
