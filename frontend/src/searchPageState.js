export const EMPTY_SEARCH_STATE = { loading: false, error: null, data: null };
export const MIN_SEARCH_QUERY_LENGTH = 2;

export function searchQueryReady(query) {
  return query.trim().length >= MIN_SEARCH_QUERY_LENGTH;
}

export function scopeTransition(currentScope, nextScope) {
  if (currentScope === nextScope) return null;
  return {
    scope: nextScope,
    state: EMPTY_SEARCH_STATE,
    activeIndex: -1,
    loadingMore: false,
  };
}

export function isCurrentSearchRequest(activeRequestId, responseRequestId) {
  return activeRequestId === responseRequestId;
}

export function searchResultCount(scope, data) {
  if (!data) return 0;
  if (scope === "all") {
    if (!data.groups) return 0;
    return Object.values(data.groups).reduce(
      (sum, group) => sum + group.results.length,
      0,
    );
  }
  return Array.isArray(data.results) ? data.results.length : 0;
}
