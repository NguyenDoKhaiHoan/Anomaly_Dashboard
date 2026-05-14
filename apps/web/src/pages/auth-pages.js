import { login, register } from "../services/auth";
import { validators, validatePasswordMatch, isFormValid } from "../utils/validation";

const icons = {
  user: `<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>`,
  lock: `<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="18" height="11" x="3" y="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>`,
  mail: `<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="20" height="16" x="2" y="4" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/></svg>`,
  eye: `<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"/><circle cx="12" cy="12" r="3"/></svg>`,
  eyeOff: `<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9.88 9.88a3 3 0 1 0 4.24 4.24"/><path d="M10.73 5.08A10.43 10.43 0 0 1 12 5c7 0 10 7 10 7a13.16 13.16 0 0 1-1.67 2.68"/><path d="M6.61 6.61A13.526 13.526 0 0 0 2 12s3 7 10 7a9.74 9.74 0 0 0 5.39-1.61"/><line x1="2" x2="22" y1="2" y2="22"/></svg>`,
  shield: `<svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10"/></svg>`,
  sparkles: `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"/><path d="M5 3v4"/><path d="M19 17v4"/><path d="M3 5h4"/><path d="M17 19h4"/></svg>`,
};

export function renderLoginPage() {
  return `
    <div class="auth-page">
      <div class="auth-decoration">
        <div class="auth-decoration-blob auth-decoration-blob-1"></div>
        <div class="auth-decoration-blob auth-decoration-blob-2"></div>
        <div class="auth-decoration-blob auth-decoration-blob-3"></div>
      </div>
      
      <div class="auth-container">
        <div class="auth-visual">
          <div class="auth-visual-content">
            <div class="auth-brand">
              <div class="auth-brand-icon">${icons.shield}</div>
              <h1>Anomaly Detection</h1>
            </div>
            <p class="auth-visual-text">
              Hệ thống giám sát realtime với AI tiên tiến, phát hiện bất thường chính xác và nhanh chóng.
            </p>
            <div class="auth-features">
              <div class="auth-feature">
                <span class="auth-feature-icon">${icons.sparkles}</span>
                <span>AI Detection</span>
              </div>
              <div class="auth-feature">
                <span class="auth-feature-icon">${icons.sparkles}</span>
                <span>Real-time Alert</span>
              </div>
              <div class="auth-feature">
                <span class="auth-feature-icon">${icons.sparkles}</span>
                <span>Dashboard Analytics</span>
              </div>
            </div>
          </div>
        </div>
        
        <div class="auth-form-container">
          <div class="auth-card">
            <div class="auth-card-header">
              <h2>Chào mừng trở lại</h2>
              <p>Đăng nhập để truy cập dashboard của bạn</p>
            </div>
            
            <form id="loginForm" class="auth-form">
              <div class="form-group">
                <label class="form-label">
                  <span class="label-icon">${icons.user}</span>
                  Username
                </label>
                <div class="input-wrapper">
                  <input 
                    name="username" 
                    placeholder="Nhập username của bạn"
                    autocomplete="username"
                  />
                </div>
                <span class="field-error" data-error="username"></span>
              </div>
              
              <div class="form-group">
                <label class="form-label">
                  <span class="label-icon">${icons.lock}</span>
                  Mật khẩu
                </label>
                <div class="input-wrapper password-wrapper">
                  <input 
                    name="password" 
                    type="password" 
                    id="loginPassword"
                    placeholder="Nhập mật khẩu"
                    autocomplete="current-password"
                  />
                  <button type="button" class="password-toggle" onclick="togglePassword('loginPassword', this)">
                    ${icons.eye}
                  </button>
                </div>
                <span class="field-error" data-error="password"></span>
              </div>
              
              <div class="form-options">
                <label class="checkbox-wrapper">
                  <input type="checkbox" name="remember" />
                  <span class="checkbox-custom"></span>
                  <span>Ghi nhớ đăng nhập</span>
                </label>
                <a href="/forgot-password" class="forgot-link">Quên mật khẩu?</a>
              </div>
              
              <div id="loginError" class="auth-error" style="display:none;"></div>
              
              <button type="submit" class="btn btn-primary btn-full">
                <span>Đăng nhập</span>
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>
              </button>
            </form>
            
            <div class="auth-divider">
              <span>hoặc</span>
            </div>
            
            <p class="auth-footer-text">
              Chưa có tài khoản? <a href="/register" data-link class="auth-link">Đăng ký ngay</a>
            </p>
          </div>
        </div>
      </div>
    </div>
  `;
}

export function bindLoginPage(navigate, refreshAuth) {
  const form = document.getElementById("loginForm");
  const errorBox = document.getElementById("loginError");
  const submitBtn = form?.querySelector('button[type="submit"]');
  
  // Add toggle password function
  window.togglePassword = function(inputId, btn) {
    const input = document.getElementById(inputId);
    if (input.type === 'password') {
      input.type = 'text';
      btn.innerHTML = icons.eyeOff;
    } else {
      input.type = 'password';
      btn.innerHTML = icons.eye;
    }
  };
  
  form?.addEventListener("submit", async (event) => {
    event.preventDefault();
    errorBox.style.display = "none";
    
    if (submitBtn) {
      submitBtn.classList.add("loading");
      submitBtn.disabled = true;
    }
    
    const data = new FormData(form);
    const payload = Object.fromEntries(data.entries());

    const errors = {
      username: validators.username(payload.username),
      password: validators.password(payload.password),
    };
    Object.entries(errors).forEach(([key, value]) => {
      const slot = document.querySelector(`[data-error="${key}"]`);
      if (slot) slot.textContent = value || "";
    });
    
    const hasErrors = Object.values(errors).some(e => e);
    if (hasErrors) {
      if (submitBtn) {
        submitBtn.classList.remove("loading");
        submitBtn.disabled = false;
      }
      return;
    }

    try {
      await login(payload.username, payload.password);
      const auth = await refreshAuth();
      if (auth.blocked) {
        errorBox.textContent = auth.blockedMessage;
        errorBox.style.display = "flex";
        if (submitBtn) {
          submitBtn.classList.remove("loading");
          submitBtn.disabled = false;
        }
        return;
      }
      navigate("/dashboard/streaming");
    } catch (error) {
      errorBox.textContent = error.message || "Tên đăng nhập hoặc mật khẩu không đúng";
      errorBox.style.display = "flex";
    } finally {
      if (submitBtn) {
        submitBtn.classList.remove("loading");
        submitBtn.disabled = false;
      }
    }
  });
}

export function renderRegisterPage() {
  return `
    <div class="auth-page">
      <div class="auth-decoration">
        <div class="auth-decoration-blob auth-decoration-blob-1"></div>
        <div class="auth-decoration-blob auth-decoration-blob-2"></div>
        <div class="auth-decoration-blob auth-decoration-blob-3"></div>
      </div>
      
      <div class="auth-container">
        <div class="auth-visual">
          <div class="auth-visual-content">
            <div class="auth-brand">
              <div class="auth-brand-icon">${icons.shield}</div>
              <h1>Anomaly Detection</h1>
            </div>
            <p class="auth-visual-text">
              Tham gia cộng đồng và bắt đầu giám sát hệ thống của bạn với công nghệ AI tiên tiến nhất.
            </p>
            <div class="auth-benefits">
              <div class="auth-benefit">
                <div class="benefit-icon">${icons.sparkles}</div>
                <div class="benefit-text">
                  <strong>Lưu trữ History</strong>
                  <span>Theo dõi và phân tích dữ liệu lịch sử</span>
                </div>
              </div>
              <div class="auth-benefit">
                <div class="benefit-icon">${icons.sparkles}</div>
                <div class="benefit-text">
                  <strong>Custom Alerts</strong>
                  <span>Nhận thông báo qua Email & SMS</span>
                </div>
              </div>
              <div class="auth-benefit">
                <div class="benefit-icon">${icons.sparkles}</div>
                <div class="benefit-text">
                  <strong>Team Collaboration</strong>
                  <span>Chia sẻ dashboard với đồng nghiệp</span>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div class="auth-form-container">
          <div class="auth-card">
            <div class="auth-card-header">
              <h2>Tạo tài khoản mới</h2>
              <p>Đăng ký để bắt đầu sử dụng dịch vụ</p>
            </div>
            
            <form id="registerForm" class="auth-form">
              <div class="form-row">
                <div class="form-group">
                  <label class="form-label">
                    <span class="label-icon">${icons.user}</span>
                    Username
                  </label>
                  <div class="input-wrapper">
                    <input 
                      name="username" 
                      placeholder="Chọn username"
                      autocomplete="username"
                    />
                  </div>
                  <span class="field-error" data-error="username"></span>
                </div>
                
                <div class="form-group">
                  <label class="form-label">
                    <span class="label-icon">${icons.mail}</span>
                    Email
                  </label>
                  <div class="input-wrapper">
                    <input 
                      name="email" 
                      type="email"
                      placeholder="email@example.com"
                      autocomplete="email"
                    />
                  </div>
                  <span class="field-error" data-error="email"></span>
                </div>
              </div>
              
              <div class="form-group">
                <label class="form-label">
                  <span class="label-icon">${icons.user}</span>
                  Họ và tên
                </label>
                <div class="input-wrapper">
                  <input 
                    name="full_name" 
                    placeholder="Nhập họ và tên đầy đủ"
                    autocomplete="name"
                  />
                </div>
                <span class="field-error" data-error="full_name"></span>
              </div>
              
              <div class="form-row">
                <div class="form-group">
                  <label class="form-label">
                    <span class="label-icon">${icons.lock}</span>
                    Mật khẩu
                  </label>
                  <div class="input-wrapper password-wrapper">
                    <input 
                      name="password" 
                      type="password"
                      id="registerPassword"
                      placeholder="Tối thiểu 6 ký tự"
                      autocomplete="new-password"
                    />
                    <button type="button" class="password-toggle" onclick="togglePassword('registerPassword', this)">
                      ${icons.eye}
                    </button>
                  </div>
                  <span class="field-error" data-error="password"></span>
                </div>
                
                <div class="form-group">
                  <label class="form-label">
                    <span class="label-icon">${icons.lock}</span>
                    Xác nhận mật khẩu
                  </label>
                  <div class="input-wrapper password-wrapper">
                    <input 
                      name="password_confirm" 
                      type="password"
                      id="registerPasswordConfirm"
                      placeholder="Nhập lại mật khẩu"
                      autocomplete="new-password"
                    />
                    <button type="button" class="password-toggle" onclick="togglePassword('registerPasswordConfirm', this)">
                      ${icons.eye}
                    </button>
                  </div>
                  <span class="field-error" data-error="password_confirm"></span>
                </div>
              </div>
              
              <div class="form-terms">
                <label class="checkbox-wrapper">
                  <input type="checkbox" name="terms" required />
                  <span class="checkbox-custom"></span>
                  <span>Tôi đồng ý với <a href="/terms" class="auth-link">Điều khoản dịch vụ</a> và <a href="/privacy" class="auth-link">Chính sách bảo mật</a></span>
                </label>
              </div>
              
              <div id="registerError" class="auth-error" style="display:none;"></div>
              
              <button type="submit" class="btn btn-primary btn-full">
                <span>Tạo tài khoản</span>
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>
              </button>
            </form>
            
            <div class="auth-divider">
              <span>hoặc</span>
            </div>
            
            <p class="auth-footer-text">
              Đã có tài khoản? <a href="/login" data-link class="auth-link">Đăng nhập ngay</a>
            </p>
          </div>
        </div>
      </div>
    </div>
  `;
}

export function bindRegisterPage(navigate) {
  const form = document.getElementById("registerForm");
  const errorBox = document.getElementById("registerError");
  const submitBtn = form?.querySelector('button[type="submit"]');
  
  // Add toggle password function
  window.togglePassword = function(inputId, btn) {
    const input = document.getElementById(inputId);
    if (input.type === 'password') {
      input.type = 'text';
      btn.innerHTML = icons.eyeOff;
    } else {
      input.type = 'password';
      btn.innerHTML = icons.eye;
    }
  };
  
  form?.addEventListener("submit", async (event) => {
    event.preventDefault();
    errorBox.style.display = "none";
    
    if (submitBtn) {
      submitBtn.classList.add("loading");
      submitBtn.disabled = true;
    }

    const data = new FormData(form);
    const payload = Object.fromEntries(data.entries());

    const errors = {
      username: validators.username(payload.username),
      email: validators.email(payload.email),
      full_name: validators.fullName(payload.full_name),
      password: validators.password(payload.password),
      password_confirm: validatePasswordMatch(payload.password, payload.password_confirm),
    };
    Object.entries(errors).forEach(([key, value]) => {
      const slot = document.querySelector(`[data-error="${key}"]`);
      if (slot) slot.textContent = value || "";
    });
    
    const hasErrors = Object.values(errors).some(e => e);
    if (hasErrors) {
      if (submitBtn) {
        submitBtn.classList.remove("loading");
        submitBtn.disabled = false;
      }
      return;
    }

    try {
      await register({
        username: payload.username,
        email: payload.email,
        password: payload.password,
        full_name: payload.full_name,
      });
      navigate("/login");
    } catch (error) {
      errorBox.textContent = error.message || "Đăng ký thất bại. Vui lòng thử lại.";
      errorBox.style.display = "flex";
    } finally {
      if (submitBtn) {
        submitBtn.classList.remove("loading");
        submitBtn.disabled = false;
      }
    }
  });
}
