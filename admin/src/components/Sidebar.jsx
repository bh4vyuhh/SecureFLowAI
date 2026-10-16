import React from 'react';
import {
  LayoutDashboard,
  BrainCircuit,
  UploadCloud,
  FileClock,
  Bot,
  Activity,
  Settings,
  Plus
} from 'lucide-react';

export default function Sidebar({ currentView, setView, alertsCount = 0, wsStatus = 'DISCONNECTED' }) {
  const menuItems = [
    { id: 'dashboard', icon: LayoutDashboard, label: 'Executive Dashboard' },
    { id: 'live', icon: BrainCircuit, label: 'Live Classification' },
    { id: 'scanner', icon: UploadCloud, label: 'File & Document Scanner' },
    { id: 'audit', icon: FileClock, label: 'Audit Logs & Forensics', badge: alertsCount },
    { id: 'copilot', icon: Bot, label: 'Analyst Copilot' },
    { id: 'health', icon: Activity, label: 'Engine Telemetry & Health' },
    { id: 'settings', icon: Settings, label: 'Banking Policies' }
  ];

  return (
    <aside className="w-20 bg-[#070708] border-r border-[#161619] flex flex-col items-center py-6 justify-between select-none shrink-0 h-screen sticky top-0">
      <div className="flex flex-col items-center gap-8 w-full">
        {/* SF Monogram Logo Badge */}
        <div 
          onClick={() => setView('dashboard')}
          className="w-12 h-12 rounded-full bg-white flex items-center justify-center cursor-pointer hover:scale-105 transition-transform duration-200 shadow-[0_0_15px_rgba(255,255,255,0.2)]"
          title="SecureFlow AI - Banking SOC"
        >
          <span className="text-black font-extrabold text-lg font-mono">SF</span>
        </div>

        {/* Live Threat WebSocket Indicator Dot */}
        <div 
          className="flex flex-col items-center gap-1 cursor-pointer"
          title={`WebSocket Threat Bus: ${wsStatus}`}
          onClick={() => setView('health')}
        >
          <span 
            className={`w-2.5 h-2.5 rounded-full transition-colors duration-300 ${
              wsStatus === 'CONNECTED' 
                ? 'bg-[#8df85f] shadow-[0_0_8px_#8df85f]' 
                : 'bg-[#f38933] shadow-[0_0_8px_#f38933]'
            }`} 
          />
        </div>

        {/* Navigation Items */}
        <nav className="flex flex-col gap-4 w-full px-2">
          {menuItems.map((item) => {
            const Icon = item.icon;
            const isActive = currentView === item.id;
            return (
              <div key={item.id} className="relative group flex justify-center">
                <button
                  onClick={() => setView(item.id)}
                  className={`w-12 h-12 rounded-2xl flex items-center justify-center transition-all duration-300 relative cursor-pointer ${
                    isActive 
                      ? 'bg-white text-black shadow-lg scale-105' 
                      : 'text-[#8e8f96] hover:bg-[#121316] hover:text-white'
                  }`}
                  title={item.label}
                >
                  <Icon className="w-5 h-5" />
                  
                  {item.badge > 0 && !isActive && (
                    <span className="absolute -top-1 -right-1 w-4 h-4 rounded-full bg-[#f38933] text-black font-extrabold text-[9px] flex items-center justify-center font-mono">
                      {item.badge > 9 ? '9+' : item.badge}
                    </span>
                  )}
                </button>

                <div className="absolute left-20 top-2.5 px-3 py-1.5 rounded-lg bg-black border border-[#1e2025] text-xs text-white opacity-0 pointer-events-none group-hover:opacity-100 transition-opacity duration-200 z-50 whitespace-nowrap font-medium shadow-xl">
                  {item.label}
                  {item.badge > 0 && (
                    <span className="ml-2 text-[#f38933] font-bold">({item.badge} open)</span>
                  )}
                </div>
              </div>
            );
          })}
        </nav>
      </div>

      {/* Quick Action Button */}
      <button 
        onClick={() => setView('scanner')}
        className="w-12 h-12 rounded-2xl bg-[#121316] border border-[#21232a] flex items-center justify-center text-white hover:border-white hover:scale-105 transition-all duration-300 shadow-md cursor-pointer"
        title="Quick Document Scan"
      >
        <Plus className="w-6 h-6" />
      </button>
    </aside>
  );
}
