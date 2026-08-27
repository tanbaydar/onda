import { Navigate } from "react-router-dom";

import { legacyBeenRedirect } from "../profileRoutes.js";


export default function LegacyBeenPage({ session }) {
  if (session.loading) return <main><p>Checking session…</p></main>;
  return <Navigate to={legacyBeenRedirect(session.user)} replace />;
}
