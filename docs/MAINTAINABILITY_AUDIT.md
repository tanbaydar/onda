# Onda Maintainability Audit

Audited read-only at commit `a83c807` as evidence for a post-Milestone 4 refactor decision.

Risk-if-refactored means the likelihood that the current tests would fail to catch a faulty cleanup: **high** means weak protection.

## Duplicated and near-duplicated logic

| Location | Finding | Maintenance severity | Risk if refactored | Suggested remedy |
|---|---|---:|---:|---|
| `backend/users/views.py:892`, `backend/users/views.py:1402` | Profile Been and the current-user diary endpoint independently build almost the same visible-entry query, lineup prefetch, event serialization, ordering, `has_review`, and pagination. | High | Medium | Extract a shared diary query and base serializer; let each endpoint add its contract-specific fields. |
| `backend/users/views.py:939`, `backend/users/views.py:1311` | Profile Reviews and event Public Reviews duplicate like-count, approved-follower-count, `viewer_has_liked`, ordering, and review serialization logic. | High | Medium | Create one review-list projection/query builder with explicit scope and ordering arguments. |
| `backend/users/views.py:608`, `backend/catalog/views.py:163` | Page validation, `Paginator` handling, out-of-range behavior, and response envelopes are repeatedly hand-built. | Medium | Low | Introduce a small shared page-number pagination utility returning the established response shape. |
| `frontend/src/components/PublicReviews.jsx:40`, `YourCircle.jsx:42`, `pages/ProfilePage.jsx:94` | Like/unlike mutation and 409 reconciliation are implemented separately on three surfaces. This is the class that previously allowed duplicate copies of one review to diverge. | High | High | Extract one review-like mutation function and a shared invalidation callback keyed by review ID. Add a rendered integration test first. |
| EventList, PublicReviews, YourCircle, WillBeThereAttendees, Discover, VenuePage, ArtistPage, EventPage, ProfilePage | The same loading/error/retry state machine—state object, retry counter, abort controller, and retry UI—is repeated broadly. | Medium | Medium | Extract a minimal `useFetchResource` hook preserving abort, retry, and HTTP-error behavior. |
| EventList, PublicReviews, YourCircle, WillBeThereAttendees, BeenPage, ProfilePage | Nearly identical previous/next pagination markup is repeated. ProfilePage already has a local pagination component. | Low | Low | Move the existing semantic pagination control into a shared component. |
| `frontend/src/pages/VenuePage.jsx`, `ArtistPage.jsx` | Venue and Artist pages duplicate detail loading, 404/error behavior, favorite mutations, and Upcoming/Past lists. | Medium | Medium | Share detail-loading and favorite-state mechanics while retaining entity-specific semantic markup. |
| VerifyEmail, PasswordResetForm, RegisterPage, LoginPage | Auth screens flatten and classify API errors differently. | High | High | Centralize field, non-field, auth/CSRF, server, and network error classification while keeping screen-specific wording local. |

## Dead or vestigial code

| Location | Finding | Maintenance severity | Risk if refactored | Suggested remedy |
|---|---|---:|---:|---|
| `frontend/src/pages/BeenPage.jsx` | This 129-line page is exported but never imported or routed. `/been` now redirects into Profile through `LegacyBeenPage`. | Medium | Low | Delete it after one final route/import search and frontend build. |
| `backend/users/auth_services.py:149` | `consume_account_code()` has no caller; the atomic success path uses `_consume_account_code_locked()` directly. | Medium | Medium | Delete it if it is not a supported public service, or make it the sole tested atomic wrapper. |
| `backend/users/services.py` | `FavoriteEvent`, `FavoriteArtist`, and `FavoriteVenue` are imported but unused. | Low | Low | Remove the imports. |
| `backend/users/home_feed.py` | `DateTimeField` is imported but unused. | Low | Low | Remove the import. |
| `backend/ingestion/views.py` | Contains only the unused Django-generated `render` import and no view. | Low | Low | Remove the import or empty module if nothing imports it. |
| `backend/users/tests/test_social_api.py` | `ReviewLike` is imported but unused. | Low | Low | Remove the import. |

Static analysis was deliberately limited to evidence-backed unused names. Dynamic Django registrations and URL-driven call sites were not classified as dead merely because static analysis could not resolve them.

## Naming and contract inconsistencies

| Location/concept | Finding | Maintenance severity | Risk if refactored | Suggested remedy |
|---|---|---:|---:|---|
| `DiaryEntry`, `/been`, `event_been`, `diary_list`, `BeenPage`, “Been” | The same domain object is called diary, entry, and Been depending on layer, making searches incomplete. | Medium | Medium | Document a vocabulary: `DiaryEntry` is the model, “Been” the product label, and private endpoint/service names use one internal term. |
| `WillBeThere`, `will-be-there`, WBT, `is_marked`, `save_will_be_there` | The feature alternates among full name, acronym, and generic “mark” language. | Low | Low | Standardize internal code on `will_be_there`; reserve WBT for prose and “marked” for response booleans. |
| API views and frontend consumers | Failure envelopes alternate between `{"error": "…"}` and `{"errors": {"field": […]}}`. | High | High | Freeze a common error-envelope contract with field-keyed actionable errors and consistent non-field codes/messages. |
| Home, notifications, page-number endpoints | Pagination names drift among `next_cursor`, `next`, `nextCursor`, and page-number metadata. | Low | Low | Normalize frontend state to `nextCursor` for cursors and `nextPage` for numbered pagination. |
| Event aggregate, Circle aggregate, rating distribution | Similar summaries use `not_enough_ratings`, threshold-one behavior, and `empty`; the product differences are valid but the names do not expose their thresholds. | Medium | Medium | Encode the threshold in a shared aggregate-result helper and document the state vocabulary. |

## Over-complex units

| Location | Finding | Maintenance severity | Risk if refactored | Suggested remedy |
|---|---|---:|---:|---|
| `backend/users/views.py` | At roughly 1,460 lines, one module owns profile, diary, review, follow, notification, Circle, favorite, and statistics APIs plus serialization. | High | Medium | Split along existing API domains without changing URLs; move common projections first. |
| `backend/users/views.py:813` | `profile_edit` parses, validates four fields, resolves catalog data, persists, and serializes in one view. | Medium | Medium | Move validation and mutation into a focused profile-edit service or Django form. |
| `backend/users/views.py:1241` | `event_circle` performs auth, pagination, sanctioned queries, aggregation, per-row like state, and serialization. Its per-reviewed-entry `.exists()` is an apparent N+1 path. | High | High | Annotate `viewer_has_liked`, extract serialization, and add a mixed-page query-count test first. |
| `backend/users/views.py:1311` | `event_review_list` combines privacy, capabilities, annotations, sorting, pagination, and payload construction. | High | Medium | Extract the approved public-review projection and serializer. |
| `frontend/src/pages/EventPage.jsx` | About 400 lines manage event loading, Been/rating/review lifecycle, WBT, favorites, attendees, social invalidation, errors, and rendering. | High | High | Extract behavior hooks by resource while retaining the existing semantic markup. |
| `frontend/src/pages/ProfilePage.jsx` | One file contains the page, pagination, facts, tabs, editor, privacy control, requests, favorites, and statistics. | Medium | Medium | Split the existing components into files without changing their data contracts. |
| `backend/users/home_feed.py:112` | `home_feed_rows` constructs six UNION branches, distributed cursor predicates, visibility, and frozen tie-breaks in one dense unit. | Medium | Medium | Extract one builder per activity type while preserving one final database union and existing query-count/order tests. |
| `backend/ingestion/runner.py:265` | `run_sync` coordinates locking, run lifecycle, budgets, seed processing, quarantine, completeness, and reconciliation. | Medium | Medium | Extract narrow run-state and seed-processing helpers while keeping transaction ownership explicit. |

## Module-boundary confusion

| Location | Finding | Maintenance severity | Risk if refactored | Suggested remedy |
|---|---|---:|---:|---|
| `backend/users/views.py:24`, `backend/catalog/views.py:277` | Users imports private catalog view serializers, while catalog event detail imports users models/services inside the function. This creates two-way knowledge between app view layers. | High | High | Move catalog serializers into a public catalog serialization module and expose one users-owned social-enrichment function. |
| `backend/users/services.py` | The module mixes mutations, event-clock eligibility, public-user serialization, aggregates, and capability policy. | Medium | Medium | Split it by current responsibility: mutations, visibility/capabilities, and projections. |
| `backend/catalog/views.py`, `backend/users/views.py` | Event-detail payload ownership is unclear: catalog owns base fields while users partially controls the final contract. | High | High | Define one explicit composition seam: catalog returns the base payload; users returns a named optional social extension. |
| `frontend/src/lib/api.js` and page-local handlers | Transport is only partly centralized; HTTP classification, business conflicts, and stale-state reconciliation remain component knowledge. | Medium | High | Add normalized error metadata—status, field errors, code—to the small fetch helper without adding a data framework. |

## Test-coverage gaps

| Location/seam | Finding | Maintenance severity | Risk if refactored | Suggested remedy |
|---|---|---:|---:|---|
| CSRF/session browser flow | No test sends a browser-equivalent `Origin` header on an unsafe request. The earlier browser registration failure passed scripted verification because the script omitted it. | High | High | Test session bootstrap followed by a CSRF POST with a trusted `HTTP_ORIGIN`, plus rejection of an untrusted origin. |
| Public Reviews + Circle duplicate rendering | No frontend integration test renders one review in both sections and verifies like/unlike synchronization in both directions. | High | High | Add an EventPage integration test covering both mutation directions and 409 reconciliation. |
| Follow control + Circle invalidation | No frontend test proves follow/unfollow updates both capability state and Circle content on one loaded page. | High | High | Add a rendered follow → Circle refresh → unfollow → empty/restored-state test. |
| Registration/auth error rendering | Frontend tests do not render registration through field-keyed 400, CSRF 403, server 500, and network failure. | High | High | Add parameterized form tests asserting each message appears exactly once in the proper location. |
| Favorite conflict vs state-drift 409 | Favorite classification has focused coverage, but the distinction is not enforced as a shared transport rule. | Medium | High | Test a shared classifier and one caller for business rejection versus refetch reconciliation. |
| `backend/users/views.py:1241` Circle endpoint | No query-count contract guards the Circle page; per-row like lookup can scale with result count. | High | High | Assert a bounded query count using a mixed rating-only/reviewed page. |
| Sanctioned queryset consumers | Boundary methods are tested, but consuming endpoints can still apply the correct boundary at the wrong scope. | High | Medium | Add concrete endpoint-level privacy leak cases for each consumer; avoid a policing meta-test. |
| Email-verification capability gate | Flag-on/off coverage does not appear to exercise every existing social write route. A future mutation can omit the shared gate. | Medium | High | Before M5 enforcement, add a parameterized flag-on contract over all social writes. |
| Verify/reset frontend screens | Backend lifecycle coverage exists, but frontend expiry, cooldown, exhausted-attempt, and reset-error rendering are untested. | Medium | High | Add screen-level error-rendering tests before flipping the M5 flag. |
| Event/Profile orchestration | Complex mutation orchestration is largely untested; the frontend suite remains helper-oriented compared with the backend suite. | High | High | Add a few high-value rendered scenarios rather than broad snapshots. |

## Areas comparatively well protected

- The six-branch Home `UNION ALL` has fixed query-count, cursor, same-time ordering, lifecycle, and privacy tests.
- Ingestion has frozen fixtures and strong completeness, quarantine, and lifecycle coverage.
- Core sanctioned visibility methods have direct behavioral coverage.
- Affected user-zone models now have physical-schema cascade tests instead of relying only on ORM declarations.

## Ranked shortlist: highest-value, lowest-risk fixes

1. **Delete orphaned `BeenPage.jsx` and verified unused imports.** High certainty, tiny behavioral surface, and strong build/static protection.
2. **Consolidate page-number pagination helpers.** Repeated stable logic with strong endpoint contract coverage.
3. **Extract the shared public-review query projection and serializer.** Removes substantial privacy/ordering duplication; add one parity test first.
4. **Centralize frontend error classification.** Directly addresses two founder-found defect families; pin the existing behavior before migrating callers.
5. **Fix and pin Circle's apparent N+1 query path.** Add a query-count test, then replace per-entry like lookups with one annotation.

The first broad structural refactor should not be EventPage or the Home feed union. Both have real cleanup value, but EventPage remains especially risky until cross-section state tests exist, while the feed union is already strongly protected and behaviorally dense.
