import React, { useState } from 'react';
import { ResponsiveContainer, LineChart, Line } from 'recharts';
import { ArrowUpRight, ArrowDownRight, Download, Search, AlertCircle, RefreshCw } from 'lucide-react';
import { sparklineDataCustomer, dotGridData, resourcePillData, timelineData } from '../utils/mockData';

export default function Dashboard({ logs, setLogs, setView }) {
  const [filterSource, setFilterSource] = useState('All');
  const [filterCategory, setFilterCategory] = useState('All');
  const [searchTerm, setSearchTerm] = useState('');

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
    link.setAttribute('download', `secureflow_audit_logs_${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const toggleIncorrectClassification = (id) => {
    setLogs(prev => prev.map(log => 
      log.id === id 
        ? { ...log, incorrectClassification: !log.incorrectClassification }
        : log
    ));
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
      
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-4xl font-extrabold tracking-tight uppercase font-sans text-white">
            CHECK BOX
          </h1>
        </div>

        <div className="flex items-center gap-3">
          <div className="bg-[#0c0c0e] border border-[#161619] rounded-2xl px-4 py-2 text-xs font-semibold text-[#8e8f96] flex items-center gap-2">
            <span>Date:</span>
            <select className="bg-transparent text-white focus:outline-none cursor-pointer">
              <option>Now</option>
              <option>Last 24h</option>
              <option>7 Days</option>
              <option>30 Days</option>
            </select>
          </div>

          <div className="bg-[#0c0c0e] border border-[#161619] rounded-2xl px-4 py-2 text-xs font-semibold text-[#8e8f96] flex items-center gap-2">
            <span>Product:</span>
            <select className="bg-transparent text-white focus:outline-none cursor-pointer">
              <option>All Gateway</option>
              <option>Extension</option>
              <option>Clipboard</option>
            </select>
          </div>

          <div className="bg-[#0c0c0e] border border-[#161619] rounded-2xl px-4 py-2 text-xs font-semibold text-[#8e8f96] flex items-center gap-2">
            <span>Profile:</span>
            <select className="bg-transparent text-white focus:outline-none cursor-pointer">
              <option>Bogdan</option>
              <option>Admin</option>
            </select>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-12 gap-8">
        
        <div className="col-span-5 flex flex-col gap-8">
          
          <div className="grid grid-cols-2 gap-8">
            <div className="bg-[#0c0c0e] border border-[#161619] rounded-[28px] p-6 flex flex-col justify-between h-[210px]">
              <div>
                <div className="flex items-center justify-between text-[11px] font-bold tracking-wider text-[#8e8f96] uppercase mb-4">
                  <span>Clipboard Activity</span>
                  <span className="cursor-pointer text-[#8e8f96] hover:text-white">•••</span>
                </div>
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <div className="text-2xl font-extrabold text-white flex items-center gap-1 font-sans">
                      2,4%
                      <span className="text-[#8df85f] text-xs"><ArrowUpRight className="w-3.5 h-3.5 inline" /></span>
                    </div>
                    <div className="text-[10px] font-semibold text-[#8e8f96]">Extension Paste</div>
                  </div>
                  <div>
                    <div className="text-2xl font-extrabold text-white flex items-center gap-1 font-sans">
                      1,1%
                      <span className="text-[#f38933] text-xs"><ArrowDownRight className="w-3.5 h-3.5 inline" /></span>
                    </div>
                    <div className="text-[10px] font-semibold text-[#8e8f96]">System Clipboard</div>
                  </div>
                </div>
              </div>
              <div className="h-14 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={sparklineDataCustomer}>
                    <Line type="monotone" dataKey="line1" stroke="#8df85f" strokeWidth={2} dot={false} />
                    <Line type="monotone" dataKey="line2" stroke="#f38933" strokeWidth={2} dot={false} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div className="bg-[#0c0c0e] border border-[#161619] rounded-[28px] p-6 flex flex-col justify-between h-[210px]">
              <div>
                <div className="flex items-center justify-between text-[11px] font-bold tracking-wider text-[#8e8f96] uppercase mb-4">
                  <span>Bulk Scanner Hits</span>
                  <span className="cursor-pointer text-[#8e8f96] hover:text-white">•••</span>
                </div>
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <div className="text-2xl font-extrabold text-white flex items-center gap-1 font-sans">
                      2,8%
                      <span className="text-[#8df85f] text-xs"><ArrowUpRight className="w-3.5 h-3.5 inline" /></span>
                    </div>
                    <div className="text-[10px] font-semibold text-[#8e8f96]">Clean Files</div>
                  </div>
                  <div>
                    <div className="text-2xl font-extrabold text-white flex items-center gap-1 font-sans">
                      3,2%
                      <span className="text-[#f38933] text-xs"><ArrowDownRight className="w-3.5 h-3.5 inline" /></span>
                    </div>
                    <div className="text-[10px] font-semibold text-[#8e8f96]">Confidential</div>
                  </div>
                </div>
              </div>
              
              <div className="grid grid-cols-14 gap-1.5 pt-4">
                {dotGridData.slice(0, 70).map((dot) => (
                  <div
                    key={dot.id}
                    className={`w-1.5 h-1.5 rounded-full transition-colors duration-300 ${
                      dot.status === 'low' ? 'bg-[#8df85f]' :
                      dot.status === 'high' ? 'bg-[#f38933]' :
                      dot.status === 'alert' ? 'bg-white' : 'bg-[#1e1f25]'
                    }`}
                  />
                ))}
              </div>
            </div>
          </div>

          <div className="bg-[#0c0c0e] border border-[#161619] rounded-[28px] p-6 flex flex-col justify-between h-[300px]">
            <div>
              <div className="flex items-center justify-between text-[11px] font-bold tracking-wider text-[#8e8f96] uppercase mb-4">
                <span>DLP Mitigation Logs</span>
                <span className="cursor-pointer text-[#8e8f96] hover:text-white">•••</span>
              </div>
            </div>

            <div className="flex justify-between items-end px-2 h-40">
              {resourcePillData.map((pill) => (
                <div key={pill.id} className="flex flex-col items-center gap-2 h-full justify-end">
                  <div 
                    className="w-5 rounded-full flex flex-col justify-between items-center py-1 transition-all duration-300 hover:scale-105"
                    style={{ 
                      height: `${pill.resources * 0.7}%`, 
                      backgroundColor: pill.resources > 75 ? '#8df85f' : pill.resources > 50 ? '#ffffff' : '#f38933',
                      color: '#000000',
                      fontWeight: 800,
                      fontSize: '9px'
                    }}
                  >
                    <span className="mt-1">{pill.labelVal}</span>
                  </div>

                  <div className="w-1.5 h-1.5 rounded-full bg-white" />

                  <div 
                    className="w-5 rounded-full transition-all duration-300 hover:scale-105"
                    style={{ 
                      height: `${pill.valid * 0.5}%`, 
                      backgroundColor: pill.valid > 60 ? '#f38933' : '#1e1f25'
                    }}
                  />
                </div>
              ))}
            </div>

            <div className="flex items-center justify-between border-t border-[#161619] pt-4 mt-2">
              <div className="flex items-center gap-5 text-[10px] font-bold tracking-wide">
                <span className="flex items-center gap-1.5 text-white">
                  <span className="w-2.5 h-2.5 rounded-full bg-white inline-block" />
                  Encrypted
                </span>
                <span className="flex items-center gap-1.5 text-[#8e8f96]">
                  <span className="w-2.5 h-2.5 rounded-full bg-[#8df85f] inline-block" />
                  Masked PII
                </span>
                <span className="flex items-center gap-1.5 text-[#8e8f96]">
                  <span className="w-2.5 h-2.5 rounded-full bg-[#f38933] inline-block" />
                  Blocked Alert
                </span>
              </div>
              <div className="text-xs font-bold text-white font-mono">
                Total Logs: <span className="text-[#8df85f]">1,012</span>
              </div>
            </div>
          </div>

        </div>

        <div className="col-span-7">
          <div className="bg-[#0c0c0e] border border-[#161619] rounded-[28px] p-6 flex flex-col justify-between h-[542px]">
            <div>
              <div className="flex items-center justify-between text-[11px] font-bold tracking-wider text-[#8e8f96] uppercase mb-6">
                <span>Anomaly Feeds Timeline</span>
                <span className="cursor-pointer text-[#8e8f96] hover:text-white">•••</span>
              </div>
            </div>

            <div className="flex-1 flex flex-col justify-between relative timeline-track pr-4">
              {timelineData.map((day) => (
                <div key={day.date} className="grid grid-cols-12 items-center relative h-10 border-b border-[#111215] last:border-b-0">
                  <div className="col-span-2 text-xs font-semibold text-[#8e8f96] font-mono">
                    {day.date}
                  </div>
                  <div className="col-span-10 relative h-full flex items-center">
                    {day.items.map((item) => (
                      <div
                        key={item.id}
                        className="absolute h-7 rounded-full flex items-center justify-between px-3 text-black font-extrabold text-[11px] select-none hover:scale-[1.02] transition-transform duration-200"
                        style={{
                          left: `${item.start * 3}%`,
                          right: `${100 - (item.end * 3)}%`,
                          backgroundColor: item.color
                        }}
                      >
                        <span className="truncate">{item.platform}</span>
                        <span>{item.count}</span>
                      </div>
                    ))}
                  </div>
                </div>
              ))}

              <div className="grid grid-cols-12 pt-4 border-t border-[#161619]">
                <div className="col-span-2" />
                <div className="col-span-10 flex justify-between px-1 text-[10px] font-bold text-[#8e8f96] font-mono">
                  <span>0</span>
                  <span>5</span>
                  <span>10</span>
                  <span>15</span>
                  <span>20</span>
                  <span>25</span>
                  <span>30</span>
                </div>
              </div>
            </div>

            <div className="flex items-center justify-between border-t border-[#161619] pt-4 mt-4">
              <div className="flex items-center gap-5 text-[10px] font-bold tracking-wide">
                <span className="flex items-center gap-1.5 text-[#8e8f96]">
                  <span className="w-2.5 h-2.5 rounded-full bg-[#8df85f] inline-block" />
                  Extension
                </span>
                <span className="flex items-center gap-1.5 text-[#8e8f96]">
                  <span className="w-2.5 h-2.5 rounded-full bg-[#f38933] inline-block" />
                  Clipboard
                </span>
                <span className="flex items-center gap-1.5 text-[#8e8f96]">
                  <span className="w-2.5 h-2.5 rounded-full bg-white inline-block" />
                  Web Ingestion
                </span>
              </div>
              <div className="text-xs font-bold text-white font-mono">
                Total Logs: <span className="text-[#8df85f]">284</span>
              </div>
            </div>
          </div>
        </div>

      </div>

      <div className="bg-[#0c0c0e] border border-[#161619] rounded-[28px] p-6 space-y-6">
        <div className="flex items-center justify-between flex-wrap gap-4">
          <div>
            <h2 className="text-xl font-bold text-white mb-1">DLP Transaction Audit Logs</h2>
            <p className="text-xs text-[#8e8f96]">Simulated 3 weeks of network and desktop ingestion activities</p>
          </div>

          <div className="flex items-center gap-3">
            <div className="relative">
              <Search className="w-4 h-4 text-[#8e8f96] absolute left-3.5 top-3" />
              <input
                type="text"
                placeholder="Search file name or details..."
                value={searchTerm}
                onChange={e => setSearchTerm(e.target.value)}
                className="bg-[#121316] border border-[#23252c] rounded-xl pl-10 pr-4 py-2 text-xs text-white placeholder-[#8e8f96] focus:outline-none focus:border-white w-56"
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
              <option value="All">All Levels</option>
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
              Export CSV
            </button>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-[#161619] text-[#8e8f96] text-xs font-semibold uppercase tracking-wider">
                <th className="py-4 px-4">Timestamp</th>
                <th className="py-4 px-4">Source</th>
                <th className="py-4 px-4">Subject/File</th>
                <th className="py-4 px-4">Category</th>
                <th className="py-4 px-4">Risk</th>
                <th className="py-4 px-4">Mitigation</th>
                <th className="py-4 px-4">Accuracy Pipeline</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#111215] text-xs">
              {filteredLogs.map((log) => {
                const isHighRisk = log.riskScore > 80;
                return (
                  <tr key={log.id} className="hover:bg-[#121316] transition-colors">
                    <td className="py-4 px-4 font-mono text-[#8e8f96]">
                      {new Date(log.timestamp).toLocaleString()}
                    </td>
                    <td className="py-4 px-4 font-medium text-white">{log.source}</td>
                    <td className="py-4 px-4 max-w-[200px] truncate" title={log.details}>
                      <span className="font-mono text-[#8df85f] block text-[11px] mb-0.5">{log.fileName}</span>
                      <span className="text-[#8e8f96] block text-[10px] truncate">{log.details}</span>
                    </td>
                    <td className="py-4 px-4">
                      <span className={`px-2 py-0.5 rounded-full font-bold text-[9px] uppercase ${
                        log.category === 'Highly Confidential' ? 'bg-[#f38933]/15 text-[#f38933] border border-[#f38933]/30' :
                        log.category === 'Confidential' ? 'bg-white/10 text-white border border-white/20' :
                        log.category === 'Internal' ? 'bg-[#8df85f]/15 text-[#8df85f] border border-[#8df85f]/30' :
                        'bg-gray-800 text-gray-400'
                      }`}>
                        {log.category}
                      </span>
                    </td>
                    <td className="py-4 px-4">
                      <div className="flex items-center gap-1.5">
                        <span className={`font-bold font-mono ${isHighRisk ? 'text-[#f38933]' : 'text-white'}`}>
                          {log.riskScore}%
                        </span>
                        {isHighRisk && <AlertCircle className="w-3.5 h-3.5 text-[#f38933]" />}
                      </div>
                    </td>
                    <td className="py-4 px-4 text-[#8e8f96]">{log.actionTaken}</td>
                    <td className="py-4 px-4">
                      <button
                        onClick={() => toggleIncorrectClassification(log.id)}
                        className={`px-3 py-1.5 rounded-lg flex items-center gap-1.5 border font-semibold text-[10px] transition ${
                          log.incorrectClassification
                            ? 'bg-[#f38933]/10 border-[#f38933] text-[#f38933]'
                            : 'border-[#23252c] text-[#8e8f96] hover:text-white hover:border-white'
                        }`}
                      >
                        <RefreshCw className="w-3 h-3" />
                        {log.incorrectClassification ? 'Reported Incorrect' : 'Report Error'}
                      </button>
                    </td>
                  </tr>
                );
              })}
              {filteredLogs.length === 0 && (
                <tr>
                  <td colSpan={7} className="py-8 text-center text-[#8e8f96] font-semibold">
                    No matching transaction logs found.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
