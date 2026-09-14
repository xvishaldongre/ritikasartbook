/* =========================================================
   ritikasartbook — interactions
   Nav state, mobile menu, htmx modal, copy-email, back-to-top
   ========================================================= */
(function () {
  "use strict";

  var $  = function (sel, root) { return (root || document).querySelector(sel); };
  var $$ = function (sel, root) {
    return Array.prototype.slice.call((root || document).querySelectorAll(sel));
  };

  /* ---------------------------------------------------- mobile menu */
  var burger = $(".burger");
  var navLinks = $("#nav-links");

  function closeMenu() {
    if (!navLinks) return;
    navLinks.classList.remove("is-open");
    if (burger) burger.setAttribute("aria-expanded", "false");
  }

  if (burger && navLinks) {
    burger.addEventListener("click", function () {
      var open = navLinks.classList.toggle("is-open");
      burger.setAttribute("aria-expanded", open ? "true" : "false");
    });
  }

  /* --------------------------------------------- smooth anchor scroll */
  document.addEventListener("click", function (evt) {
    var link = evt.target.closest ? evt.target.closest('a[href^="#"]') : null;
    if (!link) return;

    var id = link.getAttribute("href");
    if (!id || id === "#") return;

    var target = document.querySelector(id);
    if (!target) return;

    evt.preventDefault();
    closeMenu();

    var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    target.scrollIntoView({ behavior: reduce ? "auto" : "smooth", block: "start" });
    history.replaceState(null, "", id);
    target.setAttribute("tabindex", "-1");
    target.focus({ preventScroll: true });
  });

  /* ------------------------------------------------- scroll spy + sticky */
  var sections = $$("main section[id]");
  var navAnchors = $$(".nav-links a[data-nav]");
  var header = $(".site-head");
  var toTop = $("#to-top");

  function setActive(id) {
    navAnchors.forEach(function (a) {
      a.classList.toggle("is-active", a.getAttribute("data-nav") === id);
    });
  }

  if ("IntersectionObserver" in window && sections.length) {
    var visible = {};
    var spy = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { visible[en.target.id] = en.intersectionRatio; });
      var best = null, bestRatio = 0;
      Object.keys(visible).forEach(function (key) {
        if (visible[key] > bestRatio) { bestRatio = visible[key]; best = key; }
      });
      if (best) setActive(best);
    }, {
      rootMargin: "-30% 0px -45% 0px",
      threshold: [0, 0.15, 0.35, 0.6, 1]
    });
    sections.forEach(function (s) { spy.observe(s); });
  }

  function onScroll() {
    var y = window.scrollY || window.pageYOffset;
    if (header) header.classList.toggle("is-stuck", y > 10);
    if (toTop) toTop.classList.toggle("is-visible", y > 600);
  }
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  if (toTop) {
    toTop.addEventListener("click", function () {
      var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
      window.scrollTo({ top: 0, behavior: reduce ? "auto" : "smooth" });
      closeMenu();
    });
  }

  /* ------------------------------------------------------------ modal */
  var modal = $("#modal");
  var modalBody = $("#modal-body");
  var lastFocused = null;

  function openModal() {
    if (!modal) return;
    lastFocused = document.activeElement;
    modal.hidden = false;
    modal.classList.add("is-open");
    document.body.style.overflow = "hidden";
    var panel = $("#modal-panel");
    if (panel) {
      panel.scrollTop = 0;
      panel.focus({ preventScroll: true });
    }
  }

  function closeModal() {
    if (!modal || !modal.classList.contains("is-open")) return;
    modal.classList.remove("is-open");
    modal.hidden = true;
    document.body.style.overflow = "";
    if (modalBody) modalBody.innerHTML = "";
    if (lastFocused && lastFocused.focus) lastFocused.focus();
  }

  document.addEventListener("click", function (evt) {
    if (evt.target.closest && evt.target.closest("[data-close-modal]")) {
      // a "commission this" link inside the modal should still scroll the page
      var isAnchor = evt.target.closest('a[href^="#"]');
      closeModal();
      if (!isAnchor) evt.preventDefault();
    }
  });

  document.addEventListener("keydown", function (evt) {
    if (evt.key === "Escape") { closeModal(); closeMenu(); }
    if (evt.key === "Tab" && modal && modal.classList.contains("is-open")) trapFocus(evt);
  });

  function trapFocus(evt) {
    var focusables = $$(
      'a[href], button:not([disabled]), input, select, textarea, [tabindex]:not([tabindex="-1"])',
      modal
    ).filter(function (el) { return el.offsetParent !== null; });
    if (!focusables.length) return;
    var first = focusables[0];
    var last = focusables[focusables.length - 1];
    if (evt.shiftKey && document.activeElement === first) {
      evt.preventDefault(); last.focus();
    } else if (!evt.shiftKey && document.activeElement === last) {
      evt.preventDefault(); first.focus();
    }
  }

  /* --------------------------------------------- htmx wiring */
  if (window.htmx) {
    // a work-detail fragment landed -> show it
    document.body.addEventListener("htmx:afterSwap", function (evt) {
      if (evt.detail && evt.detail.target === modalBody) openModal();
    });

    // "show all N" finished -> retire the now-empty footer
    document.body.addEventListener("htmx:afterRequest", function (evt) {
      var elt = evt.detail && evt.detail.elt;
      if (!elt || !evt.detail.successful) return;
      if (!elt.hasAttribute || !elt.hasAttribute("data-retire-foot")) return;
      var foot = elt.closest(".gallery-foot");
      if (foot) foot.remove();
    });

    // keep the "active" pill in sync on the portfolio filter bar
    document.body.addEventListener("htmx:beforeRequest", function (evt) {
      var elt = evt.detail && evt.detail.elt;
      if (elt && elt.hasAttribute && elt.hasAttribute("data-filter")) {
        $$("[data-filter]").forEach(function (b) { b.classList.remove("is-active"); });
        elt.classList.add("is-active");
      }
    });

    // friendly failure text instead of a silent empty box
    document.body.addEventListener("htmx:responseError", function (evt) {
      var target = evt.detail && evt.detail.target;
      if (!target) return;
      if (target === modalBody) {
        modalBody.innerHTML =
          '<p class="lede">Sorry — that preview could not be loaded. ' +
          'Please refresh, or email <a href="mailto:ritikasartbook@gmail.com">' +
          'ritikasartbook@gmail.com</a>.</p>';
        openModal();
      } else {
        target.insertAdjacentHTML(
          "beforebegin",
          '<p class="lede">Sorry, that did not load. Please refresh the page.</p>'
        );
      }
    });
  }

  /* ------------------------------------------------- copy email chip */
  var copyBtn = $("#copy-email");
  if (copyBtn) {
    copyBtn.addEventListener("click", function () {
      var email = copyBtn.getAttribute("data-email");
      var status = $("#copy-status");
      var done = function (ok) {
        if (!status) return;
        status.textContent = ok ? "Copied! " + email : email + " (copy manually)";
        window.setTimeout(function () {
          status.textContent = "One click, no typing";
        }, 2600);
      };
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(email).then(function () { done(true); },
          function () { done(false); });
      } else {
        var tmp = document.createElement("textarea");
        tmp.value = email;
        document.body.appendChild(tmp);
        tmp.select();
        try { document.execCommand("copy"); done(true); }
        catch (err) { done(false); }
        document.body.removeChild(tmp);
      }
    });
  }
})();
