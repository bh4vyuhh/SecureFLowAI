import React, { useState, useMemo } from 'react';
import { Toaster } from 'react-hot-toast';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import Dashboard from './pages/Dashboard';
import LiveClassification from './pages/LiveClassification';
import FileScanner from './pages/FileScanner';
import AuditLogsView from './pages/AuditLogsView';
import Settings from './pages/Settings';
import Chatbot from './components/Chatbot';
import Auth from './pages/Auth';
import { initialLogs } from './utils/mockData';

export default function App() {
  const [user, setUser] = useState({ name: 'Security Officer', email: 'officer@company.com' });
  const [currentView, setView] = useState('dashboard');
  const [logs, setLogs] = useState(initialLogs);

  const alertsCount = useMemo(() => {
    return logs.filter(log => log.riskScore > 80).length;
  }, [logs]);

  const handleAddNewLog = (newLog) => {
    const logItem = {
      id: `evt-${1000 + logs.length}`,
      timestamp: new Date().toISOString(),
      incorrectClassification: false,
      ...newLog
    };
    setLogs(prev => [logItem, ...prev]);
  };

  const renderView = () => {
    switch (currentView) {
      case 'dashboard':
        return <Dashboard logs={logs} setLogs={setLogs} setView={setView} />;
      case 'live':
        return <LiveClassification onNewLog={handleAddNewLog} />;
      case 'scanner':
        return <FileScanner onNewLog={handleAddNewLog} />;
      case 'audit':
        return <AuditLogsView logs={logs} setLogs={setLogs} />;
      case 'settings':
        return <Settings />;
      case 'chatbot':
        return (
          <div className="flex-1 p-8 space-y-6">
            <div>
              <h1 className="text-4xl font-extrabold tracking-tight uppercase font-sans text-white">
                DLP SUPPORT ASSISTANT
              </h1>
              <p className="text-sm text-[#8e8f96]">Interact with the SecureFlow AI chatbot to review classification decisions, training metrics, or security controls.</p>
            </div>
            <Chatbot />
          </div>
        );
      default:
        return <Dashboard logs={logs} setLogs={setLogs} setView={setView} />;
    }
  };

  if (!user) {
    return (
      <>
        <Auth onLogin={(u) => setUser(u)} />
        <Toaster position="top-right" toastOptions={{ style: { background: '#121316', color: '#fff', border: '1px solid #23252c' } }} />
      </>
    );
  }

  return (
    <div className="flex bg-[#000000] text-white min-h-screen font-sans">
      <Toaster 
        position="top-right" 
        toastOptions={{ 
          style: { 
            background: '#0c0c0e', 
            color: '#fff', 
            border: '1px solid #161619',
            fontFamily: 'Outfit, sans-serif'
          } 
        }} 
      />

      <Sidebar currentView={currentView} setView={setView} />

      <div className="flex-1 flex flex-col min-w-0 h-screen overflow-y-auto">
        <Header currentView={currentView} setView={setView} alertsCount={alertsCount} />
        
        <main className="flex-grow">
          {renderView()}
        </main>
      </div>
    </div>
  );
}
