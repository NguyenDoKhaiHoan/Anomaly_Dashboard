import { api } from "../services/api";

export function renderModelMonitorPage() {
  return `
    <div class="stack">
      <h1 class="page-title">Model Monitor</h1>
      <p class="page-subtitle">Theo dõi model đã load và trạng thái hệ thống.</p>
      <div class="grid grid-3">
        <div class="card"><div class="muted">App</div><div id="healthApp" class="metric">...</div></div>
        <div class="card"><div class="muted">Loaded models</div><div id="healthLoadedModels" class="metric">0</div></div>
        <div class="card"><div class="muted">Active sessions</div><div id="healthActiveSessions" class="metric">0</div></div>
      </div>
      <div class="card">
        <h3>Registry</h3>
        <table class="table">
          <thead><tr><th>Key</th><th>Name</th><th>Stream</th><th>Type</th><th>Artifact</th></tr></thead>
          <tbody id="modelMonitorTable"></tbody>
        </table>
      </div>
    </div>
  `;
}

export function bindModelMonitorPage() {
  Promise.all([api.get("/health"), api.get("/models")]).then(([health, models]) => {
    document.getElementById("healthApp").textContent = health?.app_name || "...";
    document.getElementById("healthLoadedModels").textContent = String(health?.loaded_models?.length || 0);
    document.getElementById("healthActiveSessions").textContent = String(health?.active_sessions || 0);
    document.getElementById("modelMonitorTable").innerHTML = models
      .map(
        (model) => `<tr>
          <td>${model.key}</td><td>${model.name}</td><td>${model.stream_type}</td><td>${model.model_type}</td><td>${model.artifact_path}</td>
        </tr>`,
      )
      .join("");
  });
}
