import { profilePath } from "./profileRoutes.js";

export function primaryNavigationItems(user) {
  const search = { label: "Search", to: "/search", auxiliary: true };
  if (!user) return [
    { label: "Discover", to: "/discover" },
    search,
  ];
  return [
    { label: "Home", to: "/home" },
    { label: "Discover", to: "/discover" },
    search,
    { label: "Activity", to: "/activity" },
    { label: "Profile", to: profilePath(user.username) },
  ];
}
