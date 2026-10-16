const DEFAULT_GATEWAY_URL = "http://localhost:9090/api/v1/events/ingest";
const DIRECT_AI_SERVICE_URL = "http://localhost:8000/api/v1/events/ingest";
const MAX_LOCAL_EVENTS = 50;

chrome.runtime.onInstalled.addListener(() => {
  chrome.storage.local.get(["gatewayUrl", "monitoringEnabled", "recentAlerts"], (data) => {
    if (!data.gatewayUrl) {
      chrome.storage.local.set({ gatewayUrl: DEFAULT_GATEWAY_URL });
    }
    if (typeof data.monitoringEnabled === "undefined") {
      chrome.storage.local.set({ monitoringEnabled: true });
    }
    if (!data.recentAlerts) {
      chrome.storage.local.set({ recentAlerts: [] });
    }
  });
  console.log("[SecureFlow Service Worker] Installed & configured.");
});

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.type === "SECUREFLOW_INGEST_EVENT") {
    handleIngestEvent(request.payload)
      .then(result => sendResponse(result))
      .catch(err => {
        console.error("[SecureFlow Service Worker] Dispatch error:", err);
        sendResponse({ status: "error", message: err.message });
      });
    return true; 
  }
});

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
    if (targetUrl !== DIRECT_AI_SERVICE_URL) {
      try {
        console.log("[SecureFlow] Port 9090 offline, falling back directly to AI Service (8000)...");
        response = await fetch(DIRECT_AI_SERVICE_URL, {
          method: "POST",
          headers: headers,
          body: JSON.stringify(eventPayload)
        });
      } catch (fallbackErr) {
        console.warn("[SecureFlow] Ingestion gateway and AI service offline, buffered locally:", fallbackErr.message);
        return { status: "buffered_offline", localId: eventPayload.eventId };
      }
    } else {
      console.warn("[SecureFlow] Ingestion gateway currently offline, event buffered locally:", err.message);
      return { status: "buffered_offline", localId: eventPayload.eventId };
    }
  }

  if (!response || !response.ok) {
    console.warn(`[SecureFlow] Gateway responded with HTTP ${response ? response.status : 'offline'}`);
    return { status: "buffered", httpStatus: response ? response.status : 0 };
  }

  const data = await response.json();

  if (data.riskScore && data.riskScore > 70) {
    chrome.notifications.create({
      type: "basic",
      iconUrl: "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%23ff4d4f'><circle cx='12' cy='12' r='10'/></svg>",
      title: "🛡️ SecureFlow AI: High Risk Detected",
      message: `Pasted data on ${eventPayload.metadata?.hostname || 'browser'} flagged (Score: ${data.riskScore}/100)`,
      priority: 2
    });
  }

  return data;
}
