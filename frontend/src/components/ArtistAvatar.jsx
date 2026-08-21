import { useEffect, useState } from "react";

export default function ArtistAvatar({ artist, small = false, className = "", loading }) {
  const [failedSource, setFailedSource] = useState(null);
  const source = artist?.image_url ?? null;
  const classes = `artist-avatar${small ? " artist-avatar-small" : ""}${className ? ` ${className}` : ""}`;

  useEffect(() => setFailedSource(null), [source]);

  if (source && failedSource !== source) {
    return (
      <img
        className={classes}
        src={source}
        alt={`${artist.name} artist portrait`}
        loading={loading ?? (small ? "lazy" : "eager")}
        referrerPolicy="no-referrer"
        onError={() => setFailedSource(source)}
      />
    );
  }

  return (
    <span className={`${classes} artist-avatar-placeholder`} role="img" aria-label={`Placeholder portrait for ${artist?.name ?? "artist"}`}>
      <span className="artist-avatar-head" aria-hidden="true" />
      <span className="artist-avatar-shoulders" aria-hidden="true" />
    </span>
  );
}
