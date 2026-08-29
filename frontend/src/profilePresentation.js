export const PROFILE_EMPTY_STATES = {
  favourites: "No favourites yet.",
  been: "No events in Been yet.",
  reviews: "No reviews yet.",
};

export const PROFILE_REVIEW_SORTS = [
  { value: "newest", label: "Newest" },
  { value: "most_liked", label: "Most liked" },
  { value: "oldest", label: "Oldest" },
  { value: "longest", label: "Longest entry" },
];

export function profileInitials(displayName) {
  const words = String(displayName ?? "").trim().split(/\s+/).filter(Boolean);
  if (!words.length) return "?";
  return (words.length === 1 ? words[0].slice(0, 2) : `${words[0][0]}${words.at(-1)[0]}`).toUpperCase();
}

export function profileBioCount(value) {
  return `${String(value ?? "").length} / 150`;
}

export function profileTabPath(username, tab) {
  const root = `/u/${String(username).toLowerCase()}`;
  if (tab === "been") return `${root}/been`;
  if (tab === "reviews") return `${root}/reviews`;
  return root;
}
