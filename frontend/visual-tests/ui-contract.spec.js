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
  venue: { id: 335, slug: "middlesex", name: "Middlesex" },
  artists: [{ id: 842, name: "Leon Vynehall" }],
  rating_summary: { state: "unavailable", average: null, count: 0 },
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

async function mockPublicApi(page, { authenticated = false, events = [], continuationFailure = false, initialEventFailure = false } = {}) {
  await page.route("**/api/**", async (route) => {
    const url = new URL(route.request().url());
    let body;
    let status = 200;

    if (url.pathname === "/api/auth/session/") {
      body = {
        user: authenticated
          ? { id: 7, username: "onda_test", email: "test@example.com", is_verified: true }
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

  test("authenticated mobile account trigger is at least 44px", async ({ page }, testInfo) => {
    test.skip(!testInfo.project.name.startsWith("mobile"), "The 44px product target is a mobile contract.");
    await openRoute(page, PUBLIC_ROUTES[1], { authenticated: true });
    await expectMinimumTargets(page.locator(".account-menu-trigger"));
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
