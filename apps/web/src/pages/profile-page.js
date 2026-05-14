import { api } from "../services/api";

export function renderProfilePage() {
  return `
    <div class="stack">
      <h1 class="page-title">Profile</h1>
      <p class="page-subtitle">Thông tin tài khoản đang đăng nhập.</p>
      <div id="profileError" class="badge danger" style="display:none;"></div>
      <div id="profileCard" class="card"></div>
    </div>
  `;
}

export function bindProfilePage() {
  const errorBox = document.getElementById("profileError");
  const card = document.getElementById("profileCard");
  api
    .get("/auth/me")
    .then((me) => {
      card.innerHTML = `
        <p><strong>Username:</strong> ${me?.username || "-"}</p>
        <p><strong>Email:</strong> ${me?.email || "-"}</p>
        <p><strong>Full name:</strong> ${me?.full_name || "-"}</p>
        <p><strong>Role:</strong> <span class="badge ${me?.is_superuser ? "warning" : ""}">${me?.is_superuser ? "Admin" : "User"}</span></p>
        <p><strong>Status:</strong> <span class="badge ${me?.is_active ? "success" : "danger"}">${me?.is_active ? "Active" : "Blocked"}</span></p>
      `;
    })
    .catch((error) => {
      errorBox.textContent = error.message || "Tải profile thất bại";
      errorBox.style.display = "inline-flex";
    });
}
