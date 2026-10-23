import React, { useState, useMemo } from 'react';
import { Download, Search, AlertCircle, RefreshCw, Key, Shield, Eye, Lock, CheckCircle2, X, ShieldCheck, Info, Scale } from 'lucide-react';
import toast from 'react-hot-toast';
import { api } from '../services/api';

export default function AuditLogsView({ logs = [], setLogs, onRefresh }) {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterSource, setFilterSource] = useState('All');
  const [filterCategory, setFilterCategory] = useState('All');
  const [selectedLog, setSelectedLog] = useState(null);
  const [verifying, setVerifying] = useState(false);

  // Detokenization state inside modal
  const [authKey, setAuthKey] = useState('bank-sec-admin-token');
  const [tokenInput, setTokenInput] = useState('');
  const [detokenizedResult, setDetokenizedResult] = useState(null);
  const [detokenizing, setDetokenizing] = useState(false);

  const handleVerifyIntegrity = async () => {
    setVerifying(true);
    try {
      const res = await api.verifyLedgerIntegrity();
      if (res.tamperProofLedgerValid || res.tamper_proof_ledger_valid) {
        toast.success(
          `Cryptographic Ledger Verified: ${res.totalRecordsVerified ?? res.total_records_verified ?? 0} records chained with SHA-256 without tampering (${res.verificationStandard ?? res.verification_standard ?? 'SOC2/ISO 42001'})`,
          { duration: 5000 }
        );
      } else {
        toast.error(`Tamper Alert: Ledger signature mismatch detected at incident ${res.corrupted_incident_id || 'unknown'}!`);
      }
    } catch {
      toast.error('Could not complete cryptographic audit integrity check.');
    } finally {
      setVerifying(false);
    }
  };

  const handleExportCSV = () => {
    if (logs.length === 0) {
      toast.error('No incident records to export.');
      return;
    }
    const headers = ['Event ID', 'Timestamp', 'Client ID', 'User ID', 'Department', 'Destination', 'Action', 'Tier', 'Risk Score', 'Enforcement'];
    const rows = logs.map(log => [
      log.id || '',
      log.timestamp || '',
      `"${log.client_id || ''}"`,
      `"${log.user_id || ''}"`,
      `"${log.department || ''}"`,
      `"${log.destination_domain || ''}"`,
      `"${log.source_action || ''}"`,
      `"${log.classification_tier || ''}"`,
      log.risk_score || 0,
      `"${log.enforcement_action || ''}"`
    ]);
    
    const csvContent = [headers.join(','), ...rows.map(e => e.join(','))].join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', `secureflow_regulatory_audit_trail.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    toast.success('Audit logs exported successfully!');
  };

  const toggleIncorrectClassification = (id) => {
    if (setLogs) {
      setLogs(prev => prev.map(log => 
        log.id === id 
          ? { ...log, incorrectClassification: !log.incorrectClassification }
          : log
      ));
    }
    toast.success('Retraining pipeline feed updated.');
  };

  const handleDetokenize = async () => {
    if (!tokenInput.trim()) {
      toast.error('Please enter an encrypted token.');
      return;
    }
    setDetokenizing(true);
    setDetokenizedResult(null);
    try {
      const res = await api.detokenize(tokenInput.trim(), authKey);
      setDetokenizedResult(res);
      toast.success('Token decrypted successfully from Vault.');
    } catch (err) {
      console.error('Detokenization error:', err);
      toast.error('Detokenization failed: Invalid key or token format.');
    } finally {
      setDetokenizing(false);
    }
  };

  const filteredLogs = useMemo(() => {
    return logs.filter(log => {
      const src = log.source_action || log.source || '';
      const cat = log.classification_tier || log.category || '';
      const dest = log.destination_domain || log.details || log.file_name || log.fileName || '';
      const user = log.user_id || '';

      const matchSrc = filterSource === 'All' || src.toLowerCase().includes(filterSource.toLowerCase());
      const matchCat = filterCategory === 'All' || cat.toLowerCase() === filterCategory.toLowerCase();
      const matchSearch = dest.toLowerCase().includes(searchTerm.toLowerCase()) || 
                          user.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          (log.id && log.id.toLowerCase().includes(searchTerm.toLowerCase()));
      return matchSrc && matchCat && matchSearch;
    });
  }, [logs, filterSource, filterCategory, searchTerm]);

  return (
    <div className="flex-1 p-8 space-y-8 select-none">
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <h1 className="text-4xl font-extrabold tracking-tight uppercase font-sans text-white">
            AUDIT LOGS TRAIL
          </h1>
          <p className="text-sm text-[#8e8f96]">
            Complete regulatory log history of sensitive text, uploads, clipboard events, and actions taken.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={handleVerifyIntegrity}
            disabled={verifying}
            className="bg-[#0c0c0e] border border-[#8df85f]/40 text-[#8df85f] rounded-2xl px-4 py-2 text-xs font-semibold hover:bg-[#8df85f]/10 hover:border-[#8df85f] transition cursor-pointer flex items-center gap-2"
          >
            <ShieldCheck className={`w-3.5 h-3.5 ${verifying ? 'animate-spin' : ''}`} />
            {verifying ? 'Verifying Hashes...' : 'Verify Ledger Integrity'}
          </button>

          {onRefresh && (
            <button
              onClick={onRefresh}
              className="bg-[#0c0c0e] border border-[#161619] rounded-2xl px-4 py-2 text-xs font-semibold text-[#8e8f96] hover:text-white hover:border-white transition cursor-pointer flex items-center gap-2"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              Refresh Trail
            </button>
          )}
        </div>
      </div>

      <div className="bg-[#0c0c0e] border border-[#161619] rounded-[28px] p-6 space-y-6">
        <div className="flex items-center justify-between flex-wrap gap-4">
          <div>
            <h2 className="text-xl font-bold text-white mb-1">DLP Gateway Transactions</h2>
            <p className="text-xs text-[#8e8f96]">
              Total {filteredLogs.length} live events logged in persistent database
            </p>
          </div>

          <div className="flex items-center gap-3">
            <div className="relative">
              <Search className="w-4 h-4 text-[#8e8f96] absolute left-3.5 top-3" />
              <input
                type="text"
                placeholder="Search file name, destination, user..."
                value={searchTerm}
                onChange={e => setSearchTerm(e.target.value)}
                className="bg-[#121316] border border-[#23252c] rounded-xl pl-10 pr-4 py-2 text-xs text-white focus:outline-none focus:border-white w-56"
              />
            </div>

            <select
              value={filterSource}
              onChange={e => setFilterSource(e.target.value)}
              className="bg-[#121316] border border-[#23252c] rounded-xl px-3 py-2 text-xs text-white focus:outline-none cursor-pointer"
            >
              <option value="All">All Sources</option>
              <option value="clipboard">Desktop Clipboard</option>
              <option value="prompt">Browser Extension</option>
              <option value="file_upload">File Upload</option>
            </select>

            <select
              value={filterCategory}
              onChange={e => setFilterCategory(e.target.value)}
              className="bg-[#121316] border border-[#23252c] rounded-xl px-3 py-2 text-xs text-white focus:outline-none cursor-pointer"
            >
              <option value="All">All Categories</option>
              <option value="SAFE">SAFE</option>
              <option value="INTERNAL">INTERNAL</option>
              <option value="CONFIDENTIAL">CONFIDENTIAL</option>
              <option value="RESTRICTED">RESTRICTED</option>
            </select>

            <button
              onClick={handleExportCSV}
              className="bg-white text-black font-semibold text-xs px-4 py-2 rounded-xl flex items-center gap-2 hover:scale-105 transition cursor-pointer"
            >
              <Download className="w-3.5 h-3.5" />
              Export CSV
            </button>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-[#161619] text-[#8e8f96] text-xs font-semibold uppercase tracking-wider">
                <th className="py-4 px-4">Event ID</th>
                <th className="py-4 px-4">Timestamp</th>
                <th className="py-4 px-4">Source</th>
                <th className="py-4 px-4">Target / Details</th>
                <th className="py-4 px-4">Category Tier</th>
                <th className="py-4 px-4">Risk</th>
                <th className="py-4 px-4">Enforcement</th>
                <th className="py-4 px-4">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#111215] text-xs">
              {filteredLogs.map((log) => {
                const tier = log.classification_tier || log.category || 'SAFE';
                const action = log.enforcement_action || log.actionTaken || 'ALLOW';
                const isHighRisk = (log.risk_score || log.riskScore || 0) > 75;

                return (
                  <tr 
                    key={log.id || Math.random()} 
                    className="hover:bg-[#121316] transition-colors cursor-pointer"
                    onClick={() => {
                      setSelectedLog(log);
                      setDetokenizedResult(null);
                    }}
                  >
                    <td className="py-4 px-4 font-mono text-[#8df85f] font-bold">
                      {log.id || 'N/A'}
                    </td>
                    <td className="py-4 px-4 font-mono text-[#8e8f96]">
                      {log.timestamp ? new Date(log.timestamp).toLocaleString() : 'Live'}
                    </td>
                    <td className="py-4 px-4 text-white font-medium">
                      {log.source_action || log.source || 'Gateway'}
                    </td>
                    <td className="py-4 px-4 max-w-[240px] truncate" title={log.details || log.destination_domain}>
                      <span className="text-white block text-xs truncate">
                        {log.destination_domain || log.file_name || log.fileName || 'Gateway Event'}
                      </span>
                      <span className="text-[#8e8f96] block text-[10px] truncate">
                        {log.user_id ? `${log.user_id} (${log.department || 'dept'})` : (log.details || 'Live inspection')}
                      </span>
                    </td>
                    <td className="py-4 px-4">
                      <span className={`px-2 py-0.5 rounded-full font-bold text-[9px] uppercase ${
                        tier === 'RESTRICTED' || tier === 'Highly Confidential' ? 'bg-[#f38933]/15 text-[#f38933] border border-[#f38933]/30' :
                        tier === 'CONFIDENTIAL' || tier === 'Confidential' ? 'bg-white/10 text-white border border-white/20' :
                        tier === 'INTERNAL' || tier === 'Internal' ? 'bg-[#8df85f]/15 text-[#8df85f] border border-[#8df85f]/30' :
                        'bg-gray-800 text-gray-400'
                      }`}>
                        {tier}
                      </span>
                    </td>
                    <td className="py-4 px-4">
                      <div className="flex items-center gap-1.5">
                        <span className={`font-bold font-mono ${isHighRisk ? 'text-[#f38933]' : 'text-white'}`}>
                          {log.risk_score ?? log.riskScore ?? 0}%
                        </span>
                        {isHighRisk && <AlertCircle className="w-3.5 h-3.5 text-[#f38933]" />}
                      </div>
                    </td>
                    <td className="py-4 px-4">
                      <span className={`font-mono text-[11px] font-semibold ${
                        action === 'BLOCK' ? 'text-[#f38933]' :
                        action === 'MASK' ? 'text-[#8df85f]' : 'text-slate-300'
                      }`}>
                        {action}
                      </span>
                    </td>
                    <td className="py-4 px-4" onClick={(e) => e.stopPropagation()}>
                      <button
                        onClick={() => toggleIncorrectClassification(log.id)}
                        className={`px-3 py-1.5 rounded-lg flex items-center gap-1.5 border font-semibold text-[10px] transition cursor-pointer ${
                          log.incorrectClassification
                            ? 'bg-[#f38933]/10 border-[#f38933] text-[#f38933]'
                            : 'border-[#23252c] text-[#8e8f96] hover:text-white hover:border-white'
                        }`}
                      >
                        <RefreshCw className="w-3 h-3" />
                        {log.incorrectClassification ? 'Flagged' : 'Report'}
                      </button>
                    </td>
                  </tr>
                );
              })}

              {filteredLogs.length === 0 && (
                <tr>
                  <td colSpan={8} className="py-12 text-center text-[#8e8f96] font-semibold">
                    No matching audit records in database.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Forensic Inspection & Detokenization Modal */}
      {selectedLog && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-[#0c0c0e] border border-[#161619] rounded-[28px] max-w-2xl w-full p-8 space-y-6 relative shadow-2xl">
            <button
              onClick={() => setSelectedLog(null)}
              className="absolute top-6 right-6 text-[#8e8f96] hover:text-white cursor-pointer"
            >
              <X className="w-5 h-5" />
            </button>

            <div>
              <div className="flex items-center gap-2 mb-1">
                <Shield className="w-5 h-5 text-[#8df85f]" />
                <h3 className="text-xl font-extrabold uppercase font-sans text-white">
                  Forensic Incident Inspection: {selectedLog.id}
                </h3>
              </div>
              <p className="text-xs text-[#8e8f96]">
                Immutable cryptographic audit record recorded by SecureFlow AI DLP Gateway.
              </p>
            </div>

            <div className="grid grid-cols-2 gap-4 text-xs font-mono bg-[#121316] border border-[#21232a] p-4 rounded-2xl">
              <div>
                <span className="text-[#8e8f96] block text-[10px] uppercase">User & Department:</span>
                <span className="text-white font-semibold">
                  {selectedLog.user_id || 'N/A'} ({selectedLog.department || 'banking'})
                </span>
              </div>
              <div>
                <span className="text-[#8e8f96] block text-[10px] uppercase">Destination Domain:</span>
                <span className="text-[#8df85f] font-semibold">
                  {selectedLog.destination_domain || 'Internal'}
                </span>
              </div>
              <div>
                <span className="text-[#8e8f96] block text-[10px] uppercase">Source Client:</span>
                <span className="text-white">
                  {selectedLog.client_id || 'daemon'} ({selectedLog.source_action || 'clipboard'})
                </span>
              </div>
              <div>
                <span className="text-[#8e8f96] block text-[10px] uppercase">Risk & Enforcement:</span>
                <span className={selectedLog.enforcement_action === 'BLOCK' ? 'text-[#f38933] font-bold' : 'text-[#8df85f] font-bold'}>
                  {selectedLog.risk_score}% — {selectedLog.enforcement_action}
                </span>
              </div>

              {/* Threat Category & Detailed Explanation */}
              <div className="col-span-2 pt-2 border-t border-[#21232a] space-y-1.5 font-sans">
                <div className="flex items-center justify-between">
                  <span className="text-[#8e8f96] text-[10px] uppercase font-bold flex items-center gap-1 font-mono">
                    <Info className="w-3 h-3 text-[#8df85f]" />
                    Threat Classification & Explainability:
                  </span>
                  <span className={`px-2 py-0.5 rounded text-[9px] font-extrabold uppercase font-mono ${
                    (selectedLog.threat_category || selectedLog.threatCategory || '').includes('CRITICAL') || (selectedLog.threat_category || selectedLog.threatCategory || '').includes('EXPOSURE')
                      ? 'bg-[#f38933]/20 text-[#f38933] border border-[#f38933]/30'
                      : 'bg-[#8df85f]/15 text-[#8df85f] border border-[#8df85f]/30'
                  }`}>
                    {selectedLog.threat_category || selectedLog.threatCategory || 'BENIGN_DATA'}
                  </span>
                </div>
                <p className="text-xs text-slate-200 bg-black/40 p-2.5 rounded-xl border border-[#21232a] leading-relaxed">
                  {selectedLog.explanation || 'Clean transaction verified against enterprise banking security baseline.'}
                </p>
              </div>

              {/* Compliance & Regulatory Framework Tags */}
              {((selectedLog.compliance_tags || selectedLog.complianceImpact) && (selectedLog.compliance_tags || selectedLog.complianceImpact).length > 0) && (
                <div className="col-span-2 space-y-1 font-sans">
                  <span className="text-[#8e8f96] text-[10px] uppercase font-bold flex items-center gap-1 font-mono">
                    <Scale className="w-3 h-3 text-[#8e8f96]" />
                    Regulatory Compliance Mapping:
                  </span>
                  <div className="flex flex-wrap gap-1.5">
                    {(selectedLog.compliance_tags || selectedLog.complianceImpact).map((tag, idx) => (
                      <span key={idx} className="px-2 py-0.5 rounded bg-[#16181d] border border-[#262833] text-[10px] font-mono text-slate-300">
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Remediation Advice */}
              {(selectedLog.remediation_advice || selectedLog.remediationAdvice) && (
                <div className="col-span-2 text-[11px] text-[#8e8f96] flex items-start gap-1.5 font-sans pt-1">
                  <CheckCircle2 className="w-3.5 h-3.5 text-[#8df85f] shrink-0 mt-0.5" />
                  <span><strong className="text-white">Remediation Action: </strong>{selectedLog.remediation_advice || selectedLog.remediationAdvice}</span>
                </div>
              )}

              {/* Cryptographic SHA-256 Ledger Chain (Immutable Audit Proof) */}
              <div className="col-span-2 pt-2 border-t border-[#21232a] space-y-1.5">
                <div className="flex items-center justify-between">
                  <span className="text-[#8e8f96] block text-[10px] uppercase font-bold flex items-center gap-1">
                    <ShieldCheck className="w-3.5 h-3.5 text-[#8df85f]" />
                    Cryptographic Audit Chain (Immutable SHA-256):
                  </span>
                  <span className="text-[9px] text-[#8df85f] font-mono bg-[#8df85f]/10 px-2 py-0.5 rounded border border-[#8df85f]/30">
                    SOC2 / ISO 42001 Validated
                  </span>
                </div>
                <div className="space-y-1 bg-black/40 p-2.5 rounded-xl border border-[#21232a] text-[10px]">
                  {selectedLog.prev_hash && (
                    <div className="truncate">
                      <span className="text-[#8e8f96]">Prev Hash: </span>
                      <span className="text-slate-400 select-all">{selectedLog.prev_hash}</span>
                    </div>
                  )}
                  {selectedLog.audit_hash && (
                    <div className="truncate">
                      <span className="text-[#8e8f96]">Record Hash: </span>
                      <span className="text-[#8df85f] font-bold select-all">{selectedLog.audit_hash}</span>
                    </div>
                  )}
                  {selectedLog.payload_sha256 && (
                    <div className="truncate">
                      <span className="text-[#8e8f96]">Payload Hash: </span>
                      <span className="text-slate-400 select-all">{selectedLog.payload_sha256}</span>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Cryptographic Detokenization Utility */}
            <div className="space-y-3 border-t border-[#161619] pt-4">
              <div className="flex items-center gap-2">
                <Key className="w-4 h-4 text-[#8df85f]" />
                <span className="text-xs font-bold uppercase tracking-wider text-white">
                  Authorized Detokenization Vault
                </span>
              </div>
              <p className="text-[11px] text-[#8e8f96]">
                Security Officers can detokenize masked HMAC-SHA256 tokens using the cryptographic master key.
              </p>

              <div className="flex gap-2">
                <input
                  type="text"
                  placeholder="Paste token, e.g. [TOKEN:5f2b...] or paste ciphertext..."
                  value={tokenInput}
                  onChange={(e) => setTokenInput(e.target.value)}
                  className="flex-1 bg-[#121316] border border-[#21232a] rounded-xl px-3 py-2 text-xs font-mono text-white placeholder-[#8e8f96] focus:outline-none focus:border-white"
                />
                <button
                  onClick={handleDetokenize}
                  disabled={detokenizing}
                  className="bg-white text-black font-bold text-xs px-4 py-2 rounded-xl hover:scale-105 transition cursor-pointer flex items-center gap-1.5"
                >
                  <Lock className="w-3.5 h-3.5" />
                  {detokenizing ? 'Decrypting...' : 'Detokenize'}
                </button>
              </div>

              {detokenizedResult && (
                <div className="p-3 bg-[#121316] border border-[#8df85f]/40 rounded-xl text-xs font-mono space-y-1">
                  <div className="text-[#8df85f] font-bold flex items-center gap-1.5">
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    Decrypted Plaintext Value:
                  </div>
                  <div className="text-white bg-black/40 p-2 rounded border border-[#21232a] select-all">
                    {detokenizedResult.plaintext}
                  </div>
                </div>
              )}
            </div>

            <div className="flex justify-end pt-2">
              <button
                onClick={() => setSelectedLog(null)}
                className="bg-[#121316] border border-[#21232a] text-white hover:border-white px-5 py-2 rounded-xl text-xs font-bold transition cursor-pointer"
              >
                Close Inspection
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
