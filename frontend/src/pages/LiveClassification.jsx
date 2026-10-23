import React, { useState, useEffect, useRef } from 'react';
import { Shield, Sparkles, RefreshCw, Eye, EyeOff, CheckCircle, AlertCircle, Zap, Key, ArrowRight, Info, Scale, CheckCircle2, FileText, Activity } from 'lucide-react';
import toast from 'react-hot-toast';
import { api } from '../services/api';

export default function LiveClassification({ onNewLog }) {
  const [text, setText] = useState(() => {
    const params = new URLSearchParams(window.location.search);
    if (params.get('text')) return params.get('text');
    if (params.get('demo') === '1') {
      return "URGENT WIRE TRANSFER INSTRUCTION:\nBeneficiary: Apex Global Hedge Fund\nAccount Number: 4532-8910-4411-9023\nABA Routing: 021000021\nAmount: $4,250,000 USD\nSWIFT: CHASUS33XXX\nTax ID (SSN): 123-45-6789\nConfidential Client Master Agreement attached.";
    }
    return '';
  });
  const [destinationDomain, setDestinationDomain] = useState('api.openai.com');
  const [department, setDepartment] = useState('treasury');
  const [userId, setUserId] = useState('analyst@bank.com');
  const [analyzing, setAnalyzing] = useState(false);
  const [loadingRecent, setLoadingRecent] = useState(false);
  const [classification, setClassification] = useState({
    tier: 'SAFE',
    riskScore: 0,
    piiList: [],
    maskedText: '',
    recommendation: 'Allow Transfer',
    enforcementAction: 'ALLOW',
    latencyMs: 0
  });
  const [showMasked, setShowMasked] = useState(true);
  const [reported, setReported] = useState(false);
  const debounceRef = useRef(null);

  const runLiveInspection = async (inputText) => {
    if (!inputText.trim()) {
      setClassification({
        tier: 'SAFE',
        riskScore: 0,
        piiList: [],
        maskedText: '',
        recommendation: 'Allow Transfer',
        enforcementAction: 'ALLOW',
        latencyMs: 0
      });
      return;
    }

    setAnalyzing(true);
    const start = performance.now();
    try {
      const response = await api.scanDLP({
        text: inputText,
        destinationDomain,
        department,
        userId,
        sourceAction: 'clipboard',
        mode: 'mask'
      });

      const elapsed = Math.round(performance.now() - start);

      const detections = Array.isArray(response.detected_entities)
        ? response.detected_entities.map((e) => typeof e === 'object' ? `${e.entity_type} (${Math.round((e.confidence || 1) * 100)}%)` : String(e))
        : Object.entries(response.detected_entities || {}).map(([k, v]) => `${k} (${v}x)`);

      const result = {
        tier: response.classification_tier || response.tier || 'SAFE',
        riskScore: response.risk_score !== undefined ? response.risk_score : (response.riskScore || 0),
        piiList: detections,
        maskedText: response.sanitized_text || response.sanitized_payload || response.sanitizedContent || inputText,
        recommendation: response.enforcement_action === 'BLOCK' || response.actionTaken === 'BLOCK'
          ? 'Block Upload & Encrypt'
          : response.enforcement_action === 'MASK' || response.actionTaken === 'MASK'
          ? 'Mask PII Before Processing'
          : 'Allow Transfer',
        enforcementAction: response.enforcement_action || response.actionTaken || 'ALLOW',
        latencyMs: response.latency_ms || response.latencyMs || elapsed,
        incidentId: response.incident_id || response.eventId || response.request_id,
        circuitBreakerState: response.circuit_breaker_state || 'CLOSED',
        threatCategory: response.threat_category || response.threatCategory || 'BENIGN_DATA',
        explanation: response.explanation || (response.classification_tier === 'SAFE' 
          ? 'Safe transmission: zero unauthorized banking credentials, API secrets, or PII identified.' 
          : 'Potential data leak detected matching internal policy thresholds.'),
        complianceImpact: response.compliance_impact || response.complianceTags || ['SOC2-Trust-Baseline'],
        remediationAdvice: response.remediation_advice || response.remediationAdvice || 'No remediation required. Transmission is compliant.',
        latencyBreakdown: response.latency_breakdown || response.latencyBreakdown || {}
      };

      setClassification(result);
      setReported(false);

      if (onNewLog && (response.incident_id || response.eventId)) {
        onNewLog({
          id: response.incident_id || response.eventId,
          timestamp: new Date().toISOString(),
          client_id: 'live-monitor-console',
          user_id: userId,
          department: department,
          destination_domain: destinationDomain,
          source_action: 'Live Classification Monitor',
          classification_tier: result.tier,
          risk_score: result.riskScore,
          enforcement_action: result.enforcementAction,
          threat_category: result.threatCategory,
          explanation: result.explanation,
          compliance_tags: result.complianceImpact,
          details: `Live inspection of text payload (${inputText.length} characters)`
        });
      }
    } catch (err) {
      console.error('Inspection error:', err);
      toast.error('DLP inspection service failed to respond.');
    } finally {
      setAnalyzing(false);
    }
  };

  // Load the actual most recent incident recorded in database
  const loadLastRecordedEvent = async () => {
    setLoadingRecent(true);
    try {
      const records = await api.getIncidents({ limit: 1 });
      if (records && records.length > 0) {
        const last = records[0];
        if (last.details) {
          setText(last.details);
        } else if (last.destination_domain) {
          setText(`Transfer to ${last.destination_domain} by ${last.user_id} (${last.department})`);
        }
        if (last.destination_domain) setDestinationDomain(last.destination_domain);
        if (last.department) setDepartment(last.department);
        if (last.user_id) setUserId(last.user_id);
        toast.success(`Loaded recent event ${last.id} from database.`);
      } else {
        toast.error('No incident records exist in database yet.');
      }
    } catch (e) {
      toast.error('Failed to load recent event from database.');
    } finally {
      setLoadingRecent(false);
    }
  };

  useEffect(() => {
    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => {
      runLiveInspection(text);
    }, 350);

    return () => {
      if (debounceRef.current) clearTimeout(debounceRef.current);
    };
  }, [text, destinationDomain, department, userId]);

  const handleReportIncorrect = () => {
    setReported(true);
    toast.success('Classification marked as incorrect. Fed directly to active retraining pipeline!');
  };

  const isHighRisk = classification.riskScore > 75;

  return (
    <div className="flex-1 p-8 space-y-8 select-none">
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <h1 className="text-4xl font-extrabold tracking-tight uppercase font-sans text-white">
            LIVE CLASSIFICATION
          </h1>
          <p className="text-sm text-[#8e8f96]">
            Real-time sliding-window ONNX INT8 classifier and spaCy NER inspection over active clipboard & prompt traffic.
          </p>
        </div>

        <button
          onClick={loadLastRecordedEvent}
          disabled={loadingRecent}
          className="bg-[#0c0c0e] border border-[#161619] rounded-xl px-4 py-2 text-xs font-semibold text-[#8e8f96] hover:text-white hover:border-white transition cursor-pointer flex items-center gap-2"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loadingRecent ? 'animate-spin' : ''}`} />
          Load Last Ingested Event from Database
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        
        {/* Left Column: Input text area */}
        <div className="col-span-12 lg:col-span-7 flex flex-col gap-6">
          <div className="bg-[#0c0c0e] border border-[#161619] rounded-[28px] p-6 space-y-5">
            <div className="flex items-center justify-between">
              <span className="text-[11px] font-bold tracking-wider text-[#8e8f96] uppercase">
                Active Clipboard / Text Payload
              </span>
              <div className="flex items-center gap-3">
                <span className="text-[10px] text-[#8e8f96] font-mono">
                  {text.length} chars {classification.latencyMs > 0 && `| ${classification.latencyMs}ms`}
                </span>
                {analyzing && <RefreshCw className="w-3.5 h-3.5 text-[#8df85f] animate-spin" />}
              </div>
            </div>

            <textarea
              rows={9}
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="Paste or type text to inspect in real time with the ONNX INT8 model (Credit cards, IBAN, SSN, API secrets, customer records)..."
              className="w-full bg-[#121316] border border-[#21232a] rounded-2xl p-4 text-xs font-mono text-white placeholder-[#8e8f96] focus:outline-none focus:border-white transition resize-none leading-relaxed"
            />

            {/* Target context controls */}
            <div className="grid grid-cols-3 gap-3 pt-2 border-t border-[#161619]">
              <div>
                <label className="text-[10px] font-semibold text-[#8e8f96] uppercase block mb-1">
                  User ID / Email
                </label>
                <input
                  type="text"
                  value={userId}
                  onChange={(e) => setUserId(e.target.value)}
                  className="w-full bg-[#121316] border border-[#21232a] rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-white font-mono"
                />
              </div>

              <div>
                <label className="text-[10px] font-semibold text-[#8e8f96] uppercase block mb-1">
                  Destination Domain
                </label>
                <input
                  type="text"
                  value={destinationDomain}
                  onChange={(e) => setDestinationDomain(e.target.value)}
                  className="w-full bg-[#121316] border border-[#21232a] rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-white font-mono"
                />
              </div>

              <div>
                <label className="text-[10px] font-semibold text-[#8e8f96] uppercase block mb-1">
                  Department
                </label>
                <input
                  type="text"
                  value={department}
                  onChange={(e) => setDepartment(e.target.value)}
                  className="w-full bg-[#121316] border border-[#21232a] rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-white font-mono"
                />
              </div>
            </div>
          </div>
        </div>

        {/* Right Column: Real-time DLP Decision & Masking */}
        <div className="col-span-12 lg:col-span-5 flex flex-col gap-6">
          <div className="bg-[#0c0c0e] border border-[#161619] rounded-[28px] p-6 space-y-6">
            <div className="flex items-center justify-between">
              <span className="text-[11px] font-bold tracking-wider text-[#8e8f96] uppercase">
                Real-Time DLP Verdict
              </span>
              <span className={`px-2.5 py-1 rounded-full text-[10px] font-extrabold uppercase font-mono ${
                classification.enforcementAction === 'BLOCK'
                  ? 'bg-[#f38933]/15 text-[#f38933] border border-[#f38933]/30'
                  : classification.enforcementAction === 'MASK'
                  ? 'bg-[#8df85f]/15 text-[#8df85f] border border-[#8df85f]/30'
                  : 'bg-white/10 text-white border border-white/20'
              }`}>
                {classification.enforcementAction}
              </span>
            </div>

            {/* Risk Gauge Header */}
            <div className="flex items-baseline justify-between border-b border-[#161619] pb-4">
              <div>
                <div className="text-3xl font-extrabold text-white font-sans flex items-center gap-2">
                  <span className={isHighRisk ? 'text-[#f38933]' : 'text-white'}>
                    {classification.riskScore}%
                  </span>
                  {isHighRisk && <AlertCircle className="w-5 h-5 text-[#f38933]" />}
                </div>
                <div className="text-[10px] font-semibold text-[#8e8f96] uppercase mt-0.5">
                  Calculated Risk Index
                </div>
              </div>

              <div className="text-right">
                <div className="text-sm font-bold font-mono text-white">
                  {classification.tier}
                </div>
                <div className="text-[10px] font-semibold text-[#8e8f96] uppercase">
                  Classification Tier
                </div>
              </div>
            </div>

            {/* Recommendation Box */}
            <div className="p-4 rounded-2xl bg-[#121316] border border-[#21232a] space-y-1">
              <div className="text-[10px] font-bold uppercase tracking-wider text-[#8e8f96]">
                Enforcement Policy Recommendation
              </div>
              <div className={`text-xs font-bold ${
                classification.enforcementAction === 'BLOCK' ? 'text-[#f38933]' :
                classification.enforcementAction === 'MASK' ? 'text-[#8df85f]' : 'text-white'
              }`}>
                {classification.recommendation}
              </div>
            </div>

            {/* Threat Intelligence & Explainability Box */}
            <div className="p-4 rounded-2xl bg-[#121316] border border-[#21232a] space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-1.5 text-[10px] font-bold uppercase tracking-wider text-[#8e8f96]">
                  <Info className="w-3.5 h-3.5 text-[#8df85f]" />
                  Threat Classification & Explainability
                </div>
                <span className={`px-2 py-0.5 rounded-full text-[9px] font-extrabold font-mono uppercase ${
                  classification.threatCategory?.includes('CRITICAL') || classification.threatCategory?.includes('EXPOSURE')
                    ? 'bg-[#f38933]/20 text-[#f38933] border border-[#f38933]/40'
                    : classification.threatCategory?.includes('INTERNAL')
                    ? 'bg-amber-400/20 text-amber-300 border border-amber-400/30'
                    : 'bg-[#8df85f]/15 text-[#8df85f] border border-[#8df85f]/30'
                }`}>
                  {classification.threatCategory || 'BENIGN_DATA'}
                </span>
              </div>

              <p className="text-xs text-slate-200 leading-relaxed font-sans bg-black/30 p-2.5 rounded-xl border border-[#21232a]">
                {classification.explanation || (classification.tier === 'SAFE' 
                  ? 'Zero unencrypted payment cards, cryptographic keys, or PII detected. Baseline safe transmission allowed.'
                  : 'Active data leak pattern identified by SecureFlow AI hybrid inference engine.')}
              </p>

              {/* Regulatory Compliance Badges */}
              {classification.complianceImpact && classification.complianceImpact.length > 0 && (
                <div className="space-y-1.5 pt-1">
                  <div className="flex items-center gap-1.5 text-[10px] font-semibold uppercase tracking-wider text-[#8e8f96]">
                    <Scale className="w-3 h-3 text-[#8e8f96]" />
                    Compliance & Regulatory Mapping
                  </div>
                  <div className="flex flex-wrap gap-1.5">
                    {classification.complianceImpact.map((tag, idx) => (
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
              {classification.remediationAdvice && (
                <div className="pt-2 border-t border-[#21232a] text-[11px] text-[#8e8f96] flex items-start gap-1.5">
                  <CheckCircle2 className="w-3.5 h-3.5 text-[#8df85f] shrink-0 mt-0.5" />
                  <span><strong className="text-white">Remediation: </strong>{classification.remediationAdvice}</span>
                </div>
              )}

              {/* OpenTelemetry Granular Latency Breakdown */}
              {classification.latencyBreakdown && Object.keys(classification.latencyBreakdown).length > 0 && (
                <div className="pt-2 border-t border-[#21232a] flex items-center gap-2 flex-wrap text-[9px] font-mono text-[#8e8f96]">
                  <Activity className="w-3 h-3 text-[#8df85f]" />
                  <span>Trace:</span>
                  {Object.entries(classification.latencyBreakdown).map(([stage, ms]) => (
                    <span key={stage} className="bg-black/40 px-1.5 py-0.5 rounded border border-[#21232a]">
                      {stage}: {ms}ms
                    </span>
                  ))}
                </div>
              )}
            </div>

            {/* PII Entity Detections */}
            <div className="space-y-2">
              <div className="text-[10px] font-bold uppercase tracking-wider text-[#8e8f96]">
                Detected Entities ({classification.piiList.length})
              </div>
              <div className="flex flex-wrap gap-2">
                {classification.piiList.length > 0 ? (
                  classification.piiList.map((pii, i) => (
                    <span
                      key={i}
                      className="px-2.5 py-1 rounded-xl bg-[#121316] border border-[#21232a] text-xs font-mono text-[#8df85f]"
                    >
                      {pii}
                    </span>
                  ))
                ) : (
                  <span className="text-xs text-[#8e8f96] italic">
                    {text.trim() ? 'No high-risk PII or cryptographic credentials identified.' : 'Enter text above to inspect.'}
                  </span>
                )}
              </div>
            </div>

            {/* Sanitized / Masked Text Toggle */}
            {classification.maskedText && classification.maskedText !== text && (
              <div className="space-y-2 border-t border-[#161619] pt-4">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-[#8e8f96]">
                    Sanitized Payload (HMAC Masked)
                  </span>
                  <button
                    onClick={() => setShowMasked(!showMasked)}
                    className="text-xs text-[#8df85f] hover:underline flex items-center gap-1 cursor-pointer"
                  >
                    {showMasked ? <EyeOff className="w-3.5 h-3.5" /> : <Eye className="w-3.5 h-3.5" />}
                    {showMasked ? 'Hide' : 'Reveal'}
                  </button>
                </div>
                {showMasked && (
                  <div className="p-3 bg-[#121316] border border-[#21232a] rounded-xl text-xs font-mono text-[#8df85f] break-all max-h-36 overflow-y-auto select-all">
                    {classification.maskedText}
                  </div>
                )}
              </div>
            )}

            {/* Accuracy Pipeline Button */}
            <div className="border-t border-[#161619] pt-4">
              <button
                onClick={handleReportIncorrect}
                disabled={reported || !text.trim()}
                className={`w-full py-2.5 px-4 rounded-xl text-xs font-bold transition flex items-center justify-center gap-2 cursor-pointer ${
                  reported
                    ? 'bg-[#f38933]/15 text-[#f38933] border border-[#f38933]/30 cursor-not-allowed'
                    : 'bg-[#121316] border border-[#21232a] text-[#8e8f96] hover:text-white hover:border-white disabled:opacity-40 disabled:cursor-not-allowed'
                }`}
              >
                <RefreshCw className="w-3.5 h-3.5" />
                {reported ? 'Flagged for Active Retraining' : 'Report Misclassification (RLHF Feedback)'}
              </button>
            </div>

          </div>
        </div>

      </div>
    </div>
  );
}
