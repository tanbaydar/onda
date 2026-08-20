export function venueLocalDate(timeZone, now = new Date()) {
  const parts = new Intl.DateTimeFormat("en-US", {
    timeZone,
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  }).formatToParts(now);
  const values = Object.fromEntries(parts.map(({ type, value }) => [type, value]));
  return `${values.year}-${values.month}-${values.day}`;
}

export function eventCanShowTicketLink(event, now = new Date()) {
  return Boolean(
    event.is_ticketed === true &&
      event.ticket_url &&
      event.event_date >= venueLocalDate(event.venue.city.timezone, now),
  );
}

export function eventIsPast(event, now = new Date()) {
  const parts = new Intl.DateTimeFormat("en-US", {
    timeZone: event.venue.city.timezone,
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hourCycle: "h23",
  }).formatToParts(now);
  const values = Object.fromEntries(parts.map(({ type, value }) => [type, value]));
  const localWallTime = `${values.year}-${values.month}-${values.day}T${values.hour}:${values.minute}:${values.second}`;
  return localWallTime >= `${event.event_date}T${event.start_time || "00:00:00"}`;
}
