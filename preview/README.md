# Agave Apparel — preview store

Static rebuild of agaveapparel.com (from `../site-snapshot`) with sizes, a cart and Stripe checkout scaffolding.
**Preview only:** every page is `noindex` (meta tag + `X-Robots-Tag` in `_headers`, `robots.txt` disallows all).
The live site and its DNS are untouched.

- Build: `python3 build.py` → `out/` (also writes `functions/_lib/catalog.json`, the server-side price list).
- Deploy: `env -u CLOUDFLARE_API_TOKEN npx --yes wrangler@3 pages deploy out --project-name agave-apparel-preview --branch main --commit-dirty=true`

## Environment variables (Cloudflare Pages → Settings → Variables; never commit them)
| Var | Effect |
|---|---|
| *(none set)* | `/api/checkout` returns 200 `{live:false, error:"checkout_not_live"}` placeholder. No Stripe or Printful calls. |
| `STRIPE_SECRET_KEY` | `/api/checkout` creates a Stripe Checkout Session. Use an `sk_test_...` key on the preview. Prices come from the server catalog, not the browser. |
| `STRIPE_WEBHOOK_SECRET` | `/api/stripe-webhook` verifies the `Stripe-Signature` header (HMAC-SHA256, 5 min tolerance) and rejects bad ones. Unset = accepted unverified (preview only; set it before going live). |
| `PRINTFUL_API_KEY` **and** `PRINTFUL_LIVE=1` | Only when **both** are set does the webhook POST the order to Printful, and even then as a draft (`confirm: false`). Otherwise it returns the payload it would have sent. |

## TODO before going live
- `VARIANTS` in `functions/api/stripe-webhook.js`: real Printful Bella+Canvas 3001 variant ids per size (and colour per design).
- Print files: replace the 1200px site images with Courtney's originals (transparent PNG 3600×4800+ or vector).
- Review the "Made in Arizona" / small-batch / "Ships within 7–10 days" wording (kept verbatim for now).
