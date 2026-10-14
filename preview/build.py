"""Generate the static preview of agaveapparel.com into ./out from ../site-snapshot/products.json."""
import json, html, shutil, os
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).parent
SNAP = ROOT.parent / "site-snapshot"
OUT = ROOT / "out"
BASE = "https://agave-apparel-preview.pages.dev"
SIZES = ["S", "M", "L", "XL", "2XL", "3XL"]
P = json.load(open(SNAP / "products.json"))
E = html.escape

# Descriptive alt text, written from looking at each image.
ALT = {
 "agave-apparel-fade-orange-to-yello": "White t-shirt with a rounded badge of a green agave over a yellow-to-orange fade, lettered Agave Apparel",
 "agave-desert-life": "Cream t-shirt printed with a desert sunset scene, saguaros and an agave under the words Agave Apparel, Desert Life",
 "agave-love": "Cream t-shirt with an arched sunset window over a sage-green agave and the words Agave Love",
 "agave-over-hills": "Inverted triangle graphic of a sun over rolling brown hills with an orange agave, above Agave T-Shirt Co. lettering",
 "agave-to-tequila": "Cream t-shirt with a small row of icons on the chest: an agave, a piña, a jug and a tequila bottle",
 "arizona-state-image": "Arizona state outline filled with retro orange, yellow and teal stripes, a rust sun and the word Arizona",
 "bandana-triangle": "Triangle bandana-style graphic with a sun, desert plants and a large agave, lettered Agave Apparel",
 "black-rays-for-days": "Black t-shirt with a striped sunset over red mesas and cacti, lettered Rays for Days",
 "bull-head": "Brown longhorn steer skull above an agave, framed by arched Agave T-Shirt Co. lettering",
 "cactus-in-sun-brown": "Cream t-shirt with a brown saguaro inside a rust sun with rays, and small Agave T-Shirt Co text",
 "desert-life": "Light grey t-shirt with a round striped sunset in brown and orange over the words Desert Life",
 "from-the-desert-to-the-glass": "Cream t-shirt with a green agave and curved text From the Desert to the Glass, Agave Apparel, T-Shirt Co.",
 "golden-hour": "Arched window graphic of a teal sky, yellow sun, orange mesas and cacti over the words Golden Hour, Agave Apparel",
 "leave-a-mark": "Brown rattlesnake winding across a desert with a boot print and agave, under arched Leave a Mark lettering",
 "orange-rays-for-days": "Orange t-shirt with a sun and a green agave between the words Rays For and Days",
 "out-west": "Cream t-shirt with a thin line drawing of a saguaro, agave and hills above the words Out West",
 "patterened-agave": "White t-shirt with a diamond-shaped Southwestern geometric pattern around a blue-green agave",
 "rays-for-days": "Cream t-shirt with an arched sun over a desert road and saguaro, lettered Rays for Days",
 "red-rays-for-days": "Coral red t-shirt with a rising sun above stacked cream letters Rays for Days",
 "rounded-window-agave": "Cream t-shirt with a rounded adobe-window graphic of a sunset gradient over a pale green agave",
 "soul-to-sole": "Cream t-shirt with a boot sole print, cactus and sun under the words Soul to Sole",
 "stay-salty-salt-river": "Cream t-shirt with an agave over a winding river through red canyons, lettered Stay Salty, Salt River",
}

CSS = """
:root{--bone:#f5efe6;--sand:#e8dfd0;--ink:#2b2a26;--dust:#7a6f5d;--agave:#3d4a3a;--terracotta:#a4542e;--sun:#e2a73f}
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bone);color:var(--ink);font:16px/1.6 Inter,ui-sans-serif,system-ui;-webkit-font-smoothing:antialiased}
a{color:inherit}img{display:block;max-width:100%;height:auto}
.wrap{max-width:1400px;margin:0 auto;padding:0 1.5rem}@media(min-width:768px){.wrap{padding:0 2.5rem}}
.display{font-family:Fraunces,Georgia,serif;font-weight:400;letter-spacing:-.02em;line-height:1.05;margin:0}
.mono{font-family:"JetBrains Mono",ui-monospace,monospace}
.eyebrow{font-size:.75rem;font-weight:500;color:var(--dust);text-transform:uppercase;letter-spacing:.18em}
.preview{background:var(--terracotta);color:var(--bone);text-align:center;font-size:.8rem;padding:.45rem 1rem}
.strip{background:var(--agave);color:var(--bone);text-align:center;font-size:.72rem;letter-spacing:.18em;text-transform:uppercase;padding:.5rem}
header.site{position:sticky;top:0;z-index:20;background:rgba(245,239,230,.92);backdrop-filter:blur(8px);border-bottom:1px solid rgba(43,42,38,.1)}
.bar{display:flex;align-items:center;justify-content:space-between;padding-block:.8rem;gap:1rem}
.brand{display:flex;align-items:center;gap:.6rem;text-decoration:none}.brand img{width:64px;mix-blend-mode:multiply}@media(max-width:520px){.brand .eyebrow{display:none}nav{gap:1rem;font-size:.88rem}}
nav{display:flex;gap:1.4rem;font-size:.92rem}nav a{text-decoration:none}nav a:hover{color:var(--terracotta)}
.btn{display:inline-flex;align-items:center;justify-content:center;padding:.8rem 1.75rem;font-size:.85rem;text-transform:uppercase;letter-spacing:.18em;text-decoration:none;border:1px solid var(--ink);cursor:pointer;font-family:inherit;transition:background .2s,color .2s}
.btn-primary{background:var(--ink);color:var(--bone)}.btn-primary:hover{background:var(--agave)}
.btn-outline{background:transparent;color:var(--ink)}.btn-outline:hover{background:var(--ink);color:var(--bone)}
.btn[disabled]{opacity:.45;cursor:not-allowed}
.hero{display:grid;gap:3rem;padding-block:4rem 5rem;align-items:center}@media(min-width:900px){.hero{grid-template-columns:7fr 5fr;padding-block:6rem}}
.hero h1{font-size:clamp(3rem,8vw,6.5rem)}.lede{font-size:1.15rem;color:rgba(43,42,38,.75);max-width:34rem;margin-top:1.5rem}
.actions{display:flex;flex-wrap:wrap;gap:1rem;margin-top:2.25rem}
.tile{background:var(--bone);border:1px solid rgba(43,42,38,.06);overflow:hidden;aspect-ratio:1}.tile img{width:100%;height:100%;object-fit:cover;transition:transform .7s}
a.card{text-decoration:none;display:block}a.card:hover img{transform:scale(1.03)}
.card-row{display:flex;justify-content:space-between;gap:1rem;margin-top:.9rem}.card h3{font-family:Fraunces,serif;font-weight:400;font-size:1.2rem;line-height:1.2;margin:0}.card p{margin:.2rem 0 0;font-size:.88rem;color:var(--dust)}
.grid{display:grid;grid-template-columns:repeat(2,1fr);gap:3rem 1.25rem}@media(min-width:768px){.grid{grid-template-columns:repeat(3,1fr);gap:3.5rem 1.5rem}}
.pad{padding-block:5rem}.band{background:var(--agave);color:var(--bone);text-align:center;font-size:.72rem;letter-spacing:.18em;text-transform:uppercase;padding:1.4rem}
.sand{background:var(--sand)}.inkbg{background:var(--ink);color:var(--bone)}
.sec-head{display:flex;justify-content:space-between;align-items:flex-end;flex-wrap:wrap;gap:1.5rem;margin-bottom:3rem}.sec-head h2,.big{font-size:clamp(2.4rem,5vw,3.8rem)}
.split{display:grid;gap:3rem;align-items:center}@media(min-width:900px){.split{grid-template-columns:5fr 7fr}}
.steps{display:grid;gap:2.5rem;margin-top:3.5rem}@media(min-width:768px){.steps{grid-template-columns:repeat(3,1fr)}}.steps>div{border-top:1px solid rgba(43,42,38,.15);padding-top:1.4rem}.steps h3{font-family:Fraunces,serif;font-weight:400;font-size:1.8rem;margin:.6rem 0}
.prose{max-width:40rem}.prose p{font-size:1.08rem;line-height:1.75;color:rgba(43,42,38,.82)}
.product{display:grid;gap:3rem;padding-block:3rem 5rem}@media(min-width:900px){.product{grid-template-columns:7fr 5fr;gap:4rem}}
.price{font-size:1.4rem;margin-top:1.5rem}
fieldset{border:0;padding:0;margin:2rem 0 0}legend{padding:0;margin-bottom:.75rem}
.sizes{display:flex;flex-wrap:wrap;gap:.5rem}.sizes label{position:relative}.sizes input{position:absolute;opacity:0;inset:0}
.sizes span{display:inline-block;min-width:3.3rem;text-align:center;padding:.6rem .7rem;border:1px solid rgba(43,42,38,.3);font-family:"JetBrains Mono",monospace;font-size:.9rem;cursor:pointer}
.sizes input:checked+span{background:var(--ink);color:var(--bone);border-color:var(--ink)}.sizes input:focus-visible+span{outline:2px solid var(--terracotta);outline-offset:2px}
.specs{margin-top:2.5rem;border-top:1px solid rgba(43,42,38,.15)}.specs div{display:flex;justify-content:space-between;gap:1rem;padding:.7rem 0;border-bottom:1px solid rgba(43,42,38,.1);font-size:.92rem}.specs dt{color:var(--dust)}.specs dd{margin:0;text-align:right}
.note{font-size:.88rem;color:var(--dust);margin-top:1rem}.msg{min-height:1.5rem;margin-top:.8rem;font-size:.92rem;color:var(--agave)}
.cartlist{list-style:none;padding:0;margin:2rem 0;border-top:1px solid rgba(43,42,38,.15)}.cartlist li{display:grid;grid-template-columns:72px 1fr auto;gap:1rem;align-items:center;padding:1rem 0;border-bottom:1px solid rgba(43,42,38,.1)}
.qty{display:flex;align-items:center;gap:.4rem}.qty button{width:2rem;height:2rem;border:1px solid rgba(43,42,38,.3);background:none;cursor:pointer;font:inherit}
.linkbtn{background:none;border:0;color:var(--terracotta);cursor:pointer;font:inherit;font-size:.85rem;padding:0;text-decoration:underline}
.total{display:flex;justify-content:space-between;font-size:1.2rem;margin:1.5rem 0}
.notice{border:1px solid var(--terracotta);background:#fbf3ea;padding:1rem 1.2rem;margin-top:1.5rem}
footer{background:var(--agave);color:var(--bone);margin-top:6rem}.fgrid{display:grid;gap:2.5rem;padding-block:4rem}@media(min-width:768px){.fgrid{grid-template-columns:2fr 1fr 1fr}}
footer ul{list-style:none;padding:0;margin:1rem 0 0;font-size:.9rem;line-height:2}footer a{text-decoration:none}footer a:hover{color:var(--sun)}
.fbottom{border-top:1px solid rgba(245,239,230,.15);display:flex;flex-wrap:wrap;justify-content:space-between;gap:.5rem;padding-block:1.4rem;font-size:.75rem;color:rgba(245,239,230,.55)}
.cartcount{font-family:"JetBrains Mono",monospace}
"""

def page(path, title, desc, body, image="/img/og.jpg", extra_head=""):
    url = BASE + path
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(title)}</title><meta name="description" content="{E(desc)}">
<meta name="robots" content="noindex,nofollow"><link rel="canonical" href="{url}">
<meta property="og:type" content="website"><meta property="og:site_name" content="Agave Apparel Co.">
<meta property="og:title" content="{E(title)}"><meta property="og:description" content="{E(desc)}">
<meta property="og:url" content="{url}"><meta property="og:image" content="{BASE}{image}">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{E(title)}">
<meta name="twitter:description" content="{E(desc)}"><meta name="twitter:image" content="{BASE}{image}">
<link rel="icon" href="/favicon.ico" sizes="any"><link rel="icon" type="image/png" href="/favicon-32.png"><link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,300..700&amp;family=Inter:wght@300;400;500;600&amp;family=JetBrains+Mono:wght@400&amp;display=swap" rel="stylesheet">
<link rel="stylesheet" href="/style.css">{extra_head}</head><body>
<div class="preview" role="note">Preview, not the live store</div>
<header class="site"><div class="strip">Made in Arizona · Shipped Everywhere</div>
<div class="wrap bar"><a class="brand" href="/"><img src="/img/logo-sm.png" width="64" height="48" alt="Agave Apparel Co. logo: the word Agave in a thin serif with a pale green agave behind it"><span class="eyebrow">Apparel Co.</span></a>
<nav aria-label="Main"><a href="/shop/">Shop</a><a href="/about/">About</a><a href="/contact/">Contact</a><a href="/cart/">Cart <span class="cartcount" data-cart-count>(0)</span></a></nav></div></header>
<main>{body}</main>
<footer><div class="wrap fgrid"><div><div class="display" style="font-size:1.9rem">Agave Apparel Co.</div><p style="color:rgba(245,239,230,.7);max-width:24rem;font-size:.9rem">Small-batch graphic tees designed in the Sonoran Desert. One-of-a-kind pieces for people who don't dress like everyone else.</p></div>
<div><div class="eyebrow" style="color:rgba(245,239,230,.5)">Shop</div><ul><li><a href="/shop/">All designs</a></li><li><a href="/about/">Our story</a></li><li><a href="/contact/">Contact</a></li></ul></div>
<div><div class="eyebrow" style="color:rgba(245,239,230,.5)">Orders</div><ul><li><a href="mailto:orders@agaveapparel.com">orders@agaveapparel.com</a></li><li style="color:rgba(245,239,230,.6)">Phoenix, Arizona</li></ul></div></div>
<div class="wrap fbottom"><div>© 2026 Agave Apparel Co. — Made in Arizona</div><div>Designed by Courtney Messamore</div></div></footer>
<script src="/cart.js" defer></script></body></html>"""

def card(p):
    return f"""<a class="card" href="/products/{p['slug']}/"><div class="tile"><img src="/img/designs/{p['slug']}-600.webp" width="600" height="600" loading="lazy" alt="{E(ALT[p['slug']])}"></div>
<div class="card-row"><div><h3>{E(p['name'])}</h3><p>{E(p['tagline'])}</p></div><div class="mono" style="font-size:.9rem">${p['price']}</div></div></a>"""

def write(rel, s):
    f = OUT / rel; f.parent.mkdir(parents=True, exist_ok=True); f.write_text(s)

def build():
    if OUT.exists(): shutil.rmtree(OUT)
    (OUT / "img/designs").mkdir(parents=True)
    # images
    for p in P:
        im = Image.open(ROOT.parent / "designs" / f"{p['slug']}.png").convert("RGB")
        im.save(OUT / f"img/designs/{p['slug']}-1200.webp", quality=86)
        im.resize((600, 600), Image.LANCZOS).save(OUT / f"img/designs/{p['slug']}-600.webp", quality=84)
        im.save(OUT / f"img/designs/{p['slug']}-1200.jpg", quality=86)  # for OG/JSON-LD (widest support)
    logo = Image.open(SNAP / "agaveapparel.com/designs/agave-apparel-logo-larger.png").convert("RGBA")
    l = logo.copy(); l.thumbnail((256, 192)); l.save(OUT / "img/logo-sm.png")
    # favicon: square crop centred on the logo, on its own background
    bg = Image.new("RGBA", (max(logo.size),) * 2, logo.getpixel((5, 5)))
    bg.paste(logo, ((bg.width - logo.width) // 2, (bg.height - logo.height) // 2), logo)
    bg.resize((180, 180), Image.LANCZOS).save(OUT / "apple-touch-icon.png")
    bg.resize((32, 32), Image.LANCZOS).save(OUT / "favicon-32.png")
    bg.save(OUT / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])
    og = Image.new("RGB", (1200, 630), (245, 239, 230)); lo = logo.copy(); lo.thumbnail((700, 520))
    og.paste(lo, ((1200 - lo.width) // 2, (630 - lo.height) // 2), lo); og.save(OUT / "img/og.jpg", quality=88)
    write("style.css", CSS)
    shutil.copy(ROOT / "src/cart.js", OUT / "cart.js")
    (ROOT / "functions/_lib/catalog.json").write_text(json.dumps({p["slug"]: {"name": p["name"], "price": p["price"]} for p in P}, indent=1))
    write("products.json", json.dumps({p["slug"]: {"name": p["name"], "price": p["price"]} for p in P}))
    feat = next(p for p in P if p["slug"] == "golden-hour")
    home = f"""<div class="wrap hero"><div><div class="eyebrow">Sonoran Desert · Est. 2025</div><h1 class="display" style="margin-top:1.2rem">Dressed different<br>on purpose.</h1>
<p class="lede">Small-batch graphic tees designed in the Sonoran Desert. One-of-a-kind pieces for people who’d rather wear a conversation than a logo.</p>
<div class="actions"><a class="btn btn-primary" href="/shop/">Shop the collection</a><a class="btn btn-outline" href="/about/">Our story</a></div></div>
<div><a class="card" href="/products/golden-hour/"><div class="tile"><img src="/img/designs/golden-hour-1200.webp" width="1200" height="1200" alt="{E(ALT['golden-hour'])}"></div></a>
<div class="card-row"><span class="display" style="font-size:1.15rem">Golden Hour</span><span class="mono" style="color:var(--dust);font-size:.85rem">Featured</span></div></div></div>
<div class="band">Designed in Arizona <span style="opacity:.4">·</span> Small batch <span style="opacity:.4">·</span> No duplicates of anyone <span style="opacity:.4">·</span> Ships worldwide</div>
<section class="wrap pad"><div class="sec-head"><div><div class="eyebrow">The collection</div><h2 class="display" style="margin-top:1rem">Pieces you won’t<br>see on everyone else.</h2></div><a class="btn btn-outline" href="/shop/">View all 22</a></div>
<div class="grid">{''.join(card(p) for p in P[:6])}</div></section>
<section class="sand"><div class="wrap pad split"><div class="tile"><img src="/img/designs/agave-desert-life-1200.webp" width="1200" height="1200" loading="lazy" alt="{E(ALT['agave-desert-life'])}"></div>
<div><div class="eyebrow">Our story</div><h2 class="display big" style="margin-top:1rem">Built by a desert kid who never<br>wanted to blend in.</h2>
<p class="lede">Courtney has always dressed like herself — not anyone else. Agave Apparel is her way of sharing that: wearable art pulled from Arizona sunsets, saguaro shadows, and the kind of days that make you glad you live where you do.</p>
<div class="actions"><a class="btn btn-outline" href="/about/">Read more</a></div></div></div></section>
<section class="wrap pad"><div class="eyebrow">How it works</div><h2 class="display big" style="margin-top:1rem">Pick a design, pick your size.</h2>
<div class="steps"><div><div class="mono" style="color:var(--dust)">01</div><h3>Browse</h3><p>Twenty-two designs and counting. Each one is its own thing — no two Agave closets look alike.</p></div>
<div><div class="mono" style="color:var(--dust)">02</div><h3>Order</h3><p>Choose your size, add it to your cart and check out securely with a card.</p></div>
<div><div class="mono" style="color:var(--dust)">03</div><h3>Wear it out</h3><p>Everything is printed small-batch. You’ll get something made for you, not mass-produced for the algorithm.</p></div></div></section>
<section class="inkbg"><div class="wrap pad" style="text-align:center"><h2 class="display" style="font-size:clamp(2.4rem,6vw,4.5rem)">Your closet called.<br>It wants something different.</h2>
<div class="actions" style="justify-content:center"><a class="btn" style="background:var(--bone);color:var(--ink);border-color:var(--bone)" href="/shop/">Shop all designs</a></div></div></section>"""
    write("index.html", page("/", "Agave Apparel Co. — Small-batch desert graphic tees", "Small-batch graphic tees designed in the Sonoran Desert. One-of-a-kind pieces for people who’d rather wear a conversation than a logo.", home))
    shop = f"""<section class="wrap pad"><div class="eyebrow">The collection</div><h1 class="display big" style="margin:1rem 0 3rem">All 22 designs.</h1><div class="grid">{''.join(card(p) for p in P)}</div></section>"""
    write("shop/index.html", page("/shop/", "Shop — Agave Apparel Co.", "All 22 Agave Apparel designs: small-batch desert graphic tees, $28–$38.", shop))
    about = """<section class="wrap pad prose"><div class="eyebrow">About</div><h1 class="display big" style="margin:1rem 0 2rem">A small brand made in the sun.</h1>
<p>Agave Apparel started the way most good things do — because the founder couldn’t find what she wanted, so she made it.</p>
<p>Courtney Messamore has always dressed a little differently. Not to stand out for the sake of it — she just never liked the idea of opening her closet and seeing the same thing everyone else was wearing. She wanted her clothes to actually say something about her: about where she’s from, what she loves, and the way she moves through the world.</p>
<p>What she loves, mostly, is the Arizona desert. Sunsets that stop you in the parking lot. The quiet of the saguaros at dusk. The way 110-degree heat turns into a cold river float and then into golden hour. The agave plant that takes eight years to grow and then gives you a lifetime’s worth of stories. The smell of creosote after a rare rain.</p>
<p>Every design in this small collection comes from that. Some are loud. Some are quiet. All of them are hers — drawn, colored, and chosen in the same town she’s always called home.</p>
<p>Agave Apparel is deliberately small. Everything is printed in limited runs, on soft cotton, for people who want to wear something that nobody else has twenty of. If that sounds like your closet too — welcome.</p>
<div class="actions"><a class="btn btn-primary" href="/shop/">Shop the collection</a></div>
<div class="steps"><div><h3>Designed in Arizona</h3><p>Every piece starts as a sketch in the desert she calls home.</p></div><div><h3>Small batch, always</h3><p>No endless inventory. No overproduction. If you like it, grab it.</p></div><div><h3>Printed on cotton you’ll actually wear</h3><p>Soft, broken-in, unisex relaxed fit. Meant to get better with every wash.</p></div></div></section>"""
    write("about/index.html", page("/about/", "About — Agave Apparel Co.", "Agave Apparel is Courtney Messamore’s small-batch tee brand, designed in Arizona.", about))
    contact = """<section class="wrap pad prose"><div class="eyebrow">Contact</div><h1 class="display big" style="margin:1rem 0 2rem">Say hi.</h1>
<p>Orders, custom design requests, wholesale inquiries, or a nice note about a sunset — it all goes to the same inbox and Courtney reads every one.</p>
<p>We’re a tiny operation, so response time is usually a day or two.</p>
<dl class="specs"><div><dt>Orders &amp; general</dt><dd><a href="mailto:orders@agaveapparel.com">orders@agaveapparel.com</a></dd></div><div><dt>Based in</dt><dd>Phoenix, Arizona</dd></div></dl></section>"""
    write("contact/index.html", page("/contact/", "Contact — Agave Apparel Co.", "Get in touch with Agave Apparel Co. in Phoenix, Arizona.", contact))
    for p in P:
        others = [o for o in P if o["slug"] != p["slug"]][:4]
        ld = {"@context": "https://schema.org", "@type": "Product", "name": p["name"], "description": p["meta_description"],
              "image": f"{BASE}/img/designs/{p['slug']}-1200.jpg", "sku": p["slug"], "brand": {"@type": "Brand", "name": "Agave Apparel Co."},
              "offers": {"@type": "Offer", "price": f"{p['price']}.00", "priceCurrency": "USD", "availability": "https://schema.org/InStock", "url": f"{BASE}/products/{p['slug']}/"}}
        radios = "".join(f'<label><input type="radio" name="size" value="{s}" required><span>{s}</span></label>' for s in SIZES)
        body = f"""<div class="wrap" style="padding-top:2rem"><a href="/shop/" style="font-size:.9rem">← Back to the collection</a></div>
<div class="wrap product"><div class="tile"><img src="/img/designs/{p['slug']}-1200.webp" width="1200" height="1200" alt="{E(ALT[p['slug']])}"></div>
<div><div class="eyebrow">Wearable art</div><h1 class="display" style="font-size:clamp(2.6rem,5vw,4rem);margin-top:1rem">{E(p['name'])}</h1>
<p style="font-family:Fraunces,serif;font-style:italic;font-size:1.25rem;margin:.6rem 0 0">{E(p['tagline'])}</p><div class="price mono">${p['price']}</div>
<p class="prose">{E(p['meta_description'])}</p>
<form data-add-to-cart data-slug="{p['slug']}"><fieldset><legend class="eyebrow">Size · Bella+Canvas 3001</legend><div class="sizes">{radios}</div></fieldset>
<div class="actions"><button class="btn btn-primary" type="submit">Add to cart</button><a class="btn btn-outline" href="/cart/">View cart</a></div><div class="msg" role="status" aria-live="polite"></div></form>
<dl class="specs"><div><dt>Fabric</dt><dd>100% cotton, soft-washed</dd></div><div><dt>Fit</dt><dd>Unisex, relaxed</dd></div><div><dt>Printed</dt><dd>Small-batch, Arizona</dd></div><div><dt>Ships</dt><dd>Usually within 7–10 days</dd></div></dl></div></div>
<section class="wrap pad"><div class="sec-head"><h2 class="display" style="font-size:2.2rem">You might also wear</h2><a class="btn btn-outline" href="/shop/">View all</a></div><div class="grid">{''.join(card(o) for o in others)}</div></section>"""
        write(f"products/{p['slug']}/index.html", page(f"/products/{p['slug']}/", f"{p['name']} — Agave Apparel Co.", p["meta_description"], body,
              image=f"/img/designs/{p['slug']}-1200.jpg", extra_head=f'<meta property="product:price:amount" content="{p["price"]}.00"><meta property="product:price:currency" content="USD"><script type="application/ld+json">{json.dumps(ld)}</script>'))
    cart = """<section class="wrap pad" style="max-width:52rem"><div class="eyebrow">Your cart</div><h1 class="display big" style="margin-top:1rem">Cart</h1>
<div data-cart-root><p>Your cart is empty. <a href="/shop/">Browse the collection</a>.</p></div>
<div class="total"><span>Subtotal</span><span class="mono" data-cart-total>$0</span></div><p class="note">Shipping and tax are calculated at checkout.</p>
<button class="btn btn-primary" type="button" data-checkout disabled>Checkout</button><div data-checkout-msg role="status" aria-live="polite"></div></section>"""
    write("cart/index.html", page("/cart/", "Cart — Agave Apparel Co.", "Your Agave Apparel cart.", cart))
    write("checkout/success/index.html", page("/checkout/success/", "Thank you — Agave Apparel Co.", "Order received.", '<section class="wrap pad prose"><h1 class="display big">Thank you.</h1><p>Your order is in. A receipt is on its way to your email.</p><p><a href="/shop/">Back to the collection</a></p></section><script>localStorage.removeItem("agave-cart")</script>'))
    write("404.html", page("/404", "Not found — Agave Apparel Co.", "Page not found.", '<section class="wrap pad prose"><h1 class="display big">Lost in the desert.</h1><p>That page doesn’t exist. <a href="/shop/">Back to the collection</a>.</p></section>'))
    urls = ["/", "/shop/", "/about/", "/contact/"] + [f"/products/{p['slug']}/" for p in P]
    write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(f"<url><loc>{BASE}{u}</loc></url>\n" for u in urls) + "</urlset>\n")
    write("robots.txt", f"# Preview copy: keep out of search engines.\nUser-agent: *\nDisallow: /\n\nSitemap: {BASE}/sitemap.xml\n")
    write("_headers", "/*\n  X-Robots-Tag: noindex, nofollow\n  X-Content-Type-Options: nosniff\n  Referrer-Policy: strict-origin-when-cross-origin\n")

if __name__ == "__main__":
    build(); print("built", sum(1 for _ in OUT.rglob("*") if _.is_file()), "files")
