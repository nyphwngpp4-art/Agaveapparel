import re, json, sys
from urllib.parse import urljoin, urlparse
from playwright.sync_api import sync_playwright
import os; U = os.environ.get("U", "https://agave-apparel-preview.pages.dev"); Q = "/workspace/agave-apparel/qa/v2/flow"
errors, bad, seen = [], [], set()
with sync_playwright() as pw:
    b = pw.chromium.launch()
    for w, h in [(390, 844), (1280, 900)]:
        pg = b.new_page(viewport={"width": w, "height": h})
        pg.on("console", lambda m, w=w: m.type == "error" and errors.append(f"{w}: {m.text}"))
        pg.on("pageerror", lambda e, w=w: errors.append(f"{w}: {e}"))
        pg.on("response", lambda r, w=w: r.status >= 400 and "/api/checkout" not in r.url and bad.append(f"{w}: {r.status} {r.url}"))
        pg.goto(U + "/", wait_until="networkidle"); pg.screenshot(path=f"{Q}/home-{w}.png", full_page=True)
        pg.goto(U + "/products/golden-hour/", wait_until="networkidle"); pg.screenshot(path=f"{Q}/product-{w}.png", full_page=True)
        pg.click("button[type=submit]"); assert pg.evaluate("!document.querySelector(\"[data-add-to-cart]\").checkValidity()") and pg.inner_text("[data-cart-count]")=="(0)"
        pg.check("input[value=XL]"); pg.click("button[type=submit]"); pg.wait_for_selector(".msg a")
        pg.screenshot(path=f"{Q}/added-{w}.png")
        pg.goto(U + "/cart/", wait_until="networkidle"); pg.wait_for_selector(".cartlist")
        assert "$36" in pg.inner_text("[data-cart-total]"), pg.inner_text("[data-cart-total]")
        pg.screenshot(path=f"{Q}/cart-{w}.png", full_page=True)
        pg.click("[data-checkout]"); pg.wait_for_selector(".notice")
        print(w, "checkout:", pg.inner_text(".notice")); pg.screenshot(path=f"{Q}/checkout-{w}.png", full_page=True)
        imgs = pg.evaluate("[...document.images].filter(i=>!i.alt).length"); print(w, "imgs without alt on cart:", imgs)
        pg.close()
    # crawl every internal link + check alt on each page
    ctx = b.new_page(); todo = ["/"]; noalt = []
    while todo:
        p = todo.pop(); 
        if p in seen: continue
        seen.add(p); r = ctx.goto(U + p, wait_until="domcontentloaded")
        if r.status != 200: bad.append(f"crawl {r.status} {p}"); continue
        noalt += [p for _ in range(ctx.evaluate("[...document.images].filter(i=>!i.alt.trim()).length"))]
        for href in ctx.eval_on_selector_all("a[href]", "els=>els.map(e=>e.getAttribute('href'))"):
            u = urlparse(urljoin(U + p, href))
            if u.netloc == urlparse(U).netloc and u.path not in seen: todo.append(u.path)
    print("pages crawled:", len(seen), "missing alt:", noalt)
    b.close()
print("console errors:", errors); print("bad responses:", bad)

# Lighthouse-ish: CLS and LCP per page/viewport (fresh load, scrolled through like a reader).
PERF = """() => new Promise(res => {
  let cls = 0, lcp = null;
  new PerformanceObserver(l => { for (const e of l.getEntries()) if (!e.hadRecentInput) cls += e.value; }).observe({type: 'layout-shift', buffered: true});
  new PerformanceObserver(l => { const e = l.getEntries().at(-1); lcp = {t: Math.round(e.startTime), el: e.element ? e.element.tagName + '.' + (e.element.className || '') : '', size: e.size,
     w: e.element && e.element.getAttribute && e.element.getAttribute('width')}; }).observe({type: 'largest-contentful-paint', buffered: true});
  setTimeout(() => res({cls: +cls.toFixed(4), lcp}), 1500);
})"""
with sync_playwright() as pw:
    b = pw.chromium.launch()
    for w, h in [(390, 844), (1280, 860)]:
        for path in ["/", "/products/golden-hour/", "/shop/", "/cart/"]:
            pg = b.new_page(viewport={"width": w, "height": h}); pg.goto(U + path, wait_until="load")
            print(w, path, pg.evaluate(PERF)); pg.close()
    b.close()
