import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { Toaster, toast } from 'react-hot-toast';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import Dashboard from './pages/Dashboard';
import LiveClassification from './pages/LiveClassification';
import FileScanner from './pages/FileScanner';
import AuditLogsView from './pages/AuditLogsView';
import Settings from './pages/Settings';
import EngineHealth from './pages/EngineHealth';
import Chatbot from './components/Chatbot';
import { api } from './services/api';

export default function App() {
  const [currentView, setView] = useState(() => {
    const params = new URLSearchParams(window.location.search);
    return params.get('view') || 'dashboard';
  });

  const handleSetView = (v) => {
    setView(v);
    const url = new URL(window.location);
    url.searchParams.set('view', v);
    window.history.pushState({}, '', url);
  };
  // STRICTLY REAL-TIME DATA ONLY: NO MOCK DATA
  const [logs, setLogs] = useState([]);
  const [stats, setStats] = useState({
    total_scanned: 0,
    blocked_count: 0,
    masked_count: 0,
    allowed_count: 0,
    avg_latency_ms: 0,
    active_incidents_open: 0,
  });
  const [liveAlerts, setLiveAlerts] = useState([]);
  const [wsStatus, setWsStatus] = useState('CONNECTING');
  const [healthData, setHealthData] = useState(null);
  const [loading, setLoading] = useState(true);

  // Fetch real incidents from database
  const fetchIncidents = useCallback(async () => {
    try {
      const data = await api.getIncidents({ limit: 100 });
      if (Array.isArray(data)) {
        setLogs(data);
      }
    } catch (err) {
      console.error('Failed fetching real-time incidents from backend:', err);
    }
  }, []);

  // Fetch real aggregated statistics
  const fetchStats = useCallback(async () => {
    try {
      const data = await api.getStats();
      if (data) {
        setStats(data);
      }
    } catch (err) {
      console.error('Failed fetching real-time stats:', err);
    }
  }, []);

  // Fetch health telemetry
  const fetchHealth = useCallback(async () => {
    try {
      const data = await api.getHealth();
      setHealthData(data);
    } catch (err) {
      console.warn('Backend /health unreachable:', err);
    }
  }, []);

  // Initial load
  const refreshAll = useCallback(async () => {
    setLoading(true);
    await Promise.all([fetchIncidents(), fetchStats(), fetchHealth()]);
    setLoading(false);
  }, [fetchIncidents, fetchStats, fetchHealth]);

  useEffect(() => {
    refreshAll();
    const interval = setInterval(() => {
      fetchStats();
      fetchHealth();
    }, 15000);
    return () => clearInterval(interval);
  }, [refreshAll, fetchStats, fetchHealth]);

  // Connect to live WebSocket threat hub for real-time push events
  useEffect(() => {
    const wsSubscription = api.connectLiveThreats(
      (data) => {
        if (data.type === 'LIVE_THREAT_EVENT' && data.incident) {
          const inc = data.incident;
          setLiveAlerts((prev) => [inc, ...prev.slice(0, 29)]);
          setLogs((prev) => [inc, ...prev.filter((item) => item.id !== inc.id)]);
          
          // Re-fetch stats when new threat arrives
          fetchStats();

          if (inc.enforcement_action === 'BLOCK') {
            toast.error(
              `Live Exfiltration Blocked: ${inc.user_id} (${inc.department}) -> ${inc.destination_domain}`,
              { duration: 4500 }
            );
          } else if (inc.enforcement_action === 'MASK') {
            toast(
              `Live Sensitive Data Masked: ${inc.destination_domain}`,
              { icon: '🔒', duration: 3500 }
            );
          } else {
            toast.success(`Live Inspection Cleared: ${inc.source_action}`, { duration: 3000 });
          }
        }
      },
      (status) => setWsStatus(status)
    );

    return () => wsSubscription.disconnect();
  }, [fetchStats]);

  const alertsCount = useMemo(() => {
    return logs.filter((log) => log.enforcement_action === 'BLOCK' && log.status === 'OPEN').length;
  }, [logs]);

  const handleAddNewLog = (newLog) => {
    setLogs((prev) => [newLog, ...prev]);
    fetchStats();
  };

  const renderView = () => {
    switch (currentView) {
      case 'dashboard':
        return (
          <Dashboard 
            logs={logs} 
            setLogs={setLogs} 
            setView={handleSetView} 
            stats={stats} 
            liveAlerts={liveAlerts}
            onRefresh={refreshAll}
            loading={loading}
          />
        );
      case 'live':
        return <LiveClassification onNewLog={handleAddNewLog} />;
      case 'scanner':
        return <FileScanner onNewLog={handleAddNewLog} />;
      case 'audit':
        return <AuditLogsView logs={logs} setLogs={setLogs} onRefresh={fetchIncidents} />;
      case 'copilot':
        return (
          <div className="flex-1 p-8 space-y-6 select-none">
            <div>
              <h1 className="text-4xl font-extrabold tracking-tight uppercase font-sans text-white">
                DLP SUPPORT ASSISTANT
              </h1>
              <p className="text-sm text-[#8e8f96]">
                Interact with the autonomous AI assistant to review live classification decisions, explain technical alert logs, or audit encryption tokens.
              </p>
            </div>
            <Chatbot />
          </div>
        );
      case 'health':
        return <EngineHealth healthData={healthData} onRefresh={fetchHealth} wsStatus={wsStatus} />;
      case 'settings':
        return <Settings />;
      default:
        return (
          <Dashboard 
            logs={logs} 
            setLogs={setLogs} 
            setView={handleSetView} 
            stats={stats} 
            liveAlerts={liveAlerts}
            onRefresh={refreshAll}
            loading={loading}
          />
        );
    }
  };

  return (
    <div className="flex bg-[#000000] text-white min-h-screen font-sans">
      <Toaster
        position="top-right"
        toastOptions={{
          style: {
            background: '#0c0c0e',
            color: '#fff',
            border: '1px solid #161619',
            fontFamily: 'var(--font-sans)',
            fontSize: '12px',
          },
        }}
      />

      <Sidebar 
        currentView={currentView} 
        setView={handleSetView} 
        alertsCount={alertsCount} 
        wsStatus={wsStatus} 
      />

      <div className="flex-1 flex flex-col min-w-0 h-screen overflow-y-auto">
        <Header
          currentView={currentView}
          setView={handleSetView}
          alertsCount={alertsCount}
          wsStatus={wsStatus}
          onRefresh={refreshAll}
        />

        <main className="flex-grow">{renderView()}</main>
      </div>
    </div>
  );
}
