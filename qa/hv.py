import sys
from playwright.sync_api import sync_playwright
U=sys.argv[1]; D=sys.argv[2]; errs=[]
CLS="()=>new Promise(r=>{let c=0;new PerformanceObserver(l=>{for(const e of l.getEntries())if(!e.hadRecentInput)c+=e.value}).observe({type:'layout-shift',buffered:true});setTimeout(()=>r(+c.toFixed(4)),2500)})"
with sync_playwright() as pw:
    b=pw.chromium.launch(args=["--autoplay-policy=no-user-gesture-required"])
    for w,h,dpr,name in [(1440,900,1,"1440"),(1280,860,1,"1280"),(390,844,2,"390")]:
        pg=b.new_page(viewport={"width":w,"height":h},device_scale_factor=dpr)
        pg.on("console",lambda m:m.type=="error" and errs.append(m.text)); pg.on("pageerror",lambda e:errs.append(str(e)))
        pg.goto(U+"/",wait_until="load"); cls=pg.evaluate(CLS)
        st=pg.evaluate("(v=>({paused:v.paused,t:+v.currentTime.toFixed(2),src:v.currentSrc.split('/').pop(),ready:v.readyState}))(document.querySelector('[data-hero-video]'))")
        print(name,"cls",cls,st); pg.screenshot(path=f"{D}/hero-video-{name}.png"); pg.close()
    for w,h in [(1440,900),(390,844)]:
        ctx=b.new_context(reduced_motion="reduce",viewport={"width":w,"height":h}); p=ctx.new_page(); p.goto(U+"/",wait_until="load"); p.wait_for_timeout(1500)
        print("reduced",w,p.evaluate("(v=>({paused:v.paused,t:v.currentTime,ready:v.readyState,poster:v.poster.split('/').pop()}))(document.querySelector('[data-hero-video]'))"))
        p.screenshot(path=f"{D}/hero-video-{w}-reduced.png"); ctx.close()
    b.close()
print("errors",errs)
