[Onda](../README.md) / [Documentation](README.md) / API reference

# API reference

> **For** engineers who call the API. **Use** this page as a lookup table.

The API serves the React app of Onda on the same origin. It has 46 routes.
It is not a public API. It has no API keys, no version in the path, and no promise to third-party clients.
The examples come from a local run on 2026-11-27 with synthetic data.

## In brief

- All routes start with `/api/`. Bodies are JSON.
- A session cookie identifies the person. Each `POST`, `PUT` and `DELETE` request must send the header `X-CSRFToken`.
- `PUT` creates or updates: `201` the first time, `200` after that.
- `400` is an incorrect shape. `409` is a valid request in an incorrect state. `404` is unknown, hidden or not visible.
- Lists use page numbers. Home and notifications use a cursor.

## Contents

- [Conventions](#conventions): [session](#session-and-csrf-token), [status codes](#status-codes), [errors](#errors), [pagination](#pagination)
- [Routes](#routes): [account](#session-and-account), [catalog](#catalog-and-search), [Been](#been-ratings-and-reviews), [Will Be There](#will-be-there), [favorites](#favorites), [profiles](#profiles-and-follows), [Home](#home-and-notifications)
- [Objects](#objects): [event](#event), [Home item](#home-item), [profile](#profile), [notification](#notification)

## Conventions

### Session and CSRF token

Do these steps to make the first write:

1. Send `GET /api/auth/session/`. The response sets the cookie `csrftoken`.
2. Send `POST /api/auth/login/` with the header `X-CSRFToken`. Its value is the value of the cookie.
3. Send the same header with each `POST`, `PUT` and `DELETE` request.

```json
{"authenticated": false, "user": null}
```

```json
{
  "authenticated": true,
  "user": {
    "id": 5,
    "email": "ivy@example.test",
    "username": "ivy",
    "display_name": "Ivy",
    "avatar": null,
    "is_private": false
  }
}
```

| Cookie | Properties |
|---|---|
| `sessionid` | `HttpOnly`, `SameSite=Lax`, 7 days. `Secure` in production |
| `csrftoken` | `SameSite=Lax`. Script can read it, because the app must copy it into the header. `Secure` in production |

Only the owner of an account gets the `email` field. No other route returns an email address.

**Email verification.** Production turns this rule on unless the operator turns it off.
With the rule on, an account with no verified email address gets these effects:

- The session object has the field `email_verified`.
- Each route that changes product data returns `403`. `GET /api/me/home/` also returns `403`.
- Private content treats the account as a visitor with no session.

### Status codes

| Status | Meaning in all routes |
|---|---|
| `200` | Read, update, or a `PUT` that found the same state |
| `201` | A new row |
| `204` | Success with no body |
| `400` | The shape is incorrect: bad JSON, a bad field, a bad query parameter or a bad cursor |
| `401` | No session, or incorrect login data |
| `403` | Private content, an account with no verified email address, or no CSRF token |
| `404` | Unknown, hidden or not visible. A page number out of range |
| `405` | The route does not accept this method |
| `409` | The request is valid, and the state does not accept it |
| `429` | Too many attempts |

### Errors

An error body has one of four forms.

| Form | Where |
|---|---|
| `{"errors": {"<field>": ["<message>"]}}` | Validation, session, verification and most conflicts |
| `{"error": "<message>"}` | The catalog list, a page out of range, a row that is absent, and conflicts of like and follow |
| HTML page of Django | `404` for an unknown ID, a hidden event or an unknown username. `403` for a missing CSRF token |
| Empty body | `204`, and `405` with the header `Allow` |

A client must use the status code, not the body, to make a decision.
One fault has two forms: a bad cursor gives `errors` on Home and on search, and `error` on notifications.

A `429` from a rate limit has the header `Retry-After`. The `429` for a second code in 60 seconds has no such header. It has the JSON field `retry_after`.

### Pagination

| Type | Routes | Parameters | Response |
|---|---|---|---|
| Page number | Catalog lists, profile lists, reviews, plans, follow requests | `page`, `page_size` | The object `pagination`. A page out of range gives `404` |
| Cursor | Home, notifications | `cursor`, `page_size` | `next_cursor`, or `null` on the last page. A bad cursor gives `400` |
| Offset | Search with one scope | `cursor` is a number from 0 to 10,000 | `next_cursor` as text, or `null` |

The default `page_size` is 20 and the maximum is 100.
Two lists are the exception: event reviews and the circle of an event have a default of 10 and a maximum of 50.

```json
{"page": 1, "page_size": 20, "total_results": 329, "total_pages": 17, "next_page": 2, "previous_page": null}
```

A cursor is text that the client sends back unchanged. A client must not read it or build it.

### Times

| Field | Format | Zone |
|---|---|---|
| `created_at`, `rated_at`, `published_at`, `activity_at`, `read_at` | `2026-11-27T02:59:30.257272Z` | UTC |
| `event_date` | `2026-11-07` | The date at the venue |
| `start_time` | `22:00:00` or `null` | The time at the venue |

## Routes

The column "Session" shows if the route must have a session.
Each route that must have a session can return `401`, and `403` for an account with no verified email address.
The column "Other" lists the other statuses.

### Session and account

| Method | Path | Session | Success | Other |
|---|---|---|---|---|
| `GET` | `/api/auth/session/` | No | `200` | |
| `POST` | `/api/auth/register/` | No | `201` | `400`, `429` |
| `POST` | `/api/auth/login/` | No | `200` | `400`, `401`, `429` |
| `POST` | `/api/auth/logout/` | No | `204` | |
| `POST` | `/api/auth/verification/request/` | Yes | `200` | `429` |
| `POST` | `/api/auth/verification/confirm/` | Yes | `200` | `400` |
| `POST` | `/api/auth/password-reset/request/` | No | `200` | `400`, `429` |
| `POST` | `/api/auth/password-reset/confirm/` | No | `200` | `400`, `429` |

- The login field `email` accepts an email address or a username.
- A password has a minimum of 12 characters.
- A code has 6 digits. It expires after 15 minutes. It accepts 5 incorrect attempts. A new code is possible after 60 seconds.
- The reset request returns the same body for a known address and for an unknown address.
- A successful reset deletes all sessions of the account.

| Limit | Value |
|---|---|
| Login, for one client address | 10 in 5 minutes |
| Login, for one account | 50 in 1 hour |
| Register, for one client address | 20 in 1 hour |
| Reset request, for one client address and for one account | 10 and 5 in 1 hour |
| Avatar upload, for one account | 20 in 1 hour |

While the login limit is active, a correct password also gets `429`.

### Catalog and search

A session is not necessary for the routes in this group. With a session, a response can have more fields about the viewer.

| Method | Path | Success | Other | Parameters |
|---|---|---|---|---|
| `GET` | `/api/cities/` | `200` | | |
| `GET` | `/api/events/` | `200` | `400`, `404` | `when` is `upcoming` or `past`. Exactly one of `city_id`, `venue_id`, `artist_id` |
| `GET` | `/api/events/{id}/` | `200` | `404` | |
| `GET` | `/api/venues/{id}/` | `200` | `404` | |
| `GET` | `/api/artists/{id}/` | `200` | `404` | |
| `GET` | `/api/search/` | `200` | `400` | `q` with 1 to 100 characters. `scope` is `all`, `events`, `artists`, `venues` or `people`. `city_id` |

- The order of upcoming events is `(event_date, id)`. The order of past events is the opposite.
- A past list adds `rating_summary` to each event.
- An old alias ID of an event returns the first event row.
- `scope=all` returns a maximum of 5 results for each group. One scope returns 20 results for each page.
- Search does not look at email addresses.

### Been, ratings and reviews

| Method | Path | Session | Success | Other |
|---|---|---|---|---|
| `PUT` | `/api/events/{id}/been/` | Yes | `201`, `200` | `400`, `404`, `409` the event did not start |
| `DELETE` | `/api/events/{id}/been/` | Yes | `204` | `404` no entry |
| `DELETE` | `/api/events/{id}/been/rating/` | Yes | `200` | `404` no entry |
| `PUT` | `/api/events/{id}/been/review/` | Yes | `201`, `200` | `400`, `404` no entry, `409` no rating |
| `DELETE` | `/api/events/{id}/been/review/` | Yes | `204` | `404` no review |
| `GET` | `/api/events/{id}/reviews/` | No | `200` | `400`, `404` |
| `GET` | `/api/events/{id}/circle/` | Yes | `200` | `400`, `404` |
| `POST` | `/api/reviews/{id}/like/` | Yes | `201` | `404`, `409` second like or own review |
| `DELETE` | `/api/reviews/{id}/like/` | Yes | `204` | `404` no like |
| `GET` | `/api/me/been/` | Yes | `200` | `400`, `404` |

```http
PUT /api/events/1/been/
Content-Type: application/json
X-CSRFToken: <value of the csrftoken cookie>

{"rating": 4.5}
```

```json
{
  "entry": {
    "id": 1,
    "rating": 4.5,
    "rated_at": "2026-11-27T02:59:30.257272Z",
    "created_at": "2026-11-27T02:59:30.257644Z",
    "review": null
  }
}
```

| Request | Status | Body |
|---|---|---|
| `{"rating": 4.3}` | `400` | `{"errors": {"rating": ["Rating must be a half-star value from 0.5 to 5.0."]}}` |
| `{"rating": "4.5"}` | `400` | The same body. The value must be a JSON number |
| An event that did not start | `409` | `{"errors": {"event": ["This event can be added to Been once its scheduled start arrives."]}}` |
| A review with no rating | `409` | `{"errors": {"rating": ["A rating is required to publish a review."]}}` |

- A review body has 1 to 1,000 characters after the removal of spaces at the two ends.
- `DELETE …/been/rating/` keeps the entry. It deletes the review and the likes of the review, and it reports the two.

  ```json
  {"entry": {"id": 1, "rating": null, "rated_at": null, "created_at": "2026-11-27T02:59:30.257644Z", "review": null},
   "cascade": {"review_deleted": true, "review_likes_deleted": 1}}
  ```

- `GET …/reviews/` shows authors with a public profile only. It does not show the review of the viewer. `sort` is `most_liked` or `newest`.
- `GET …/circle/` shows the ratings and the reviews of the followees of the viewer, with the average of the circle.

### Will Be There

| Method | Path | Session | Success | Other |
|---|---|---|---|---|
| `PUT` | `/api/events/{id}/will-be-there/` | Yes | `201`, `200` | `404`, `409` the day of the event is over |
| `DELETE` | `/api/events/{id}/will-be-there/` | Yes | `204` each time | `404` unknown event |
| `GET` | `/api/events/{id}/will-be-there/public/` | No | `200` | `400`, `404` |
| `GET` | `/api/events/{id}/will-be-there/circle/` | Yes | `200` | `400`, `404` |

A new mark writes one notification for each approved follower.

### Favorites

| Method | Path | Session | Success | Other |
|---|---|---|---|---|
| `PUT` | `/api/events/{id}/favorite/` | Yes | `201`, `200` | `404`, `409` the fourth favorite |
| `PUT` | `/api/artists/{id}/favorite/` | Yes | `201`, `200` | `404`, `409` |
| `PUT` | `/api/venues/{id}/favorite/` | Yes | `201`, `200` | `404`, `409` |
| `DELETE` | The same three paths | Yes | `204` each time | `404` unknown target |
| `GET` | `/api/me/favorite-venues/` | Yes | `200` | `400`, `404` |
| `GET` | `/api/users/{username}/favorites/` | No | `200` | `403`, `404` |

A person has a maximum of 3 favorites of each type.

### Profiles and follows

| Method | Path | Session | Success | Other |
|---|---|---|---|---|
| `GET` | `/api/users/{username}/` | No | `200` | `404` |
| `GET` | `/api/users/{username}/been/` | No | `200` | `400`, `403`, `404` |
| `GET` | `/api/users/{username}/reviews/` | No | `200` | `400`, `403`, `404` |
| `GET` | `/api/users/{username}/stats/` | No | `200` | `403`, `404` |
| `GET` | `/api/users/{username}/followers/` | No | `200` | `400`, `404` |
| `GET` | `/api/users/{username}/following/` | No | `200` | `400`, `404` |
| `POST` | `/api/users/{user_id}/follow/` | Yes | `201` | `404`, `409` second follow or follow to yourself |
| `DELETE` | `/api/users/{user_id}/follow/` | Yes | `204` | `404` no follow |
| `GET` | `/api/me/follow-requests/` | Yes | `200` | `400`, `404` |
| `POST` | `/api/me/follow-requests/{follower_id}/accept/` | Yes | `200` | `404` no open request |
| `POST` | `/api/me/follow-requests/{follower_id}/decline/` | Yes | `204` | `404` no open request |
| `PUT` | `/api/me/privacy/` | Yes | `200` | `400` |
| `PUT` | `/api/me/profile/` | Yes | `200` | `400` |
| `POST` | `/api/me/profile/avatar/` | Yes | `200` | `400`, `429` |
| `DELETE` | `/api/me/profile/avatar/` | Yes | `200` | |

- The follow routes use the numeric ID of the person. The profile routes use the username.
- A follow to a public profile is `approved` immediately. A follow to a private profile is `pending`.
- `sort` for profile reviews is `newest`, `most_liked`, `oldest` or `longest`.
- `PUT /api/me/profile/` must send `display_name`, `bio` and `home_city_id`. It refuses the key `avatar`.
- An avatar is a JPEG, PNG or WebP file with a maximum of 2 MB and 4,096 pixels on each side. Onda stores a new 512 by 512 JPEG.
- `PUT /api/me/privacy/` with `{"is_private": false}` approves all open requests in the same transaction. The response gives the count.

**What a private profile shows to a person who is not an approved follower.**

| Route | Result |
|---|---|
| `/api/users/{username}/` | `200` with `"access": "stub"`. Name, avatar, bio, home city and the two counts |
| `/followers/`, `/following/` | `200` with the full list. The connections of a profile are public |
| `/been/`, `/reviews/`, `/favorites/`, `/stats/` | `403` with `{"errors": {"profile": ["This profile's content is private."]}}` |

### Home and notifications

| Method | Path | Session | Success | Other |
|---|---|---|---|---|
| `GET` | `/api/me/home/` | Yes | `200` | `400` |
| `GET` | `/api/me/notifications/` | Yes | `200` | `400` |
| `POST` | `/api/me/notifications/{id}/read/` | Yes | `200` | `404` |
| `POST` | `/api/me/notifications/read-all/` | Yes | `200` | |

The two lists accept `cursor` and `page_size`. They return `results` and `next_cursor`.
A read of the list does not change the read state of a notification.

## Objects

### Event

`GET /api/events/{id}/`. The three `viewer_` fields come only with a session.
The rating distribution has 10 buckets, one for each half step. This example shows one.

```json
{
  "id": 1,
  "title": "Example Night One",
  "event_date": "2026-11-07",
  "start_time": "22:00:00",
  "cover_image_url": null,
  "venue": {"id": 1, "name": "Example Venue",
            "city": {"id": 1, "name": "New York City", "timezone": "America/New_York"}},
  "artists": [{"id": 1, "name": "Example Artist One", "position": 1},
              {"id": 2, "name": "Example Artist Two", "position": 2}],
  "rating_summary": {"state": "available", "count": 1, "average": 4.0},
  "rating_distribution": {"state": "available",
                          "buckets": [{"rating": 4.0, "count": 1, "relative_value": 1.0}]},
  "been": {"loggable": true, "unavailable_reason": null},
  "will_be_there_summary": {"active_count": 0},
  "viewer_entry": {"id": 1, "rating": 4.0, "rated_at": "2026-11-27T02:59:30.257272Z",
                   "created_at": "2026-11-27T02:59:30.257644Z", "review": null},
  "viewer_will_be_there": {"is_marked": false, "was_marked": false, "can_mark": false,
                           "unavailable_reason": "Will Be There expired at the end of the event's local date."},
  "viewer_favorite": {"is_favorite": false, "added_at": null}
}
```

- `rating_summary.state` is `available` or `not_enough_ratings`. One rating is sufficient for an average.
- The average includes the ratings of private profiles, with no name.
- The response does not contain the source ID or the status of the event.

### Home item

```json
{
  "type": "review_like",
  "activity_at": "2026-11-27T03:00:18.745368Z",
  "actor": {"id": 1, "username": "maya", "display_name": "Maya", "avatar": null},
  "target": {
    "event": {"id": 2, "title": "Example Night Two", "event_date": "2026-11-17", "start_time": null,
              "cover_image_url": null, "venue": {"name": "Example Venue", "city": {"name": "New York City"}}},
    "review": {"id": 2, "body": "Slow start, strong finish.", "rating": 3.5,
               "author": {"id": 4, "username": "sam", "display_name": "Sam"}}
  },
  "context": null
}
```

| `type` | `target` | `context` |
|---|---|---|
| `will_be_there`, `favorite_event`, `been` | `event` | `null` |
| `rated_been`, `review` | `event` | `rating`, and `review` with `id` and `body`, or `null` |
| `review_like` | `event` and `review` | `null` |
| `favorite_artist` | `artist` with `id`, `name`, `image_url` | `null` |

### Profile

`GET /api/users/{username}/`.

```json
{
  "profile": {"id": 1, "username": "maya", "display_name": "Maya", "avatar": null, "bio": null,
              "follower_count": 2, "following_count": 0, "home_city": null},
  "access": "full",
  "relationship": {"outgoing_status": "approved", "follows_you": false,
                   "can_follow": false, "can_unfollow": true, "follow_action": null}
}
```

- `access` is `owner`, `full` or `stub`.
- The owner gets `account` with `is_private`, and no `relationship`.
- A visitor with no session gets no `relationship`.
- `follow_action` is `follow`, `request` or `null`.

### Notification

| Field | Value |
|---|---|
| `type` | `review_like`, `follow`, `follow_request`, `request_accepted` or `will_be_there` |
| `actor` | `id`, `username`, `display_name`, `avatar` |
| `review` | `id`, `event_id`, `event_title`, or `null`. Only for `review_like` |
| `event` | `id`, `title`, or `null`. Only for `will_be_there` |
| `created_at`, `read_at` | Times. `read_at` is `null` before the read |

## Security rules of the API

- The browser sends cookies to the same origin only. A request that changes state must have the CSRF token.
- Production redirects HTTP to HTTPS. It sets HSTS, a content security policy, and the headers `X-Content-Type-Options: nosniff` and `X-Frame-Options: DENY`.
- Caddy limits a request body to 3 MB before Django reads it.
- Onda stores a rate limit key as an HMAC. It does not store the address of the client or the email address in that table.
- Onda stores a code as an HMAC, and it compares codes in constant time.
- Privacy filters are in the queries. A private row does not go to the React app.
- An avatar goes through a decode and a new encode. Onda does not trust the file name or the type that the client gives.

## Source files

| Subject | File |
|---|---|
| Routes | [`backend/config/urls.py`](../backend/config/urls.py), [`backend/users/urls.py`](../backend/users/urls.py), [`backend/users/been_urls.py`](../backend/users/been_urls.py) |
| Catalog views and search | [`backend/catalog/views.py`](../backend/catalog/views.py), [`backend/catalog/search.py`](../backend/catalog/search.py) |
| Product views | [`backend/users/views.py`](../backend/users/views.py) |
| Service functions | [`backend/users/services.py`](../backend/users/services.py), [`backend/users/auth_services.py`](../backend/users/auth_services.py) |
| Rate limits | [`backend/users/rate_limits.py`](../backend/users/rate_limits.py), `ONDA_AUTH_RATE_LIMITS` in [`backend/config/settings.py`](../backend/config/settings.py) |
| The fetch wrapper of the app | [`frontend/src/api.js`](../frontend/src/api.js) |
