import { Link, Route, Routes } from "react-router-dom";

import ArtistPage from "./pages/ArtistPage.jsx";
import DiscoverPage from "./pages/DiscoverPage.jsx";
import EventPage from "./pages/EventPage.jsx";
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
  return (
    <>
      <header>
        <p>Danced</p>
        <nav aria-label="Primary navigation">
          <ul>
            <li>
              <Link to="/">Discover</Link>
            </li>
          </ul>
        </nav>
      </header>
      <Routes>
        <Route path="/" element={<DiscoverPage />} />
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
