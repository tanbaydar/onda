const TIMESTAMP_FORMATTER = new Intl.DateTimeFormat("en-US", {
  month: "short",
  day: "numeric",
  year: "numeric",
  timeZone: "UTC",
});


export function formatTimestamp(value) {
  return TIMESTAMP_FORMATTER.format(new Date(value));
}
