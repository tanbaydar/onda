import { useEffect, useMemo, useRef, useState } from "react";
import { useSearchParams } from "react-router-dom";

import { fetchJson } from "../api.js";
import SearchResults from "../components/SearchResults.jsx";
import { RECENT_SEARCHES_KEY, readRecentSearches, recordRecentSearch } from "../recentSearches.js";
import { EMPTY_SEARCH_STATE, isCurrentSearchRequest, scopeTransition, searchResultCount } from "../searchPageState.js";

const SCOPES = [["all", "All"], ["events", "Events"], ["artists", "Artists"], ["venues", "Venues"], ["people", "People"]];
export default function SearchPage() {
  const [params, setParams] = useSearchParams();
  const initialQuery = params.get("q") ?? "";
  const initialScope = SCOPES.some(([value]) => value === params.get("scope")) ? params.get("scope") : "all";
  const [query, setQuery] = useState(initialQuery);
  const [scope, setScope] = useState(initialScope);
  const [recent, setRecent] = useState(readRecentSearches);
  const [state, setState] = useState(EMPTY_SEARCH_STATE);
  const [activeIndex, setActiveIndex] = useState(-1);
  const [loadingMore, setLoadingMore] = useState(false);
  const activeRequestId = useRef(0);
  const trimmed = query.trim();

  useEffect(() => {
    const requestId = ++activeRequestId.current;
    if (!trimmed) { setState(EMPTY_SEARCH_STATE); return undefined; }
    const controller = new AbortController();
    setState({ loading: true, error: null, data: null });
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
  }, [scope, setParams, trimmed]);

  useEffect(() => {
    function syncRecent(event) { setRecent(event.detail); }
    window.addEventListener("danced:recent-searches", syncRecent);
    return () => window.removeEventListener("danced:recent-searches", syncRecent);
  }, []);

  const resultCount = useMemo(() => searchResultCount(scope, state.data), [scope, state.data]);
  function commitRecent() { setRecent(recordRecentSearch(query)); }
  function removeRecent(item) { setRecent((current) => { const next = current.filter((value) => value !== item); localStorage.setItem(RECENT_SEARCHES_KEY, JSON.stringify(next)); return next; }); }
  function changeScope(nextScope) {
    const transition = scopeTransition(scope, nextScope);
    if (!transition) return;
    if (trimmed) commitRecent();
    activeRequestId.current += 1;
    setState(transition.state);
    setLoadingMore(transition.loadingMore);
    setActiveIndex(transition.activeIndex);
    setScope(transition.scope);
  }
  function onKeyDown(event) {
    if (event.key === "Escape") { setQuery(""); setParams({}, { replace: true }); setActiveIndex(-1); }
    if (event.key === "ArrowDown" && resultCount) { event.preventDefault(); setActiveIndex((value) => (value + 1) % resultCount); }
    if (event.key === "ArrowUp" && resultCount) { event.preventDefault(); setActiveIndex((value) => (value <= 0 ? resultCount - 1 : value - 1)); }
    if (event.key === "Enter" && event.target.classList.contains("search-primary") && trimmed) commitRecent();
  }
  async function loadMore() {
    if (!state.data?.next_cursor) return;
    const requestId = activeRequestId.current;
    setLoadingMore(true);
    try {
      const next = await fetchJson(`/api/search/?${new URLSearchParams({ q: trimmed, scope, cursor: state.data.next_cursor })}`);
      if (!isCurrentSearchRequest(activeRequestId.current, requestId)) return;
      setState((current) => ({ loading: false, error: null, data: { ...next, results: [...current.data.results, ...next.results] } }));
    } catch (error) { if (isCurrentSearchRequest(activeRequestId.current, requestId)) setState((current) => ({ ...current, error })); }
    finally { if (isCurrentSearchRequest(activeRequestId.current, requestId)) setLoadingMore(false); }
  }
  return (
    <main className="search-page" onKeyDown={onKeyDown}>
      <h1>Search</h1>
      <input className="search-primary" type="search" value={query} autoFocus aria-label="Search Danced" onChange={(event) => { setQuery(event.target.value); setActiveIndex(-1); }} />
      <nav className="search-scopes" aria-label="Search scope">{SCOPES.map(([value, label]) => <button key={value} className={scope === value ? "active" : ""} type="button" aria-pressed={scope === value} onClick={() => changeScope(value)}>{label}</button>)}</nav>
      {!trimmed ? <section className="recent-searches"><h2>Recent searches</h2>{recent.length ? <><ul>{recent.map((item) => <li key={item}><button type="button" onClick={() => setQuery(item)}>{item}</button><button type="button" aria-label={`Remove ${item}`} onClick={() => removeRecent(item)}>×</button></li>)}</ul><button className="quiet-action" type="button" onClick={() => { localStorage.removeItem(RECENT_SEARCHES_KEY); setRecent([]); }}>Clear all</button></> : <p>No recent searches.</p>}</section> : null}
      {state.loading ? <p className="search-status" role="status" aria-live="polite">Searching…</p> : null}
      {state.error ? <p role="alert">Search could not be loaded.</p> : null}
      {trimmed && state.data && resultCount === 0 ? <p className="search-empty" role="status" aria-live="polite">No results for &quot;{trimmed}&quot;.</p> : null}
      {state.data && resultCount ? <SearchResults data={state.data} scope={scope} activeIndex={activeIndex} onActiveIndex={setActiveIndex} onResultOpen={commitRecent} onViewAll={changeScope} /> : null}
      {scope !== "all" && state.data?.next_cursor ? <button className="quiet-control search-load-more" type="button" disabled={loadingMore} onClick={loadMore}>{loadingMore ? "Loading…" : "Load more"}</button> : null}
    </main>
  );
}
