import React, { useState, useEffect } from 'react';
import { Shield, Sparkles, RefreshCw, Eye, EyeOff, CheckCircle, AlertCircle } from 'lucide-react';
import toast from 'react-hot-toast';

export default function LiveClassification({ onNewLog }) {
  const [text, setText] = useState('');
  const [classification, setClassification] = useState({
    label: 'Public',
    riskScore: 0,
    piiList: [],
    maskedText: '',
    recommendation: 'Allow Transfer'
  });
  const [showMasked, setShowMasked] = useState(false);
  const [reported, setReported] = useState(false);

  const analyzeText = (val) => {
    if (!val.trim()) {
      return {
        label: 'Public',
        riskScore: 0,
        piiList: [],
        maskedText: '',
        recommendation: 'Allow Transfer'
      };
    }

    const ssnRegex = /\b\d{3}-\d{2}-\d{4}\b/g;
    const ccRegex = /\b(?:\d[ -]*?){13,16}\b/g;
    const apiKeyRegex = /\b(?:key|secret|token|password)[a-zA-Z0-9_]{10,30}\b/gi;
    const emailRegex = /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/g;

    const ssnMatches = val.match(ssnRegex) || [];
    const ccMatches = val.match(ccRegex) || [];
    const apiKeyMatches = val.match(apiKeyRegex) || [];
    const emailMatches = val.match(emailRegex) || [];

    const detections = [];
    let masked = val;

    if (ssnMatches.length > 0) {
      detections.push(`SSN (${ssnMatches.length}x)`);
      masked = masked.replace(ssnRegex, '[REDACTED SSN]');
    }
    if (ccMatches.length > 0) {
      detections.push(`Credit Card (${ccMatches.length}x)`);
      masked = masked.replace(ccRegex, '[REDACTED CREDIT CARD]');
    }
    if (apiKeyMatches.length > 0) {
      detections.push(`API Key (${apiKeyMatches.length}x)`);
      masked = masked.replace(apiKeyRegex, '[REDACTED API KEY]');
    }
    if (emailMatches.length > 0) {
      detections.push(`Email Address (${emailMatches.length}x)`);
      masked = masked.replace(emailRegex, '[REDACTED EMAIL]');
    }

    let score = Math.min(10, (ssnMatches.length + ccMatches.length + apiKeyMatches.length) * 15 + (emailMatches.length * 5));
    if (detections.length > 0) {
      score = Math.min(100, score + 40);
    }
    
    let label = 'Public';
    let recommendation = 'Allow Transfer';

    if (score > 80) {
      label = 'Highly Confidential';
      recommendation = 'Block Upload & Encrypt';
    } else if (score > 50) {
      label = 'Confidential';
      recommendation = 'Auto-Encrypt on Ingestion';
    } else if (score > 20) {
      label = 'Internal';
      recommendation = 'Mask PII before processing';
    }

    return {
      label,
      riskScore: score,
      piiList: detections,
      maskedText: masked,
      recommendation
    };
  };

  useEffect(() => {
    const delayDebounce = setTimeout(() => {
      const result = analyzeText(text);
      setClassification(result);
      setReported(false);
    }, 200);

    return () => clearTimeout(delayDebounce);
  }, [text]);

  const handleReportIncorrect = () => {
    setReported(true);
    toast.success('Classification marked as incorrect. Fed to ML retraining pipeline!');
    
    if (onNewLog) {
      onNewLog({
        source: 'Live Classification Monitor',
        fileName: 'live_clipboard_paste.txt',
        riskScore: classification.riskScore,
        category: classification.label,
        actionTaken: 'Reported Misclassification',
        piiDetected: classification.piiList,
        details: `User reported misclassification. Value parsed: "${text.substring(0, 40)}..."`
      });
    }
  };

  return (
    <div className="flex-1 p-8 space-y-8 select-none">
      <div>
        <h1 className="text-4xl font-extrabold tracking-tight uppercase font-sans text-white">
          LIVE CLASSIFICATION
        </h1>
        <p className="text-sm text-[#8e8f96]">Paste text in real-time to analyze risk profile, extract PII, and simulate DLP classifications.</p>
      </div>

      <div className="grid grid-cols-12 gap-8">
        <div className="col-span-7 flex flex-col gap-6">
          <div className="bg-[#0c0c0e] border border-[#161619] rounded-[28px] p-6 space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-white uppercase tracking-wider">Paste Text Content</span>
              <button
                onClick={() => setText('Demo PII paste: My social security number is 443-21-9982 and my api key is secret_token_abc123xyz.')}
                className="text-xs text-[#8df85f] hover:underline font-semibold"
              >
                Insert Sample PII
              </button>
            </div>
            
            <textarea
              value={text}
              onChange={e => setText(e.target.value)}
              placeholder="Paste content here to scan for sensitive tokens (SSN, credit card, API keys, emails)..."
              className="w-full h-80 bg-[#121316] border border-[#23252c] rounded-2xl p-4 text-sm text-white focus:outline-none focus:border-white transition-all font-mono resize-none leading-relaxed"
            />
          </div>
        </div>

        <div className="col-span-5">
          <div className="bg-[#0c0c0e] border border-[#161619] rounded-[28px] p-6 space-y-6 flex flex-col justify-between min-h-[440px]">
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-[#8e8f96] uppercase tracking-wider">Real-time Risk Metrics</span>
                <span className="flex items-center gap-1.5 text-xs text-[#8df85f] font-semibold bg-[#8df85f]/10 px-3 py-1 rounded-full">
                  <Sparkles className="w-3.5 h-3.5" />
                  Active Model
                </span>
              </div>

              <div className="space-y-2">
                <div className="text-xs text-[#8e8f96]">Sensitivity Level</div>
                <div className="flex items-center gap-3">
                  <span className={`text-2xl font-extrabold tracking-wide uppercase px-4 py-1.5 rounded-2xl ${
                    classification.label === 'Highly Confidential' ? 'bg-[#f38933] text-black font-extrabold' :
                    classification.label === 'Confidential' ? 'bg-white text-black font-extrabold' :
                    classification.label === 'Internal' ? 'bg-[#8df85f] text-black font-extrabold' :
                    'bg-[#121316] text-[#8e8f96] border border-[#23252c]'
                  }`}>
                    {classification.label}
                  </span>
                </div>
              </div>

              <div className="space-y-2">
                <div className="flex justify-between text-xs font-semibold text-[#8e8f96]">
                  <span>Risk Score Gauge</span>
                  <span className={classification.riskScore > 80 ? 'text-[#f38933] font-bold animate-pulse' : 'text-white'}>
                    {classification.riskScore}%
                  </span>
                </div>
                <div className="h-3 w-full bg-[#121316] rounded-full overflow-hidden border border-[#23252c]">
                  <div 
                    className="h-full transition-all duration-500 rounded-full"
                    style={{ 
                      width: `${classification.riskScore}%`,
                      backgroundColor: classification.riskScore > 80 ? '#f38933' : classification.riskScore > 50 ? '#ffffff' : '#8df85f'
                    }}
                  />
                </div>
              </div>

              <div className="space-y-2">
                <div className="text-xs text-[#8e8f96]">Identified PII Entities</div>
                {classification.piiList.length > 0 ? (
                  <div className="flex flex-wrap gap-2">
                    {classification.piiList.map((pii, i) => (
                      <span key={i} className="text-[10px] font-bold text-white bg-[#121316] border border-[#23252c] px-3 py-1.5 rounded-xl flex items-center gap-1.5">
                        <AlertCircle className="w-3.5 h-3.5 text-[#f38933]" />
                        {pii}
                      </span>
                    ))}
                  </div>
                ) : (
                  <div className="text-xs text-[#8e8f96] italic bg-[#121316]/50 border border-[#23252c]/50 p-3 rounded-xl">
                    No PII tokens matched in the scanner buffer.
                  </div>
                )}
              </div>

              <div className="space-y-1">
                <div className="text-xs text-[#8e8f96]">DLP Gateway Action Recommendation</div>
                <div className="text-sm font-bold text-white font-mono">{classification.recommendation}</div>
              </div>
            </div>

            <div className="flex items-center gap-3 border-t border-[#161619] pt-6">
              <button
                onClick={() => setShowMasked(!showMasked)}
                disabled={!text.trim()}
                className={`flex-1 h-12 rounded-xl flex items-center justify-center gap-2 font-semibold text-xs transition cursor-pointer border ${
                  showMasked 
                    ? 'bg-white text-black border-white' 
                    : 'bg-[#121316] text-white border-[#23252c] hover:border-white'
                }`}
              >
                {showMasked ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                {showMasked ? 'Show Original' : 'Toggle PII Masking'}
              </button>

              <button
                onClick={handleReportIncorrect}
                disabled={!text.trim() || reported}
                className="h-12 px-4 rounded-xl border border-[#23252c] text-[#8e8f96] hover:text-white hover:border-white disabled:opacity-50 disabled:cursor-not-allowed transition flex items-center justify-center gap-1.5"
              >
                <RefreshCw className="w-4 h-4" />
                Report Error
              </button>
            </div>
          </div>
        </div>
      </div>

      {showMasked && text.trim() && (
        <div className="bg-[#0c0c0e] border border-[#161619] rounded-[28px] p-6 space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-[#8df85f] uppercase tracking-wider flex items-center gap-1.5">
              <CheckCircle className="w-4 h-4" />
              Ingestion Stream Preview (PII Redacted)
            </span>
          </div>
          <pre className="bg-[#121316] border border-[#23252c] rounded-2xl p-4 text-xs text-[#8e8f96] font-mono leading-relaxed overflow-x-auto whitespace-pre-wrap">
            {classification.maskedText}
          </pre>
        </div>
      )}
    </div>
  );
}
