import React, { useState, useEffect } from 'react';
import {
  Download,
  Search,
  Filter,
  ShieldAlert,
  ShieldCheck,
  Lock,
  Key,
  Eye,
  CheckCircle,
  X,
  RefreshCw,
  ExternalLink,
} from 'lucide-react';
import toast from 'react-hot-toast';
import { api } from '../services/api';

export default function AuditLogsView({ logs = [], setLogs }) {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterAction, setFilterAction] = useState('All');
  const [filterDepartment, setFilterDepartment] = useState('All');
  const [selectedIncident, setSelectedIncident] = useState(null);

  // Detokenization Modal State
  const [detokenizeModalOpen, setDetokenizeModalOpen] = useState(false);
  const [tokenInput, setTokenInput] = useState('');
  const [authKeyInput, setAuthKeyInput] = useState('bank-soc-super-secret-key-2026');
  const [detokenizedResult, setDetokenizedResult] = useState(null);
  const [detokenizing, setDetokenizing] = useState(false);

  useEffect(() => {
    // Attempt fetching live incidents from PostgreSQL API
    api.getIncidents({ limit: 50 })
      .then((records) => {
        if (Array.isArray(records) && records.length > 0) {
          setLogs(records);
        }
      })
      .catch((err) => {
        console.warn('Backend audit API offline; using local state logs:', err);
      });
  }, []);

  const handleExportCSV = () => {
    const headers = [
      'Incident ID',
      'Timestamp',
      'User ID',
      'Department',
      'Destination Domain',
      'Classification Tier',
      'Risk Score',
      'Enforcement Action',
      'Payload SHA-256',
    ];

    const rows = logs.map((l) => [
      l.id,
      l.timestamp,
      `"${l.user_id || 'anonymous'}"`,
      `"${l.department || 'general'}"`,
      `"${l.destination_domain || 'internal'}"`,
      l.classification_tier,
      l.risk_score,
      l.enforcement_action,
      `"${l.payload_sha256}"`,
    ]);

    const csvContent = [headers.join(','), ...rows.map((r) => r.join(','))].join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `secureflow_forensic_audit_${new Date().toISOString().slice(0, 10)}.csv`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    toast.success('Forensic audit log exported to CSV.');
  };

  const handleOpenDetokenize = (incident = null) => {
    setSelectedIncident(incident);
    setDetokenizedResult(null);
    setTokenInput(
      incident?.token || 'TOK_CREDIT_CARD_4a8b1c9e2f3d5a6b'
    );
    setDetokenizeModalOpen(true);
  };

  const executeDetokenization = async () => {
    if (!tokenInput.trim() || !authKeyInput.trim()) {
      toast.error('Token and SOC authorization key are required.');
      return;
    }
    setDetokenizing(true);
    setDetokenizedResult(null);

    try {
      const res = await api.detokenize(tokenInput.trim(), authKeyInput.trim());
      setDetokenizedResult(res);
      toast.success('Cryptographic detokenization authorized.');
    } catch (err) {
      // Offline fallback demonstration
      if (authKeyInput === 'bank-soc-super-secret-key-2026') {
        setTimeout(() => {
          setDetokenizedResult({
            token: tokenInput,
            plaintext_value: '4530-8921-0043-9182',
            entity_type: 'CREDIT_CARD',
            key_version: 'v1',
          });
          toast.success('Cryptographic detokenization authorized.');
          setDetokenizing(false);
        }, 300);
      } else {
        toast.error('Invalid SOC authorization key (403 Forbidden).');
        setDetokenizing(false);
      }
    } finally {
      setDetokenizing(false);
    }
  };

  const filteredLogs = logs.filter((log) => {
    const matchAction = filterAction === 'All' || log.enforcement_action === filterAction;
    const matchDept = filterDepartment === 'All' || log.department === filterDepartment;
    const q = searchTerm.toLowerCase();
    const matchSearch =
      (log.id && log.id.toLowerCase().includes(q)) ||
      (log.user_id && log.user_id.toLowerCase().includes(q)) ||
      (log.destination_domain && log.destination_domain.toLowerCase().includes(q)) ||
      (log.payload_sha256 && log.payload_sha256.toLowerCase().includes(q));
    return matchAction && matchDept && matchSearch;
  });

  return (
    <div className="p-8 space-y-8 select-none max-w-7xl mx-auto">
      {/* Header & Controls */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-white font-heading">
            Incident Triage & Forensic Audit Trail
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Non-repudiable zero-leak audit repository. Plaintext customer PII is never stored in logs; only cryptographic SHA-256 fingerprints are retained.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => handleOpenDetokenize()}
            className="px-4 py-2.5 rounded-xl bg-[#161d2d] border border-[#232f48] text-amber-400 hover:text-amber-300 text-xs font-semibold flex items-center gap-2 transition cursor-pointer"
          >
            <Key className="w-4 h-4" />
            Authorized Detokenizer
          </button>
          <button
            onClick={handleExportCSV}
            className="px-4 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold flex items-center gap-2 transition shadow-lg shadow-blue-600/30 cursor-pointer"
          >
            <Download className="w-4 h-4" />
            Export CSV
          </button>
        </div>
      </div>

      {/* Filter Toolbar */}
      <div className="banking-card p-5 rounded-2xl flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-3 flex-1 min-w-[280px]">
          <div className="relative flex-1">
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
            <input
              type="text"
              placeholder="Search by User, Domain, Incident ID, or SHA-256..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full bg-[#080b11] border border-[#1a2233] rounded-xl pl-10 pr-4 py-2 text-xs font-mono text-white focus:outline-none focus:border-blue-500"
            />
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 text-xs text-slate-400">
            <Filter className="w-3.5 h-3.5" /> Action:
            <select
              value={filterAction}
              onChange={(e) => setFilterAction(e.target.value)}
              className="bg-[#080b11] border border-[#1a2233] rounded-xl px-3 py-1.5 text-xs text-white focus:outline-none cursor-pointer"
            >
              <option value="All">All Actions</option>
              <option value="BLOCK">BLOCK</option>
              <option value="MASK">MASK / ENCRYPT</option>
              <option value="ALLOW">ALLOW</option>
            </select>
          </div>

          <div className="flex items-center gap-2 text-xs text-slate-400">
            Department:
            <select
              value={filterDepartment}
              onChange={(e) => setFilterDepartment(e.target.value)}
              className="bg-[#080b11] border border-[#1a2233] rounded-xl px-3 py-1.5 text-xs text-white focus:outline-none cursor-pointer"
            >
              <option value="All">All Departments</option>
              <option value="Investment Banking">Investment Banking</option>
              <option value="Treasury & Liquidity">Treasury & Liquidity</option>
              <option value="Wealth Management">Wealth Management</option>
              <option value="Retail Banking">Retail Banking</option>
            </select>
          </div>
        </div>
      </div>

      {/* Incident Audit Table */}
      <div className="banking-card rounded-3xl overflow-hidden border border-[#1c2436]">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-[#1c2436] bg-[#090d14] text-[11px] font-bold text-slate-400 uppercase tracking-wider">
                <th className="py-3.5 px-5">Incident / Time</th>
                <th className="py-3.5 px-5">User & Dept</th>
                <th className="py-3.5 px-5">Target Domain</th>
                <th className="py-3.5 px-5">Tier</th>
                <th className="py-3.5 px-5">Action</th>
                <th className="py-3.5 px-5">Risk</th>
                <th className="py-3.5 px-5">Payload SHA-256</th>
                <th className="py-3.5 px-5 text-right">Triage</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#161d2d] text-xs">
              {filteredLogs.map((log) => {
                const isBlock = log.enforcement_action === 'BLOCK';
                const isMask = log.enforcement_action === 'MASK';
                return (
                  <tr key={log.id} className="hover:bg-[#0c1018] transition">
                    <td className="py-3.5 px-5">
                      <div className="font-mono font-semibold text-white">{log.id}</div>
                      <div className="text-[10px] text-slate-500 font-mono">
                        {new Date(log.timestamp).toLocaleTimeString([], {
                          hour: '2-digit',
                          minute: '2-digit',
                        })}
                      </div>
                    </td>

                    <td className="py-3.5 px-5">
                      <div className="font-semibold text-slate-200">{log.user_id}</div>
                      <div className="text-[10px] text-slate-400">{log.department}</div>
                    </td>

                    <td className="py-3.5 px-5 font-mono text-slate-300">
                      {log.destination_domain}
                    </td>

                    <td className="py-3.5 px-5">
                      <span className="font-mono text-[11px] font-bold text-slate-300">
                        {log.classification_tier}
                      </span>
                    </td>

                    <td className="py-3.5 px-5">
                      <span
                        className={`px-2.5 py-1 rounded-md text-[10px] font-bold font-mono ${
                          isBlock
                            ? 'bg-red-500/20 text-red-400 border border-red-500/30'
                            : isMask
                            ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                            : 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                        }`}
                      >
                        {log.enforcement_action}
                      </span>
                    </td>

                    <td className="py-3.5 px-5 font-mono font-bold">
                      <span className={isBlock ? 'text-red-400' : isMask ? 'text-amber-400' : 'text-emerald-400'}>
                        {log.risk_score}/100
                      </span>
                    </td>

                    <td className="py-3.5 px-5 font-mono text-[11px] text-slate-400">
                      {log.payload_sha256?.slice(0, 16)}...
                    </td>

                    <td className="py-3.5 px-5 text-right">
                      <button
                        onClick={() => handleOpenDetokenize(log)}
                        className="px-2.5 py-1 rounded-lg bg-[#141b2b] border border-[#232f48] text-blue-400 hover:text-white hover:border-blue-500 text-[11px] font-medium transition cursor-pointer"
                      >
                        Inspect Vault
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Cryptographic Detokenization Modal */}
      {detokenizeModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-4">
          <div className="bg-[#0d111a] border border-[#1e2638] rounded-3xl w-full max-w-lg p-6 space-y-6 shadow-2xl">
            <div className="flex items-center justify-between border-b border-[#1c2436] pb-4">
              <div className="flex items-center gap-2.5">
                <div className="w-9 h-9 rounded-xl bg-amber-500/20 border border-amber-500/30 flex items-center justify-center text-amber-400">
                  <Key className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-base font-bold text-white font-heading">
                    Authorized SOC Detokenization
                  </h3>
                  <p className="text-[11px] text-slate-400">AES-256-GCM Envelope Recovery</p>
                </div>
              </div>
              <button
                onClick={() => setDetokenizeModalOpen(false)}
                className="text-slate-400 hover:text-white cursor-pointer"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <label className="text-xs text-slate-300 block mb-1 font-semibold">HMAC Token</label>
                <input
                  type="text"
                  value={tokenInput}
                  onChange={(e) => setTokenInput(e.target.value)}
                  placeholder="TOK_CREDIT_CARD_..."
                  className="w-full bg-[#080b11] border border-[#1a2233] rounded-xl px-3.5 py-2 text-xs font-mono text-cyan-400 focus:outline-none focus:border-blue-500"
                />
              </div>

              <div>
                <label className="text-xs text-slate-300 block mb-1 font-semibold">
                  SOC Officer Secret Authorization Key
                </label>
                <input
                  type="password"
                  value={authKeyInput}
                  onChange={(e) => setAuthKeyInput(e.target.value)}
                  placeholder="Enter authorized SOC master key..."
                  className="w-full bg-[#080b11] border border-[#1a2233] rounded-xl px-3.5 py-2 text-xs font-mono text-slate-300 focus:outline-none focus:border-amber-500"
                />
                <span className="text-[10px] text-slate-500 block mt-1">
                  Default Bank Key: bank-soc-super-secret-key-2026
                </span>
              </div>

              {detokenizedResult && (
                <div className="p-4 rounded-2xl bg-[#090d14] border border-emerald-500/30 space-y-2">
                  <div className="text-[11px] font-semibold text-emerald-400 flex items-center gap-1.5">
                    <CheckCircle className="w-4 h-4" /> Decrypted Plaintext Value:
                  </div>
                  <div className="text-base font-mono font-bold text-white bg-[#06080d] p-3 rounded-xl border border-[#1e2638] select-all">
                    {detokenizedResult.plaintext_value}
                  </div>
                  <div className="text-[10px] text-slate-400 font-mono flex justify-between">
                    <span>Classification: {detokenizedResult.entity_type}</span>
                    <span>Key Version: {detokenizedResult.key_version}</span>
                  </div>
                </div>
              )}
            </div>

            <div className="flex items-center justify-end gap-3 pt-3 border-t border-[#1c2436]">
              <button
                onClick={() => setDetokenizeModalOpen(false)}
                className="px-4 py-2 rounded-xl text-xs font-semibold text-slate-400 hover:text-white cursor-pointer"
              >
                Close
              </button>
              <button
                onClick={executeDetokenization}
                disabled={detokenizing}
                className="px-5 py-2 rounded-xl bg-amber-500 hover:bg-amber-400 text-black text-xs font-bold transition flex items-center gap-2 cursor-pointer"
              >
                <Key className="w-3.5 h-3.5" />
                {detokenizing ? 'Decrypting...' : 'Authorize & Decrypt'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
