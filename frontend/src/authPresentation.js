export const INVALID_LOGIN_MESSAGE = "That username or email and password don't match. Try again or reset your password.";
export const CODE_EXPIRY_NOTICE = "Codes expire after 15 minutes.";

export function resetConfirmation(email) {
  return `If an account exists for ${email}, a six-digit code is on its way. Check your inbox.`;
}

export function retainRegistrationValues(values) {
  return { ...values };
}

export function codeError(messages = []) {
  const copy = messages.join(" ").toLowerCase();
  return copy.includes("expired") ? "That code has expired. We've sent a new one." : "That code isn't right. Check the email or resend.";
}
