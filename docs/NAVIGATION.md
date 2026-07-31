# Danced Navigation Contract

> Status: binding product-navigation contract
>
> Authority: derived from PRODUCT_QA_SPEC Q127, Q135–141, Q151–152,
> Q179, and Q201–203, including the appended amendment to Q136.
>
> Scope: primary navigation positions, landing behavior, interim navigation
> elements, and the absorption of temporary navigation into the final skeleton.

## Purpose

Danced has exactly five primary destination positions:

1. Home
2. Discover
3. Search
4. Activity
5. Profile

This document prevents the primary navigation from growing one destination at a
time as features are implemented.

A route, screen, or useful feature is not automatically entitled to a primary
navigation position. Contextual resources such as events, artists, venues, public
profiles, reviews, and Been tabs remain reachable through the five-destination
information architecture.

Any currently rendered navigation item outside the five positions is temporary or
an authentication control. Its final owner and removal point are declared below.

## Final primary-navigation skeleton

| Order | Destination | Final route | Owning specification | Current state | Delivery slice |
|---:|---|---|---|---|---|
| 1 | Home | `/home` | Q151–153, Q202–203 | Not implemented | Home/feed slice, after the required follows and feed-activity foundations exist |
| 2 | Discover | `/discover` | Q127, Q152, Q201 | Implemented at interim route `/` | Existing; moved to `/discover` by the Home slice when `/` becomes the landing resolver |
| 3 | Search | `/search` | Q127, Q142, Q151–152 | Not implemented | Global Search slice |
| 4 | Activity | `/activity` | Q151–152, Q179–180 | Not implemented | Notifications/Activity slice |
| 5 | Profile | `/u/{username}` | Q127, Q135–141, Q151–152 | Not implemented; `/been` is an interim fragment | Profile slice |

The order is fixed. Visual treatments may change, but no implementation may reorder
the five positions without an approved product-spec amendment.

Unimplemented destinations do not require empty placeholder screens or dead links.
They enter the rendered navigation when their consuming slice delivers a real
screen. Their eventual position is nevertheless reserved by this contract.

## Destination ownership

### 1. Home

Final route:

```text
/home
```

Home is the signed-in social feed. It contains followed-user activity and is not an
event-discovery screen.

Home is meaningful only to authenticated users. It does not appear in guest
navigation.

Home becomes the signed-in landing destination in the same slice that delivers the
real Home feed. No empty Home stub should be introduced merely to satisfy the final
navigation order.

### 2. Discover

Final route:

```text
/discover
```

Interim route:

```text
/
```

Discover owns event browsing and city-scoped discovery. It is meaningful to guests
and authenticated users.

Discover currently occupies `/`. That remains valid until Home exists. The Home
slice performs the coordinated transition:

1. move the Discover screen to `/discover`;
2. make `/` an authentication-aware landing resolver;
3. route guests from `/` to Discover;
4. route eligible signed-in users from `/` to Home;
5. update every existing Discover and city-filter link without changing the
   shareable `city_id` query contract.

After that transition, city-filtered Discover URLs use:

```text
/discover?city_id={id}
```

The Home slice must preserve backward compatibility for old `/?city_id={id}` links,
either by redirecting them to `/discover?city_id={id}` or by another explicitly
tested compatibility rule. It must not silently discard a shared city filter.

The already-authorized Slice 2.5 **Recent events** section is a content addition
inside Discover. It conforms to this contract and has no primary-navigation impact.

### 3. Search

Final route:

```text
/search
```

Search owns grouped global results for:

- events;
- artists;
- venues;
- users.

Search is meaningful to guests and authenticated users. Q127 grants guests both
search and discovery, so Search appears in guest navigation when implemented.

Event, artist, venue, and public-profile pages remain contextual resources reached
through Search, Discover, and links. They do not become additional primary
destinations.

### 4. Activity

Final route:

```text
/activity
```

Activity contains notifications concerning the current user:

- likes;
- follows;
- follow requests;
- follow-request acceptances;
- other notification types explicitly added to the product specification.

Activity does not contain followed-user feed activity; that belongs to Home.
Activity is meaningful only to authenticated users and does not appear in guest
navigation.

### 5. Profile

Canonical public profile route:

```text
/u/{username}
```

Profile uses a dedicated `/u/` namespace rather than `/{username}`. This avoids
permanent collisions between usernames and static application routes such as
`/home`, `/discover`, `/search`, `/activity`, `/register`, `/login`, `/events`,
`/venues`, and `/artists`.

The `/u/` namespace also prevents future top-level routes from forcing a reserved
username expansion or breaking previously issued profile URLs.

The authenticated user's Profile destination links to:

```text
/u/{current_username}
```

Other users' public profiles use the same route and are reached through Search,
contextual links, follows, reviews, feeds, or Activity. They are not separate primary
destinations.

#### Profile tabs

Been is the default profile tab:

```text
/u/{username}
```

Reviews has a path route:

```text
/u/{username}/reviews
```

Path routing is preferred over a query parameter because Been and Reviews are
distinct, shareable profile surfaces with independent ordering and later pagination
behavior. A path also avoids treating the selected profile surface as disposable
filter state.

The default Been tab contains every Been attendance entry, including an entry whose
rating was removed. The later Q186 lifecycle ruling governs over Q136's earlier
phrase “all rated events.” A preserved unrated attendance entry must not disappear
from its owner's profile.

Profile eventually owns:

- Been;
- Reviews;
- favorite events;
- favorite artists;
- profile statistics;
- the distribution of ratings the user has given;
- follow/follower relationships;
- account-privacy-aware public presentation.

Settings and account actions may be reached from the Profile position, but they do
not become a sixth primary destination.

## Landing rules

### Guest landing

A signed-out guest who opens `/` lands on Discover, per Q201.

Before Home exists, this is implemented directly because Discover itself occupies
`/`.

After Home exists, `/` becomes an authentication-aware landing resolver and sends
the guest to:

```text
/discover
```

Guests are never sent to Home or Activity.

### Signed-in landing before Home exists

Until the Home slice delivers a real Home feed, signed-in users land on Discover.

This applies to:

- direct navigation to `/`;
- successful registration;
- successful login.

This is an explicit interim rule, not an interpretation that Q202 has already been
satisfied. No empty Home scaffold is required to end the interim early.

### Signed-in landing after Home exists

When the Home slice ships:

- direct signed-in navigation to `/` resolves to `/home`;
- successful login lands on `/home`;
- successful registration eventually proceeds toward `/home`, subject to the
  onboarding rule below.

The Home slice is the named flip-point. The landing behavior must not change earlier
in an unrelated slice.

### Registration and onboarding

The complete intended flow is:

```text
registration
→ email verification
→ optional onboarding when its dependencies exist
→ Home
```

Q203's onboarding sequence is:

1. optional home city;
2. optional favorite artists;
3. optional favorite venues;
4. optional suggested-user follows;
5. Home.

Every onboarding step is skippable.

Three dependencies are currently deferred:

- email verification;
- onboarding data/actions;
- Home.

Therefore the current interim behavior remains:

```text
registration or login
→ Discover
```

When Home exists but onboarding dependencies do not yet exist, login and registration
flip to Home without speculative onboarding stubs.

The onboarding sequence inserts before first Home entry only when its real
dependencies—favorites and suggested users—exist. The slice that activates
onboarding must document how it distinguishes first-time onboarding from ordinary
subsequent login.

Email verification remains a separate frozen-requirement repayment and must be
completed before public deployment.

## Guest navigation

Q127 defines what guests may read. It does not turn every readable resource into a
primary destination.

The guest navigation displays only final destination positions meaningful without
an account:

1. Discover
2. Search, once implemented
3. the Profile position occupied by authentication access

Guests do not see:

- Home;
- Activity;
- a personal Profile destination;
- Been;
- Reviews as a primary destination;
- events, venues, artists, or other users as primary destinations.

Public resources remain reachable contextually:

- events through Discover and Search;
- artists and venues through Discover, Search, and event links;
- public reviews through event/profile surfaces;
- public profiles through Search and contextual links.

At the Profile position, guests receive authentication controls:

- Log in
- Register

These controls occupy the account/profile area of navigation but are not sixth or
seventh primary destinations.

## Signed-in navigation

As destinations are delivered, an authenticated user's final primary-navigation
order is:

1. Home
2. Discover
3. Search
4. Activity
5. Profile

The Profile position links to:

```text
/u/{current_username}
```

Account controls, including logout and future settings access, are structurally
attached to the Profile position. They are not additional primary destinations.

The current plain-text `Signed in as {username}` status is temporary. The Profile
slice absorbs that identity signal into the Profile position and removes the
standalone primary-nav list item.

## Interim register

Every currently rendered navigation item that is not one of the five final
destinations is classified here. Nothing currently rendered remains unclassified.

| Current item | Current route/action | Classification | Final owner/absorber | Required absorption slice |
|---|---|---|---|---|
| Register | `/register` | Auth control | Guest auth access attached to the Profile position | Profile slice |
| Log in | `/login` | Auth control | Guest auth access attached to the Profile position | Profile slice |
| `Signed in as {username}` | No route; status text | Interim account-status UI | Authenticated Profile position | Profile slice |
| Been | `/been` | Interim organ | Profile's default Been tab at `/u/{username}` | Profile slice |
| Log out | Session-ending button | Auth control | Account actions attached to the Profile position | Profile slice |

Discover is not listed because it is one of the five final destinations. Its current
`/` route is transitional and governed by the landing rules.

The `Danced` header text is not a navigation item because it is a plain paragraph.
If it later becomes a link, its target must follow the landing rules rather than
create a sixth destination.

### Interim contextual controls

These controls are not primary navigation items, but use the same named-absorber
discipline so temporary user-discovery surfaces cannot become permanent by accident.

| Surface | Purpose | Final owner/absorber | Required absorption slice |
|---|---|---|---|
| Follow/unfollow control on a public-review author byline | Temporary reachable follow action for currently visible public authors; guests see no control and the author name is not a link | Public Profile at `/u/{username}` | Profile slice |

Private-account request initiation is API-complete but has no current UI because
private authors are not reachable through Public reviews. Search/Profile delivery
adds the discoverable private-user surface and request controls; this interim does
not authorize a dead profile link or a Settings destination.

## Absorption requirements

### Been absorption

The Profile slice must:

1. deliver `/u/{username}`;
2. make Been the default tab;
3. deliver `/u/{username}/reviews` if Reviews ships in the same slice, or reserve
   that route without rendering a dead tab until Reviews exists;
4. preserve event-date-descending Been ordering;
5. include rated and unrated Been attendance entries;
6. preserve owner/privacy visibility through the sanctioned queryset boundary;
7. replace signed-in `/been` navigation with the Profile position;
8. decide whether `/been` redirects to the signed-in user's canonical profile or is
   removed only after all internal links migrate;
9. test whichever compatibility behavior is selected.

This contract does not authorize a redirect implementation now. The Profile slice
must make that compatibility choice explicitly.

### Authentication-control absorption

The Profile slice must structurally distinguish:

- the five destination positions;
- guest authentication controls;
- authenticated account/status controls.

For guests, Log in and Register occupy the Profile/account position.

For authenticated users:

- Profile becomes the identity-bearing destination;
- `Signed in as {username}` is no longer a separate list item;
- Log out is attached to the Profile/account area;
- future Settings access is attached there rather than becoming a primary
  destination.

This is a future markup obligation. This documentation slice does not require
changing the current frontend.

## Standing navigation rule

Any future navigation addition must satisfy exactly one of these conditions:

1. It is one of the five primary destinations:
   - Home
   - Discover
   - Search
   - Activity
   - Profile
2. It is declared in this document's interim register in the same slice that adds
   it, with:
   - its classification;
   - its owning absorber;
   - its named absorption slice.

There are no sixth primary destinations.

The following do not become primary destinations merely because they receive pages:

- Been;
- Reviews;
- Settings;
- favorites;
- followers/following;
- events;
- venues;
- artists;
- public profiles of other users;
- notifications subtypes;
- onboarding steps.

Guest navigation shows only destinations meaningful to guests under Q127:

- Discover;
- Search once implemented;
- authentication access at the Profile position.

Home and Activity remain signed-in-only.

## Per-slice checklist

Every future implementation prompt that can affect global navigation must include
and verify:

> Nav changes conform to `docs/NAVIGATION.md` or update it in the same commit.

A slice is not navigation-complete until it verifies:

- no sixth primary destination was introduced;
- destination order remains correct;
- guest visibility follows Q127;
- auth controls remain attached to the Profile position;
- any new interim item has a named absorber and absorption slice;
- route/landing changes preserve or explicitly migrate existing deep links;
- contextual resources remain contextual rather than entering primary navigation.

## Current implementation checkpoint

Slice 4B's coordinated transition produces this rendered navigation:

Guest:

1. Discover → `/discover`
2. Register → `/register`
3. Log in → `/login`

Signed in:

1. Home → `/home`
2. Discover → `/discover`
3. Activity → `/activity`
4. `Signed in as {username}` → plain status
5. Been → `/been`
6. Log out → session action

Implemented contextual routes:

- `/events/{id}`
- `/venues/{id}`
- `/artists/{id}`

Slice 2.5's authorized **Recent events** section changes content within Discover and
requires no navigation addition or interim-register entry.

Search and Profile remain absent rather than rendering empty stubs. The remaining
non-final elements are classified by the interim register and remain accountable to
their named absorber.

### Slice 4B transition ruling

Slice 4B executes the Home transition described above. During this interim state,
direct guest navigation to `/home` redirects to `/discover`; logging out while on
`/home` does the same. Home never renders as a guest destination or empty guest
shell. A legacy root URL containing `city_id` redirects to the matching Discover URL
before authentication-based landing is considered, so shared city state is never
dropped.
