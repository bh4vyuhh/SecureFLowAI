import React, { useState, useRef } from 'react';
import { Upload, FileText, ShieldCheck, Mail, Send, Download, RefreshCw, AlertCircle, FileCheck, Lock, Key, Info, Scale, CheckCircle2, Activity, Play } from 'lucide-react';
import toast from 'react-hot-toast';
import { api } from '../services/api';

export default function FileScanner({ onNewLog }) {
  const [file, setFile] = useState(null);
  const [isDragOver, setIsDragOver] = useState(false);
  const [scanning, setScanning] = useState(false);
  const [result, setResult] = useState(null);
  const fileInputRef = useRef(null);

  const handleFileUpload = async (selectedFile) => {
    if (!selectedFile) return;
    setFile(selectedFile);
    setScanning(true);
    setResult(null);

    const start = performance.now();
    try {
      const response = await api.scanFileUpload(selectedFile, 'mask');
      const elapsed = Math.round(performance.now() - start);
      setScanning(false);

      const rawEntities = response.detected_entities || response.entities || [];
      const detections = Array.isArray(rawEntities)
        ? rawEntities.map((e) => typeof e === 'object' ? `${e.entity_type} (${Math.round((e.confidence || 1) * 100)}%)` : String(e))
        : Object.entries(rawEntities).map(([k, v]) => `${k} (${v}x)`);

      const tier = response.classification_tier || response.tier || 'SAFE';
      const action = response.enforcement_action || response.action || 'ALLOW';
      const riskScore = response.risk_score ?? 0;
      const incidentId = response.incident_id || response.request_id || `scan-${Date.now()}`;

      const scanResult = {
        fileName: selectedFile.name,
        fileSize: (selectedFile.size / 1024).toFixed(1) + ' KB',
        tier,
        riskScore,
        detections,
        threatCategory: response.threat_category || (riskScore > 75 ? 'CRITICAL_DATA_LEAK' : riskScore >= 45 ? 'INTERNAL_CONFIDENTIAL_PII' : 'BENIGN_BUSINESS_DATA'),
        explanation: response.explanation || (tier === 'SAFE'
          ? 'Zero unencrypted payment cards, cryptographic keys, or unauthorized PII detected in document contents. Standard upload authorized.'
          : 'Potential data leak detected in file structure. Automated DLP policy and encryption routing applied.'),
        complianceImpact: response.compliance_impact || (riskScore > 75 ? ['PCI-DSS-v4.0', 'GLBA', 'ISO-27001'] : tier === 'CONFIDENTIAL' ? ['GDPR-Art-32', 'SOC2-Privacy'] : ['SOC2-Baseline-Compliance']),
        remediationAdvice: response.remediation_advice || (riskScore > 75 ? 'Block upload immediately and inspect source repository.' : 'Verify recipient clearance before transferring file.'),
        latencyBreakdown: response.latency_breakdown || {},
        recommendation: action === 'BLOCK'
          ? 'Block Upload & Quarantine'
          : action === 'MASK' || action === 'ENCRYPT'
          ? 'Auto-Encrypt on Ingestion (AES-256)'
          : 'Approved for transport',
        enforcementAction: action,
        sanitizedSnippet: response.sanitized_text || response.sanitized_content || '',
        incidentId,
        rawTokens: response.tokens_generated || [],
        latencyMs: response.latency_ms ? Math.round(response.latency_ms) : elapsed
      };

      setResult(scanResult);

      if (onNewLog) {
        onNewLog({
          id: incidentId,
          timestamp: new Date().toISOString(),
          client_id: 'web-file-scanner',
          user_id: 'analyst@bank.com',
          department: 'compliance',
          destination_domain: 'internal.bank.vault',
          source_action: 'File Scanner Ingestion',
          classification_tier: tier,
          risk_score: riskScore,
          enforcement_action: action,
          details: `Document inspection for "${selectedFile.name}" (${scanResult.fileSize})`
        });
      }

      if (scanResult.riskScore > 75) {
        toast.error(`High Risk Detected in ${selectedFile.name}: Exfiltration quarantined!`);
      } else if (scanResult.enforcementAction === 'MASK') {
        toast.success(`DLP Rule Triggered: Sensitive tokens masked via HMAC-SHA256.`);
      } else {
        toast.success(`Document cleared: No regulatory banking leaks detected.`);
      }

    } catch (err) {
      setScanning(false);
      console.error('File scan error:', err);
      toast.error('File scan failed. Ensure backend microservice is running.');
    }
  };

  const handleDrag = (e) => {
    e.preventDefault();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setIsDragOver(true);
    } else if (e.type === 'dragleave') {
      setIsDragOver(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileUpload(e.dataTransfer.files[0]);
    }
  };

  return (
    <div className="flex-1 p-8 space-y-8 select-none">
      <div>
        <h1 className="text-4xl font-extrabold tracking-tight uppercase font-sans text-white">
          DOCUMENT & FILE SCANNER
        </h1>
        <p className="text-sm text-[#8e8f96]">
          Multi-format gateway scanner supporting PDF, DOCX, XLSX, CSV, ZIP, TXT, and OCR Image Ingestion.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        
        {/* Left Column: Real Dropzone */}
        <div className="col-span-12 lg:col-span-7 flex flex-col gap-6">
          <div
            onDragEnter={handleDrag}
            onDragOver={handleDrag}
            onDragLeave={handleDrag}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
            className={`bg-[#0c0c0e] border border-dashed rounded-[28px] p-12 flex flex-col items-center justify-center transition-all duration-300 min-h-[360px] text-center cursor-pointer ${
              isDragOver ? 'border-[#8df85f] bg-[#121316]' : 'border-[#161619] hover:border-[#23252c]'
            }`}
          >
            <div className="w-16 h-16 rounded-full bg-[#121316] border border-[#21232a] flex items-center justify-center mb-4 text-[#8df85f]">
              <Upload className="w-7 h-7" />
            </div>

            <div className="text-base font-bold text-white mb-1">
              Drag & Drop Banking Documents Here
            </div>
            <p className="text-xs text-[#8e8f96] max-w-sm mb-6">
              Select or drop any real document (.pdf, .docx, .xlsx, .csv, .txt, .json, .zip, .png, .jpg) for server-side inspection.
            </p>

            <button
              type="button"
              onClick={(e) => {
                e.stopPropagation();
                fileInputRef.current?.click();
              }}
              className="bg-white text-black font-semibold text-xs px-6 py-2.5 rounded-xl hover:scale-105 transition cursor-pointer shadow-md"
            >
              Browse Files From Device
            </button>

            <input
              ref={fileInputRef}
              type="file"
              className="hidden"
              onChange={(e) => {
                if (e.target.files && e.target.files[0]) {
                  const selected = e.target.files[0];
                  e.target.value = '';
                  handleFileUpload(selected);
                }
              }}
            />
          </div>

          {/* Quick Demo Pre-load Samples */}
          <div className="flex flex-col gap-2 p-4 rounded-2xl bg-[#0c0c0e] border border-[#161619]">
            <div className="text-[11px] font-bold text-[#8e8f96] uppercase tracking-wider flex items-center gap-1.5">
              <Play className="w-3.5 h-3.5 text-[#8df85f]" />
              Quick-Test Live Demonstration Samples
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 pt-1">
              <button
                type="button"
                onClick={() => {
                  const sampleCSV = `Employee_ID,Name,Social_Security_Number,Department,Account_Number,Annual_Base_Salary\nEMP-10492,Alice Wright,123-45-6789,Executive Leadership,4532891234569812,$1450000\nEMP-10821,Robert Vance,987-65-4321,Finance,9021847291,$980000`;
                  const blob = new Blob([sampleCSV], { type: 'text/csv' });
                  const testFile = new File([blob], 'EXECUTIVE_PAYROLL_AND_COMPENSATION.csv', { type: 'text/csv' });
                  handleFileUpload(testFile);
                }}
                className="text-left p-3 rounded-xl bg-[#121316] border border-[#21232a] hover:border-[#8df85f] hover:bg-[#16171b] transition group cursor-pointer"
              >
                <div className="text-xs font-bold text-white group-hover:text-[#8df85f]">Payroll CSV</div>
                <div className="text-[10px] text-[#8e8f96]">SSN & Cards (RESTRICTED)</div>
              </button>
              <button
                type="button"
                onClick={() => {
                  const sampleWire = `CONFIDENTIAL WIRE TRANSFER MEMORANDUM\nBeneficiary: Barclays Bank UK\nSWIFT: BARCGB22XXX\nIBAN: GB29BARC20201534892144\nAmount: $14,850,000 USD\nReference: Escrow Settlement M&A`;
                  const blob = new Blob([sampleWire], { type: 'text/plain' });
                  const testFile = new File([blob], 'CONFIDENTIAL_WIRE_TRANSFER_MEMO.txt', { type: 'text/plain' });
                  handleFileUpload(testFile);
                }}
                className="text-left p-3 rounded-xl bg-[#121316] border border-[#21232a] hover:border-[#8df85f] hover:bg-[#16171b] transition group cursor-pointer"
              >
                <div className="text-xs font-bold text-white group-hover:text-[#8df85f]">Wire Transfer TXT</div>
                <div className="text-[10px] text-[#8e8f96]">IBAN & SWIFT (CONFIDENTIAL)</div>
              </button>
              <button
                type="button"
                onClick={() => {
                  const sampleSafe = `GLOBAL TECH ANNOUNCEMENT\nRelease Date: Q4 2026\nSecureFlow AI announces enterprise general availability of cryptographic zero-leak data loss prevention platform.`;
                  const blob = new Blob([sampleSafe], { type: 'text/plain' });
                  const testFile = new File([blob], 'BENIGN_PUBLIC_ANNOUNCEMENT.txt', { type: 'text/plain' });
                  handleFileUpload(testFile);
                }}
                className="text-left p-3 rounded-xl bg-[#121316] border border-[#21232a] hover:border-[#8df85f] hover:bg-[#16171b] transition group cursor-pointer"
              >
                <div className="text-xs font-bold text-white group-hover:text-[#8df85f]">Public Release TXT</div>
                <div className="text-[10px] text-[#8e8f96]">Clean Data (SAFE - ALLOW)</div>
              </button>
            </div>
          </div>
        </div>

        {/* Right Column: Scan Step Progress & Result Card */}
        <div className="col-span-12 lg:col-span-5 flex flex-col gap-6">
          <div className="bg-[#0c0c0e] border border-[#161619] rounded-[28px] p-6 space-y-6">
            <div className="flex items-center justify-between">
              <span className="text-[11px] font-bold tracking-wider text-[#8e8f96] uppercase">
                Scanner Inspection Engine
              </span>
              {scanning && (
                <span className="text-xs font-mono text-[#8df85f] flex items-center gap-1.5 animate-pulse">
                  <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                  ANALYZING
                </span>
              )}
            </div>

            {scanning && (
              <div className="p-4 rounded-2xl bg-[#121316] border border-[#21232a] space-y-3">
                <div className="text-xs font-semibold text-white flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-[#8df85f] animate-ping" />
                  Uploading and inspecting binary on FastAPI server...
                </div>
                <div className="w-full bg-[#1e2025] h-1.5 rounded-full overflow-hidden">
                  <div className="bg-[#8df85f] h-full rounded-full w-2/3 animate-pulse" />
                </div>
              </div>
            )}

            {result ? (
              <div className="space-y-6">
                <div className="flex items-baseline justify-between border-b border-[#161619] pb-4">
                  <div>
                    <div className="text-3xl font-extrabold text-white font-sans flex items-center gap-2">
                      <span className={result.riskScore > 75 ? 'text-[#f38933]' : 'text-white'}>
                        {result.riskScore}%
                      </span>
                      {result.riskScore > 75 && <AlertCircle className="w-5 h-5 text-[#f38933]" />}
                    </div>
                    <div className="text-[10px] font-semibold text-[#8e8f96] uppercase mt-0.5">
                      Calculated Document Risk ({result.latencyMs}ms)
                    </div>
                  </div>

                  <div className="text-right">
                    <span className={`px-2.5 py-1 rounded-full text-[10px] font-extrabold uppercase font-mono ${
                      result.enforcementAction === 'BLOCK'
                        ? 'bg-[#f38933]/15 text-[#f38933] border border-[#f38933]/30'
                        : result.enforcementAction === 'MASK'
                        ? 'bg-[#8df85f]/15 text-[#8df85f] border border-[#8df85f]/30'
                        : 'bg-white/10 text-white border border-white/20'
                    }`}>
                      {result.enforcementAction}
                    </span>
                    <div className="text-[10px] text-[#8e8f96] mt-1 font-mono">{result.tier}</div>
                  </div>
                </div>

                <div className="p-3.5 rounded-2xl bg-[#121316] border border-[#21232a] space-y-1">
                  <div className="text-[10px] font-bold uppercase tracking-wider text-[#8e8f96]">
                    Inspected File Metadata
                  </div>
                  <div className="text-xs font-bold text-white font-mono truncate">{result.fileName}</div>
                  <div className="text-[10px] text-[#8e8f96] font-mono">{result.fileSize}</div>
                </div>

                {/* Threat Intelligence & Explainability Card */}
                <div className="p-4 rounded-2xl bg-[#121316] border border-[#21232a] space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-1.5 text-[10px] font-bold uppercase tracking-wider text-[#8e8f96]">
                      <Info className="w-3.5 h-3.5 text-[#8df85f]" />
                      Threat Classification & Explainability
                    </div>
                    <span className={`px-2 py-0.5 rounded-full text-[9px] font-extrabold font-mono uppercase ${
                      result.threatCategory?.includes('CRITICAL') || result.threatCategory?.includes('EXPOSURE') || result.threatCategory?.includes('PAYMENT') || result.threatCategory?.includes('KEY')
                        ? 'bg-[#f38933]/20 text-[#f38933] border border-[#f38933]/40'
                        : result.threatCategory?.includes('INTERNAL') || result.threatCategory?.includes('CONFIDENTIAL')
                        ? 'bg-amber-400/20 text-amber-300 border border-amber-400/30'
                        : 'bg-[#8df85f]/15 text-[#8df85f] border border-[#8df85f]/30'
                    }`}>
                      {result.threatCategory || 'BENIGN_DATA'}
                    </span>
                  </div>

                  <p className="text-xs text-slate-200 leading-relaxed font-sans bg-black/30 p-2.5 rounded-xl border border-[#21232a]">
                    {result.explanation}
                  </p>

                  {/* Regulatory Compliance Badges */}
                  {result.complianceImpact && result.complianceImpact.length > 0 && (
                    <div className="space-y-1.5 pt-1">
                      <div className="flex items-center gap-1.5 text-[10px] font-semibold uppercase tracking-wider text-[#8e8f96]">
                        <Scale className="w-3 h-3 text-[#8e8f96]" />
                        Compliance & Regulatory Mapping
                      </div>
                      <div className="flex flex-wrap gap-1.5">
                        {result.complianceImpact.map((tag, idx) => (
                          <span
                            key={idx}
                            className="px-2 py-0.5 rounded-md bg-[#16181d] border border-[#262833] text-[10px] font-mono text-slate-300"
                          >
                            {tag}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Remediation Guidance */}
                  {result.remediationAdvice && (
                    <div className="pt-2 border-t border-[#21232a] text-[11px] text-[#8e8f96] flex items-start gap-1.5">
                      <CheckCircle2 className="w-3.5 h-3.5 text-[#8df85f] shrink-0 mt-0.5" />
                      <span><strong className="text-white">Remediation: </strong>{result.remediationAdvice}</span>
                    </div>
                  )}

                  {/* OpenTelemetry Granular Latency Breakdown */}
                  {result.latencyBreakdown && Object.keys(result.latencyBreakdown).length > 0 && (
                    <div className="pt-2 border-t border-[#21232a] flex items-center gap-2 flex-wrap text-[9px] font-mono text-[#8e8f96]">
                      <Activity className="w-3 h-3 text-[#8df85f]" />
                      <span>Trace:</span>
                      {result.latencyBreakdown.normalization_ms !== undefined && (
                        <span>norm:{result.latencyBreakdown.normalization_ms}ms</span>
                      )}
                      {result.latencyBreakdown.inference_ms !== undefined && (
                        <span>infer:{result.latencyBreakdown.inference_ms}ms</span>
                      )}
                      {result.latencyBreakdown.rules_ms !== undefined && (
                        <span>rules:{result.latencyBreakdown.rules_ms}ms</span>
                      )}
                      {result.latencyBreakdown.ner_ms !== undefined && (
                        <span>ner:{result.latencyBreakdown.ner_ms}ms</span>
                      )}
                      {result.latencyBreakdown.redaction_ms !== undefined && (
                        <span>redact:{result.latencyBreakdown.redaction_ms}ms</span>
                      )}
                      {result.latencyBreakdown.total_ms !== undefined && (
                        <span className="text-white font-bold">total:{result.latencyBreakdown.total_ms}ms</span>
                      )}
                    </div>
                  )}
                </div>

                {/* Detected Entities */}
                <div className="space-y-2">
                  <div className="text-[10px] font-bold uppercase tracking-wider text-[#8e8f96]">
                    DLP Detections ({result.detections.length})
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {result.detections.length > 0 ? (
                      result.detections.map((det, idx) => (
                        <span
                          key={idx}
                          className="px-2.5 py-1 rounded-xl bg-[#121316] border border-[#21232a] text-xs font-mono text-[#8df85f]"
                        >
                          {det}
                        </span>
                      ))
                    ) : (
                      <span className="text-xs text-[#8e8f96] italic">Clean payload: No PII flags raised.</span>
                    )}
                  </div>
                </div>

                {/* Sanitized output snippet */}
                {result.sanitizedSnippet && (
                  <div className="space-y-2 border-t border-[#161619] pt-4">
                    <div className="text-[10px] font-bold uppercase tracking-wider text-[#8e8f96]">
                      Sanitized Payload Preview
                    </div>
                    <div className="p-3 bg-[#121316] border border-[#21232a] rounded-xl text-xs font-mono text-white max-h-32 overflow-y-auto whitespace-pre-wrap select-all">
                      {result.sanitizedSnippet}
                    </div>
                  </div>
                )}
              </div>
            ) : !scanning ? (
              <div className="py-12 flex flex-col items-center justify-center text-center space-y-2 border border-dashed border-[#161619] rounded-2xl">
                <FileCheck className="w-8 h-8 text-[#8e8f96]" />
                <div className="text-xs font-semibold text-white">No active document scanned</div>
                <div className="text-[11px] text-[#8e8f96] max-w-xs">
                  Upload any document using the dropzone on the left to view server-side ONNX classification and PII extraction.
                </div>
              </div>
            ) : null}

          </div>
        </div>

      </div>
    </div>
  );
}
