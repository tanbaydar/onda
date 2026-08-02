export function compactLineup(artists, omittedArtistId = null, limit = 2) {
  const ordered = artists.filter((artist) => String(artist.id) !== String(omittedArtistId));
  const names = ordered.slice(0, limit).map((artist) => artist.name);
  const remaining = Math.max(0, ordered.length - names.length);
  return `${names.join(", ")}${remaining ? ` +${remaining}` : ""}`;
}
