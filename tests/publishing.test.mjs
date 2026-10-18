import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { access, cp, glob, mkdir, mkdtemp, readFile, symlink, writeFile } from "node:fs/promises";
import { join } from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

const project = fileURLToPath(new URL("../", import.meta.url));

test("publishing renders Markdown and excludes drafts and future posts", { timeout: 180_000 }, async () => {
  await mkdir(join(project, ".artifacts"), { recursive: true });
  // Astro 6 needs a shared path ancestor for source files and symlinked dependencies.
  const fixture = await mkdtemp(join(project, ".artifacts/publishing-"));
  try {
    for (const file of ["src", "public", "astro.config.ts", "astro-paper.config.ts", "tsconfig.json", "package.json"]) {
      await cp(join(project, file), join(fixture, file), {
        recursive: true,
        filter: source => ![join(project, "public/pagefind"), join(project, "src/content/posts")].includes(source),
      });
    }
    await symlink(join(project, "node_modules"), join(fixture, "node_modules"), "dir");
    const posts = join(fixture, "src/content/posts");
    await mkdir(posts, { recursive: true });
    const sample = await readFile(join(project, "src/content/posts/layout-sample.md"), "utf8");
    for (const [slug, draft, date, marker] of [
      ["published-post", false, "2000-01-01T09:00:00+08:00", "PUBLIC_POST_FIXTURE_2026"],
      ["draft-post", true, "2000-01-01T09:00:00+08:00", "DRAFT_POST_FIXTURE_2026"],
      ["future-post", false, "2999-01-01T09:00:00+08:00", "FUTURE_POST_FIXTURE_2026"],
    ]) {
      await writeFile(join(posts, `${slug}.md`), sample
        .replace(/^draft: .+$/m, `draft: ${draft}`)
        .replace(/^pubDatetime: .+$/m, `pubDatetime: ${date}`)
        .replace("BLOG_DRAFT_SAMPLE_2026", marker));
    }

    for (const args of [
      [join(project, "node_modules/astro/bin/astro.mjs"), "build"],
      [join(project, "node_modules/pagefind/lib/runner/bin.cjs"), "--site", "dist"],
    ]) {
      try {
        execFileSync(process.execPath, args, {
          cwd: fixture,
          env: { ...process.env, ASTRO_TELEMETRY_DISABLED: "1" },
          encoding: "utf8",
          timeout: 120_000,
          maxBuffer: 10 * 1024 * 1024,
        });
      } catch (error) {
        throw new Error(`Build command failed: ${args.join(" ")}\n${error.stdout ?? ""}\n${error.stderr ?? ""}`, { cause: error });
      }
    }

    const dist = join(fixture, "dist");
    const html = await readFile(join(dist, "posts/published-post/index.html"), "utf8");
    assert.match(html, /PUBLIC_POST_FIXTURE_2026/);
    assert.match(html, /<h2\b[^>]*id="中文正文与标题"/);
    assert.ok(html.includes(`href="#${encodeURIComponent("中文正文与标题")}"`));
    assert.match(html, /<summary\b[^>]*>展开目录<\/summary>/);
    assert.match(html, /<pre\b/);
    assert.match(html, /longLineForHorizontalScroll/);
    assert.match(html, /<table\b/);
    assert.match(html, /href="\/about\/"/);
    assert.match(html, /alt="三个依次排列的方框/);
    const image = html.match(/<img\b[^>]*src="([^"]*layout-sample[^"]*)"/);
    assert.ok(image, "the local Markdown image is emitted");
    await access(join(dist, decodeURIComponent(new URL(image[1], "https://darwin-lau.github.io").pathname)));
    for (const slug of ["draft-post", "future-post"]) {
      await assert.rejects(access(join(dist, `posts/${slug}/index.html`)));
    }

    let sitemap = "";
    for await (const file of glob("*.xml", { cwd: dist })) {
      const xml = await readFile(join(dist, file), "utf8");
      assert.doesNotMatch(xml, /draft-post|future-post|DRAFT_POST_FIXTURE_2026|FUTURE_POST_FIXTURE_2026/);
      if (file.startsWith("sitemap")) sitemap += xml;
    }
    assert.match(await readFile(join(dist, "rss.xml"), "utf8"), /posts\/published-post/);
    assert.match(sitemap, /posts\/published-post/);
    const entry = JSON.parse(await readFile(join(dist, "pagefind/pagefind-entry.json"), "utf8"));
    assert.equal(Object.values(entry.languages).reduce((total, language) => total + language.page_count, 0), 1);
  } catch (error) {
    throw new Error(`Publishing fixture retained at ${fixture}`, { cause: error });
  }
});
