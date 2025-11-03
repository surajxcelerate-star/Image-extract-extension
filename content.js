// content.js - toggles an inspector mode that changes cursor and lets user click an element
(function () {
  // Prevent double-injection
  if (window.__elementInspectorInjected) return;
  window.__elementInspectorInjected = true;

  // If inspector already active, ignore (we toggle only by injection/cleanup)
  if (window.__inspectorActive) {
    // Already active; do nothing
    return;
  }

  window.__inspectorActive = true;

  // Save previous cursor to restore later
  const prevCursor = document.documentElement.style.cursor || "";

  // Add a little floating hint element
  const hint = document.createElement("div");
  hint.id = "__inspector_hint";
  hint.textContent = "Inspector: click an element to copy image URL — Esc to cancel";
  Object.assign(hint.style, {
    position: "fixed",
    top: "10px",
    right: "10px",
    zIndex: 2147483647,
    background: "rgba(0,0,0,0.75)",
    color: "white",
    padding: "6px 10px",
    borderRadius: "6px",
    fontFamily: "sans-serif",
    fontSize: "13px",
    pointerEvents: "none",
    boxShadow: "0 2px 8px rgba(0,0,0,0.3)"
  });
  document.documentElement.appendChild(hint);

  // Set crosshair cursor on body/html to hint selection mode
  document.documentElement.style.cursor = "crosshair";
  document.body.style.cursor = "crosshair";

  // Overlay to prevent accidental link navigation etc (transparent)
  const blocker = document.createElement("div");
  blocker.id = "__inspector_blocker";
  Object.assign(blocker.style, {
    position: "fixed",
    inset: "0",
    zIndex: 2147483646,
    background: "transparent",
    pointerEvents: "auto"
  });
  document.documentElement.appendChild(blocker);

  function getBackgroundImageUrl(el) {
    try {
      const bg = getComputedStyle(el).backgroundImage || "";
      const match = bg.match(/url\(["']?(.*?)["']?\)/);
      if (match && match[1]) return match[1];
    } catch (e) {
      // ignore cross-origin computedStyle errors
    }
    return null;
  }

  function makeToast(text) {
    const t = document.createElement("div");
    Object.assign(t.style, {
      position: "fixed",
      bottom: "20px",
      left: "50%",
      transform: "translateX(-50%)",
      zIndex: 2147483647,
      background: "rgba(0,0,0,0.85)",
      color: "white",
      padding: "8px 12px",
      borderRadius: "6px",
      fontFamily: "sans-serif",
      fontSize: "13px",
      boxShadow: "0 2px 8px rgba(0,0,0,0.3)"
    });
    t.textContent = text;
    document.documentElement.appendChild(t);
    setTimeout(() => t.remove(), 2200);
  }

  async function handleClick(e) {
    e.preventDefault();
    e.stopPropagation();

    // The element the user actually clicked (not the blocker)
    const el = document.elementFromPoint(e.clientX, e.clientY) || e.target;

    // Prefer <img> src, otherwise background-image, otherwise try dataset or srcset
    let url = null;

    if (el && el.tagName && el.tagName.toLowerCase() === "img") {
      url = el.currentSrc || el.src || null;
    }

    if (!url) {
      // Try data attributes commonly used for lazy load
      const dataAttrs = ["data-src", "data-original", "data-lazy-src", "data-srcset"];
      for (const a of dataAttrs) {
        if (el && el.getAttribute && el.getAttribute(a)) {
          url = el.getAttribute(a);
          break;
        }
      }
    }

    if (!url) {
      url = getBackgroundImageUrl(el);
    }

    if (!url) {
      // check inside element for <img> child
      const imgChild = el.querySelector && el.querySelector("img");
      if (imgChild) url = imgChild.currentSrc || imgChild.src || null;
    }

    if (!url) {
      makeToast("No image URL found on that element.");
      cleanup();
      return;
    }

    // Resolve relative URLs to absolute
    try {
      url = new URL(url, location.href).href;
    } catch (e) {
      // leave as-is if invalid
    }

    // Try to copy to clipboard — must be within user gesture (click) so OK
    try {
      await navigator.clipboard.writeText(url);
      makeToast("Image URL copied to clipboard.");
    } catch (err) {
      // fallback: show prompt so user can copy manually
      const fallback = prompt("Image URL (copy manually):", url);
      if (fallback === null) {
        // user cancelled
      }
    }

    // Also log to console for debug
    console.log("Inspector captured image URL:", url);

    // Cleanup and exit inspector mode
    cleanup();
  }

  function handleKeyDown(e) {
    if (e.key === "Escape") {
      makeToast("Inspector cancelled.");
      cleanup();
    }
  }

  function cleanup() {
    // Remove event listeners and restore cursor
    document.removeEventListener("click", handleClick, true);
    document.removeEventListener("keydown", handleKeyDown, true);
    if (hint && hint.parentNode) hint.remove();
    if (blocker && blocker.parentNode) blocker.remove();
    document.documentElement.style.cursor = prevCursor || "";
    document.body.style.cursor = prevCursor || "";
    window.__inspectorActive = false;

    // allow re-injection in future if needed
    setTimeout(() => {
      window.__elementInspectorInjected = false;
    }, 50);
  }

  // Attach listeners in capture phase so we intercept clicks before page handlers
  document.addEventListener("click", handleClick, true);
  document.addEventListener("keydown", handleKeyDown, true);

  // If user navigates away or page unloads, cleanup automatically
  window.addEventListener("beforeunload", cleanup, { once: true });
})();
