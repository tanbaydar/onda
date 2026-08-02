import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";

import { fetchJson } from "../api.js";
import SearchResults from "./SearchResults.jsx";

export default function QuickSearch({ cityId = null, discover = false }) {
  const navigate = useNavigate();
  const rootRef = useRef(null);
  const [query, setQuery] = useState("");
  const [data, setData] = useState(null);
  const trimmed = query.trim();

  useEffect(() => {
    if (!trimmed) { setData(null); return undefined; }
    const controller = new AbortController();
    const timer = setTimeout(() => {
      const params = new URLSearchParams({ q: trimmed, scope: discover ? "events" : "all" });
      if (cityId) params.set("city_id", cityId);
      fetchJson(`/api/search/?${params}`, { signal: controller.signal }).then(setData).catch((error) => { if (error.name !== "AbortError") setData(null); });
    }, 250);
    return () => { clearTimeout(timer); controller.abort(); };
  }, [cityId, discover, trimmed]);

  useEffect(() => {
    function close(event) { if (!rootRef.current?.contains(event.target)) { setQuery(""); setData(null); } }
    document.addEventListener("pointerdown", close);
    return () => document.removeEventListener("pointerdown", close);
  }, []);

  const count = data ? (discover ? data.results.length : Object.values(data.groups).reduce((sum, group) => sum + group.results.length, 0)) : 0;
  function openSearch(scope = "all") { if (trimmed) navigate(`/search?${new URLSearchParams({ q: trimmed, ...(scope === "all" ? {} : { scope }) })}`); }

  return (
    <div className={`quick-search ${discover ? "discover-search" : "header-search"}`} ref={rootRef}>
      <input type="search" value={query} aria-label={discover ? "Search events in selected city" : "Quick search"} placeholder={discover ? "Search events in this city" : "Search"} onChange={(event) => setQuery(event.target.value)} onKeyDown={(event) => { if (event.key === "Enter") openSearch(discover ? "events" : "all"); if (event.key === "Escape") { setQuery(""); setData(null); } }} />
      {trimmed && data ? (
        <div className="search-panel">
          {count ? <SearchResults data={data} scope={discover ? "events" : "all"} activeIndex={-1} onActiveIndex={() => {}} onViewAll={openSearch} /> : <p className="search-empty">No results for &quot;{trimmed}&quot;.</p>}
          {discover && data.total < 3 ? <button className="search-all-cities" type="button" onClick={() => openSearch("events")}>Search all cities →</button> : null}
        </div>
      ) : null}
    </div>
  );
}
