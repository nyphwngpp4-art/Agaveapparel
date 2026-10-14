import sys
from playwright.sync_api import sync_playwright
U = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8765"; D = sys.argv[2] if len(sys.argv) > 2 else "/tmp/it"
errs = []
with sync_playwright() as pw:
    b = pw.chromium.launch()
    for w, h in [(390, 844), (1280, 860)]:
        pg = b.new_page(viewport={"width": w, "height": h}, device_scale_factor=2 if w == 390 else 1)
        pg.on("console", lambda m: m.type == "error" and errs.append(m.text)); pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.goto(U + "/", wait_until="networkidle"); pg.wait_for_timeout(600)
        pg.screenshot(path=f"{D}/home-{w}-fold.png")
        pg.evaluate("async()=>{for(let y=0;y<document.body.scrollHeight;y+=400){scrollTo(0,y);await new Promise(r=>setTimeout(r,60))}scrollTo(0,0)}"); pg.wait_for_timeout(500); pg.screenshot(path=f"{D}/home-{w}.png", full_page=True)
        pg.goto(U + "/products/golden-hour/", wait_until="networkidle"); pg.evaluate("async()=>{for(let y=0;y<document.body.scrollHeight;y+=400){scrollTo(0,y);await new Promise(r=>setTimeout(r,60))}scrollTo(0,0)}"); pg.wait_for_timeout(400); pg.screenshot(path=f"{D}/product-{w}.png", full_page=True)
        pg.goto(U + "/products/red-rays-for-days/", wait_until="networkidle"); pg.screenshot(path=f"{D}/product2-{w}-fold.png")
        pg.close()
    b.close()
print("errors:", errs)
