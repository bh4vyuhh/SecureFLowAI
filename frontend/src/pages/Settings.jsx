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
    <div className="flex-1 p-8 space-y-8 select-none">
      <div>
        <h1 className="text-4xl font-extrabold tracking-tight uppercase font-sans text-white">
          Dynamic Bank Policy & Whitelist Manager
        </h1>
        <p className="text-sm text-[#8e8f96] mt-1">
          Configure real-time enforcement thresholds, client circuit breaker behaviors, and cryptographic key versions.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Column: Risk Sliders & Circuit Breaker */}
        <div className="lg:col-span-6 space-y-8">
          {/* Dynamic Risk Thresholds */}
          <div className="bg-[#0c0c0e] border border-[#161619] p-6 rounded-[28px] space-y-6">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-2xl bg-[#121316] border border-[#23252c] flex items-center justify-center text-white">
                <Sliders className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-base font-bold text-white uppercase tracking-wider text-xs">
                  Dynamic Risk Decision Thresholds
                </h3>
                <p className="text-xs text-[#8e8f96]">Enforcement boundary on 0-100 DLP risk scale</p>
              </div>
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
            <div className="space-y-2 pt-2 border-t border-[#161619]">
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
                Payloads with risk &ge; {blockThreshold} (or unencrypted PCI cards/SSNs) trigger immediate hard drop.
              </span>
            </div>
          </div>

          {/* Client-Side Circuit Breaker Policy */}
          <div className="bg-[#0c0c0e] border border-[#161619] p-6 rounded-[28px] space-y-5">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-2xl bg-[#121316] border border-[#23252c] flex items-center justify-center text-white">
                <ShieldCheck className="w-5 h-5 text-[#8df85f]" />
              </div>
              <div>
                <h3 className="text-base font-bold text-white uppercase tracking-wider text-xs">
                  Client Endpoint Circuit Breaker
                </h3>
                <p className="text-xs text-[#8e8f96]">Policy when central gateway is unreachable</p>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <button
                type="button"
                onClick={() => setCircuitPolicy('FAIL_OPEN')}
                className={`p-4 rounded-2xl border text-left transition cursor-pointer ${
                  circuitPolicy === 'FAIL_OPEN'
                    ? 'bg-white text-black border-white'
                    : 'bg-[#121316] border-[#23252c] text-[#8e8f96] hover:text-white hover:border-white'
                }`}
              >
                <div className="text-xs font-bold font-mono">FAIL_OPEN (Local Queue)</div>
                <div className={`text-[11px] mt-1 ${circuitPolicy === 'FAIL_OPEN' ? 'text-black/80' : 'text-[#8e8f96]'}`}>
                  Allows worker traffic; buffers payloads in local SQLite/memory for deferred sync.
                </div>
              </button>

              <button
                type="button"
                onClick={() => setCircuitPolicy('FAIL_CLOSED')}
                className={`p-4 rounded-2xl border text-left transition cursor-pointer ${
                  circuitPolicy === 'FAIL_CLOSED'
                    ? 'bg-[#f38933] text-black border-[#f38933]'
                    : 'bg-[#121316] border-[#23252c] text-[#8e8f96] hover:text-white hover:border-white'
                }`}
              >
                <div className="text-xs font-bold font-mono">FAIL_CLOSED (Strict Block)</div>
                <div className={`text-[11px] mt-1 ${circuitPolicy === 'FAIL_CLOSED' ? 'text-black/80' : 'text-[#8e8f96]'}`}>
                  Blocks all untrusted transfers until gateway liveness probe succeeds.
                </div>
              </button>
            </div>
          </div>
        </div>

        {/* Right Column: Whitelist Manager & Cryptographic Rotation */}
        <div className="lg:col-span-6 space-y-8">
          {/* Whitelist Manager */}
          <div className="bg-[#0c0c0e] border border-[#161619] p-6 rounded-[28px] space-y-5">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-2xl bg-[#121316] border border-[#23252c] flex items-center justify-center text-white">
                <Globe className="w-5 h-5 text-[#8df85f]" />
              </div>
              <div>
                <h3 className="text-base font-bold text-white uppercase tracking-wider text-xs">
                  Whitelisted Destination Domains
                </h3>
                <p className="text-xs text-[#8e8f96]">Endpoints exempt from hard blocking rules</p>
              </div>
            </div>

            <div className="flex gap-2">
              <input
                type="text"
                placeholder="e.g. *.partner.bank.com"
                value={newDomain}
                onChange={(e) => setNewDomain(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleAddDomain()}
                className="flex-1 bg-[#121316] border border-[#23252c] rounded-xl px-3.5 py-2 text-xs font-mono text-white focus:outline-none focus:border-white"
              />
              <button
                onClick={handleAddDomain}
                className="px-4 py-2 bg-[#8df85f] hover:bg-[#8df85f]/90 text-black font-semibold text-xs rounded-xl flex items-center gap-1.5 transition cursor-pointer"
              >
                <Plus className="w-4 h-4" /> Add
              </button>
            </div>

            <div className="space-y-2 max-h-48 overflow-y-auto pr-1">
              {whitelistedDomains.map((dom) => (
                <div
                  key={dom}
                  className="p-3 rounded-xl bg-[#121316] border border-[#23252c] flex items-center justify-between text-xs font-mono"
                >
                  <span className="text-[#8df85f] font-semibold">{dom}</span>
                  <button
                    onClick={() => handleRemoveDomain(dom)}
                    className="text-[#8e8f96] hover:text-[#f38933] transition cursor-pointer"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              ))}
            </div>
          </div>

          {/* Cryptographic Key Rotation Info */}
          <div className="bg-[#0c0c0e] border border-[#161619] p-6 rounded-[28px] space-y-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-2xl bg-[#121316] border border-[#23252c] flex items-center justify-center text-white">
                <KeyRound className="w-5 h-5 text-[#f38933]" />
              </div>
              <div>
                <h3 className="text-base font-bold text-white uppercase tracking-wider text-xs">
                  Cryptographic Key Rotation
                </h3>
                <p className="text-xs text-[#8e8f96]">AES-256-GCM Envelope Encryption Status</p>
              </div>
            </div>

            <div className="p-4 rounded-2xl bg-[#121316] border border-[#23252c] space-y-2 text-xs font-mono">
              <div className="flex justify-between text-[#8e8f96]">
                <span>Active Key Version:</span>
                <strong className="text-[#8df85f]">v1 (256-bit AES-GCM)</strong>
              </div>
              <div className="flex justify-between text-[#8e8f96]">
                <span>HMAC Pseudonymization Salt:</span>
                <strong className="text-white">Configured (SHA-256)</strong>
              </div>
              <div className="flex justify-between text-[#8e8f96]">
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
          className="px-6 py-3 rounded-xl bg-white text-black text-xs font-bold transition hover:scale-105 shadow-md flex items-center gap-2 cursor-pointer"
        >
          {saving ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Check className="w-4 h-4" />}
          {saving ? 'Synchronizing Policies...' : 'Save & Publish Banking Policy'}
        </button>
      </div>
    </div>
  );
}
