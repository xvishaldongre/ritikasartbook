#!/usr/bin/env python3
"""Live smoke test: drive the deployed site through the Chrome DevTools Protocol.

Runs real clicks in the page's own context, so it exercises the actual htmx
requests against GitHub Pages (not a local copy).

    .venv/bin/python tools/live_check.py [url]

Requires Chrome already listening on --remote-debugging-port=9222.
"""
import json
import sys
import time
import urllib.parse
import urllib.request

import websocket

URL = sys.argv[1] if len(sys.argv) > 1 else \
    "https://xvishaldongre.github.io/ritikasartbook/index.html"
PORT = 9222

TEST_JS = r"""
(async () => {
  const L = [];
  const log = s => L.push(s);
  const wait = ms => new Promise(r => setTimeout(r, ms));
  const uniq = a => a.filter((v, i) => a.indexOf(v) === i);
  const cards = r => r.querySelectorAll('.card');
  const d = document, w = window;

  log('url           : ' + w.location.href);
  log('title         : ' + d.title);
  log('');

  log('== assets ==');
  log('  htmx         : ' + (typeof w.htmx !== 'undefined' ? w.htmx.version : 'MISSING'));
  log('  Baloo 2      : ' + d.fonts.check('700 40px "Baloo 2"'));
  log('  Quicksand    : ' + d.fonts.check('500 17px Quicksand'));
  const fig = d.querySelector('.hero-art-figure');
  log('  hero src     : ' + fig.currentSrc.split('/').pop());
  log('  hero decoded : ' + fig.naturalWidth + 'x' + fig.naturalHeight +
      ' (' + Math.round(fig.currentSrc.length ? 0 : 0) + ')');
  const bad = [];
  [...d.images].forEach(im => { if (im.complete && im.naturalWidth === 0) bad.push(im.getAttribute('src')); });
  log('  images       : ' + d.images.length + ' total, ' + bad.length + ' broken' +
      (bad.length ? ' -> ' + bad.join(', ') : ''));
  log('');

  log('== TEST 1: portfolio filter (live htmx fetch) ==');
  d.querySelector('[data-filter="book-cover"]').click();
  await wait(2500);
  const pg = d.querySelector('#portfolio-grid');
  log('  cards        : ' + cards(pg).length);
  log('  tags         : ' + uniq([...pg.querySelectorAll('.card-tag')].map(t => t.textContent.trim())).join(' / '));
  log('  active pill  : ' + d.querySelector('[data-filter].is-active').dataset.filter);
  d.querySelector('[data-filter="all"]').click();
  await wait(2500);
  log('  back to All  : ' + cards(pg).length + ' cards');
  log('');

  log('== TEST 2: show all (live htmx fetch) ==');
  const mb = d.querySelector('#book-cover [data-retire-foot]');
  log('  button       : ' + (mb ? 'found' : 'MISSING'));
  if (mb) {
    mb.click();
    await wait(2800);
    log('  cards        : ' + cards(d.querySelector('#grid-book-cover')).length);
    log('  footer gone  : ' + !d.querySelector('#book-cover .gallery-foot'));
  }
  log('');

  log('== TEST 3: work modal (live htmx fetch) ==');
  const pk = d.querySelector('#work-general-illustration-1 .card-peek');
  pk.click();
  await wait(2800);
  const body = d.querySelector('#modal-body');
  log('  modal open   : ' + d.querySelector('#modal').classList.contains('is-open'));
  log('  heading      : ' + (body.querySelector('h2') ? body.querySelector('h2').textContent : 'NONE'));
  log('  detail image : ' + (body.querySelector('img') ? body.querySelector('img').naturalWidth : 0) + 'px wide');
  log('  tag pills    : ' + body.querySelectorAll('.pill').length);
  d.querySelector('.modal-close').click();
  await wait(400);
  log('  closed       : ' + !d.querySelector('#modal').classList.contains('is-open') +
      ', body cleared: ' + (body.innerHTML === ''));
  log('');

  log('== TEST 4: nav anchor scroll ==');
  const before = w.scrollY;
  d.querySelector('.nav-links a[href="#character-design"]').click();
  await wait(1200);
  const sec = d.querySelector('#character-design').getBoundingClientRect().top;
  log('  scrollY      : ' + Math.round(before) + ' -> ' + Math.round(w.scrollY));
  log('  section top  : ' + Math.round(sec) + 'px (should clear the sticky nav)');
  log('');

  log('== layout ==');
  log('  overflowX    : ' + (d.documentElement.scrollWidth > w.innerWidth + 1 ? 'YES ***' : 'no') +
      ' (scrollWidth=' + d.documentElement.scrollWidth + ', innerWidth=' + w.innerWidth + ')');
  log('  brand        : "' + d.querySelector('.brand').textContent.trim() + '"');
  log('  sections     : ' + d.querySelectorAll('main section[id]').length);
  log('  total cards  : ' + d.querySelectorAll('.card').length);
  log('  nav anchors  : ' + [...d.querySelectorAll('.nav-links a')].map(a => a.getAttribute('href')).join(' '));
  log('  IG link      : ' + !!d.querySelector('a[href*="instagram.com/ritikasartbook"]'));
  log('  email link   : ' + !!d.querySelector('a[href^="mailto:ritikasartbook@gmail.com"]'));
  log('');
  log('DONE');
  return L.join('\n');
})()
"""


def cdp(ws, method, params=None, msg_id=[0]):
    msg_id[0] += 1
    ws.send(json.dumps({"id": msg_id[0], "method": method, "params": params or {}}))
    while True:
        msg = json.loads(ws.recv())
        if msg.get("id") == msg_id[0]:
            return msg


def main():
    # open a fresh tab on the target url
    req = urllib.request.Request(
        f"http://127.0.0.1:{PORT}/json/new?{urllib.parse.quote(URL, safe='')}",
        method="PUT",
    )
    tab = json.loads(urllib.request.urlopen(req, timeout=10).read())
    ws_url = tab["webSocketDebuggerUrl"]
    print(f"-> {URL}\n")

    # suppress_origin: Chrome rejects CDP websockets carrying a browser Origin
    ws = websocket.create_connection(ws_url, timeout=90, suppress_origin=True)
    cdp(ws, "Page.enable")
    cdp(ws, "Runtime.enable")
    time.sleep(5)  # let fonts, images and htmx settle

    res = cdp(ws, "Runtime.evaluate", {
        "expression": TEST_JS,
        "awaitPromise": True,
        "returnByValue": True,
    })
    result = res.get("result", {}).get("result", {})
    if "value" in result:
        print(result["value"])
    else:
        print("no value returned; raw:", json.dumps(res)[:800])

    cdp(ws, "Target.closeTarget", {"targetId": tab["id"]})
    ws.close()


if __name__ == "__main__":
    main()
