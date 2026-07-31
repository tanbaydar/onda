export const AUTHENTICATED_LANDING = "/home";
export const GUEST_DISCOVER = "/discover";

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
