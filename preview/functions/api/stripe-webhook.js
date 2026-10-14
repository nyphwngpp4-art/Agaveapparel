// POST /api/stripe-webhook  (Stripe -> us, event checkout.session.completed)
// 1. Verifies the Stripe-Signature header when STRIPE_WEBHOOK_SECRET is set (rejects if invalid).
//    If the secret is unset, it accepts but only logs (preview/dev only).
// 2. Maps the paid line items to a Printful order payload, as a DRAFT (confirm=false).
// 3. Sends it to Printful ONLY if PRINTFUL_API_KEY is set AND PRINTFUL_LIVE === "1". Otherwise it just returns the payload.
import { CATALOG } from "../_lib/catalog.js";

// Printful catalog variant ids for Bella+Canvas 3001 by size. TODO: fill from Printful's catalog API
// (GET /products/71 lists 3001 variants per color). Colour choice per design is also TODO.
export const VARIANTS = { S: "TODO_3001_S", M: "TODO_3001_M", L: "TODO_3001_L", XL: "TODO_3001_XL", "2XL": "TODO_3001_2XL", "3XL": "TODO_3001_3XL" };
// Print file per design. TODO: replace with Courtney's hi-res originals (transparent PNG, 3600x4800+) once uploaded.
const printFile = (origin, slug) => `${origin}/img/designs/${slug}-1200.jpg`;

const enc = new TextEncoder();
const hex = (buf) => [...new Uint8Array(buf)].map((b) => b.toString(16).padStart(2, "0")).join("");

async function verify(payload, header, secret, toleranceSec = 300) {
  const parts = Object.fromEntries(header.split(",").map((kv) => kv.split("=")).filter((p) => p.length === 2 && p[0] === "t"));
  const t = parts.t, sigs = header.split(",").filter((p) => p.startsWith("v1=")).map((p) => p.slice(3));
  if (!t || !sigs.length || Math.abs(Date.now() / 1000 - Number(t)) > toleranceSec) return false;
  const key = await crypto.subtle.importKey("raw", enc.encode(secret), { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
  const expected = hex(await crypto.subtle.sign("HMAC", key, enc.encode(`${t}.${payload}`)));
  return sigs.some((s) => s.length === expected.length && [...s].reduce((d, c, i) => d | (c.charCodeAt(0) ^ expected.charCodeAt(i)), 0) === 0);
}

export function toPrintfulOrder(session, lineItems, origin) {
  const a = session.shipping_details?.address || session.customer_details?.address || {};
  return {
    external_id: session.id,
    confirm: false, // draft only; a human confirms in Printful
    recipient: { name: session.shipping_details?.name || session.customer_details?.name, email: session.customer_details?.email,
      address1: a.line1, address2: a.line2, city: a.city, state_code: a.state, country_code: a.country, zip: a.postal_code },
    items: lineItems.map((li) => {
      const { slug, size } = li.price?.product?.metadata || {};
      return { variant_id: VARIANTS[size] ?? "TODO_UNKNOWN_SIZE", quantity: li.quantity, name: CATALOG[slug]?.name ?? slug,
        retail_price: (li.price.unit_amount / 100).toFixed(2), files: [{ type: "front", url: printFile(origin, slug) }] };
    }),
  };
}

const json = (body, status = 200) => new Response(JSON.stringify(body), { status, headers: { "content-type": "application/json" } });

export async function onRequestPost({ request, env }) {
  const raw = await request.text();
  if (env.STRIPE_WEBHOOK_SECRET) {
    const ok = await verify(raw, request.headers.get("stripe-signature") || "", env.STRIPE_WEBHOOK_SECRET);
    if (!ok) return json({ error: "bad_signature" }, 400);
  }
  let event; try { event = JSON.parse(raw); } catch { return json({ error: "bad_json" }, 400); }
  if (event.type !== "checkout.session.completed") return json({ received: true, ignored: event.type });

  const session = event.data.object;
  let lineItems = [];
  if (env.STRIPE_SECRET_KEY) {
    const r = await fetch(`https://api.stripe.com/v1/checkout/sessions/${session.id}/line_items?expand[]=data.price.product&limit=100`,
      { headers: { authorization: `Bearer ${env.STRIPE_SECRET_KEY}` } });
    if (!r.ok) return json({ error: "stripe_line_items_failed" }, 502);
    lineItems = (await r.json()).data;
  }
  const order = toPrintfulOrder(session, lineItems, new URL(request.url).origin);

  if (env.PRINTFUL_API_KEY && env.PRINTFUL_LIVE === "1") {
    const r = await fetch("https://api.printful.com/orders", { method: "POST", body: JSON.stringify(order),
      headers: { authorization: `Bearer ${env.PRINTFUL_API_KEY}`, "content-type": "application/json" } });
    return json({ received: true, printful: r.ok ? "draft_created" : `error_${r.status}` }, r.ok ? 200 : 502);
  }
  return json({ received: true, printful: "skipped (PRINTFUL_API_KEY + PRINTFUL_LIVE=1 not both set)", order });
}

export const onRequest = () => json({ error: "method_not_allowed" }, 405);
