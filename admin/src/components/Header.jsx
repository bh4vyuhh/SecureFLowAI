import React from 'react';
import { CheckSquare, Activity, MessageSquare, ShieldAlert, Search, RefreshCw } from 'lucide-react';

export default function Header({ 
  currentView, 
  setView, 
  alertsCount = 0, 
  wsStatus = 'DISCONNECTED',
  onRefresh
}) {
  const tabs = [
    { id: 'dashboard', label: 'Check Box', icon: CheckSquare },
    { id: 'live', label: 'Monitoring', icon: Activity },
    { id: 'copilot', label: 'Support', icon: MessageSquare },
    { id: 'audit', label: 'Incidents', icon: ShieldAlert },
  ];

  return (
    <header className="h-20 bg-[#000000] px-8 flex items-center justify-between select-none shrink-0 border-b border-[#161619] sticky top-0 z-40">
      <div className="flex items-center gap-4">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = currentView === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setView(tab.id)}
              className={`h-11 px-5 rounded-full flex items-center gap-2.5 text-sm font-medium transition-all duration-300 cursor-pointer ${
                isActive 
                  ? 'bg-[#121316] border border-[#23252c] text-white shadow-sm' 
                  : 'text-[#8e8f96] hover:text-white hover:bg-[#0c0c0e]'
              }`}
            >
              <Icon className={`w-4.5 h-4.5 ${isActive ? 'text-[#8df85f]' : ''}`} />
              {tab.label}
            </button>
          );
        })}

        {/* Search trigger */}
        <div 
          onClick={() => setView('audit')} 
          className="flex items-center justify-center w-11 h-11 rounded-full bg-[#121316] border border-[#23252c] cursor-pointer hover:border-white transition-all duration-300"
          title="Search Forensic Audit Logs"
        >
          <Search className="w-4.5 h-4.5 text-[#8e8f96] hover:text-white" />
        </div>

        {/* Manual Refresh Button */}
        {onRefresh && (
          <button
            onClick={onRefresh}
            className="flex items-center justify-center w-11 h-11 rounded-full bg-[#121316] border border-[#23252c] cursor-pointer hover:border-white transition-all duration-300 text-[#8e8f96] hover:text-white"
            title="Refresh Real-Time Data"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        )}
      </div>

      <div className="flex items-center gap-5">
        {/* Real-Time WebSocket Telemetry Pill */}
        <div className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-full bg-[#0c0c0e] border border-[#161619] text-[11px] font-mono">
          <span className={`w-2 h-2 rounded-full ${wsStatus === 'CONNECTED' ? 'bg-[#8df85f] animate-pulse' : 'bg-[#f38933]'}`} />
          <span className="text-[#8e8f96]">Threat Stream:</span>
          <span className={wsStatus === 'CONNECTED' ? 'text-white font-semibold' : 'text-[#f38933]'}>
            {wsStatus === 'CONNECTED' ? 'LIVE' : wsStatus}
          </span>
        </div>

        <div className="text-right">
          <div className="text-sm font-semibold text-white">Security Officer</div>
          <div className="text-xs text-[#8e8f96]">@DLP_Admin</div>
        </div>

        <div className="relative cursor-pointer" onClick={() => setView('audit')}>
          <div className="w-11 h-11 rounded-full overflow-hidden border border-[#23252c] hover:border-white transition-all bg-gradient-to-tr from-[#f38933] to-[#8df85f] p-[2px]">
            <div className="w-full h-full bg-[#0c0c0e] rounded-full flex items-center justify-center font-bold text-xs text-white">
              SO
            </div>
          </div>
          {alertsCount > 0 && (
            <div className="absolute -top-1.5 -right-1.5 bg-[#f38933] text-black font-extrabold text-[10px] w-5 h-5 rounded-full flex items-center justify-center animate-bounce shadow-md">
              {alertsCount}
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
