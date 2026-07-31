import { useEffect, useState } from "react";
import { Link, Route, Routes } from "react-router-dom";

import { fetchJson, fetchWithCsrf } from "./api.js";
import ArtistPage from "./pages/ArtistPage.jsx";
import DiscoverPage from "./pages/DiscoverPage.jsx";
import EventPage from "./pages/EventPage.jsx";
import LoginPage from "./pages/LoginPage.jsx";
import RegisterPage from "./pages/RegisterPage.jsx";
import VenuePage from "./pages/VenuePage.jsx";

function NotFoundPage() {
  return (
    <main>
      <h1>Page not found</h1>
      <p>The page you requested does not exist.</p>
      <p>
        <Link to="/">Return to Discover</Link>
      </p>
    </main>
  );
}

export default function App() {
  const [retry, setRetry] = useState(0);
  const [session, setSession] = useState({
    loading: true,
    error: null,
    user: null,
  });

  useEffect(() => {
    const controller = new AbortController();
    setSession({ loading: true, error: null, user: null });
    fetchJson("/api/auth/session/", { signal: controller.signal })
      .then((data) => {
        setSession({ loading: false, error: null, user: data.user });
      })
      .catch((error) => {
        if (error.name !== "AbortError") {
          setSession({ loading: false, error, user: null });
        }
      });
    return () => controller.abort();
  }, [retry]);

  async function handleLogout() {
    try {
      await fetchWithCsrf("/api/auth/logout/", {
        method: "POST",
        body: JSON.stringify({}),
        headers: { "Content-Type": "application/json" },
      });
      setSession({ loading: false, error: null, user: null });
    } catch (error) {
      setSession((current) => ({ ...current, error }));
    }
  }

  return (
    <>
      <header>
        <p>Danced</p>
        <nav aria-label="Primary navigation">
          <ul>
            <li>
              <Link to="/">Discover</Link>
            </li>
            {session.user ? (
              <>
                <li>Signed in as {session.user.username}</li>
                <li>
                  <button type="button" onClick={handleLogout}>
                    Log out
                  </button>
                </li>
              </>
            ) : (
              <>
                <li>
                  <Link to="/register">Register</Link>
                </li>
                <li>
                  <Link to="/login">Log in</Link>
                </li>
              </>
            )}
          </ul>
        </nav>
        {session.loading ? <p>Checking session.</p> : null}
        {session.error ? (
          <>
            <p>Account status could not be loaded.</p>
            <button type="button" onClick={() => setRetry((value) => value + 1)}>
              Retry
            </button>
          </>
        ) : null}
      </header>
      <Routes>
        <Route path="/" element={<DiscoverPage />} />
        <Route
          path="/register"
          element={
            <RegisterPage
              onAuthenticated={(user) =>
                setSession({ loading: false, error: null, user })
              }
            />
          }
        />
        <Route
          path="/login"
          element={
            <LoginPage
              onAuthenticated={(user) =>
                setSession({ loading: false, error: null, user })
              }
            />
          }
        />
        <Route path="/events/:eventId" element={<EventPage />} />
        <Route path="/venues/:venueId" element={<VenuePage />} />
        <Route path="/artists/:artistId" element={<ArtistPage />} />
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
      <footer>
        <p>
          Event data sourced from{" "}
          <a href="https://ra.co">Resident Advisor</a>.
        </p>
      </footer>
    </>
  );
}
