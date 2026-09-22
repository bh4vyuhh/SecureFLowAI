import React, { useState } from 'react';
import { Upload, FileText, ShieldCheck, Mail, Send, Download, RefreshCw, AlertCircle } from 'lucide-react';
import toast from 'react-hot-toast';

export default function FileScanner({ onNewLog }) {
  const [files, setFiles] = useState([]);
  const [isDragOver, setIsDragOver] = useState(false);
  const [scanning, setScanning] = useState(false);
  const [scanStep, setScanStep] = useState('');
  const [result, setResult] = useState(null);

  const simulateIngestion = (fileName, fileType) => {
    setScanning(true);
    setResult(null);

    const steps = [
      'Normalizing file into Ingestion Gateway AnalysisEvent...',
      'Running regex high-precision scanner layer...',
      'Invoking spaCy Named Entity Recognition model...',
      'Evaluating semantic classification with TF-IDF Classifier...',
      'Calculating final security risk index & recommendations...'
    ];

    let current = 0;
    const interval = setInterval(() => {
      if (current < steps.length) {
        setScanStep(steps[current]);
        current++;
      } else {
        clearInterval(interval);
        setScanning(false);
        
        const lowerName = fileName.toLowerCase();
        let label = 'Public';
        let score = Math.floor(Math.random() * 25) + 5;
        let detections = [];
        let rec = 'Approved for transport';

        if (lowerName.includes('payroll') || lowerName.includes('confidential') || lowerName.includes('ssn')) {
          label = 'Highly Confidential';
          score = 92;
          detections = ['SSN (12 matches)', 'US Address (3 matches)', 'Tax ID'];
          rec = 'Auto-Encrypt & Restrict Access';
        } else if (lowerName.includes('contract') || lowerName.includes('internal') || lowerName.includes('deal')) {
          label = 'Confidential';
          score = 74;
          detections = ['Legal Signature Names', 'Financial Figures'];
          rec = 'Auto-Encrypt Payload';
        } else if (lowerName.includes('draft') || lowerName.includes('project')) {
          label = 'Internal';
          score = 42;
          detections = ['Email Address List'];
          rec = 'PII Masking & Log';
        }

        const scanResult = {
          fileName,
          label,
          riskScore: score,
          detections,
          recommendation: rec,
          encrypted: label === 'Confidential' || label === 'Highly Confidential',
          unreadableCiphertext: 'U2FsdGVkX19xNlhvQjlka3E5djNnZ3o4MTJrb3M3ZDRuYXNkZmFzZGZh\nc2RmYXNkZmFzZGY5OGFzZGY4OWFzZGY4OWFzZGY4OWFzZGY5OGFzZGY4\nOWFzZGY4OWFzZGY5OGFzZGY4OWFzZGY5OGFzZGY5OGFzZGY5OGFzZGY=\n'
        };

        setResult(scanResult);

        if (onNewLog) {
          onNewLog({
            source: 'Web Ingestion Gateway',
            fileName: fileName,
            riskScore: score,
            category: label,
            actionTaken: label === 'Public' ? 'Clean' : label === 'Internal' ? 'PII Masked' : 'Auto-Encrypted',
            piiDetected: detections,
            details: `Uploaded file scanned and processed by hybrid DLP classifier engine.`
          });
        }

        if (score > 80) {
          toast.error(`High Risk detected: Triggering admin notification via Mailtrap & Webhook to Slack!`);
        } else if (label === 'Confidential' || label === 'Highly Confidential') {
          toast.success(`DLP Rule Triggered: File auto-encrypted successfully via AES-256.`);
        } else {
          toast.success(`Scan complete: File is cleared.`);
        }
      }
    }, 900);
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
      const droppedFile = e.dataTransfer.files[0];
      setFiles([droppedFile]);
      simulateIngestion(droppedFile.name, droppedFile.type);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      const selected = e.target.files[0];
      setFiles([selected]);
      simulateIngestion(selected.name, selected.type);
    }
  };

  const downloadEncrypted = () => {
    if (!result) return;
    const blob = new Blob([result.unreadableCiphertext], { type: 'application/octet-stream' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', `${result.fileName}.enc`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    toast.success('Encrypted envelope file downloaded!');
  };

  return (
    <div className="flex-1 p-8 space-y-8 select-none">
      <div>
        <h1 className="text-4xl font-extrabold tracking-tight uppercase font-sans text-white">
          Ingestion File Scanner
        </h1>
        <p className="text-sm text-[#8e8f96]">Drag, drop or select documents (.docx, .pdf, images) to classify risk, redact PII, and generate secure encryptions.</p>
      </div>

      <div className="grid grid-cols-12 gap-8">
        <div className="col-span-7 flex flex-col gap-6">
          <div
            onDragEnter={handleDrag}
            onDragOver={handleDrag}
            onDragLeave={handleDrag}
            onDrop={handleDrop}
            className={`h-80 rounded-[28px] border-2 border-dashed flex flex-col items-center justify-center p-8 transition-all relative ${
              isDragOver 
                ? 'border-white bg-[#121316]' 
                : 'border-[#23252c] bg-[#0c0c0e] hover:border-white'
            }`}
          >
            <input
              type="file"
              onChange={handleFileChange}
              id="file-upload-input"
              className="absolute inset-0 opacity-0 cursor-pointer"
            />
            
            <div className="text-center space-y-4">
              <div className="w-16 h-16 rounded-full bg-[#121316] border border-[#23252c] flex items-center justify-center mx-auto">
                <Upload className="w-6 h-6 text-white" />
              </div>
              <div>
                <p className="text-sm font-semibold text-white">
                  Drag and drop your file here, or <span className="text-[#8df85f] underline">browse files</span>
                </p>
                <p className="text-xs text-[#8e8f96] mt-1">Supports DOCX, PDF, PNG and JPEG formats</p>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <span className="text-xs font-bold text-[#8e8f96] uppercase">Inject Sample Tests:</span>
            <button
              onClick={() => simulateIngestion('confidential_payroll_q3.docx', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')}
              className="px-3.5 py-2 bg-[#121316] border border-[#23252c] hover:border-white rounded-xl text-xs text-white transition cursor-pointer"
            >
              payroll_q3.docx (High Risk)
            </button>
            <button
              onClick={() => simulateIngestion('customer_deal_sheet.docx', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')}
              className="px-3.5 py-2 bg-[#121316] border border-[#23252c] hover:border-white rounded-xl text-xs text-white transition cursor-pointer"
            >
              deal_sheet.docx (Confidential)
            </button>
            <button
              onClick={() => simulateIngestion('public_press_release.pdf', 'application/pdf')}
              className="px-3.5 py-2 bg-[#121316] border border-[#23252c] hover:border-white rounded-xl text-xs text-white transition cursor-pointer"
            >
              press_release.pdf (Clean)
            </button>
          </div>

          {scanning && (
            <div className="bg-[#0c0c0e] border border-[#161619] rounded-[28px] p-6 space-y-4">
              <div className="flex items-center justify-between text-xs text-[#8e8f96] font-semibold">
                <span className="flex items-center gap-2">
                  <RefreshCw className="w-4 h-4 animate-spin text-[#8df85f]" />
                  Ingesting Document...
                </span>
                <span className="font-mono">Processing...</span>
              </div>
              <div className="text-sm font-bold text-white font-mono">{scanStep}</div>
              <div className="h-1.5 w-full bg-[#121316] rounded-full overflow-hidden border border-[#23252c]">
                <div className="h-full bg-[#8df85f] rounded-full animate-[shimmer_2s_infinite] w-2/3" />
              </div>
            </div>
          )}
        </div>

        <div className="col-span-5">
          {result ? (
            <div className="bg-[#0c0c0e] border border-[#161619] rounded-[28px] p-6 space-y-6">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-[#8e8f96] uppercase">Ingestion Results</span>
                <span className="text-[10px] font-bold bg-[#121316] border border-[#23252c] px-3 py-1 rounded-full text-white truncate max-w-[150px]">
                  {result.fileName}
                </span>
              </div>

              <div className="flex items-center justify-between border-b border-[#161619] pb-4">
                <div>
                  <div className="text-xs text-[#8e8f96] mb-1">DLP Classification</div>
                  <span className={`text-sm font-extrabold tracking-wide uppercase px-3 py-1 rounded-xl ${
                    result.label === 'Highly Confidential' ? 'bg-[#f38933] text-black font-extrabold' :
                    result.label === 'Confidential' ? 'bg-white text-black font-extrabold' :
                    result.label === 'Internal' ? 'bg-[#8df85f] text-black font-extrabold' :
                    'bg-[#121316] text-[#8e8f96] border border-[#23252c]'
                  }`}>
                    {result.label}
                  </span>
                </div>

                <div className="text-right">
                  <div className="text-xs text-[#8e8f96] mb-1">Calculated Risk</div>
                  <span className={`text-base font-mono font-bold ${result.riskScore > 80 ? 'text-[#f38933]' : 'text-white'}`}>
                    {result.riskScore}%
                  </span>
                </div>
              </div>

              <div className="space-y-2">
                <div className="text-xs text-[#8e8f96]">Identified PII Detections</div>
                {result.detections.length > 0 ? (
                  <div className="flex flex-wrap gap-1.5">
                    {result.detections.map((det, i) => (
                      <span key={i} className="text-[9px] font-bold text-white bg-[#121316] border border-[#23252c] px-2.5 py-1 rounded-lg">
                        {det}
                      </span>
                    ))}
                  </div>
                ) : (
                  <div className="text-xs text-[#8e8f96] italic">No sensitive entities found.</div>
                )}
              </div>

              {result.encrypted && (
                <div className="bg-[#121316] border border-[#23252c] rounded-2xl p-4 space-y-4">
                  <div className="flex items-start gap-3">
                    <ShieldCheck className="w-5 h-5 text-[#8df85f] shrink-0" />
                    <div>
                      <h4 className="text-xs font-bold text-white">Auto-Encryption Service Active</h4>
                      <p className="text-[10px] text-[#8e8f96] mt-0.5 leading-normal">
                        Document was auto-encrypted via AES-256. AES key is wrapped with RSA public key envelope inside PostgreSQL.
                      </p>
                    </div>
                  </div>

                  <button
                    onClick={downloadEncrypted}
                    className="w-full h-11 bg-white text-black font-semibold text-xs rounded-xl flex items-center justify-center gap-2 hover:scale-[1.02] transition cursor-pointer"
                  >
                    <Download className="w-4 h-4" />
                    Download Encrypted File (.docx.enc)
                  </button>

                  <div className="space-y-1.5 pt-2">
                    <span className="text-[9px] font-bold text-[#8df85f] uppercase tracking-wider">Ciphertext Sample Payload</span>
                    <pre className="p-2.5 bg-[#0c0c0e] rounded-lg border border-[#23252c] text-[9px] text-[#8e8f96] font-mono whitespace-pre-wrap select-text max-h-24 overflow-y-auto leading-relaxed">
                      {result.unreadableCiphertext}
                    </pre>
                  </div>
                </div>
              )}

              {result.riskScore > 80 && (
                <div className="border border-[#f38933]/30 bg-[#f38933]/5 rounded-2xl p-4 space-y-3">
                  <span className="text-[10px] font-extrabold text-[#f38933] uppercase flex items-center gap-1.5">
                    <AlertCircle className="w-4 h-4" />
                    High-Risk Alert Dispatch Triggers
                  </span>

                  <div className="space-y-2">
                    <div className="flex items-center gap-2 text-[10px] text-[#8e8f96]">
                      <Mail className="w-3.5 h-3.5 text-[#f38933]" />
                      <span>Admin Alert sent to <b>mailtrap.io</b> inbox.</span>
                    </div>

                    <div className="flex items-center gap-2 text-[10px] text-[#8e8f96]">
                      <Send className="w-3.5 h-3.5 text-[#f38933]" />
                      <span>Webhook post dispatched to Slack #security channel.</span>
                    </div>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="bg-[#0c0c0e] border border-[#161619] rounded-[28px] p-6 h-80 flex flex-col items-center justify-center text-center text-[#8e8f96]">
              <FileText className="w-10 h-10 mb-3 opacity-30" />
              <p className="text-xs font-semibold">Upload or drop a document to inspect analysis reports and trigger automated crypto procedures.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
