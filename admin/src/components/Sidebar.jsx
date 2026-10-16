import React from 'react';
import {
  LayoutDashboard,
  BrainCircuit,
  UploadCloud,
  ShieldAlert,
  Bot,
  Sliders,
  Activity,
  Shield
} from 'lucide-react';

export default function Sidebar({ currentView, setView, alertsCount = 0, wsStatus = 'DISCONNECTED' }) {
  const menuItems = [
    { id: 'dashboard', icon: LayoutDashboard, label: 'Executive Dashboard' },
    { id: 'live', icon: BrainCircuit, label: 'Live DLP Inspection' },
    { id: 'scanner', icon: UploadCloud, label: 'Document & File Scanner' },
    { id: 'audit', icon: ShieldAlert, label: 'Incident & Forensic Audit', badge: alertsCount },
    { id: 'copilot', icon: Bot, label: 'Analyst Copilot' },
    { id: 'policies', icon: Sliders, label: 'Policy & Governance' },
    { id: 'health', icon: Activity, label: 'Engine & Cryptography' },
  ];

  return (
    <aside className="w-64 bg-[#07080a] border-r border-[#1c2436] flex flex-col justify-between py-6 select-none shrink-0 h-screen sticky top-0">
      <div className="flex flex-col gap-6">
        {/* Bank Brand Header */}
        <div className="px-6 flex items-center gap-3 cursor-pointer" onClick={() => setView('dashboard')}>
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 via-indigo-500 to-cyan-400 flex items-center justify-center shadow-lg shadow-blue-500/20">
            <Shield className="w-6 h-6 text-white" />
          </div>
          <div>
            <div className="text-base font-extrabold tracking-tight text-white font-heading">
              SecureFlow<span className="text-blue-500 font-mono">AI</span>
            </div>
            <div className="text-[10px] uppercase tracking-wider text-slate-400 font-mono">
              Enterprise Banking DLP
            </div>
          </div>
        </div>

        {/* Live Stream Pulse Badge */}
        <div className="mx-6 px-3 py-2 rounded-xl bg-[#0d111a] border border-[#1e2638] flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className={`w-2.5 h-2.5 rounded-full ${wsStatus === 'CONNECTED' ? 'bg-emerald-500 animate-pulse' : 'bg-amber-500'}`} />
            <span className="text-xs font-semibold text-slate-300">
              {wsStatus === 'CONNECTED' ? 'Threat Bus: Live' : 'Threat Bus: Polling'}
            </span>
          </div>
          <span className="text-[10px] font-mono text-slate-400 bg-[#161d2d] px-2 py-0.5 rounded">
            P95 &lt; 25ms
          </span>
        </div>

        {/* Navigation Items */}
        <nav className="flex flex-col gap-1 px-3">
          {menuItems.map((item) => {
            const Icon = item.icon;
            const isActive = currentView === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setView(item.id)}
                className={`w-full flex items-center justify-between px-3.5 py-3 rounded-xl text-xs font-medium transition-all duration-200 cursor-pointer ${
                  isActive
                    ? 'bg-blue-600/15 text-blue-400 border border-blue-500/30 shadow-sm'
                    : 'text-slate-400 hover:bg-[#0e1320] hover:text-slate-200'
                }`}
              >
                <div className="flex items-center gap-3">
                  <Icon className={`w-4.5 h-4.5 ${isActive ? 'text-blue-400' : 'text-slate-400'}`} />
                  <span className="tracking-wide">{item.label}</span>
                </div>
                {item.badge > 0 && (
                  <span className="px-2 py-0.5 text-[10px] font-bold rounded-full bg-red-500/20 text-red-400 border border-red-500/30">
                    {item.badge}
                  </span>
                )}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Security Department Card */}
      <div className="px-6">
        <div className="p-3.5 rounded-2xl bg-[#0d111a] border border-[#1e2638] space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-semibold text-slate-300">SOC Perimeter</span>
            <span className="text-[10px] font-mono text-emerald-400 bg-emerald-500/10 px-1.5 py-0.5 rounded">
              Air-Gapped
            </span>
          </div>
          <div className="text-[10px] text-slate-400 leading-relaxed">
            Models, parsers, and token vault operating with 0% external cloud egress.
          </div>
        </div>
      </div>
    </aside>
  );
}
