export function appendUniqueEvents(current, incoming) {
  const seen = new Set(current.map((event) => event.id));
  return [...current, ...incoming.filter((event) => {
    if (seen.has(event.id)) return false;
    seen.add(event.id);
    return true;
  })];
}
