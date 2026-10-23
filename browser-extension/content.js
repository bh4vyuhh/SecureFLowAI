// =============================================================================
// SecureFlow AI - Enterprise Client Browser DLP Agent (Manifest V3 Content Script)
// Universal Form Submission, Webmail (Gmail, Outlook), Chat (Gemini, ChatGPT, Claude),
// Keystroke & File Upload Guard Powered by Hybrid AI Model + Deterministic Checksums
// =============================================================================

(function () {
  // Do NOT intercept or show alerts on the internal SecureFlow SOC Admin Console
  const host = window.location.hostname;
  const port = window.location.port;
  if ((host === "localhost" || host === "127.0.0.1") && (port === "5174" || port === "8000" || port === "9090")) {
    console.log("%c[SecureFlow AI]%c Extension dormant on internal SOC Console.", "color: #8df85f; font-weight: bold;", "");
    return;
  }

  console.log(
    "%c[SecureFlow AI]%c DLP Browser Agent Initialized (v2.3 Production Final Guard).",
    "color: #8df85f; font-weight: bold;",
    "color: inherit;"
  );

  // ---------------------------------------------------------------------------
  // 1. DLP Detection Patterns (Banking, PCI-DSS, PII, Secrets, Passwords)
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

    // Credit Card: Valid Luhn OR 16-grouped digits with card context
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

  // ---------------------------------------------------------------------------
  // 2. AI Neural Model Integration & Query Cache (/api/v1/scan/dlp on Port 8000)
  // ---------------------------------------------------------------------------
  const aiScanCache = new Map();
  const MAX_CACHE_SIZE = 150;

  function getFromAiCache(text) {
    if (!text) return null;
    return aiScanCache.get(text.trim());
  }

  function setInAiCache(text, result) {
    if (!text || !result) return;
    if (aiScanCache.size >= MAX_CACHE_SIZE) {
      const firstKey = aiScanCache.keys().next().value;
      aiScanCache.delete(firstKey);
    }
    aiScanCache.set(text.trim(), result);
  }

  async function queryAiDlpModel(text) {
    if (!text || text.trim().length < 12) return null;
    const cleanText = text.trim();

    const cached = getFromAiCache(cleanText);
    if (cached) return cached;

    // A. Query via Background Service Worker (Bypasses host page CSP)
    try {
      if (typeof chrome !== "undefined" && chrome.runtime && typeof chrome.runtime.sendMessage === "function") {
        const response = await new Promise((resolve) => {
          chrome.runtime.sendMessage(
            {
              type: "SECUREFLOW_AI_SCAN",
              payload: {
                text: cleanText,
                destinationDomain: window.location.hostname,
                sourceAction: "prompt_injection"
              }
            },
            (res) => {
              if (chrome.runtime && chrome.runtime.lastError) {
                resolve(null);
              } else {
                resolve(res);
              }
            }
          );
        });

        if (response && response.status === "success") {
          setInAiCache(cleanText, response);
          return response;
        }
      }
    } catch (_) {}

    // B. Direct Fallback Query to FastAPI Port 8000
    try {
      const res = await fetch("http://127.0.0.1:8000/api/v1/scan/dlp", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          client_id: "browser-ext-direct",
          destination_domain: window.location.hostname,
          text: cleanText,
          mode: "mask"
        })
      });
      if (res.ok) {
        const data = await res.json();
        const formatted = {
          status: "success",
          tier: data.classification_tier,
          riskScore: data.risk_score,
          action: data.enforcement_action,
          entities: data.detected_entities || [],
          threatCategory: data.threat_category,
          explanation: data.explanation
        };
        setInAiCache(cleanText, formatted);
        return formatted;
      }
    } catch (_) {}

    return null;
  }

  // ---------------------------------------------------------------------------
  // 3. Universal Element Text Extraction (Google Gemini, Quill, ProseMirror, Shadow DOM)
  // ---------------------------------------------------------------------------
  function getTopEditableContainer(el) {
    if (!el || el.nodeType !== 1) return null;
    return (
      el.closest(
        "rich-textarea, div[aria-label*='Message Body' i], div[aria-label*='Message body' i], div.Am.Al.editable, [contenteditable='true'], [role='textbox'], .ql-editor, .ProseMirror, [data-slate-editor='true'], .editable, #prompt-textarea"
      ) || el
    );
  }

  function getElementValueOrText(el) {
    if (!el) return "";

    // A. Native Form Inputs (INPUT, TEXTAREA, SELECT)
    if (el.tagName === "INPUT" || el.tagName === "TEXTAREA" || el.tagName === "SELECT") {
      return el.value || "";
    }

    // B. Google Gemini custom web component (<rich-textarea>) and Quill editors
    if (el.tagName === "RICH-TEXTAREA" || el.classList?.contains("ql-editor") || el.classList?.contains("textarea")) {
      const qlEditor = el.querySelector?.(".ql-editor, [contenteditable='true'], [role='textbox'], p");
      if (qlEditor && qlEditor !== el) {
        const qlText = (qlEditor.innerText || qlEditor.textContent || "").trim();
        if (qlText) return qlText;
      }
    }

    // C. Inspect Shadow DOM if attached
    if (el.shadowRoot) {
      const innerEditor = el.shadowRoot.querySelector(
        ".ql-editor, [contenteditable='true'], [role='textbox'], textarea, input, p"
      );
      if (innerEditor) {
        const sText = getElementValueOrText(innerEditor).trim();
        if (sText) return sText;
      }
      const shadowTxt = (el.shadowRoot.innerText || el.shadowRoot.textContent || "").trim();
      if (shadowTxt) return shadowTxt;
    }

    // D. Check for child contenteditable or Quill nodes
    const nestedEditable = el.querySelector?.(
      ".ql-editor, [contenteditable='true'], [role='textbox'], textarea, p"
    );
    if (nestedEditable && nestedEditable !== el) {
      const nestedText = (nestedEditable.innerText || nestedEditable.textContent || nestedEditable.value || "").trim();
      if (nestedText) return nestedText;
    }

    // E. General innerText or textContent fallback
    const directText = (el.innerText || el.textContent || "").trim();
    if (directText) return directText;

    // F. Fallback property check
    if (typeof el.value === "string" && el.value.trim()) {
      return el.value.trim();
    }

    return "";
  }

  function getDeepTextAndElement(event) {
    const path = (event && typeof event.composedPath === "function") ? event.composedPath() : [];
    const target = (event && event.target) ? event.target : document.activeElement;

    // 1. Traverse composed path (handles Web Components and Shadow DOM)
    for (let el of path) {
      if (!el || el.nodeType !== 1) continue;
      const topContainer = getTopEditableContainer(el);
      if (topContainer) {
        const text = getElementValueOrText(topContainer).trim();
        if (text.length >= 5) {
          return { element: topContainer, text: text };
        }
      }
    }

    // 2. Target element inspection
    if (target && target.nodeType === 1) {
      const topContainer = getTopEditableContainer(target);
      if (topContainer) {
        const text = getElementValueOrText(topContainer).trim();
        if (text.length >= 5) {
          return { element: topContainer, text: text };
        }
      }
      const val = getElementValueOrText(target).trim();
      if (val.length >= 5) {
        return { element: target, text: val };
      }
    }

    // 3. Document activeElement inspection
    const active = document.activeElement;
    if (active && active.nodeType === 1) {
      const topContainer = getTopEditableContainer(active);
      if (topContainer) {
        const text = getElementValueOrText(topContainer).trim();
        if (text.length >= 5) {
          return { element: topContainer, text: text };
        }
      }
      const aVal = getElementValueOrText(active).trim();
      if (aVal.length >= 5) {
        return { element: active, text: aVal };
      }
    }

    // 4. Global fallback to active AI prompts or chat boxes on the page
    const aiSelectors = [
      "rich-textarea",
      "div.ql-editor[contenteditable='true']",
      "#prompt-textarea",
      "div[role='textbox'][contenteditable='true']",
      "div[aria-label*='Message Body' i]",
      "div[aria-label*='Message body' i]",
      "div.Am.Al.editable",
    ];
    for (let sel of aiSelectors) {
      const el = document.querySelector(sel);
      if (el) {
        const txt = getElementValueOrText(el).trim();
        if (txt.length >= 5) return { element: el, text: txt };
      }
    }

    return { element: target || active, text: "" };
  }

  // ---------------------------------------------------------------------------
  // 4. Scan Multiple Elements (Forms, Email Composers, Chat Boxes)
  // ---------------------------------------------------------------------------
  function inspectElementsCollection(elements) {
    for (let el of elements) {
      if (!el || el.nodeType !== 1) continue;
      if (el.type === "hidden" || el.type === "submit" || el.type === "button") continue;

      const txt = getElementValueOrText(el).trim();
      if (txt.length >= 5) {
        const detected = detectSensitivePii(txt);
        const cachedAi = getFromAiCache(txt);
        if (detected.length > 0) {
          return { offendingElement: el, text: txt, detected };
        }
        if (cachedAi && (cachedAi.tier === "RESTRICTED" || (cachedAi.tier === "CONFIDENTIAL" && cachedAi.riskScore >= 70 && cachedAi.action === "BLOCK"))) {
          const aiReasons = [
            `AI Model: ${cachedAi.threatCategory?.replace(/_/g, " ") || cachedAi.tier} (${cachedAi.riskScore}% Risk)`
          ];
          return { offendingElement: el, text: txt, detected: aiReasons };
        }
      }
    }
    return null;
  }

  function findComposeOrFormContext(targetElement) {
    if (!targetElement) return null;

    // A. Check if target is inside a standard HTML form
    const form = targetElement.closest("form");
    if (form) return { type: "form", container: form };

    // B. Check if target is inside an email composer, chat input box, or prompt container
    const composer = targetElement.closest(
      "rich-textarea, .input-area-container, .bottom-container, .compose, .composer, .Am.Al, .chat-input, .msg-form, .email-composer, div.inboxsdk__compose"
    );
    if (composer) return { type: "composer", container: composer };

    return null;
  }

  function applyElementHighlight(element) {
    const visibleContainer =
      element?.closest?.("rich-textarea, .input-area-container, form, .composer, .Am.Al, .chat-input") || element;

    if (visibleContainer && visibleContainer.style) {
      visibleContainer.style.outline = "2.5px solid #ff4d4f";
      visibleContainer.style.boxShadow = "0 0 18px rgba(255, 77, 79, 0.6)";
      visibleContainer.dataset.sfFlagged = "true";
    }
  }

  function clearElementHighlight(element) {
    if (!element) return;
    const visibleContainer =
      element?.closest?.("rich-textarea, .input-area-container, form, .composer, .Am.Al, .chat-input") || element;

    if (visibleContainer && visibleContainer.dataset && visibleContainer.dataset.sfFlagged) {
      visibleContainer.style.outline = "";
      visibleContainer.style.boxShadow = "";
      delete visibleContainer.dataset.sfFlagged;
    }
  }

  function highlightAndBlock(element, detected, contextTitle, triggerType, textContent) {
    removeTypingWarningBadge();

    const visibleContainer =
      element?.closest?.("rich-textarea, .input-area-container, form, .composer, .Am.Al, .chat-input") || element;

    if (visibleContainer && visibleContainer.style) {
      visibleContainer.style.outline = "3.5px solid #ff4d4f";
      visibleContainer.style.boxShadow = "0 0 28px rgba(255, 77, 79, 0.85)";
      visibleContainer.dataset.sfFlagged = "true";
      try { visibleContainer.scrollIntoView({ behavior: "smooth", block: "center" }); } catch (_) {}
    }

    showInPageAlert(detected, contextTitle, true);
    console.warn(
      `%c[SecureFlow DLP BLOCKED]%c ${contextTitle} - Flagged:`,
      "color: #ff4d4f; font-weight: bold; font-size: 13px;",
      "",
      detected
    );

    safeDispatchEvent({
      eventId: "ext-block-" + Math.random().toString(36).substring(2, 10),
      timestamp: new Date().toISOString(),
      source: "CHROME_EXTENSION",
      eventType: "PROMPT_TRANSMISSION_BLOCKED",
      content: textContent,
      fileName: `blocked_${triggerType.toLowerCase()}_${window.location.hostname}.txt`,
      actionEnforced: "BLOCK",
      metadata: {
        url: window.location.href,
        hostname: window.location.hostname,
        pageTitle: document.title,
        trigger: triggerType,
        instantFlags: detected,
      },
    });
  }

  // ---------------------------------------------------------------------------
  // 5. FORM SUBMISSION INTERCEPTION (Intercepts all HTML Forms)
  // ---------------------------------------------------------------------------
  function handleFormSubmit(event) {
    const form = event.target;
    if (!form || !form.querySelectorAll) return;

    const inputs = form.querySelectorAll("input, textarea, select, [contenteditable='true']");
    const result = inspectElementsCollection(inputs);

    if (result) {
      event.preventDefault();
      event.stopPropagation();
      event.stopImmediatePropagation();

      highlightAndBlock(
        result.offendingElement,
        result.detected,
        "Form Submission Blocked",
        "FORM_SUBMIT",
        result.text
      );
      return false;
    }
  }

  window.addEventListener("submit", handleFormSubmit, true);
  document.addEventListener("submit", handleFormSubmit, true);

  // ---------------------------------------------------------------------------
  // 6. BUTTON CLICK INTERCEPTION (Gemini, ChatGPT, Claude, Gmail, Outlook, Forms)
  // ---------------------------------------------------------------------------
  function isSendOrSubmitButton(el) {
    if (!el || el.nodeType !== 1) return false;

    // Look for button or clickable element in hierarchy
    const btn = el.closest(
      "button, [role='button'], input[type='submit'], input[type='button'], a[role='button'], .aoO, .T-I-atl, .send-button, [data-tooltip*='Send' i], [aria-label*='Send' i], [aria-label*='prompt' i], [data-tooltip*='Ctrl-Enter' i], [aria-label*='Ctrl-Enter' i], [data-qa*='send' i], [data-testid*='send' i], [data-testid*='tweetButton' i]"
    );
    if (!btn) return false;

    // Explicit signatures
    if (btn.classList && (btn.classList.contains("aoO") || btn.classList.contains("T-I-atl") || btn.classList.contains("send-button"))) {
      return btn;
    }

    // Check attributes across all standard web applications
    const aria = (btn.getAttribute("aria-label") || "").toLowerCase();
    const tooltip = (btn.getAttribute("data-tooltip") || "").toLowerCase();
    const title = (btn.getAttribute("title") || "").toLowerCase();
    const btnText = (btn.innerText || btn.textContent || btn.value || "").toLowerCase().trim();
    const btnId = (btn.id || "").toLowerCase();
    const btnClass = (btn.className || "").toString().toLowerCase();

    const matchesSend =
      aria.includes("send") ||
      aria.includes("submit") ||
      aria.includes("prompt") ||
      aria.includes("ctrl-enter") ||
      tooltip.includes("send") ||
      tooltip.includes("submit") ||
      tooltip.includes("ctrl-enter") ||
      title.includes("send") ||
      title.includes("submit") ||
      title.includes("ctrl-enter") ||
      btnId.includes("send") ||
      btnId.includes("submit") ||
      btnClass.includes("send") ||
      btnClass.includes("submit") ||
      btnClass.includes("aoo") ||
      btn.type === "submit" ||
      /^(send|submit|post|publish|share|tweet|reply|transfer|pay|checkout|confirm|next|save|envoyer|enviar|senden)$/i.test(btnText) ||
      /\b(send|submit)\b/i.test(btnText);

    return matchesSend ? btn : false;
  }

  function handleSendClick(event) {
    const btn = isSendOrSubmitButton(event.target);
    if (!btn) return; // Not a send button -> let native click pass through instantly!

    let elementsToScan = [];

    // 1. Check parent compose dialog / form container
    const context = findComposeOrFormContext(btn);
    if (context && context.container) {
      elementsToScan = Array.from(
        context.container.querySelectorAll(
          "textarea, [contenteditable='true'], input:not([type='hidden']):not([type='submit']):not([type='button']), .ql-editor, div[role='textbox'], .Am.Al"
        )
      );
    }

    // 2. If no container was found, fallback to targeted active compose elements
    if (elementsToScan.length === 0) {
      const composerSelectors = [
        "rich-textarea .ql-editor",
        "rich-textarea [contenteditable='true']",
        "#prompt-textarea",
        ".Am.Al.editable",
        "div[role='textbox'][contenteditable='true']",
      ];
      for (let sel of composerSelectors) {
        const matched = document.querySelectorAll(sel);
        matched.forEach((m) => {
          if (!elementsToScan.includes(m)) elementsToScan.push(m);
        });
        if (elementsToScan.length > 0) break;
      }
    }

    // 3. Include document.activeElement if it is an editable input
    if (document.activeElement && !elementsToScan.includes(document.activeElement)) {
      if (document.activeElement.isContentEditable || document.activeElement.tagName === "TEXTAREA" || document.activeElement.tagName === "INPUT") {
        elementsToScan.push(document.activeElement);
      }
    }

    const result = inspectElementsCollection(elementsToScan);
    if (result) {
      // ONLY block if sensitive data is detected!
      event.preventDefault();
      event.stopPropagation();
      event.stopImmediatePropagation();

      highlightAndBlock(
        result.offendingElement,
        result.detected,
        "Transmission Blocked (Send Button)",
        "BUTTON_CLICK_ATTEMPT",
        result.text
      );
      return false;
    }

    // If clean, do NOT call preventDefault or stopPropagation.
    // The native button click proceeds directly on the FIRST click!
  }

  // Single clean capture click listener (eliminates multiple click requirements)
  document.addEventListener("click", handleSendClick, true);

  // ---------------------------------------------------------------------------
  // 7. KEYBOARD SHORTCUT & ENTER-KEY TRANSMISSION INTERCEPTION
  // ---------------------------------------------------------------------------
  function handleKeyDown(event) {
    const isEnter = event.key === "Enter" || event.keyCode === 13;
    if (!isEnter) return;

    const isCtrlOrCmd = event.ctrlKey || event.metaKey;
    const isShift = event.shiftKey;

    // A. Ctrl+Enter or Cmd+Enter: Standard Send shortcut in Gmail, Outlook, LinkedIn, Slack, etc.
    if (isCtrlOrCmd) {
      const { element, text } = getDeepTextAndElement(event);
      let detected = detectSensitivePii(text);

      const cachedAi = getFromAiCache(text);
      if (detected.length === 0 && cachedAi && (cachedAi.tier === "RESTRICTED" || (cachedAi.tier === "CONFIDENTIAL" && cachedAi.riskScore >= 70 && cachedAi.action === "BLOCK"))) {
        detected = [`AI Model: ${cachedAi.threatCategory?.replace(/_/g, " ") || cachedAi.tier} (${cachedAi.riskScore}% Risk)`];
      }

      if (detected.length > 0) {
        event.preventDefault();
        event.stopPropagation();
        event.stopImmediatePropagation();

        highlightAndBlock(
          element,
          detected,
          "Email Transmission Blocked (Ctrl+Enter Send)",
          "KEYBOARD_SHORTCUT_SEND",
          text
        );
        return false;
      }
    }

    // B. Plain Enter (without Shift) in single-line inputs, AI chat prompts (Gemini, ChatGPT), or forms
    if (!isCtrlOrCmd && !isShift) {
      const target = event.target || document.activeElement;

      // If inside a <form>, check form inputs before allowing Enter submission
      if (target && target.closest) {
        const form = target.closest("form");
        if (form) {
          const inputs = form.querySelectorAll("input, textarea, select, [contenteditable='true']");
          const result = inspectElementsCollection(inputs);
          if (result) {
            event.preventDefault();
            event.stopPropagation();
            event.stopImmediatePropagation();

            highlightAndBlock(
              result.offendingElement,
              result.detected,
              "Form Submission Blocked (Enter Key)",
              "FORM_ENTER_SUBMIT",
              result.text
            );
            return false;
          }
        }
      }

      // Check current element (e.g. Gemini prompt, ChatGPT prompt, Chatbox, single input)
      const { element, text } = getDeepTextAndElement(event);
      if (text && text.length >= 5) {
        let detected = detectSensitivePii(text);
        const cachedAi = getFromAiCache(text);
        if (detected.length === 0 && cachedAi && (cachedAi.tier === "RESTRICTED" || (cachedAi.tier === "CONFIDENTIAL" && cachedAi.riskScore >= 70 && cachedAi.action === "BLOCK"))) {
          detected = [`AI Model: ${cachedAi.threatCategory?.replace(/_/g, " ") || cachedAi.tier} (${cachedAi.riskScore}% Risk)`];
        }

        if (detected.length > 0) {
          event.preventDefault();
          event.stopPropagation();
          event.stopImmediatePropagation();

          highlightAndBlock(
            element,
            detected,
            "Prompt Transmission Blocked (Enter Key)",
            "ENTER_KEY_ATTEMPT",
            text
          );
          return false;
        }
      }
    }
  }

  document.addEventListener("keydown", handleKeyDown, true);

  // ---------------------------------------------------------------------------
  // 8. CLIPBOARD PASTE INTERCEPTION (Instant Zero-Exfiltration Intercept)
  // ---------------------------------------------------------------------------
  function handlePaste(event) {
    try {
      const clipboardData = event.clipboardData || window.clipboardData;
      if (!clipboardData) return;

      const pastedText = clipboardData.getData("text");
      if (!pastedText || pastedText.trim().length < 5) return;

      const detected = detectSensitivePii(pastedText);

      // Pre-warm AI model scan cache on paste
      if (pastedText.trim().length >= 12) {
        queryAiDlpModel(pastedText).then((aiRes) => {
          if (aiRes && (aiRes.tier === "RESTRICTED" || (aiRes.tier === "CONFIDENTIAL" && aiRes.riskScore >= 70 && aiRes.action === "BLOCK"))) {
            const { element } = getDeepTextAndElement(event);
            applyElementHighlight(element);
            const aiLabel = `AI Model: ${aiRes.threatCategory?.replace(/_/g, " ") || aiRes.tier} (${aiRes.riskScore}% Risk)`;
            showTypingWarningBadge([aiLabel], `AI DLP Alert: ${aiRes.tier} Tier`);
          }
        }).catch(() => {});
      }

      if (detected.length > 0) {
        event.preventDefault();
        event.stopPropagation();
        event.stopImmediatePropagation();

        const { element } = getDeepTextAndElement(event);
        highlightAndBlock(
          element,
          detected,
          "Clipboard Paste Blocked",
          "CLIPBOARD_PASTE",
          pastedText
        );
      }
    } catch (err) {
      console.warn("[SecureFlow AI] Paste handler warning:", err);
    }
  }

  document.addEventListener("paste", handlePaste, true);

  // ---------------------------------------------------------------------------
  // 9. REAL-TIME HYBRID TYPING DETECTION & FLOATING WARNING BADGE (Regex + AI Model)
  // ---------------------------------------------------------------------------
  let typingTimer = null;
  let currentScanId = 0;
  const TYPING_DEBOUNCE_MS = 350;

  function handleInput(event) {
    clearTimeout(typingTimer);
    const scanId = ++currentScanId;

    typingTimer = setTimeout(async () => {
      const { element, text } = getDeepTextAndElement(event);
      if (!text || text.length < 5) {
        removeTypingWarningBadge();
        clearElementHighlight(element);
        return;
      }

      // Tier 1: Local Deterministic Regex Scan
      const localHits = detectSensitivePii(text);
      if (localHits.length > 0) {
        applyElementHighlight(element);
        showTypingWarningBadge(localHits, "Sensitive PII Detected");
        return;
      }

      // Tier 2: Real-Time Deep AI Neural Model Scan via Port 8000
      // Only queries if text has at least 15 chars and multiple words
      if (text.length >= 15 && text.includes(" ")) {
        const aiResult = await queryAiDlpModel(text);
        if (scanId !== currentScanId) return; // Stale event

        // Only alert if the AI model flags high severity RESTRICTED or BLOCK action
        if (
          aiResult &&
          (aiResult.tier === "RESTRICTED" ||
            (aiResult.tier === "CONFIDENTIAL" && aiResult.riskScore >= 70 && aiResult.action === "BLOCK"))
        ) {
          applyElementHighlight(element);
          const aiLabels = [];
          if (
            aiResult.threatCategory &&
            aiResult.threatCategory !== "BENIGN_DATA" &&
            aiResult.threatCategory !== "BENIGN_BUSINESS_DATA"
          ) {
            aiLabels.push(`AI Model: ${aiResult.threatCategory.replace(/_/g, " ")} (${aiResult.riskScore}% Risk)`);
          } else {
            aiLabels.push(`AI Model: ${aiResult.tier} Tier (${aiResult.riskScore}% Risk)`);
          }

          showTypingWarningBadge(aiLabels, `AI DLP Engine: ${aiResult.tier} Tier`);
          return;
        }
      }

      // If clean (normal sentence): ENSURE NO POPUP and NO RED BORDER
      removeTypingWarningBadge();
      clearElementHighlight(element);
    }, TYPING_DEBOUNCE_MS);
  }

  // Bind input listeners
  document.addEventListener("input", handleInput, true);
  document.addEventListener("keyup", handleInput, true);
  document.addEventListener("change", handleInput, true);

  // ---------------------------------------------------------------------------
  // 10. ACTIVE FILE ATTACHMENT & DRAG-AND-DROP INTERCEPTION
  // ---------------------------------------------------------------------------
  function inspectFileObject(file, sourceElement) {
    if (!file) return;

    // Scan any document or file up to 15MB
    if (file.size <= 15 * 1024 * 1024) {
      const reader = new FileReader();
      reader.onload = async function (e) {
        const text = e.target.result || "";
        let detected = detectSensitivePii(text);

        // Also query AI DLP model for deep file content analysis
        if (text.length >= 15) {
          const aiRes = await queryAiDlpModel(text.substring(0, 4000));
          if (aiRes && (aiRes.tier === "RESTRICTED" || (aiRes.tier === "CONFIDENTIAL" && aiRes.riskScore >= 70 && aiRes.action === "BLOCK"))) {
            const aiLabel = `AI Model: ${aiRes.threatCategory?.replace(/_/g, " ") || aiRes.tier} (${aiRes.riskScore}% Risk)`;
            detected = Array.from(new Set([...detected, aiLabel]));
          }
        }

        if (detected.length > 0) {
          if (sourceElement && "value" in sourceElement) {
            try {
              sourceElement.value = "";
              if (sourceElement.files) {
                sourceElement.files = new DataTransfer().files;
              }
            } catch (_) {}
          }
          if (sourceElement && sourceElement.style) {
            sourceElement.style.outline = "3px solid #ff4d4f";
            sourceElement.style.boxShadow = "0 0 25px rgba(255, 77, 79, 0.75)";
          }
          showInPageAlert(detected, `File Upload Blocked: ${file.name}`, true);

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
              instantFlags: detected,
            },
          });
        }
      };
      reader.readAsText(file);
    }
  }

  // Listen for Kernel-Level Upload Blocks from network_guard.js
  window.addEventListener("SECUREFLOW_FILE_UPLOAD_BLOCKED", function (e) {
    if (!e || !e.detail) return;
    const { filename, reasons } = e.detail;
    showInPageAlert(reasons || ["Confidential Data"], `File Upload Blocked: ${filename || "Document"}`, true);

    const uploadTargets = document.querySelectorAll(
      "input[type='file'], [class*='dropzone'], [class*='upload'], [id*='dropzone'], [id*='upload'], [role='region']"
    );
    uploadTargets.forEach((el) => {
      if (el && el.style) {
        el.style.outline = "3px solid #ff4d4f";
        el.style.boxShadow = "0 0 25px rgba(255, 77, 79, 0.75)";
      }
      if (el && el.tagName === "INPUT" && el.type === "file") {
        try { el.value = ""; el.files = new DataTransfer().files; } catch (_) {}
      }
    });
  });

  // Relay Kernel-Level Audit Events from network_guard.js to Port 8000
  window.addEventListener("message", function (event) {
    if (event.data && event.data.type === "SECUREFLOW_PAGE_AUDIT_EVENT") {
      safeDispatchEvent(event.data.payload);
    }
  });

  // Inject Main-World Network Guard if not already active
  try {
    const s = document.createElement("script");
    s.src = chrome.runtime.getURL("network_guard.js");
    s.onload = function () { this.remove(); };
    (document.head || document.documentElement).appendChild(s);
  } catch (_) {}

  document.addEventListener(
    "change",
    function (event) {
      const target = event.target;
      if (target && target.type === "file" && target.files && target.files.length > 0) {
        for (let i = 0; i < target.files.length; i++) {
          inspectFileObject(target.files[i], target);
        }
      }
    },
    true
  );

  document.addEventListener(
    "drop",
    function (event) {
      if (event.dataTransfer && event.dataTransfer.files && event.dataTransfer.files.length > 0) {
        for (let i = 0; i < event.dataTransfer.files.length; i++) {
          inspectFileObject(event.dataTransfer.files[i], null);
        }
      }
    },
    true
  );

  // ---------------------------------------------------------------------------
  // 11. MULTI-CHANNEL SAFE DISPATCHER (Port 8000 Primary)
  // ---------------------------------------------------------------------------
  function safeDispatchEvent(eventPayload) {
    try {
      if (typeof chrome !== "undefined" && chrome.runtime && typeof chrome.runtime.sendMessage === "function") {
        chrome.runtime.sendMessage(
          {
            type: "SECUREFLOW_INGEST_EVENT",
            payload: eventPayload,
          },
          (response) => {
            if (chrome.runtime && chrome.runtime.lastError) {
              directIngestFallback(eventPayload);
            }
          }
        );
        return;
      }
    } catch (_) {}

    directIngestFallback(eventPayload);
  }

  function directIngestFallback(eventPayload) {
    fetch("http://127.0.0.1:8000/api/v1/events/ingest", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Capture-Source": "SecureFlow-BrowserExt-Direct",
      },
      body: JSON.stringify(eventPayload),
    }).catch(() => {
      fetch("http://localhost:8000/api/v1/events/ingest", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(eventPayload),
      }).catch(() => {});
    });
  }

  // ---------------------------------------------------------------------------
  // 12. IN-PAGE FLOATING ALERT BANNERS & REAL-TIME TYPING BADGES
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
        0%, 100% { box-shadow: 0 0 8px #ff4d4f; }
        50% { box-shadow: 0 0 18px #ff7875; }
      }
    `;
    (document.head || document.documentElement).appendChild(styleEl);
  }

  // Floating Real-Time Typing Badge
  function showTypingWarningBadge(detected, contextTitle) {
    ensureStylesInjected();
    let badge = document.getElementById("sf-dlp-typing-badge");
    if (!badge) {
      badge = document.createElement("div");
      badge.id = "sf-dlp-typing-badge";
      badge.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #0f111a;
        color: #ffffff;
        border: 1.5px solid #f59e0b;
        box-shadow: 0 12px 35px rgba(0,0,0,0.85), 0 0 16px rgba(245,158,11,0.35);
        padding: 12px 18px;
        border-radius: 10px;
        z-index: 2147483647;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        font-size: 13px;
        display: flex;
        align-items: center;
        gap: 12px;
        animation: sfFadeIn 0.2s cubic-bezier(0.16, 1, 0.3, 1);
        pointer-events: auto;
      `;
      (document.body || document.documentElement).appendChild(badge);
    }

    badge.innerHTML = `
      <div style="width: 12px; height: 12px; border-radius: 50%; background: #f59e0b; box-shadow: 0 0 10px #f59e0b; animation: sfPulse 1.2s infinite; flex-shrink: 0;"></div>
      <div>
        <div style="font-weight: 700; color: #fbbf24; font-size: 13px; letter-spacing: -0.2px;">
          ⚠️ ${contextTitle || "SecureFlow AI DLP &bull; Sensitive Data Detected"}
        </div>
        <div style="color: #cbd5e1; font-size: 12px; margin-top: 2px;">
          Flagged: <strong style="color: #fde68a;">${detected.join(", ")}</strong>
        </div>
        <div style="color: #94a3b8; font-size: 11px; margin-top: 2px;">
          Will be blocked upon Enter or Send.
        </div>
      </div>
    `;
  }

  function removeTypingWarningBadge() {
    const badge = document.getElementById("sf-dlp-typing-badge");
    if (badge) badge.remove();
  }

  // Full Screen Transmission Block Alert Banner
  function showInPageAlert(reasons, context, isBlocked) {
    ensureStylesInjected();
    const existing = document.getElementById("sf-dlp-alert-banner");
    if (existing) existing.remove();

    const banner = document.createElement("div");
    banner.id = "sf-dlp-alert-banner";
    banner.style.cssText = `
      position: fixed;
      top: 22px;
      right: 22px;
      background: #0f111a;
      color: #ffffff;
      border: 1.5px solid #ff4d4f;
      box-shadow: 0 14px 40px rgba(0,0,0,0.85), 0 0 20px rgba(255,77,79,0.35);
      padding: 16px 20px;
      border-radius: 12px;
      z-index: 2147483647;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      font-size: 13.5px;
      display: flex;
      align-items: center;
      gap: 14px;
      animation: sfFadeIn 0.25s cubic-bezier(0.16, 1, 0.3, 1);
    `;

    banner.innerHTML = `
      <div style="width: 14px; height: 14px; border-radius: 50%; background: #ff4d4f; animation: sfPulse 1.5s infinite; flex-shrink: 0;"></div>
      <div>
        <div style="font-weight: 700; color: #ff7875; font-size: 14px; letter-spacing: -0.2px;">
          ${isBlocked ? "🛡️ SecureFlow AI &bull; Transmission Blocked" : "⚠️ SecureFlow AI Warning"}
        </div>
        <div style="color: #cbd5e1; font-size: 12.5px; margin-top: 3px; line-height: 1.4;">
          ${context}: <strong style="color: #fca5a5;">${reasons.join(", ")}</strong>
        </div>
      </div>
      <button id="sf-close-btn" style="background: transparent; border: none; color: #94a3b8; font-size: 20px; cursor: pointer; margin-left: 12px; line-height: 1;">&times;</button>
    `;

    (document.body || document.documentElement).appendChild(banner);

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
