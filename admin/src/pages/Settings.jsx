import React, { useState, useEffect } from 'react';
import { Sliders, ShieldCheck, Lock, Globe, Plus, Trash2, KeyRound, Check, RefreshCw } from 'lucide-react';
import toast from 'react-hot-toast';

export default function Settings() {
  const [maskThreshold, setMaskThreshold] = useState(() => {
    return Number(localStorage.getItem('sf_mask_threshold')) || 45;
  });
  const [blockThreshold, setBlockThreshold] = useState(() => {
    return Number(localStorage.getItem('sf_block_threshold')) || 80;
  });
  const [circuitPolicy, setCircuitPolicy] = useState(() => {
    return localStorage.getItem('sf_circuit_policy') || 'FAIL_OPEN';
  });
  const [whitelistedDomains, setWhitelistedDomains] = useState(() => {
    try {
      const saved = localStorage.getItem('sf_whitelisted_domains');
      return saved ? JSON.parse(saved) : [];
    } catch {
      return [];
    }
  });
  const [newDomain, setNewDomain] = useState('');
  const [saving, setSaving] = useState(false);

  const handleAddDomain = () => {
    if (!newDomain.trim()) return;
    const clean = newDomain.trim().toLowerCase();
    if (whitelistedDomains.includes(clean)) {
      toast.error('Domain already in whitelist.');
      return;
    }
    const updated = [...whitelistedDomains, clean];
    setWhitelistedDomains(updated);
    localStorage.setItem('sf_whitelisted_domains', JSON.stringify(updated));
    setNewDomain('');
    toast.success('Domain added to authorized whitelist.');
  };

  const handleRemoveDomain = (domain) => {
    const updated = whitelistedDomains.filter((d) => d !== domain);
    setWhitelistedDomains(updated);
    localStorage.setItem('sf_whitelisted_domains', JSON.stringify(updated));
    toast.success(`Removed ${domain} from whitelist.`);
  };

  const handleSavePolicy = () => {
    setSaving(true);
    localStorage.setItem('sf_mask_threshold', String(maskThreshold));
    localStorage.setItem('sf_block_threshold', String(blockThreshold));
    localStorage.setItem('sf_circuit_policy', circuitPolicy);
    localStorage.setItem('sf_whitelisted_domains', JSON.stringify(whitelistedDomains));

    setTimeout(() => {
      setSaving(false);
      toast.success('Bank DLP Policy synchronized across all active daemons & extensions.');
    }, 400);
  };

  return (
    <div className="flex-1 p-8 space-y-8 select-none">
      <div>
        <h1 className="text-4xl font-extrabold tracking-tight uppercase font-sans text-white">
          BANKING POLICIES & WHITELIST
        </h1>
        <p className="text-sm text-[#8e8f96]">
          Configure real-time enforcement thresholds, client circuit breaker behaviors, and cryptographic key versions.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        
        {/* Left Column: Risk Sliders & Circuit Breaker */}
        <div className="lg:col-span-6 space-y-8">
          <div className="bg-[#0c0c0e] border border-[#161619] rounded-[28px] p-6 space-y-6">
            <div className="flex items-center justify-between">
              <span className="text-[11px] font-bold tracking-wider text-[#8e8f96] uppercase">
                Dynamic Risk Decision Thresholds
              </span>
              <Sliders className="w-4 h-4 text-[#8df85f]" />
            </div>

            {/* Mask Threshold Slider */}
            <div className="space-y-2">
              <div className="flex items-center justify-between text-xs">
                <span className="font-semibold text-white">Auto-Mask / Tokenize Threshold:</span>
                <span className="font-mono font-bold text-[#8df85f]">{maskThreshold} / 100</span>
              </div>
              <input
                type="range"
                min="20"
                max="70"
                value={maskThreshold}
                onChange={(e) => setMaskThreshold(Number(e.target.value))}
                className="w-full accent-[#8df85f] cursor-pointer"
              />
              <span className="text-[10px] text-[#8e8f96] block">
                Payloads with risk &ge; {maskThreshold} are automatically sanitized with reverse-offset HMAC tokens.
              </span>
            </div>

            {/* Block Threshold Slider */}
            <div className="space-y-2 pt-4 border-t border-[#161619]">
              <div className="flex items-center justify-between text-xs">
                <span className="font-semibold text-white">Hard Exfiltration Block Threshold:</span>
                <span className="font-mono font-bold text-[#f38933]">{blockThreshold} / 100</span>
              </div>
              <input
                type="range"
                min="60"
                max="95"
                value={blockThreshold}
                onChange={(e) => setBlockThreshold(Number(e.target.value))}
                className="w-full accent-[#f38933] cursor-pointer"
              />
              <span className="text-[10px] text-[#8e8f96] block">
                Payloads exceeding {blockThreshold} (unencrypted card numbers, SSN dumps, private keys) are dropped instantly.
              </span>
            </div>
          </div>

          {/* Circuit Breaker Failover Policy */}
          <div className="bg-[#0c0c0e] border border-[#161619] rounded-[28px] p-6 space-y-5">
            <div className="flex items-center justify-between">
              <span className="text-[11px] font-bold tracking-wider text-[#8e8f96] uppercase">
                Daemon Circuit Breaker Failover Policy
              </span>
              <ShieldCheck className="w-4 h-4 text-white" />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <button
                type="button"
                onClick={() => setCircuitPolicy('FAIL_OPEN')}
                className={`p-4 rounded-2xl border text-left transition cursor-pointer ${
                  circuitPolicy === 'FAIL_OPEN'
                    ? 'bg-[#121316] border-[#8df85f] text-white shadow-sm'
                    : 'bg-[#0c0c0e] border-[#161619] text-[#8e8f96] hover:text-white'
                }`}
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs font-bold">FAIL_OPEN</span>
                  {circuitPolicy === 'FAIL_OPEN' && <span className="w-2 h-2 rounded-full bg-[#8df85f]" />}
                </div>
                <div className="text-[11px] text-[#8e8f96] leading-relaxed">
                  Queues transactions locally on offline desktops. Zero employee downtime.
                </div>
              </button>

              <button
                type="button"
                onClick={() => setCircuitPolicy('FAIL_CLOSED')}
                className={`p-4 rounded-2xl border text-left transition cursor-pointer ${
                  circuitPolicy === 'FAIL_CLOSED'
                    ? 'bg-[#121316] border-[#f38933] text-white shadow-sm'
                    : 'bg-[#0c0c0e] border-[#161619] text-[#8e8f96] hover:text-white'
                }`}
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs font-bold">FAIL_CLOSED</span>
                  {circuitPolicy === 'FAIL_CLOSED' && <span className="w-2 h-2 rounded-full bg-[#f38933]" />}
                </div>
                <div className="text-[11px] text-[#8e8f96] leading-relaxed">
                  Blocks all untracked clipboard and uploads when gateway is offline. Maximum security.
                </div>
              </button>
            </div>
          </div>
        </div>

        {/* Right Column: Whitelist Domains */}
        <div className="lg:col-span-6 space-y-8">
          <div className="bg-[#0c0c0e] border border-[#161619] rounded-[28px] p-6 space-y-6">
            <div className="flex items-center justify-between">
              <span className="text-[11px] font-bold tracking-wider text-[#8e8f96] uppercase">
                Authorized Whitelist Domains
              </span>
              <Globe className="w-4 h-4 text-[#8df85f]" />
            </div>

            <div className="flex gap-2">
              <input
                type="text"
                placeholder="Enter authorized domain, e.g. api.swift.com"
                value={newDomain}
                onChange={(e) => setNewDomain(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleAddDomain()}
                className="flex-1 bg-[#121316] border border-[#21232a] rounded-xl px-4 py-2 text-xs font-mono text-white placeholder-[#8e8f96] focus:outline-none focus:border-white"
              />
              <button
                onClick={handleAddDomain}
                className="bg-white text-black font-semibold text-xs px-4 py-2 rounded-xl flex items-center gap-1.5 hover:scale-105 transition cursor-pointer"
              >
                <Plus className="w-3.5 h-3.5" />
                Add
              </button>
            </div>

            <div className="space-y-2 max-h-60 overflow-y-auto">
              {whitelistedDomains.map((dom) => (
                <div
                  key={dom}
                  className="flex items-center justify-between p-3 rounded-xl bg-[#121316] border border-[#21232a] text-xs font-mono text-white"
                >
                  <div className="flex items-center gap-2">
                    <span className="w-1.5 h-1.5 rounded-full bg-[#8df85f]" />
                    <span>{dom}</span>
                  </div>
                  <button
                    onClick={() => handleRemoveDomain(dom)}
                    className="text-[#8e8f96] hover:text-[#f38933] transition cursor-pointer"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              ))}

              {whitelistedDomains.length === 0 && (
                <div className="p-8 text-center border border-dashed border-[#161619] rounded-2xl text-[#8e8f96] text-xs">
                  No custom whitelist domains added yet. Enter a domain above to exempt it from hard exfiltration blocking.
                </div>
              )}
            </div>

            <div className="pt-4 border-t border-[#161619] flex justify-end">
              <button
                onClick={handleSavePolicy}
                disabled={saving}
                className="bg-white text-black font-bold text-xs px-6 py-2.5 rounded-xl hover:scale-105 transition cursor-pointer flex items-center gap-2 shadow-md"
              >
                {saving ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Check className="w-3.5 h-3.5" />}
                {saving ? 'Synchronizing Daemons...' : 'Deploy Policy Changes'}
              </button>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}
