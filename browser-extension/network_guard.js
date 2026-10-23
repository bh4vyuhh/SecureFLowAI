// =============================================================================
// SecureFlow AI - Network & File Upload Guard (Main World Script)
// Intercepts & Blocks Unauthorized File Uploads via Fetch API & XMLHttpRequest
// =============================================================================

(function () {
  if (window.__SECUREFLOW_NETWORK_GUARD_ACTIVE__) return;
  window.__SECUREFLOW_NETWORK_GUARD_ACTIVE__ = true;

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
    CREDIT_CARD: /\b(?:\d[ -]*?){13,19}\b/,
    IBAN: /\b[A-Z]{2}\d{2}(?:[ ]?[A-Z0-9]){11,30}\b/i,
    BANK_ACCOUNT: /(?:account|acct|a\/c|acc)[\s#:]+(\d{8,18})\b/i,
    ABA_ROUTING: /\b(?:routing|aba|rtn)?[:\s#]*\b(0[1-9]\d{7}|[1-3]\d{8})\b/i,
    SWIFT_BIC: /\b[A-Z]{4}[A-Z]{2}[A-Z0-9]{2}(?:[A-Z0-9]{3})?\b/i,
    PAN_CARD: /\b[A-Z]{5}[0-9]{4}[A-Z]\b/,
    AADHAAR: /\b\d{4}[ -]\d{4}[ -]\d{4}\b/,
    API_KEY: /\b(?:sk-[a-zA-Z0-9_\-]{20,}|gh[pousr]_[0-9a-zA-Z]{36}|AIza[0-9A-Za-z\-_]{35}|xox[baprs]-[0-9a-zA-Z]{10,48}|hf_[0-9a-zA-Z]{34,}|AKIA[0-9A-Z]{16})\b/i,
    PASSWORD_SECRET: /(?:password|passwd|pwd|db_pass|secret|jwt_secret|private_key|access_key)[\s:=]+([^\s,;'"<>]{5,})/i,
    BEARER_TOKEN: /\bBearer\s+[a-zA-Z0-9_\-\.]{25,}\b/,
    JWT_TOKEN: /\beyJ[a-zA-Z0-9_-]{10,}\.eyJ[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}\b/,
    DB_CONN: /\b(?:postgres|postgresql|mysql|mongodb|redis|mssql|jdbc):\/\/[^\s"']+:[^\s"']+@[^\s"']+\b/i,
    PRIVATE_KEY: /-----BEGIN (?:RSA|EC|OPENSSH|DSA|ENCRYPTED|PRIVATE) KEY-----/i,
    CONFIDENTIAL: /\b(?:CONFIDENTIAL|STRICTLY CONFIDENTIAL|TRADE SECRET|INTERNAL USE ONLY|RESTRICTED DOCUMENT)\b/i,
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
      const isGrouped = /^\d{4}[ -]\d{4}[ -]\d{4}[ -]\d{1,4}$/.test(rawCard.trim());
      const hasCardContext = /(?:card|cc|visa|master|amex|pan|exp|cvv|payment|debit|credit)/i.test(text);
      if (isLuhn || isGrouped || (digits.length >= 13 && digits.length <= 19 && hasCardContext) || digits.length === 16) {
        hits.push("Credit Card (PCI-DSS)");
      }
    }

    if (DLP_PATTERNS.SSN.test(text)) hits.push("US SSN / National ID");
    if (DLP_PATTERNS.PAN_CARD.test(text)) hits.push("Tax ID / PAN Card");
    if (DLP_PATTERNS.AADHAAR.test(text)) hits.push("National Identity / UID");
    if (DLP_PATTERNS.IBAN.test(text)) hits.push("IBAN Bank Account");
    if (DLP_PATTERNS.BANK_ACCOUNT.test(text)) hits.push("Bank Account Number");
    if (DLP_PATTERNS.SWIFT_BIC.test(text)) hits.push("SWIFT / BIC");
    if (DLP_PATTERNS.PRIVATE_KEY.test(text)) hits.push("Cryptographic Private Key");
    if (DLP_PATTERNS.API_KEY.test(text)) hits.push("Live API Credential");
    if (DLP_PATTERNS.PASSWORD_SECRET.test(text)) hits.push("Exposed Password / Secret");
    if (DLP_PATTERNS.BEARER_TOKEN.test(text) || DLP_PATTERNS.JWT_TOKEN.test(text)) hits.push("Authentication Token");
    if (DLP_PATTERNS.DB_CONN.test(text)) hits.push("Database Connection String");
    if (DLP_PATTERNS.CONFIDENTIAL.test(text)) hits.push("Confidential Document Marker");

    return hits;
  }

  // Notify UI and SOC backend
  function triggerBlockedUpload(filename, hits, textSnippet) {
    console.warn(
      `%c[SecureFlow AI BLOCKED FILE UPLOAD]%c "${filename}" blocked. Detected:`,
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

    // 2. Transmit blocked audit record directly to FastAPI
    try {
      const payload = {
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
      };

      fetch("http://127.0.0.1:8000/api/v1/events/ingest", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      }).catch(() => {
        fetch("http://localhost:8000/api/v1/events/ingest", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        }).catch(() => {});
      });
    } catch (_) {}
  }

  // Helper to inspect FormData or Blobs
  async function inspectFormData(formData) {
    if (!formData || !(formData instanceof FormData)) return null;

    for (const [key, val] of formData.entries()) {
      if (val instanceof Blob || val instanceof File) {
        try {
          const text = await val.text();
          const detected = detectSensitivePii(text);
          if (detected.length > 0) {
            return { filename: val.name || key, hits: detected, snippet: text };
          }
        } catch (_) {}
      } else if (typeof val === "string") {
        const detected = detectSensitivePii(val);
        if (detected.length > 0) {
          return { filename: key, hits: detected, snippet: val };
        }
      }
    }
    return null;
  }

  // ---------------------------------------------------------------------------
  // 2. HOOK WINDOW.FETCH (Intercepts all modern fetch file uploads)
  // ---------------------------------------------------------------------------
  const originalFetch = window.fetch;
  window.fetch = async function (input, init) {
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
          const detected = detectSensitivePii(text);
          if (detected.length > 0) {
            triggerBlockedUpload(init.body.name || "binary_payload", detected, text);
            throw new Error(
              `[SecureFlow AI DLP Blocked] File upload blocked: ${detected.join(", ")}`
            );
          }
        } catch (e) {
          if (e.message && e.message.includes("SecureFlow AI DLP Blocked")) throw e;
        }
      } else if (typeof init.body === "string") {
        const detected = detectSensitivePii(init.body);
        if (detected.length > 0) {
          triggerBlockedUpload("request_payload.json", detected, init.body);
          throw new Error(
            `[SecureFlow AI DLP Blocked] Request payload transmission blocked: ${detected.join(", ")}`
          );
        }
      }
    }

    return originalFetch.apply(this, arguments);
  };

  // ---------------------------------------------------------------------------
  // 3. HOOK XMLHTTPREQUEST (Intercepts Axios, jQuery, and traditional XHR uploads)
  // ---------------------------------------------------------------------------
  const originalXhrSend = XMLHttpRequest.prototype.send;
  XMLHttpRequest.prototype.send = function (body) {
    if (body) {
      if (body instanceof FormData) {
        const files = [];
        for (const [k, v] of body.entries()) {
          if (v instanceof Blob || v instanceof File) {
            files.push(v);
          } else if (typeof v === "string") {
            const hits = detectSensitivePii(v);
            if (hits.length > 0) {
              triggerBlockedUpload(k, hits, v);
              this.abort();
              return;
            }
          }
        }

        if (files.length > 0) {
          // Read all file contents asynchronously
          Promise.all(files.map((f) => f.text().catch(() => ""))).then((texts) => {
            for (let i = 0; i < files.length; i++) {
              const hits = detectSensitivePii(texts[i]);
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
            // Clean file: proceed with actual network transmission
            originalXhrSend.call(this, body);
          });
          return;
        }
      } else if (body instanceof Blob || body instanceof File) {
        body.text().then((text) => {
          const hits = detectSensitivePii(text);
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
      } else if (typeof body === "string") {
        const hits = detectSensitivePii(body);
        if (hits.length > 0) {
          triggerBlockedUpload("xhr_payload", hits, body);
          this.abort();
          return;
        }
      }
    }

    return originalXhrSend.apply(this, arguments);
  };
})();
