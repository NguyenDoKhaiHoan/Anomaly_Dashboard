/**
 * Normalize user object to ensure all fields have correct types
 * @param {Object} user - Raw user object from API
 * @returns {Object} - Normalized user object
 */
export function normalizeUser(user) {
  if (!user) return null;

  return {
    ...user,
    id: typeof user.id === "string" ? parseInt(user.id, 10) : user.id,
  };
}

/**
 * Ensure user ID is a number
 * @param {any} id - User ID
 * @returns {number} - Numeric ID
 */
export function ensureUserId(id) {
  if (typeof id === "string") {
    const parsed = parseInt(id, 10);
    return isNaN(parsed) ? 0 : parsed;
  }
  return typeof id === "number" ? id : 0;
}
