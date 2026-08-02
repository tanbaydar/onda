export function headerSearchMode(pathname, expanded) {
  if (pathname === "/search") return "text";
  return expanded ? "input" : "text";
}

export function shouldExpandHeaderSearch(pathname, desktop) {
  return pathname !== "/search" && desktop;
}
