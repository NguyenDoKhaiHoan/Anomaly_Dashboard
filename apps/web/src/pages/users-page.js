import { api } from "../services/api";

export function renderUsersPage() {
  return `
    <div class="stack">
      <h1 class="page-title">Users Administration</h1>
      <p class="page-subtitle">Quản trị users, quyền admin và trạng thái kích hoạt.</p>
      <div id="usersError" class="badge danger" style="display:none;"></div>
      <div class="grid grid-4">
        <div class="card"><div class="muted">Total users</div><div id="ovTotalUsers" class="metric">0</div></div>
        <div class="card"><div class="muted">Active users</div><div id="ovActiveUsers" class="metric">0</div></div>
        <div class="card"><div class="muted">Running sessions</div><div id="ovRunningSessions" class="metric">0</div></div>
        <div class="card"><div class="muted">Notifications</div><div id="ovNotifications" class="metric">0</div></div>
      </div>
      <div class="card">
        <table class="table">
          <thead><tr><th>ID</th><th>Username</th><th>Email</th><th>Role</th><th>Status</th><th>Created</th><th>Actions</th></tr></thead>
          <tbody id="usersTableBody"></tbody>
        </table>
      </div>
    </div>
  `;
}

export function bindUsersPage() {
  const errorBox = document.getElementById("usersError");
  const body = document.getElementById("usersTableBody");

  function setError(message) {
    if (!message) {
      errorBox.style.display = "none";
      return;
    }
    errorBox.textContent = message;
    errorBox.style.display = "inline-flex";
  }

  async function load() {
    const [users, overview] = await Promise.all([api.get("/admin/users"), api.get("/admin/overview")]);
    document.getElementById("ovTotalUsers").textContent = String(overview?.total_users ?? 0);
    document.getElementById("ovActiveUsers").textContent = String(overview?.active_users ?? 0);
    document.getElementById("ovRunningSessions").textContent = String(overview?.running_sessions ?? 0);
    document.getElementById("ovNotifications").textContent = String(overview?.total_notifications ?? 0);
    body.innerHTML = users
      .map(
        (user) => `<tr>
        <td>${user.id}</td>
        <td>${user.username}</td>
        <td>${user.email}</td>
        <td><span class="badge ${user.is_superuser ? "warning" : ""}">${user.is_superuser ? "Admin" : "User"}</span></td>
        <td><span class="badge ${user.is_active ? "success" : "danger"}">${user.is_active ? "Active" : "Blocked"}</span></td>
        <td>${new Date(user.created_at).toLocaleString()}</td>
        <td>
          <button data-action="toggle-active" data-user-id="${user.id}" class="secondary">${user.is_active ? "Block" : "Unblock"}</button>
          <button data-action="toggle-admin" data-user-id="${user.id}">${user.is_superuser ? "Remove admin" : "Make admin"}</button>
        </td>
      </tr>`,
      )
      .join("");
  }

  body.addEventListener("click", async (event) => {
    const target = event.target;
    if (!(target instanceof HTMLButtonElement)) return;
    const action = target.dataset.action;
    const userId = target.dataset.userId;
    if (!action || !userId) return;
    try {
      setError("");
      if (action === "toggle-active") {
        const current = target.textContent === "Block";
        await api.patch(`/admin/users/${userId}`, { is_active: !current });
      }
      if (action === "toggle-admin") {
        const current = target.textContent === "Remove admin";
        await api.patch(`/admin/users/${userId}`, { is_superuser: !current });
      }
      await load();
    } catch (error) {
      setError(error.message || "Cập nhật user thất bại");
    }
  });

  load().catch((error) => setError(error.message || "Không tải được users"));
}
