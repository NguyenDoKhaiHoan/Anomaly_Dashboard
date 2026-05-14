import { api, API_BASE } from "../services/api";
import { drawLineChart } from "../lib/charts";

function badgeClass(ok) {
  return ok ? "success" : "danger";
}

function renderEventRows(events) {
  if (!events.length) return `<tr><td colspan="5" class="muted">Chưa có sự kiện.</td></tr>`;
  return events
    .slice()
    .reverse()
    .map(
      (event) => `<tr>
      <td>${event.time}</td>
      <td>${Number(event.anomaly_score ?? 0).toFixed(4)}</td>
      <td><span class="badge ${badgeClass(!event.is_anomaly)}">${event.is_anomaly ? "Anomaly" : "Normal"}</span></td>
      <td>${(event.reasons || []).join(", ") || "-"}</td>
      <td><pre class="code">${JSON.stringify(event.raw_payload ?? event.raw_event ?? {}, null, 2)}</pre></td>
    </tr>`,
    )
    .join("");
}

export function renderStreamingPage() {
  return `
    <div class="stack">
      <h1 class="page-title">Streaming Dashboard</h1>
      <p class="page-subtitle">Dashboard stream realtime.</p>
      <div id="streamError" class="badge danger" style="display:none;"></div>
      <div class="card stack">
        <h3>Tạo hoặc điều khiển session</h3>
        <div class="grid grid-2">
          <div class="input-group"><label>Stream type</label><select id="streamType"><option value="credit_card">Credit Card</option><option value="iot_sensor">IoT Sensor</option></select></div>
          <div class="input-group"><label>Model</label><select id="modelKey"></select></div>
          <div class="input-group"><label>Dataset</label><select id="datasetKey"></select></div>
          <div class="input-group"><label>Interval (seconds)</label><input id="streamInterval" type="number" value="1" step="0.1" /></div>
          <div class="input-group"><label>Threshold override</label><input id="thresholdOverride" type="number" step="0.01" /></div>
        </div>
        <div id="currentParams" class="badge" style="display:none; margin-bottom: 8px;"></div>
        <div class="flex">
          <button id="createSessionBtn">Tạo session</button>
          <button id="resetFormBtn" class="secondary">Reset</button>
          <button id="startSessionBtn">Start</button>
          <button id="stopSessionBtn" class="secondary">Stop</button>
          <button id="updateSessionBtn" class="secondary">Update Params</button>
        </div>
      </div>
      <div class="grid grid-3">
        <div class="card"><div class="muted">Total events</div><div id="metricEvents" class="metric">0</div></div>
        <div class="card"><div class="muted">Total anomalies</div><div id="metricAnomalies" class="metric">0</div></div>
        <div class="card"><div class="muted">Anomaly rate</div><div id="metricRate" class="metric">0.00%</div></div>
      </div>
      <div class="grid grid-2">
        <div class="card"><h3>Anomaly score stream</h3><canvas id="scoreChart" width="700" height="280"></canvas></div>
        <div class="card"><h3>Detector latency (ms)</h3><canvas id="latencyChart" width="700" height="280"></canvas></div>
      </div>
      <div class="card">
        <h3>Recent events</h3>
        <table class="table"><thead><tr><th>Time</th><th>Score</th><th>Status</th><th>Reasons</th><th>Raw payload</th></tr></thead><tbody id="eventsTableBody"></tbody></table>
      </div>
    </div>
  `;
}

export function bindStreamingPage() {
  const state = {
    models: [],
    datasets: [],
    sessions: [],
    activeSession: null,
    events: [],
    runtime: null,
    eventSource: null,
  };

  const elements = {
    error: document.getElementById("streamError"),
    streamType: document.getElementById("streamType"),
    modelKey: document.getElementById("modelKey"),
    datasetKey: document.getElementById("datasetKey"),
    streamInterval: document.getElementById("streamInterval"),
    thresholdOverride: document.getElementById("thresholdOverride"),
    createBtn: document.getElementById("createSessionBtn"),
    resetBtn: document.getElementById("resetFormBtn"),
    startBtn: document.getElementById("startSessionBtn"),
    stopBtn: document.getElementById("stopSessionBtn"),
    updateBtn: document.getElementById("updateSessionBtn"),
    currentParams: document.getElementById("currentParams"),
    metricEvents: document.getElementById("metricEvents"),
    metricAnomalies: document.getElementById("metricAnomalies"),
    metricRate: document.getElementById("metricRate"),
    eventsBody: document.getElementById("eventsTableBody"),
    scoreChart: document.getElementById("scoreChart"),
    latencyChart: document.getElementById("latencyChart"),
  };

  function setError(message) {
    if (!message) {
      elements.error.style.display = "none";
      return;
    }
    elements.error.textContent = message;
    elements.error.style.display = "inline-flex";
  }

  function closeRealtime() {
    state.eventSource?.close?.();
    state.eventSource = null;
  }

  function updateParamsDisplay() {
    const session = state.activeSession;
    if (!session || !session.stream_interval) {
      elements.currentParams.style.display = "none";
      return;
    }
    const interval = session.stream_interval;
    const threshold = session.threshold_override ?? "default";
    const isRunning = session.status === "running";
    elements.currentParams.textContent = `${isRunning ? "Đang chạy" : "Session mới"}: interval=${interval}s | threshold=${threshold}`;
    elements.currentParams.style.display = "inline-block";
  }

  function refreshMetrics() {
    const totalEvents = state.runtime?.total_events ?? 0;
    const totalAnomalies = state.runtime?.total_anomalies ?? 0;
    const anomalyRate = totalEvents ? ((totalAnomalies / totalEvents) * 100).toFixed(2) : "0.00";
    elements.metricEvents.textContent = String(totalEvents);
    elements.metricAnomalies.textContent = String(totalAnomalies);
    elements.metricRate.textContent = `${anomalyRate}%`;
    elements.eventsBody.innerHTML = renderEventRows(state.events);
    drawLineChart(elements.scoreChart, state.events, "anomaly_score");
    drawLineChart(elements.latencyChart, state.events, "detector_latency_ms");
  }

  function filterByType(rows, streamType) {
    return rows.filter((item) => item.stream_type === streamType);
  }

  function refreshSelects() {
    const streamType = elements.streamType.value;
    const currentDataset = elements.datasetKey.value; // Keep current selection
    const filteredModels = filterByType(state.models, streamType);
    const filteredDatasets = filterByType(state.datasets, streamType);
    elements.modelKey.innerHTML = filteredModels
      .map((item) => `<option value="${item.key}">${item.name}</option>`)
      .join("");
    elements.datasetKey.innerHTML = ['<option value="">Không chọn</option>']
      .concat(filteredDatasets.map((item) => `<option value="${item.key}">${item.name}</option>`))
      .join("");
    // Restore selection if still valid and auto-fill threshold
    if (currentDataset && filteredDatasets.some(d => d.key === currentDataset)) {
      elements.datasetKey.value = currentDataset;
      autoFillThreshold();
    }
  }

  function autoFillThreshold() {
    const modelKey = elements.modelKey.value;
    // For fraud_statistical model, use hardcoded threshold 14.27 (from optimized metadata.json)
    if (modelKey === "fraud_statistical") {
      elements.thresholdOverride.value = 14.27;
      return;
    }
    // For other models, use model's threshold from backend
    const currentModel = state.models.find(m => m.key === modelKey);
    elements.thresholdOverride.value = currentModel?.threshold ?? "";
  }

  function buildPayload() {
    return {
      stream_type: elements.streamType.value,
      model_key: elements.modelKey.value,
      dataset_key: elements.datasetKey.value || null,
      asset_symbol: null,
      stream_interval: Number(elements.streamInterval.value || 1),
      threshold_override: elements.thresholdOverride.value ? Number(elements.thresholdOverride.value) : null,
    };
  }

  function attachRealtime(sessionId) {
    closeRealtime();
    const token = localStorage.getItem("access_token");
    state.eventSource = new EventSource(`${API_BASE}/streams/sessions/${sessionId}/events?token=${token}`);
    state.eventSource.onmessage = (event) => {
      const payload = JSON.parse(event.data);
      state.events = [
        ...state.events.slice(-59),
        {
          ...payload,
          time: payload.timestamp ? new Date(payload.timestamp).toLocaleTimeString() : new Date().toLocaleTimeString(),
        },
      ];
      if (payload.summary) state.runtime = payload.summary;
      refreshMetrics();
    };
  }

  async function hydrateRunningSession(sessionId) {
    const runtimeData = await api.get(`/streams/sessions/${sessionId}/runtime`);
    state.runtime = runtimeData;
    attachRealtime(sessionId);
    refreshMetrics();
  }

  async function loadCatalog() {
    const [modelRows, datasetRows, sessionRows] = await Promise.all([
      api.get("/models"),
      api.get("/datasets"),
      api.get("/streams/sessions"),
    ]);
    state.models = modelRows;
    state.datasets = datasetRows;
    state.sessions = sessionRows;
    state.activeSession = sessionRows.find((item) => item.status === "running") || sessionRows[0] || null;
    refreshSelects();
    syncFormWithSession();
    updateParamsDisplay();
    if (state.activeSession?.status === "running") await hydrateRunningSession(state.activeSession.id);
  }

  function syncFormWithSession() {
    const session = state.activeSession;
    if (!session) return;
    elements.streamType.value = session.stream_type || "credit_card";
    elements.modelKey.value = session.model_key || "";
    elements.datasetKey.value = session.dataset_key || "";
    elements.streamInterval.value = session.stream_interval || 1;
    // Use session's threshold_override if set, otherwise auto-fill from model
    if (session.threshold_override !== null && session.threshold_override !== undefined) {
      elements.thresholdOverride.value = session.threshold_override;
    } else {
      autoFillThreshold();
    }
    refreshSelects(); // Refresh dropdowns after changing stream type
  }

  elements.streamType.addEventListener("change", refreshSelects);
  
  elements.modelKey.addEventListener("change", () => {
    autoFillThreshold();
  });
  
  elements.datasetKey.addEventListener("change", () => {
    autoFillThreshold();
  });
  
  elements.resetBtn.addEventListener("click", () => {
    const currentModel = state.models.find(m => m.key === elements.modelKey.value);
    const defaultThreshold = currentModel?.threshold ?? "";
    elements.streamInterval.value = "1";
    elements.thresholdOverride.value = defaultThreshold;
    elements.datasetKey.value = "";
    // Update display to show default config
    state.activeSession = { ...state.activeSession, stream_interval: 1, threshold_override: defaultThreshold || null, dataset_key: null };
    updateParamsDisplay();
  });
  elements.createBtn.addEventListener("click", async () => {
    try {
      setError("");
      console.log("Creating session with payload:", buildPayload());
      const result = await api.post("/streams/sessions", buildPayload());
      console.log("Session created:", result);
      state.events = [];
      state.runtime = null;
      refreshMetrics();
      await loadCatalog();
      refreshSelects();
      updateParamsDisplay();
    } catch (error) {
      console.error("Create session error:", error);
      setError(error.message || "Tạo session thất bại");
    }
  });
  elements.startBtn.addEventListener("click", async () => {
    if (!state.activeSession) return;
    try {
      setError("");
      await api.post(`/streams/sessions/${state.activeSession.id}/start`, {});
      state.events = [];
      await hydrateRunningSession(state.activeSession.id);
      await loadCatalog();
      updateParamsDisplay();
    } catch (error) {
      setError(error.message || "Khởi động session thất bại");
    }
  });
  elements.stopBtn.addEventListener("click", async () => {
    if (!state.activeSession) return;
    try {
      setError("");
      await api.post(`/streams/sessions/${state.activeSession.id}/stop`, {});
      closeRealtime();
      await loadCatalog();
    } catch (error) {
      setError(error.message || "Dừng session thất bại");
    }
  });
  elements.updateBtn.addEventListener("click", async () => {
    if (!state.activeSession) return;
    try {
      setError("");
      await api.patch(`/streams/sessions/${state.activeSession.id}`, buildPayload());
      // Update local state
      state.activeSession.stream_interval = Number(elements.streamInterval.value || 1);
      state.activeSession.threshold_override = elements.thresholdOverride.value ? Number(elements.thresholdOverride.value) : null;
      // Show success notification
      updateParamsDisplay();
      const prevText = elements.updateBtn.textContent;
      elements.updateBtn.textContent = "✓ Updated!";
      elements.updateBtn.style.background = "#22c55e";
      setTimeout(() => {
        elements.updateBtn.textContent = prevText;
        elements.updateBtn.style.background = "";
      }, 1500);
    } catch (error) {
      setError(error.message || "Cập nhật thất bại");
    }
  });

  // Update params display when session is loaded
  loadCatalog().then(() => updateParamsDisplay()).catch((error) => setError(error.message || "Không tải được catalog"));
  refreshMetrics();

  return () => closeRealtime();
}
