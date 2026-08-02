import { useEffect, useState } from "react";
import { Link, Navigate, NavLink, Route, Routes, useLocation, useNavigate } from "react-router-dom";

import { fetchJson, fetchWithCsrf } from "./api.js";
import ArtistPage from "./pages/ArtistPage.jsx";
import ActivityPage from "./pages/ActivityPage.jsx";
import DiscoverPage from "./pages/DiscoverPage.jsx";
import EventPage from "./pages/EventPage.jsx";
import EditProfilePage from "./pages/EditProfilePage.jsx";
import HomePage from "./pages/HomePage.jsx";
import LoginPage from "./pages/LoginPage.jsx";
import PasswordResetFormPage from "./pages/PasswordResetFormPage.jsx";
import PasswordResetRequestPage from "./pages/PasswordResetRequestPage.jsx";
import LegacyBeenPage from "./pages/LegacyBeenPage.jsx";
import ProfilePage from "./pages/ProfilePage.jsx";
import RegisterPage from "./pages/RegisterPage.jsx";
import VenuePage from "./pages/VenuePage.jsx";
import VerifyEmailPage from "./pages/VerifyEmailPage.jsx";
import SearchPage from "./pages/SearchPage.jsx";
import { GUEST_DISCOVER, landingPath } from "./landing.js";
import { primaryNavigationItems } from "./primaryNavigation.js";

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
            {primaryNavigationItems(session.user).map((item) => <li key={item.label}><NavLink to={item.to}>{item.label}</NavLink></li>)}
          </ul>
        </nav>
        <section aria-label="Account controls">
          {session.user ? (
            <>
              <p>Account: @{session.user.username}</p>
              <button type="button" onClick={handleLogout}>Log out</button>
            </>
          ) : (
            <p><Link to="/register">Register</Link>{" · "}<Link to="/login">Log in</Link></p>
          )}
        </section>
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
        <Route path="/search" element={<SearchPage />} />
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
        <Route path="/verify-email" element={<VerifyEmailPage />} />
        <Route path="/reset-password" element={<PasswordResetRequestPage />} />
        <Route path="/reset-password/confirm" element={<PasswordResetFormPage />} />
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
        <Route path="/been" element={<LegacyBeenPage session={session} />} />
        <Route path="/u/:username" element={<ProfilePage session={session} tab="been" />} />
        <Route path="/u/:username/reviews" element={<ProfilePage session={session} tab="reviews" />} />
        <Route path="/settings/profile" element={<EditProfilePage session={session} />} />
        <Route path="/activity" element={<ActivityPage session={session} />} />
        <Route path="/venues/:venueId" element={<VenuePage user={session.user} />} />
        <Route path="/artists/:artistId" element={<ArtistPage user={session.user} />} />
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
