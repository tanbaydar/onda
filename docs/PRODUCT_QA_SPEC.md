# Product Questions and Answers

## Question 1

**Question:** Describe the app in one sentence, using your own words.

**Answer:** A vertical social network for musical events, combining ideas from Instagram, Twitter, Letterboxd, and Beli.

## Question 2

**Question:** Who is the first ideal user? Describe one specific person—their age range, where they live, what kinds of music events they attend, how often they attend, and what they currently use to discover, remember, rate, or share those events.

**Answer:** Users are 18–30 and may live anywhere. The product is global and is not limited by genre, event-attendance frequency, or one behavioral archetype. It should support people who use it only to discover events, only to remember events, only to rate events, only to share events, or to combine any of those behaviors.

## Question 3

**Question:** When a brand-new user opens the app for the first time after creating an account, what should the app primarily help them do first?

**Answer:** After email verification, show a fully skippable onboarding sequence for home city, favorite artists, favorite venues, and suggested users to follow. Then enter Home.

## Question 4

**Question:** What should most often cause an existing user to reopen the app?

**Answer:** All of the listed reasons:

- See what friends attended, rated, reviewed, or posted.
- Discover upcoming events.
- Log or review an attended event.
- Check reactions to their own activity.
- Browse event-related conversations.
- Update their diary, ratings, or profile.
- Receive personalized recommendations.

No single return loop is currently designated as dominant.

## Question 5

**Question:** What is the exact boundary of one event page when several performers appear during the same advertised night?

**Answer:** The complete advertised night has one event page. Only one object is evaluated: the whole night. Individual performances within the night are not separately rated.

## Question 6

**Question:** How should a user produce the whole-night ranking?

**Answer:** Superseded. Comparative ranking is excluded from MVP. The active logging flow is a mandatory half-star rating followed by save.

## Question 7

**Question:** What should the short questions before the comparison ranking measure?

**Answer:** Superseded. The MVP has no preliminary experience questions.

## Question 8

**Question:** How should a multi-day music festival be represented?

**Answer:** Follow the external catalog source's event boundaries. One source event record becomes one Onda event. If the source provides separate daily events, Onda shows separate event pages. If the source provides one multi-day event, Onda shows one event page. Onda does not independently split or merge festival records.

## Question 9

**Question:** Can a user save an attended event to their personal history without rating, ranking, reviewing, or posting anything about it?

**Answer:** No. To save an attended event, the user must provide a half-star rating.

## Question 10

**Question:** Must every saved event complete the comparison step and receive a position in the user's personal ranking, or may a user save it after answering the minimum required question and rank it later?

**Answer:** Superseded. Comparative ranking is excluded from MVP. Every saved event must contain a half-star rating.

## Question 11

**Question:** When a user saves an attended event but postpones ranking it, where should that action become visible?

**Answer:** Not applicable. Comparative ranking is excluded from MVP.

## Question 12

**Question:** When the user later completes or changes the event's ranking, should that update create a new item in followers' feeds?

**Answer:** Not applicable. Comparative ranking is excluded from MVP.

## Question 13

**Question:** Can users add events they attended before joining the app, including events from many years ago?

**Answer:** The product supports retroactive logging for any past event present in
Onda's canonical catalog. For v1, the target catalog window is approximately two
months around launch—recent plus upcoming events—in the seeded launch cities, loaded
through a one-time Resident Advisor backfill, plus all events acquired going forward.
Retroactive logging is limited accordingly. This is a deliberate resume-project scope
cut: the demo needs a populated, live catalog, while greater depth adds no
demonstrative value. Deeper history remains a one-flag rerun of the same ingestion
path if ever wanted.

The historical backfill is gated on source reconnaissance confirming that RA supports past-date listing queries. If unsupported, v1 falls back to launch-forward coverage and retroactive logging is limited to events that exist in the accumulated catalog. The application never fetches RA synchronously in response to a user search or action.

## Question 14

**Question:** At what point may a user mark an event as attended?

**Answer:** A user may mark an event as attended as soon as its scheduled start time arrives.

## Question 15

**Question:** Does the app accept attendance claims on trust, or must users prove they were present?

**Answer:** Trust users completely. Attendance is self-reported and requires no verification or supporting proof.

## Question 16

**Question:** What should the primary action for adding a past or current event to personal history be called in the interface?

**Answer:** Match Beli. The attended collection is called **Been**, and the action moves the event into the user's Been list. Working action copy: **Add to Been**.

## Question 17

**Question:** What should the equivalent status and list be for an upcoming event the user wants to attend?

**Answer:** **Will Be There**.

## Question 18

**Question:** What form should the event evaluation use?

**Answer:** Use one half-star rating from 0.5 to 5 stars. It is required before save.

## Question 19

**Question:** Must the sentiment choice and half-star rating agree according to fixed ranges?

**Answer:** Not applicable. The sentiment choice was removed from MVP.

## Question 20

**Question:** When first adding an event to Been, which input is mandatory?

**Answer:** A half-star rating from 0.5 to 5 stars is mandatory.

## Question 21

**Question:** Is a written review optional, and can a user add or edit it later without repeating the rating and ranking flow?

**Answer:** A written review is optional. The user can add or edit it later without changing or re-entering the star rating.

## Question 22

**Question:** Can one user create more than one separate written review for the same event?

**Answer:** No. Each user has one written review per event and can continually edit that review.

## Question 23

**Question:** Is the event review itself the user's social post, or can a user create additional Instagram/Twitter-style posts about the same event?

**Answer:** There are no free-floating social posts. Every entry belongs to one canonical event and appears inside that event. For MVP, a user's event entry contains the evaluation and may contain one optional written review. Photo posting is excluded.

## Question 24

**Question:** How many photos may one user attach to their entry for one event?

**Answer:** Superseded. Photos are excluded from MVP.

## Question 25

**Question:** Does each photo have its own optional caption, or do all photos share one caption?

**Answer:** Superseded. Photos and photo captions are excluded from MVP.

## Question 26

**Question:** Can event entries include video in addition to photos?

**Answer:** No for MVP. Media posting is excluded.

## Question 27

**Question:** Should the simplified MVP logging flow still allow the star rating and comparison steps to be postponed?

**Answer:** Superseded. Comparative ranking is excluded from MVP. The event cannot be saved to Been until the user provides a half-star rating.

## Question 28

**Question:** How should the comparison step place a newly logged event into the user's existing ranked list?

**Answer:** Superseded. Comparative ranking is excluded from MVP.

## Question 29

**Question:** What should **Too tough** mean for the ranking?

**Answer:** Superseded. Comparative ranking and **Too tough** are excluded from MVP.

## Question 30

**Question:** Does every event belong to one combined personal ranking, even when the events are very different?

**Answer:** Superseded for MVP because comparative ranking is excluded. All event types still use the same evaluation system and rating scale.

## Question 31

**Question:** May the final personal ranking contradict the user's star rating?

**Answer:** Not applicable. Comparative ranking is excluded from MVP.

## Question 32

**Question:** Who should see the user's event rating?

**Answer:** Visibility is controlled by one of two account-level privacy settings:

- **Public account:** Everyone can see the user's event entry, including the star rating.
- **Private account:** Only the user's friends can see the event entry and its answers.

Every valid star rating still contributes anonymously to the event's aggregate average. A hidden individual rating is included in the system calculation but is not publicly attributable to the private user.

For a public account, profile and rating visibility does not require following. Any user who opens the public profile can see its visible event ratings. Following only subscribes the viewer to the account's future activity.

## Question 33

**Question:** In a private account, who qualifies as a **friend**?

**Answer:** Anyone the private user approves as a follower. Mutual following is not required. In this context, an approved follower is a friend and can see the private account's entries.

## Question 34

**Question:** How should following work for public accounts?

**Answer:** Following a public account is immediate and requires no approval. Following controls feed subscription, not profile access; anyone can view a public account's profile and ratings without following.

## Question 35

**Question:** What happens to existing followers when a public account switches to private?

**Answer:** All existing followers remain approved friends. Switching to private does not remove them or require them to request access again.

## Question 36

**Question:** What happens to pending follow requests when a private account switches to public?

**Answer:** Every pending follow request is automatically accepted. Those requesters immediately become followers of the now-public account.

## Question 37

**Question:** What can someone see when they open a private profile they are not approved to follow?

**Answer:** Only:

- Profile photo
- Username
- Display name
- Bio
- Home city

Follower/following counts, event counts, favorite events, diary entries, ratings, written reviews, and all other activity are hidden.

## Question 38

**Question:** Should private accounts appear in user search results and be discoverable by username or display name?

**Answer:** Yes. Private accounts appear in user search results and can be found by username or display name.

## Question 39

**Question:** Should users be able to block other users in MVP?

**Answer:** No. Blocking is excluded from MVP.

## Question 40

**Question:** After User A blocks User B, what visibility should remain between them?

**Answer:** Not applicable. Blocking is excluded from MVP.

## Question 41

**Question:** Can a user change their star rating after saving an event to Been?

**Answer:** Yes. A user can change their star rating after saving the event to Been.

## Question 42

**Question:** When a user changes an existing rating, should that edit create a new item in followers' feeds?

**Answer:** No. The existing event entry updates silently. A rating change does not create a new feed item.

## Question 43

**Question:** When a user adds or edits the optional written review later, should that create new feed activity?

**Answer:** All later review changes are silent. Adding the first written review after the original event log or editing an existing review does not create new feed activity.

## Question 44

**Question:** Can a user remove an event from Been after saving it?

**Answer:** Yes. A user can remove an event from Been after saving it.

## Question 45

**Question:** What happens to the user's rating and written review when they remove the event from Been?

**Answer:** Both are permanently deleted. The deleted rating stops contributing to the event's aggregate average.

## Question 46

**Question:** Should removing an event from Been require a confirmation step?

**Answer:** Yes. Removing an event from Been always requires confirmation because the action permanently deletes the rating and any written review.

## Question 47

**Question:** After removing an event from Been, can the user add the same event again later as a new entry?

**Answer:** Yes. The event can be added again as a new entry. Previously deleted ratings and reviews are not restored.

## Question 48

**Question:** How many ratings must an event receive before its average rating is publicly displayed?

**Answer:** The public average rating is displayed after the event has received at least 3 valid ratings.

## Question 49

**Question:** Before an event reaches 3 ratings, what should viewers see in place of the public average?

**Answer:** Display **Not enough ratings** instead of a public average.

## Question 50

**Question:** Once available, how precisely should the average rating be displayed?

**Answer:** Display the average to one decimal place, such as **4.3**.

## Question 51

**Question:** Should an event page show the distribution of ratings in addition to the average?

**Answer:** Yes. Once the event has enough ratings to display an average, its page also shows the distribution across all half-star rating values. Ratings from private accounts contribute anonymously.

## Question 52

**Question:** Should the rating distribution show raw counts, percentages, or only relative bar lengths?

**Answer:** Relative bar lengths only. Do not display raw counts or percentages on the distribution.

## Question 53

**Question:** Should an event page show a separate average based only on ratings from people the viewer follows?

**Answer:** Yes. The event page shows a separate average based on ratings from people the viewer follows alongside the global average.

## Question 54

**Question:** Which individual user entries should a viewer be able to see on an event page?

**Answer:** Visible entries are separated into two sections:

- **Your Circle**
- **Public**

Private entries that the viewer is not permitted to access are never displayed or attributed, although their ratings still contribute anonymously to aggregate calculations. The exact relationship used to populate the Your Circle section is defined in the next question.

## Question 55

**Question:** Which users belong in the viewer's **Your Circle** section on an event page?

**Answer:** Everyone the viewer follows. Mutual following is not required. The section is called **Your Circle**, not Friends.

## Question 56

**Question:** If a followed user has a public account, should their entry appear only in Your Circle, or appear in both Your Circle and Public?

**Answer:** Both. The entry appears in **Your Circle** because the viewer follows the user, and it also remains in **Public** because the account is public.

## Question 57

**Question:** How should entries be ordered inside the Public section of an event page?

**Answer:** The **Public** section contains only entries with written reviews. A rating without a written review does not appear there. The interaction model should resemble an Instagram comment section or Letterboxd review section.

The section has two sorting options:

1. **Most liked** — default
2. **Newest**

## Question 58

**Question:** Does the Your Circle section show rating-only entries from people the viewer follows, or only entries containing written reviews?

**Answer:** Both. **Your Circle** shows rating-only entries and entries containing written reviews from people the viewer follows. **Public** remains limited to entries with written reviews.

## Question 59

**Question:** How should entries be ordered inside Your Circle?

**Answer:** **Your Circle** is ordered by **Newest** only. It has no sorting control.

## Question 60

**Question:** Can users like rating-only entries in Your Circle, or can they like only entries containing a written review?

**Answer:** Only written review entries can receive likes. Rating-only activity cannot be liked.

## Question 61

**Question:** Can users reply to or comment on a written review entry?

**Answer:** No for MVP. Comments and replies on written reviews are recorded as a future feature.

## Question 62

**Question:** Can a user like their own written review?

**Answer:** No. A user cannot like their own written review.

## Question 63

**Question:** Can a user remove a like they previously gave to a review?

**Answer:** Yes. A user can remove a like they previously gave.

## Question 64

**Question:** When viewing a review, should users see only its like count or also the list of users who liked it?

**Answer:** Show only the like count. Do not expose a list of users who liked the review.

## Question 65

**Question:** What is the maximum length of a written event review?

**Answer:** 1,000 characters.

## Question 66

**Question:** Should a review require any minimum length beyond containing at least one visible, non-space character?

**Answer:** No. After trimming surrounding whitespace, at least one visible character is sufficient.

## Question 67

**Question:** Should reviews support clickable links, hashtags, or @mentions in MVP?

**Answer:** No. MVP reviews are plain text and do not support clickable links, hashtags, or @mentions.

## Question 68

**Question:** Should an edited written review display an **Edited** label?

**Answer:** No. Review edits do not display an **Edited** label.

## Question 69

**Question:** When sorting reviews by Newest or Oldest, should an edited review keep its original publication position or move according to its latest edit time?

**Answer:** Keep the original publication position. **Newest** and **Oldest** sort by the review's original publication time, not its latest edit time.

## Question 70

**Question:** Can a user delete only their written review while keeping the event in Been and preserving their star rating?

**Answer:** Yes. Deleting the written review does not remove the event from Been and does not remove or change the user's star rating.

## Question 71

**Question:** When a written review is deleted, should all likes on that review be permanently deleted as well?

**Answer:** Yes. All likes are permanently deleted with the review. If the user writes another review later, it starts with zero likes.

## Question 72

**Question:** Must every published event have an exact calendar date?

**Answer:** Yes. A specific start date is mandatory for every published event. A start hour/time is optional.

## Question 73

**Question:** If an event has a start date but no start time, when may users begin adding it to Been?

**Answer:** At 12:00 AM at the beginning of the event's start date.

## Question 74

**Question:** Which timezone determines when an event becomes loggable?

**Answer:** The event venue's local timezone. The same event becomes loggable at one shared moment for all users.

## Question 75

**Question:** Must every published event have a specific venue?

**Answer:** For MVP, every published event must have a known, specific venue. **TBA**, unknown, and undisclosed venues are not supported.

## Question 76

**Question:** Are online-only events or livestreams included in MVP?

**Answer:** No. MVP includes only physical events at known venues.

## Question 77

**Question:** Must every published event have at least one known artist or performer?

**Answer:** For MVP, at least one known artist or performer is required.

## Question 78

**Question:** Must every event have an official title, or may the app generate a display title from the performer and venue?

**Answer:** For MVP, every event must have an official title.

## Question 79

**Question:** Must every published event have an official poster or cover image?

**Answer:** Every event page must display a cover image. Use the official poster when one is available; otherwise assign a default image.

## Question 80

**Question:** Is an event end date or end time required for MVP?

**Answer:** No. End date and end time are optional and never block publication.

## Question 81

**Question:** Should each venue have its own viewable catalog page in MVP?

**Answer:** Yes. Each venue has a viewable catalog page in MVP showing its location and associated events.

## Question 82

**Question:** Which events should a venue page display?

**Answer:** Separate **Upcoming** and **Past** event sections.

## Question 83

**Question:** Can users rate or review a venue itself in MVP?

**Answer:** No. Venues cannot be rated or reviewed. Only events receive ratings and reviews.

## Question 84

**Question:** Can users follow or save a venue in MVP to receive or find its future events more easily?

**Answer:** A user can privately favorite a venue. Favorite-venue status is not visible to other users.

## Question 85

**Question:** What does favoriting a venue do for the user in MVP?

**Answer:**

- Adds the venue to the user's private favorite-venues list.
- Prioritizes that venue's upcoming events in discovery.
- Offers optional notifications for new events at that venue; the user is not automatically forced to receive them.

## Question 86

**Question:** Should each artist or performer have their own viewable catalog page in MVP?

**Answer:** Yes. Each artist or performer has a viewable catalog page in MVP.

## Question 87

**Question:** Which events should an artist page display?

**Answer:** Separate **Upcoming** and **Past** event sections.

## Question 88

**Question:** Can users rate or review an artist directly in MVP?

**Answer:** No. Artists cannot be rated or reviewed directly. Only events receive ratings and reviews.

## Question 89

**Question:** Can users privately favorite artists in MVP?

**Answer:** Yes. This answer was later expanded: favorite artists are symmetric with favorite events. A user may feature up to 3 favorite artists on their profile, subject to account privacy.

## Question 90

**Question:** What does favoriting an artist do for the user in MVP?

**Answer:**

- Adds the artist to the user's favorite-artists list.
- Prioritizes the artist's upcoming events in discovery.
- Offers optional notifications when new events featuring the artist are added.

The profile-facing favorite-artist set is limited to 3, is unranked, and is ordered by date added from earliest to most recent.

## Question 91

**Question:** Can users save an individual upcoming event they may want to attend?

**Answer:** Yes. A user can mark an upcoming event as **Will Be There**.

## Question 92

**Question:** Who can see that a user marked an event as Will Be There?

**Answer:** Use the same account-privacy rule as event ratings:

- Public account: visible to everyone.
- Private account: visible only to approved followers.

## Question 93

**Question:** How should an event page show users who marked Will Be There?

**Answer:** Show separate **Your Circle** and **Public** user lists. Private-account visibility rules still apply.

## Question 94

**Question:** When an event's start time arrives, what happens to a user's Will Be There status?

**Answer:** It remains active throughout the event's local calendar day. It expires at 12:00 AM in the venue's local timezone on the day after the event's start date. It does not automatically become Been. The user must provide a rating to add the event to Been.

## Question 95

**Question:** Does marking an event Will Be There create an item in followers' feeds?

**Answer:** Yes. Marking **Will Be There** creates an item in followers' feeds, subject to account privacy.

## Question 96

**Question:** If the user removes Will Be There before the event starts, what happens to its existing feed item?

**Answer:** Delete the existing feed item silently. Do not create cancellation activity.

## Question 97

**Question:** When Will Be There automatically expires on the day after the event, what happens to its existing feed item?

**Answer:** It disappears. Expired **Will Be There** activity is not retained as historical feed content.

## Question 98

**Question:** Can a user first mark Will Be There after the event has already started but before it expires the next day?

**Answer:** Yes. A user can mark **Will Be There** at any time before its venue-local expiration at 12:00 AM on the day after the event date.

## Question 99

**Question:** If a user adds the event to Been while Will Be There is still active, what happens to Will Be There?

**Answer:** Keep both states until **Will Be There** expires naturally.

## Question 100

**Question:** If Will Be There is still visible when the user adds the event to Been, should followers' feeds temporarily show both activity items?

**Answer:** Yes. Both activity items may appear simultaneously. The **Will Be There** item disappears at expiration; the **Been** rating entry remains.

## Question 101

**Question:** Does every newly saved Been rating create an item in followers' feeds, even when it has no written review?

**Answer:** Yes. Every newly saved **Been** rating creates an item in followers' feeds, whether or not it includes a written review.

## Question 102

**Question:** How should the main following feed be ordered?

**Answer:** Strictly newest first for MVP. Algorithmic feed ranking is recorded as a future feature.

## Question 103

**Question:** When someone likes a user's written review, should the review author receive an in-app notification?

**Answer:** Yes. A review like generates an in-app notification for the review author.

## Question 104

**Question:** Should a user receive an in-app notification when someone follows them?

**Answer:** Yes. A new follow generates an in-app notification.

## Question 105

**Question:** Should a private account receive an in-app notification when someone requests to follow it?

**Answer:** Yes. A follow request generates an in-app notification for the private account.

## Question 106

**Question:** Should the requester receive an in-app notification when a private account accepts their follow request?

**Answer:** Yes. Acceptance generates an in-app notification for the requester.

## Question 107

**Question:** Should the requester be notified when a private account declines their follow request?

**Answer:** No. Declining a follow request does not notify the requester.

## Question 108

**Question:** Does MVP include device push notifications, or only an in-app notifications screen?

**Answer:** MVP is a website-first product and includes only an in-app notifications screen. Device push notifications are excluded from MVP.

## Question 109

**Question:** Should MVP send email notifications for social activity?

**Answer:** No. All MVP social notifications are in-app only.

## Question 110

**Question:** How much control should users have over social email notifications?

**Answer:** Not applicable. MVP sends no social email notifications.

## Question 111

**Question:** Can users change their username after creating an account?

**Answer:** Yes. Users can change their username after creating an account.

## Question 112

**Question:** Should username changes have a cooldown or frequency limit?

**Answer:** No. Username changes are unlimited.

## Question 113

**Question:** After a user changes their username, can another account immediately claim the old username?

**Answer:** Match Letterboxd's current policy. The old username enters a cooling-off period and cannot immediately be claimed by another account. During that period, the original account may revert to it. When the cooling-off period ends, the username becomes available to anyone.

## Question 114

**Question:** How many days should the old-username cooling-off period last?

**Answer:** 30 days.

## Question 115

**Question:** During the 30-day cooling-off period, what should happen when someone visits the user's old profile URL?

**Answer:** Return a profile-not-found page and show the nearest matching profile results. Do not redirect to the user's new username.

## Question 116

**Question:** What characters and length should usernames allow?

**Answer:** Use a conventional social-platform format:

- 3–30 characters
- Letters, numbers, underscores, and periods only
- No spaces
- Must begin and end with a letter or number
- No consecutive periods
- Uniqueness is case-insensitive
- Usernames are displayed in lowercase

## Question 117

**Question:** Can two users have the same display name?

**Answer:** Yes. Display names are not unique.

## Question 118

**Question:** Is a display name required, and what is its maximum length?

**Answer:** Use a conventional social-profile rule. Display name is required and must contain 1–50 visible characters after trimming surrounding whitespace. It does not need to be unique.

## Question 119

**Question:** What is the maximum profile-bio length?

**Answer:** 150 characters, matching Instagram. Line breaks, emoji, spaces, and ordinary text all count toward the same limit.

## Question 120

**Question:** Is uploading a profile photo required?

**Answer:** No. Profile photos are optional. Accounts without one use a default avatar.

## Question 121

**Question:** Is choosing a home city required when creating an account?

**Answer:** No. Home city is optional and can be added or changed later.

## Question 122

**Question:** Is age 18 a hard registration minimum, or only part of the target audience description?

**Answer:** Age 18 is not a hard registration minimum. The 18–30 range describes the target audience only.

## Question 123

**Question:** Does MVP enforce any minimum registration age?

**Answer:** No. MVP does not enforce a minimum registration age. Jurisdiction-specific age and parental-consent requirements must be reviewed before public launch.

## Question 124

**Question:** What information is mandatory when creating an account?

**Answer:** Mandatory:

- Email
- Password
- Username
- Display name

Profile photo, bio, and home city are optional.

## Question 125

**Question:** Must users verify their email address before they can use the app?

**Answer:** Yes. Email verification is mandatory.

## Question 126

**Question:** What may an unverified account do before completing email verification?

**Answer:** Public content can be browsed without any account. An unverified account has the same read-only access as a guest but cannot perform account actions until email verification is completed.

## Question 127

**Question:** Which content can a signed-out guest browse?

**Answer:** Signed-out guests can browse:

- Event pages and global ratings
- Public written reviews
- Artist pages
- Venue pages
- Public user profiles and ratings
- Search and discovery

Guests cannot rate, review, like, follow, mark **Will Be There**, or favorite artists or venues.

## Question 128

**Question:** What happens when a guest tries to perform an account-only action?

**Answer:** Show an account-required message only. Do not navigate away, open authentication automatically, save the intended action, or resume it later.

## Question 129

**Question:** Are user-created event lists included in MVP?

**Answer:** No. User-created event lists are excluded from MVP and recorded as a future feature.

## Question 130

**Question:** Can users select favorite events to feature on their profile in MVP?

**Answer:** Yes. A user may feature up to 3 favorite events on their profile.

## Question 131

**Question:** Must a favorite event already be in the user's Been history?

**Answer:** No. A user can feature an event as a favorite without having added it to Been.

## Question 132

**Question:** Can the user manually choose the display order of their three favorite events?

**Answer:** No. Favorite events are an unranked set, not a first-to-third ranking.

## Question 133

**Question:** In what order should the unranked favorite events be displayed?

**Answer:** Order by the date the user added each event to favorites. The earliest-added favorite appears first and the most recently added favorite appears last. The event's own date does not affect this order.

## Question 134

**Question:** Who can see a user's favorite events?

**Answer:** Use the same account-privacy rule as ratings:

- Public account: visible to everyone.
- Private account: visible only to approved followers.

Favorite artists follow the same visibility rule.

## Question 135

**Question:** How should a user's Been history be ordered on their profile?

**Answer:** By event date, newest event first. Adding an older event later places it at its historical position rather than at the top.

## Question 136

**Question:** How should Been ratings and written reviews be organized on a user's profile?

**Answer:** Use separate **Been** and **Reviews** tabs. **Been** contains all rated events. **Reviews** contains only events for which the user has a written review.

## Question 137

**Question:** How should a user's Reviews tab be ordered by default?

**Answer:** Default to review publication date, newest first. Visitors can switch to **Most liked**. Editing a review does not change its original publication date.

## Question 138

**Question:** Should the profile Reviews tab offer any additional sort options besides Newest and Most liked?

**Answer:** Yes. The profile **Reviews** tab has four sort options:

1. **Newest** — default
2. **Most liked**
3. **Oldest**
4. **Longest entry**

## Question 139

**Question:** Should the profile Been tab support filtering in MVP?

**Answer:** No. The **Been** tab shows event-date history newest first, with no filters or alternative sorting in MVP.

## Question 140

**Question:** Which statistics should appear on a user's profile in MVP?

**Answer:**

- Events in Been
- Written reviews
- Venues visited
- Cities visited
- Average rating given
- Followers
- Following

**Artists seen** is excluded.

These statistics follow account privacy and are hidden from outsiders on private accounts.

## Question 141

**Question:** Should a user profile show the distribution of ratings that user has given?

**Answer:** Yes. Show a Letterboxd-style distribution of the ratings the user has given. It follows the profile's account-privacy visibility.

## Question 142

**Question:** Which object types should global search return in MVP?

**Answer:** Global search returns:

- Events
- Artists
- Venues
- Users

Results are grouped by object type rather than mixed into one list.

## Question 143

**Question:** In what order should the four search-result groups appear?

**Answer:** **Users → Venues → Artists → Events**.

## Question 144

**Question:** Should search update live while the user types, or only after they submit the query?

**Answer:** Search results update live while the user types.

## Question 145

**Question:** How many typed characters are required before live search begins?

**Answer:** 1 character. Live search begins with the first typed character.

## Question 146

**Question:** What should the Search screen show before the user enters a query?

**Answer:** Recent searches.

## Question 147

**Question:** How many recent searches should be shown?

**Answer:** 10.

## Question 148

**Question:** Can users remove recent searches?

**Answer:** Yes. Users can remove individual searches and can clear all recent searches.

## Question 149

**Question:** How should results be ordered within each search-result group?

**Answer:** Exact and prefix matches first, followed by popularity.

## Question 150

**Question:** What should count as popularity for search ordering in MVP?

**Answer:**

- **Events:** number of Been ratings and active **Will Be There** users
- **Artists:** number of favorites and activity across associated events
- **Venues:** number of favorites and activity across associated events
- **Users:** follower count

Text relevance, especially exact and prefix matching, takes precedence over popularity.

## Question 151

**Question:** What should the website's primary navigation destinations be?

**Answer:**

- Home
- Search
- Activity
- Profile

## Question 152

**Question:** How should Home separate social activity from event discovery?

**Answer:** Home is social-only. Discovery is a separate fifth primary navigation destination placed second.

Final primary navigation order:

1. Home
2. Discover
3. Search
4. Activity
5. Profile

## Question 153

**Question:** Which activity types should appear in the Home feed in MVP?

**Answer:** Home shows these activities from people the viewer follows:

- New **Been** ratings, with optional written reviews
- New **Will Be There** activity
- New follows
- Review likes
- Newly selected favorite events
- Newly selected favorite artists

Profile changes do not appear. Favorite venues remain private and do not appear.

## Question 154

**Question:** Which sections should the Discover screen contain in MVP?

**Answer:**

- Upcoming near the user's home city
- Popular upcoming events globally
- Popular recent events
- Events featuring favorite artists
- Events at favorite venues
- Recommended events based on ratings and favorites
- Popular artists
- Popular venues

## Question 155

**Question:** What should happen to the home-city discovery section when the user has not selected a home city?

**Answer:** Show a prompt to choose a home city in place of the local section. The rest of Discover remains available.

## Question 156

**Question:** Can users temporarily browse a city other than their saved home city?

**Answer:** Yes. Browsing another city does not change the user's saved home city.

## Question 157

**Question:** Does “Upcoming near this city” mean events strictly inside the selected city, or also events within a surrounding distance?

**Answer:** Events strictly assigned to the selected city. Do not expand by distance or metro area.

## Question 158

**Question:** Should cancelled events remain publicly viewable?

**Answer:** No. Cancelled events are hidden from public view and removed from normal catalog browsing and discovery.

## Question 159

**Question:** If an event is marked cancelled after users already added it to Been, what happens to those entries?

**Answer:** Cancellation is actionable only when the source supplies an explicit cancellation signal.

- **Explicit cancellation on a future-dated event:** Hide the event and delete all associated user content and activity, including Been entries, ratings, reviews, review likes, **Will Be There** states, and related feed items. In the normal case, this primarily removes **Will Be There** and feed activity because Been logging has not opened.
- **Explicit cancellation on a past-dated event:** Hide the event but preserve all user-created history. Past Been entries, ratings, reviews, and likes are never deleted by a source correction. Record the condition for later review.
- **Event absent from source listings without an explicit cancellation signal:** The catalog lifecycle may hide the event, but all user content is preserved.
- **Source fetch failure:** No event or user-content state changes.

The explicit-cancellation branch may be implemented only after source reconnaissance confirms how Resident Advisor expresses cancellation in its schema. There is no staff role in the product.

## Question 160

**Question:** Can ordinary users create missing event pages in MVP?

**Answer:** No. Every canonical event must come from the future external catalog source.

## Question 161

**Question:** Can users submit a request for a missing event to be added?

**Answer:** No. MVP has no missing-event request flow.

## Question 162

**Question:** Can users report incorrect event, artist, or venue information in MVP?

**Answer:** No. MVP has no catalog-correction reporting flow.

## Question 163

**Question:** If an event is postponed to a new date, should it remain the same event page?

**Answer:** The external catalog source controls postponement data. The existing canonical event is refreshed with the new date when the source updates it.

## Question 164

**Question:** If a Will Be There event is postponed, should the user's Will Be There status remain attached to the new date?

**Answer:** Yes. The **Will Be There** status remains attached to the event and follows it to the new date.

## Question 165

**Question:** Should users marked Will Be There receive an in-app notification when the event date changes?

**Answer:** No. The **Will Be There** status silently follows the event to its new date.

## Question 166

**Question:** Should users marked Will Be There also be notified if the venue or start time changes?

**Answer:** No for MVP. Date, venue, and start-time updates do not generate notifications.

## Question 167

**Question:** If an event is cancelled, should users marked Will Be There receive an in-app cancellation notification before the event disappears?

**Answer:** No for MVP. Cancelled events disappear silently.

## Question 168

**Question:** Can users report written reviews or user profiles in MVP?

**Answer:** Both. Users can report written reviews and user profiles.

## Question 169

**Question:** How are reports resolved if there is no staff-facing role in the product?

**Answer:** MVP captures and stores report data only. Report review and resolution behavior will be decided later. Reports do not automatically hide content.

## Question 170

**Question:** What information must a user provide when submitting a report?

**Answer:** A required free-text explanation only. There are no predefined reason categories in MVP.

## Question 171

**Question:** What is the maximum length of a report explanation?

**Answer:** 1,000 characters.

## Question 172

**Question:** Can the same user submit multiple reports against the same review or profile?

**Answer:** Only one report per user per target.

## Question 173

**Question:** Can a user withdraw or edit a submitted report?

**Answer:** No. Submitted reports cannot be edited or withdrawn in MVP.

## Question 174

**Question:** When a user deletes their account, what happens to their ratings, reviews, likes, follows, favorites, and Will Be There activity?

**Answer:** Match Letterboxd's account lifecycle:

- The user may first deactivate the account.
- Deactivation immediately hides the profile and all associated content, removes its activity from public views, and disables sign-in.
- A deactivated account can be reactivated through an emailed recovery link.
- The user may request permanent deletion.
- Permanent deletion is scheduled for 90 days after the request.
- The recovery email may offer an option to shorten the waiting period to 30 days, but never less than 30 days.
- The account may be reactivated during the waiting period.
- After permanent deletion completes, the account and its ratings, reviews, likes, follows, follow requests, favorites, notifications, reports, and **Will Be There** activity cannot be restored.
- Permanently deleted ratings stop contributing to event averages and distributions.

## Question 175

**Question:** What happens to a deactivated account's username?

**Answer:** Match Letterboxd. Deactivation immediately releases the username for another account to claim. The 30-day username-change cooling period does not apply to deactivation.

## Question 176

**Question:** If a deactivated user returns after someone else has claimed their former username, what should happen?

**Answer:** Match the constraints of Letterboxd's policy. If the former username is still available, restore it. If another account has claimed it, require the returning user to choose a new available username before reactivation completes.

## Question 177

**Question:** Should users be able to report or hide Home-feed activity they do not want to see?

**Answer:** No per-item hide control in MVP. Unfollowing is the only feed-control mechanism.

## Question 178

**Question:** When a user unfollows someone, should that person's existing items disappear from Home immediately?

**Answer:** Yes. Their existing Home-feed items disappear immediately.

## Question 179

**Question:** What should the Activity destination contain?

**Answer:** Only notifications about the current user, including likes, follows, follow requests, and follow-request acceptances. It does not include a second followed-user activity tab because that activity already appears on Home.

## Question 180

**Question:** How should Activity notifications be ordered and marked read?

**Answer:**

- Newest first
- Unread notifications are visually distinct
- Opening a notification marks it read
- A **Mark all as read** action is available

## Question 181

**Question:** What should the MVP Recommended events section use to personalize results?

**Answer:**

- Favorite artists
- Favorite venues
- Artists and venues from highly rated Been events
- Home or browsing city
- Popularity as a fallback

No machine learning is required for MVP.

## Question 182

**Question:** Should the Recommended events section contain only upcoming events?

**Answer:** Yes. It contains only upcoming events and excludes events already in the user's Been history.

## Question 183

**Question:** What time window defines Popular recent events?

**Answer:** The previous 30 days.

## Question 184

**Question:** Which engagement signals determine event popularity on Discover?

**Answer:**

- Number of Been ratings
- Number of written reviews
- Number of review likes
- Active **Will Be There** count for upcoming events

Average star rating is a separate quality signal and is not itself popularity.

## Question 185

**Question:** How should the four popularity signals be weighted?

**Answer:** For MVP, use a simple unweighted sum:

`Been ratings + written reviews + review likes + active Will Be There users`

More sophisticated weighting is recorded as a future improvement.

## Question 186

**Question:** Can a user remove only their star rating while keeping the event in Been?

**Answer:** Yes. A rating is required when the event is first added to Been, but the user may remove that rating later while keeping the event in Been. The entry becomes an unrated attendance record and stops contributing to the event's averages and distribution.

## Question 187

**Question:** If the user removes the rating, can their written review remain published?

**Answer:** No. Removing the rating permanently deletes the written review and all of its likes. The unrated Been entry remains.

## Question 188

**Question:** Should removing a rating require confirmation?

**Answer:** Yes. The confirmation must warn that the written review and its likes will also be permanently deleted when present.

## Question 189

**Question:** What happens to the original Home-feed item when a user removes the rating but keeps the event in Been?

**Answer:** The original Home-feed item disappears. The unrated attendance remains visible in Been according to account privacy.

## Question 190

**Question:** If the user later rates that unrated Been event again, should it create a new Home-feed item?

**Answer:** Yes. Re-rating the event creates a new Home-feed item.

Unrated Been entries still count as events in Been, but do not contribute to rating averages or distributions.

## Question 191

**Question:** In Your Circle, where do rating-only entries appear when sorting by Longest entry?

**Answer:** Not applicable. **Longest entry** was removed from the event-page Your Circle section.

## Question 192

**Question:** When two reviews tie under Most liked or Longest entry, which appears first?

**Answer:** Partially superseded. **Longest entry** was removed from event pages. A tie-breaker for **Most liked** is defined in the next question.

## Question 193

**Question:** When two Public reviews have the same like count under Most liked, which appears first?

**Answer:** The review written by the more popular account appears first.

## Question 194

**Question:** What determines account popularity for this tie-breaker?

**Answer:** Follower count.

## Question 195

**Question:** If tied reviews also have authors with the same follower count, which appears first?

**Answer:** Yes. **Most liked** ordering uses:

1. Like count, descending
2. Author follower count, descending
3. Review publication time, newest first

## Question 196

**Question:** Should an event's global rating be the simple arithmetic average of all currently valid user ratings?

**Answer:** Yes. Use a simple arithmetic average. Every user contributes at most one current rating and every rating has equal weight.

## Question 197

**Question:** How many ratings from people the viewer follows are required before the Your Circle average appears?

**Answer:** 1. The Your Circle average does not use the global 3-rating threshold.

## Question 198

**Question:** Should the viewer's own rating be included in their Your Circle average?

**Answer:** Yes. Your Circle average includes the viewer's own rating plus ratings from people they follow.

## Question 199

**Question:** What should signed-out guests see where an event page normally shows Your Circle?

**Answer:** Show a prompt to log in and see friends' ratings. The global rating and Public reviews remain browsable.

## Question 200

**Question:** Which physical music-event formats are included in MVP?

**Answer:** The product design supports concerts, club nights, DJ sets, day parties, and festivals, provided they satisfy the catalog requirements. Multi-day festivals follow the external source's event boundaries.

**Catalog-scope amendment:** The product remains genre-agnostic. All application behavior—Been, ratings, reviews, social activity, profiles, and discovery—works identically for every kind of physical music event. However, MVP catalog coverage is limited to Resident Advisor listings in the seeded launch cities. Events outside RA's coverage, such as the Shakira at Madison Square Garden example, may not exist in v1. This is a source-coverage limitation, not a product exclusion.

Canonical Event, Venue, and Artist records are source-neutral. Provider identifiers live in `EXTERNAL_IDENTITY`, not on canonical records. Adding a future provider requires no catalog schema change, but does require an entity-matching process whose output attaches provider identities to canonical records through `EXTERNAL_IDENTITY`. Cross-source matching is future work, not an automatically solved property.

## Question 201

**Question:** What should a signed-out guest see as the website's default landing destination?

**Answer:** Discover.

## Question 202

**Question:** What should a signed-in user's default landing destination be?

**Answer:** Home.

## Question 203

**Question:** What should a newly verified user be asked to do before entering Home for the first time?

**Answer:**

1. Optionally choose a home city.
2. Optionally select favorite artists.
3. Optionally select favorite venues.
4. Optionally follow suggested users.
5. Enter Home.

Every step is skippable.

## Question 204

**Question:** Are newly created accounts public or private by default?

**Answer:** Neither. The user must explicitly choose **Public** or **Private** during account setup. This choice cannot be skipped.

## Question 205

**Question:** Can users switch between Public and Private at any time from settings?

**Answer:** Yes. Users can switch between Public and Private at any time from settings. Existing followers and pending requests transition according to Questions 35 and 36.

## Question 206

**Question:** Can users change their email address, and must the new address be verified before the change takes effect?

**Answer:** Yes. The new email address does not take effect until it has been verified.

## Question 207

**Question:** What name should the product specification use for the app?

**Answer:** Onda.

## Question 208

**Question:** How should a multi-day festival be represented?

**Answer:** Follow the external catalog source's event boundaries. One source event record becomes one Onda event. Onda does not independently split or merge festival records.

## Question 209

**Question:** How should rating-distribution values be presented?

**Answer:** Relative bar lengths only, without visible raw counts or percentages.

## Question 210

**Question:** What happens when a signed-out guest starts an account-only action?

**Answer:** Show an account-required message only. The guest remains on the current page, and the action is not saved or resumed.

## Amendment to Question 75

Question 75's requirement for a specific venue means that published events cannot
be venue-less. A venue record legitimately named **TBA**, unknown, undisclosed, or
similar by the external source is still an ordinary venue and is accepted as source
truth. Onda does not filter venues by name or parse event titles to override the
source. This follows Question 8's principle that Onda preserves the external
catalog source's event boundaries rather than independently reinterpreting them.

## Temporary amendment to Questions 125–126

Email verification is deliberately deferred during the identity-only development
slice; it is not cancelled. Accounts are temporarily created active and signed in
immediately without verifying their email address. The user schema still records the
nullable email-verification state required by the frozen design, but no behavior in
this slice reads that field or uses it as an authorization gate.

Before any public deployment or account actions beyond identity are introduced, a
later repayment slice must add the mandatory verification flow. That slice will
change both temporary behaviors: registration will no longer grant an active,
immediately usable signed-in account, and the user will instead be directed to check
their email and complete verification before account actions.

The current-session API may return an authenticated user's email to that same user.
Email is self-only account data and must never be included in any future serializer
for another user's profile, reviews, feed activity, or other public/social surface.

## Amendment to Questions 13–14 and 73–74

Been logging opens at the event's scheduled venue-local wall-clock time. On the
fall-back daylight-saving transition, an ambiguous scheduled time opens at its
first occurrence. On the spring-forward transition, a nonexistent scheduled time
opens immediately after the clock jump. A missing source start time continues to
mean venue-local midnight on the event date. This is a display-boundary ruling; it
does not invent source precision or convert the catalog's local date and time.

## Implementation note for Questions 186–188

Removing a rating while keeping a Been entry is supported before written reviews
exist. The current confirmation states that the event remains in Been. The reviews
slice must extend that warning to explain and apply the review- and like-deletion
consequences required by Questions 187–188; those consequences are vacuous until
review records exist.

## Amendment to Question 136

Question 136's phrase “Been contains all rated events” predates the unrated-entry
lifecycle established by Question 186. The later lifecycle ruling governs: the
Profile **Been** tab contains all preserved Been attendance entries, including entries
whose rating has been removed. Removing a rating does not make the attendance entry
disappear from its owner's Been history. The **Reviews** tab remains limited to
entries with a written review.

## Interim implementation note for Question 154

Before event-engagement signals are meaningful, Discover includes a city-scoped
**Recent events** section ordered by recency through the existing past-events
catalog contract. This is a plain recency list, not Question 154's **Popular recent
events** section. It is an interim stand-in only; the popularity-ranked version
remains deferred until its specified engagement signals can support a truthful
ranking.

## Amendment to Question 158

Question 158's cancellation-hiding rule applies only when cancellation is conveyed
by a trustworthy structured source signal. Cancellation prose in an event title does
not hide the event: Onda preserves the title and keeps the event visible under its
ordinary derived lifecycle. The live Boston catalog example `[CANCELLED] Nocturnal
District presents: Rooftop Sessions 02` demonstrates why this distinction is
user-visible.

The ingestion pipeline must not interpret title text, strip cancellation markers,
or synthesize lifecycle state from prose. This is consistent with Question 75's TBA
venue amendment, Question 8's follow-the-source principle, and the no-title-parsing
invariant. Structurally absent events already move through the three-miss
unverified-to-hidden lifecycle. A future structured cancellation feature requires
new source evidence and an explicit contract amendment.

## Amendment to Questions 34–36: follow approval time

The follow relationship records both its immutable initiation time and, separately,
the moment it becomes approved. `FOLLOW.approved_at` is NULL while a private-account
request is pending and non-NULL exactly when `status = approved`; the database
enforces that biconditional. Public follows set initiation and approval together.
Manual and private-to-public bulk acceptance preserve the original request time and
record the true approval transition time.

This application-schema freeze-break preserves a domain event at the only moment it
can be recorded accurately. Deferring the column and later backfilling it from the
request timestamp would permanently invent false approval times for delayed
acceptances. Follow activity therefore orders by approval time, while initiation
time remains available as distinct lifecycle evidence.

## Interim implementation note for Question 205

The follow-graph slice delivers and contract-tests the authenticated privacy-change
API, including transactionally serialized public/private transitions and pending
request auto-acceptance. It does not add a Settings or Profile control. Question
205 is therefore service-complete but surface-pending until the Profile/Settings
slice supplies its final UI. No interim Settings destination or navigation organ is
introduced.

## Interim implementation note for Questions 34 and 38

Until Search and Profile make users—including private accounts—discoverable, the
only temporary follow control appears on public-review author bylines. It supports
following and unfollowing those public authors. Guests see no control, author names
do not link to a nonexistent profile route, and private follow-request initiation
remains API-complete but unavailable through the current UI. The Profile slice
absorbs this control into `/u/{username}`; Search/Profile delivery supplies the
human-reachable private-request flow required by Question 38.

## Amendment to Question 59

**Your Circle** orders entries by `rated_at DESC, entry_id DESC`. `rated_at` is
the one honest activity timestamp shared by rating-only and reviewed entries. Rating
edits remain in place, later review publication or editing does not move an entry,
and removing then restoring a rating creates fresh activity as required by Question
190. The entry ID is a technical stable-pagination tiebreak, not a second product
ranking signal.

## Named Slice 4B follow-ordering obligation

Slice 4A records true follow approval time but has no Home or approved-follow
ordering surface. Slice 4B must contract-test both consequences when Home consumes
the relationship: a delayed private-request acceptance sorts by `approved_at`, not
the preserved request `created_at`; and bulk same-time approvals order
deterministically through the frozen heterogeneous feed tiebreak.

## Amendment to Questions 102, 153, 178, and 189–190

Home is assembled at query time from source-of-truth activity rows; it has no feed
table and performs no fan-out writes. Rated Been activity uses immutable `rated_at`,
approved-follow activity uses `approved_at`, and review-like activity uses the
like's `created_at`. Source querysets are combined with `UNION ALL` in the database
before cursor pagination. The frozen descending key is `(activity_at,
activity_type, source_key)`, where activity type is a stable lexical discriminator
and source key is a fixed-width source-scoped identifier. This is a technical
pagination rule, not product prioritization.

Visibility is enforced inside every union branch. A review-like item exists only
when its liked review is visible to the feed viewer; hidden events suppress their
event-backed items and resurrection restores them. Removing a source row makes its
item disappear without cleanup copies. Future Will Be There, favorite-event, and
favorite-artist sources must join this same database union and cursor key. They may
not be fetched and merged in Python.

## Amendment to Question 93

Will Be There attendee lists order newest marks first by `created_at DESC`, with
`user_id DESC` as the stable technical pagination tiebreak. This is the same recency
convention used by other activity surfaces; the user ID does not represent product
ranking. Public and Your Circle attendee sections paginate independently.

Expired rows are retained logically rather than swept: physical deletion would
destroy the settled requirement that Will Be There follows a postponed event to its
new date. Liveness is the venue-local calendar predicate `today <= event_date`.
Dormant rows are nonexistent on read surfaces but can become live again when the
canonical event date moves forward.

## Amendment to Question 138

The Profile Reviews tab's **Longest entry** sort orders by stored review-body length
descending, then original `published_at` descending, then review ID descending. The
newer-first product tiebreak follows the established final recency key used by review
ordering; the ID is only a stable technical pagination tiebreak. Review edits retain
their original publication time and therefore cannot manufacture a newer tie position.

## Amendment to Question 119

Profile bios are stored verbatim and measured against the 150-character limit exactly
as stored. Surrounding whitespace and line breaks are not trimmed when at least one
visible character exists. An empty or whitespace-only submission is semantically empty
and normalizes to NULL; this normalization does not alter any nonempty bio text.

## Amendment to Questions 84–85

The owner's private favorite-venues list orders by `added_at ASC, venue_id ASC`.
This applies the same earliest-added-first chronology used by profile-facing event
and artist favorites; venue ID is only a stable technical tiebreak. The specification
is silent about favorite-venue order, so this is a product interpretation rather than
an inferred source rule.

## Amendment to Questions 93 and 196–198

An event exposes an anonymous-inclusive active **Will Be There** count. Every active
mark contributes regardless of account privacy, following the same aggregate-versus-
attribution separation used for ratings in Question 32. This count is distinct from
the privacy-filtered Public and Your Circle attendee lists: list pagination totals
must never be presented as the anonymous aggregate. Expired or otherwise dormant
marks do not contribute.

## Amendment: password reset and dark verification machinery

Password reset was not addressed by the original 210 questions. Onda supports a
non-enumerating email reset request followed by a six-digit code and a new password.
The request response never reveals whether an account exists. Codes expire after 15
minutes, permit at most five failed entry attempts, and may be resent after a 60-second
cooldown. A successful reset invalidates every existing session for that account.

Email verification uses the same six-digit-code lifecycle. Development delivery uses
Django's console email backend; a deployment provider remains a settings-only choice.
The machinery is initially built dark behind `EMAIL_VERIFICATION_ENFORCED`, whose
default is false. While false, the existing Questions 125–126 freeze-break remains
exactly in force: registration creates an active account, signs it in immediately, and
verification gates nothing. When deployment enables the flag, an unverified account
retains its own session and guest-equivalent public browsing but cannot perform account
actions until verification. Enabling the flag and changing registration's destination
remain explicit Milestone 5 deployment actions, not behavior of the dark build.

## Amendments — 2026-08-01/02 session

Each entry is an operator ruling made during the M4 polish/integration session.
Where an entry supersedes a numbered question, the original answer remains in
place as historical record; this block governs.

### Search (Q142–Q150, Q127)

- **Q143 superseded.** Search result groups render **Events → Artists → Venues → People**.
- **Q142 display label.** The Users group displays as **"People."** The object type remains User.
- **Added: scope row.** All · Events · Artists · Venues · People under the search bar. All = grouped results capped at 5 rows per group with "View all (N)" switching scope in place; single scopes render one cursor-paginated list.
- **Added: Discover city-scoped search** (component: DiscoverSearch). Events-only inline search on Discover scoped to the selected city; thin results (<3) append a "Search all cities →" tail routing to /search with the query.
- **Removed: desktop header quick-search.** Built, then cut by ruling (commit 879b1f3) after repeated interaction failures. The Search nav entry routes directly to /search on all widths. The Search page and DiscoverSearch are the only search surfaces. Recorded as a dated delta in search-handoff.md.
- **Q145 upheld.** Live search fires at 1 typed character (~250ms debounce).
- **Q146–148 upheld.** Pre-query state shows up to 10 recent searches, newest first, per-row remove, Clear all.
- **Added: recents recording rule.** A recent search is recorded only on commit signals — opening a result, pressing Enter, or activating a scope/"View all" with an active query. Live-search fires never record. Recording dedupes case-insensitively and removes existing prefixes of the new query. Client-side storage (localStorage).
- **Search is chrome.** Zero judgment color anywhere in search UI.

### Profile statistics and identity (Q140, Q141)

- **Q140 amended.** Followers and Following are **not statistics**. They are social-identity data rendered in the profile header beside the name/@handle, and they are **publicly visible on every profile, including private profiles viewed by outsiders** (counts only — follower/following lists and all other private-profile visibility rules unchanged; backend commit 50caa91). The STATISTICS module holds five items: Events in Been, Written reviews, Venues visited, Cities visited, Average rating given.
- **Statistics presentation.** Horizontal strip, numeral-above-label, one shared label baseline. Events in Been leads (largest numeral, first). Average rating given is the only judgment stat (numeral in judgment color) and forms one visual unit with the rating-distribution histogram. Desktop fits a profile-specific 988px measure with zero scroll (documented exception to the 800px ledger); mobile is a three-row restructure with zero horizontal scroll.
- **Q141 amended.** Rating distribution is a compact vertical ten-bar histogram (½★→5★), all bars in judgment color, counts on hover/tap only. **It always renders** — the interim ≥5-ratings gate was removed by ruling; zero-count buckets render as baseline stubs. Sizing is placement-driven: ~104×30 inside the statistics strip (data register — top of tallest bar aligns with the average numeral), 160×100 standalone. The minimum-n display question from the patch-1 backlog is reopened (unanswered) by the gate's removal.

### Sorting controls (Q137, Q138)

- Review sorting uses the custom sort menu component (no native selects): quiet right-aligned "Newest ▾" on the tab-row baseline, panel-register menu, keyboard/Esc/outside-click, selected = ink 600, focus/hover = subtle wash. Profile Reviews tab carries Q138's four options; the event page carries its two (Newest default, Most liked). No caps overline labels a sort control. Native form selects survive only as intentional form inputs on the Edit surface.

### Event page

- **Rating input.** Native select replaced by StarInput: ten-step (0.5–5.0), half-star hit zones, drag scrub, keyboard ←/→ 0.5 steps, slider a11y; selected fill in judgment color; committed numeral beside. Interaction conform (hover preview, frictionless re-adjustment) ordered this session (STARINPUT-INTERACTION-CONFORM).
- **Owner block.** The five per-item caps sections collapsed into one hairline-topped headerless block; contents gate on event state from venue-local time. Upcoming: Mark Will Be There + Add favorite, WBT count takes the color slot, zero rating/review chrome (verified live both directions). Past, unrated: StarInput + quiet Add favorite. Past, rated: entry lives in the review column as "Yours" + "Edit ▾".
- **Plural grammar (product-wide).** Zero-form sentences ("No active marks yet."), correct singular/plural elsewhere ("1 active mark" / "N active marks"). Closes the pluralization backlog item.
- **Review rows.** Feed grammar adapted in place: avatar 26 (image or initials) + reviewer name fn 600 (no underline; the profile-header display-face override does not apply) + @handle micro muted; rating as judgment-color star glyphs, never text; body in quiet prose with line clamp and inline "more" expanding in place; like count micro + quiet Like/Unlike; shared anatomy across Circle, owner entry, and Public reviews. Circle aggregate remains a sentence (stars-for-numeral unruled).
- **Favorite cap rejection.** The rejection message persists (invariant 26) and the control returns to a usable resting state; retry re-issues the request.
- **Error register.** 12px wine text + tinted field border — first ruled use on the favorite-cap rejection; now the product-wide error treatment (also used across auth).

### Profile surface

- Page composition: identity header (72px avatar; display name in display face — see design-system override below; @handle · City metadata line with silent absence; F/F counts; bio quiet prose or silently absent; owner sees quiet "Edit profile" link) → statistics strip → Been | Reviews tabs → rows. Empty states are single quiet lines; no orphaned overlines; no "No bio." placeholders.
- **Tab register (product pattern).** Text tabs fn 14, active ink 600 with a 2px action-color indicator flush on the full-width hairline, resting muted, never underlined. Only content below the hairline swaps.
- **Been/Reviews rows.** EventListRow anatomy: flier thumb, display-face event name, meta line, judgment element as small stars (never "2.0 stars" text), "Written review" marker, "Unrated attendance" preserved; whole row navigates.
- **Avatar mechanic (v1).** Initials-avatar is the real default (1–2 initials on the avatar-gray circle); "Avatar URL" is an advanced text field on the Edit surface. The words "Default avatar" never render.
- **Edit Profile** lives at /settings/profile in the auth-column register (360px centered; caps micro labels; bordered-ink primary "Save changes" — no filled buttons; live "0 / 150" bio counter; custom city dropdown styled to the input register; privacy radio pair with consequence copy; follow-requests section). No edit-form content on the profile page.
- **FollowControl.** One fixed box across all states (Follow / Unfollow / Request to follow / Requested): 32px high, min-width 150, centered text, zero layout shift on toggle.
- **Favorites** render as hairline-separated rows (name in row-title register + micro meta), never inline link prose.

### Home feed

- **One feed-item anatomy across all six Q153 activity types.** Actor line: avatar 26 + name fn 600 + quiet action phrase; object names in display face; event-bearing items carry the flier thumb; ratings as judgment-color star glyphs; review excerpts clamp at four lines with an inline "more" routing to the event ("more" renders only when actually truncated).
- **Verb-survival rule.** Actor/object names may truncate; the action phrase is always visible at every width. A feed item never loses its verb.
- **Timestamps (product-wide feed rule).** Compact relative timestamps ("18h", "2d"), right-aligned, applied on Home and Activity. Closes the feed-timestamp backlog item.
- **Layout.** 800px ledger centered; no page title — the feed begins directly. Empty state: one line ("No activity from people you follow yet.") + a single bordered "Discover events" affordance.
- Presentation-field serializer amendment: see Backend contract amendments.

### Discover

- **City is the page title** (display face); the "Discover" H1 is removed — nav already names the destination. City dropdown + DiscoverSearch render as one matched control pair (header-band pattern): right of the title on desktop, stacked on mobile.
- **No "Venue:" / "Artists:" labels anywhere.** Metadata self-identifies in quiet meta lines (compact date · venue).
- **Lineups collapse on rows**: 2–3 names in listing order + "+N". The full lineup in listing order belongs to the event page only.
- Rows: flier thumb, display-face title clamped at 2 lines (never underlined or free-wrapping), compact date grammar, "venue TBA" quiet in-register, whole row navigates via canonical slug routes. Upcoming/Recent in the tab register with independent pagination.
- **Flag (undesigned):** Recent-tab rows are past events and may warrant a compact judgment element; anatomy currently assumed identical to Upcoming.

### Authentication

- **Login accepts username or email** (backend amendment da851a3, case-insensitive). Non-enumerating: unknown-identifier and wrong-password produce byte-identical error responses; one error message covers both, with an inline "reset your password" link.
- **Registration contract defended**: username, email, password, display name, and explicit Public/Private selection — all five, in the auth-column register. The handoff's three-field reduction was rejected and recorded as a dated delta.
- **Password reset** keys on email only; three steps; the request confirmation uses non-enumerating copy verbatim ("If an account exists for …"). Code-entry screens (reset and verification) display "Codes expire after 15 minutes."
- **Verification screen** renders wordmark-only chrome and stands alone as the future post-registration landing. Resend confirmation ("Code sent.") is quiet ink — success states are chrome, never judgment color.
- All auth surfaces: auth-column register, wine error register, no judgment color, no filled buttons.

### Session / navigation

- **Logout affordance.** The header account element (@handle, quiet) opens a flat panel menu: "Edit profile" → /settings/profile, "Log out" → POST /api/auth/logout, clears session, routes to Discover. Guests render Register (bordered-ink acquisition affordance) · Log in (quiet text) in the same position; no account element.
- **Public URLs are slug-first, ID-last**: /e/{slug}-{id}, /v/{slug}-{id}, /a/{slug}-{id}. The trailing numeric ID is the sole lookup key; slugs are derived on render (no storage, no uniqueness constraints). Bare-ID, stale-slug, and legacy numeric paths self-heal to the canonical URL via client-side replace; production adds true HTTP 301s by giving Django ownership of the public entity paths (deploy line-item). /u/{username} unchanged.

### Backend contract amendments (all additive, all with operator-ruling provenance)

1. **7114de7** — Home feed payload: actor avatar (nullable), event cover_image_url (nullable), venue name, city. Union membership, ordering, cursors, visibility, deletion asserted unchanged.
2. **2fb1f78** — Public-review authors and Circle users: nullable avatar, same field name and null semantics as (1) — one avatar-delivery pattern across attributed payloads.
3. **88efdf1** (within slug work) — additive event_title on review-like notifications so Activity emits canonical links.
4. **da851a3** — username-or-email authentication (see Authentication).

Ruling standard applied to all four: presentation/identity data on rows the viewer is already entitled to see, through the sanctioned named boundary; invariants 19–22 asserted by test; counts-vs-lists distinction preserved (aggregate counts are not list access).

### Verification-enforcement slice — status change

All three M5 prerequisites are **complete and on main** (c147d74, 42cc60b, a1b294f): guest-equivalent reads for unverified sessions, self-only verification state in session payloads, flag-on routing to /verify-email. Flag-off behavior proven byte-identical to the legacy contract. The slice is code-complete and armed; remaining work is deployment-only (flag flip, email provider, landing flow).

### Design-system rulings

- **Allocation rule ratified as settled law (color clause).** Judgment color means *someone judged something* — stars, likes, averages, distributions, WBT counts on upcoming events — and nothing else. Chrome, nav, wordmark, buttons, statistics: ink. Challenged twice in session (all-stats-green; brand-green including nav/wordmark; Register-in-green), upheld each time, and confirmed by operator ruling after evaluating flier-dense pages ("semantic green, done"). Warmth is carried by imagery per the brief. Legitimate extensions: marked/favorited control states may carry judgment color; the judgment-unit pattern (average numeral + histogram as one object).
- **Display-face override (scoped).** User display names render in the display face on **profile headers only** (20/24px); names in rows, reviews, feeds, and search remain functional 600.
- **Page-title convention is contextual**: the city name titles Discover; Home has no title (the feed begins); "Discover"/"Home" H1s are dead.
- **New composed patterns blessed via approved renders**: header band (title + matched control pair), tab register, sort menu, account menu, FollowControl fixed box. Account menu and sort menu are flagged for a formal Claude Design blessing pass (composed from existing registers; low risk).
- **Panel register enforced**: flat — bg + 1px strong border, no shadow, no filter — across search panels, sort menus, the account menu, and the city dropdown menu. Focus/hover rows use the subtle background wash everywhere.
- **988px profile statistics measure** is a documented exception to the 800px ledger, scoped to the statistics strip only.

### Process rulings

- **Markdown-only handoff authority** (34e21d9; AGENTS.md): the .md in frontend/design-handoffs/ is sole authority; no spec HTML lives in the repo; visual disputes escalate to the operator. Handoff citations of spec/*.html files are historical dead references.
- **Every order gets a report**, even "already shipped in X" — two completions shipped unreported this session and had to be reconstructed from git.
- **Approved orders push by default**; a push is held only when the order says so or unrelated work would publish (then ask).
- **Design-by-exception provenance**: the statistics strip was designed by Codex under a fully-constrained prompt and ratified from the render — recorded as exception, not precedent.

### Dated addendum — 2026-08-02, second wave

- **StarInput and shared stars.** Half-star geometry is fixed and all star rendering converges on shared `RatingStars` (`53fa4c5`, `f2c0dfe`); operator live-verified.
- **Imagery-polish wave** (`3d2b68b`, `70799b7`, `21567db`). Product-wide initial-on-tone placeholders replace empty image slots, with the full-bleed hero excluded. Favorites use full-row anatomy with three types in one list. Avatar upload replaces the URL field using local media, a 2MB cap, and a server-side 512px square center-crop. Event pages use label-free metadata and a quiet “Lineup” header with a display-face headliner. Discover Recent rows show average stars at three or more ratings and remain silent below that surface-scoped minimum-n threshold. Grouped feed items apply only to one-line types; rated and WBT items never group. Account and sort menus are blessed. Failed image URLs fall through the shared placeholder.
- **Favorite heart control.** The `♡`/`♥` judgment grammar covers all six states, including cap-rejection composition. The first motion ruling is a 120ms ease-out scale on judgment commit only.
- **Favorites boundary and cap** (`70799b7`). The uniform cap is three per type, including venues. Grandfathered over-cap collections remain intact and removable, while additions are blocked until the collection is below the cap. Venue favorites are public under the standard account-privacy regime.
- **Repository formalization** (`2c73b00`). `.gitignore` is hardened, the README is recruiter-facing, and the full-history secrets audit was clean with zero rotations required. Design handoffs remain tracked under `frontend/design-handoffs/`.
- **Frontend quality audit and Fix A** (`00dd359`, `34ba1c0`). The read-only audit completed; Tier A plus B12 and B3 shipped: visible session failure with Retry, centralized null/failed avatar fallbacks, single-dispatch `ConfirmDialog`, bordered-ink as the global button default with zero exceptions, dead `ExpandableText` removal, the `DiscoverEventRow` split with Artist/Venue pages adopting its anatomy and the last labeled prose removed, neutral `SortMenu`, and honestly relabeled source-assertion tests. The Tier B refactor slice and browser-DOM test slice enter the backlog with the audit report and coverage map as their specification. The A1 error-slot placement awaits design blessing.
- **Repository artifact cleanup** (`f1d6370`). Personal notes and the archived app-screen HTML were removed.
