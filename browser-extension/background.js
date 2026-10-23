// =============================================================================
// SecureFlow AI - Background Service Worker (Manifest V3)
// Relays Telemetry & AI Model Inspections to Port 8000 (Exempt from Page CSP)
// =============================================================================

const DEFAULT_GATEWAY_URL = "http://127.0.0.1:8000/api/v1/events/ingest";
const LOCALHOST_GATEWAY_URL = "http://localhost:8000/api/v1/events/ingest";
const DEFAULT_SCAN_URL = "http://127.0.0.1:8000/api/v1/scan/dlp";
const LOCALHOST_SCAN_URL = "http://localhost:8000/api/v1/scan/dlp";
const MAX_LOCAL_EVENTS = 50;

chrome.runtime.onInstalled.addListener(() => {
  chrome.storage.local.get(["monitoringEnabled", "recentAlerts"], (data) => {
    chrome.storage.local.set({ gatewayUrl: DEFAULT_GATEWAY_URL });
    if (typeof data.monitoringEnabled === "undefined") {
      chrome.storage.local.set({ monitoringEnabled: true });
    }
    if (!data.recentAlerts) {
      chrome.storage.local.set({ recentAlerts: [] });
    }
  });
  console.log("[SecureFlow Service Worker] Installed & configured to FastAPI Port 8000.");
});

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  // 1. Ingest Event Telemetry Dispatch
  if (request.type === "SECUREFLOW_INGEST_EVENT") {
    handleIngestEvent(request.payload)
      .then(result => sendResponse(result))
      .catch(err => {
        console.error("[SecureFlow Service Worker] Dispatch error:", err);
        sendResponse({ status: "error", message: err.message });
      });
    return true; 
  }

  // 2. Real-Time Deep AI Neural Model Scan via /api/v1/scan/dlp
  if (request.type === "SECUREFLOW_AI_SCAN") {
    handleAiScan(request.payload)
      .then(result => sendResponse(result))
      .catch(err => {
        console.error("[SecureFlow Service Worker] AI Model Scan error:", err);
        sendResponse({ status: "error", message: err.message });
      });
    return true;
  }
});

// -----------------------------------------------------------------------------
// Real-Time Deep AI Scan Handler (Queries ONNX HybridDLPEngine on Port 8000)
// -----------------------------------------------------------------------------
async function handleAiScan(payload) {
  if (!payload || !payload.text || payload.text.trim().length < 8) {
    return { status: "ignored", reason: "too_short" };
  }

  const scanBody = {
    client_id: "browser-extension",
    user_id: payload.userId || "employee@secureflow.ai",
    department: payload.department || "corporate",
    destination_domain: payload.destinationDomain || "browser",
    source_action: payload.sourceAction || "prompt_injection",
    text: payload.text,
    mode: "mask"
  };

  const headers = {
    "Content-Type": "application/json",
    "X-Capture-Source": "SecureFlow-BrowserExt-AI-Worker"
  };

  let response = null;
  const timeoutSignal = AbortSignal.timeout ? AbortSignal.timeout(2500) : undefined;
  try {
    response = await fetch(DEFAULT_SCAN_URL, {
      method: "POST",
      headers: headers,
      body: JSON.stringify(scanBody),
      signal: timeoutSignal
    });
  } catch (err) {
    try {
      const fallbackSignal = AbortSignal.timeout ? AbortSignal.timeout(2500) : undefined;
      response = await fetch(LOCALHOST_SCAN_URL, {
        method: "POST",
        headers: headers,
        body: JSON.stringify(scanBody),
        signal: fallbackSignal
      });
    } catch (fallbackErr) {
      console.warn("[SecureFlow Service Worker] AI scan endpoint unreachable:", fallbackErr.message);
      return { status: "offline", error: fallbackErr.message };
    }
  }

  if (!response || !response.ok) {
    return { status: "error", httpStatus: response ? response.status : 0 };
  }

  const result = await response.json();
  return {
    status: "success",
    tier: result.classification_tier,         // "SAFE", "CONFIDENTIAL", "RESTRICTED"
    riskScore: result.risk_score,             // 0-100
    action: result.enforcement_action,        // "ALLOW", "MASK", "BLOCK"
    entities: result.detected_entities || [],
    threatCategory: result.threat_category,
    explanation: result.explanation,
    complianceImpact: result.compliance_impact || []
  };
}

// -----------------------------------------------------------------------------
// Event Ingestion Handler
// -----------------------------------------------------------------------------
async function handleIngestEvent(eventPayload) {
  const { monitoringEnabled, gatewayUrl, recentAlerts = [], authToken } = 
    await chrome.storage.local.get(["monitoringEnabled", "gatewayUrl", "recentAlerts", "authToken"]);

  if (!monitoringEnabled) {
    console.log("[SecureFlow] Monitoring disabled by user toggle.");
    return { status: "ignored", reason: "monitoring_disabled" };
  }

  const targetUrl = gatewayUrl || DEFAULT_GATEWAY_URL;

  const logItem = {
    id: eventPayload.eventId,
    timestamp: eventPayload.timestamp,
    source: eventPayload.source,
    targetUrl: eventPayload.metadata?.url,
    hostname: eventPayload.metadata?.hostname,
    field: eventPayload.metadata?.targetField,
    flags: eventPayload.metadata?.instantFlags || [],
    contentSnippet: (eventPayload.content || "").substring(0, 60) + "..."
  };

  const updatedAlerts = [logItem, ...recentAlerts.slice(0, MAX_LOCAL_EVENTS - 1)];
  await chrome.storage.local.set({ recentAlerts: updatedAlerts });

  const headers = {
    "Content-Type": "application/json",
    "X-Capture-Source": "SecureFlow-BrowserExt-v1"
  };
  if (authToken) {
    headers["Authorization"] = `Bearer ${authToken}`;
  }

  let response = null;
  try {
    response = await fetch(targetUrl, {
      method: "POST",
      headers: headers,
      body: JSON.stringify(eventPayload)
    });
  } catch (err) {
    try {
      response = await fetch(LOCALHOST_GATEWAY_URL, {
        method: "POST",
        headers: headers,
        body: JSON.stringify(eventPayload)
      });
    } catch (fallbackErr) {
      console.warn("[SecureFlow] Ingestion gateway offline, event buffered locally:", fallbackErr.message);
      return { status: "buffered_offline", localId: eventPayload.eventId };
    }
  }

  if (!response || !response.ok) {
    console.warn(`[SecureFlow] Gateway responded with HTTP ${response ? response.status : 'offline'}`);
    return { status: "buffered", httpStatus: response ? response.status : 0 };
  }

  const data = await response.json();

  if (data.riskScore && data.riskScore > 70) {
    try {
      chrome.notifications.create({
        type: "basic",
        iconUrl: "icon128.png",
        title: "🛡️ SecureFlow AI: High Risk Detected",
        message: `Sensitive transmission on ${eventPayload.metadata?.hostname || 'browser'} blocked (Risk: ${data.riskScore}/100)`,
        priority: 2
      });
    } catch (_) {}
  }

  return data;
}
