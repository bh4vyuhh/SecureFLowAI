// =============================================================================
// SecureFlow AI - Network & File Upload Guard (Main World Script)
// Intercepts & Blocks Unauthorized File Uploads & HTTP Submissions (Fetch & XHR)
// =============================================================================

(function () {
  if (window.__SECUREFLOW_NETWORK_GUARD_ACTIVE__) return;
  window.__SECUREFLOW_NETWORK_GUARD_ACTIVE__ = true;

  // Do NOT intercept network requests on internal SecureFlow SOC Admin Console
  const host = window.location.hostname;
  const port = window.location.port;
  if ((host === "localhost" || host === "127.0.0.1") && (port === "5174" || port === "8000" || port === "9090")) {
    console.log("%c[SecureFlow AI]%c Network Guard dormant on internal SOC Console.", "color: #8df85f; font-weight: bold;", "");
    return;
  }

  console.log(
    "%c[SecureFlow AI]%c Active Network & File Upload Guard Loaded (Kernel Level).",
    "color: #8df85f; font-weight: bold;",
    "color: inherit;"
  );

  // ---------------------------------------------------------------------------
  // 1. Universal DLP Detection Engine
  // ---------------------------------------------------------------------------
  const DLP_PATTERNS = {
    SSN: /\b\d{3}[- ]?\d{2}[- ]?\d{4}\b/,
    SSN_CONTEXT: /\b(?:ssn|social\s+security)[\s#:]*(\d{9}|\d{3}[- ]\d{2}[- ]\d{4})\b/i,
    CREDIT_CARD: /\b(?:\d[ -]*?){13,19}\b/,
    IBAN: /\b[A-Z]{2}\d{2}(?:[ ]?[A-Z0-9]){11,30}\b/i,
    BANK_ACCOUNT: /\b(?:bank\s+account|acct\s+no|account\s+number)[\s#:]+(\d{8,18})\b/i,
    ABA_ROUTING: /\b(?:routing|aba|rtn)[\s#:]+(0[1-9]\d{7}|[1-3]\d{8})\b/i,
    SWIFT_BIC: /\b(?:swift|bic)[\s#:]+([A-Z]{4}[A-Z]{2}[A-Z0-9]{2}(?:[A-Z0-9]{3})?)\b/,
    PAN_CARD: /\b[A-Z]{5}[0-9]{4}[A-Z]\b/,
    AADHAAR: /\b(?:aadhaar|uid|uidai)[\s#:]*[2-9]\d{3}[ -]?\d{4}[ -]?\d{4}\b/i,
    API_KEY: /\b(?:sk-[a-zA-Z0-9_\-]{20,}|sk-ant-[a-zA-Z0-9_\-]{20,}|gh[pousr]_[0-9a-zA-Z]{36}|AIza[0-9A-Za-z\-_]{35}|xox[baprs]-[0-9a-zA-Z]{10,48}|hf_[0-9a-zA-Z]{34,}|AKIA[0-9A-Z]{16})\b/i,
    GENERIC_KEY: /\b(?:api[_-]?key|client[_-]?secret|secret[_-]?key|auth[_-]?token|access[_-]?token)[\s:=]+([a-zA-Z0-9_\-\.]{12,})\b/i,
    PASSWORD_SECRET: /\b(?:admin\s+)?(?:password|passwd|pwd|db_pass|jwt_secret|private_key|access_key)[\s:=]+([^\s,;'"<>]{4,})/i,
    PLAIN_PASSWORD: /\b(?:my|our|the|your|admin|root)\s+(?:password|passcode)\s+(?:is|was|=|:)\s*([^\s,;'"<>]{3,})/i,
    BEARER_TOKEN: /\bBearer\s+[a-zA-Z0-9_\-\.]{25,}\b/,
    JWT_TOKEN: /\beyJ[a-zA-Z0-9_-]{10,}\.eyJ[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}\b/,
    DB_CONN: /\b(?:postgres|postgresql|mysql|mongodb|redis|mssql|jdbc):\/\/[^\s"']+:[^\s"']+@[^\s"']+\b/i,
    PRIVATE_KEY: /-----BEGIN (?:RSA|EC|OPENSSH|DSA|ENCRYPTED|PRIVATE) KEY-----/i,
    CONFIDENTIAL: /\b(?:STRICTLY\s+CONFIDENTIAL|TOP\s+SECRET|TRADE\s+SECRET|INTERNAL\s+USE\s+ONLY|RESTRICTED\s+DOCUMENT|PROPRIETARY\s+AND\s+CONFIDENTIAL)\b/i,
  };

  function luhnCheck(cardStr) {
    const digits = (cardStr || "").replace(/\D/g, "");
    if (digits.length < 13 || digits.length > 19) return false;
    let sum = 0;
    let shouldDouble = false;
    for (let i = digits.length - 1; i >= 0; i--) {
      let digit = parseInt(digits.charAt(i), 10);
      if (shouldDouble) {
        digit *= 2;
        if (digit > 9) digit -= 9;
      }
      sum += digit;
      shouldDouble = !shouldDouble;
    }
    return sum % 10 === 0;
  }

  function detectSensitivePii(text) {
    if (!text || typeof text !== "string") return [];
    const hits = [];

    // Credit Card Check
    const cardMatch = text.match(DLP_PATTERNS.CREDIT_CARD);
    if (cardMatch) {
      const rawCard = cardMatch[0];
      const digits = rawCard.replace(/\D/g, "");
      const isLuhn = luhnCheck(rawCard);
      const isGrouped16 = /^\d{4}[ -]\d{4}[ -]\d{4}[ -]\d{4}$/.test(rawCard.trim());
      const hasCardContext = /(?:credit\s*card|debit\s*card|visa|mastercard|amex|card\s*number|cvv)/i.test(text);
      if (isLuhn || (isGrouped16 && hasCardContext) || (digits.length >= 13 && digits.length <= 19 && isLuhn)) {
        hits.push("Credit Card (PCI-DSS)");
      }
    }

    if (DLP_PATTERNS.SSN.test(text) || DLP_PATTERNS.SSN_CONTEXT.test(text)) hits.push("US SSN / National ID");
    if (DLP_PATTERNS.PAN_CARD.test(text)) hits.push("Tax ID / PAN Card");
    if (DLP_PATTERNS.AADHAAR.test(text)) hits.push("National Identity / UID");
    if (DLP_PATTERNS.IBAN.test(text)) hits.push("IBAN Bank Account");
    if (DLP_PATTERNS.BANK_ACCOUNT.test(text)) hits.push("Bank Account Number");
    if (DLP_PATTERNS.ABA_ROUTING.test(text)) hits.push("ABA Routing Number");
    if (DLP_PATTERNS.SWIFT_BIC.test(text)) hits.push("SWIFT / BIC");
    if (DLP_PATTERNS.PRIVATE_KEY.test(text)) hits.push("Cryptographic Private Key");
    if (DLP_PATTERNS.API_KEY.test(text) || DLP_PATTERNS.GENERIC_KEY.test(text)) hits.push("Live API Credential / Secret");
    if (DLP_PATTERNS.PASSWORD_SECRET.test(text) || DLP_PATTERNS.PLAIN_PASSWORD.test(text)) hits.push("Exposed Password / Passcode");
    if (DLP_PATTERNS.BEARER_TOKEN.test(text) || DLP_PATTERNS.JWT_TOKEN.test(text)) hits.push("Authentication Token");
    if (DLP_PATTERNS.DB_CONN.test(text)) hits.push("Database Connection String");
    if (DLP_PATTERNS.CONFIDENTIAL.test(text)) hits.push("Confidential Document Marker");

    return hits;
  }

  function scanPayloadText(rawText) {
    if (!rawText || typeof rawText !== "string") return [];
    let hits = detectSensitivePii(rawText);
    if (hits.length > 0) return hits;

    // Check URL-decoded variant (for x-www-form-urlencoded and webmail sync requests)
    if (rawText.includes("%") || rawText.includes("+")) {
      try {
        const decoded = decodeURIComponent(rawText.replace(/\+/g, " "));
        const decHits = detectSensitivePii(decoded);
        if (decHits.length > 0) return decHits;
      } catch (_) {}
    }
    return [];
  }

  function extractStringFromPayload(val) {
    if (typeof val === "string") return val;
    if (val instanceof URLSearchParams) return val.toString();
    if (val instanceof ArrayBuffer) {
      try { return new TextDecoder("utf-8").decode(new Uint8Array(val)); } catch (_) {}
    }
    if (ArrayBuffer.isView(val)) {
      try { return new TextDecoder("utf-8").decode(val); } catch (_) {}
    }
    return null;
  }

  // Notify UI and SOC backend
  function triggerBlockedUpload(filename, hits, textSnippet) {
    console.warn(
      `%c[SecureFlow AI BLOCKED TRANSMISSION]%c "${filename}" blocked. Detected:`,
      "color: #ff4d4f; font-weight: bold; font-size: 13px;",
      "",
      hits
    );

    // 1. Dispatch custom event caught by content.js for in-page banner and red outline
    window.dispatchEvent(
      new CustomEvent("SECUREFLOW_FILE_UPLOAD_BLOCKED", {
        detail: {
          filename: filename || "uploaded_file.txt",
          reasons: hits,
          snippet: (textSnippet || "").substring(0, 100),
        },
      })
    );

    // 2. Transmit blocked audit record via window.postMessage to content.js (exempt from page CSP)
    try {
      window.postMessage(
        {
          type: "SECUREFLOW_PAGE_AUDIT_EVENT",
          payload: {
            eventId: "ext-upload-" + Math.random().toString(36).substring(2, 10),
            timestamp: new Date().toISOString(),
            source: "CHROME_EXTENSION",
            eventType: "FILE_UPLOAD_BLOCKED",
            fileName: filename || "uploaded_file.txt",
            content: (textSnippet || "").substring(0, 5000),
            actionEnforced: "BLOCK",
            metadata: {
              url: window.location.href,
              hostname: window.location.hostname,
              pageTitle: document.title,
              instantFlags: hits,
            },
          },
        },
        "*"
      );
    } catch (_) {}
  }

  // Helper to inspect FormData or Blobs
  async function inspectFormData(formData) {
    if (!formData || !(formData instanceof FormData)) return null;

    for (const [key, val] of formData.entries()) {
      if (val instanceof Blob || val instanceof File) {
        try {
          const text = await val.text();
          const detected = scanPayloadText(text);
          if (detected.length > 0) {
            return { filename: val.name || key, hits: detected, snippet: text };
          }
        } catch (_) {}
      } else if (typeof val === "string") {
        const detected = scanPayloadText(val);
        if (detected.length > 0) {
          return { filename: key, hits: detected, snippet: val };
        }
      }
    }
    return null;
  }

  // ---------------------------------------------------------------------------
  // 2. HOOK WINDOW.FETCH (Intercepts all modern fetch requests & file uploads)
  // ---------------------------------------------------------------------------
  const originalFetch = window.fetch;
  window.fetch = async function (input, init) {
    const url = typeof input === "string" ? input : (input && input.url ? input.url : "");

    // Do NOT intercept SecureFlow's internal telemetry dispatches to port 8000
    if (url.includes("/api/v1/events/ingest") || url.includes(":8000")) {
      return originalFetch.apply(this, arguments);
    }

    if (init && init.body) {
      if (init.body instanceof FormData) {
        const blocked = await inspectFormData(init.body);
        if (blocked) {
          triggerBlockedUpload(blocked.filename, blocked.hits, blocked.snippet);
          throw new Error(
            `[SecureFlow AI DLP Blocked] Upload of "${blocked.filename}" was blocked by enterprise policy: ${blocked.hits.join(", ")}`
          );
        }
      } else if (init.body instanceof Blob || init.body instanceof File) {
        try {
          const text = await init.body.text();
          const detected = scanPayloadText(text);
          if (detected.length > 0) {
            triggerBlockedUpload(init.body.name || "binary_payload", detected, text);
            throw new Error(
              `[SecureFlow AI DLP Blocked] File upload blocked: ${detected.join(", ")}`
            );
          }
        } catch (e) {
          if (e.message && e.message.includes("SecureFlow AI DLP Blocked")) throw e;
        }
      } else {
        const str = extractStringFromPayload(init.body);
        if (str) {
          const detected = scanPayloadText(str);
          if (detected.length > 0) {
            triggerBlockedUpload("request_payload", detected, str);
            throw new Error(
              `[SecureFlow AI DLP Blocked] Request payload transmission blocked: ${detected.join(", ")}`
            );
          }
        }
      }
    } else if (input instanceof Request && !init?.body) {
      try {
        const cloned = input.clone();
        const text = await cloned.text();
        const detected = scanPayloadText(text);
        if (detected.length > 0) {
          triggerBlockedUpload("request_stream", detected, text);
          throw new Error(
            `[SecureFlow AI DLP Blocked] Request payload transmission blocked: ${detected.join(", ")}`
          );
        }
      } catch (e) {
        if (e.message && e.message.includes("SecureFlow AI DLP Blocked")) throw e;
      }
    }

    return originalFetch.apply(this, arguments);
  };

  // ---------------------------------------------------------------------------
  // 3. HOOK XMLHTTPREQUEST (Intercepts Axios, jQuery, and traditional XHR uploads)
  // ---------------------------------------------------------------------------
  const originalXhrOpen = XMLHttpRequest.prototype.open;
  XMLHttpRequest.prototype.open = function (method, url) {
    this.__sfUrl = url ? url.toString() : "";
    return originalXhrOpen.apply(this, arguments);
  };

  const originalXhrSend = XMLHttpRequest.prototype.send;
  XMLHttpRequest.prototype.send = function (body) {
    if (this.__sfUrl && (this.__sfUrl.includes("/api/v1/events/ingest") || this.__sfUrl.includes(":8000"))) {
      return originalXhrSend.apply(this, arguments);
    }

    if (body) {
      if (body instanceof FormData) {
        const files = [];
        for (const [k, v] of body.entries()) {
          if (v instanceof Blob || v instanceof File) {
            files.push(v);
          } else if (typeof v === "string") {
            const hits = scanPayloadText(v);
            if (hits.length > 0) {
              triggerBlockedUpload(k, hits, v);
              this.abort();
              return;
            }
          }
        }

        if (files.length > 0) {
          Promise.all(files.map((f) => f.text().catch(() => ""))).then((texts) => {
            for (let i = 0; i < files.length; i++) {
              const hits = scanPayloadText(texts[i]);
              if (hits.length > 0) {
                triggerBlockedUpload(files[i].name, hits, texts[i]);
                this.abort();
                try {
                  this.dispatchEvent(new ProgressEvent("error"));
                  this.dispatchEvent(new ProgressEvent("abort"));
                } catch (_) {}
                return;
              }
            }
            originalXhrSend.call(this, body);
          });
          return;
        }
      } else if (body instanceof Blob || body instanceof File) {
        body.text().then((text) => {
          const hits = scanPayloadText(text);
          if (hits.length > 0) {
            triggerBlockedUpload(body.name || "file_blob", hits, text);
            this.abort();
            try {
              this.dispatchEvent(new ProgressEvent("error"));
              this.dispatchEvent(new ProgressEvent("abort"));
            } catch (_) {}
            return;
          }
          originalXhrSend.call(this, body);
        }).catch(() => {
          originalXhrSend.call(this, body);
        });
        return;
      } else {
        const str = extractStringFromPayload(body);
        if (str) {
          const hits = scanPayloadText(str);
          if (hits.length > 0) {
            triggerBlockedUpload("xhr_payload", hits, str);
            this.abort();
            return;
          }
        }
      }
    }

    return originalXhrSend.apply(this, arguments);
  };
})();
