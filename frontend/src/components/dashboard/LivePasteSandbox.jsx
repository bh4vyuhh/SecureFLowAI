import React, { useState } from 'react';
import { useToast } from '../../contexts/ToastContext';
import { ShieldAlert, Brain, Terminal, ShieldAlert as AlertIcon } from 'lucide-react';

export const LivePasteSandbox = () => {
  const [inputText, setInputText] = useState('');
  const [analysisResult, setAnalysisResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const { success, warning } = useToast();

  const handlePasteAnalyze = async () => {
    if (!inputText.trim()) return;
    setLoading(true);

    setTimeout(() => {
      let riskScore = 15;
      let label = 'Public';
      let detections = [];
      let recommendation = 'No action required';

      const ssnPattern = /\b\d{3}-\d{2}-\d{4}\b/;
      const ccPattern = /\b(?:\d[ -]*?){13,16}\b/;
      const apiKeyPattern = /xox[bap]-[0-9]{12}/i;

      if (ssnPattern.test(inputText)) {
        riskScore = 95;
        label = 'Highly Confidential';
        detections.push('SSN Sequence Detected');
        recommendation = 'Auto-encrypt & Redact PII';
      } else if (ccPattern.test(inputText)) {
        riskScore = 88;
        label = 'Highly Confidential';
        detections.push('Credit Card Pattern');
        recommendation = 'Mask & Flag Alert';
      } else if (apiKeyPattern.test(inputText)) {
        riskScore = 84;
        label = 'Confidential';
        detections.push('Slack Auth Secret');
        recommendation = 'Restrict access & Notify Admin';
      } else if (/confidential|private|secret/i.test(inputText)) {
        riskScore = 55;
        label = 'Confidential';
        detections.push('Keywords signaling internal restrictions');
        recommendation = 'Review Access Rights';
      }

      const result = {
        label,
        riskScore,
        confidence: 0.94,
        detections,
        recommendation
      };

      setAnalysisResult(result);
      setLoading(false);

      if (riskScore >= 80) {
        warning('High Risk Detected', `Classification: ${label} (Risk score: ${riskScore})`);
      } else {
        success('Scan Completed', `Content classified as ${label}`);
      }
    }, 800);
  };

  const getLabelColor = (lbl) => {
    switch (lbl) {
      case 'Highly Confidential': return 'var(--danger)';
      case 'Confidential': return 'var(--warning)';
      case 'Internal': return 'var(--blue-ai)';
      default: return 'var(--success)';
    }
  };

  return (
    <div className="chart-card" style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
      <div className="chart-header" style={{ marginBottom: 0 }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
            <div className="chart-title">Live Monitor Sandbox</div>
            <span className="ai-badge">
              <span className="ai-badge-dot" />
              Realtime
            </span>
          </div>
          <div className="chart-subtitle">Paste sensitive text to test instant AI classification</div>
        </div>
      </div>

      <div style={{ position: 'relative' }}>
        <textarea
          style={{
            width: '100%',
            height: 120,
            background: 'var(--bg-surface-2)',
            border: '1px solid var(--border)',
            borderRadius: 'var(--radius-md)',
            padding: 14,
            fontSize: '0.82rem',
            color: 'var(--text-primary)',
            fontFamily: 'var(--font-mono)',
            outline: 'none',
            resize: 'none'
          }}
          placeholder="Paste log dump, email transcripts, or test PII data here..."
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
        />
        <button
          onClick={handlePasteAnalyze}
          disabled={loading || !inputText.trim()}
          style={{
            position: 'absolute',
            bottom: 12,
            right: 12,
            background: 'var(--accent)',
            color: '#fff',
            border: 'none',
            borderRadius: 'var(--radius-xs)',
            padding: '6px 14px',
            fontSize: '0.75rem',
            fontWeight: 600,
            cursor: 'pointer',
            opacity: inputText.trim() ? 1 : 0.6
          }}
        >
          {loading ? 'Analyzing...' : 'Analyze Text'}
        </button>
      </div>

      {analysisResult && (
        <div style={{
          background: 'var(--bg-surface-2)',
          border: '1px solid var(--border-strong)',
          borderRadius: 'var(--radius-md)',
          padding: 14,
          animation: 'fadeIn var(--duration-base) ease-out'
        }}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginBottom: 12 }}>
            <div>
              <span style={{ fontSize: '0.68rem', color: 'var(--text-muted)' }}>Class Label</span>
              <div style={{ fontSize: '0.9rem', fontWeight: 700, color: getLabelColor(analysisResult.label) }}>
                {analysisResult.label}
              </div>
            </div>
            <div>
              <span style={{ fontSize: '0.68rem', color: 'var(--text-muted)' }}>Risk Score</span>
              <div style={{ fontSize: '0.9rem', fontWeight: 700, color: getRiskColor(analysisResult.riskScore), fontFamily: 'var(--font-mono)' }}>
                {analysisResult.riskScore}
              </div>
            </div>
          </div>

          {analysisResult.detections.length > 0 && (
            <div style={{ marginBottom: 10 }}>
              <span style={{ fontSize: '0.68rem', color: 'var(--text-muted)' }}>Detections</span>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginTop: 4 }}>
                {analysisResult.detections.map((d, i) => (
                  <span key={i} style={{
                    fontSize: '0.7rem',
                    padding: '2px 8px',
                    borderRadius: 4,
                    background: 'rgba(239,68,68,0.12)',
                    color: 'var(--danger-light)',
                    border: '1px solid rgba(239,68,68,0.2)'
                  }}>{d}</span>
                ))}
              </div>
            </div>
          )}

          <div>
            <span style={{ fontSize: '0.68rem', color: 'var(--text-muted)' }}>Response Action</span>
            <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', marginTop: 2, display: 'flex', alignItems: 'center', gap: 5 }}>
              <Terminal size={12} />
              {analysisResult.recommendation}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default LivePasteSandbox;
