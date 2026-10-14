// Design viewer: hover-magnify on product shots, and a modal that grows each image out of its tile (FLIP).
// Esc / backdrop / close button close it; arrows and horizontal swipe move between designs; <dialog>.showModal()
// makes the page behind inert, and focus returns to the tile that opened it.
(function () {
  const triggers = () => [...document.querySelectorAll("[data-lb]")];
  if (!triggers().length) return;
  const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const EASE = "cubic-bezier(.2,.75,.15,1)";

  // product page: magnify follows the cursor (CSS does the scale; we only move the origin)
  document.querySelectorAll("[data-magnify]").forEach((el) => {
    const img = el.querySelector("img");
    el.addEventListener("pointermove", (e) => {
      if (e.pointerType !== "mouse") return;
      const r = el.getBoundingClientRect();
      img.style.setProperty("--zx", ((e.clientX - r.left) / r.width) * 100 + "%");
      img.style.setProperty("--zy", ((e.clientY - r.top) / r.height) * 100 + "%");
    });
  });

  let designs = null;
  let pending = null;
  const load = () => pending || (pending = fetch("/designs.json").then((r) => r.json()).then((d) => (designs = d)));
  const esc = (s) => s.replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);
  const icon = (d) => `<svg viewBox="0 0 24 24" aria-hidden="true"><path d="${d}"/></svg>`;

  const dlg = document.createElement("dialog");
  dlg.className = "lb";
  dlg.setAttribute("aria-label", "Design viewer");
  dlg.innerHTML = `<div class="lb-bg" data-close></div>
    <p class="lb-count" aria-live="polite"></p>
    <button class="lb-btn lb-close" type="button" aria-label="Close" data-close>${icon("M5 5l14 14M19 5L5 19")}</button>
    <div class="lb-stage"><div class="lb-frame"><img alt="Selected design" width="948" height="948"></div>
      <div class="lb-info"><span class="num" aria-hidden="true"></span><h2 class="ed"></h2><p class="tagline"></p>
        <span class="price"></span><a class="btn btn-fill" href="#">Choose a size</a>
        <div class="lb-nav"><button class="lb-btn" type="button" data-step="-1" aria-label="Previous design">${icon("M15 5l-7 7 7 7")}</button>
        <button class="lb-btn" type="button" data-step="1" aria-label="Next design">${icon("M9 5l7 7-7 7")}</button></div></div></div>`;
  document.body.appendChild(dlg);
  const frame = dlg.querySelector(".lb-frame"), big = frame.querySelector("img"), bg = dlg.querySelector(".lb-bg");
  const info = dlg.querySelector(".lb-info");
  let idx = 0, opener = null, busy = false;

  const src = (slug) => `/img/designs/${slug}-960.webp`;
  const render = (d, i) => {
    big.src = src(d.slug); big.alt = d.alt;
    info.querySelector(".num").textContent = `${String(i + 1).padStart(2, "0")}/${designs.length}`;
    const [first, ...rest] = d.name.split(" ");
    info.querySelector("h2").innerHTML = `<em>${esc(first)}</em>${rest.length ? ` <span class="caps">${esc(rest.join(" "))}</span>` : ""}`;
    info.querySelector(".tagline").textContent = d.tagline;
    info.querySelector(".price").textContent = `$${d.price}`;
    const a = info.querySelector("a"); a.href = `/products/${d.slug}/`; a.textContent = `Choose a size for ${d.name}`;
    dlg.querySelector(".lb-count").textContent = `Design ${i + 1} of ${designs.length}`;
  };

  // FLIP: a fixed "ghost" image sits in the destination box and animates in from the source box.
  const fly = (fromRect, toRect, url, dur) => {
    const g = new Image(); g.src = url; g.className = "lb-ghost"; g.alt = "";
    Object.assign(g.style, { left: toRect.left + "px", top: toRect.top + "px", width: toRect.width + "px", height: toRect.height + "px" });
    dlg.appendChild(g);   // must live inside the <dialog>: the top layer paints above any z-index
    const dx = fromRect.left - toRect.left, dy = fromRect.top - toRect.top, s = fromRect.width / toRect.width;
    const anim = g.animate([{ transform: `translate(${dx}px,${dy}px) scale(${s})`, transformOrigin: "0 0" }, { transform: "none", transformOrigin: "0 0" }],
      { duration: dur, easing: EASE, fill: "both" });
    return anim.finished.then(() => g);
  };
  const tileFor = (slug) => document.querySelector(`[data-lb="${slug}"]`);
  const visible = (el) => { if (!el) return false; const r = el.getBoundingClientRect(); return r.bottom > 0 && r.top < innerHeight && r.width > 0; };

  async function open(slug, trigger) {
    if (busy) return; busy = true;
    await load();
    idx = Math.max(0, designs.findIndex((d) => d.slug === slug));
    opener = trigger; render(designs[idx], idx);
    document.documentElement.classList.add("lb-open");
    dlg.showModal();
    const fromImg = trigger.querySelector("img");
    if (reduce || !fromImg) {
      dlg.animate([{ opacity: 0 }, { opacity: 1 }], { duration: 200, easing: "ease-out" });
    } else {
      const to = frame.getBoundingClientRect();
      big.style.visibility = "hidden"; info.style.opacity = 0;
      bg.animate([{ opacity: 0 }, { opacity: 1 }], { duration: 420, easing: "ease-out" });
      const g = await fly(fromImg.getBoundingClientRect(), to, fromImg.currentSrc || fromImg.src, 560);
      big.style.visibility = ""; g.remove();
      info.animate([{ opacity: 0, transform: "translateY(14px)" }, { opacity: 1, transform: "none" }], { duration: 380, easing: EASE, fill: "forwards" });
      info.style.opacity = "";
    }
    dlg.querySelector(".lb-close").focus();
    busy = false;
  }

  let opening = null;
  async function close() {
    if (opening) await opening;          // a close during the open animation waits for it, never gets dropped
    if (busy || !dlg.open) return; busy = true;
    const target = tileFor(designs[idx].slug);
    const back = target && visible(target) ? target : null;
    if (reduce || !back) {
      await dlg.animate([{ opacity: 1 }, { opacity: 0 }], { duration: 180, easing: "ease-in" }).finished;
    } else {
      const from = frame.getBoundingClientRect(), to = back.querySelector("img").getBoundingClientRect();
      big.style.visibility = "hidden"; info.style.opacity = 0;
      bg.animate([{ opacity: 1 }, { opacity: 0 }], { duration: 380, easing: "ease-in", fill: "forwards" });
      const g = await fly(from, to, big.src, 420).catch(() => null);
      if (g) g.remove();
    }
    dlg.close();
    big.style.visibility = ""; info.style.opacity = "";
    dlg.getAnimations({ subtree: true }).forEach((a) => a.cancel());
    document.documentElement.classList.remove("lb-open");
    (back || opener || document.body).focus({ preventScroll: true });
    busy = false;
  }

  function step(n) {
    if (busy || !designs) return;
    idx = (idx + n + designs.length) % designs.length;
    const d = designs[idx];
    if (reduce) { render(d, idx); return; }
    const out = [{ opacity: 1, transform: "none" }, { opacity: 0, transform: `translateX(${-n * 40}px)` }];
    Promise.all([big.animate(out, { duration: 160, easing: "ease-in" }).finished, info.animate(out, { duration: 160, easing: "ease-in" }).finished]).then(() => {
      render(d, idx);
      const inn = [{ opacity: 0, transform: `translateX(${n * 40}px)` }, { opacity: 1, transform: "none" }];
      const go = () => { big.animate(inn, { duration: 340, easing: EASE }); info.animate(inn, { duration: 340, easing: EASE }); };
      big.decode ? big.decode().then(go, go) : go();
    });
  }

  document.addEventListener("click", (e) => {
    const t = e.target.closest("[data-lb]");
    if (t) { e.preventDefault(); opening = open(t.dataset.lb, t).finally(() => (opening = null)); }
  });
  dlg.addEventListener("click", (e) => {
    if (e.target.closest("[data-close]")) close();
    const s = e.target.closest("[data-step]"); if (s) step(+s.dataset.step);
  });
  dlg.addEventListener("cancel", (e) => { e.preventDefault(); close(); });
  dlg.addEventListener("keydown", (e) => {
    if (e.key === "ArrowRight") { e.preventDefault(); step(1); }
    else if (e.key === "ArrowLeft") { e.preventDefault(); step(-1); }
    else if (e.key === "Tab") {           // keep focus cycling inside the viewer (browser chrome excluded)
      const f = [...dlg.querySelectorAll("button,a[href]")];
      const i = f.indexOf(document.activeElement);
      if (e.shiftKey && i <= 0) { e.preventDefault(); f.at(-1).focus(); }
      else if (!e.shiftKey && i === f.length - 1) { e.preventDefault(); f[0].focus(); }
    }
  });
  let sx = null, sy = 0;
  frame.addEventListener("pointerdown", (e) => { sx = e.clientX; sy = e.clientY; });
  frame.addEventListener("pointerup", (e) => {
    if (sx === null) return;
    const dx = e.clientX - sx, dy = e.clientY - sy; sx = null;
    if (Math.abs(dx) > 50 && Math.abs(dx) > Math.abs(dy) * 1.4) step(dx < 0 ? 1 : -1);
  });
  frame.addEventListener("pointercancel", () => (sx = null));
})();
