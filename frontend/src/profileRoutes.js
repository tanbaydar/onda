export function profilePath(username) {
  return `/u/${username.toLowerCase()}`;
}

export function legacyBeenRedirect(user) {
  return user ? profilePath(user.username) : "/login";
}
