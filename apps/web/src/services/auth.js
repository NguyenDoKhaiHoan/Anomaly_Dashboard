import { api } from "./api";

/**
 * Login user with username and password
 * @param {string} username - User username
 * @param {string} password - User password
 * @returns {Promise} - Returns token and user info
 */
export async function login(username, password) {
  try {
    const payload = await api.post("/auth/login", { username, password });
    if (!payload.access_token) {
      throw new Error("Không nhận được token từ server");
    }
    localStorage.setItem("access_token", payload.access_token);
    return payload;
  } catch (error) {
    throw new Error(error.message || "Đăng nhập thất bại");
  }
}

/**
 * Register new user
 * @param {Object} form - Registration form data
 * @param {string} form.username - Username
 * @param {string} form.email - Email
 * @param {string} form.password - Password
 * @param {string} form.full_name - Full name
 * @returns {Promise} - Returns user info
 */
export async function register(form) {
  try {
    const response = await api.post("/auth/register", {
      username: form.username,
      email: form.email,
      password: form.password,
      full_name: form.full_name,
    });
    return response;
  } catch (error) {
    throw new Error(error.message || "Đăng ký thất bại");
  }
}

/**
 * Logout - Remove token from storage
 */
export function logout() {
  localStorage.removeItem("access_token");
}

/**
 * Get stored access token
 * @returns {string|null} - Access token or null
 */
export function getAccessToken() {
  return localStorage.getItem("access_token");
}

/**
 * Check if user is logged in
 * @returns {boolean} - True if token exists
 */
export function isLoggedIn() {
  return !!getAccessToken();
}
