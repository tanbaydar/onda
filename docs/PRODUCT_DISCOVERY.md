# Product Discovery — Music Events App

**Status:** Discovery in progress  
**Purpose:** Living source for product decisions made during the design conversation  
**Rule:** A statement enters “Confirmed decisions” only after explicit confirmation.  
**End result:** An implementation contract precise enough that coding decisions are unambiguous.

---

## 1. Confirmed decisions

### Product analogy

- The product is analogous to Letterboxd, but for music events.
- The primary catalog object is a music event.
- Example events include:
  - Shakira performing at Madison Square Garden.
  - John Summit performing a DJ set at Savaya Bali.

### Design process

- Product behavior will be designed before technical architecture.
- The goal is an exceptionally specific product specification.
- Decisions will be developed iteratively in conversation from first principles.
- This conversation is ultimately about coding the application.
- Before technical work begins, every product behavior will be expressed in plain language.
- Product statements will define screens, states, actions, rules, permissions, transitions, edge cases, and failure behavior.
- Technical design and implementation must trace back to confirmed product statements.

---

## 2. Provisional interpretations

These are working interpretations, not confirmed decisions.

- A user records their relationship to a canonical event through a diary/log entry.
- Artists and venues may exist as catalog entities without being account holders.
- An event rating may evaluate the complete event experience.
- Social discovery, reviews, lists, and profiles may follow recognizable Letterboxd patterns.
- External event-data acquisition is unresolved and should not determine early product behavior.

---

## 3. Current discovery stage

### Stage 1 — Product identity and boundaries

We are defining:

- who the product is for;
- the user problem and emotional payoff;
- what counts as a music event;
- what the user is actually recording;
- whether the app is primarily a diary, review network, discovery tool, or some combination;
- what should deliberately not exist.

---

## 4. Open decision groups

1. Product promise and target audience
2. Definition and identity of an event
3. Attendance, logging, ratings, and reviews
4. Artist, venue, tour, festival, and set relationships
5. User identity, profiles, and privacy
6. Social graph and activity
7. Lists, favorites, tags, and personal organization
8. Search, browsing, and discovery
9. Upcoming events and intent to attend
10. Catalog creation, corrections, and duplicate resolution
11. Moderation, reporting, and community rules
12. Notifications and retention loops
13. Geography, timezones, and event dates
14. Cancelled, postponed, recurring, online, and private events
15. Product language, visual identity, and brand voice
16. MVP boundary and later product layers
17. Screen states, transitions, and navigation
18. Validation, errors, empty states, and recovery behavior
19. Acceptance criteria and requirement traceability

---

## 5. Decision log

| Date | Decision | Status | Notes |
|---|---|---|---|
| 2026-07-30 | Use a music event as the Letterboxd-equivalent primary object | Confirmed | Examples: Shakira at MSG; John Summit at Savaya Bali |
| 2026-07-30 | Restart product design without technical constraints | Confirmed | Technology will be addressed after product behavior |
| 2026-07-30 | Describe all behavior in words before coding | Confirmed | The final product spec will operate as an implementation contract |

---

## 6. Parking lot

- Technical stack
- Database design
- API design
- Data ingestion provider
- Hosting and deployment

These topics are intentionally deferred until the product specification is mature.

---

## 7. Specification standard

Each feature will eventually define:

1. Purpose
2. Entry points
3. Preconditions
4. Visible information
5. Available user actions
6. State transitions
7. Validation rules
8. Empty states
9. Loading states
10. Error and retry behavior
11. Permissions and visibility
12. Deletion and restoration behavior
13. Interaction with other features
14. Edge cases
15. Acceptance criteria

No code should be written for a feature while product-critical behavior remains implicit.
