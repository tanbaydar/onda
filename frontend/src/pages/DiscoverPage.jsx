import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";

import { fetchJson } from "../api.js";
import EventList from "../components/EventList.jsx";
import DiscoverSearch from "../components/DiscoverSearch.jsx";
import CityDropdown from "../components/CityDropdown.jsx";
import "../discover.css";

function emptyLedger() {
  return { page: 1, retry: 0, requestKey: null, state: { loading: true, error: null, data: null } };
}

function DiscoverLedgers({ city }) {
  const [view, setView] = useState("upcoming");
  const [ledgers, setLedgers] = useState({ upcoming: emptyLedger(), recent: emptyLedger() });
  return <>
    <nav className="section-tabs" aria-label="Event timeframe">
      <button type="button" className={`tab-action${view === "upcoming" ? " active" : ""}`} aria-pressed={view === "upcoming"} onClick={() => setView("upcoming")}>Upcoming</button>
      <button type="button" className={`tab-action${view === "recent" ? " active" : ""}`} aria-pressed={view === "recent"} onClick={() => setView("recent")}>Recent</button>
    </nav>
    {view === "upcoming" ? <EventList
      heading={`Upcoming events in ${city.name}`}
      scopeName="city_id"
      scopeId={city.id}
      when="upcoming"
      emptyMessage={`No upcoming events in ${city.name}.`}
      quietHeading
      discover
      ledger={ledgers.upcoming}
      onLedgerChange={(update) => setLedgers((current) => ({ ...current, upcoming: update(current.upcoming) }))}
    /> : <EventList
      heading={`Recent events in ${city.name}`}
      scopeName="city_id"
      scopeId={city.id}
      when="past"
      pageSize={10}
      emptyMessage={`No recent events in ${city.name}.`}
      quietHeading
      discover
      ledger={ledgers.recent}
      onLedgerChange={(update) => setLedgers((current) => ({ ...current, recent: update(current.recent) }))}
    />}
  </>;
}

export default function DiscoverPage() {
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
    <main className="discover-page" aria-busy={state.loading}>
      {!selectedCity ? <div className="discover-header-band"><h1 className="functional-title">Discover Events</h1></div> : null}
      {state.loading ? <p role="status" aria-live="polite">Loading cities…</p> : null}
      {state.error ? (
        <div className="event-list-error" role="alert">
          <p>Cities could not be loaded.</p>
          <button className="recovery-action" type="button" onClick={() => setRetry((value) => value + 1)}>
            Retry
          </button>
        </div>
      ) : null}
      {state.cities && state.cities.length === 0 ? (
        <p>No cities are available.</p>
      ) : null}
      {selectedCity ? (
        <>
          <div className="discover-header-band">
            <h1 className="identity-title">Discover Events</h1>
            <div className="discover-control-pair">
              <CityDropdown cities={state.cities} selectedCity={selectedCity} label="City" hideLabel onSelect={(cityId) => setSearchParams({ city_id: String(cityId) })} />
              <DiscoverSearch cityId={String(selectedCity.id)} cityName={selectedCity.name} />
            </div>
          </div>
          <DiscoverLedgers key={selectedCity.id} city={selectedCity} />
        </>
      ) : null}
    </main>
  );
}
