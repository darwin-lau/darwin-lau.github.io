import assert from "node:assert/strict";
import { access, glob, readFile } from "node:fs/promises";
import test from "node:test";
import * as z from "zod/v4";

test("Astro prerendering resolves a compatible local Zod", () => {
  assert.equal(
    typeof z.function({ input: [], output: z.promise(z.any()) }).optional,
    "function"
  );
  assert.ok(import.meta.resolve("zod/v4").startsWith(new URL("../node_modules/", import.meta.url).href));
});

test("production includes every public entry point, even with no posts", async () => {
  for (const file of [
    "index.html", "posts/index.html", "tags/index.html", "archives/index.html",
    "about/index.html", "search/index.html", "404.html", "rss.xml",
    "sitemap-index.xml", "default-og.png", "pagefind/pagefind.js",
  ]) {
    await access(`dist/${file}`);
  }
});

test("rendered pages, feeds, and sitemap exclude the draft sample", async () => {
  for await (const file of glob("**/*.{html,xml}", { cwd: "dist" })) {
    const content = await readFile(`dist/${file}`, "utf8");
    assert.ok(!content.includes("BLOG_DRAFT_SAMPLE_2026"), file);
    assert.ok(!content.includes("/posts/layout-sample"), file);
  }
  await assert.rejects(access("dist/posts/layout-sample/index.html"));
});

test("Chinese metadata, canonical URL, and local resources are configured", async () => {
  const html = await readFile("dist/index.html", "utf8");
  assert.match(html, /lang="zh-CN"/);
  assert.match(html, /Darwin 的技术笔记/);
  assert.match(html, /rel="canonical" href="https:\/\/darwin-lau\.github\.io\//);
  assert.doesNotMatch(html, /fonts\.(googleapis|gstatic)\.com/);
  assert.doesNotMatch(html, /satna\.ing|astro-paper\.pages\.dev/);
});

test("internal page and asset links resolve to built files", async () => {
  for await (const file of glob("**/*.html", { cwd: "dist" })) {
    const html = await readFile(`dist/${file}`, "utf8");
    for (const match of html.matchAll(/(?:href|src)="(\/[^\"]*)"/g)) {
      const pathname = decodeURIComponent(new URL(match[1], "https://darwin-lau.github.io").pathname);
      const target = `dist${pathname}`;
      const candidates = [target, `${target.replace(/\/$/, "")}/index.html`];
      const exists = await Promise.all(candidates.map(path => access(path).then(() => true, () => false)));
      assert.ok(exists.some(Boolean), `${file}: ${match[1]}`);
    }
  }
});
