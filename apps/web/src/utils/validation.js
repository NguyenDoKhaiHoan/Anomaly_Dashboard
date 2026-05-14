/**
 * Validation utilities for forms
 */

export const validators = {
  username: (value) => {
    if (!value) return "Username không được để trống";
    if (value.length < 3) return "Username phải ít nhất 3 ký tự";
    if (value.length > 80) return "Username không được vượt 80 ký tự";
    if (!/^[a-zA-Z0-9_-]+$/.test(value))
      return "Username chỉ được chứa chữ, số, _, -";
    return "";
  },

  email: (value) => {
    if (!value) return "Email không được để trống";
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(value)) return "Email không hợp lệ";
    return "";
  },

  password: (value, minLength = 6) => {
    if (!value) return "Mật khẩu không được để trống";
    if (value.length < minLength)
      return `Mật khẩu phải ít nhất ${minLength} ký tự`;
    if (value.length > 128) return "Mật khẩu không được vượt 128 ký tự";
    return "";
  },

  passwordMatch: (password, confirm) => {
    if (password !== confirm) return "Mật khẩu xác nhận không khớp";
    return "";
  },

  fullName: (value) => {
    if (!value) return "Họ tên không được để trống";
    if (value.length < 2) return "Họ tên phải ít nhất 2 ký tự";
    if (value.length > 80) return "Họ tên không được vượt 80 ký tự";
    return "";
  },
};

/**
 * Validate all form fields
 */
export function validateForm(form, fields) {
  const errors = {};
  fields.forEach((field) => {
    const validator = validators[field];
    if (validator) {
      const error = validator(form[field]);
      if (error) errors[field] = error;
    }
  });
  return errors;
}

/**
 * Validate password match
 */
export function validatePasswordMatch(password, confirm) {
  return validators.passwordMatch(password, confirm);
}

/**
 * Check if all form values are filled
 */
export function isFormValid(errors) {
  return Object.keys(errors).length === 0;
}
