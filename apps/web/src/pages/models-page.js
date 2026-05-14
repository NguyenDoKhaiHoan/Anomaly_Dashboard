import { api } from "../services/api";

export function renderModelsPage() {
  return `
    <div class="stack">
      <h1 class="page-title">Model Registry</h1>
      <p class="page-subtitle">Danh sách model backend đang load.</p>
      <div id="modelsError" class="badge danger" style="display:none;"></div>
      <div id="modelsGrid" class="grid grid-2"></div>
    </div>
  `;
}

export function bindModelsPage() {
  const errorBox = document.getElementById("modelsError");
  const grid = document.getElementById("modelsGrid");
  api
    .get("/models")
    .then((models) => {
      grid.innerHTML = models
        .map(
          (model) => `<div class="card">
          <h3>${model.name}</h3>
          <p><strong>Key:</strong> ${model.key}</p>
          <p><strong>Stream type:</strong> ${model.stream_type}</p>
          <p><strong>Status:</strong> <span class="badge ${model.is_active ? "success" : "danger"}">${model.is_active ? "Active" : "Inactive"}</span></p>
          <p><strong>Description:</strong> ${model.description || "-"}</p>
        </div>`,
        )
        .join("");
    })
    .catch((error) => {
      errorBox.textContent = error.message || "Tải models thất bại";
      errorBox.style.display = "inline-flex";
    });
}
