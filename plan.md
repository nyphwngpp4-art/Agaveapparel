# Agave Apparel Co. — Site Review & Automation Plan
_Prepared Oct 14, 2026 for Jay & Courtney Messamore. Fetched live at ~3:20 AM Phoenix time (MST)._

## 1. Website review (https://agaveapparel.com)
**Status:** Live (HTTP 200). Not parked.

**Platform:** Custom **Next.js** app (`/_next/static/...` assets) behind **Cloudflare**. Not Shopify, Squarespace or Wix. There's no built-in cart or checkout, so "staying on the platform" means adding payments to the code yourselves.

**What's there**
- Pages: Home, Shop, About, Contact, and 22 product pages (all returned 200).
- 22 designs priced **$28–$38** (most $30–$36), e.g. Golden Hour $36, Agave Desert Life $34, Out West $32, Arizona, Home $28.
- Copy is strong and on-brand ("Dressed different on purpose", "wear a conversation than a logo"). The product taglines are good.
- Fonts: Fraunces, Inter and JetBrains Mono. There's a viewport meta tag, so it's set up for mobile (I didn't test it on a real device).

**Problems found**
1. **No checkout.** "Order this design" opens an email to Courtney, and payment is **by Zelle**. This is the biggest problem: there's no cards, no instant purchase and no buyer protection, and every order is manual.
2. **No size selector** on product pages. Size is settled over email.
3. **Product claims will need to change with print-on-demand:** "Printed small-batch, Arizona", "Made in Arizona", "Ships within 7–10 days", "No duplicates". These need rewording if fulfillment moves to a POD provider outside AZ.
4. **SEO basics are missing:** `/sitemap.xml` returns **404**, there's **no favicon** (`/favicon.ico` 404), and there are **no Open Graph, Twitter or JSON-LD Product tags** (0 found), so shared links have no preview and Google gets no rich product results. There *is* a meta description and good titles.
5. **Images are CSS background-images** with no `<img>`/alt text. That hurts accessibility and Google Images.
6. **No social links** (no Instagram, TikTok or Facebook found) and no email signup.
7. Small mismatch: the footer says "Phoenix, Arizona", but you're in Chandler. Fine if intentional.

**Quick wins:** add Stripe Payment Links plus a size dropdown; add a sitemap, favicon, OG and Product schema; use `<img alt>` or next/image; add an Instagram link and an email capture.

## 2. Recommended automation stack (low subscription)

### Print-on-demand comparison (Bella+Canvas 3001, US, S–XL, one front print)
| Provider | Base cost (free plan) | Paid plan | Quality / notes |
|---|---|---|---|
| **Printful** | **$11.69** | Growth ~$24.99/mo → $9.05 | In-house printing, most consistent quality; API, Shopify/Etsy/Woo/Wix integrations |
| **Printify** | ~$8.50–9.50 (depends on provider) | Premium $39/mo (raised Feb 2026) | Cheapest, but quality and turnaround vary by provider; check each provider's rating |
| **Gelato** | ~$11.99 | Gelato+ ~$24–30/mo | Strongest for international orders; quoted per destination |
| CustomCat | ~$7.95 | none | Cheap; fewer reviews |

Sources: [PodVector – Printful 3001 cost](https://podvector.ai/articles/printful/costs-and-charges/printful-bella-canvas-3001-base-cost-full-breakdown-for-pod-sellers), [ApparelHub 2026 comparison](https://apparelhub.ai/blog/best-print-on-demand-supplier-for-t-shirts), [PodVector 3-way comparison](https://podvector.ai/articles/printful/comparison/printify-vs-printful-vs-gelato-comparison-which-is-best-for-pod-sellers), [Merch Titans](https://merchtitans.com/blog/printful-vs-printify-vs-gelato-comparison). Prices are from third-party 2026 articles; confirm them in each catalog before setting prices.

**Arizona facilities:** I found no confirmed Arizona facility for Printful or Gelato. With Printify you can filter providers by location in the dashboard, so check there. A local Phoenix-area DTG shop would keep "Made in Arizona" true, but it would need to be contacted (not done).

**Pick: Printful, free plan.** Quality matters at a $30+ price point, there's no subscription, and the API is the cleanest. Revisit Printify only if volume grows past ~30 orders/month.

### Storefront and payment
- **Keep the current Next.js site** and add **Stripe Checkout or Payment Links**. Stripe has no monthly fee; it charges 2.9% + $0.30 per US card charge ([stripe.com/pricing](https://stripe.com/pricing)).
- Not recommended: Shopify (~$39/mo Basic, more subscription) or Etsy as the main store. Etsy is optional as a second channel: no monthly fee, $0.20 listing + 6.5% transaction fee + payment processing, and Printful/Printify integrate natively.

### Automatic order routing (no paid middleware)
Stripe webhook (`checkout.session.completed`), then a small Cloudflare Worker or Next.js API route (free tier), then a **Printful Orders API** call with the size and design variant. Printful emails tracking, and the Worker emails or forwards it to the customer. No Zapier subscription needed.

### AI design-idea pipeline
1. **Weekly trend research** (a bot routine): AZ seasons and events (monsoon, spring training, Salt River tubing), Etsy and X trends, plus her best sellers.
2. **Image generation:** generate 5–10 concepts in her style (pay-per-use image APIs, roughly cents per image; or her existing tools).
3. **Human approval:** Courtney picks, edits or rejects. Nothing goes live without her.
4. **Mockups** via the Printful Mockup Generator API (free with an account).
5. **Auto-publish:** add the product to the site's product data, create the Stripe Price and the Printful sync product, then redeploy.

### Unit economics (one tee, Printful free plan, sold on own site)
| | $28 tee | $34 tee | $36 tee |
|---|---|---|---|
| Printful base (S–XL) | 11.69 | 11.69 | 11.69 |
| Shipping (charge customer, or absorb ≈$4.75*) | (4.75) | (4.75) | (4.75) |
| Stripe 2.9%+$0.30 | 1.11 | 1.29 | 1.34 |
| **Profit if shipping is charged to the customer** | **$15.20** | **$21.02** | **$22.97** |
| Profit if shipping is absorbed | ~$10.45 | ~$16.27 | ~$18.22 |

*Printful's US first-item tee shipping is about $4.75; verify it in the dashboard. 2XL and up costs +$2.50–7.50 base.

**Monthly fixed cost: about $0** (Stripe, Printful free plan, Cloudflare free tier). The only possible extras are image-generation usage (a few dollars) and the domain, which you already pay for.

### Risks
- **Trademark and copyright:** AI images can echo existing artwork. Purely AI-generated art may not be copyrightable in the US (U.S. Copyright Office guidance), so Courtney should materially edit each design. Avoid brand names, logos and team marks. "Salt River", "tequila" and other place or product words are generally fine, but don't imitate other brands' labels. Run a USPTO search on slogans.
- **Quality control:** order a sample of every new design before listing it (Printful offers sample discounts), and check print color on the darker shirts.
- **Copy accuracy:** update the "Printed in Arizona / small-batch / 7–10 days" claims.

## 3. Phased rollout
**What Jay or Courtney must do (bots can't):** create Stripe and Printful accounts (bank, tax ID, identity verification), approve every design, order samples, and decide on the "Made in AZ" wording.

**What bots can run:** Bob builds the Stripe checkout, size picker, webhook-to-Printful routing and SEO fixes. A weekly routine delivers 5–10 design ideas for Courtney to approve, then generates mockups and publishes the approved ones.

- **Phase 1 (week 1–2):** accounts, checkout, SEO fixes, and upload the 22 existing designs to Printful; order samples.
- **Phase 2 (week 3–4):** automated order routing live; retire Zelle and email ordering.
- **Phase 3 (month 2+):** weekly AI idea routine with an approval gate; optional Etsy channel; Instagram.

**First 3 steps**
1. Courtney exports print-ready files (PNG, 300 DPI, transparent) for the 22 designs. Jay signs up for free Printful and Stripe accounts.
2. Order 2–3 samples of best sellers from Printful to check quality.
3. Bob adds a size selector, Stripe Checkout, sitemap, favicon and OG tags to the Next.js site, plus the Stripe-to-Printful webhook.
