const PASSWORD_RESET_EMAIL_KEY = "onda.passwordResetEmail";

function sessionStorageOrNull() {
  try {
    return globalThis.sessionStorage ?? null;
  } catch {
    return null;
  }
}

export function readPasswordResetEmail(storage = sessionStorageOrNull()) {
  try {
    return storage?.getItem(PASSWORD_RESET_EMAIL_KEY) ?? "";
  } catch {
    return "";
  }
}

export function savePasswordResetEmail(email, storage = sessionStorageOrNull()) {
  const normalizedEmail = email.trim().toLowerCase();
  try {
    if (normalizedEmail) storage?.setItem(PASSWORD_RESET_EMAIL_KEY, normalizedEmail);
    else storage?.removeItem(PASSWORD_RESET_EMAIL_KEY);
  } catch {
    // Reset remains usable through navigation state when storage is unavailable.
  }
  return normalizedEmail;
}

export function clearPasswordResetEmail(storage = sessionStorageOrNull()) {
  try {
    storage?.removeItem(PASSWORD_RESET_EMAIL_KEY);
  } catch {
    // Storage cleanup must not hide a successful password reset.
  }
}
