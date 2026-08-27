import { defineConfig } from "@playwright/test";
import { tmpdir } from "node:os";
import { join } from "node:path";

const chromeExecutablePath = process.env.PLAYWRIGHT_CHROME_PATH;
const chromeChannel = process.env.PLAYWRIGHT_BROWSER_CHANNEL ?? "chrome";
const artifactsRoot = process.env.PLAYWRIGHT_OUTPUT_DIR ?? join(tmpdir(), "onda-playwright-results");

export default defineConfig({
  testDir: "./visual-tests",
  outputDir: join(artifactsRoot, "artifacts"),
  fullyParallel: true,
  forbidOnly: Boolean(process.env.CI),
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: process.env.CI
    ? [["line"], ["html", { open: "never", outputFolder: join(artifactsRoot, "report") }]]
    : "line",
  use: {
    baseURL: "http://127.0.0.1:4173",
    channel: chromeExecutablePath ? undefined : chromeChannel,
    launchOptions: chromeExecutablePath ? { executablePath: chromeExecutablePath } : {},
    screenshot: "only-on-failure",
    trace: "retain-on-failure",
    video: "off",
  },
  projects: [
    {
      name: "mobile-chrome-320",
      use: { viewport: { width: 320, height: 720 } },
    },
    {
      name: "mobile-chrome-390",
      use: { viewport: { width: 390, height: 844 } },
    },
    {
      name: "mobile-chrome-767",
      use: { viewport: { width: 767, height: 900 } },
    },
    {
      name: "desktop-chrome-768",
      use: { viewport: { width: 768, height: 900 } },
    },
    {
      name: "desktop-chrome-1280",
      use: { viewport: { width: 1280, height: 900 } },
    },
  ],
  webServer: {
    command: "npm run dev -- --host 127.0.0.1 --port 4173 --strictPort",
    url: "http://127.0.0.1:4173",
    reuseExistingServer: !process.env.CI,
    timeout: 30_000,
  },
});
