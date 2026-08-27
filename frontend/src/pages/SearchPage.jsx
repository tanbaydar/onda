import { useEffect, useMemo, useRef, useState } from "react";
import { useSearchParams } from "react-router-dom";

import { fetchJson } from "../api.js";
import SearchResults from "../components/SearchResults.jsx";
import { RECENT_SEARCHES_KEY, readRecentSearches, recordRecentSearch } from "../recentSearches.js";
import { EMPTY_SEARCH_STATE, isCurrentSearchRequest, scopeTransition, searchResultCount } from "../searchPageState.js";

const SCOPES = [["all", "All"], ["events", "Events"], ["artists", "Artists"], ["venues", "Venues"], ["people", "People"]];

function scopeRailHasHiddenScope(rail) {
  const lastScope = rail?.lastElementChild;
  if (!rail || !lastScope) return false;
  return lastScope.getBoundingClientRect().right > rail.getBoundingClientRect().right + 1;
}

export default function SearchPage() {
  const [params, setParams] = useSearchParams();
  const initialQuery = params.get("q") ?? "";
  const initialScope = SCOPES.some(([value]) => value === params.get("scope")) ? params.get("scope") : "all";
  const [query, setQuery] = useState(initialQuery);
  const [scope, setScope] = useState(initialScope);
  const [recent, setRecent] = useState(readRecentSearches);
  const [state, setState] = useState(EMPTY_SEARCH_STATE);
  const [activeIndex, setActiveIndex] = useState(-1);
  const [retry, setRetry] = useState(0);
  const [loadingMore, setLoadingMore] = useState(false);
  const [loadMoreError, setLoadMoreError] = useState(null);
  const activeRequestId = useRef(0);
  const scopeRailRef = useRef(null);
  const [scopeHasMore, setScopeHasMore] = useState(false);
  const trimmed = query.trim();
  const searchReady = Boolean(trimmed);

  useEffect(() => {
    const requestId = ++activeRequestId.current;
    if (!searchReady) {
      setState(EMPTY_SEARCH_STATE);
      setLoadingMore(false);
      setLoadMoreError(null);
      return undefined;
    }
    const controller = new AbortController();
    setState({ loading: true, error: null, data: null });
    setLoadMoreError(null);
    const timer = setTimeout(() => {
      fetchJson(`/api/search/?${new URLSearchParams({ q: trimmed, scope })}`, { signal: controller.signal })
        .then((data) => {
          if (!isCurrentSearchRequest(activeRequestId.current, requestId)) return;
          setState({ loading: false, error: null, data });
          setParams({ q: trimmed, ...(scope === "all" ? {} : { scope }) }, { replace: true });
        })
        .catch((error) => { if (error.name !== "AbortError" && isCurrentSearchRequest(activeRequestId.current, requestId)) setState({ loading: false, error, data: null }); });
    }, 250);
    return () => { clearTimeout(timer); controller.abort(); };
  }, [retry, scope, searchReady, setParams, trimmed]);

  useEffect(() => {
    function syncRecent(event) { setRecent(event.detail); }
    window.addEventListener("onda:recent-searches", syncRecent);
    return () => window.removeEventListener("onda:recent-searches", syncRecent);
  }, []);

  useEffect(() => {
    function updateScopeCue() {
      setScopeHasMore(scopeRailHasHiddenScope(scopeRailRef.current));
    }
    updateScopeCue();
    window.addEventListener("resize", updateScopeCue);
    return () => window.removeEventListener("resize", updateScopeCue);
  }, []);

  const resultCount = useMemo(() => searchResultCount(scope, state.data), [scope, state.data]);
  function commitRecent() { setRecent(recordRecentSearch(query)); }
  function removeRecent(item) { setRecent((current) => { const next = current.filter((value) => value !== item); localStorage.setItem(RECENT_SEARCHES_KEY, JSON.stringify(next)); return next; }); }
  function clearSearch() {
    activeRequestId.current += 1;
    setQuery("");
    setParams({}, { replace: true });
    setState(EMPTY_SEARCH_STATE);
    setActiveIndex(-1);
    setLoadingMore(false);
    setLoadMoreError(null);
  }
  function changeScope(nextScope) {
    const transition = scopeTransition(scope, nextScope);
    if (!transition) return;
    if (searchReady) commitRecent();
    activeRequestId.current += 1;
    setState(transition.state);
    setLoadingMore(transition.loadingMore);
    setLoadMoreError(null);
    setActiveIndex(transition.activeIndex);
    setScope(transition.scope);
  }
  function onKeyDown(event) {
    if (event.key === "Escape") clearSearch();
    if (event.key === "ArrowDown" && searchReady && resultCount) { event.preventDefault(); setActiveIndex((value) => (value + 1) % resultCount); }
    if (event.key === "ArrowUp" && searchReady && resultCount) { event.preventDefault(); setActiveIndex((value) => (value <= 0 ? resultCount - 1 : value - 1)); }
    if (event.key === "Enter" && event.target.classList.contains("search-primary") && searchReady) commitRecent();
  }
  async function loadMore() {
    if (!state.data?.next_cursor) return;
    const requestId = activeRequestId.current;
    setLoadingMore(true);
    setLoadMoreError(null);
    try {
      const next = await fetchJson(`/api/search/?${new URLSearchParams({ q: trimmed, scope, cursor: state.data.next_cursor })}`);
      if (!isCurrentSearchRequest(activeRequestId.current, requestId)) return;
      setState((current) => ({ loading: false, error: null, data: { ...next, results: [...current.data.results, ...next.results] } }));
    } catch (error) { if (isCurrentSearchRequest(activeRequestId.current, requestId)) setLoadMoreError(error); }
    finally { if (isCurrentSearchRequest(activeRequestId.current, requestId)) setLoadingMore(false); }
  }
  return (
    <main className="search-page" onKeyDown={onKeyDown}>
      <h1 className="functional-title search-title">Search</h1>
      <div className="search-primary-wrap">
        <input className="search-primary" type="search" value={query} autoFocus aria-label="Search Onda" onChange={(event) => { setQuery(event.target.value); setActiveIndex(-1); }} />
        {query ? <button className="search-primary-clear" type="button" aria-label="Clear search" onClick={clearSearch}>×</button> : null}
      </div>
      <div className="search-scopes-rail"><nav className="search-scopes" aria-label="Search scope" ref={scopeRailRef} onScroll={() => setScopeHasMore(scopeRailHasHiddenScope(scopeRailRef.current))}>{SCOPES.map(([value, label]) => <button key={value} className={`tab-action${scope === value ? " active" : ""}`} type="button" aria-pressed={scope === value} onFocus={(event) => { event.currentTarget.scrollIntoView({ block: "nearest", inline: "nearest" }); window.requestAnimationFrame(() => setScopeHasMore(scopeRailHasHiddenScope(scopeRailRef.current))); }} onClick={() => changeScope(value)}>{label}</button>)}</nav><span className={`search-scopes-cue${scopeHasMore ? "" : " is-end"}`} aria-hidden="true">More →</span></div>
      {!trimmed ? <section className="recent-searches"><h2 className="section-heading">Recent searches</h2>{recent.length ? <><ul className="ledger-list">{recent.map((item) => <li key={item}><button type="button" onClick={() => setQuery(item)}>{item}</button><button type="button" aria-label={`Remove ${item}`} onClick={() => removeRecent(item)}>×</button></li>)}</ul><button className="quiet-action" type="button" onClick={() => { localStorage.removeItem(RECENT_SEARCHES_KEY); setRecent([]); }}>Clear all</button></> : <p>No recent searches.</p>}</section> : null}
      {searchReady && state.loading ? <p className="search-status" role="status" aria-live="polite">Searching…</p> : null}
      {searchReady && state.error ? <div className="search-error" role="alert"><p>Search could not be loaded.</p><button className="recovery-action" type="button" onClick={() => setRetry((value) => value + 1)}>Retry</button></div> : null}
      {searchReady && state.data && resultCount === 0 ? <p className="search-empty" role="status" aria-live="polite">No results for &quot;{trimmed}&quot;.</p> : null}
      {searchReady && state.data && resultCount ? <SearchResults data={state.data} scope={scope} activeIndex={activeIndex} onActiveIndex={setActiveIndex} onResultOpen={commitRecent} onViewAll={changeScope} /> : null}
      {loadMoreError ? <div className="search-error" role="alert"><p>More results could not be loaded.</p><button className="recovery-action" type="button" onClick={loadMore}>Retry</button></div> : null}
      {searchReady && scope !== "all" && state.data?.next_cursor ? <button className="quiet-control pagination-action search-load-more" type="button" disabled={loadingMore} onClick={loadMore}>{loadingMore ? "Loading…" : "Load more"}</button> : null}
    </main>
  );
}
