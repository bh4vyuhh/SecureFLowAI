
(function () {
  console.log("%c[SecureFlow AI]%c DLP Browser Agent Initialized.", "color: #8df85f; font-weight: bold;", "color: inherit;");


  // Regex patterns aligned with AI Classification & Detection Engine
  const DLP_PATTERNS = {
    SSN: /\b\d{3}-\d{2}-\d{4}\b/,
    CREDIT_CARD: /\b(?:\d[ -]*?){13,19}\b/,
    IBAN: /\b[A-Z]{2}[0-9]{2}[A-Z0-9]{4}[0-9]{7}(?:[A-Z0-9]?){0,16}\b/i,
    ABA_ROUTING: /\b\d{9}\b/,
    SWIFT_BIC: /\b[A-Z]{4}[A-Z]{2}[A-Z0-9]{2}(?:[A-Z0-9]{3})?\b/i,
    API_KEY: /\b(?:sk_live_[0-9a-zA-Z]{24,}|ghp_[0-9a-zA-Z]{36}|AKIA[0-9A-Z]{16}|(?:key|secret|token|password)[a-zA-Z0-9_]{10,40})\b/i,
    PRIVATE_KEY: /-----BEGIN (?:RSA|EC|OPENSSH|DSA|ENCRYPTED|PRIVATE) KEY-----/i,
    EMAIL: /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/
  };

  function detectSensitivePii(text) {
    const hits = [];
    if (DLP_PATTERNS.CREDIT_CARD.test(text)) hits.push("Credit Card (PCI-DSS)");
    if (DLP_PATTERNS.SSN.test(text)) hits.push("US SSN");
    if (DLP_PATTERNS.IBAN.test(text)) hits.push("IBAN Bank Account");
    if (DLP_PATTERNS.SWIFT_BIC.test(text)) hits.push("SWIFT / BIC");
    if (DLP_PATTERNS.ABA_ROUTING.test(text)) hits.push("ABA Routing Number");
    if (DLP_PATTERNS.PRIVATE_KEY.test(text)) hits.push("Cryptographic Private Key");
    if (DLP_PATTERNS.API_KEY.test(text)) hits.push("Live API Credential");
    return hits;
  }


  document.addEventListener("paste", function (event) {
    try {
      const clipboardData = event.clipboardData || window.clipboardData;
      if (!clipboardData) return;

      const pastedText = clipboardData.getData("text");
      if (!pastedText || pastedText.trim().length < 5) return;

      const target = event.target;
      const targetTagName = target.tagName ? target.tagName.toLowerCase() : "unknown";
      const targetIdentifier = target.id || target.name || target.getAttribute("aria-label") || targetTagName;

      const detected = detectSensitivePii(pastedText);

      // Construct normalized Capture Layer DTO
      const eventPayload = {
        eventId: "ext-" + Math.random().toString(36).substring(2, 10),
        timestamp: new Date().toISOString(),
        source: "CHROME_EXTENSION",
        eventType: "BROWSER_PASTE",
        content: pastedText,
        fileName: `web_paste_${window.location.hostname}.txt`,
        metadata: {
          url: window.location.href,
          hostname: window.location.hostname,
          pageTitle: document.title,
          targetField: targetIdentifier,
          targetType: targetTagName,
          instantFlags: detected
        }
      };

      // If high-confidence PII is pasted, proactively enforce inline blocking
      if (detected.length > 0) {
        // Active Inline Prevention: Cancel paste into DOM input field
        event.preventDefault();
        event.stopImmediatePropagation();

        // Optional fallback: Replace paste with masked placeholder text
        if (target && (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA' || target.isContentEditable)) {
          const placeholderNotice = `[BLOCKED BY SECUREFLOW AI: ${detected.join(', ')}]`;
          try {
            document.execCommand('insertText', false, placeholderNotice);
          } catch (_) {
            // execCommand fallback
          }
        }

        showInPageAlert(detected, targetIdentifier, true);
      }

      // Send event to service worker for centralized audit logging & WebSocket broadcast
      chrome.runtime.sendMessage({
        type: "SECUREFLOW_INGEST_EVENT",
        payload: {
          ...eventPayload,
          actionEnforced: detected.length > 0 ? "BLOCK" : "ALLOW"
        }
      }, (response) => {
        if (chrome.runtime.lastError) {
          console.warn("[SecureFlow AI] Background worker unavailable:", chrome.runtime.lastError.message);
        } else if (response && response.riskScore > 75) {
          showInPageAlert([`Blocked by Policy (Risk: ${response.riskScore}/100)`], targetIdentifier, true);
        }
      });

    } catch (err) {
      console.error("[SecureFlow AI] Content script error:", err);
    }
  }, true); // Use capture phase so we see paste before target handles it

  function showInPageAlert(reasons, field) {
    const existing = document.getElementById("sf-dlp-alert-banner");
    if (existing) existing.remove();

    const banner = document.createElement("div");
    banner.id = "sf-dlp-alert-banner";
    banner.style.cssText = `
      position: fixed;
      top: 18px;
      right: 18px;
      background: #0c0c0e;
      color: #ffffff;
      border: 1px solid #ff4d4f;
      box-shadow: 0 10px 25px rgba(0,0,0,0.6);
      padding: 12px 16px;
      border-radius: 12px;
      z-index: 2147483647;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      font-size: 13px;
      display: flex;
      align-items: center;
      gap: 12px;
      animation: sfFadeIn 0.3s ease-out;
    `;

    banner.innerHTML = `
      <div style="width: 10px; height: 10px; border-radius: 50%; background: #ff4d4f; box-shadow: 0 0 8px #ff4d4f;"></div>
      <div>
        <div style="font-weight: bold; color: #ff7875;">SecureFlow DLP Warning</div>
        <div style="color: #a0a0a5; font-size: 11px;">Sensitive pattern pasted into [${field}]: ${reasons.join(", ")}</div>
      </div>
      <button id="sf-close-btn" style="background: transparent; border: none; color: #888; font-size: 16px; cursor: pointer; margin-left: 8px;">&times;</button>
    `;

    document.body.appendChild(banner);

    document.getElementById("sf-close-btn")?.addEventListener("click", () => {
      banner.remove();
    });

    setTimeout(() => {
      if (banner && banner.parentNode) {
        banner.remove();
      }
    }, 6000);
  }
})();
