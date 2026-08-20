import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";

import { fetchJson } from "../api.js";
import { recordRecentSearch } from "../recentSearches.js";
import SearchResults from "./SearchResults.jsx";

export default function DiscoverSearch({ cityId, cityName = "this city" }) {
  const navigate = useNavigate();
  const rootRef = useRef(null);
  const [query, setQuery] = useState("");
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [retry, setRetry] = useState(0);
  const trimmed = query.trim();

  useEffect(() => {
    if (!trimmed) { setData(null); setError(null); setLoading(false); return undefined; }
    const controller = new AbortController();
    setError(null);
    setLoading(true);
    const timer = setTimeout(() => {
      const params = new URLSearchParams({ q: trimmed, scope: "events", city_id: cityId });
      fetchJson(`/api/search/?${params}`, { signal: controller.signal })
        .then((nextData) => { setData(nextData); setLoading(false); })
        .catch((nextError) => { if (nextError.name !== "AbortError") { setData(null); setError(nextError); setLoading(false); } });
    }, 250);
    return () => { clearTimeout(timer); controller.abort(); };
  }, [cityId, retry, trimmed]);

  useEffect(() => {
    function close(event) { if (!rootRef.current?.contains(event.target)) { setQuery(""); setData(null); } }
    document.addEventListener("pointerdown", close);
    return () => document.removeEventListener("pointerdown", close);
  }, []);

  function openSearch() {
    if (!trimmed) return;
    recordRecentSearch(query);
    navigate(`/search?${new URLSearchParams({ q: trimmed, scope: "events" })}`);
  }

  return (
    <div className="discover-search" ref={rootRef}>
      <div className="discover-search-input-wrap">
        <input type="text" value={query} aria-label={`Search events in ${cityName}`} placeholder={`Search events in ${cityName}`} onChange={(event) => setQuery(event.target.value)} onKeyDown={(event) => { if (event.key === "Enter") openSearch(); if (event.key === "Escape") { setQuery(""); setData(null); } }} />
        {query ? <button className="discover-search-clear" type="button" aria-label="Clear search" onClick={() => { setQuery(""); setData(null); }}>×</button> : null}
      </div>
      {trimmed && (data || error || loading) ? (
        <div className="search-panel">
          {loading ? <p className="search-status" role="status" aria-live="polite">Searching…</p> : null}
          {error ? <p className="search-error" role="alert">Search failed. <button type="button" onClick={() => setRetry((value) => value + 1)}>Try again.</button></p> : null}
          {data?.results.length ? <SearchResults compact data={data} scope="events" activeIndex={-1} onActiveIndex={() => {}} onResultOpen={() => recordRecentSearch(query)} onViewAll={openSearch} /> : data ? <p className="search-empty" role="status" aria-live="polite">No results for &quot;{trimmed}&quot;.</p> : null}
          {data && data.total < 3 ? <button className="search-all-cities" type="button" onClick={openSearch}>Search all cities →</button> : null}
        </div>
      ) : null}
    </div>
  );
}
