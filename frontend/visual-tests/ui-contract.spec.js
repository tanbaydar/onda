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

async function mockPublicApi(page, { authenticated = false } = {}) {
  await page.route("**/api/**", async (route) => {
    const url = new URL(route.request().url());
    let body;

    if (url.pathname === "/api/auth/session/") {
      body = {
        user: authenticated
          ? { id: 7, username: "onda_test", email: "test@example.com", is_verified: true }
          : null,
      };
    } else if (url.pathname === "/api/cities/") {
      body = { results: [{ id: 1, name: "Boston" }] };
    } else if (url.pathname === "/api/events/") {
      body = { results: [], pagination: EMPTY_PAGINATION };
    } else if (url.pathname === "/api/search/") {
      body = { results: [], next_cursor: null };
    } else {
      body = {};
    }

    await route.fulfill({
      status: 200,
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
