import { logoutUser, getAuthState } from "../state/auth-state";

const menu = [
  ["/dashboard/streaming", "Streaming", "🎬"],
  ["/dashboard/history", "History", "📈"],
  ["/dashboard/alerts", "Alerts", "🔔"],
  ["/dashboard/models", "Model Monitor", "🤖"],
  ["/admin/datasets", "Dataset Manager", "🗂️"],
  ["/admin/models", "Model Registry", "🧠"],
  ["/admin/users", "Users", "👥"],
  ["/profile", "Profile", "⚙️"],
];

function navLink(path, label, icon, currentPath) {
  const active = currentPath === path ? "active" : "";
  return `<a href="${path}" data-link class="nav-link ${active}"><span class="nav-link-icon">${icon}</span><span>${label}</span></a>`;
}

export function renderShell(contentHtml, currentPath) {
  const { user } = getAuthState();
  const isAdmin = Boolean(user?.is_superuser);
  return `
    <div class="layout">
      <aside class="sidebar">
        <div class="brand">Anomaly Detection</div>
        ${
          user
            ? `<div class="card user-mini-card">
                <div class="muted" style="font-size: 0.8rem;">Đang đăng nhập</div>
                <strong>${user.username}</strong>
              </div>`
            : ""
        }
        <nav style="flex:1">
          <div class="menu-group-label">Dashboard</div>
          ${menu.slice(0, 4).map(([p, l, i]) => navLink(p, l, i, currentPath)).join("")}
          ${
            isAdmin
              ? `<div class="menu-group-label">Admin</div>
                 ${menu.slice(4, 7).map(([p, l, i]) => navLink(p, l, i, currentPath)).join("")}`
              : ""
          }
          <div class="menu-group-label">Tài khoản</div>
          ${menu.slice(7).map(([p, l, i]) => navLink(p, l, i, currentPath)).join("")}
        </nav>
        <button id="logoutBtn" class="secondary" style="width:100%; margin-top:16px;">Đăng xuất</button>
      </aside>
      <main class="main">${contentHtml}</main>
    </div>
  `;
}

export function bindShellEvents(navigate) {
  const btn = document.getElementById("logoutBtn");
  if (!btn) return;
  btn.addEventListener("click", () => {
    logoutUser();
    navigate("/login");
  });
}
