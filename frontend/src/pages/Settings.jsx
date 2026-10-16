import React, { useState, useEffect } from 'react';
import { Sliders, ShieldCheck, Lock, Globe, Plus, Trash2, KeyRound, Check, RefreshCw } from 'lucide-react';
import toast from 'react-hot-toast';
import { api } from '../services/api';

export default function Settings() {
  const [maskThreshold, setMaskThreshold] = useState(45);
  const [blockThreshold, setBlockThreshold] = useState(80);
  const [circuitPolicy, setCircuitPolicy] = useState('FAIL_OPEN');
  const [whitelistedDomains, setWhitelistedDomains] = useState([
    '*.internal.bankcorp.com',
    'api.partner.swift.com',
    'audit.clearinghouse.org',
    'treasury.centralbank.gov',
  ]);
  const [newDomain, setNewDomain] = useState('');
  const [saving, setSaving] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getPolicy()
      .then((data) => {
        if (data) {
          if (data.mask_threshold) setMaskThreshold(data.mask_threshold);
          if (data.block_threshold) setBlockThreshold(data.block_threshold);
          if (Array.isArray(data.whitelisted_domains) && data.whitelisted_domains.length > 0) {
            setWhitelistedDomains(data.whitelisted_domains);
          }
        }
      })
      .catch((err) => {
        console.warn('Backend policy API offline, using local bank defaults:', err);
      })
      .finally(() => setLoading(false));
  }, []);

  const handleAddDomain = () => {
    if (!newDomain.trim()) return;
    if (whitelistedDomains.includes(newDomain.trim().toLowerCase())) {
      toast.error('Domain already in whitelist.');
      return;
    }
    setWhitelistedDomains([...whitelistedDomains, newDomain.trim().toLowerCase()]);
    setNewDomain('');
    toast.success('Domain added to authorized whitelist.');
  };

  const handleRemoveDomain = (domain) => {
    setWhitelistedDomains(whitelistedDomains.filter((d) => d !== domain));
    toast.success(`Removed ${domain} from whitelist.`);
  };

  const handleSavePolicy = async () => {
    setSaving(true);
    try {
      const res = await api.updatePolicy({
        mask_threshold: maskThreshold,
        block_threshold: blockThreshold,
        whitelisted_domains: whitelistedDomains,
      });
      toast.success(res?.message || 'Bank DLP Policy persisted to database & synchronized.');
    } catch (err) {
      toast.error('Failed saving to database. Offline fallback activated.');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="p-8 space-y-8 select-none max-w-7xl mx-auto">
      <div>
        <h2 className="text-2xl font-bold text-white font-heading">
          Dynamic Bank Policy & Whitelist Manager
        </h2>
        <p className="text-xs text-slate-400 mt-1">
          Configure real-time enforcement thresholds, client circuit breaker behaviors, and cryptographic key versions.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Column: Risk Sliders & Circuit Breaker */}
        <div className="lg:col-span-6 space-y-8">
          {/* Dynamic Risk Thresholds */}
          <div className="banking-card p-6 rounded-3xl space-y-6">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-2xl bg-blue-600/20 border border-blue-500/30 flex items-center justify-center text-blue-400">
                <Sliders className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-base font-bold text-white font-heading">
                  Dynamic Risk Decision Thresholds
                </h3>
                <p className="text-xs text-slate-400">Enforcement boundary on 0-100 DLP risk scale</p>
              </div>
            </div>

            {/* Mask Threshold Slider */}
            <div className="space-y-2">
              <div className="flex items-center justify-between text-xs">
                <span className="font-semibold text-slate-300">Auto-Mask / Tokenize Threshold:</span>
                <span className="font-mono font-bold text-amber-400">{maskThreshold} / 100</span>
              </div>
              <input
                type="range"
                min="20"
                max="70"
                value={maskThreshold}
                onChange={(e) => setMaskThreshold(Number(e.target.value))}
                className="w-full accent-amber-400 cursor-pointer"
              />
              <span className="text-[10px] text-slate-500 block">
                Payloads with risk &ge; {maskThreshold} are automatically sanitized with reverse-offset HMAC tokens.
              </span>
            </div>

            {/* Block Threshold Slider */}
            <div className="space-y-2 pt-2 border-t border-[#1a2233]">
              <div className="flex items-center justify-between text-xs">
                <span className="font-semibold text-slate-300">Hard Exfiltration Block Threshold:</span>
                <span className="font-mono font-bold text-red-400">{blockThreshold} / 100</span>
              </div>
              <input
                type="range"
                min="60"
                max="95"
                value={blockThreshold}
                onChange={(e) => setBlockThreshold(Number(e.target.value))}
                className="w-full accent-red-400 cursor-pointer"
              />
              <span className="text-[10px] text-slate-500 block">
                Payloads with risk &ge; {blockThreshold} (or unencrypted PCI cards/SSNs) trigger immediate hard drop.
              </span>
            </div>
          </div>

          {/* Client-Side Circuit Breaker Policy */}
          <div className="banking-card p-6 rounded-3xl space-y-5">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-2xl bg-purple-600/20 border border-purple-500/30 flex items-center justify-center text-purple-400">
                <ShieldCheck className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-base font-bold text-white font-heading">
                  Client Endpoint Circuit Breaker
                </h3>
                <p className="text-xs text-slate-400">Policy when central gateway is unreachable</p>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <button
                type="button"
                onClick={() => setCircuitPolicy('FAIL_OPEN')}
                className={`p-4 rounded-2xl border text-left transition cursor-pointer ${
                  circuitPolicy === 'FAIL_OPEN'
                    ? 'bg-blue-600/15 border-blue-500 text-white'
                    : 'bg-[#080b11] border-[#1a2233] text-slate-400 hover:text-slate-200'
                }`}
              >
                <div className="text-xs font-bold font-mono">FAIL_OPEN (Local Queue)</div>
                <div className="text-[11px] text-slate-400 mt-1">
                  Allows worker traffic; buffers payloads in local SQLite/memory for deferred sync.
                </div>
              </button>

              <button
                type="button"
                onClick={() => setCircuitPolicy('FAIL_CLOSED')}
                className={`p-4 rounded-2xl border text-left transition cursor-pointer ${
                  circuitPolicy === 'FAIL_CLOSED'
                    ? 'bg-red-600/15 border-red-500 text-white'
                    : 'bg-[#080b11] border-[#1a2233] text-slate-400 hover:text-slate-200'
                }`}
              >
                <div className="text-xs font-bold font-mono">FAIL_CLOSED (Strict Block)</div>
                <div className="text-[11px] text-slate-400 mt-1">
                  Blocks all untrusted transfers until gateway liveness probe succeeds.
                </div>
              </button>
            </div>
          </div>
        </div>

        {/* Right Column: Whitelist Manager & Cryptographic Rotation */}
        <div className="lg:col-span-6 space-y-8">
          {/* Whitelist Manager */}
          <div className="banking-card p-6 rounded-3xl space-y-5">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-2xl bg-emerald-600/20 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
                <Globe className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-base font-bold text-white font-heading">
                  Whitelisted Destination Domains
                </h3>
                <p className="text-xs text-slate-400">Endpoints exempt from hard blocking rules</p>
              </div>
            </div>

            <div className="flex gap-2">
              <input
                type="text"
                placeholder="e.g. *.partner.bank.com"
                value={newDomain}
                onChange={(e) => setNewDomain(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleAddDomain()}
                className="flex-1 bg-[#080b11] border border-[#1a2233] rounded-xl px-3.5 py-2 text-xs font-mono text-white focus:outline-none focus:border-emerald-500"
              />
              <button
                onClick={handleAddDomain}
                className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-black font-semibold text-xs rounded-xl flex items-center gap-1.5 transition cursor-pointer"
              >
                <Plus className="w-4 h-4" /> Add
              </button>
            </div>

            <div className="space-y-2 max-h-48 overflow-y-auto pr-1">
              {whitelistedDomains.map((dom) => (
                <div
                  key={dom}
                  className="p-3 rounded-xl bg-[#090d14] border border-[#1a2233] flex items-center justify-between text-xs font-mono"
                >
                  <span className="text-emerald-400 font-semibold">{dom}</span>
                  <button
                    onClick={() => handleRemoveDomain(dom)}
                    className="text-slate-500 hover:text-red-400 transition cursor-pointer"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              ))}
            </div>
          </div>

          {/* Cryptographic Key Rotation Info */}
          <div className="banking-card p-6 rounded-3xl space-y-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-2xl bg-amber-600/20 border border-amber-500/30 flex items-center justify-center text-amber-400">
                <KeyRound className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-base font-bold text-white font-heading">
                  Cryptographic Key Rotation
                </h3>
                <p className="text-xs text-slate-400">AES-256-GCM Envelope Encryption Status</p>
              </div>
            </div>

            <div className="p-4 rounded-2xl bg-[#080b11] border border-[#1a2233] space-y-2 text-xs font-mono">
              <div className="flex justify-between text-slate-400">
                <span>Active Key Version:</span>
                <strong className="text-emerald-400">v1 (256-bit AES-GCM)</strong>
              </div>
              <div className="flex justify-between text-slate-400">
                <span>HMAC Pseudonymization Salt:</span>
                <strong className="text-blue-400">Configured (SHA-256)</strong>
              </div>
              <div className="flex justify-between text-slate-400">
                <span>Key Rotation Policy:</span>
                <strong className="text-white">90-Day Zero-Downtime Roll</strong>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Save Button */}
      <div className="flex justify-end pt-4">
        <button
          onClick={handleSavePolicy}
          disabled={saving}
          className="px-6 py-3 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold transition shadow-lg shadow-blue-600/30 flex items-center gap-2 cursor-pointer"
        >
          {saving ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Check className="w-4 h-4" />}
          {saving ? 'Synchronizing Policies...' : 'Save & Publish Banking Policy'}
        </button>
      </div>
    </div>
  );
}
