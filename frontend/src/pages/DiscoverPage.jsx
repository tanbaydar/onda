import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";

import { fetchJson } from "../api.js";
import EventList from "../components/EventList.jsx";

export default function DiscoverPage() {
  const [view, setView] = useState("upcoming");
  const [searchParams, setSearchParams] = useSearchParams();
  const [retry, setRetry] = useState(0);
  const [state, setState] = useState({
    loading: true,
    error: null,
    cities: null,
  });

  useEffect(() => {
    const controller = new AbortController();
    setState({ loading: true, error: null, cities: null });
    fetchJson("/api/cities/", { signal: controller.signal })
      .then((data) => {
        setState({ loading: false, error: null, cities: data.results });
      })
      .catch((error) => {
        if (error.name !== "AbortError") {
          setState({ loading: false, error, cities: null });
        }
      });
    return () => controller.abort();
  }, [retry]);

  const requestedCityId = searchParams.get("city_id");
  const selectedCity =
    state.cities?.find((city) => String(city.id) === requestedCityId) ??
    state.cities?.[0] ??
    null;

  useEffect(() => {
    if (selectedCity && String(selectedCity.id) !== requestedCityId) {
      setSearchParams({ city_id: String(selectedCity.id) }, { replace: true });
    }
  }, [requestedCityId, selectedCity, setSearchParams]);

  return (
    <main className="discover-page">
      <h1>Discover</h1>
      {state.loading ? <p>Loading cities.</p> : null}
      {state.error ? (
        <>
          <p>Cities could not be loaded.</p>
          <button type="button" onClick={() => setRetry((value) => value + 1)}>
            Retry
          </button>
        </>
      ) : null}
      {state.cities && state.cities.length === 0 ? (
        <p>No cities are available.</p>
      ) : null}
      {selectedCity ? (
        <>
          <form>
            <label htmlFor="city">Browse city</label>{" "}
            <select
              id="city"
              value={selectedCity.id}
              onChange={(event) => {
                setSearchParams({ city_id: event.target.value });
              }}
            >
              {state.cities.map((city) => (
                <option key={city.id} value={city.id}>
                  {city.name}
                </option>
              ))}
            </select>
          </form>
          <h2 className="discover-city">{selectedCity.name}</h2>
          <nav className="section-tabs" aria-label="Event timeframe">
            <button type="button" className={view === "upcoming" ? "active" : ""} aria-pressed={view === "upcoming"} onClick={() => setView("upcoming")}>Upcoming</button>
            <button type="button" className={view === "recent" ? "active" : ""} aria-pressed={view === "recent"} onClick={() => setView("recent")}>Recent</button>
          </nav>
          <EventList
            key={selectedCity.id}
            heading={`Upcoming events in ${selectedCity.name}`}
            scopeName="city_id"
            scopeId={selectedCity.id}
            when="upcoming"
            emptyMessage={`No upcoming events in ${selectedCity.name}.`}
            showCity={false}
            hidden={view !== "upcoming"}
            quietHeading
          />
          <EventList
            key={`recent-${selectedCity.id}`}
            heading={`Recent events in ${selectedCity.name}`}
            scopeName="city_id"
            scopeId={selectedCity.id}
            when="past"
            pageSize={10}
            emptyMessage={`No recent events in ${selectedCity.name}.`}
            showCity={false}
            hidden={view !== "recent"}
            quietHeading
          />
        </>
      ) : null}
    </main>
  );
}
