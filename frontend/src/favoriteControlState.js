export const FAVORITE_CONTROL_INITIAL = { pending: false, message: null };

export function favoriteRequestStarted() {
  return { pending: true, message: null };
}

export function favoriteRequestRejected(message) {
  return { pending: false, message };
}

export function favoriteRequestSettled() {
  return FAVORITE_CONTROL_INITIAL;
}
