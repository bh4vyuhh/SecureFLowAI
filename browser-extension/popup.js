document.addEventListener("DOMContentLoaded", async () => {
  const guardToggle = document.getElementById("guardToggle");
  const gatewayInput = document.getElementById("gatewayInput");
  const saveConfigBtn = document.getElementById("saveConfigBtn");
  const clearLogsBtn = document.getElementById("clearLogsBtn");
  const eventsList = document.getElementById("eventsList");
  const statusIndicator = document.getElementById("statusIndicator");
  const statusText = document.getElementById("statusText");

  // Load saved state
  const data = await chrome.storage.local.get(["monitoringEnabled", "gatewayUrl", "recentAlerts"]);
  
  if (typeof data.monitoringEnabled !== "undefined") {
    guardToggle.checked = data.monitoringEnabled;
    updateStatus(data.monitoringEnabled);
  }

  if (data.gatewayUrl) {
    gatewayInput.value = data.gatewayUrl;
  } else {
    gatewayInput.value = "http://localhost:9090/api/v1/events/ingest";
  }

  renderEvents(data.recentAlerts || []);

  // Event handlers
  guardToggle.addEventListener("change", (e) => {
    const isEnabled = e.target.checked;
    chrome.storage.local.set({ monitoringEnabled: isEnabled });
    updateStatus(isEnabled);
  });

  saveConfigBtn.addEventListener("click", () => {
    const url = gatewayInput.value.trim();
    if (url) {
      chrome.storage.local.set({ gatewayUrl: url }, () => {
        saveConfigBtn.textContent = "Saved!";
        setTimeout(() => { saveConfigBtn.textContent = "Save"; }, 1500);
      });
    }
  });

  clearLogsBtn.addEventListener("click", () => {
    chrome.storage.local.set({ recentAlerts: [] }, () => {
      renderEvents([]);
    });
  });

  function updateStatus(enabled) {
    const dot = statusIndicator.querySelector(".status-dot");
    if (enabled) {
      dot.className = "status-dot online";
      statusText.textContent = "Active";
      statusIndicator.style.color = "#8df85f";
    } else {
      dot.className = "status-dot offline";
      statusText.textContent = "Disabled";
      statusIndicator.style.color = "#ff4d4f";
    }
  }

  function renderEvents(events) {
    if (!events || events.length === 0) {
      eventsList.innerHTML = `<div class="empty-state">No sensitive events intercepted yet.</div>`;
      return;
    }

    eventsList.innerHTML = events.slice(0, 10).map(evt => {
      const timeStr = evt.timestamp ? new Date(evt.timestamp).toLocaleTimeString() : "";
      const flagsHtml = (evt.flags || []).map(f => `<span class="tag-badge">${f}</span>`).join("");
      return `
        <div class="event-card">
          <div class="event-card-top">
            <span class="event-host">${evt.hostname || "Web Input"}</span>
            <span class="event-time">${timeStr}</span>
          </div>
          <div style="color: #8e8f96; font-size: 10px; margin-bottom: 2px;">Field: &lt;${evt.field || 'input'}&gt;</div>
          <div style="color: #636672; font-family: monospace; font-size: 10px; word-break: break-all;">${evt.contentSnippet || ""}</div>
          <div class="event-tags">${flagsHtml}</div>
        </div>
      `;
    }).join("");
  }
});
