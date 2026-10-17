import React from 'react';
import { 
  FileClock, 
  Settings, 
  LayoutDashboard, 
  BrainCircuit, 
  ShieldAlert as ScannerIcon, 
  Sparkles,
  Activity
} from 'lucide-react';

export default function Sidebar({ currentView, setView, alertsCount = 0, wsStatus = 'CONNECTED' }) {
  const menuItems = [
    { id: 'dashboard', icon: LayoutDashboard, label: 'Dashboard' },
    { id: 'live', icon: BrainCircuit, label: 'Live Classification' },
    { id: 'scanner', icon: ScannerIcon, label: 'File Scanner' },
    { id: 'audit', icon: FileClock, label: 'Audit Logs', badge: alertsCount },
    { id: 'copilot', icon: Sparkles, label: 'AI Copilot' },
    { id: 'health', icon: Activity, label: 'Engine Health' },
    { id: 'policies', icon: Settings, label: 'Policy Manager' },
  ];

  const isWsLive = wsStatus === 'OPEN' || wsStatus === 'CONNECTED';

  return (
    <aside className="w-20 bg-[#070708] border-r border-[#161619] flex flex-col items-center py-6 justify-between select-none shrink-0 h-[calc(100vh-5rem)] sticky top-20">
      <div className="flex flex-col items-center gap-6 w-full pt-2">
        {/* Navigation Items */}
        <nav className="flex flex-col gap-5 w-full px-2">
          {menuItems.map((item) => {
            const Icon = item.icon;
            const isActive = currentView === item.id;
            return (
              <div key={item.id} className="relative group flex justify-center">
                <button
                  onClick={() => setView(item.id)}
                  className={`w-12 h-12 rounded-2xl flex items-center justify-center transition-all duration-300 ${
                    isActive 
                      ? 'bg-white text-black shadow-lg scale-105' 
                      : 'text-[#8e8f96] hover:bg-[#121316] hover:text-white'
                  }`}
                  title={item.label}
                >
                  <Icon className="w-5 h-5" />
                </button>
                {/* Alert badge */}
                {item.badge > 0 && (
                  <span className="absolute top-0 right-1.5 w-4 h-4 rounded-full bg-red-500 text-[9px] font-bold text-white flex items-center justify-center animate-pulse z-10">
                    {item.badge > 9 ? '9+' : item.badge}
                  </span>
                )}
                <div className="absolute left-20 top-3 px-3 py-1.5 rounded-lg bg-black border border-[#1e2025] text-xs text-white opacity-0 pointer-events-none group-hover:opacity-100 transition-opacity duration-200 z-50 whitespace-nowrap font-medium">
                  {item.label}
                </div>
              </div>
            );
          })}
        </nav>
      </div>
    </aside>
  );
}
