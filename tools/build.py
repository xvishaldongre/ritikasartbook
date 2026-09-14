#!/usr/bin/env python3
"""Build ritikasartbook.com - a static, htmx-powered portfolio.

Sources of truth
  data/works.json                          -> all artwork entries + category copy
  assets/css/style.css, assets/js/main.js  -> hand written
Outputs
  index.html
  partials/*.html                          -> htmx fragments

Run:  python3 tools/build.py
"""
import html
import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = json.loads((ROOT / "data" / "works.json").read_text(encoding="utf-8"))

SITE = {
    "name": "ritikasartbook",
    "artist": "Ritika",
    "handle": "@ritikasartbook",
    "instagram": "https://www.instagram.com/ritikasartbook/",
    "email": "ritikasartbook@gmail.com",
    "domain": "ritikasartbook.com",
    "tagline": "Whimsical illustration, book covers, character design & surface pattern",
    "year": date.today().year,
}

# how many cards render inline in each category section before the htmx "show more"
INLINE_PER_SECTION = 4

CATEGORIES = DATA["categories"]
WORKS = DATA["works"]
BY_CAT = {c["slug"]: [w for w in WORKS if w["category"] == c["slug"]] for c in CATEGORIES}
CAT_LABEL = {c["slug"]: c["label"] for c in CATEGORIES}
FEATURED = [w for w in WORKS if w.get("featured")]


def e(text):
    return html.escape(str(text), quote=True)


# --------------------------------------------------------------------------- cards
def card(work, peek=True):
    cat_label = CAT_LABEL[work["category"]]
    peek_btn = ""
    if peek:
        peek_btn = (
            f'\n      <button class="card-peek" type="button"'
            f'\n              hx-get="partials/work/{e(work["id"])}.html"'
            f'\n              hx-target="#modal-body"'
            f'\n              hx-swap="innerHTML"'
            f'\n              aria-label="See more about {e(work["title"])}">'
            f'\n        Peek closer <span aria-hidden="true">&rarr;</span>'
            f"\n      </button>"
        )
    return f"""    <article class="card" id="work-{e(work["id"])}">
      <div class="card-media">
        <img src="images/{e(work["id"])}.svg" alt="{e(work["alt"])}"
             width="800" height="600" loading="lazy" decoding="async">
        <span class="card-tag">{e(cat_label)}</span>
      </div>
      <div class="card-body">
        <h3>{e(work["title"])}</h3>
        <p>{e(work["blurb"])}</p>
      </div>{peek_btn}
    </article>"""


def card_grid(items):
    return "\n".join(card(w) for w in items)


def work_detail(work):
    cat = next(c for c in CATEGORIES if c["slug"] == work["category"])
    pills = "".join(f'<span class="pill">{e(t)}</span>' for t in work["tags"])
    return f"""<div class="modal-art">
  <img src="images/{e(work["id"])}.svg" alt="{e(work["alt"])}"
       width="800" height="600">
</div>
<p class="eyebrow">{e(cat["icon"])} {e(cat["label"])}</p>
<h2>{e(work["title"])}</h2>
<p class="lede">{e(work["blurb"])}</p>
<p>{e(work["detail"])}</p>
<div class="pill-row">{pills}</div>
<p style="margin-top:22px">
  <a class="btn btn--pink" href="#contact" data-close-modal>
    Commission something like this <span aria-hidden="true">&#10024;</span>
  </a>
</p>
"""


# --------------------------------------------------------------------------- nav
NAV_ITEMS = [("portfolio", "Portfolio", "#portfolio")]
NAV_ITEMS += [(c["slug"], c["nav"], f'#{c["slug"]}') for c in CATEGORIES]
NAV_ITEMS += [("about", "About", "#about"), ("contact", "Contact", "#contact")]


def nav_links():
    return "\n".join(
        f'          <li><a href="{href}" data-nav="{slug}">{e(label)}</a></li>'
        for slug, label, href in NAV_ITEMS
    )


# --------------------------------------------------------------------------- sections
def portfolio_section():
    filters = ['<button class="btn btn--ghost is-active" type="button"'
               ' hx-get="partials/filter-all.html" hx-target="#portfolio-grid"'
               ' hx-swap="innerHTML" hx-indicator="#portfolio-loading"'
               ' data-filter="all">All work</button>']
    for c in CATEGORIES:
        filters.append(
            f'<button class="btn btn--ghost" type="button"'
            f' hx-get="partials/filter-{c["slug"]}.html" hx-target="#portfolio-grid"'
            f' hx-swap="innerHTML" hx-indicator="#portfolio-loading"'
            f' data-filter="{c["slug"]}">{e(c["icon"])} {e(c["nav"])}</button>'
        )
    return f"""  <section class="section" id="portfolio" aria-labelledby="portfolio-title">
    <div class="wrap">
      <div class="section-head center">
        <span class="eyebrow">&#127912; Selected work</span>
        <h2 id="portfolio-title">A little shelf of favourite pieces</h2>
      </div>

      <div class="hero-actions" style="justify-content:center" role="group"
           aria-label="Filter work by category">
        {"".join(filters)}
      </div>

      <p style="text-align:center">
        <span id="portfolio-loading" class="htmx-indicator lede">&#10024; fetching&hellip;</span>
      </p>

      <div class="grid grid--wide" id="portfolio-grid" aria-live="polite">
{card_grid(FEATURED)}
      </div>
    </div>
  </section>"""


def category_section(cat, index):
    works = BY_CAT[cat["slug"]]
    first, rest = works[:INLINE_PER_SECTION], works[INLINE_PER_SECTION:]
    more_block = ""
    if rest:
        more_block = f"""
      <div class="gallery-foot">
        <button class="btn btn--lav" type="button"
                hx-get="partials/{cat["slug"]}-more.html"
                hx-target="#grid-{cat["slug"]}"
                hx-swap="beforeend"
                hx-indicator="#more-loading-{cat["slug"]}"
                data-retire-foot="true">
          Show all {len(works)} {e(cat["label"].lower())}
          <span aria-hidden="true">&#128071;</span>
        </button>
        <span id="more-loading-{cat["slug"]}" class="htmx-indicator lede"
              style="margin-left:12px">&#10024; loading&hellip;</span>
      </div>"""
    return f"""  <section class="section" id="{cat["slug"]}" aria-labelledby="{cat["slug"]}-title">
    <div class="wrap">
      <div class="section-head">
        <span class="eyebrow">{cat["icon"]} {e(cat["label"])}</span>
        <h2 id="{cat["slug"]}-title">{e(cat["label"])}</h2>
        <p class="lede">{e(cat["blurb"])}</p>
      </div>

      <div class="grid" id="grid-{cat["slug"]}">
{card_grid(first)}
      </div>{more_block}
    </div>
  </section>"""


# --------------------------------------------------------------------------- page
def build_index():
    about_facts = [
        ("&#127912;", "Illustration for picture books, middle grade and editorial"),
        ("&#128218;", "Book covers designed with space for type and shelf appeal"),
        ("&#127800;", "Seamless surface patterns for fabric, wallpaper and packaging"),
        ("&#128062;", "Character design with turnarounds, expressions and story bibles"),
        ("&#128172;", "Friendly, deadline-respecting collaboration from sketch to print files"),
    ]
    facts = "\n".join(
        f'          <li><span class="ico" aria-hidden="true">{ico}</span>'
        f'<span>{text}</span></li>'
        for ico, text in about_facts
    )
    nav_blocks = "\n\n".join(category_section(c, i) for i, c in enumerate(CATEGORIES))

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{SITE["name"]} &mdash; {SITE["tagline"]}</title>
<meta name="description" content="Portfolio of {SITE["artist"]} ({SITE["name"]}) &mdash;
  whimsical children's book illustration, book covers, general illustration,
  character design and surface pattern. Open for commissions and licensing.">
<meta name="author" content="{SITE["artist"]} &mdash; {SITE["name"]}">
<meta name="theme-color" content="#ffe3ec">
<link rel="canonical" href="https://{SITE["domain"]}/">

<meta property="og:type" content="website">
<meta property="og:title" content="{SITE["name"]} &mdash; {SITE["tagline"]}">
<meta property="og:description" content="Whimsical illustration, book covers, character
  design and surface pattern by {SITE["artist"]}.">
<meta property="og:url" content="https://{SITE["domain"]}/">
<meta property="og:image" content="https://{SITE["domain"]}/images/og-cover.svg">
<meta name="twitter:card" content="summary_large_image">

<link rel="icon" href="favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="images/logo.svg">

<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Baloo+2:wght@500;600;700;800&family=Caveat:wght@600;700&family=Quicksand:wght@400;500;600;700&display=swap" rel="stylesheet">

<link rel="stylesheet" href="assets/css/style.css">
<script src="assets/vendor/htmx.min.js" defer></script>
<script src="assets/js/main.js" defer></script>
</head>
<body>
<a class="skip-link" href="#portfolio">Skip to the artwork</a>

<div class="bg-bloom" aria-hidden="true"><span></span><span></span><span></span><span></span></div>

<header class="site-head">
  <nav class="nav wrap" aria-label="Main">
    <a class="brand" href="#top">
      <img src="images/logo.svg" alt="" width="42" height="42">
      ritikasartbook
    </a>

    <button class="burger" type="button" aria-expanded="false" aria-controls="nav-links"
            aria-label="Open menu">&#9776;</button>

    <ul class="nav-links" id="nav-links">
{nav_links()}
    </ul>

    <a class="nav-cta" href="#contact" aria-label="Say hello">
      <span class="nav-cta-text">Say hello</span> <span aria-hidden="true">&#128075;</span>
    </a>
  </nav>
</header>

<main id="top">

  <!-- ============ HERO / ARTIST INTRO ============ -->
  <section class="hero wrap" aria-labelledby="hero-title">
    <div class="hero-grid">
      <div class="hero-copy">
        <span class="eyebrow">&#10024; Open for commissions &amp; licensing</span>
        <h1 id="hero-title">Hi, I&rsquo;m {SITE["artist"]} &mdash; I draw
          <span class="hl">whimsical</span> little worlds.</h1>
        <p class="hero-role">children&rsquo;s book illustration &middot; book covers &middot;
          general illustration &middot; character design &middot; surface pattern</p>
        <p class="lede">I make soft, story-filled pictures where the moon misplaces a shoe,
          garden gnomes have opinions, and every character has a favourite snack. If you need
          artwork that feels like a warm bedtime story, you&rsquo;re in the right place.</p>

        <div class="hero-actions">
          <a class="btn btn--pink" href="#portfolio">See the portfolio
            <span aria-hidden="true">&#127912;</span></a>
          <a class="btn btn--mint" href="mailto:{SITE["email"]}">Work with me
            <span aria-hidden="true">&#9993;&#65039;</span></a>
        </div>

        <ul class="hero-contact">
          <li>
            <a class="chip" href="{SITE["instagram"]}" target="_blank" rel="noopener">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                <rect x="3" y="3" width="18" height="18" rx="5" stroke="#6b5b71" stroke-width="2"/>
                <circle cx="12" cy="12" r="4.2" stroke="#6b5b71" stroke-width="2"/>
                <circle cx="17.4" cy="6.6" r="1.4" fill="#6b5b71"/>
              </svg>
              {SITE["handle"]}
            </a>
          </li>
          <li>
            <a class="chip" href="mailto:{SITE["email"]}">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                <rect x="2.5" y="5" width="19" height="14" rx="3.5" stroke="#6b5b71" stroke-width="2"/>
                <path d="M4 7.5l8 5.5 8-5.5" stroke="#6b5b71" stroke-width="2"
                      stroke-linecap="round"/>
              </svg>
              {SITE["email"]}
            </a>
          </li>
        </ul>
      </div>

      <div class="hero-art">
        <picture>
          <source srcset="images/hero-ritika.webp" type="image/webp">
          <img class="hero-art-figure" src="images/hero-ritika.png"
               alt="Illustrated portrait of Ritika: a character with blue hair in a
                    top-knot, a yellow heart-print tee and a backpack, smiling with
                    her arms folded"
               width="900" height="900" fetchpriority="high">
        </picture>
      </div>
    </div>
  </section>

  <!-- ============ RIBBON ============ -->
  <div class="ribbon" aria-hidden="true">
    <div class="ribbon-track">
      <span>&#127912; picture books</span><span>&#10024; book covers</span>
      <span>&#128062; characters</span><span>&#127800; surface pattern</span>
      <span>&#9728;&#65039; general illustration</span><span>&#128171; licensing</span>
      <span>&#127912; picture books</span><span>&#10024; book covers</span>
      <span>&#128062; characters</span><span>&#127800; surface pattern</span>
      <span>&#9728;&#65039; general illustration</span><span>&#128171; licensing</span>
    </div>
  </div>

{portfolio_section()}

{nav_blocks}

  <!-- ============ ABOUT ============ -->
  <section class="section" id="about" aria-labelledby="about-title">
    <div class="wrap">
      <div class="about-grid">
        <div>
          <span class="eyebrow">&#128156; The artist</span>
          <h2 id="about-title">Soft pictures, made carefully</h2>
          <p class="lede">I&rsquo;m {SITE["artist"]} &mdash; the artist behind
            {SITE["name"]}. I illustrate for children&rsquo;s books and for the small,
            lovely things around them: covers, patterns, characters and the occasional
            editorial spread.</p>
          <p>My work leans pastel and playful, with a strong line and a lot of heart.
            I like art that a child can read before they can read words &mdash; clear
            silhouettes, warm faces, and one feeling per picture.</p>
          <a class="btn btn--lav" href="mailto:{SITE["email"]}?subject=Illustration%20enquiry">
            Start a project <span aria-hidden="true">&#128640;</span></a>
        </div>

        <div class="about-card">
          <h3>What I can make for you</h3>
          <ul class="fact-list">
{facts}
          </ul>
          <p class="foot-note" style="margin-top:16px">
            Studio replies usually within 1&ndash;2 working days.
          </p>
        </div>
      </div>
    </div>
  </section>

  <!-- ============ CONTACT ============ -->
  <section class="section" id="contact" aria-labelledby="contact-title">
    <div class="wrap">
      <div class="contact-shell">
        <span class="eyebrow">&#128236; Contact</span>
        <h2 id="contact-title">Let&rsquo;s make something whimsical</h2>
        <p class="lede" style="max-width:640px;margin-inline:auto">
          Tell me about your book, your product or your brand &mdash; a rough deadline,
          a favourite thing your character does, anything. The quickest way to reach me
          is Instagram DM or email.
        </p>

        <div class="contact-cards">
          <a class="contact-card" href="{SITE["instagram"]}" target="_blank" rel="noopener">
            <span class="ico" aria-hidden="true">&#128247;</span>
            <strong>Instagram</strong>
            <span>{SITE["handle"]} &mdash; DMs open, fastest reply</span>
          </a>
          <a class="contact-card" href="mailto:{SITE["email"]}?subject=Illustration%20enquiry">
            <span class="ico" aria-hidden="true">&#9993;&#65039;</span>
            <strong>Email</strong>
            <span>{SITE["email"]}</span>
          </a>
          <button class="contact-card" type="button" id="copy-email"
                  data-email="{SITE["email"]}">
            <span class="ico" aria-hidden="true">&#128203;</span>
            <strong>Copy my email</strong>
            <span id="copy-status">One click, no typing</span>
          </button>
        </div>

        <p class="copy-row">Currently taking on picture-book, cover and licensing projects
          for the next season.</p>
      </div>
    </div>
  </section>
</main>

<footer class="site-foot">
  <div class="wrap foot-grid">
    <div>
      <a class="brand" href="#top">
        <img src="images/logo.svg" alt="" width="42" height="42">
        ritikasartbook
      </a>
      <p class="foot-note">&copy; {SITE["year"]} {SITE["artist"]} &middot; {SITE["name"]}.
        All artwork is copyrighted; please don&rsquo;t reuse without permission.</p>
    </div>
    <ul class="foot-links">
      <li><a href="#portfolio">Portfolio</a></li>
      <li><a href="#book-cover">Book cover</a></li>
      <li><a href="#general-illustration">General illustration</a></li>
      <li><a href="#character-design">Character design</a></li>
      <li><a href="#surface-pattern">Surface pattern</a></li>
      <li><a href="mailto:{SITE["email"]}">Email</a></li>
      <li><a href="{SITE["instagram"]}" target="_blank" rel="noopener">Instagram</a></li>
    </ul>
  </div>
</footer>

<button class="to-top" type="button" id="to-top" aria-label="Back to top"
        title="Back to top">&#8679;</button>

<!-- ============ htmx MODAL ============ -->
<div class="modal" id="modal" role="dialog" aria-modal="true"
     aria-label="Artwork details" hidden>
  <button class="modal-backdrop" type="button" data-close-modal
          aria-label="Close details"></button>
  <div class="modal-panel" id="modal-panel">
    <button class="modal-close" type="button" data-close-modal
            aria-label="Close details">&#10005;</button>
    <div id="modal-body"></div>
  </div>
</div>

<noscript>
  <div class="wrap" style="padding:24px 0">
    <p class="lede">JavaScript is off, so the htmx filters and &ldquo;peek closer&rdquo;
      pop-ups are unavailable &mdash; every gallery section still shows its artwork above,
      just without the fancy bits.</p>
  </div>
</noscript>
</body>
</html>
"""


def build_partials():
    out = ROOT / "partials"
    (out / "work").mkdir(parents=True, exist_ok=True)
    written = []

    def dump(path, text):
        path.write_text(text, encoding="utf-8")
        written.append(path.relative_to(ROOT))

    # portfolio filter fragments
    dump(out / "filter-all.html", card_grid(FEATURED) + "\n")
    for c in CATEGORIES:
        items = [w for w in FEATURED if w["category"] == c["slug"]]
        if items:
            dump(out / f'filter-{c["slug"]}.html', card_grid(items) + "\n")

    # "show more" fragments per category
    for c in CATEGORIES:
        rest = BY_CAT[c["slug"]][INLINE_PER_SECTION:]
        if rest:
            dump(out / f'{c["slug"]}-more.html', card_grid(rest) + "\n")

    # per-work detail fragments
    for w in WORKS:
        dump(out / "work" / f'{w["id"]}.html', work_detail(w))

    return written


if __name__ == "__main__":
    (ROOT / "index.html").write_text(build_index(), encoding="utf-8")
    files = build_partials()
    print(f"index.html written ({len(WORKS)} works, {len(CATEGORIES)} categories)")
    print(f"{len(files)} partials written to partials/")
