import { expect, test } from "@playwright/test";

const PUBLIC_ROUTES = [
  { name: "auth", path: "/login", heading: "Log in" },
  { name: "search", path: "/search", heading: "Search" },
  { name: "public shell", path: "/discover", heading: "Boston" },
];

const EMPTY_PAGINATION = {
  page: 1,
  page_size: 20,
  total_count: 0,
  total_pages: 1,
  next_page: null,
  previous_page: null,
};

const EVENT_ROW_FIXTURE = {
  id: 468,
  slug: "keep-on-leon-vynehall-open-to-close",
  title: "KEEP ON - Leon Vynehall (OPEN TO CLOSE)",
  event_date: "2026-08-27",
  start_time: "22:00:00",
  cover_image_url: null,
  venue: { id: 335, slug: "middlesex", name: "Middlesex", city: { id: 1, name: "Boston", timezone: "America/New_York" } },
  artists: [{ id: 842, name: "Leon Vynehall" }],
  rating_summary: { state: "unavailable", average: null, count: 0 },
};

const EVENT_DETAIL_FIXTURE = {
  id: 468,
  title: "Franky Rizardo - Flow",
  event_date: "2099-08-29",
  start_time: "22:00:00",
  cover_image_url: "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='160' height='200'%3E%3Crect width='160' height='200' fill='%23ECECEC'/%3E%3C/svg%3E",
  venue: {
    id: 335,
    name: "Pacha New York",
    city: { id: 8, name: "New York City", timezone: "America/New_York" },
  },
  artists: [
    { id: 842, name: "Franky Rizardo" },
    { id: 843, name: "Mason Collective" },
    { id: 844, name: "Ms. Mada" },
  ],
  will_be_there_summary: { active_count: 1 },
  viewer_will_be_there: { can_mark: true, is_marked: false, was_marked: false },
  viewer_entry: null,
};

const PAST_EVENT_DETAIL_FIXTURE = {
  ...EVENT_DETAIL_FIXTURE,
  event_date: "2000-08-20",
  rating_summary: { state: "unavailable", average: null, count: 1 },
  rating_distribution: { buckets: [] },
  viewer_favorite: { is_favorite: false, added_at: null },
  viewer_will_be_there: { can_mark: false, is_marked: false, was_marked: false },
  viewer_entry: {
    rating: 5,
    rated_at: "2026-08-20T12:00:00Z",
    review: { id: 14, body: "Incredible.", published_at: "2026-08-20T12:00:00Z", like_count: 0, viewer_has_liked: false },
  },
};

const FOLLOW_REQUEST_FIXTURES = [
  { user: { id: 8, username: "first_listener", display_name: "First Listener", avatar: null }, created_at: "2026-08-27T12:00:00Z" },
  { user: { id: 9, username: "second_listener", display_name: "Second Listener", avatar: null }, created_at: "2026-08-27T13:00:00Z" },
];

const PROFILE_EVENT_FIXTURE = {
  ...EVENT_ROW_FIXTURE,
  event_date: "2000-08-20",
  cover_image_url: null,
};

const PROFILE_FIXTURE = {
  profile: {
    id: 7,
    username: "onda_test",
    display_name: "Onda Test",
    avatar: "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='160' height='160'%3E%3Crect width='160' height='160' fill='%236E6E6E'/%3E%3C/svg%3E",
    bio: "Finding the rooms worth remembering.",
    home_city: { id: 1, name: "Boston", timezone: "America/New_York" },
    follower_count: 846,
    following_count: 792,
  },
  access: "owner",
  account: { is_private: false },
};

const PROFILE_STATS_FIXTURE = {
  statistics: {
    events_in_been: 18,
    written_reviews: 7,
    venues_visited: 12,
    cities_visited: 3,
    average_rating_given: { state: "available", value: 4.5 },
  },
  rating_distribution: {
    state: "available",
    buckets: Array.from({ length: 10 }, (_, index) => ({ rating: (index + 1) / 2, count: index === 8 ? 5 : 0, relative_value: index === 8 ? 1 : 0 })),
  },
};

const DENSE_EVENT_ROW_FIXTURES = [
  EVENT_ROW_FIXTURE,
  {
    ...EVENT_ROW_FIXTURE,
    id: 469,
    slug: "an-extremely-long-event-title-for-capacity-validation",
    title: "AN EXTREMELY LONG EVENT TITLE WITH MULTIPLE ARTISTS AND AN OPEN-TO-CLOSE ANNOUNCEMENT",
    cover_image_url: "/failed-event-poster.jpg",
    venue: { id: 336, slug: "a-venue-with-a-long-name", name: "A Venue With A Deliberately Long Name" },
    artists: [
      { id: 843, name: "A Deliberately Long Artist Name" },
      { id: 844, name: "Another Deliberately Long Artist Name" },
      { id: 845, name: "Third Artist" },
    ],
  },
];

async function mockPublicApi(page, { authenticated = false, events = [], continuationFailure = false, initialEventFailure = false, eventDetail = EVENT_DETAIL_FIXTURE, notifications = [], followRequests = [] } = {}) {
  await page.route("**/api/**", async (route) => {
    const url = new URL(route.request().url());
    let body;
    let status = 200;

    if (url.pathname === "/api/auth/session/") {
      body = {
        user: authenticated
          ? { id: 7, username: "onda_test", display_name: "Onda Test", avatar: "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='26' height='26'%3E%3Crect width='26' height='26' fill='%236E6E6E'/%3E%3C/svg%3E", email: "test@example.com", is_verified: true }
          : null,
      };
    } else if (url.pathname === "/api/cities/") {
      body = { results: [{ id: 1, name: "Boston" }] };
    } else if (url.pathname === "/api/events/") {
      const pageNumber = Number(url.searchParams.get("page") ?? "1");
      if (initialEventFailure || (continuationFailure && pageNumber > 1)) {
        status = 500;
        body = { detail: "fixture failure" };
      } else {
        body = {
          results: events,
          pagination: {
            ...EMPTY_PAGINATION,
            total_count: events.length,
            total_pages: continuationFailure ? 2 : 1,
            next_page: continuationFailure ? 2 : null,
          },
        };
      }
    } else if (url.pathname === "/api/events/468/") {
      body = eventDetail;
    } else if (url.pathname.startsWith("/api/events/468/will-be-there/")) {
      body = { results: [], pagination: EMPTY_PAGINATION };
    } else if (url.pathname === "/api/events/468/circle/") {
      body = { rating_summary: { state: "unavailable", average: null, count: 0 }, results: [], pagination: { ...EMPTY_PAGINATION, total_results: 0 } };
    } else if (url.pathname === "/api/events/468/reviews/") {
      body = { results: [], pagination: { ...EMPTY_PAGINATION, total_results: 0 } };
    } else if (url.pathname === "/api/me/notifications/") {
      body = { results: notifications, next_cursor: null };
    } else if (url.pathname === "/api/me/notifications/read-all/") {
      body = {};
    } else if (url.pathname === "/api/me/follow-requests/") {
      body = { results: followRequests, pagination: { page: 1, page_size: 20, total_results: followRequests.length, total_pages: 1, next_page: null, previous_page: null } };
    } else if (url.pathname === "/api/users/onda_test/") {
      body = PROFILE_FIXTURE;
    } else if (url.pathname === "/api/users/onda_test/stats/") {
      body = PROFILE_STATS_FIXTURE;
    } else if (url.pathname === "/api/users/onda_test/been/") {
      body = { results: [{ id: 1, event: PROFILE_EVENT_FIXTURE, rating: 4.5, has_review: true }], pagination: EMPTY_PAGINATION };
    } else if (url.pathname === "/api/users/onda_test/reviews/") {
      body = { results: [{ id: 1, event: PROFILE_EVENT_FIXTURE, rating: 4.5, body: "The room, the sound, and the crowd all landed at once.", published_at: "2026-08-20T12:00:00Z", like_count: 0 }], pagination: EMPTY_PAGINATION };
    } else if (url.pathname === "/api/users/onda_test/favorites/") {
      body = { events: [], artists: [], venues: [] };
    } else if (url.pathname === "/api/search/") {
      body = { results: [], next_cursor: null };
    } else {
      body = {};
    }

    await route.fulfill({
      status,
      contentType: "application/json",
      body: JSON.stringify(body),
    });
  });
}

async function openRoute(page, route, options) {
  await mockPublicApi(page, options);
  await page.goto(route.path);
  await expect(page.getByRole("heading", { level: 1, name: route.heading })).toBeVisible();
  await expect(page.getByText("Checking session…")).toHaveCount(0);
}

async function expectNoHorizontalOverflow(page) {
  const widths = await page.evaluate(() => ({
    client: document.documentElement.clientWidth,
    scroll: document.documentElement.scrollWidth,
  }));
  expect(widths.scroll, `document width ${widths.scroll}px exceeds viewport ${widths.client}px`).toBeLessThanOrEqual(widths.client);
}

async function expectChromeClearsMain(page, isMobile) {
  const geometry = await page.evaluate(() => {
    const root = document.querySelector("body > div");
    const header = document.querySelector("header.site-header");
    const account = header?.querySelector(":scope > section");
    const main = document.querySelector("main");
    const rootStyle = getComputedStyle(root);
    const rect = (element) => element?.getBoundingClientRect().toJSON();
    return {
      viewportHeight: window.innerHeight,
      rootPaddingTop: Number.parseFloat(rootStyle.paddingTop),
      rootPaddingBottom: Number.parseFloat(rootStyle.paddingBottom),
      header: rect(header),
      account: rect(account),
      main: rect(main),
    };
  });

  expect(geometry.header).toBeTruthy();
  expect(geometry.main).toBeTruthy();
  if (isMobile) {
    expect(geometry.header.y + geometry.header.height).toBeCloseTo(geometry.viewportHeight, 0);
    expect(geometry.rootPaddingBottom).toBeGreaterThanOrEqual(geometry.header.height);
    expect(geometry.account).toBeTruthy();
    expect(geometry.rootPaddingTop).toBeGreaterThanOrEqual(geometry.account.height);
    expect(geometry.main.y).toBeGreaterThanOrEqual(geometry.account.y + geometry.account.height);
  } else {
    expect(geometry.header.y).toBe(0);
    expect(geometry.rootPaddingTop).toBeGreaterThanOrEqual(geometry.header.height);
    expect(geometry.main.y).toBeGreaterThanOrEqual(geometry.header.y + geometry.header.height);
  }
}

async function expectStrongFocus(locator) {
  await locator.focus();
  await expect(locator).toBeFocused();
  const focus = await locator.evaluate((element) => {
    const style = getComputedStyle(element);
    return {
      outlineStyle: style.outlineStyle,
      outlineWidth: Number.parseFloat(style.outlineWidth),
      boxShadow: style.boxShadow,
    };
  });
  const outlineIsStrong = focus.outlineStyle !== "none" && focus.outlineWidth >= 2;
  const insetSpread = focus.boxShadow.match(/inset\s+(?:rgb\([^)]*\)|#[0-9a-f]+|[a-z]+)?\s*0(?:px)?\s+0(?:px)?\s+0(?:px)?\s+([0-9.]+)px/i);
  const insetIsStrong = Number.parseFloat(insetSpread?.[1] ?? "0") >= 2;
  expect(
    outlineIsStrong || insetIsStrong,
    `focus must use at least a 2px outline or inset ring; received ${JSON.stringify(focus)}`,
  ).toBe(true);
}

async function expectMinimumTargets(locator, minimum = 44) {
  const targets = await locator.evaluateAll((elements) => elements.map((element) => {
    const rect = element.getBoundingClientRect();
    return {
      label: element.getAttribute("aria-label") || element.textContent?.trim() || element.tagName,
      width: rect.width,
      height: rect.height,
    };
  }));
  expect(targets.length).toBeGreaterThan(0);
  for (const target of targets) {
    expect(target.width, `${target.label} target width`).toBeGreaterThanOrEqual(minimum);
    expect(target.height, `${target.label} target height`).toBeGreaterThanOrEqual(minimum);
  }
}

test.describe("public-beta visual contract", () => {
  for (const route of PUBLIC_ROUTES) {
    test(`${route.name} route keeps chrome clear and stays within the viewport`, async ({ page }, testInfo) => {
      await openRoute(page, route);
      await expectNoHorizontalOverflow(page);
      await expectChromeClearsMain(page, testInfo.project.name.startsWith("mobile"));
    });
  }

  test("computed palette tokens meet the approved readable values", async ({ page }) => {
    await openRoute(page, PUBLIC_ROUTES[0]);
    const colors = await page.evaluate(() => {
      const root = getComputedStyle(document.documentElement);
      const label = getComputedStyle(document.querySelector(".auth-field label"));
      const input = getComputedStyle(document.querySelector(".auth-field input"));
      return {
        mutedToken: root.getPropertyValue("--text-muted").trim().toLowerCase(),
        borderToken: root.getPropertyValue("--border-strong").trim().toLowerCase(),
        labelColor: label.color,
        inputBorderColor: input.borderTopColor,
      };
    });
    expect(colors).toEqual({
      mutedToken: "#6e6e6e",
      borderToken: "#949494",
      labelColor: "rgb(110, 110, 110)",
      inputBorderColor: "rgb(148, 148, 148)",
    });
  });

  test("event rows keep the display title and give all information one computed recipe", async ({ page }) => {
    await openRoute(page, PUBLIC_ROUTES[2], { events: [EVENT_ROW_FIXTURE] });
    const styles = await page.locator(".discover-event-row").evaluate((row) => {
      const read = (selector) => {
        const style = getComputedStyle(row.querySelector(selector));
        return {
          color: style.color,
          fontFamily: style.fontFamily,
          fontSize: style.fontSize,
          fontWeight: style.fontWeight,
        };
      };
      return {
        title: read(".discover-event-title"),
        meta: read(".discover-event-meta"),
        time: read("time"),
        lineup: read(".discover-event-lineup"),
      };
    });
    expect(styles.title.fontFamily).toContain("Rozha One");
    expect(styles.meta).toEqual(styles.time);
    expect(styles.meta).toEqual(styles.lineup);
    expect(styles.meta.fontFamily).toContain("General Sans");
    expect(styles.meta.fontSize).toBe("14px");
    expect(styles.meta.fontWeight).toBe("400");
  });

  test("Discover is venue-first and suppresses start time for past events", async ({ page }) => {
    await openRoute(page, PUBLIC_ROUTES[2], { events: [PROFILE_EVENT_FIXTURE] });
    const meta = page.locator(".discover-event-meta");
    await expect(meta).toContainText("Middlesex · Sun 20 Aug");
    await expect(meta).not.toContainText("10:00 pm");
  });

  test("failed event media falls back without changing the governed row geometry", async ({ page }, testInfo) => {
    test.skip(testInfo.project.name !== "mobile-chrome-390", "Failed media is measured once at the primary mobile evidence width.");
    await page.route("**/failed-event-poster.jpg", (route) => route.abort());
    await openRoute(page, PUBLIC_ROUTES[2], { events: [DENSE_EVENT_ROW_FIXTURES[1]] });
    await expect(page.locator(".discover-event-flier.image-slot")).toBeVisible();
    await expect(page.locator(".discover-event-flier img")).toHaveCount(0);
    await expectNoHorizontalOverflow(page);
  });

  test("dense event rows survive 200 percent text enlargement", async ({ page }, testInfo) => {
    test.skip(testInfo.project.name !== "desktop-chrome-1280", "Text enlargement is measured once with desktop capacity.");
    await page.route("**/failed-event-poster.jpg", (route) => route.abort());
    await openRoute(page, PUBLIC_ROUTES[2], { events: DENSE_EVENT_ROW_FIXTURES });
    await page.addStyleTag({ content: `:root{--text-micro:24px;--text-ui:28px;--text-body:32px;--text-body-lg:36px;--text-row-title:40px;--text-title-past:48px;--text-title:72px}` });
    await expect(page.locator(".discover-event-row")).toHaveCount(2);
    await expectNoHorizontalOverflow(page);
  });

  test("initial event failure owns one local Retry target", async ({ page }, testInfo) => {
    test.skip(testInfo.project.name !== "mobile-chrome-390", "Initial recovery is measured once at the primary mobile evidence width.");
    await openRoute(page, PUBLIC_ROUTES[2], { initialEventFailure: true });
    await expect(page.getByText("Events could not be loaded.")).toBeVisible();
    const retry = page.getByRole("button", { name: "Retry" });
    await expectMinimumTargets(retry);
  });

  test("continuation failure preserves successful event rows and retries locally", async ({ page }, testInfo) => {
    test.skip(testInfo.project.name !== "mobile-chrome-390", "Continuation recovery is measured once at the primary mobile evidence width.");
    await openRoute(page, PUBLIC_ROUTES[2], { events: [EVENT_ROW_FIXTURE], continuationFailure: true });
    await expect(page.locator(".discover-event-row")).toHaveCount(1);
    await expect(page.getByText("More events could not be loaded.")).toBeVisible();
    await expect(page.locator(".discover-event-row")).toHaveCount(1);
    await expectMinimumTargets(page.getByRole("button", { name: "Retry" }));
  });

  test("keyboard focus is visibly at least two pixels on every route class", async ({ page }) => {
    await openRoute(page, PUBLIC_ROUTES[0]);
    await expectStrongFocus(page.getByRole("link", { name: "Reset it" }));

    await page.goto(PUBLIC_ROUTES[1].path);
    await expect(page.getByRole("heading", { level: 1, name: "Search" })).toBeVisible();
    await expectStrongFocus(page.getByRole("button", { name: "Events" }));

    await page.goto(PUBLIC_ROUTES[2].path);
    await expect(page.getByRole("heading", { level: 1, name: "Boston" })).toBeVisible();
    await expectStrongFocus(page.getByRole("button", { name: "Upcoming" }));
  });

  test("essential mobile navigation, account, and auth targets are at least 44px", async ({ page }, testInfo) => {
    test.skip(!testInfo.project.name.startsWith("mobile"), "The 44px product target is a mobile contract.");
    await openRoute(page, PUBLIC_ROUTES[0]);
    await expectMinimumTargets(page.locator("header.site-header nav a"));
    await expectMinimumTargets(page.locator(".guest-auth-controls a"));
    await expectMinimumTargets(page.locator("main.auth-page button[type=submit]"));
    await expectMinimumTargets(page.locator("main.auth-page .auth-links a"));
  });

  test("authenticated account avatar and menu align with the persistent header", async ({ page }) => {
    await openRoute(page, PUBLIC_ROUTES[1], { authenticated: true });
    const trigger = page.getByRole("button", { name: "Account menu for Onda Test" });
    await expectMinimumTargets(trigger);
    await expect(trigger.locator("img.profile-avatar-small")).toBeVisible();
    await expect(page.getByText("@onda_test")).toHaveCount(0);
    const viewport = page.viewportSize();
    const mobile = viewport.width < 768;
    const headerBox = await page.locator(mobile ? "header.site-header > section" : "header.site-header").boundingBox();
    const triggerBox = await trigger.boundingBox();
    expect(headerBox).not.toBeNull();
    expect(triggerBox).not.toBeNull();
    expect(Math.abs((triggerBox.y + triggerBox.height / 2) - (headerBox.y + headerBox.height / 2))).toBeLessThanOrEqual(1);
    await trigger.click();
    const editProfile = page.getByRole("menuitem", { name: "Edit profile" });
    await expect(editProfile).toBeVisible();
    await expect(page.getByRole("menuitem", { name: "Log out" })).toBeVisible();
    await expectMinimumTargets(editProfile, mobile ? 44 : 24);
    await expectMinimumTargets(page.getByRole("menuitem", { name: "Log out" }), mobile ? 44 : 24);
    const panelBox = await page.locator(".account-menu-panel").boundingBox();
    expect(panelBox).not.toBeNull();
    expect(panelBox.y).toBeGreaterThanOrEqual(headerBox.y + headerBox.height);
    expect(Math.abs((panelBox.x + panelBox.width) - (triggerBox.x + triggerBox.width))).toBeLessThanOrEqual(1);
  });

  test("upcoming event identity has one calm information hierarchy", async ({ page }) => {
    await mockPublicApi(page, { authenticated: true });
    await page.goto("/e/franky-rizardo-flow-468");
    await expect(page.getByRole("heading", { level: 1, name: "Franky Rizardo - Flow" })).toBeVisible();
    await expect(page.locator(".event-location-line")).toHaveText("Pacha New York · New York City");
    await expect(page.locator(".event-meta-stack time")).toContainText("Aug 29, 2099 · 10:00 PM");
    await expect(page.getByRole("heading", { level: 2, name: "Lineup" })).toBeVisible();
    await expect(page.locator(".event-lineup a")).toHaveCount(3);
    await expect(page.locator(".wbt-count")).toHaveText("1 active mark");

    const hierarchy = await page.locator("main.event-page").evaluate((main) => {
      const read = (selector) => {
        const style = getComputedStyle(main.querySelector(selector));
        return { color: style.color, fontFamily: style.fontFamily, fontSize: style.fontSize, fontWeight: style.fontWeight };
      };
      return {
        meta: read(".event-meta-stack p"),
        lineupTitle: read(".event-lineup-title"),
        artist: read(".event-lineup a"),
        count: read(".wbt-count"),
        button: read(".wbt-action"),
        overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth,
      };
    });
    expect(hierarchy.meta.fontSize).toBe("14px");
    expect(hierarchy.meta.fontWeight).toBe("400");
    expect(hierarchy.artist.fontSize).toBe(hierarchy.meta.fontSize);
    expect(hierarchy.artist.fontWeight).toBe(hierarchy.meta.fontWeight);
    expect(hierarchy.artist.color).toBe(hierarchy.meta.color);
    expect(hierarchy.lineupTitle.fontSize).toBe("14px");
    expect(hierarchy.lineupTitle.fontWeight).toBe("600");
    expect(hierarchy.count.fontFamily).toBe(hierarchy.meta.fontFamily);
    expect(hierarchy.button.color).toBe(hierarchy.count.color);
    expect(hierarchy.overflow).toBeLessThanOrEqual(0);

    const wbt = page.getByRole("button", { name: "Will Be There" });
    await wbt.click();
    await expect(page.getByRole("button", { name: "Remove Will Be There" })).toBeVisible();
    const committedColor = await page.locator(".wbt-action.is-marked").evaluate((element) => getComputedStyle(element).color);
    expect(committedColor).toBe(hierarchy.count.color);
  });

  test("past event keeps lineup in identity and groups owner mutations under Edit", async ({ page }) => {
    await mockPublicApi(page, { authenticated: true, eventDetail: PAST_EVENT_DETAIL_FIXTURE });
    await page.goto("/e/franky-rizardo-flow-468");
    await expect(page.getByRole("heading", { level: 1, name: "Franky Rizardo - Flow" })).toBeVisible();
    await expect(page.getByRole("heading", { level: 2, name: "Lineup" })).toBeVisible();
    await expect(page.locator(".event-meta-stack time")).toHaveText("Sun, Aug 20, 2000");
    await expect(page.locator(".event-meta-stack time")).not.toContainText("10:00 PM");
    const positions = await page.locator("main.event-page").evaluate((main) => ({
      lineup: main.querySelector(".event-lineup").getBoundingClientRect().top,
      rating: main.querySelector(".event-rating-block").getBoundingClientRect().top,
      ownerReview: main.querySelector(".owner-entry").getBoundingClientRect().top,
    }));
    expect(positions.lineup).toBeLessThan(positions.rating);
    expect(positions.lineup).toBeLessThan(positions.ownerReview);
    expect(await page.locator(".event-lineup").count()).toBe(1);

    await page.locator(".review-actions-trigger").click();
    await expect(page.getByRole("menuitem", { name: "Edit review" })).toBeVisible();
    await expect(page.getByRole("menuitem", { name: "Remove review" })).toBeVisible();
    await expect(page.getByRole("menuitem", { name: "Remove from Been" })).toBeVisible();
    await expect(page.getByText("Remove rating", { exact: true })).toHaveCount(0);
    await expectMinimumTargets(page.locator(".review-actions-options .menu-action"), page.viewportSize().width < 768 ? 44 : 24);
    await page.getByRole("menuitem", { name: "Edit review" }).click();
    await expect(page.getByLabel("Written review")).toBeVisible();
    await expectNoHorizontalOverflow(page);
  });

  test("event detail preserves the artwork slot when no flyer exists", async ({ page }) => {
    await mockPublicApi(page, { eventDetail: { ...EVENT_DETAIL_FIXTURE, cover_image_url: null } });
    await page.goto("/e/franky-rizardo-flow-468");
    await expect(page.locator(".event-identity > .image-slot")).toBeVisible();
    await expectNoHorizontalOverflow(page);
  });

  test("profile applies Instagram spacing and Letterboxd review placement", async ({ page }) => {
    await mockPublicApi(page, { authenticated: true });
    await page.goto("/u/onda_test/reviews");
    await expect(page.getByRole("heading", { level: 1, name: "Onda Test" })).toBeVisible();
    await expect(page.getByText("Avg. Rating", { exact: true })).toBeVisible();
    await expect(page.getByText("The room, the sound, and the crowd all landed at once.")).toBeVisible();
    await expect(page.locator(".profile-diary-likes")).toContainText("No likes yet");
    await expect(page.locator(".profile-diary-attended")).not.toContainText("10:00");

    const geometry = await page.locator("main.profile-page").evaluate((main) => {
      const header = main.querySelector(".profile-header").getBoundingClientRect();
      const avatar = main.querySelector(".profile-header > .profile-avatar").getBoundingClientRect();
      const action = main.querySelector(".profile-header-action").getBoundingClientRect();
      const row = main.querySelector(".profile-diary-row");
      const top = (selector) => row.querySelector(selector).getBoundingClientRect().top;
      return {
        headerWidth: header.width,
        avatarWidth: avatar.width,
        actionBelowAvatar: action.top >= avatar.bottom,
        order: [top(".profile-diary-title-line"), top(".profile-diary-venue"), top(".profile-diary-judgment"), top(".profile-diary-review"), top(".profile-diary-likes")],
      };
    });
    expect(geometry.headerWidth).toBeLessThanOrEqual(800);
    expect(geometry.avatarWidth).toBe(page.viewportSize().width < 768 ? 80 : 160);
    expect(geometry.actionBelowAvatar).toBe(true);
    expect(geometry.order).toEqual([...geometry.order].sort((left, right) => left - right));
    await expectNoHorizontalOverflow(page);
  });

  test("pending follow requests are actionable from both Activity locations", async ({ page }) => {
    const notification = {
      id: 25,
      type: "follow_request",
      actor: FOLLOW_REQUEST_FIXTURES[0].user,
      created_at: "2026-08-27T12:00:00Z",
      read_at: null,
      review: null,
    };
    await mockPublicApi(page, { authenticated: true, notifications: [notification], followRequests: FOLLOW_REQUEST_FIXTURES });
    await page.goto("/activity");
    await expect(page.getByRole("heading", { level: 1, name: "Activity" })).toBeVisible();
    const positions = await page.locator("main.activity-page").evaluate((main) => ({
      requests: main.querySelector(".activity-follow-requests").getBoundingClientRect().top,
      notifications: main.querySelector(".activity-list").getBoundingClientRect().top,
    }));
    expect(positions.requests).toBeLessThan(positions.notifications);
    await expect(page.getByText("2 pending requests")).toBeVisible();
    await page.getByRole("button", { name: /Follow requests/ }).click();
    await expect(page.locator(".activity-follow-request-actions").getByRole("button", { name: "Approve" })).toHaveCount(2);
    await expect(page.locator(".activity-follow-request-actions").getByRole("button", { name: "Delete" })).toHaveCount(2);
    await expect(page.locator(".activity-item .activity-request-actions")).toBeVisible();
    await expect(page.locator(".activity-item .activity-request-actions").getByRole("button", { name: "Approve" })).toHaveCount(1);
    await expect(page.locator(".activity-item .activity-request-actions").getByRole("button", { name: "Delete" })).toHaveCount(1);
    await expectMinimumTargets(page.locator(".activity-follow-request-actions button"), page.viewportSize().width < 768 ? 44 : 24);
    await expectMinimumTargets(page.locator(".activity-request-actions button"), page.viewportSize().width < 768 ? 44 : 24);
    await page.locator(".activity-follow-request-actions").getByRole("button", { name: "Approve" }).first().click();
    await expect(page.locator(".activity-item .activity-request-actions")).toHaveCount(0);
    await expectNoHorizontalOverflow(page);
  });

  test("the 767 to 768 shell transition preserves usable content capacity", async ({ page }, testInfo) => {
    test.skip(testInfo.project.name !== "desktop-chrome-1280", "Measured once because this test controls its own viewport.");
    await mockPublicApi(page);
    await page.setViewportSize({ width: 767, height: 900 });
    await page.goto("/discover");
    await expect(page.getByRole("heading", { level: 1, name: "Boston" })).toBeVisible();
    const narrow = await page.locator("main").evaluate((element) => {
      const style = getComputedStyle(element);
      return element.clientWidth - Number.parseFloat(style.paddingLeft) - Number.parseFloat(style.paddingRight);
    });
    await page.setViewportSize({ width: 768, height: 900 });
    const desktop = await page.locator("main").evaluate((element) => {
      const style = getComputedStyle(element);
      return element.clientWidth - Number.parseFloat(style.paddingLeft) - Number.parseFloat(style.paddingRight);
    });
    expect(desktop).toBeGreaterThanOrEqual(narrow);
  });

  test("the 320px Search scope rail discloses and scrolls every scope into view", async ({ page }, testInfo) => {
    test.skip(testInfo.project.name !== "mobile-chrome-320", "The local rail is the approved 320px composition.");
    await openRoute(page, PUBLIC_ROUTES[1]);
    const rail = page.locator(".search-scopes");
    const overflow = await rail.evaluate((element) => ({ client: element.clientWidth, scroll: element.scrollWidth }));
    expect(overflow.scroll).toBeGreaterThan(overflow.client);
    await expect(page.locator(".search-scopes-cue")).toBeVisible();
    await page.getByRole("button", { name: "People" }).focus();
    await expect(page.getByRole("button", { name: "People" })).toBeFocused();
    const geometry = await page.getByRole("button", { name: "People" }).evaluate((element) => {
      const button = element.getBoundingClientRect();
      const railRect = element.parentElement.getBoundingClientRect();
      return { buttonLeft: button.left, buttonRight: button.right, railLeft: railRect.left, railRight: railRect.right };
    });
    expect(geometry.buttonLeft).toBeGreaterThanOrEqual(geometry.railLeft);
    expect(geometry.buttonRight).toBeLessThanOrEqual(geometry.railRight);
    await expect(page.locator(".search-scopes-cue")).toBeHidden();
  });
});
