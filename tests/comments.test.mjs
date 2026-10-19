import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";
import vm from "node:vm";

// The vendor owns iframe loading; exercise only our Astro/theme integration.
const source = (await readFile(
  new URL("../src/scripts/comments.ts", import.meta.url),
  "utf8"
)).replace(/^import "giscus";\s*/, "");

function createPage() {
  let currentWidget = null;
  const listeners = new Map();
  const observers = [];
  const root = { dataset: { theme: "light" } };
  const document = {
    documentElement: root,
    querySelector: selector => {
      assert.equal(selector, "giscus-widget");
      return currentWidget;
    },
    addEventListener(type, callback, options = {}) {
      if (!listeners.has(type)) listeners.set(type, new Set());
      listeners.get(type).add({ callback, once: options.once });
    },
  };
  class MutationObserver {
    active = false;

    constructor(callback) {
      this.callback = callback;
      observers.push(this);
    }

    observe() {
      this.active = true;
    }

    disconnect() {
      this.active = false;
    }
  }
  const dispatch = type => {
    for (const listener of [...(listeners.get(type) ?? [])]) {
      if (listener.once) listeners.get(type).delete(listener);
      listener.callback();
    }
  };
  vm.runInNewContext(source, { document, MutationObserver });
  return {
    observers,
    load(widget = null) {
      currentWidget = widget;
      dispatch("astro:page-load");
    },
    leave: () => dispatch("astro:before-swap"),
    listenerCount: type => listeners.get(type)?.size ?? 0,
    setTheme(theme) {
      root.dataset.theme = theme;
      for (const observer of observers) {
        if (observer.active) observer.callback();
      }
    },
  };
}

function widget() {
  const attributes = new Map([["theme", "noborder_light"]]);
  return {
    setAttribute: (name, value) => attributes.set(name, value),
    get theme() {
      return attributes.get("theme");
    },
  };
}

test("pages without comments do not bind theme observers or navigation cleanup", () => {
  const page = createPage();
  page.load();
  assert.equal(page.observers.length, 0);
  assert.equal(page.listenerCount("astro:before-swap"), 0);
});

test("comments receive the initial theme and follow light/dark changes", () => {
  const page = createPage();
  const comments = widget();
  page.setTheme("dark");
  page.load(comments);
  assert.equal(comments.theme, "noborder_dark");
  page.setTheme("light");
  assert.equal(comments.theme, "noborder_light");
  page.setTheme("dark");
  assert.equal(comments.theme, "noborder_dark");
});

test("navigation cleans up the old observer and synchronizes only the new widget", () => {
  const page = createPage();
  const first = widget();
  page.load(first);
  page.leave();
  assert.equal(page.observers[0].active, false);
  assert.equal(page.listenerCount("astro:before-swap"), 0);

  const second = widget();
  page.load(second);
  page.setTheme("dark");
  assert.equal(first.theme, "noborder_light");
  assert.equal(second.theme, "noborder_dark");
  assert.equal(page.observers[1].active, true);

  page.leave();
  page.load();
  page.setTheme("light");
  assert.equal(second.theme, "noborder_dark");
  assert.equal(page.observers.every(observer => !observer.active), true);
});
