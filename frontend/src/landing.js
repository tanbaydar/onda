export const AUTHENTICATED_LANDING = "/home";
export const GUEST_DISCOVER = "/discover";
export const VERIFY_EMAIL = "/verify-email";

export function postAuthDestination(user) {
  return user?.email_verified === false ? VERIFY_EMAIL : AUTHENTICATED_LANDING;
}

export function landingPath(user, search = "") {
  const params = new URLSearchParams(search);
  if (params.has("city_id")) {
    const city = new URLSearchParams({ city_id: params.get("city_id") });
    return `/discover?${city}`;
  }
  return user ? AUTHENTICATED_LANDING : GUEST_DISCOVER;
}

export function homeAccessRedirect(user) {
  return user ? null : GUEST_DISCOVER;
}
