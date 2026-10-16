import React from 'react';
import { UserCheck } from 'lucide-react';

export default function Header({ setView }) {
  return (
    <header className="h-20 bg-[#07080a] border-b border-[#1c2436] px-6 flex items-center justify-between sticky top-0 z-50 select-none shrink-0 w-full">
      {/* Leftmost Area: SecureFlow AI brand */}
      <div 
        onClick={() => setView && setView('dashboard')}
        className="flex items-center gap-3.5 cursor-pointer group"
      >
        <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-600 flex items-center justify-center font-extrabold text-white text-sm font-mono shadow-md shadow-blue-600/30 group-hover:scale-105 transition-transform">
          SF
        </div>
        <div className="flex items-baseline gap-2">
          <span className="text-xl font-bold text-white tracking-tight font-heading">
            SecureFlow <span className="text-blue-500">AI</span>
          </span>
          <span className="hidden sm:inline-block text-[11px] font-mono text-slate-500 uppercase tracking-wider">
            | Banking DLP
          </span>
        </div>
      </div>

      {/* Rightmost Area: Profile Section */}
      <div className="flex items-center gap-3.5">
        <div className="hidden md:flex flex-col text-right">
          <span className="text-xs font-semibold text-white">Chief Information Security Officer</span>
          <span className="text-[11px] text-slate-500 font-mono">ciso@bankcorp.internal</span>
        </div>
        <div 
          className="w-10 h-10 rounded-xl bg-[#0f1420] border border-[#232f48] flex items-center justify-center font-bold text-white cursor-pointer hover:border-blue-500 transition-colors shadow-sm"
          title="Chief Security Officer"
        >
          <UserCheck className="w-4.5 h-4.5 text-cyan-400" />
        </div>
      </div>
    </header>
  );
}
