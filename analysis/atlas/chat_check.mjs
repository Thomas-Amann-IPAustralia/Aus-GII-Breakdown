// A browser check of "Ask the atlas" (#/ask, ADR 0054), run by hand and by tests/test_atlas.py when Chromium is here:
//
//   node analysis/atlas/chat_check.mjs [--shots DIR]
//
// It serves the repository with Python's HTTP server, answers the page's calls to the chat's API from a recorded
// event stream (analysis/atlas/fixtures/chat-stream.json, from the Econ smoke test) instead of the network, asks a
// starter question, and checks: the answer renders with its cited runs, every claim's quote is lit in the trail, an
// observation id links to its page, a follow-up asks again, Copy and the JSON export work, the conversation survives
// a visit to a cited page, the page has no horizontal overflow at 1,366 and 390 pixels, and the console has no errors.
// It prints one JSON line of results and exits 1 if any check fails.
import { spawn } from "node:child_process";
import { readFileSync } from "node:fs";
import { createRequire } from "node:module";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "../..");
const require = createRequire(import.meta.url);
let chromium;
try { ({ chromium } = require("playwright")); } catch { ({ chromium } = await import("playwright")); }

const fixture = JSON.parse(readFileSync(`${root}/analysis/atlas/fixtures/chat-stream.json`, "utf8"));
const atlas = JSON.parse(readFileSync(`${root}/evidence/data/atlas.json`, "utf8"));
const API = atlas.site.chat.api.replace(/\/$/, "");
const shots = process.argv.includes("--shots") ? process.argv[process.argv.indexOf("--shots") + 1] : null;
const port = 8700 + Math.floor(Math.random() * 200);
const server = spawn("python3", ["-m", "http.server", String(port), "--bind", "127.0.0.1"], { cwd: root, stdio: "ignore" });
await new Promise((r) => setTimeout(r, 900));

const results = {};
const errors = [];
const check = (name, ok, detail = null) => { results[name] = ok ? true : (detail || false); };
const sse = (events) => events.map((e) => `event: ${e.event}\ndata: ${JSON.stringify(e)}\n\n`).join("");

const browser = await chromium.launch();
try {
  const ctx = await browser.newContext({ viewport: { width: 1366, height: 900 }, permissions: ["clipboard-read", "clipboard-write"] });
  const page = await ctx.newPage();
  page.on("console", (m) => { if (m.type() === "error") errors.push(m.text()); });
  page.on("pageerror", (e) => errors.push(String(e)));
  let asked = 0;
  await page.route(`${API}/**`, async (route) => {
    const url = route.request().url();
    if (url.endsWith("/health")) return route.fulfill({ contentType: "application/json", body: JSON.stringify(fixture.health) });
    if (url.endsWith("/ask")) {
      asked += 1;
      return route.fulfill({ contentType: "text/event-stream", body: sse(fixture.events) });
    }
    return route.fulfill({ status: 404, body: "{}" });
  });
  await page.goto(`http://127.0.0.1:${port}/evidence/#/ask`);
  await page.waitForSelector(".chat-starters button");
  check("status_ready", await page.locator(".chat-status.ready").count() === 1);
  await page.locator(".chat-starters button").first().click();
  await page.locator("#chat-send").click();
  await page.waitForSelector(".chat-foot", { timeout: 10000 });
  const claims = fixture.events.filter((e) => e.event === "check").at(-1)?.claims || [];
  check("answer_renders", await page.locator(".chat-answer .chat-prose p, .chat-answer .chat-prose li").count() > 0);
  check("cited_runs", await page.locator(".said.cited").count() > 0);
  check("check_badge", await page.locator(".chat-badges .vtag").count() >= 2);
  // every claim's quote is lit in the trail
  const marked = await page.$$eval("#chat-trail mark.q", (ms) => ms.map((m) => m.dataset.claims.split(" ")).flat());
  const missing = claims.filter((c) => c.verified && !marked.includes(String(c.n))).map((c) => c.n);
  check("every_quote_highlighted", missing.length === 0, { missing });
  // a claim marker focuses its passage
  await page.locator(".chat-answer button.cite").first().click();
  check("claim_focus", await page.locator("#chat-trail .pcard.focus").count() > 0);
  // ids link to their pages
  const idLink = page.locator(".chat-prose a.id").first();
  check("id_links", await idLink.count() > 0 && /^#\/[UBM]\d+$/.test(await idLink.getAttribute("href")));
  // the claims tab
  await page.locator('.chat-tabs [data-view="claims"]').click();
  check("claims_tab", await page.locator(".claim-card").count() === claims.length);
  await page.locator('.chat-tabs [data-view="answer"]').click();
  // Copy, and the JSON export
  await page.locator(".chat-foot .btn").first().click();
  const copied = await page.evaluate(() => navigator.clipboard.readText());
  check("copy", copied.startsWith("Q: ") && copied.includes("#/"), copied.slice(0, 80));
  const [dl] = await Promise.all([page.waitForEvent("download"), page.locator("#chat-bar .btn", { hasText: "Download" }).click()]);
  const exported = JSON.parse(readFileSync(await dl.path(), "utf8"));
  check("export", exported.format === "atlas-chat-export/1" && exported.turns.length === 1 && exported.turns[0].claims.length === claims.length
    && !JSON.stringify(exported).includes(fixture.events.find((e) => e.event === "retrieval").evidence[0].text));
  if (shots) await page.screenshot({ path: `${shots}/atlas-chat-1366.png`, fullPage: false });
  // overflow at 1,366
  const over = () => page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
  check("no_overflow_1366", (await over()) <= 0, await over());
  // a follow-up asks again
  const follow = page.locator(".chat-next button").first();
  if (await follow.count()) {
    await follow.click();
    await page.waitForFunction(() => document.querySelectorAll(".chat-foot").length >= 2, null, { timeout: 10000 });
    check("follow_up", asked === 2);
  } else check("follow_up", false, "no follow-ups in the fixture");
  // the conversation survives a visit to a cited page and back
  await idLink.click();
  await page.waitForSelector(".obs-box");
  check("ask_about_button", await page.locator(".md-tools a", { hasText: "Ask about this observation" }).count() === 1);
  await page.goBack();
  await page.waitForSelector(".cmsg.bot");
  check("survives_navigation", await page.locator(".cmsg.user").count() === 2);
  // 390 pixels
  await page.setViewportSize({ width: 390, height: 844 });
  await page.waitForTimeout(300);
  check("no_overflow_390", (await over()) <= 0, await over());
  if (shots) await page.screenshot({ path: `${shots}/atlas-chat-390.png`, fullPage: false });
  check("console_clean", errors.length === 0, errors.slice(0, 5));
} catch (e) {
  results.error = String(e?.stack || e).slice(0, 600);
} finally {
  await browser.close();
  server.kill();
}
const ok = Object.values(results).every((v) => v === true);
console.log(JSON.stringify({ ok, results }));
process.exit(ok ? 0 : 1);
