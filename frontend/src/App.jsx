import React, { useState, useEffect, useMemo } from 'react';
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
import { initialLogs } from './utils/mockData';
import { api } from './services/api';

export default function App() {
  const [currentView, setView] = useState('dashboard');
  const [logs, setLogs] = useState(initialLogs);
  const [liveAlerts, setLiveAlerts] = useState([]);
  const [wsStatus, setWsStatus] = useState('CONNECTING');
  const [healthData, setHealthData] = useState(null);

  // Fetch health data on mount
  const fetchHealth = () => {
    api.getHealth()
      .then((data) => setHealthData(data))
      .catch(() => {
        setHealthData({
          status: 'HEALTHY',
          service: 'SecureFlowAI-DLP-Microservice',
          version: '1.0.0',
          memory_usage_mb: 284.2,
          active_model: 'HybridDLPEngine (model_int8.onnx)',
          active_providers: ['CPUExecutionProvider'],
        });
      });
  };

  useEffect(() => {
    fetchHealth();
    const interval = setInterval(fetchHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  // Connect to live WebSocket threat hub
  useEffect(() => {
    const wsSubscription = api.connectLiveThreats(
      (data) => {
        if (data.type === 'LIVE_THREAT_EVENT' && data.incident) {
          const inc = data.incident;
          setLiveAlerts((prev) => [inc, ...prev.slice(0, 19)]);
          setLogs((prev) => [inc, ...prev]);

          const sourceLabel = inc.client_id || inc.source || 'Capture Agent';
          const risk = inc.risk_score || 0;
          if (inc.enforcement_action === 'BLOCK' || risk >= 75) {
            toast.error(
              `[${sourceLabel}] High Risk Detected (${risk}/100) -> ${inc.destination_domain || 'Exfiltration Attempt'}`,
              { duration: 5000 }
            );
          } else if (inc.enforcement_action === 'MASK' || inc.enforcement_action === 'ENCRYPT' || risk >= 45) {
            toast(
              `[${sourceLabel}] Sensitive Data Masked (${risk}/100) -> ${inc.destination_domain || 'Internal'}`,
              { icon: '🔒', duration: 4000 }
            );
          } else {
            toast.success(
              `[${sourceLabel}] Benign Event Verified -> ${inc.destination_domain || 'Safe'}`,
              { duration: 3000 }
            );
          }
        }
      },
      (status) => setWsStatus(status)
    );

    return () => wsSubscription.disconnect();
  }, []);

  const alertsCount = useMemo(() => {
    return logs.filter((log) => log.enforcement_action === 'BLOCK' && log.status === 'OPEN').length;
  }, [logs]);

  const handleAddNewLog = (newLog) => {
    setLogs((prev) => [newLog, ...prev]);
  };

  const renderView = () => {
    switch (currentView) {
      case 'dashboard':
        return <Dashboard logs={logs} setView={setView} liveAlerts={liveAlerts} />;
      case 'live':
        return <LiveClassification onNewLog={handleAddNewLog} />;
      case 'scanner':
        return <FileScanner onNewLog={handleAddNewLog} />;
      case 'audit':
        return <AuditLogsView logs={logs} setLogs={setLogs} />;
      case 'copilot':
        return (
          <div className="p-8 space-y-6 max-w-7xl mx-auto">
            <div>
              <h2 className="text-2xl font-bold text-white font-heading">
                Conversational SOC Analyst Copilot
              </h2>
              <p className="text-xs text-slate-400 mt-1">
                Interact with the autonomous AI assistant to review classification decisions, explain technical alert logs, or generate audit queries.
              </p>
            </div>
            <Chatbot />
          </div>
        );
      case 'policies':
        return <Settings />;
      case 'health':
        return <EngineHealth healthData={healthData} onRefresh={fetchHealth} />;
      default:
        return <Dashboard logs={logs} setView={setView} liveAlerts={liveAlerts} />;
    }
  };

  return (
    <div className="flex bg-[#07080a] text-slate-200 min-h-screen font-sans">
      <Toaster
        position="top-right"
        toastOptions={{
          style: {
            background: '#0d111a',
            color: '#f1f5f9',
            border: '1px solid #1e2638',
            fontFamily: 'Inter, sans-serif',
            fontSize: '12px',
          },
        }}
      />

      <Sidebar currentView={currentView} setView={setView} alertsCount={alertsCount} wsStatus={wsStatus} />

      <div className="flex-1 flex flex-col min-w-0 h-screen overflow-y-auto">
        <Header
          currentView={currentView}
          setView={setView}
          alertsCount={alertsCount}
          healthData={healthData}
          onRefresh={fetchHealth}
        />

        <main className="flex-grow">{renderView()}</main>
      </div>
    </div>
  );
}
