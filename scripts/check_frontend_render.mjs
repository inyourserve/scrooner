#!/usr/bin/env node

/**
 * Dependency-free rendered frontend contract for local QA.
 *
 * Prerequisites:
 *   - Astro site running (default http://127.0.0.1:4321)
 *   - Next.js app running (default http://127.0.0.1:3000)
 *   - Product backend running for the screener happy path
 *   - Chrome/Chromium, or CHROME_PATH set explicitly
 */

import { existsSync, mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { basename, join, resolve } from "node:path";
import { spawn } from "node:child_process";

const cli = new Map();
for (let index = 2; index < process.argv.length; index += 2) {
  cli.set(process.argv[index], process.argv[index + 1]);
}

const siteUrl = (cli.get("--site-url") ?? "http://127.0.0.1:4321").replace(/\/$/, "");
const appUrl = (cli.get("--app-url") ?? "http://127.0.0.1:3000").replace(/\/$/, "");
const outputDirectory = resolve(cli.get("--output") ?? join(tmpdir(), "scrooner-render-contract"));
const chromeCandidates = [
  cli.get("--chrome-path"),
  process.env.CHROME_PATH,
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
  "/usr/bin/google-chrome",
  "/usr/bin/chromium",
  "/usr/bin/chromium-browser",
].filter(Boolean);
const chromePath = chromeCandidates.find((candidate) => existsSync(candidate));

if (!chromePath) {
  throw new Error("Chrome/Chromium was not found. Set CHROME_PATH or pass --chrome-path.");
}

mkdirSync(outputDirectory, { recursive: true });

const surfaces = [
  {
    name: "homepage",
    url: `${siteUrl}/`,
    expected: ["Screen US companies in plain English", "Explore SEC-derived financials"],
  },
  {
    name: "catalog",
    url: `${siteUrl}/design-system/`,
    expected: ["One visual language for every Scrooner surface", "Brand and color"],
  },
  {
    name: "company-aapl",
    url: `${siteUrl}/stock/aapl/`,
    expected: ["Apple Inc.", "Financials", "Recent Filings"],
  },
  {
    name: "screener",
    url: `${appUrl}/screener`,
    expected: ["Find companies", "What companies are you looking for?", "Show matches", "Build with filters"],
    forbidden: ["Metric definitions are unavailable"],
  },
];

const viewports = [
  { name: "desktop", width: 1440, height: 1100, mobile: false },
  { name: "mobile", width: 390, height: 844, mobile: true },
];

const profileDirectory = mkdtempSync(join(tmpdir(), "scrooner-chrome-profile-"));
const chrome = spawn(
  chromePath,
  [
    "--headless=new",
    "--disable-background-networking",
    "--disable-default-apps",
    "--disable-extensions",
    "--disable-gpu",
    "--hide-scrollbars",
    "--no-first-run",
    "--remote-debugging-address=127.0.0.1",
    "--remote-debugging-port=0",
    `--user-data-dir=${profileDirectory}`,
    "about:blank",
  ],
  { stdio: ["ignore", "ignore", "pipe"] },
);

let chromeDiagnostics = "";
chrome.stderr.on("data", (chunk) => {
  chromeDiagnostics = (chromeDiagnostics + chunk.toString()).slice(-8000);
});

const delay = (milliseconds) => new Promise((resolveDelay) => setTimeout(resolveDelay, milliseconds));

async function waitForDevToolsPort() {
  const activePortFile = join(profileDirectory, "DevToolsActivePort");
  for (let attempt = 0; attempt < 120; attempt += 1) {
    if (existsSync(activePortFile)) {
      const [port] = readFileSync(activePortFile, "utf8").trim().split("\n");
      return Number(port);
    }
    if (chrome.exitCode !== null) {
      throw new Error(`Chrome exited before DevTools started.\n${chromeDiagnostics}`);
    }
    await delay(100);
  }
  throw new Error(`Timed out waiting for Chrome DevTools.\n${chromeDiagnostics}`);
}

async function waitForProcessExit(processHandle, milliseconds) {
  if (processHandle.exitCode !== null) return true;
  return Promise.race([
    new Promise((resolveExit) => processHandle.once("exit", () => resolveExit(true))),
    delay(milliseconds).then(() => false),
  ]);
}

async function removeProfileDirectory() {
  for (let attempt = 0; attempt < 10; attempt += 1) {
    try {
      rmSync(profileDirectory, { recursive: true, force: true });
      return;
    } catch (error) {
      if (!(error instanceof Error) || !error.message.includes("ENOTEMPTY") || attempt === 9) throw error;
      await delay(100);
    }
  }
}

function connect(url) {
  return new Promise((resolveConnection, rejectConnection) => {
    const socket = new WebSocket(url);
    let commandId = 0;
    const pending = new Map();
    const eventWaiters = new Map();

    socket.addEventListener("message", (event) => {
      const message = JSON.parse(event.data);
      if (message.id && pending.has(message.id)) {
        const handlers = pending.get(message.id);
        pending.delete(message.id);
        if (message.error) handlers.reject(new Error(message.error.message));
        else handlers.resolve(message.result);
        return;
      }
      const waiters = eventWaiters.get(message.method) ?? [];
      eventWaiters.delete(message.method);
      for (const waiter of waiters) waiter(message.params);
    });

    socket.addEventListener("error", () => rejectConnection(new Error("Chrome DevTools WebSocket failed.")));
    socket.addEventListener("open", () => {
      resolveConnection({
        close: () => socket.close(),
        command(method, params = {}) {
          return new Promise((resolveCommand, rejectCommand) => {
            const id = ++commandId;
            pending.set(id, { resolve: resolveCommand, reject: rejectCommand });
            socket.send(JSON.stringify({ id, method, params }));
          });
        },
        event(method) {
          return new Promise((resolveEvent) => {
            eventWaiters.set(method, [...(eventWaiters.get(method) ?? []), resolveEvent]);
          });
        },
      });
    });
  });
}

async function waitForContent(client, surface) {
  const expression = JSON.stringify({ expected: surface.expected, forbidden: surface.forbidden ?? [] });
  for (let attempt = 0; attempt < 80; attempt += 1) {
    const result = await client.command("Runtime.evaluate", {
      expression: `(() => { const rules = ${expression}; const text = document.body?.innerText ?? ""; return { ready: rules.expected.every((item) => text.includes(item)), forbidden: rules.forbidden.filter((item) => text.includes(item)), title: document.title, text: text.slice(0, 1200) }; })()`,
      returnByValue: true,
    });
    const state = result.result.value;
    if (state.forbidden.length > 0) {
      throw new Error(`${surface.name} rendered forbidden state: ${state.forbidden.join(", ")}`);
    }
    if (state.ready) return state;
    await delay(200);
  }
  const diagnostic = await client.command("Runtime.evaluate", {
    expression: "(document.body?.innerText ?? '').slice(0, 1200)",
    returnByValue: true,
  });
  throw new Error(`${surface.name} did not render expected content: ${surface.expected.join(", ")}\nRendered text:\n${diagnostic.result.value}`);
}

async function verifyScreenerResult(client, viewport) {
  const clicked = await client.command("Runtime.evaluate", {
    expression: `(() => {
      const button = document.querySelector('button[aria-label^="Run example:"]');
      if (!(button instanceof HTMLButtonElement)) return false;
      button.click();
      return true;
    })()`,
    returnByValue: true,
  });
  if (!clicked.result.value) throw new Error(`screener/${viewport.name}: runnable example button was not found.`);

  let lastState;
  for (let attempt = 0; attempt < 180; attempt += 1) {
    const check = await client.command("Runtime.evaluate", {
      expression: `(() => {
        const text = document.body?.innerText ?? "";
        const normalizedText = text.toLowerCase();
        const results = document.querySelector('.results-section');
        const builder = document.querySelector('.advanced-builder');
        const resultsCount = document.querySelectorAll('.results-section').length;
        const builderCount = document.querySelectorAll('.advanced-builder').length;
        return {
          complete: normalizedText.includes('current screen') && normalizedText.includes('matching companies') && Boolean(results),
          failed: normalizedText.includes('the screen did not run') || normalizedText.includes('clarify this screen'),
          text: text.slice(0, 1600),
          resultsCount,
          builderCount,
          resultsTop: results?.getBoundingClientRect().top ?? null,
          builderTop: builder?.getBoundingClientRect().top ?? null,
          documentWidth: document.documentElement.scrollWidth,
          bodyWidth: document.body.scrollWidth,
        };
      })()`,
      returnByValue: true,
    });
    const state = check.result.value;
    lastState = state;
    if (state.failed) throw new Error(`screener/${viewport.name}: example did not produce results.\n${state.text}`);
    if (state.resultsCount > 1 || state.builderCount > 1) {
      throw new Error(
        `screener/${viewport.name}: workflow landmarks rendered more than once (${JSON.stringify(state)}).`,
      );
    }
    if (state.complete) {
      if (state.documentWidth > viewport.width || state.bodyWidth > viewport.width) {
        throw new Error(`screener-results/${viewport.name}: horizontal overflow (${JSON.stringify(state)}).`);
      }
      if (state.resultsTop === null || state.builderTop === null || state.resultsTop >= state.builderTop) {
        throw new Error(`screener-results/${viewport.name}: results do not appear before the exact filter editor (${JSON.stringify(state)}).`);
      }
      const screenshot = await client.command("Page.captureScreenshot", {
        format: "png",
        captureBeyondViewport: false,
        fromSurface: true,
      });
      const screenshotPath = join(outputDirectory, `screener-results-${viewport.name}.png`);
      writeFileSync(screenshotPath, Buffer.from(screenshot.data, "base64"));
      return basename(screenshotPath);
    }
    await delay(200);
  }

  throw new Error(`screener/${viewport.name}: timed out waiting for the example result.\nLast state:\n${JSON.stringify(lastState, null, 2)}`);
}

let client;
let exitCode = 0;

try {
  const metricResponse = await fetch(`${appUrl}/api/metrics`);
  if (!metricResponse.ok) {
    throw new Error(`Metric catalog prerequisite returned HTTP ${metricResponse.status}.`);
  }
  const liveMetrics = await metricResponse.json();
  const uncuratedMetrics = liveMetrics
    .filter((metric) => metric.category === "Other" || metric.short_definition === "Defined Scrooner metric.")
    .map((metric) => metric.metric_name);
  if (uncuratedMetrics.length > 0) {
    throw new Error(`Metric catalog contains uncurated presentation fallbacks: ${uncuratedMetrics.join(", ")}`);
  }

  const port = await waitForDevToolsPort();
  const targets = await fetch(`http://127.0.0.1:${port}/json/list`).then((response) => response.json());
  const page = targets.find((target) => target.type === "page");
  if (!page?.webSocketDebuggerUrl) throw new Error("Chrome did not expose a page target.");

  client = await connect(page.webSocketDebuggerUrl);
  await client.command("Page.enable");

  const results = [];
  for (const surface of surfaces) {
    for (const viewport of viewports) {
      await client.command("Emulation.setDeviceMetricsOverride", {
        width: viewport.width,
        height: viewport.height,
        deviceScaleFactor: 1,
        mobile: viewport.mobile,
        screenWidth: viewport.width,
        screenHeight: viewport.height,
      });

      const loaded = client.event("Page.loadEventFired");
      await client.command("Page.navigate", { url: surface.url });
      await loaded;
      const content = await waitForContent(client, surface);
      await delay(250);

      const dimensions = await client.command("Runtime.evaluate", {
        expression: "({ viewportWidth: innerWidth, viewportHeight: innerHeight, documentWidth: document.documentElement.scrollWidth, bodyWidth: document.body.scrollWidth })",
        returnByValue: true,
      });
      const measured = dimensions.result.value;
      if (measured.viewportWidth !== viewport.width) {
        throw new Error(`${surface.name}/${viewport.name}: expected ${viewport.width}px viewport, received ${measured.viewportWidth}px.`);
      }
      if (measured.documentWidth > viewport.width || measured.bodyWidth > viewport.width) {
        throw new Error(`${surface.name}/${viewport.name}: horizontal overflow (${JSON.stringify(measured)}).`);
      }

      const screenshot = await client.command("Page.captureScreenshot", {
        format: "png",
        captureBeyondViewport: false,
        fromSurface: true,
      });
      const screenshotPath = join(outputDirectory, `${surface.name}-${viewport.name}.png`);
      writeFileSync(screenshotPath, Buffer.from(screenshot.data, "base64"));
      const interactionScreenshot = surface.name === "screener"
        ? await verifyScreenerResult(client, viewport)
        : undefined;
      results.push({
        surface: surface.name,
        viewport: viewport.name,
        width: measured.viewportWidth,
        documentWidth: measured.documentWidth,
        title: content.title,
        screenshot: basename(screenshotPath),
        ...(interactionScreenshot ? { interactionScreenshot } : {}),
      });
    }
  }

  process.stdout.write(`${JSON.stringify({ outputDirectory, curatedMetrics: liveMetrics.length, checks: results }, null, 2)}\n`);
} catch (error) {
  exitCode = 1;
  process.stderr.write(`frontend render contract failed: ${error instanceof Error ? error.message : String(error)}\n`);
} finally {
  client?.close();
  if (chrome.exitCode === null) chrome.kill("SIGTERM");
  if (!(await waitForProcessExit(chrome, 1500)) && chrome.exitCode === null) {
    chrome.kill("SIGKILL");
    await waitForProcessExit(chrome, 1500);
  }
  chrome.stderr.destroy();
  chrome.unref();
  await removeProfileDirectory();
}

process.exit(exitCode);
