/* Measure archive navigation without collecting search text or URL queries. */
(function () {
  "use strict";
  function track(name, parameters) {
    if (typeof window.gtag === "function") {
      window.gtag("event", name, parameters);
    }
  }
  if (document.querySelector("[data-page-not-found]")) {
    track("page_not_found", { page_path: window.location.pathname });
  }
  document.addEventListener("click", function (event) {
    var link = event.target.closest("a");
    if (!link) return;
    var reading = link.closest(".post-links");
    var discovery = link.closest("[data-discovery]");
    if (!reading && !discovery) return;
    var destination = new URL(link.href, window.location.href);
    if (destination.origin !== window.location.origin) return;
    track("reading_link_click", {
      page_path: window.location.pathname,
      link_path: destination.pathname,
      link_type: reading ? reading.getAttribute("aria-label") : discovery.dataset.discovery
    });
  });
}());
