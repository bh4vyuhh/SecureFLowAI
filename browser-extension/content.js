// =============================================================================
// SecureFlow AI - Tier 2 Client Browser Agent (Manifest V3 Content Script)
// Real-Time Keystroke, Paste, and Prompt Transmission Interception (Shadow-DOM Aware)
// =============================================================================

(function () {
  console.log("%c[SecureFlow AI]%c DLP Browser Agent Initialized (v2.0 Universal Shadow-DOM Guard).", "color: #8df85f; font-weight: bold;", "color: inherit;");

  // Aligned Detection Patterns (Banking, PCI-DSS, PII, Secrets)
  const DLP_PATTERNS = {
    SSN: /\b\d{3}-\d{2}-\d{4}\b/,
    CREDIT_CARD: /\b(?:\d[ -]*?){13,19}\b/,
    IBAN: /\b[A-Z]{2}[0-9]{2}[A-Z0-9]{4}[0-9]{7}(?:[A-Z0-9]?){0,16}\b/i,
    ABA_ROUTING: /\b\d{9}\b/,
    SWIFT_BIC: /\b[A-Z]{4}[A-Z]{2}[A-Z0-9]{2}(?:[A-Z0-9]{3})?\b/i,
    API_KEY: /\b(?:sk_live_[0-9a-zA-Z]{24,}|ghp_[0-9a-zA-Z]{36}|AKIA[0-9A-Z]{16}|(?:key|secret|token|password)[a-zA-Z0-9_]{10,40})\b/i,
    PRIVATE_KEY: /-----BEGIN (?:RSA|EC|OPENSSH|DSA|ENCRYPTED|PRIVATE) KEY-----/i,
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

    // Credit Card with mandatory mathematical Luhn validation to avoid false positives
    const cardMatch = text.match(DLP_PATTERNS.CREDIT_CARD);
    if (cardMatch && luhnCheck(cardMatch[0])) {
      hits.push("Credit Card (PCI-DSS)");
    }

    if (DLP_PATTERNS.SSN.test(text)) hits.push("US SSN");
    if (DLP_PATTERNS.IBAN.test(text)) hits.push("IBAN Bank Account");
    if (DLP_PATTERNS.SWIFT_BIC.test(text)) hits.push("SWIFT / BIC");
    if (DLP_PATTERNS.PRIVATE_KEY.test(text)) hits.push("Cryptographic Private Key");
    if (DLP_PATTERNS.API_KEY.test(text)) hits.push("Live API Credential");
    return hits;
  }

  // ---------------------------------------------------------------------------
  // Universal Text Extractor (Works on Standard Inputs, Gemini Shadow-DOM, ChatGPT, Claude)
  // ---------------------------------------------------------------------------
  function getDeepTextAndElement(event) {
    const path = (event && typeof event.composedPath === "function") ? event.composedPath() : [];

    // 1. Check every element in the composedPath (Shadow DOM traversal)
    for (let el of path) {
      if (!el || el.nodeType !== 1) continue;

      if (typeof el.value === "string" && el.value.trim().length >= 5) {
        return { element: el, text: el.value.trim() };
      }

      const txt = (el.innerText || el.textContent || "").trim();
      if (txt.length >= 5 && (el.isContentEditable || el.getAttribute?.("role") === "textbox" || el.tagName === "P" || el.classList?.contains("ql-editor"))) {
        return { element: el, text: txt };
      }

      // Check shadowRoot if present (e.g. Google Gemini's <rich-textarea>)
      if (el.shadowRoot) {
        const shadowEls = el.shadowRoot.querySelectorAll("textarea, input, [contenteditable='true'], .ql-editor, p");
        for (let sEl of shadowEls) {
          const sTxt = (sEl.value || sEl.innerText || sEl.textContent || "").trim();
          if (sTxt.length >= 5) return { element: sEl, text: sTxt };
        }
      }
    }

    // 2. Fallback to activeElement
    const active = document.activeElement;
    if (active) {
      if (typeof active.value === "string" && active.value.trim().length >= 5) {
        return { element: active, text: active.value.trim() };
      }
      if (active.shadowRoot) {
        const shadowEls = active.shadowRoot.querySelectorAll("textarea, input, [contenteditable='true'], .ql-editor, p");
        for (let sEl of shadowEls) {
          const sTxt = (sEl.value || sEl.innerText || sEl.textContent || "").trim();
          if (sTxt.length >= 5) return { element: sEl, text: sTxt };
        }
      }
      const aTxt = (active.innerText || active.textContent || "").trim();
      if (aTxt.length >= 5) return { element: active, text: aTxt };
    }

    // 3. Fallback specifically for Google Gemini <rich-textarea>
    const richTextarea = document.querySelector("rich-textarea");
    if (richTextarea) {
      if (richTextarea.shadowRoot) {
        const editor = richTextarea.shadowRoot.querySelector("[contenteditable='true'], .ql-editor, p");
        if (editor) {
          const gTxt = (editor.innerText || editor.textContent || "").trim();
          if (gTxt.length >= 5) return { element: editor, text: gTxt };
        }
      }
      const gTxt = (richTextarea.innerText || richTextarea.textContent || "").trim();
      if (gTxt.length >= 5) return { element: richTextarea, text: gTxt };
    }

    // 4. Default target
    const fallbackEl = (event && event.target) ? event.target : active;
    const fbText = (fallbackEl && (fallbackEl.value || fallbackEl.innerText || fallbackEl.textContent || "")) || "";
    return { element: fallbackEl, text: fbText.trim() };
  }

  // ---------------------------------------------------------------------------
  // 1. ACTIVE CLIPBOARD PASTE INTERCEPTION
  // ---------------------------------------------------------------------------
  function handlePaste(event) {
    try {
      const clipboardData = event.clipboardData || window.clipboardData;
      if (!clipboardData) return;

      const pastedText = clipboardData.getData("text");
      if (!pastedText || pastedText.trim().length < 5) return;

      const detected = detectSensitivePii(pastedText);

      if (detected.length > 0) {
        // Intercept and destroy paste in capture phase
        event.preventDefault();
        event.stopPropagation();
        event.stopImmediatePropagation();

        const { element } = getDeepTextAndElement(event);
        if (element && element.style) {
          element.style.outline = "3px solid #ff4d4f";
          element.style.boxShadow = "0 0 15px rgba(255, 77, 79, 0.6)";
        }

        showInPageAlert(detected, "Clipboard Paste Blocked", true);
        console.warn("%c[SecureFlow AI Paste Blocked]%c", "color: #ff4d4f; font-weight: bold;", "", detected);

        safeDispatchEvent({
          eventId: "ext-paste-" + Math.random().toString(36).substring(2, 10),
          timestamp: new Date().toISOString(),
          source: "CHROME_EXTENSION",
          eventType: "BROWSER_PASTE",
          content: pastedText,
          fileName: `paste_${window.location.hostname}.txt`,
          actionEnforced: "BLOCK",
          metadata: {
            url: window.location.href,
            hostname: window.location.hostname,
            pageTitle: document.title,
            instantFlags: detected
          }
        });
      }
    } catch (err) {
      console.warn("[SecureFlow AI] Paste handler warning:", err);
    }
  }

  window.addEventListener("paste", handlePaste, true);
  document.addEventListener("paste", handlePaste, true);

  // ---------------------------------------------------------------------------
  // 2. ACTIVE ENTER-KEY INTERCEPTION (Blocks Enter on Gemini, ChatGPT, Claude)
  // ---------------------------------------------------------------------------
  function handleKeyDown(event) {
    if (event.key === "Enter" && !event.shiftKey) {
      const { element, text } = getDeepTextAndElement(event);
      if (text && text.length >= 5) {
        const detected = detectSensitivePii(text);
        if (detected.length > 0) {
          // Hard cancel Enter key in capture phase before page handlers can send prompt
          event.preventDefault();
          event.stopPropagation();
          event.stopImmediatePropagation();

          if (element && element.style) {
            element.style.outline = "3px solid #ff4d4f";
            element.style.boxShadow = "0 0 20px rgba(255, 77, 79, 0.7)";
          }

          showInPageAlert(detected, "Transmission Blocked (Enter Key)", true);
          console.warn("%c[SecureFlow AI Prompt Send Blocked]%c Sensitive PII found:", "color: #ff4d4f; font-weight: bold;", "", detected);

          safeDispatchEvent({
            eventId: "ext-enter-" + Math.random().toString(36).substring(2, 10),
            timestamp: new Date().toISOString(),
            source: "CHROME_EXTENSION",
            eventType: "PROMPT_TRANSMISSION_BLOCKED",
            content: text,
            fileName: `blocked_enter_${window.location.hostname}.txt`,
            actionEnforced: "BLOCK",
            metadata: {
              url: window.location.href,
              hostname: window.location.hostname,
              trigger: "ENTER_KEY_ATTEMPT",
              instantFlags: detected
            }
          });

          return false;
        }
      }
    }
  }

  window.addEventListener("keydown", handleKeyDown, true);
  document.addEventListener("keydown", handleKeyDown, true);

  // ---------------------------------------------------------------------------
  // 3. ACTIVE "SEND" BUTTON CLICK INTERCEPTION
  // ---------------------------------------------------------------------------
  function handleClick(event) {
    const btn = event.target.closest("button, [role='button'], input[type='submit'], [aria-label*='send' i], [aria-label*='submit' i]");
    if (!btn) return;

    const { element, text } = getDeepTextAndElement(event);
    if (text && text.length >= 5) {
      const detected = detectSensitivePii(text);
      if (detected.length > 0) {
        event.preventDefault();
        event.stopPropagation();
        event.stopImmediatePropagation();

        if (element && element.style) {
          element.style.outline = "3px solid #ff4d4f";
          element.style.boxShadow = "0 0 20px rgba(255, 77, 79, 0.7)";
        }

        showInPageAlert(detected, "Transmission Blocked (Send Button)", true);
        console.warn("%c[SecureFlow AI Send Button Blocked]%c", "color: #ff4d4f; font-weight: bold;", "", detected);

        safeDispatchEvent({
          eventId: "ext-click-" + Math.random().toString(36).substring(2, 10),
          timestamp: new Date().toISOString(),
          source: "CHROME_EXTENSION",
          eventType: "PROMPT_TRANSMISSION_BLOCKED",
          content: text,
          fileName: `blocked_click_${window.location.hostname}.txt`,
          actionEnforced: "BLOCK",
          metadata: {
            url: window.location.href,
            hostname: window.location.hostname,
            trigger: "BUTTON_CLICK_ATTEMPT",
            instantFlags: detected
          }
        });

        return false;
      }
    }
  }

  window.addEventListener("click", handleClick, true);
  document.addEventListener("click", handleClick, true);

  // ---------------------------------------------------------------------------
  // 4. REAL-TIME TYPING & INPUT INTERCEPTION (Debounced 300ms)
  // ---------------------------------------------------------------------------
  let typingTimer = null;
  const TYPING_DEBOUNCE_MS = 300;

  function handleInput(event) {
    clearTimeout(typingTimer);
    typingTimer = setTimeout(() => {
      const { element, text } = getDeepTextAndElement(event);
      if (!text || text.length < 5) {
        if (element && element.dataset && element.dataset.sfFlagged) {
          element.style.outline = "";
          element.style.boxShadow = "";
          delete element.dataset.sfFlagged;
        }
        return;
      }

      const detected = detectSensitivePii(text);
      if (detected.length > 0) {
        if (element && element.style) {
          element.style.outline = "2px solid #ff4d4f";
          element.style.boxShadow = "0 0 12px rgba(255, 77, 79, 0.45)";
          element.dataset.sfFlagged = "true";
        }

        // Silent visual badge on input border without spawning disruptive popups
        console.warn("%c[SecureFlow DLP Typing Warning]%c", "color: #ff4d4f; font-weight: bold;", "", detected);

        safeDispatchEvent({
          eventId: "ext-type-" + Math.random().toString(36).substring(2, 10),
          timestamp: new Date().toISOString(),
          source: "CHROME_EXTENSION",
          eventType: "BROWSER_TYPING",
          content: text,
          fileName: `typing_${window.location.hostname}.txt`,
          actionEnforced: "WARN",
          metadata: {
            url: window.location.href,
            hostname: window.location.hostname,
            pageTitle: document.title,
            instantFlags: detected
          }
        });
      } else if (element && element.dataset && element.dataset.sfFlagged) {
        element.style.outline = "";
        element.style.boxShadow = "";
        delete element.dataset.sfFlagged;
      }
    }, TYPING_DEBOUNCE_MS);
  }

  window.addEventListener("input", handleInput, true);
  document.addEventListener("input", handleInput, true);
  document.addEventListener("change", handleInput, true);

  // ---------------------------------------------------------------------------
  // 5. ACTIVE FILE ATTACHMENT & DRAG-AND-DROP INTERCEPTION
  // ---------------------------------------------------------------------------
  function inspectFileObject(file, sourceElement) {
    if (!file) return;

    // A. Plain text files (.txt, .csv, .log, .json, .xml, .md, .sql)
    if (file.type.startsWith("text/") || /\.(txt|csv|log|json|xml|md|sql)$/i.test(file.name)) {
      const reader = new FileReader();
      reader.onload = function (e) {
        const text = e.target.result || "";
        const detected = detectSensitivePii(text);
        if (detected.length > 0) {
          if (sourceElement && "value" in sourceElement) {
            try { sourceElement.value = ""; } catch (_) {}
          }
          showInPageAlert(detected, `File Upload Blocked: ${file.name}`, true);
          alert(`[SecureFlow AI Guard]\n\nUpload of "${file.name}" blocked!\nConfidential data detected:\n- ${detected.join("\n- ")}`);

          safeDispatchEvent({
            eventId: "ext-file-" + Math.random().toString(36).substring(2, 10),
            timestamp: new Date().toISOString(),
            source: "CHROME_EXTENSION",
            eventType: "FILE_UPLOAD_BLOCKED",
            fileName: file.name,
            content: text.substring(0, 5000),
            actionEnforced: "BLOCK",
            metadata: {
              url: window.location.href,
              hostname: window.location.hostname,
              fileSize: file.size,
              fileType: file.type,
              instantFlags: detected
            }
          });
        }
      };
      reader.readAsText(file);
    } 
    // B. Binary documents & images (.pdf, .docx, .xlsx, .png, .jpg)
    else if (/\.(pdf|docx|xlsx|png|jpg|jpeg|bmp)$/i.test(file.name) || file.type.startsWith("image/") || file.type === "application/pdf") {
      const reader = new FileReader();
      reader.onload = function (e) {
        const base64Data = (e.target.result || "").split(",")[1];
        if (base64Data) {
          safeDispatchEvent({
            eventId: "ext-bin-" + Math.random().toString(36).substring(2, 10),
            timestamp: new Date().toISOString(),
            source: "CHROME_EXTENSION",
            eventType: "BINARY_DOCUMENT_UPLOAD",
            fileName: file.name,
            fileBytesBase64: base64Data,
            actionEnforced: "INSPECT",
            metadata: {
              url: window.location.href,
              hostname: window.location.hostname,
              fileSize: file.size,
              fileType: file.type
            }
          });
        }
      };
      reader.readAsDataURL(file);
    }
  }

  // Intercept file picker changes
  window.addEventListener("change", function (event) {
    const target = event.target;
    if (target && target.type === "file" && target.files && target.files.length > 0) {
      for (let i = 0; i < target.files.length; i++) {
        inspectFileObject(target.files[i], target);
      }
    }
  }, true);

  // Intercept drag-and-drop file drops onto web pages
  window.addEventListener("drop", function (event) {
    if (event.dataTransfer && event.dataTransfer.files && event.dataTransfer.files.length > 0) {
      for (let i = 0; i < event.dataTransfer.files.length; i++) {
        inspectFileObject(event.dataTransfer.files[i], null);
      }
    }
  }, true);

  // ---------------------------------------------------------------------------
  // 6. MULTI-CHANNEL SAFE DISPATCHER (Never crashes if context is invalidated)
  // ---------------------------------------------------------------------------
  function safeDispatchEvent(eventPayload) {
    try {
      if (typeof chrome !== "undefined" && chrome.runtime && typeof chrome.runtime.sendMessage === "function") {
        chrome.runtime.sendMessage({
          type: "SECUREFLOW_INGEST_EVENT",
          payload: eventPayload
        }, (response) => {
          if (chrome.runtime && chrome.runtime.lastError) {
            directIngestFallback(eventPayload);
          } else if (response && response.riskScore > 75) {
            showInPageAlert([`Blocked by Policy (Risk: ${response.riskScore}/100)`], "SOC Central Policy", true);
          }
        });
        return;
      }
    } catch (_) {
      // Extension context invalidated / reloaded
    }

    directIngestFallback(eventPayload);
  }

  function directIngestFallback(eventPayload) {
    try {
      fetch("http://localhost:9090/api/v1/events/ingest", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Capture-Source": "SecureFlow-BrowserExt-Direct"
        },
        body: JSON.stringify(eventPayload)
      }).catch(() => {
        fetch("http://127.0.0.1:8000/api/v1/events/ingest", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(eventPayload)
        }).catch(() => {});
      });
    } catch (_) {}
  }

  // ---------------------------------------------------------------------------
  // 6. IN-PAGE FLOATING ALERT BANNER
  // ---------------------------------------------------------------------------
  function ensureStylesInjected() {
    if (document.getElementById("sf-dlp-styles")) return;
    const styleEl = document.createElement("style");
    styleEl.id = "sf-dlp-styles";
    styleEl.textContent = `
      @keyframes sfFadeIn {
        from { opacity: 0; transform: translateY(-12px) scale(0.96); }
        to { opacity: 1; transform: translateY(0) scale(1); }
      }
      @keyframes sfPulse {
        0%, 100% { box-shadow: 0 0 10px #ff4d4f; }
        50% { box-shadow: 0 0 20px #ff7875; }
      }
    `;
    (document.head || document.documentElement).appendChild(styleEl);
  }

  function showInPageAlert(reasons, context, isBlocked) {
    ensureStylesInjected();
    const existing = document.getElementById("sf-dlp-alert-banner");
    if (existing) existing.remove();

    const banner = document.createElement("div");
    banner.id = "sf-dlp-alert-banner";
    banner.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      background: #0f111a;
      color: #ffffff;
      border: 1px solid #ff4d4f;
      box-shadow: 0 12px 35px rgba(0,0,0,0.7), 0 0 15px rgba(255,77,79,0.3);
      padding: 14px 18px;
      border-radius: 10px;
      z-index: 2147483647;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      font-size: 13px;
      display: flex;
      align-items: center;
      gap: 14px;
      animation: sfFadeIn 0.25s cubic-bezier(0.16, 1, 0.3, 1);
    `;

    banner.innerHTML = `
      <div style="width: 12px; height: 12px; border-radius: 50%; background: #ff4d4f; animation: sfPulse 1.5s infinite;"></div>
      <div>
        <div style="font-weight: 700; color: #ff7875; font-size: 14px;">
          ${isBlocked ? "🛡️ SecureFlow DLP Blocked" : "⚠️ SecureFlow DLP Warning"}
        </div>
        <div style="color: #cbd5e1; font-size: 12px; margin-top: 2px;">
          ${context}: <strong style="color: #fca5a5;">${reasons.join(", ")}</strong>
        </div>
      </div>
      <button id="sf-close-btn" style="background: transparent; border: none; color: #94a3b8; font-size: 18px; cursor: pointer; margin-left: 10px; line-height: 1;">&times;</button>
    `;

    (document.body || document.documentElement).appendChild(banner);

    document.getElementById("sf-close-btn")?.addEventListener("click", () => {
      banner.remove();
    });

    setTimeout(() => {
      if (banner && banner.parentNode) {
        banner.remove();
      }
    }, 7000);
  }
})();
