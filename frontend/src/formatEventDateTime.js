const WEEKDAYS = [
  "Sunday",
  "Monday",
  "Tuesday",
  "Wednesday",
  "Thursday",
  "Friday",
  "Saturday",
];

const MONTHS = [
  "January",
  "February",
  "March",
  "April",
  "May",
  "June",
  "July",
  "August",
  "September",
  "October",
  "November",
  "December",
];

export function formatEventDateTime(eventDate, startTime) {
  const [year, month, day] = eventDate.split("-").map(Number);
  const weekday = WEEKDAYS[
    new Date(Date.UTC(year, month - 1, day)).getUTCDay()
  ];
  const formattedDate = `${weekday}, ${MONTHS[month - 1]} ${day}, ${year}`;

  if (!startTime) {
    return formattedDate;
  }

  const [hour, minute] = startTime.split(":").map(Number);
  const period = hour >= 12 ? "PM" : "AM";
  const displayHour = hour % 12 || 12;

  return `${formattedDate} at ${displayHour}:${String(minute).padStart(2, "0")} ${period}`;
}

export function formatCompactEventDateTime(eventDate, startTime) {
  const [year, month, day] = eventDate.split("-").map(Number);
  const weekday = WEEKDAYS[new Date(Date.UTC(year, month - 1, day)).getUTCDay()].slice(0, 3);
  const date = `${weekday} ${day} ${MONTHS[month - 1].slice(0, 3)}`;
  if (!startTime) return date;
  const [hour, minute] = startTime.split(":").map(Number);
  return `${date}, ${hour % 12 || 12}:${String(minute).padStart(2, "0")} ${hour >= 12 ? "pm" : "am"}`;
}

export function formatEventIdentityDateTime(eventDate, startTime) {
  const [year, month, day] = eventDate.split("-").map(Number);
  const weekday = WEEKDAYS[new Date(Date.UTC(year, month - 1, day)).getUTCDay()].slice(0, 3);
  const date = `${weekday}, ${MONTHS[month - 1].slice(0, 3)} ${day}, ${year}`;
  if (!startTime) return date;
  const [hour, minute] = startTime.split(":").map(Number);
  return `${date} · ${hour % 12 || 12}:${String(minute).padStart(2, "0")} ${hour >= 12 ? "PM" : "AM"}`;
}
