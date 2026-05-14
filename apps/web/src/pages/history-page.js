import { api } from "../services/api";

export function renderHistoryPage() {
  return `
    <div class="stack">
      <h1 class="page-title">History</h1>
      <p class="page-subtitle">Lịch sử anomaly của người dùng theo từng session. Click vào dòng để xem chi tiết.</p>
      <div id="historyError" class="badge danger" style="display:none;"></div>
      
      <!-- Filter controls -->
      <div class="card history-filters">
        <div class="filter-row">
          <div class="filter-group">
            <label>Lọc theo thời gian</label>
            <select id="filterPeriod">
              <option value="all">Tất cả</option>
              <option value="today">Hôm nay</option>
              <option value="week">Tuần này</option>
              <option value="month">Tháng này</option>
              <option value="year">Năm nay</option>
            </select>
          </div>
          <div class="filter-group">
            <label>Lọc theo Stream</label>
            <select id="filterStream">
              <option value="">Tất cả</option>
              <option value="credit_card">Credit Card</option>
              <option value="iot_sensor">IoT Sensor</option>
            </select>
          </div>
          <div class="filter-group">
            <label>Lọc theo Status</label>
            <select id="filterStatus">
              <option value="">Tất cả</option>
              <option value="anomaly">Anomaly</option>
              <option value="normal">Normal</option>
            </select>
          </div>
          <div class="filter-group">
            <label>Hiển thị</label>
            <select id="filterLimit">
              <option value="50">50 dòng</option>
              <option value="100">100 dòng</option>
              <option value="200">200 dòng</option>
            </select>
          </div>
          <button id="applyFilterBtn" class="btn btn-secondary">Áp dụng</button>
          <button id="exportCsvBtn" class="btn btn-primary">Export CSV</button>
        </div>
      </div>
      
      <div class="card">
        <div class="history-stats">
          <span id="historyTotal" class="muted">Total records: 0</span>
          <span id="historyAnomalyCount" class="badge danger">Anomaly: 0</span>
          <span id="historyNormalCount" class="badge success">Normal: 0</span>
        </div>
        <table class="table history-table">
          <thead>
            <tr>
              <th>Time</th>
              <th>Session</th>
              <th>Stream</th>
              <th>Model</th>
              <th>Score</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody id="historyTableBody"></tbody>
        </table>
      </div>
    </div>
    
    <!-- Detail Modal -->
    <div id="detailModal" class="modal-overlay" style="display:none;">
      <div class="modal-content">
        <div class="modal-header">
          <h3 id="modalTitle">Event Details</h3>
          <button id="closeModalBtn" class="modal-close">&times;</button>
        </div>
        <div class="modal-body" id="modalBody">
        </div>
      </div>
    </div>
  `;
}

function formatTime(timestamp) {
  try {
    if (!timestamp) return "-";
    const date = new Date(timestamp);
    if (isNaN(date.getTime())) return "-";
    return date.toLocaleString('vi-VN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: false
    });
  } catch (e) {
    return "-";
  }
}

function showDetailModal(item) {
  const modal = document.getElementById("detailModal");
  const modalTitle = document.getElementById("modalTitle");
  const modalBody = document.getElementById("modalBody");
  
  const statusClass = item.is_anomaly ? "danger" : "success";
  const statusText = item.is_anomaly ? "Anomaly" : "Normal";
  
  modalTitle.innerHTML = `
    <span class="badge ${statusClass}">${statusText}</span>
    Event Details
  `;
  
  modalBody.innerHTML = `
    <div class="detail-section">
      <h4>Thông tin chung</h4>
      <div class="detail-grid">
        <div class="detail-item">
          <span class="detail-label">Session ID</span>
          <span class="detail-value">${item.session_id || "-"}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">Stream Type</span>
          <span class="detail-value">${item.stream_type || "-"}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">Model Key</span>
          <span class="detail-value">${item.model_key || "-"}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">Thời gian</span>
          <span class="detail-value">${formatTime(item.event_timestamp)}</span>
        </div>
      </div>
    </div>
    
    <div class="detail-section">
      <h4>Kết quả phân tích</h4>
      <div class="detail-grid">
        <div class="detail-item highlight">
          <span class="detail-label">Anomaly Score</span>
          <span class="detail-value score-value ${item.is_anomaly ? 'anomaly' : 'normal'}">${Number(item.anomaly_score ?? 0).toFixed(6)}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">Trạng thái</span>
          ${item.anomaly_score === 0 
            ? '<span class="badge warning">Warming up - Chưa đủ dữ liệu</span>' 
            : `<span class="badge ${statusClass}">${statusText}</span>`}
        </div>
        <div class="detail-item">
          <span class="detail-label">Detector Latency</span>
          <span class="detail-value">${item.detector_latency_ms ? item.detector_latency_ms.toFixed(2) + " ms" : "-"}</span>
        </div>
      </div>
    </div>
    
    ${item.reasons && item.reasons.length > 0 ? `
    <div class="detail-section">
      <h4>Lý do phát hiện Anomaly</h4>
      <ul class="reasons-list">
        ${item.reasons.map(r => `<li class="reason-item">${r}</li>`).join('')}
      </ul>
    </div>
    ` : ''}
    
    ${item.feature_payload && Object.keys(item.feature_payload).length > 0 ? `
    <div class="detail-section">
      <h4>Feature Payload</h4>
      <div class="json-viewer">
        <pre>${JSON.stringify(item.feature_payload, null, 2)}</pre>
      </div>
    </div>
    ` : ''}
    
    ${item.raw_payload && Object.keys(item.raw_payload).length > 0 ? `
    <div class="detail-section">
      <h4>Raw Payload</h4>
      <div class="json-viewer">
        <pre>${JSON.stringify(item.raw_payload, null, 2)}</pre>
      </div>
    </div>
    ` : ''}
  `;
  
  modal.style.display = "flex";
}

function hideDetailModal() {
  const modal = document.getElementById("detailModal");
  modal.style.display = "none";
}

export function bindHistoryPage() {
  const errorBox = document.getElementById("historyError");
  const total = document.getElementById("historyTotal");
  const anomalyCount = document.getElementById("historyAnomalyCount");
  const normalCount = document.getElementById("historyNormalCount");
  const tableBody = document.getElementById("historyTableBody");
  const modal = document.getElementById("detailModal");
  const closeModalBtn = document.getElementById("closeModalBtn");
  const applyFilterBtn = document.getElementById("applyFilterBtn");
  const exportCsvBtn = document.getElementById("exportCsvBtn");
  const filterStream = document.getElementById("filterStream");
  const filterStatus = document.getElementById("filterStatus");
  const filterLimit = document.getElementById("filterLimit");
  const filterPeriod = document.getElementById("filterPeriod");
  
  let allData = [];
  
  // Modal close events
  closeModalBtn?.addEventListener("click", hideDetailModal);
  modal?.addEventListener("click", (e) => {
    if (e.target === modal) hideDetailModal();
  });
  
  function renderTable(data) {
    if (!data.length) {
      tableBody.innerHTML = `<tr><td colspan="7" class="muted" style="text-align:center;">Chưa có dữ liệu</td></tr>`;
      return;
    }
    
    // Count stats
    const anomalies = data.filter(d => d.is_anomaly).length;
    const normals = data.filter(d => !d.is_anomaly).length;
    
    total.textContent = `Total records: ${data.length}`;
    anomalyCount.textContent = `Anomaly: ${anomalies}`;
    normalCount.textContent = `Normal: ${normals}`;
    
    tableBody.innerHTML = data
      .map((item) => `
        <tr class="history-row" data-id="${item.id}">
          <td class="time-cell">${formatTime(item.event_timestamp)}</td>
          <td class="session-cell">${item.session_id || "-"}</td>
          <td>
            <span class="stream-badge ${item.stream_type}">${item.stream_type === 'credit_card' ? '💳' : '📡'} ${item.stream_type || "-"}</span>
          </td>
          <td class="model-cell">${item.model_key || "-"}</td>
          <td class="score-cell ${item.is_anomaly ? 'anomaly-score' : 'normal-score'}" 
              title="${item.anomaly_score === 0 ? 'Đang khởi tạo - chưa đủ dữ liệu để so sánh' : ''}">
            ${Number(item.anomaly_score ?? 0).toFixed(4)}
          </td>
          <td>
            ${item.anomaly_score === 0 
              ? '<span class="badge warning">Warming up</span>' 
              : `<span class="badge ${item.is_anomaly ? "danger" : "success"}">${item.is_anomaly ? "Anomaly" : "Normal"}</span>`}
          </td>
          <td>
            <button class="btn-detail" data-item='${JSON.stringify(item).replace(/'/g, "&#39;")}'>
              👁️ Chi tiết
            </button>
          </td>
        </tr>
      `)
      .join("");
      
    // Add click handlers for detail buttons
    tableBody.querySelectorAll('.btn-detail').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        try {
          const item = JSON.parse(btn.dataset.item);
          showDetailModal(item);
        } catch (err) {
          console.error('Error parsing item:', err);
        }
      });
    });
    
    // Add click handlers for rows
    tableBody.querySelectorAll('.history-row').forEach(row => {
      row.addEventListener('click', () => {
        const id = row.dataset.id;
        const item = allData.find(d => d.id == id);
        if (item) showDetailModal(item);
      });
    });
  }
  
  async function loadData() {
    const streamType = document.getElementById("filterStream")?.value || "";
    const statusFilter = document.getElementById("filterStatus")?.value || "";
    const limit = document.getElementById("filterLimit")?.value || "50";
    const period = document.getElementById("filterPeriod")?.value || "all";
    
    try {
      errorBox.style.display = "none";
      const params = new URLSearchParams();
      params.append("limit", limit);
      if (streamType) params.append("stream_type", streamType);
      params.append("period", period);
      
      console.log("Loading history with params:", params.toString());
      const response = await api.get(`/history/events?${params.toString()}`);
      allData = response.items || [];
      
      // Apply status filter locally
      let filtered = [...allData];
      if (statusFilter === "anomaly") {
        filtered = filtered.filter(item => item.is_anomaly === true);
      } else if (statusFilter === "normal") {
        filtered = filtered.filter(item => item.is_anomaly === false);
      }
      
      renderTable(filtered);
    } catch (error) {
      console.error("Load history error:", error);
      errorBox.textContent = error.message || "Tải history thất bại: " + JSON.stringify(error);
      errorBox.style.display = "inline-flex";
    }
  }
  
  applyFilterBtn?.addEventListener("click", loadData);
  
  exportCsvBtn?.addEventListener("click", async () => {
    const streamType = document.getElementById("filterStream")?.value || "";
    const period = document.getElementById("filterPeriod")?.value || "all";
    const params = new URLSearchParams();
    if (streamType) params.append("stream_type", streamType);
    params.append("period", period);
    
    const timestamp = new Date().toISOString().replace(/[:.]/g, "-").slice(0, 19);
    const filename = `anomaly_events_${period}_${timestamp}.csv`;
    
    try {
      exportCsvBtn.disabled = true;
      exportCsvBtn.textContent = "Dang tai...";
      await api.download(`/history/events/export?${params.toString()}`, filename);
    } catch (error) {
      errorBox.textContent = "Export CSV that bai: " + (error.message || "");
      errorBox.style.display = "inline-flex";
    } finally {
      exportCsvBtn.disabled = false;
      exportCsvBtn.textContent = "Export CSV";
    }
  });
  
  // Initial load
  loadData();
}
