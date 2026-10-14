import sys
from playwright.sync_api import sync_playwright
U,D=sys.argv[1],sys.argv[2]; errs=[]; bad=[]
with sync_playwright() as pw:
    b=pw.chromium.launch()
    for w,h,dsf in [(1280,860,1),(390,844,2)]:
        c=b.new_context(viewport={"width":w,"height":h},device_scale_factor=dsf); p=c.new_page()
        p.on("console",lambda m:m.type=="error" and errs.append(m.text)); p.on("response",lambda r:r.status>=400 and bad.append((r.status,r.url)))
        p.goto(U+"/shop/",wait_until="networkidle"); p.evaluate("window.scrollTo(0,document.querySelector('.card').getBoundingClientRect().top+scrollY-90)"); p.wait_for_timeout(900)
        p.screenshot(path=f"{D}/shop-{w}.png", full_page=True)
        print(w,"cards",p.locator(".card").count(), "nums", p.eval_on_selector_all(".card .num","e=>e.slice(0,3).map(x=>x.textContent)"))
        cls=p.evaluate("new Promise(r=>{let s=0;new PerformanceObserver(l=>l.getEntries().forEach(e=>{if(!e.hadRecentInput)s+=e.value})).observe({type:'layout-shift',buffered:true});setTimeout(()=>r(s),800)})"); print(w,"shop CLS",round(cls,4))
        p.goto(U+"/products/patterened-agave/",wait_until="networkidle"); p.screenshot(path=f"{D}/product-{w}.png")
        p.goto(U+"/",wait_until="networkidle"); p.screenshot(path=f"{D}/home-{w}.png", full_page=True)
        # links
        hrefs=set(p.eval_on_selector_all("a[href^='/']","e=>e.map(a=>a.getAttribute('href'))"))
        for hr in hrefs:
            r=p.request.get(U+hr); 
            if r.status>=400: bad.append((r.status,hr))
        p.goto(U+"/products/soul-to-sole/",wait_until="networkidle"); p.check("input[value=L]"); p.click("button[type=submit]"); p.wait_for_selector(".msg a")
        p.goto(U+"/cart/",wait_until="networkidle"); print(w,"cart lines",p.locator(".line, .cart-line, li").count())
        c.close()
    b.close()
print("errors",errs); print("bad",bad)
