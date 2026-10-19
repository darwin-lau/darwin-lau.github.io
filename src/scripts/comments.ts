import "giscus";

document.addEventListener("astro:page-load", () => {
  const widget = document.querySelector("giscus-widget");
  if (!widget) return;

  const syncTheme = () => {
    widget.setAttribute(
      "theme",
      document.documentElement.dataset.theme === "dark"
        ? "noborder_dark"
        : "noborder_light"
    );
  };
  syncTheme();
  const observer = new MutationObserver(syncTheme);
  observer.observe(document.documentElement, {
    attributes: true,
    attributeFilter: ["data-theme"],
  });
  document.addEventListener("astro:before-swap", () => observer.disconnect(), {
    once: true,
  });
});
