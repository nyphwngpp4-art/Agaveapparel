from playwright.sync_api import sync_playwright
U="https://agave-apparel-preview.pages.dev"; D="/workspace/agave-apparel/qa/v2"
SCROLL="async()=>{for(let y=0;y<document.body.scrollHeight;y+=400){scrollTo(0,y);await new Promise(r=>setTimeout(r,80))}scrollTo(0,0);await new Promise(r=>setTimeout(r,400))}"
errs=[]
with sync_playwright() as pw:
    b=pw.chromium.launch()
    for w,h,dpr in [(390,844,2),(1280,860,1)]:
        pg=b.new_page(viewport={"width":w,"height":h},device_scale_factor=dpr)
        pg.on("console",lambda m:m.type=="error" and errs.append(m.text))
        for path,name in [("/","home"),("/products/golden-hour/","product")]:
            pg.goto(U+path,wait_until="networkidle"); pg.evaluate(SCROLL); pg.screenshot(path=f"{D}/{name}-{w}.png",full_page=True)
        pg.close()
    pg=b.new_page(viewport={"width":1440,"height":900},device_scale_factor=2); pg.goto(U+"/",wait_until="networkidle"); pg.wait_for_timeout(800)
    pg.screenshot(path=f"{D}/hero-closeup.png",clip={"x":300,"y":100,"width":900,"height":560})
    pg.screenshot(path=f"{D}/hero-1440.png")
    # scratch interaction proof
    pg.evaluate("document.querySelector('[data-scratch]').scrollIntoView({block:'center'})"); pg.wait_for_timeout(400)
    bb=pg.locator("[data-scratch] canvas").bounding_box()
    pg.mouse.move(bb["x"]+40,bb["y"]+bb["height"]*.3)
    for i in range(40): pg.mouse.move(bb["x"]+40+i*(bb["width"]-80)/40,bb["y"]+bb["height"]*(.3+.4*(i%8)/8),steps=2)
    pg.screenshot(path=f"{D}/scratch-1440.png")
    # reduced motion: parallax plates must not move
    ctx=b.new_context(reduced_motion="reduce",viewport={"width":1280,"height":860}); p2=ctx.new_page(); p2.goto(U+"/",wait_until="networkidle"); p2.mouse.wheel(0,400); p2.wait_for_timeout(500)
    print("reduced-motion transform on .p-near:", p2.evaluate("getComputedStyle(document.querySelector('.p-near')).transform"))
    b.close()
print("errors:",errs)
