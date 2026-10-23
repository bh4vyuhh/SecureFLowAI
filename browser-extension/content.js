// =============================================================================
// SecureFlow AI - Enterprise Client Browser DLP Agent (Manifest V3 Content Script)
// Universal Form Submission, Webmail (Gmail, Outlook), Chat, Keystroke & File Guard
// =============================================================================

(function () {
  console.log(
    "%c[SecureFlow AI]%c DLP Browser Agent Initialized (v2.0 Universal Form, Email & Web Application Guard).",
    "color: #8df85f; font-weight: bold;",
    "color: inherit;"
  );

  // ---------------------------------------------------------------------------
  // 1. DLP Detection Patterns (Banking, PCI-DSS, PII, Secrets, Passwords)
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
    PASSWORD_SECRET: /(?:password|passwd|pwd|db_pass|secret|jwt_secret|private_key|access_key|passcode|passphrase)[\s:=]+([^\s,;'"<>]{4,})/i,
    PLAIN_PASSWORD: /\b(?:my\s+)?(?:password|secret|passcode)\s+(?:is|:)\s*([^\s,;'"<>]{4,})/i,
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

    // Credit Card: Valid Luhn OR grouped 15-16 digit sequence OR digits with card context OR 16 digits
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
    if (DLP_PATTERNS.ABA_ROUTING.test(text)) hits.push("ABA Routing Number");
    if (DLP_PATTERNS.SWIFT_BIC.test(text)) hits.push("SWIFT / BIC");
    if (DLP_PATTERNS.PRIVATE_KEY.test(text)) hits.push("Cryptographic Private Key");
    if (DLP_PATTERNS.API_KEY.test(text)) hits.push("Live API Credential");
    if (DLP_PATTERNS.PASSWORD_SECRET.test(text) || DLP_PATTERNS.PLAIN_PASSWORD.test(text)) hits.push("Exposed Password / Secret");
    if (DLP_PATTERNS.BEARER_TOKEN.test(text) || DLP_PATTERNS.JWT_TOKEN.test(text)) hits.push("Authentication Token");
    if (DLP_PATTERNS.DB_CONN.test(text)) hits.push("Database Connection String");
    if (DLP_PATTERNS.CONFIDENTIAL.test(text)) hits.push("Confidential Document Marker");

    return hits;
  }

  // ---------------------------------------------------------------------------
  // 2. Universal Element Text Collector & Top-Level Compose Container Resolution
  // ---------------------------------------------------------------------------
  function getTopEditableContainer(el) {
    if (!el || el.nodeType !== 1) return null;
    return el.closest(
      "div[aria-label*='Message Body' i], div[aria-label*='Message body' i], div.Am.Al.editable, [contenteditable='true'], [role='textbox'], .ql-editor, .ProseMirror, [data-slate-editor='true'], rich-textarea, .editable"
    );
  }

  function getElementValueOrText(el) {
    if (!el) return "";
    if (typeof el.value === "string" && el.tagName !== "DIV" && el.tagName !== "SPAN") {
      return el.value;
    }
    if (el.shadowRoot) {
      const inner = el.shadowRoot.querySelector("textarea, input, [contenteditable='true'], .ql-editor, p");
      if (inner) return getElementValueOrText(inner);
    }
    return el.innerText || el.textContent || "";
  }

  function getDeepTextAndElement(event) {
    const path = (event && typeof event.composedPath === "function") ? event.composedPath() : [];
    const target = (event && event.target) ? event.target : document.activeElement;

    // 1. Resolve to outermost editable container if user is inside a rich composer (Gmail, Outlook, Slack, etc.)
    for (let el of path) {
      if (!el || el.nodeType !== 1) continue;
      const topContainer = getTopEditableContainer(el);
      if (topContainer) {
        const text = (topContainer.innerText || topContainer.textContent || "").trim();
        if (text.length >= 5) {
          return { element: topContainer, text: text };
        }
      }
    }

    if (target && target.nodeType === 1) {
      const topContainer = getTopEditableContainer(target);
      if (topContainer) {
        const text = (topContainer.innerText || topContainer.textContent || "").trim();
        if (text.length >= 5) {
          return { element: topContainer, text: text };
        }
      }
      const val = getElementValueOrText(target).trim();
      if (val.length >= 5) {
        return { element: target, text: val };
      }
    }

    const active = document.activeElement;
    if (active && active.nodeType === 1) {
      const topContainer = getTopEditableContainer(active);
      if (topContainer) {
        const text = (topContainer.innerText || topContainer.textContent || "").trim();
        if (text.length >= 5) {
          return { element: topContainer, text: text };
        }
      }
      const aVal = getElementValueOrText(active).trim();
      if (aVal.length >= 5) {
        return { element: active, text: aVal };
      }
    }

    const richTextarea = document.querySelector("rich-textarea");
    if (richTextarea) {
      const gTxt = getElementValueOrText(richTextarea).trim();
      if (gTxt.length >= 5) return { element: richTextarea, text: gTxt };
    }

    return { element: target || active, text: "" };
  }

  // ---------------------------------------------------------------------------
  // 3. Scan Multiple Elements (Forms, Email Composers, Chat Boxes)
  // ---------------------------------------------------------------------------
  function inspectElementsCollection(elements) {
    for (let el of elements) {
      if (!el || el.nodeType !== 1) continue;
      if (el.type === "hidden" || el.type === "submit" || el.type === "button") continue;

      const txt = getElementValueOrText(el).trim();
      if (txt.length >= 5) {
        const detected = detectSensitivePii(txt);
        if (detected.length > 0) {
          return { offendingElement: el, text: txt, detected };
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

    // B. Check if target is inside an email composer, modal dialog, or chat container
    const composer = targetElement.closest(
      "[role='dialog'], [role='region'], .compose, .composer, .Am.Al, .modal, .chat-input, .msg-form, .email-composer, table.Ao, div.AD, div.nH, div.M9, div.inboxsdk__compose"
    );
    if (composer) return { type: "composer", container: composer };

    return null;
  }

  function highlightAndBlock(element, detected, contextTitle, triggerType, textContent) {
    if (element && element.style) {
      element.style.outline = "3px solid #ff4d4f";
      element.style.boxShadow = "0 0 22px rgba(255, 77, 79, 0.75)";
      element.dataset.sfFlagged = "true";
      try { element.scrollIntoView({ behavior: "smooth", block: "center" }); } catch (_) {}
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
  // 4. FORM SUBMISSION INTERCEPTION (Intercepts all HTML Forms)
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
  // 5. BUTTON CLICK INTERCEPTION (Gmail Send, Outlook, Google Forms, Web Apps)
  // ---------------------------------------------------------------------------
  function isSendOrSubmitButton(el) {
    if (!el || el.nodeType !== 1) return false;

    // Look for button or clickable element in hierarchy
    const btn = el.closest(
      "button, [role='button'], input[type='submit'], input[type='button'], a[role='button'], .aoO, .T-I-atl, [data-tooltip*='Send' i], [aria-label*='Send' i], [data-tooltip*='Ctrl-Enter' i], [aria-label*='Ctrl-Enter' i], [data-qa*='send' i], [data-testid*='send' i], [data-testid*='tweetButton' i]"
    );
    if (!btn) return false;

    // A. Gmail Send Button explicit class signature (.aoO is Gmail's permanent Send button class)
    if (btn.classList && (btn.classList.contains("aoO") || btn.classList.contains("T-I-atl"))) {
      return btn;
    }

    // B. Check attributes across all standard web applications
    const aria = (btn.getAttribute("aria-label") || "").toLowerCase();
    const tooltip = (btn.getAttribute("data-tooltip") || "").toLowerCase();
    const title = (btn.getAttribute("title") || "").toLowerCase();
    const btnText = (btn.innerText || btn.textContent || btn.value || "").toLowerCase().trim();
    const btnId = (btn.id || "").toLowerCase();
    const btnClass = (btn.className || "").toString().toLowerCase();

    const matchesSend =
      aria.includes("send") ||
      aria.includes("submit") ||
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

  function interceptSendAttempt(event, triggerType) {
    const btn = isSendOrSubmitButton(event.target);
    if (!btn) return false;

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

    // 2. Also always scan common webmail compose bodies (Gmail, Outlook, etc.)
    const webmailSelectors = [
      "div[aria-label*='Message Body' i]",
      "div[aria-label*='Message body' i]",
      "div.Am.Al.editable",
      "div[role='textbox'][contenteditable='true']",
      "#prompt-textarea",
      "rich-textarea",
      ".ql-editor",
      ".ProseMirror",
      "[data-slate-editor='true']"
    ];
    for (let sel of webmailSelectors) {
      const matched = document.querySelectorAll(sel);
      matched.forEach((m) => {
        if (!elementsToScan.includes(m)) elementsToScan.push(m);
      });
    }

    // 3. Include document.activeElement
    if (document.activeElement && !elementsToScan.includes(document.activeElement)) {
      elementsToScan.push(document.activeElement);
    }

    // 4. Universal page fallback if no elements found yet
    if (elementsToScan.length === 0) {
      const container = btn.closest(".container, .card, .box, section, main, article, body") || document.body || document;
      elementsToScan = Array.from(
        container.querySelectorAll(
          "textarea, [contenteditable='true'], input:not([type='hidden']):not([type='submit']):not([type='button']), .ql-editor, div[role='textbox']"
        )
      );
    }

    const result = inspectElementsCollection(elementsToScan);
    if (result) {
      event.preventDefault();
      event.stopPropagation();
      event.stopImmediatePropagation();

      highlightAndBlock(
        result.offendingElement,
        result.detected,
        `Transmission Blocked (${triggerType})`,
        "BUTTON_CLICK_ATTEMPT",
        result.text
      );
      return true;
    }
    return false;
  }

  // Intercept click, pointerdown, and mousedown in capture phase to preempt webmail handlers
  window.addEventListener("click", (e) => interceptSendAttempt(e, "Send Button"), true);
  document.addEventListener("click", (e) => interceptSendAttempt(e, "Send Button"), true);
  window.addEventListener("mousedown", (e) => interceptSendAttempt(e, "Send MouseDown"), true);
  document.addEventListener("mousedown", (e) => interceptSendAttempt(e, "Send MouseDown"), true);
  window.addEventListener("pointerdown", (e) => interceptSendAttempt(e, "Send PointerDown"), true);
  document.addEventListener("pointerdown", (e) => interceptSendAttempt(e, "Send PointerDown"), true);

  // ---------------------------------------------------------------------------
  // 6. KEYBOARD SHORTCUT & ENTER-KEY TRANSMISSION INTERCEPTION
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

      let offendingEl = element;
      let offendingText = text;

      // If not detected in immediate focused element, check all open composers on the page
      if (detected.length === 0) {
        const composers = document.querySelectorAll(
          "div[aria-label*='Message Body' i], div[aria-label*='Message body' i], div.Am.Al.editable, [contenteditable='true'][role='textbox'], .ql-editor, .ProseMirror"
        );
        for (let comp of composers) {
          const compTxt = (comp.innerText || comp.textContent || "").trim();
          const hits = detectSensitivePii(compTxt);
          if (hits.length > 0) {
            detected = hits;
            offendingEl = comp;
            offendingText = compTxt;
            break;
          }
        }
      }

      if (detected.length > 0) {
        event.preventDefault();
        event.stopPropagation();
        event.stopImmediatePropagation();

        highlightAndBlock(
          offendingEl,
          detected,
          "Email Transmission Blocked (Ctrl+Enter Send)",
          "KEYBOARD_SHORTCUT_SEND",
          offendingText
        );
        return false;
      }
    }

    // B. Plain Enter (without Shift) in single-line inputs, chatboxes, or forms
    if (!isCtrlOrCmd && !isShift) {
      const target = event.target || document.activeElement;

      // If inside a <form> (e.g. Google Forms), check ALL form inputs before allowing Enter submission
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

      // Check current element (e.g. Chatbox, AI prompt, single input)
      const { element, text } = getDeepTextAndElement(event);
      if (text && text.length >= 5) {
        const detected = detectSensitivePii(text);
        if (detected.length > 0) {
          event.preventDefault();
          event.stopPropagation();
          event.stopImmediatePropagation();

          highlightAndBlock(
            element,
            detected,
            "Transmission Blocked (Enter Key)",
            "ENTER_KEY_ATTEMPT",
            text
          );
          return false;
        }
      }
    }
  }

  window.addEventListener("keydown", handleKeyDown, true);
  document.addEventListener("keydown", handleKeyDown, true);

  // ---------------------------------------------------------------------------
  // 7. CLIPBOARD PASTE INTERCEPTION (Instant Zero-Exfiltration Intercept)
  // ---------------------------------------------------------------------------
  function handlePaste(event) {
    try {
      const clipboardData = event.clipboardData || window.clipboardData;
      if (!clipboardData) return;

      const pastedText = clipboardData.getData("text");
      if (!pastedText || pastedText.trim().length < 5) return;

      const detected = detectSensitivePii(pastedText);

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

  window.addEventListener("paste", handlePaste, true);
  document.addEventListener("paste", handlePaste, true);

  // ---------------------------------------------------------------------------
  // 8. REAL-TIME TYPING BADGE (Debounced 350ms, Visual border warning)
  // ---------------------------------------------------------------------------
  let typingTimer = null;
  const TYPING_DEBOUNCE_MS = 350;

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
        console.warn("%c[SecureFlow DLP Typing Warning]%c", "color: #ff4d4f; font-weight: bold;", "", detected);
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
  // 9. ACTIVE FILE ATTACHMENT & DRAG-AND-DROP INTERCEPTION
  // ---------------------------------------------------------------------------
  function inspectFileObject(file, sourceElement) {
    if (!file) return;

    // Scan any document or file up to 15MB
    if (file.size <= 15 * 1024 * 1024) {
      const reader = new FileReader();
      reader.onload = function (e) {
        const text = e.target.result || "";
        const detected = detectSensitivePii(text);
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

  // Relay Kernel-Level Audit Events from network_guard.js to Port 8000 (Exempt from Page CSP)
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

  window.addEventListener(
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

  window.addEventListener(
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
  // 10. MULTI-CHANNEL SAFE DISPATCHER (Port 8000 Primary)
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
  // 11. IN-PAGE FLOATING ALERT BANNER (High Visibility & Self-Dismissing)
  // ---------------------------------------------------------------------------
  function ensureStylesInjected() {
    if (document.getElementById("sf-dlp-styles")) return;
    const styleEl = document.createElement("style");
    styleEl.id = "sf-dlp-styles";
    styleEl.textContent = `
      @keyframes sfFadeIn {
        from { opacity: 0; transform: translateY(-14px) scale(0.95); }
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
      top: 22px;
      right: 22px;
      background: #0f111a;
      color: #ffffff;
      border: 1.5px solid #ff4d4f;
      box-shadow: 0 14px 40px rgba(0,0,0,0.8), 0 0 20px rgba(255,77,79,0.35);
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
