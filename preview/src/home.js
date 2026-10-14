// Home only: hero video start and dust-scratch reveal (T7).
(function () {
  const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;

  // Hero video: start only when motion is welcome. Poster stays for reduced motion / Save-Data / no JS.
  const v = document.querySelector("[data-hero-video]");
  if (v && !reduce && !(navigator.connection && navigator.connection.saveData)) {
    v.preload = "auto";
    v.play().catch(() => {});
  }

  // T7: scrape the sun-bleached dust off the featured print. The real <img> underneath carries the alt text.
  const box = document.querySelector("[data-scratch]");
  if (!box) return;
  const img = box.querySelector("img"), cv = box.querySelector("canvas"), ctx = cv.getContext("2d");
  let dust, w, h, dpr, last = null, raf = 0;
  const makeDust = () => {
    const c = document.createElement("canvas"); c.width = w; c.height = h;
    const g = c.getContext("2d");
    g.filter = "grayscale(.85) sepia(.35) brightness(1.18) contrast(.62) blur(1px)";
    g.drawImage(img, 0, 0, w, h);
    g.filter = "none";
    g.fillStyle = "rgba(226,204,170,.34)"; g.fillRect(0, 0, w, h);
    for (let i = 0; i < (w * h) / 90; i++) {           // dust specks
      g.fillStyle = `rgba(${150 + Math.random() * 60},${120 + Math.random() * 50},${90 + Math.random() * 40},${Math.random() * 0.35})`;
      g.fillRect(Math.random() * w, Math.random() * h, Math.random() * 2.2 * dpr, Math.random() * 2.2 * dpr);
    }
    return c;
  };
  const size = () => {
    dpr = Math.min(devicePixelRatio || 1, 2);
    const r = box.getBoundingClientRect(); w = cv.width = Math.round(r.width * dpr); h = cv.height = Math.round(r.height * dpr);
    dust = makeDust(); ctx.globalCompositeOperation = "source-over"; ctx.drawImage(dust, 0, 0);
    // one pre-made swipe so it's obvious there is colour underneath
    last = null; for (let t = 0; t <= 1; t += 0.04) scrape(w * (0.18 + 0.5 * t), h * (0.62 - 0.22 * t + 0.05 * Math.sin(t * 6)));
    last = null;
  };
  const scrape = (x, y) => {
    ctx.globalCompositeOperation = "destination-out";
    const R = 34 * dpr;
    const from = last || { x, y }, steps = Math.max(1, Math.hypot(x - from.x, y - from.y) / (R / 4));
    for (let s = 0; s <= steps; s++) {
      const px = from.x + ((x - from.x) * s) / steps, py = from.y + ((y - from.y) * s) / steps;
      for (let k = 0; k < 6; k++) {                    // noisy brush: a cluster of soft dabs
        const a = Math.random() * Math.PI * 2, d = Math.random() * R * 0.7, rr = R * (0.25 + Math.random() * 0.45);
        const gx = px + Math.cos(a) * d, gy = py + Math.sin(a) * d;
        const grd = ctx.createRadialGradient(gx, gy, 0, gx, gy, rr);
        grd.addColorStop(0, "rgba(0,0,0,.9)"); grd.addColorStop(1, "rgba(0,0,0,0)");
        ctx.fillStyle = grd; ctx.beginPath(); ctx.arc(gx, gy, rr, 0, Math.PI * 2); ctx.fill();
      }
    }
    last = { x, y };
    if (!raf) raf = requestAnimationFrame(settle);
  };
  let idle = 0;
  function settle() {                                   // the dust slowly drifts back
    idle++;
    if (idle > 90) { ctx.globalCompositeOperation = "source-over"; ctx.globalAlpha = 0.012; ctx.drawImage(dust, 0, 0); ctx.globalAlpha = 1; }
    raf = idle < 900 ? requestAnimationFrame(settle) : 0;
  }
  const pos = (e) => { const r = cv.getBoundingClientRect(); return [(e.clientX - r.left) * dpr, (e.clientY - r.top) * dpr]; };
  cv.addEventListener("pointermove", (e) => {
    if (e.pointerType !== "mouse" && !e.pressure) return;
    idle = 0; scrape(...pos(e));
  });
  cv.addEventListener("pointerleave", () => (last = null));
  cv.addEventListener("pointerup", () => (last = null));
  cv.addEventListener("pointerdown", (e) => { last = null; idle = 0; scrape(...pos(e)); });
  const start = () => { size(); let t; addEventListener("resize", () => { clearTimeout(t); t = setTimeout(size, 200); }); };
  img.complete ? start() : img.addEventListener("load", start, { once: true });
})();
