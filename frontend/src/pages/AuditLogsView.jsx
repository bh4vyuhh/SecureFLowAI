import React, { useState } from 'react';
import { Download, Search, AlertCircle, RefreshCw } from 'lucide-react';
import toast from 'react-hot-toast';

export default function AuditLogsView({ logs, setLogs }) {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterSource, setFilterSource] = useState('All');
  const [filterCategory, setFilterCategory] = useState('All');
  const [selectedLog, setSelectedLog] = useState(null);

  const handleExportCSV = () => {
    const headers = ['Event ID', 'Timestamp', 'Source', 'File Name', 'Risk Score', 'Classification', 'Action Taken', 'PII Detections'];
    const rows = logs.map(log => [
      log.id,
      log.timestamp,
      `"${log.source}"`,
      `"${log.fileName}"`,
      log.riskScore,
      log.category,
      log.actionTaken,
      `"${log.piiDetected.join(', ')}"`
    ]);
    
    const csvContent = [headers.join(','), ...rows.map(e => e.join(','))].join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', `secureflow_audit_logs_full.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    toast.success('Audit logs exported successfully!');
  };

  const toggleIncorrectClassification = (id) => {
    setLogs(prev => prev.map(log => 
      log.id === id 
        ? { ...log, incorrectClassification: !log.incorrectClassification }
        : log
    ));
    toast.success('Retraining pipeline feed updated.');
  };

  const filteredLogs = logs.filter(log => {
    const matchSrc = filterSource === 'All' || log.source === filterSource;
    const matchCat = filterCategory === 'All' || log.category === filterCategory;
    const matchSearch = log.details.toLowerCase().includes(searchTerm.toLowerCase()) || 
                        log.fileName.toLowerCase().includes(searchTerm.toLowerCase());
    return matchSrc && matchCat && matchSearch;
  });

  return (
    <div className="flex-1 p-8 space-y-8 select-none">
      <div>
        <h1 className="text-4xl font-extrabold tracking-tight uppercase font-sans text-white">
          AUDIT LOGS TRAIL
        </h1>
        <p className="text-sm text-[#8e8f96]">Complete regulatory log history of sensitive text, uploads, clipboard events, and actions taken.</p>
      </div>

      <div className="bg-[#0c0c0e] border border-[#161619] rounded-[28px] p-6 space-y-6">
        <div className="flex items-center justify-between flex-wrap gap-4">
          <div>
            <h2 className="text-xl font-bold text-white mb-1">DLP Gateway Transactions</h2>
            <p className="text-xs text-[#8e8f96]">Total {filteredLogs.length} events logged over the past 3 weeks</p>
          </div>

          <div className="flex items-center gap-3">
            <div className="relative">
              <Search className="w-4 h-4 text-[#8e8f96] absolute left-3.5 top-3" />
              <input
                type="text"
                placeholder="Search file name..."
                value={searchTerm}
                onChange={e => setSearchTerm(e.target.value)}
                className="bg-[#121316] border border-[#23252c] rounded-xl pl-10 pr-4 py-2 text-xs text-white focus:outline-none focus:border-white w-52"
              />
            </div>

            <select
              value={filterSource}
              onChange={e => setFilterSource(e.target.value)}
              className="bg-[#121316] border border-[#23252c] rounded-xl px-3 py-2 text-xs text-white focus:outline-none"
            >
              <option value="All">All Sources</option>
              <option value="Chrome Extension">Chrome Extension</option>
              <option value="Desktop Clipboard">Desktop Clipboard</option>
              <option value="Email Gateway">Email Gateway</option>
              <option value="Web Upload">Web Upload</option>
              <option value="Local File Agent">Local File Agent</option>
            </select>

            <select
              value={filterCategory}
              onChange={e => setFilterCategory(e.target.value)}
              className="bg-[#121316] border border-[#23252c] rounded-xl px-3 py-2 text-xs text-white focus:outline-none"
            >
              <option value="All">All Categories</option>
              <option value="Public">Public</option>
              <option value="Internal">Internal</option>
              <option value="Confidential">Confidential</option>
              <option value="Highly Confidential">Highly Confidential</option>
            </select>

            <button
              onClick={handleExportCSV}
              className="bg-white text-black font-semibold text-xs px-4 py-2 rounded-xl flex items-center gap-2 hover:scale-105 transition cursor-pointer"
            >
              <Download className="w-3.5 h-3.5" />
              Export
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
                <th className="py-4 px-4">File Name</th>
                <th className="py-4 px-4">Classification</th>
                <th className="py-4 px-4">Risk Score</th>
                <th className="py-4 px-4">Action</th>
                <th className="py-4 px-4 text-center">Retraining Feed</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#111215] text-xs">
              {filteredLogs.map((log) => (
                <tr key={log.id} className="hover:bg-[#121316] transition-colors cursor-pointer" onClick={() => setSelectedLog(log)}>
                  <td className="py-4 px-4 font-mono text-[#8df85f]">{log.id}</td>
                  <td className="py-4 px-4 font-mono text-[#8e8f96]">
                    {new Date(log.timestamp).toLocaleString()}
                  </td>
                  <td className="py-4 px-4 text-white font-medium">{log.source}</td>
                  <td className="py-4 px-4 max-w-[150px] truncate" title={log.fileName}>{log.fileName}</td>
                  <td className="py-4 px-4">
                    <span className={`px-2.5 py-0.5 rounded-full font-bold text-[9px] uppercase ${
                      log.category === 'Highly Confidential' ? 'bg-[#f38933]/15 text-[#f38933] border border-[#f38933]/30' :
                      log.category === 'Confidential' ? 'bg-white/10 text-white border border-white/20' :
                      log.category === 'Internal' ? 'bg-[#8df85f]/15 text-[#8df85f] border border-[#8df85f]/30' :
                      'bg-gray-800 text-gray-400'
                    }`}>
                      {log.category}
                    </span>
                  </td>
                  <td className="py-4 px-4 font-mono font-bold">{log.riskScore}%</td>
                  <td className="py-4 px-4 text-[#8e8f96]">{log.actionTaken}</td>
                  <td className="py-4 px-4 text-center" onClick={e => e.stopPropagation()}>
                    <button
                      onClick={() => toggleIncorrectClassification(log.id)}
                      className={`px-3 py-1 rounded-lg border font-semibold text-[10px] transition ${
                        log.incorrectClassification
                          ? 'bg-[#f38933]/10 border-[#f38933] text-[#f38933]'
                          : 'border-[#23252c] text-[#8e8f96] hover:text-white hover:border-white'
                      }`}
                    >
                      {log.incorrectClassification ? 'Flagged Error' : 'Report Error'}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {selectedLog && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 z-50 animate-fade-in">
          <div className="bg-[#0c0c0e] border border-[#161619] rounded-[28px] max-w-lg w-full p-8 space-y-6 shadow-2xl relative">
            <div className="flex items-center justify-between border-b border-[#161619] pb-4">
              <h3 className="text-base font-bold text-white font-mono">DLP Transaction Detail: {selectedLog.id}</h3>
              <button 
                onClick={() => setSelectedLog(null)}
                className="text-xs text-[#8e8f96] hover:text-white font-bold"
              >
                Close
              </button>
            </div>
            
            <div className="space-y-4 text-xs">
              <div className="grid grid-cols-3 gap-2">
                <span className="text-[#8e8f96]">Timestamp:</span>
                <span className="col-span-2 text-white font-mono">{new Date(selectedLog.timestamp).toString()}</span>
              </div>

              <div className="grid grid-cols-3 gap-2">
                <span className="text-[#8e8f96]">Source Endpoint:</span>
                <span className="col-span-2 text-white font-semibold">{selectedLog.source}</span>
              </div>

              <div className="grid grid-cols-3 gap-2">
                <span className="text-[#8e8f96]">Payload Name:</span>
                <span className="col-span-2 text-[#8df85f] font-mono">{selectedLog.fileName}</span>
              </div>

              <div className="grid grid-cols-3 gap-2">
                <span className="text-[#8e8f96]">DLP Classification:</span>
                <span className="col-span-2 font-bold text-white">{selectedLog.category}</span>
              </div>

              <div className="grid grid-cols-3 gap-2">
                <span className="text-[#8e8f96]">DLP Risk Index:</span>
                <span className="col-span-2 font-bold font-mono text-white">{selectedLog.riskScore}%</span>
              </div>

              <div className="grid grid-cols-3 gap-2">
                <span className="text-[#8e8f96]">Mitigation Status:</span>
                <span className="col-span-2 text-[#8e8f96]">{selectedLog.actionTaken}</span>
              </div>

              {selectedLog.piiDetected.length > 0 && (
                <div className="grid grid-cols-3 gap-2">
                  <span className="text-[#8e8f96]">PII Identified:</span>
                  <div className="col-span-2 flex flex-wrap gap-1">
                    {selectedLog.piiDetected.map((pii, i) => (
                      <span key={i} className="bg-[#121316] border border-[#23252c] px-2 py-0.5 rounded text-[9px] text-white">
                        {pii}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              <div className="border-t border-[#161619] pt-4 space-y-1">
                <span className="text-[10px] font-bold text-[#8e8f96] uppercase">Transaction Diagnostics</span>
                <p className="text-[#8e8f96] leading-relaxed bg-[#121316] border border-[#23252c] p-3 rounded-xl">
                  {selectedLog.details}
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
