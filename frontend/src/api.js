export class ApiError extends Error {
  constructor(message, status, data = null) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.data = data;
  }
}

export async function fetchJson(url, options = {}) {
  const response = await fetch(url, {
    credentials: "same-origin",
    ...options,
  });
  const data =
    response.status === 204 ? null : await response.json().catch(() => null);
  if (!response.ok) {
    throw new ApiError(
      `Request failed with status ${response.status}.`,
      response.status,
      data,
    );
  }
  return data;
}

function getCookie(name) {
  const prefix = `${name}=`;
  const cookie = document.cookie
    .split(";")
    .map((value) => value.trim())
    .find((value) => value.startsWith(prefix));
  return cookie ? decodeURIComponent(cookie.slice(prefix.length)) : null;
}

export async function fetchWithCsrf(url, options = {}) {
  if (!getCookie("csrftoken")) {
    await fetchJson("/api/auth/session/");
  }
  const headers = new Headers(options.headers);
  headers.set("X-CSRFToken", getCookie("csrftoken"));
  return fetchJson(url, {...options, headers});
}
