export function profilePath(username) {
  return `/u/${username.toLowerCase()}`;
}

export function legacyBeenRedirect(user) {
  return user ? `${profilePath(user.username)}/been` : "/login";
}

export function profileNavigationVisible(access) {
  return access === "full" || access === "owner";
}
