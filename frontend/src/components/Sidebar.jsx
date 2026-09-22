import React from 'react';
import { Heart, FileClock, ShieldAlert, Settings, Plus, LayoutDashboard, BrainCircuit, ShieldAlert as ScannerIcon } from 'lucide-react';

export default function Sidebar({ currentView, setView }) {
  const menuItems = [
    { id: 'dashboard', icon: LayoutDashboard, label: 'Dashboard' },
    { id: 'live', icon: BrainCircuit, label: 'Live Classification' },
    { id: 'scanner', icon: ScannerIcon, label: 'File Scanner' },
    { id: 'audit', icon: FileClock, label: 'Audit Logs' },
    { id: 'settings', icon: Settings, label: 'Settings' }
  ];

  return (
    <aside className="w-20 bg-[#070708] border-r border-[#161619] flex flex-col items-center py-6 justify-between select-none shrink-0 h-screen sticky top-0">
      <div className="flex flex-col items-center gap-10 w-full">
        <div className="w-12 h-12 rounded-full bg-white flex items-center justify-center cursor-pointer hover:scale-105 transition-transform duration-200 shadow-[0_0_15px_rgba(255,255,255,0.2)]">
          <span className="text-black font-extrabold text-lg font-mono">SF</span>
        </div>

        <nav className="flex flex-col gap-6 w-full px-2">
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
                  <Icon className="w-5.5 h-5.5" />
                </button>
                <div className="absolute left-20 top-3 px-3 py-1.5 rounded-lg bg-black border border-[#1e2025] text-xs text-white opacity-0 pointer-events-none group-hover:opacity-100 transition-opacity duration-200 z-50 whitespace-nowrap font-medium">
                  {item.label}
                </div>
              </div>
            );
          })}
        </nav>
      </div>

      <button 
        onClick={() => setView('scanner')}
        className="w-12 h-12 rounded-2xl bg-[#121316] border border-[#21232a] flex items-center justify-center text-white hover:border-white hover:scale-105 transition-all duration-300 shadow-md cursor-pointer"
        title="Quick Scan File"
      >
        <Plus className="w-6 h-6" />
      </button>
    </aside>
  );
}
