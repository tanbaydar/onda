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
