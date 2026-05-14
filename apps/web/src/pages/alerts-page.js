import { api } from "../services/api";

export function renderAlertsPage() {
  return `
    <div class="stack">
      <h1 class="page-title">Alerts</h1>
      <p class="page-subtitle">Tạo alert rule và xem notifications.</p>
      <div id="alertsError" class="badge danger" style="display:none;"></div>
      <div class="grid grid-2">
        <div class="card stack">
          <h3>Create alert rule</h3>
          <input id="ruleName" placeholder="Rule name" value="High score alert" />
          <select id="ruleStream"><option value="credit_card">Credit Card</option><option value="iot_sensor">IoT Sensor</option></select>
          <input id="ruleThreshold" type="number" step="0.01" value="0.5" />
          <input id="ruleConsecutive" type="number" value="1" />
          <select id="ruleChannel">
            <option value="in_app">In-App Notification</option>
            <option value="sms">SMS</option>
          </select>
          <input id="rulePhone" placeholder="Phone number (for SMS)" />
          <button id="createRuleBtn">Create rule</button>
        </div>
        <div class="card">
          <h3>Configured rules</h3>
          <table class="table">
            <thead><tr><th>Name</th><th>Stream</th><th>Threshold</th><th>Channel</th><th>Phone</th><th>Actions</th></tr></thead>
            <tbody id="rulesTableBody"></tbody>
          </table>
        </div>
      </div>
      <div class="card">
        <h3>Recent notifications</h3>
        <div class="filter-row" style="margin-bottom: 16px;">
          <div class="filter-group">
            <label>Lọc theo thời gian</label>
            <select id="notificationPeriod">
              <option value="all">Tất cả</option>
              <option value="today">Hôm nay</option>
              <option value="week">Tuần này</option>
              <option value="month">Tháng này</option>
              <option value="year">Năm nay</option>
            </select>
          </div>
          <button id="refreshNotifications" class="btn-secondary">Làm mới</button>
        </div>
        <div id="notificationsWrap" class="stack"></div>
      </div>
    </div>
  `;
}

export function bindAlertsPage() {
  const errorBox = document.getElementById("alertsError");
  const rulesBody = document.getElementById("rulesTableBody");
  const notificationsWrap = document.getElementById("notificationsWrap");

  function setError(message) {
    if (!message) {
      errorBox.style.display = "none";
      return;
    }
    errorBox.textContent = message;
    errorBox.style.display = "inline-flex";
  }

  async function loadData() {
    const period = document.getElementById("notificationPeriod")?.value || "all";
    const [rules, notifications] = await Promise.all([
      api.get("/alerts/rules"),
      api.get(`/alerts/notifications?period=${period}`),
    ]);
    rulesBody.innerHTML = rules.length
      ? rules
          .map(
            (rule) => `<tr>
      <td>${rule.name}</td>
      <td>${rule.stream_type || "all"}</td>
      <td>${rule.score_threshold}</td>
      <td><span class="badge ${rule.channel === 'sms' ? 'warning' : rule.channel === 'fcm' ? 'primary' : 'success'}">${rule.channel}</span></td>
      <td>${rule.fcm_token ? rule.fcm_token.substring(0, 20) + '...' : rule.phone_number || "-"}</td>
      <td><button class="btn-detail danger" onclick="deleteRule(${rule.id})">Xóa</button></td>
    </tr>`,
          )
          .join("")
      : `<tr><td colspan="6" class="muted">Chưa có rule nào.</td></tr>`;
    
    notificationsWrap.innerHTML = notifications.length
      ? notifications
          .map(
            (item) => `<div class="card" style="padding:12px;" id="notif-${item.id}">
          <div class="flex justify-between align-center">
            <strong>${item.title}</strong>
            <div class="flex gap-8">
              <span class="badge ${item.is_read ? "success" : "danger"}">${item.is_read ? "Đã đọc" : "Chưa đọc"}</span>
              <button class="btn-detail" onclick="markRead(${item.id})">Đánh dấu đã đọc</button>
              <button class="btn-detail danger" onclick="deleteNotification(${item.id})">Xóa</button>
            </div>
          </div>
          <div class="muted" style="margin-top:6px;">${item.message}</div>
        </div>`,
          )
          .join("")
      : `<div class="muted">Chưa có thông báo.</div>`;
  }

  async function loadNotifications() {
    const period = document.getElementById("notificationPeriod")?.value || "all";
    try {
      const notifications = await api.get(`/alerts/notifications?period=${period}`);
      notificationsWrap.innerHTML = notifications.length
        ? notifications
            .map(
              (item) => `<div class="card" style="padding:12px;" id="notif-${item.id}">
            <div class="flex justify-between align-center">
              <strong>${item.title}</strong>
              <div class="flex gap-8">
                <span class="badge ${item.is_read ? "success" : "danger"}">${item.is_read ? "Đã đọc" : "Chưa đọc"}</span>
                <button class="btn-detail" onclick="markRead(${item.id})">Đánh dấu đã đọc</button>
                <button class="btn-detail danger" onclick="deleteNotification(${item.id})">Xóa</button>
              </div>
            </div>
            <div class="muted" style="margin-top:6px;">${item.message}</div>
          </div>`,
            )
            .join("")
        : `<div class="muted">Không có thông báo trong khoảng thời gian này.</div>`;
    } catch (error) {
      setError(error.message || "Không tải được notifications");
    }
  }

  window.deleteRule = async function(ruleId) {
    if (!confirm("Bạn có chắc muốn xóa rule này?")) return;
    try {
      await api.del(`/alerts/rules/${ruleId}`);
      await loadData();
    } catch (error) {
      setError(error.message || "Xóa rule thất bại");
    }
  };

  window.deleteNotification = async function(notifId) {
    try {
      await api.del(`/alerts/notifications/${notifId}`);
      const el = document.getElementById(`notif-${notifId}`);
      if (el) el.remove();
    } catch (error) {
      setError(error.message || "Xóa notification thất bại");
    }
  };

  window.markRead = async function(notifId) {
    try {
      await api.post(`/alerts/notifications/${notifId}/read`);
      const el = document.getElementById(`notif-${notifId}`);
      if (el) {
        const badge = el.querySelector(".badge");
        if (badge) {
          badge.className = "badge success";
          badge.textContent = "Đã đọc";
        }
      }
    } catch (error) {
      setError(error.message || "Cập nhật thất bại");
    }
  };

  document.getElementById("createRuleBtn")?.addEventListener("click", async () => {
    try {
      setError("");
      const channel = document.getElementById("ruleChannel").value;
      const phoneNumber = document.getElementById("rulePhone").value;

      await api.post("/alerts/rules", {
        name: document.getElementById("ruleName").value,
        stream_type: document.getElementById("ruleStream").value,
        score_threshold: Number(document.getElementById("ruleThreshold").value),
        consecutive_count: Number(document.getElementById("ruleConsecutive").value),
        channel: channel,
        phone_number: channel === "sms" ? phoneNumber : null,
      });
      await loadData();
    } catch (error) {
      setError(error.message || "Tạo rule thất bại");
    }
  });

  document.getElementById("refreshNotifications")?.addEventListener("click", loadNotifications);
  document.getElementById("notificationPeriod")?.addEventListener("change", loadNotifications);

  loadData().catch((error) => setError(error.message || "Không tải được alerts"));
}
