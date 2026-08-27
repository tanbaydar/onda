import { useEffect, useState } from "react";
import { Link, Navigate, NavLink, Route, Routes, useLocation, useNavigate } from "react-router-dom";

import { fetchJson, fetchWithCsrf } from "./api.js";
import AccountMenu from "./components/AccountMenu.jsx";
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
import SystemStatePage from "./components/SystemStatePage.jsx";
import { GUEST_DISCOVER, landingPathForSession } from "./landing.js";
import { primaryNavigationItems } from "./primaryNavigation.js";

function LandingPage({ session }) {
  const location = useLocation();
  const destination = landingPathForSession(session, location.search);
  if (!destination) return <main><p>Checking session…</p></main>;
  return <Navigate to={destination} replace />;
}

function NotFoundPage() {
  return (
    <SystemStatePage title="Page not found">
      <p>The page you requested does not exist.</p>
    </SystemStatePage>
  );
}

export default function App() {
  const navigate = useNavigate();
  const location = useLocation();
  const [retry, setRetry] = useState(0);
  const [session, setSession] = useState({
    loading: true,
    error: null,
    user: null,
  });
  const [accountProfile, setAccountProfile] = useState(null);
  const [logoutState, setLogoutState] = useState({ pending: false, error: null });

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

  useEffect(() => {
    if (!session.user) {
      setAccountProfile(null);
      return undefined;
    }
    const controller = new AbortController();
    fetchJson(`/api/users/${encodeURIComponent(session.user.username)}/`, { signal: controller.signal, cache: "no-store" })
      .then((data) => setAccountProfile(data.profile ?? null))
      .catch((error) => {
        if (error.name !== "AbortError") setAccountProfile(null);
      });
    return () => controller.abort();
  }, [session.user?.username]);

  async function handleLogout() {
    if (logoutState.pending) return;
    setLogoutState({ pending: true, error: null });
    try {
      await fetchWithCsrf("/api/auth/logout/", {
        method: "POST",
        body: JSON.stringify({}),
        headers: { "Content-Type": "application/json" },
      });
      setSession({ loading: false, error: null, user: null });
      setAccountProfile(null);
      setLogoutState({ pending: false, error: null });
      navigate(GUEST_DISCOVER, { replace: true });
    } catch (error) {
      setLogoutState({ pending: false, error });
    }
  }

  const isAuthRoute = ["/register", "/login", "/verify-email", "/reset-password", "/reset-password/confirm"].includes(location.pathname);

  return (
    <>
      <header className="site-header">
        <Link className="site-wordmark" to="/" aria-label="Onda home">
          <img src="/logo.png" alt="Onda" />
        </Link>
        <nav aria-label="Primary navigation">
          <ul>
            {primaryNavigationItems(session.user).map((item) => <li key={item.label}><NavLink className="navigation-action" to={item.to}>{item.label}</NavLink></li>)}
          </ul>
        </nav>
        <section aria-label="Account controls">
          {session.user ? (
            <AccountMenu user={accountProfile ?? session.user} onLogout={handleLogout} logoutState={logoutState} />
          ) : (
            <p className="guest-auth-controls"><Link className="guest-register account-action" to="/register">Register</Link><Link className="account-action" to="/login">Log in</Link></p>
          )}
        </section>
      </header>
      {session.error ? (
        <div className="session-error-slot" role="alert">
          <span>Account status could not be loaded.</span>
          <button className="recovery-action" type="button" onClick={() => setRetry((value) => value + 1)}>Retry</button>
        </div>
      ) : null}
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
        <Route path="/verify-email" element={<VerifyEmailPage email={session.user?.email} />} />
        <Route path="/reset-password" element={<PasswordResetRequestPage />} />
        <Route path="/reset-password/confirm" element={<PasswordResetFormPage />} />
        <Route
          path="/e/:eventKey"
          element={
            <EventPage
              user={session.user}
              sessionReady={!session.loading}
              onAuthenticationRequired={() =>
                setSession({ loading: false, error: null, user: null })
              }
            />
          }
        />
        <Route path="/events/:eventKey" element={<EventPage user={session.user} sessionReady={!session.loading} onAuthenticationRequired={() => setSession({ loading: false, error: null, user: null })} />} />
        <Route path="/been" element={<LegacyBeenPage session={session} />} />
        <Route path="/u/:username" element={<ProfilePage session={session} tab="been" />} />
        <Route path="/u/:username/reviews" element={<ProfilePage session={session} tab="reviews" />} />
        <Route path="/settings/profile" element={<EditProfilePage session={session} onProfileUpdated={setAccountProfile} />} />
        <Route path="/activity" element={<ActivityPage session={session} />} />
        <Route path="/v/:venueKey" element={<VenuePage user={session.user} sessionReady={!session.loading} />} />
        <Route path="/venues/:venueKey" element={<VenuePage user={session.user} sessionReady={!session.loading} />} />
        <Route path="/a/:artistKey" element={<ArtistPage user={session.user} sessionReady={!session.loading} />} />
        <Route path="/artists/:artistKey" element={<ArtistPage user={session.user} sessionReady={!session.loading} />} />
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
      {!isAuthRoute ? <footer>
        <p>
          Event data sourced from{" "}
          <a href="https://ra.co">Resident Advisor</a>.
        </p>
      </footer> : null}
    </>
  );
}
