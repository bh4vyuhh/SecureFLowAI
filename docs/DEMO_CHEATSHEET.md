# SecureFlow AI — 1-Page Live Demo Cheatsheet

### ⚡ Instant Startup
Double-click `START_DEMO.bat` in the project root.
* Automatically verifies dependencies.
* Starts FastAPI Backend (`http://127.0.0.1:8000`).
* Starts Admin SOC Console (`http://localhost:5174`).
* Automatically opens your browser to `http://localhost:5174/?demo=1`.

---

### ⏱️ 5-Act Presentation Timeline (10 Minutes)

| Time | Tab | Action | What to Say / Highlight |
| :--- | :--- | :--- | :--- |
| **0:00 - 2:00** | **Check Box (Dashboard)** | Overview of screen | "Traditional DLP leaks confidential records to third-party cloud LLMs. SecureFlow AI is a 5-layer, air-gapped banking DLP platform with an INT8 ONNX neural engine running 100% locally with sub-25ms latency." Highlight `Threat Stream: LIVE` and SQLite count. |
| **2:00 - 4:00** | **Terminal / Launcher** | In `START_DEMO.bat` console, press `[1]` | "Every endpoint streams telemetry asynchronously over our zero-overhead event bus." Watch toast alerts pop up and metrics increment live **without refreshing**. |
| **4:00 - 6:00** | **Monitoring (Live Classification)** | Page automatically loads the wire transfer payload | "Our sliding-window INT8 ONNX classifier analyzes context alongside spaCy NER." Point out `100% Risk`, `RESTRICTED` tier, `BLOCK` alert, and HMAC token masking (`[CARD_****9023]`). |
| **6:00 - 8:00** | **File Scanner** | Drag & drop `data\demo_samples\sample_banking_leak.csv` | "Multi-format binary scanner parses documents and OCR images." Shows 100% risk, `RESTRICTED` tier, `BLOCK` quarantine, and redacted CSV preview. |
| **8:00 - 10:00** | **Incidents (Audit Logs) + Support (Copilot)** | 1. Click an incident row<br>2. Open Support tab | 1. Show immutable SHA-256 hash & AES-256-GCM Detokenization Vault.<br>2. Ask Copilot: *"Summarize high-risk DLP violations today"* — show autonomous triage. |

---

### 📋 Demo Test Data Location
* **Payloads to Copy/Paste:** `data\demo_samples\DEMO_PAYLOADS.txt`
* **Files to Drag & Drop:** `data\demo_samples\sample_banking_leak.csv` and `data\demo_samples\demo_clean_contract.txt`

---

### 🆘 Emergency Troubleshooting
* **Backend not responding?** Restart via `START_DEMO.bat` or run:
  `.\.venv\Scripts\uvicorn.exe app.main:app --app-dir ai-service --host 127.0.0.1 --port 8000`
* **WebSocket disconnected?** Verify `http://127.0.0.1:8000/health` shows `HEALTHY`.
* **Port collision?** `START_DEMO.bat` automatically frees ports 8000 and 5174 before startup.
