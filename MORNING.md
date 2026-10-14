# Morning notes: Agave Apparel

## Preview
https://agave-apparel-preview.pages.dev  (test copy, not indexed by search engines, banner says "Preview, not the live store")
The live agaveapparel.com and its DNS were not touched. Nothing was pushed to GitHub.

What it has: all 22 product pages, sizes S–3XL (Bella+Canvas 3001), a cart, and a Checkout button.
Checkout says "Checkout is not live yet" until Stripe test keys are added. No card can be charged.

## Designs
All 22 site images are 1200×1200 px with no transparency, and 16 of them are photos of shirts, not the artwork.
None can be printed well. We need Courtney's originals for all 22: transparent PNG at 3600×4800 px or larger, or vector (AI/SVG/PDF).
Details: designs/designs.csv

## Printful
Signed in via 1Password on 2026-10-14 ~3:33 AM. Nothing was uploaded, created, connected, or bought.
- Account: "courtney messamore" (Courtney's Gmail). Confirm this is the account to use.
- Plan: Free ($0/mo). The Growth trial was declined, not started.
- Billing: no card on file, wallet $0, no payments.
- Store: one Shopify store, "My Store", showing an authorization Error (needs Reconnect). Not touched.
- Products: 1 template, "Women's Relaxed T-Shirt" (front print), unpublished.
- File library: the Agave Apparel logo plus Printful's sample files.
- Orders: none.
- API tokens: generated at Printful Developers when you're ready. I didn't create one.
- No designs uploaded tonight: all 22 site images are 1200px, and 16 are shirt photos. Uploading waits for Courtney's originals.
- Decide whether to drop the old Shopify store connection, since the new site will route orders by API instead.

## "Made in Arizona" wording (kept word for word on the preview)
- "Made in Arizona · Shipped Everywhere" (top bar)
- "© 2026 Agave Apparel Co. — Made in Arizona" (footer)
- "Designed in Arizona · Small batch · No duplicates of anyone · Ships worldwide"
- "Small-batch graphic tees designed in the Sonoran Desert. One-of-a-kind pieces for people who’d rather wear a conversation than a logo."
- "Everything is printed small-batch. You’ll get something made for you, not mass-produced for the algorithm."
- "Agave Apparel is deliberately small. Everything is printed in limited runs, on soft cotton…"
- "Small batch, always. No endless inventory. No overproduction."
- Product pages: "Printed: Small-batch, Arizona" and "Ships: Usually within 7–10 days"

With print-on-demand, Printful prints the shirts at its own facilities, which may not be in Arizona.
So "Made in Arizona", "Printed … Arizona", "small-batch" and "no duplicates" may need rewording. Jay to decide.
("Designed in Arizona" stays true.)
Copy I did change: the "How it works" order step and the Contact page no longer mention emailing to order or paying by Zelle, since the preview has a cart.

## Jay's to-do
1. Create a Stripe account. Put the test keys (STRIPE_SECRET_KEY = sk_test_…, later STRIPE_WEBHOOK_SECRET) into Cloudflare Pages → agave-apparel-preview → Settings → Variables. Never in the code.
2. Get Courtney's original files for all 22 designs (see Designs above).
3. Review the "Made in Arizona" / small-batch / 7–10 days wording.
4. Decide the Printful plan and account (see Printful above). Orders are only sent to Printful when PRINTFUL_API_KEY is set and PRINTFUL_LIVE=1, and even then only as drafts.
