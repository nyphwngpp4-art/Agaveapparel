// POST /api/checkout  { items: [{slug, size, qty}] }
// STRIPE_SECRET_KEY unset -> 200 {live:false} placeholder (200 so browsers log no error). Set (use sk_test_... in preview) -> creates a Stripe Checkout Session.
// Keys live only in Cloudflare Pages env vars, never in this repo.
import { CATALOG, SIZES } from "../_lib/catalog.js";

const json = (body, status = 200) => new Response(JSON.stringify(body), { status, headers: { "content-type": "application/json" } });

export async function onRequestPost({ request, env }) {
  let items;
  try { ({ items } = await request.json()); } catch { return json({ error: "bad_request", message: "Invalid JSON." }, 400); }
  items = (Array.isArray(items) ? items : []).filter((i) => CATALOG[i.slug] && SIZES.includes(i.size) && Number.isInteger(i.qty) && i.qty > 0 && i.qty <= 20);
  if (!items.length) return json({ error: "empty_cart", message: "Your cart is empty." }, 400);

  if (!env.STRIPE_SECRET_KEY) {
    return json({ live: false, error: "checkout_not_live", message: "Checkout is not live yet. This is a preview of the new store, so no order was placed and no card was charged." }, 200);
  }

  const origin = new URL(request.url).origin;
  const f = new URLSearchParams({ mode: "payment", success_url: `${origin}/checkout/success/?session_id={CHECKOUT_SESSION_ID}`, cancel_url: `${origin}/cart/` });
  f.append("shipping_address_collection[allowed_countries][0]", "US");
  items.forEach((i, n) => {
    const p = CATALOG[i.slug];
    f.append(`line_items[${n}][quantity]`, String(i.qty));
    f.append(`line_items[${n}][price_data][currency]`, "usd");
    f.append(`line_items[${n}][price_data][unit_amount]`, String(p.price * 100));
    f.append(`line_items[${n}][price_data][product_data][name]`, `${p.name} (${i.size})`);
    // Read back by /api/stripe-webhook to build the Printful order.
    f.append(`line_items[${n}][price_data][product_data][metadata][slug]`, i.slug);
    f.append(`line_items[${n}][price_data][product_data][metadata][size]`, i.size);
  });
  const r = await fetch("https://api.stripe.com/v1/checkout/sessions", {
    method: "POST", body: f,
    headers: { authorization: `Bearer ${env.STRIPE_SECRET_KEY}`, "content-type": "application/x-www-form-urlencoded" },
  });
  const s = await r.json();
  if (!r.ok) return json({ error: "stripe_error", message: "Checkout could not be started. Please try again." }, 502);
  return json({ live: true, url: s.url });
}

export const onRequest = () => json({ error: "method_not_allowed" }, 405);
