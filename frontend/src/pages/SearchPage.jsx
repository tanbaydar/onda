import { useEffect, useMemo, useState } from "react";
import { useSearchParams } from "react-router-dom";

import { fetchJson } from "../api.js";
import SearchResults from "../components/SearchResults.jsx";

const SCOPES = [["all", "All"], ["events", "Events"], ["artists", "Artists"], ["venues", "Venues"], ["people", "People"]];
const RECENT_KEY = "danced.recentSearches";

function readRecent() {
  try { return JSON.parse(localStorage.getItem(RECENT_KEY) ?? "[]").filter((item) => typeof item === "string").slice(0, 10); }
  catch { return []; }
}

export default function SearchPage() {
  const [params, setParams] = useSearchParams();
  const initialQuery = params.get("q") ?? "";
  const initialScope = SCOPES.some(([value]) => value === params.get("scope")) ? params.get("scope") : "all";
  const [query, setQuery] = useState(initialQuery);
  const [scope, setScope] = useState(initialScope);
  const [recent, setRecent] = useState(readRecent);
  const [state, setState] = useState({ loading: false, error: null, data: null });
  const [activeIndex, setActiveIndex] = useState(-1);
  const [loadingMore, setLoadingMore] = useState(false);
  const trimmed = query.trim();

  useEffect(() => {
    if (!trimmed) { setState({ loading: false, error: null, data: null }); return undefined; }
    const controller = new AbortController();
    const timer = setTimeout(() => {
      setState({ loading: true, error: null, data: null });
      fetchJson(`/api/search/?${new URLSearchParams({ q: trimmed, scope })}`, { signal: controller.signal })
        .then((data) => {
          setState({ loading: false, error: null, data });
          setParams({ q: trimmed, ...(scope === "all" ? {} : { scope }) }, { replace: true });
          setRecent((current) => {
            const next = [trimmed, ...current.filter((item) => item.toLowerCase() !== trimmed.toLowerCase())].slice(0, 10);
            localStorage.setItem(RECENT_KEY, JSON.stringify(next));
            return next;
          });
        })
        .catch((error) => { if (error.name !== "AbortError") setState({ loading: false, error, data: null }); });
    }, 250);
    return () => { clearTimeout(timer); controller.abort(); };
  }, [scope, setParams, trimmed]);

  const resultCount = useMemo(() => state.data ? (scope === "all" ? Object.values(state.data.groups).reduce((sum, group) => sum + group.results.length, 0) : state.data.results.length) : 0, [scope, state.data]);
  function removeRecent(item) { setRecent((current) => { const next = current.filter((value) => value !== item); localStorage.setItem(RECENT_KEY, JSON.stringify(next)); return next; }); }
  function onKeyDown(event) {
    if (event.key === "Escape") { setQuery(""); setParams({}, { replace: true }); setActiveIndex(-1); }
    if (event.key === "ArrowDown" && resultCount) { event.preventDefault(); setActiveIndex((value) => (value + 1) % resultCount); }
    if (event.key === "ArrowUp" && resultCount) { event.preventDefault(); setActiveIndex((value) => (value <= 0 ? resultCount - 1 : value - 1)); }
  }
  async function loadMore() {
    if (!state.data?.next_cursor) return;
    setLoadingMore(true);
    try {
      const next = await fetchJson(`/api/search/?${new URLSearchParams({ q: trimmed, scope, cursor: state.data.next_cursor })}`);
      setState((current) => ({ loading: false, error: null, data: { ...next, results: [...current.data.results, ...next.results] } }));
    } catch (error) { setState((current) => ({ ...current, error })); }
    finally { setLoadingMore(false); }
  }
  return (
    <main className="search-page" onKeyDown={onKeyDown}>
      <h1>Search</h1>
      <input className="search-primary" type="search" value={query} autoFocus aria-label="Search Danced" onChange={(event) => { setQuery(event.target.value); setActiveIndex(-1); }} />
      <nav className="search-scopes" aria-label="Search scope">{SCOPES.map(([value, label]) => <button key={value} className={scope === value ? "active" : ""} type="button" onClick={() => { setScope(value); setActiveIndex(-1); }}>{label}</button>)}</nav>
      {!trimmed ? <section className="recent-searches"><h2>Recent searches</h2>{recent.length ? <><ul>{recent.map((item) => <li key={item}><button type="button" onClick={() => setQuery(item)}>{item}</button><button type="button" aria-label={`Remove ${item}`} onClick={() => removeRecent(item)}>×</button></li>)}</ul><button className="quiet-action" type="button" onClick={() => { localStorage.removeItem(RECENT_KEY); setRecent([]); }}>Clear all</button></> : <p>No recent searches.</p>}</section> : null}
      {state.loading ? <p className="search-status">Searching…</p> : null}
      {state.error ? <p role="alert">Search could not be loaded.</p> : null}
      {trimmed && state.data && resultCount === 0 ? <p className="search-empty">No results for &quot;{trimmed}&quot;.</p> : null}
      {state.data && resultCount ? <SearchResults data={state.data} scope={scope} activeIndex={activeIndex} onActiveIndex={setActiveIndex} onViewAll={(nextScope) => setScope(nextScope)} /> : null}
      {scope !== "all" && state.data?.next_cursor ? <button className="quiet-control search-load-more" type="button" disabled={loadingMore} onClick={loadMore}>{loadingMore ? "Loading…" : "Load more"}</button> : null}
    </main>
  );
}
