/**
 * SecureFlow AI - Background Service Worker (Manifest V3)
 * Receives intercepted events from content scripts, persists local log buffer,
 * and transmits normalized event payload to Spring Boot Ingestion Gateway.
 */

const DEFAULT_GATEWAY_URL = "http://localhost:9090/api/v1/events/ingest";
const MAX_LOCAL_EVENTS = 50;

// Initialize defaults on install
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

// Handle incoming messages from content script or popup UI
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.type === "SECUREFLOW_INGEST_EVENT") {
    handleIngestEvent(request.payload)
      .then(result => sendResponse(result))
      .catch(err => {
        console.error("[SecureFlow Service Worker] Dispatch error:", err);
        sendResponse({ status: "error", message: err.message });
      });
    return true; // Keep message channel open for async response
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

  // Add to local audit log buffer
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

  // Transmit payload to Spring Boot Gateway
  const headers = {
    "Content-Type": "application/json",
    "X-Capture-Source": "SecureFlow-BrowserExt-v1"
  };
  if (authToken) {
    headers["Authorization"] = `Bearer ${authToken}`;
  }

  try {
    const response = await fetch(targetUrl, {
      method: "POST",
      headers: headers,
      body: JSON.stringify(eventPayload)
    });

    if (!response.ok) {
      console.warn(`[SecureFlow] Gateway responded with HTTP ${response.status}`);
      return { status: "buffered", httpStatus: response.status };
    }

    const data = await response.json();

    // Trigger Chrome system notification if flagged as risk
    if (data.riskScore && data.riskScore > 70) {
      chrome.notifications.create({
        type: "basic",
        iconUrl: "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%23ff4d4f'><circle cx='12' cy='12' r='10'/></svg>",
        title: "🛡️ SecureFlow AI: High Risk Detected",
        message: `Pasted data on ${eventPayload.metadata?.hostname} flagged (Score: ${data.riskScore}/100)`,
        priority: 2
      });
    }

    return data;
  } catch (err) {
    console.warn("[SecureFlow] Ingestion gateway currently offline, event buffered locally:", err.message);
    return { status: "buffered_offline", localId: eventPayload.eventId };
  }
}
