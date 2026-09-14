# ritikasartbook.com

Whimsical pastel portfolio site for **Ritika** — children&rsquo;s book illustration, book
covers, general illustration, character design and surface pattern.

Static HTML + CSS, with [htmx](https://htmx.org) doing the interactive bits. No build
toolchain, no framework, no server-side code: it is ready for GitHub Pages.

---

## Preview it locally

```bash
python3 tools/serve.py          # http://127.0.0.1:8788
```

`tools/serve.py` is a tiny threaded static server (the stdlib&rsquo;s plain
`python3 -m http.server` is single threaded and stalls when a browser opens several
connections at once).

## What&rsquo;s on the page

| Section | Anchor | Notes |
| --- | --- | --- |
| Artist intro | `#top` / hero | Intro, Instagram `@ritikasartbook`, email `ritikasartbook@gmail.com` |
| Selected work | `#portfolio` | htmx filter pills swap the grid in place |
| Book Cover | `#book-cover` | htmx &ldquo;show all&rdquo; appends the rest |
| General Illustration | `#general-illustration` | same pattern |
| Character Design | `#character-design` | same pattern |
| Surface Pattern | `#surface-pattern` | same pattern |
| About | `#about` | longer artist bio + services |
| Contact | `#contact` | Instagram, email, and a copy-email button |

Every navbar link is a same-page anchor, so clicking one smooth-scrolls to that
section (`scroll-margin-top` keeps it clear of the sticky header).

### Where htmx is used

1. **Portfolio filters** — each pill `hx-get`s a fragment from `partials/filter-*.html`
   into `#portfolio-grid`.
2. **Show all** — `partials/<category>-more.html` is appended with
   `hx-swap="beforeend"`, then the button retires itself.
3. **Peek closer** — clicking a card loads `partials/work/<id>.html` into the modal.
4. **Graceful failure** — `htmx:responseError` shows a friendly message instead of a
   blank box.

If JavaScript is off, all sections still render their first four pieces inline and the
page stays readable — htmx only adds the extras.

---

## Editing the content

All artwork entries live in **`data/works.json`**:

```json
{
  "id": "book-cover-1",
  "category": "book-cover",
  "featured": true,
  "title": "The Moon's Lost Slipper",
  "blurb": "One line that shows under the card.",
  "alt": "Accessible description of the image.",
  "tags": ["Picture book", "Ages 3-6", "Gouache"],
  "detail": "The longer story shown in the 'peek closer' pop-up."
}
```

After editing, rebuild the HTML and fragments:

```bash
python3 tools/build.py
```

That regenerates `index.html` and everything in `partials/`. Never hand-edit those
generated files — edit `data/works.json`, `assets/css/style.css`, `assets/js/main.js`
or `tools/build.py` instead.

`id` must match an image filename in `images/` (for example `book-cover-1` →
`images/book-cover-1.svg`).

## Replacing the placeholder artwork

The gallery images in `images/` are **generated pastel placeholders** so the layout
reads correctly. To use real artwork:

1. Drop your images into `images/` using the same names as the entry `id`
   (`book-cover-1.svg` → `book-cover-1.jpg`). If you change the extension, update
   `card()` / `work_detail()` in `tools/build.py` and re-run the build.
2. Adjust the `alt` text in `data/works.json` to describe the real artwork.
3. Replace `images/og-cover.svg` with a social-share image (1200×630) that uses your
   own art — it is what shows up when the site is shared on Instagram or WhatsApp.

`tools/gen_art.py` regenerates the placeholders if you ever want them back.

### The hero illustration

The hero uses a **real drawing**: a head-and-shoulders portrait cropped from
`~/Downloads/hero-art.png`, shown as a round portrait on a pastel disc.

```bash
.venv/bin/python tools/prepare_hero.py                  # uses ~/Downloads/hero-art.png
.venv/bin/python tools/prepare_hero.py path/to/other.png
.venv/bin/python tools/prepare_hero.py other.png --mode full
```

That script finds the figure by its alpha channel, crops the empty canvas away,
trims stray export marks, and writes `images/hero-ritika.webp` (served first, ~72 KB)
plus `images/hero-ritika.png` (fallback, ~380 KB). The heavy source PNG stays in
`Downloads` and is never committed.

Two modes:

- `bust` (default) — a square head-and-torso crop framed for the round portrait
- `full` — the whole figure, cut out, if you ever want the full-body version somewhere

Crop tuning lives in the constants at the top of the script. `BODY_CENTRE_SHIFT`
matters most: the backpack widens the bounding box on one side, so this nudges the
crop left to keep her face centred in the circle. If she looks off-centre, adjust it.

To change how large the portrait sits inside its pastel disc, edit `.hero-art-figure`
`width`/`height` in `assets/css/style.css` (currently `86%`, with a dashed ring at
`2%` and the disc filling the box). Keep everything between `0%` and `100%` — the
decoration is positioned inside the box on purpose so it can never cause horizontal
scrolling.

The image tools need Pillow, which lives in a local virtualenv (git-ignored):

```bash
python3 -m venv .venv && .venv/bin/pip install Pillow numpy
```

---

## Deploying to GitHub Pages

Only run this once the local preview looks right. The deploy is **two stages**, so the
GitHub Pages preview works immediately and the custom domain can follow whenever DNS
is ready.

### Stage 1 — publish to GitHub Pages

```bash
bash tools/deploy.sh
```

Creates the public repo under your account, commits and pushes, and turns on Pages
for the branch root. No `CNAME` file is written, so the site is live at:

```
https://xvishaldongre.github.io/ritikasartbook/
```

Override defaults with `REPO=... BRANCH=... bash tools/deploy.sh`.

### Stage 2 — point ritikasartbook.com at it

Add these DNS records at your registrar first:

| Type | Name | Value |
| --- | --- | --- |
| A | `@` | `185.199.108.153` |
| A | `@` | `185.199.109.153` |
| A | `@` | `185.199.110.153` |
| A | `@` | `185.199.111.153` |
| CNAME | `www` | `xvishaldongre.github.io` |

Then, once DNS resolves:

```bash
SET_CUSTOM_DOMAIN=1 bash tools/deploy.sh
```

That writes the `CNAME` file (from `tools/CNAME.custom-domain`) and sets the custom
domain on the Pages config. Finally tick **Enforce HTTPS** in *Settings → Pages* once
the certificate is issued.

> Adding the `CNAME` before DNS resolves makes the `github.io` URL redirect to
> `ritikasartbook.com` and appear broken — which is exactly why stage 1 leaves it out.

---

## Project layout

```
index.html            generated — the whole one-page site
404.html              whimsical not-found page
robots.txt, sitemap.xml, favicon.svg
data/works.json       ← the content you edit
partials/             generated htmx fragments
  filter-*.html         portfolio filter results
  <category>-more.html  "show all" batches
  work/<id>.html        modal details
assets/css/style.css  the pastel theme
assets/js/main.js     nav state, modal, copy-email, error handling
assets/vendor/        htmx 2.0.4, vendored so it works offline
images/               generated placeholders + the real hero portrait
  hero-ritika.webp      the hero portrait (served first, ~72 KB)
  hero-ritika.png       hero portrait fallback
tools/
  build.py            JSON → index.html + partials
  gen_art.py          regenerates the placeholder SVGs
  prepare_hero.py     crops the hero portrait out of a source PNG
  serve.py            local preview server
  deploy.sh           repo + Pages (+ optional custom domain)
  CNAME.custom-domain the domain stage 2 copies into CNAME
```

## Colours and type

Pastels are CSS custom properties at the top of `assets/css/style.css`
(`--pink`, `--mint`, `--butter`, `--sky`, `--lav`, `--peach`). Fonts are Baloo 2
(headings), Quicksand (body) and Caveat (handwritten accents), loaded from Google
Fonts with system fallbacks.

## Accessibility notes

- Skip link, sensible heading order, and `alt` text on every image.
- Modal traps focus, closes on <kbd>Esc</kbd>, backdrop click, and restores focus.
- Nav marks the active section and the mobile menu button is `aria-expanded` aware.
- `prefers-reduced-motion` disables the drifting blobs, floating art and smooth
  scrolling.
