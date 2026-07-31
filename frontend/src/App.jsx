import { useEffect, useState } from "react";
import { Link, Navigate, Route, Routes, useLocation, useNavigate } from "react-router-dom";

import { fetchJson, fetchWithCsrf } from "./api.js";
import ArtistPage from "./pages/ArtistPage.jsx";
import ActivityPage from "./pages/ActivityPage.jsx";
import BeenPage from "./pages/BeenPage.jsx";
import DiscoverPage from "./pages/DiscoverPage.jsx";
import EventPage from "./pages/EventPage.jsx";
import HomePage from "./pages/HomePage.jsx";
import LoginPage from "./pages/LoginPage.jsx";
import RegisterPage from "./pages/RegisterPage.jsx";
import VenuePage from "./pages/VenuePage.jsx";
import { GUEST_DISCOVER, landingPath } from "./landing.js";

function LandingPage({ session }) {
  const location = useLocation();
  if (session.loading) return <main><p>Checking session.</p></main>;
  if (session.error) return <main><p>Landing page could not be resolved.</p></main>;
  return <Navigate to={landingPath(session.user, location.search)} replace />;
}

function NotFoundPage() {
  return (
    <main>
      <h1>Page not found</h1>
      <p>The page you requested does not exist.</p>
      <p>
        <Link to="/discover">Return to Discover</Link>
      </p>
    </main>
  );
}

export default function App() {
  const location = useLocation();
  const navigate = useNavigate();
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
      if (location.pathname === "/home") navigate(GUEST_DISCOVER, { replace: true });
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
            {session.user ? <li><Link to="/home">Home</Link></li> : null}
            <li><Link to="/discover">Discover</Link></li>
            {session.user ? (
              <>
                <li>
                  <Link to="/activity">Activity</Link>
                </li>
                <li>Signed in as {session.user.username}</li>
                <li>
                  <Link to="/been">Been</Link>
                </li>
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
        <Route path="/" element={<LandingPage session={session} />} />
        <Route path="/discover" element={<DiscoverPage />} />
        <Route path="/home" element={<HomePage session={session} />} />
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
        <Route
          path="/events/:eventId"
          element={
            <EventPage
              user={session.user}
              onAuthenticationRequired={() =>
                setSession({ loading: false, error: null, user: null })
              }
            />
          }
        />
        <Route path="/been" element={<BeenPage session={session} />} />
        <Route path="/activity" element={<ActivityPage session={session} />} />
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
