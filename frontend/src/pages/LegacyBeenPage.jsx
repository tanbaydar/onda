import { Navigate, useLocation } from "react-router-dom";

import { legacyBeenRedirect } from "../profileRoutes.js";


export default function LegacyBeenPage({ session }) {
  const location = useLocation();
  if (session.loading) return <main><p>Checking session…</p></main>;
  return <Navigate to={legacyBeenRedirect(session.user)} replace state={!session.user ? { from: `${location.pathname}${location.search}` } : undefined} />;
}
