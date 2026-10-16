import React from 'react';
import { ShieldCheck, Bell, UserCheck, RefreshCw, Cpu } from 'lucide-react';

export default function Header({ currentView, setView, alertsCount = 0, healthData = null, onRefresh }) {
  const titles = {
    dashboard: 'CISO Executive Threat Dashboard',
    live: 'Real-Time Synchronous DLP Inspection',
    scanner: 'Multi-Format Banking Document Scanner',
    audit: 'Forensic Audit & Tokenized Vault Trail',
    copilot: 'Conversational SOC Analyst Copilot',
    policies: 'Dynamic Bank Policy & Whitelist Manager',
    health: 'Hardware Acceleration & Cryptographic Engine',
  };

  return (
    <header className="h-18 bg-[#07080a]/90 backdrop-blur-md border-b border-[#1c2436] px-8 flex items-center justify-between sticky top-0 z-40 select-none">
      <div>
        <h1 className="text-lg font-bold text-white font-heading tracking-tight flex items-center gap-2">
          {titles[currentView] || 'Banking DLP Control Center'}
        </h1>
        <div className="flex items-center gap-2 text-xs text-slate-400">
          <span>Tier-5 Governance Platform</span>
          <span>•</span>
          <span className="text-emerald-400 flex items-center gap-1 font-mono">
            <ShieldCheck className="w-3.5 h-3.5" /> PCI-DSS & GDPR Enforced
          </span>
        </div>
      </div>

      <div className="flex items-center gap-4">
        {/* Hardware & Latency Pill */}
        <div className="hidden lg:flex items-center gap-3 bg-[#0d111a] border border-[#1e2638] px-3.5 py-1.5 rounded-xl text-xs">
          <div className="flex items-center gap-1.5 text-slate-300">
            <Cpu className="w-3.5 h-3.5 text-blue-400" />
            <span className="font-mono text-[11px]">
              {healthData?.active_model || 'ONNX INT8 Transformer'}
            </span>
          </div>
          <span className="text-slate-600">|</span>
          <span className="font-mono text-emerald-400 text-[11px]">
            Avg: 11.2ms
          </span>
        </div>

        {/* Refresh button */}
        {onRefresh && (
          <button
            onClick={onRefresh}
            className="p-2 rounded-xl bg-[#0d111a] border border-[#1e2638] text-slate-400 hover:text-white hover:bg-[#161d2d] transition cursor-pointer"
            title="Refresh Metrics"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        )}

        {/* Alert Bell */}
        <div className="relative cursor-pointer" onClick={() => setView('audit')}>
          <div className="p-2 rounded-xl bg-[#0d111a] border border-[#1e2638] text-slate-400 hover:text-white hover:bg-[#161d2d] transition">
            <Bell className="w-4 h-4" />
          </div>
          {alertsCount > 0 && (
            <span className="absolute -top-1 -right-1 w-4 h-4 rounded-full bg-red-500 text-[10px] font-bold text-white flex items-center justify-center animate-pulse">
              {alertsCount}
            </span>
          )}
        </div>

        {/* User Badge */}
        <div className="flex items-center gap-2.5 pl-2 border-l border-[#1c2436]">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-slate-800 to-slate-700 border border-slate-600 flex items-center justify-center font-bold text-xs text-white">
            <UserCheck className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="hidden md:block text-left">
            <div className="text-xs font-semibold text-white">Chief Security Officer</div>
            <div className="text-[10px] text-slate-400 font-mono">ciso@bankcorp.internal</div>
          </div>
        </div>
      </div>
    </header>
  );
}
