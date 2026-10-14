// localStorage cart: [{slug, size, qty}]. Prices always come from /products.json (and server-side in /api/checkout).
(function () {
  const KEY = "agave-cart";
  const read = () => { try { return JSON.parse(localStorage.getItem(KEY)) || []; } catch { return []; } };
  const save = (c) => { localStorage.setItem(KEY, JSON.stringify(c)); renderCount(); };
  const renderCount = () => {
    const n = read().reduce((s, i) => s + i.qty, 0);
    document.querySelectorAll("[data-cart-count]").forEach((el) => (el.textContent = `(${n})`));
  };
  renderCount();

  const form = document.querySelector("[data-add-to-cart]");
  if (form) form.addEventListener("submit", (e) => {
    e.preventDefault();
    const size = new FormData(form).get("size");
    const msg = form.querySelector(".msg");
    if (!size) { msg.textContent = "Pick a size first."; return; }
    const cart = read(), slug = form.dataset.slug;
    const hit = cart.find((i) => i.slug === slug && i.size === size);
    hit ? hit.qty++ : cart.push({ slug, size, qty: 1 });
    save(cart);
    msg.innerHTML = `Added size ${size} to your cart. <a href="/cart/">View cart</a>`;
  });

  const root = document.querySelector("[data-cart-root]");
  if (!root) return;
  const btn = document.querySelector("[data-checkout]"), out = document.querySelector("[data-checkout-msg]");
  fetch("/products.json").then((r) => r.json()).then((P) => {
    const render = () => {
      const cart = read().filter((i) => P[i.slug]);
      const total = cart.reduce((s, i) => s + P[i.slug].price * i.qty, 0);
      document.querySelector("[data-cart-total]").textContent = `$${total}`;
      btn.disabled = cart.length === 0;
      if (!cart.length) { root.innerHTML = '<p>Your cart is empty. <a href="/shop/">Browse the collection</a>.</p>'; return; }
      root.innerHTML = '<ul class="cartlist">' + cart.map((i, n) => `<li>
        <img src="/img/designs/${i.slug}-600.webp" width="72" height="72" alt="${P[i.slug].name} t-shirt">
        <div><a href="/products/${i.slug}/">${P[i.slug].name}</a><div class="mono" style="font-size:.85rem;color:var(--dust)">Size ${i.size} · $${P[i.slug].price}</div>
        <button class="linkbtn" data-rm="${n}" type="button">Remove</button></div>
        <div class="qty"><button type="button" data-dec="${n}" aria-label="Decrease quantity">−</button><span class="mono">${i.qty}</span><button type="button" data-inc="${n}" aria-label="Increase quantity">+</button></div></li>`).join("") + "</ul>";
    };
    root.addEventListener("click", (e) => {
      const c = read().filter((i) => P[i.slug]), d = e.target.dataset;
      if (d.inc) c[d.inc].qty++;
      else if (d.dec) { c[d.dec].qty--; if (c[d.dec].qty < 1) c.splice(d.dec, 1); }
      else if (d.rm) c.splice(d.rm, 1);
      else return;
      save(c); render();
    });
    btn.addEventListener("click", async () => {
      btn.disabled = true; out.textContent = "";
      try {
        const r = await fetch("/api/checkout", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ items: read() }) });
        const j = await r.json();
        if (j.url) { location.href = j.url; return; }
        out.innerHTML = `<div class="notice">${j.message || "Checkout is unavailable right now."}</div>`;
      } catch { out.innerHTML = '<div class="notice">Could not reach checkout. Please try again.</div>'; }
      btn.disabled = false;
    });
    render();
  });
})();
