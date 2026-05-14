import { api } from "../services/api";
import { logout as clearToken, getAccessToken } from "../services/auth";
import { normalizeUser } from "../utils/user";

const authState = {
  user: null,
  loading: true,
  blocked: false,
  blockedMessage: "",
};

export async function refreshAuth() {
  authState.loading = true;
  const token = getAccessToken();
  if (!token) {
    authState.user = null;
    authState.loading = false;
    authState.blocked = false;
    authState.blockedMessage = "";
    return authState;
  }

  try {
    const user = await api.get("/auth/me");
    const normalizedUser = normalizeUser(user);
    if (normalizedUser && normalizedUser.is_active === false) {
      clearToken();
      authState.user = null;
      authState.blocked = true;
      authState.blockedMessage = "Tài khoản của bạn đã bị khóa. Vui lòng liên hệ quản trị viên.";
    } else {
      authState.user = normalizedUser;
      authState.blocked = false;
      authState.blockedMessage = "";
    }
  } catch {
    clearToken();
    authState.user = null;
    authState.blocked = false;
    authState.blockedMessage = "";
  } finally {
    authState.loading = false;
  }
  return authState;
}

export function getAuthState() {
  return authState;
}

export function logoutUser() {
  clearToken();
  authState.user = null;
  authState.blocked = false;
  authState.blockedMessage = "";
}
