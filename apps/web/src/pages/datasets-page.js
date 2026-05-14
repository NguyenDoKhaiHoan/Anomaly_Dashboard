import { api } from "../services/api";

export function renderDatasetsPage() {
  return `
    <div class="stack">
      <h1 class="page-title">Dataset Manager</h1>
      <p class="page-subtitle">Quản lý dataset catalog cho stream simulator.</p>
      <div id="datasetsError" class="badge danger" style="display:none;"></div>
      <div id="datasetsGrid" class="grid grid-2"></div>
    </div>
  `;
}

export function bindDatasetsPage() {
  const errorBox = document.getElementById("datasetsError");
  const grid = document.getElementById("datasetsGrid");
  api
    .get("/datasets")
    .then((datasets) => {
      grid.innerHTML = datasets
        .map(
          (dataset) => `<div class="card">
          <h3>${dataset.name}</h3>
          <p><strong>Key:</strong> ${dataset.key}</p>
          <p><strong>Stream type:</strong> ${dataset.stream_type}</p>
          <p><strong>Path:</strong> ${dataset.file_path}</p>
          <p><strong>Description:</strong> ${dataset.description || "-"}</p>
        </div>`,
        )
        .join("");
    })
    .catch((error) => {
      errorBox.textContent = error.message || "Tải dataset thất bại";
      errorBox.style.display = "inline-flex";
    });
}
