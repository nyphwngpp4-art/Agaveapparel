"""Generate the static preview (v2, "Golden Hour Editorial") into ./out from ../site-snapshot/products.json."""
import json, html, shutil, colorsys
from pathlib import Path
from PIL import Image
from alt import ALT

ROOT = Path(__file__).parent
SNAP = ROOT.parent / "site-snapshot"
OUT = ROOT / "out"
SRC = ROOT / "src"
BASE = "https://agave-apparel-preview.pages.dev"
SIZES = ["S", "M", "L", "XL", "2XL", "3XL"]
# v4 catalog: just the 10 real design files Courtney has (designs-v2/clean/NN.*), in her order.
V4 = ["soul-to-sole", "bandana-triangle", "agave-over-hills", "bull-head", "red-rays-for-days",
      "black-rays-for-days", "rays-for-days", "patterened-agave", "from-the-desert-to-the-glass", "agave-desert-life"]
_ALL = {p["slug"]: p for p in json.load(open(SNAP / "products.json"))}
P = [_ALL[s] for s in V4]
CLEAN = ROOT.parent / "designs-v2" / "clean"
N = len(P)
E = html.escape


def hexc(rgb): return "#%02x%02x%02x" % tuple(int(round(c)) for c in rgb)


# Palette (from the logo): bone paper, oxblood ink, agave leaf, mist support.
BONE, INK, AGAVE, MIST = "#E6E2DB", "#250909", "#7A8985", "#CDD1CB"


def mix(a, b, t):
    return hexc([int(a[i:i + 2], 16) * (1 - t) + int(b[i:i + 2], 16) * t for i in (1, 3, 5)])


def color_world(slug, im):
    """Per-design page tint inside the system: bone pulled toward agave by how much cool/green the print holds
    (4-20%). No new hues; ink text throughout."""
    small = im.resize((80, 80)).convert("RGB")
    cool = sum(1 for r, g, b in small.getdata() if g >= r - 6 and abs(g - b) < 40 and max(r, g, b) - min(r, g, b) > 18) / 6400
    t = round(min(0.2, max(0.04, 0.04 + cool * 0.6)), 3)
    return {"bg": mix(BONE, AGAVE, t), "fg": INK, "tile": hexc(im.getpixel((8, 8))), "t": t}


def ed_name(name):
    """T4 treatment for a design name: first word italic, the rest in caps."""
    first, _, rest = name.partition(" ")
    return f"<em>{E(first)}</em> <span class=\"caps\">{E(rest)}</span>" if rest else f"<em>{E(name)}</em>"


def head(path, title, desc, image, extra=""):
    url = BASE + path
    return f"""<!doctype html><html lang="en" class="no-js"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(title)}</title><meta name="description" content="{E(desc)}">
<meta name="robots" content="noindex,nofollow"><link rel="canonical" href="{url}">
<meta name="theme-color" content="#3B2B47">
<meta property="og:type" content="website"><meta property="og:site_name" content="Agave Apparel Co.">
<meta property="og:title" content="{E(title)}"><meta property="og:description" content="{E(desc)}">
<meta property="og:url" content="{url}"><meta property="og:image" content="{BASE}{image}">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{E(title)}">
<meta name="twitter:description" content="{E(desc)}"><meta name="twitter:image" content="{BASE}{image}">
<link rel="icon" href="/favicon.ico" sizes="any"><link rel="icon" type="image/png" href="/favicon-32.png"><link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="preload" href="/fonts/instrument-serif.woff2" as="font" type="font/woff2" crossorigin><link rel="preload" href="/fonts/instrument-serif-italic.woff2" as="font" type="font/woff2" crossorigin><link rel="preload" href="/fonts/familjen-grotesk.woff2" as="font" type="font/woff2" crossorigin>
<script>document.documentElement.classList.remove("no-js");document.fonts&&document.fonts.ready.then(function(){{document.documentElement.classList.add("fonts-ready")}});setTimeout(function(){{document.documentElement.classList.add("fonts-ready")}},1200)</script><link rel="stylesheet" href="/site.css">{extra}</head><body>
<div class="preview" role="note">Preview, not the live store</div>"""


def nav(solid=True):
    logo = "/logo.svg" if solid else "/logo-light.svg"
    return f"""<header class="site{' solid' if solid else ''}">
<nav class="nav-l" aria-label="Shop"><a class="u" href="/shop/">Shop</a><a class="u" href="/about/">About</a></nav>
<a class="mast" href="/"><img src="{logo}" width="150" height="104" alt="Agave Apparel Co., home"></a>
<nav class="nav-r" aria-label="Help and cart"><a class="u" href="/contact/">Contact</a><a class="u" href="/cart/">Cart <span class="count" data-cart-count>(0)</span></a></nav></header>"""


FOOT = """<footer><div class="wrap fgrid"><div><a class="mast" href="/"><img src="/logo-light.svg" width="170" height="118" loading="lazy" alt="Agave Apparel Co."></a><p style="max-width:24rem">Small-batch graphic tees designed in the Sonoran Desert. One-of-a-kind pieces for people who don't dress like everyone else.</p></div>
<div><h4>Shop</h4><ul><li><a class="u" href="/shop/">All designs</a></li><li><a class="u" href="/about/">Our story</a></li><li><a class="u" href="/contact/">Contact</a></li></ul></div>
<div><h4>Orders</h4><ul><li><a class="u" href="mailto:orders@agaveapparel.com">orders@agaveapparel.com</a></li><li>Phoenix, Arizona</li></ul></div></div>
<div class="wrap fbottom"><div>© 2026 Agave Apparel Co. Designed in AZ, shipped everywhere.</div><div>Designed by Courtney Messamore</div></div></footer>
<script src="/cart.js" defer></script><script src="/lightbox.js" defer></script>"""


def pic(slug, sizes, eager=False, cls=""):
    load = 'fetchpriority="high"' if eager else 'loading="lazy" decoding="async"'
    return (f'<img{cls} src="/img/designs/{slug}-960.webp" srcset="/img/designs/{slug}-600.webp 600w, /img/designs/{slug}-960.webp 948w" '
            f'sizes="{sizes}" width="948" height="948" {load} alt="{E(ALT[slug])}">')


def card(p, i):
    # The image is a button (opens the viewer); the caption is the link to the product page.
    return f"""<article class="card"><button class="tile" type="button" data-lb="{p['slug']}" aria-label="View {E(p['name'])} larger">{pic(p['slug'], "(min-width:900px) 31vw, 46vw")}</button>
<a class="meta u-host" href="/products/{p['slug']}/"><span class="idx">{i:02d}</span><h3><span class="u">{E(p['name'])}</span></h3><span class="p">${p['price']}</span><p class="tag">{E(p['tagline'])}</p></a></article>"""


def write(rel, s):
    f = OUT / rel; f.parent.mkdir(parents=True, exist_ok=True); f.write_text(s)


def page(path, title, desc, body, image="/img/og.jpg", extra="", solid=True):
    return head(path, title, desc, image, extra) + (nav(solid) if solid else "") + f"<main>{body}</main>" + FOOT + "</body></html>"


VIDEO = ROOT.parent / "hero-video"
VIDEO_FILES = ["hero.mp4", "hero.webm", "hero-mobile.mp4", "hero-poster.jpg"]


def hero_video():
    """Hook: if ../hero-video/ has the footage, copy it and emit <video>; otherwise a palette-only fallback.
    The <video> has no autoplay attribute: home.js starts it unless prefers-reduced-motion or Save-Data,
    so reduced-motion visitors only ever see the poster."""
    have = [f for f in VIDEO_FILES if (VIDEO / f).exists() and (VIDEO / f).stat().st_size > 0]
    if "hero-poster.jpg" not in have or not ({"hero.mp4", "hero.webm"} & set(have)):
        return '<div class="fallback"><img src="/logo-leaf.svg" alt="" width="1500" height="1040"></div><!-- hero video hook: add files to hero-video/ and rebuild -->'
    (OUT / "video").mkdir(exist_ok=True)
    for f in have: shutil.copy(VIDEO / f, OUT / "video" / f)
    src = []
    if "hero-mobile.mp4" in have: src.append('<source src="/video/hero-mobile.mp4" type="video/mp4" media="(max-width: 760px)">')
    if "hero.webm" in have: src.append('<source src="/video/hero.webm" type="video/webm">')
    if "hero.mp4" in have: src.append('<source src="/video/hero.mp4" type="video/mp4">')
    return ('<video data-hero-video muted loop playsinline preload="none" poster="/video/hero-poster.jpg" width="1920" height="1080">'
            + "".join(src) + '</video>')


def build():
    if OUT.exists(): shutil.rmtree(OUT)
    (OUT / "img/designs").mkdir(parents=True)
    worlds = {}
    for i, p in enumerate(P, 1):
        im = Image.open(CLEAN / f"{i:02d}.png").convert("RGB")   # 1600 square, bone edge to edge
        crop = im.resize((948, 948), Image.LANCZOS)
        im = im.resize((1200, 1200), Image.LANCZOS)
        crop.save(OUT / f"img/designs/{p['slug']}-960.webp", quality=84)
        crop.resize((600, 600), Image.LANCZOS).save(OUT / f"img/designs/{p['slug']}-600.webp", quality=80)
        im.save(OUT / f"img/designs/{p['slug']}-1200.jpg", quality=84)  # OG / JSON-LD
        worlds[p["slug"]] = color_world(p["slug"], crop)
    logo = Image.open(SNAP / "agaveapparel.com/designs/agave-apparel-logo-larger.png").convert("RGBA")
    bg = Image.new("RGBA", (max(logo.size),) * 2, logo.getpixel((5, 5)))
    bg.paste(logo, ((bg.width - logo.width) // 2, (bg.height - logo.height) // 2), logo)
    bg.resize((180, 180), Image.LANCZOS).save(OUT / "apple-touch-icon.png")
    bg.resize((32, 32), Image.LANCZOS).save(OUT / "favicon-32.png")
    bg.save(OUT / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])
    og = Image.new("RGB", (1200, 630), (243, 235, 221)); lo = logo.copy(); lo.thumbnail((700, 520))
    og.paste(lo, ((1200 - lo.width) // 2, (630 - lo.height) // 2), lo); og.save(OUT / "img/og.jpg", quality=88)
    for f in ["site.css", "cart.js", "home.js", "lightbox.js", "logo.svg", "logo-light.svg", "logo-leaf.svg"]: shutil.copy(SRC / f, OUT / f)
    shutil.copytree(SRC / "vendor", OUT / "vendor"); shutil.copytree(SRC / "fonts", OUT / "fonts")
    cat = {p["slug"]: {"name": p["name"], "price": p["price"]} for p in P}
    (ROOT / "functions/_lib/catalog.json").write_text(json.dumps(cat, indent=1))
    write("products.json", json.dumps(cat))
    write("designs.json", json.dumps([{"slug": p["slug"], "name": p["name"], "price": p["price"], "tagline": p["tagline"], "alt": ALT[p["slug"]]} for p in P]))

    hero_media = hero_video()
    feat = next(p for p in P if p["slug"] == "black-rays-for-days")
    home = f"""<section class="hero" aria-labelledby="h">{nav(False)}
<div class="hero-media" aria-hidden="true">{hero_media}</div><div class="scrim" aria-hidden="true"></div>
<h1 id="h" class="sr-only">Dressed different, on purpose.</h1><p class="word w1" aria-hidden="true">Dressed</p><p class="word w2" aria-hidden="true">Different</p>
<div class="hero-foot"><div><p>Small-batch graphic tees designed in the Sonoran Desert. One-of-a-kind pieces for people who’d rather wear a conversation than a logo.</p></div>
<div class="cta-row"><a class="btn btn-fill" href="/shop/">Shop all {N} designs</a><span class="rule" aria-hidden="true"></span><span class="num" aria-hidden="true">{N}</span></div></div>
</section>

<section class="wrap sec feature" aria-labelledby="fh">
<div><div class="scratch" data-scratch>{pic(feat['slug'], "(min-width:900px) 56vw, 92vw")}<canvas aria-hidden="true"></canvas></div>
<p class="hint">This is the featured print under a layer of desert dust. Drag across it to wipe it clean (side to side on a phone).</p></div>
<div><h2 id="fh" class="ed"><em>Rays</em> <span class="caps">for days,</span> <em>after dark.</em></h2>
<p class="lede">{E(feat['meta_description'])}</p>
<p><span class="price">${feat['price']}</span></p>
<div class="actions"><a class="btn btn-ink" href="/products/{feat['slug']}/">Choose a size for {E(feat['name'])}</a></div></div>
</section>

<section class="sec coll" aria-labelledby="ch"><div class="wrap">
<div class="coll-head"><h2 id="ch" class="ed"><em>Pieces you</em> <span class="caps">won’t see</span> <em>on everyone else.</em></h2><span class="num" aria-hidden="true">{N}</span></div>
<div class="grid">{''.join(card(p, i + 1) for i, p in enumerate(P[1:7], start=1))}</div>
<div class="more"><a class="btn btn-ink" href="/shop/">See all {N} designs</a></div></div></section>

<section class="dusk"><div class="wrap sec story">
<h2 class="ed"><em>Built by a desert kid</em> <span class="caps">who never wanted</span> <em class="leaf">to blend in.</em></h2>
<div><p>Courtney has always dressed like herself — not anyone else. Agave Apparel is her way of sharing that: wearable art pulled from Arizona sunsets, saguaro shadows, and the kind of days that make you glad you live where you do.</p>
<p><a class="u" href="/about/">Read Courtney’s story</a></p></div></div></section>

<section class="wrap sec" aria-labelledby="hh"><h2 id="hh" class="ed" style="font-size:clamp(2.4rem,5vw,4.6rem)"><em>Pick a design,</em> <span class="caps">pick your size.</span></h2>
<div class="steps"><ol><li><h3>Browse</h3><p>Twenty-two designs and counting. Each one is its own thing — no two Agave closets look alike.</p></li>
<li><h3>Order</h3><p>Choose your size, add it to your cart and check out securely with a card.</p></li>
<li><h3>Wear it out</h3><p>Everything is printed small-batch. You’ll get something made for you, not mass-produced for the algorithm.</p></li></ol></div></section>

<section class="close"><div class="wrap sec"><h2 class="ed"><em>Your closet called.</em><br><span class="caps">It wants something different.</span></h2>
<div class="actions" style="justify-content:center;margin-top:2.5rem"><a class="btn btn-fill" href="/shop/">Shop all designs</a></div></div></section>"""
    # steps markup: ol inside .steps grid
    home = home.replace('<div class="steps"><ol>', '<ol class="steps">').replace('</li></ol></div></section>', '</li></ol></section>')
    write("index.html", page("/", "Agave Apparel Co. — Small-batch desert graphic tees", "Small-batch graphic tees designed in the Sonoran Desert. One-of-a-kind pieces for people who’d rather wear a conversation than a logo.", home,
          extra='<script src="/home.js" defer></script>', solid=False))

    shop = f"""<section class="sec coll"><div class="wrap"><div class="coll-head"><h1 class="ed"><em>All</em> <span class="caps">{N} designs.</span></h1><span class="num" aria-hidden="true">{N}</span></div>
<div class="grid">{''.join(card(p, i + 1) for i, p in enumerate(P))}</div></div></section>"""
    write("shop/index.html", page("/shop/", "Shop — Agave Apparel Co.", f"All {N} Agave Apparel designs: small-batch desert graphic tees, $28–$38.", shop))

    about = """<section class="wrap sec plain prose"><h1 class="ed"><em>A small brand</em> <span class="caps">made in the sun.</span></h1>
<p>Agave Apparel started the way most good things do — because the founder couldn’t find what she wanted, so she made it.</p>
<p>Courtney Messamore has always dressed a little differently. Not to stand out for the sake of it — she just never liked the idea of opening her closet and seeing the same thing everyone else was wearing. She wanted her clothes to actually say something about her: about where she’s from, what she loves, and the way she moves through the world.</p>
<p>What she loves, mostly, is the Arizona desert. Sunsets that stop you in the parking lot. The quiet of the saguaros at dusk. The way 110-degree heat turns into a cold river float and then into golden hour. The agave plant that takes eight years to grow and then gives you a lifetime’s worth of stories. The smell of creosote after a rare rain.</p>
<p>Every design in this small collection comes from that. Some are loud. Some are quiet. All of them are hers — drawn, colored, and chosen in the same town she’s always called home.</p>
<p>Agave Apparel is deliberately small. Everything is printed in limited runs, on soft cotton, for people who want to wear something that nobody else has twenty of. If that sounds like your closet too — welcome.</p>
<div class="actions"><a class="btn btn-ink" href="/shop/">Shop the collection</a></div>
<ol class="steps" style="counter-reset:none"><li><h3>Designed in Arizona</h3><p>Every piece starts as a sketch in the desert she calls home.</p></li><li><h3>Small batch, always</h3><p>No endless inventory. No overproduction. If you like it, grab it.</p></li><li><h3>Printed on cotton you’ll actually wear</h3><p>Soft, broken-in, unisex relaxed fit. Meant to get better with every wash.</p></li></ol></section>"""
    about = about.replace('<ol class="steps" style="counter-reset:none">', '<ol class="steps nocount">')
    write("about/index.html", page("/about/", "About — Agave Apparel Co.", "Agave Apparel is Courtney Messamore’s small-batch tee brand, designed in Arizona.", about))
    contact = """<section class="wrap sec plain prose"><h1 class="ed"><em>Say</em> <span class="caps">hi.</span></h1>
<p>Orders, custom design requests, wholesale inquiries, or a nice note about a sunset — it all goes to the same inbox and Courtney reads every one.</p>
<p>We’re a tiny operation, so response time is usually a day or two.</p>
<p><a class="u" href="mailto:orders@agaveapparel.com">orders@agaveapparel.com</a><br>Phoenix, Arizona</p></section>"""
    write("contact/index.html", page("/contact/", "Contact — Agave Apparel Co.", "Get in touch with Agave Apparel Co. in Phoenix, Arizona.", contact))

    for i, p in enumerate(P, start=1):
        w = worlds[p["slug"]]
        others = [o for o in P if o["slug"] != p["slug"]][:3]
        ld = {"@context": "https://schema.org", "@type": "Product", "name": p["name"], "description": p["meta_description"],
              "image": f"{BASE}/img/designs/{p['slug']}-1200.jpg", "sku": p["slug"], "brand": {"@type": "Brand", "name": "Agave Apparel Co."},
              "offers": {"@type": "Offer", "price": f"{p['price']}.00", "priceCurrency": "USD", "availability": "https://schema.org/InStock", "url": f"{BASE}/products/{p['slug']}/"}}
        radios = "".join(f'<label><input type="radio" name="size" value="{s}" required><span>{s}</span></label>' for s in SIZES)
        body = f"""<div class="world" style="--w-bg:{w['bg']};--w-fg:{w['fg']};--w-tile:{w['tile']}">{nav()}
<div class="wrap"><a class="back u" href="/shop/">Back to all {N} designs</a></div>
<div class="wrap pd"><button class="shot" type="button" data-lb="{p['slug']}" data-magnify aria-label="View {E(p['name'])} larger">{pic(p['slug'], "(min-width:960px) 56vw, 92vw", eager=True)}</button>
<div class="info"><span class="num" aria-hidden="true">{i:02d}/{N}</span><p class="sr-only">Design {i} of {N}</p>
<h1 class="ed">{ed_name(p['name'])}</h1><p class="tagline">{E(p['tagline'])}</p>
<p class="price" style="margin-top:1.6rem">${p['price']}</p><p class="desc">{E(p['meta_description'])}</p>
<form data-add-to-cart data-slug="{p['slug']}"><fieldset><legend>Size (Bella+Canvas 3001, unisex)</legend><div class="sizes">{radios}</div></fieldset>
<div class="actions"><button class="btn btn-ink" type="submit">Add to cart</button><a class="u" href="/cart/">View cart</a></div><div class="msg" role="status" aria-live="polite"></div></form>
<dl class="specs"><div><dt>Fabric</dt><dd>100% cotton, soft-washed</dd></div><div><dt>Fit</dt><dd>Unisex, relaxed</dd></div><div><dt>Printed</dt><dd>Small-batch, Arizona</dd></div><div><dt>Ships</dt><dd>Usually within 7–10 days</dd></div></dl></div></div></div>
<section class="sec coll"><div class="wrap"><h2 class="ed" style="font-size:clamp(2.2rem,4.5vw,3.8rem);margin-bottom:2.5rem"><em>You might</em> <span class="caps">also wear</span></h2>
<div class="grid">{''.join(card(o, P.index(o) + 1) for o in others)}</div></div></section>"""
        extra = (f'<meta property="product:price:amount" content="{p["price"]}.00"><meta property="product:price:currency" content="USD">'
                 f'<meta name="theme-color" content="{w["bg"]}"><script type="application/ld+json">{json.dumps(ld)}</script>')
        write(f"products/{p['slug']}/index.html", page(f"/products/{p['slug']}/", f"{p['name']} — Agave Apparel Co.", p["meta_description"], body,
              image=f"/img/designs/{p['slug']}-1200.jpg", extra=extra, solid=False))

    cart = """<section class="wrap sec plain" style="max-width:56rem"><h1 class="ed"><em>Your</em> <span class="caps">cart</span></h1>
<div data-cart-root><p>Your cart is empty. <a class="u" href="/shop/">Browse the collection</a>.</p></div>
<div class="total"><span>Subtotal</span><span data-cart-total>$0</span></div><p class="note">Shipping and tax are added at checkout.</p>
<button class="btn btn-ink" type="button" data-checkout disabled>Check out</button><div data-checkout-msg role="status" aria-live="polite"></div></section>"""
    write("cart/index.html", page("/cart/", "Cart — Agave Apparel Co.", "Your Agave Apparel cart.", cart))
    write("checkout/success/index.html", page("/checkout/success/", "Thank you — Agave Apparel Co.", "Order received.", '<section class="wrap sec plain prose"><h1 class="ed"><em>Thank</em> <span class="caps">you.</span></h1><p>Your order is in. A receipt is on its way to your email.</p><p><a class="u" href="/shop/">Back to the collection</a></p></section><script>localStorage.removeItem("agave-cart")</script>'))
    write("404.html", page("/404", "Not found — Agave Apparel Co.", "Page not found.", '<section class="wrap sec plain prose"><h1 class="ed"><em>Lost in</em> <span class="caps">the desert.</span></h1><p>That page doesn’t exist. <a class="u" href="/shop/">Back to the collection</a>.</p></section>'))
    urls = ["/", "/shop/", "/about/", "/contact/"] + [f"/products/{p['slug']}/" for p in P]
    write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(f"<url><loc>{BASE}{u}</loc></url>\n" for u in urls) + "</urlset>\n")
    write("robots.txt", f"# Preview copy: keep out of search engines.\nUser-agent: *\nDisallow: /\n\nSitemap: {BASE}/sitemap.xml\n")
    write("_headers", "/*\n  X-Robots-Tag: noindex, nofollow\n  X-Content-Type-Options: nosniff\n  Referrer-Policy: strict-origin-when-cross-origin\n/vendor/*\n  Cache-Control: public, max-age=31536000, immutable\n/fonts/*\n  Cache-Control: public, max-age=31536000, immutable\n")
    json.dump(worlds, open(ROOT / "worlds.json", "w"), indent=1)


if __name__ == "__main__":
    build(); print("built", sum(1 for _ in OUT.rglob("*") if _.is_file()), "files")
