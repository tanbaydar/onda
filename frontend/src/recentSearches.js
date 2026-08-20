export const RECENT_SEARCHES_KEY = "onda.recentSearches";

export function readRecentSearches(storage = localStorage) {
  try {
    return JSON.parse(storage.getItem(RECENT_SEARCHES_KEY) ?? "[]")
      .filter((item) => typeof item === "string")
      .slice(0, 10);
  } catch {
    return [];
  }
}

export function recordRecentSearch(query, storage = localStorage) {
  const trimmed = query.trim();
  if (!trimmed) return readRecentSearches(storage);
  const normalized = trimmed.toLowerCase();
  const next = [
    trimmed,
    ...readRecentSearches(storage).filter(
      (item) => !normalized.startsWith(item.toLowerCase()),
    ),
  ].slice(0, 10);
  storage.setItem(RECENT_SEARCHES_KEY, JSON.stringify(next));
  if (storage === globalThis.localStorage) {
    globalThis.dispatchEvent(new CustomEvent("onda:recent-searches", { detail: next }));
  }
  return next;
}
