# Design Lens: Viktor Oddy → Agave Apparel redesign brief

Researched 2026-10-14 using read-only public X tools: 1 profile lookup, 2 timeline pages (about 42 original posts, 2026-09-30 to 2026-10-14), and 1 keyword search. I also fetched the current preview at https://agave-apparel-preview.pages.dev.

## 1. Handle and style

- **Confirmed handle:** [@viktoroddy](https://x.com/viktoroddy), user id 893369654768529408, "Viktor Oddy", about 73.8k followers. His bio says he is the founder of Design Rocket and links to motionsites.ai, his library of 500+ website prompts.
- **Style:** Cinematic, single-scene hero pages. Oversized display type works as part of the image: a subject breaks through the letters, or a 3D or glass object refracts them. Real-time WebGL, scroll-driven camera moves, and tactile cursor interactions do the work that stock layouts usually do.
- His workflow is AI-first. Images come from Nano Banana, video from Seedance, and code from Claude or GPT. Read the techniques below as visual patterns, not a set of hand-coding tutorials.

**Caveats:** Almost all of his recent posts are video demos or "model A vs B" comparisons. The text rarely explains how something is built. Where the build approach below is mine and not his, I mark it **(my implementation)**. The one exception is post 2106062582243344412, which includes a long, detailed spec (Three.js r169, exact CSS). I could only see video thumbnails, not the motion itself. None of his recent posts are an actual apparel or e-commerce store; the closest is a toy-store landing page.

**Current state of Agave Apparel:** The copy is good ("Dressed different on purpose", Golden Hour, Stay Salty, Out West, the Courtney story, Browse/Order/Wear it out). The structure is a generic hero, a product grid, and a three-step block. Nothing about it is ownable yet.

## 2. Techniques (10)

### T1. Subject breaks through giant headline type
- **Post:** https://x.com/viktoroddy/status/2107639871934460340 (ref `refs/2107639871934460340.jpg`). An orange octopus overlaps the "OCTOPUS / MENTALITY" headline. The headline is set in a tall, thin, high-contrast display face, in two colors and two rows that sit at opposite edges of the frame. Images were made with Nano Banana 2.1.
- **Build (my implementation):** Use three stacked layers: a background image, a full-bleed `<h1>` sized at about `clamp(4rem, 14vw, 16rem)`, and a cut-out PNG or WebP of the subject with `position:absolute; z-index` above the type. Only part of the subject should overlap the letters. Optionally, mask the subject's lower half with `mask-image` so it sits behind some letters and in front of others.
- **Agave:** Use a saguaro or an agave cut-out rising through "GOLDEN HOUR", or a folded tee breaking "OUT WEST". Put a different hero on each design's product page.

### T2. Headline behind subject with layered parallax ("Galaxy Home")
- **Posts:** https://x.com/viktoroddy/status/2107473352659239328 (full tutorial covering the prompt, the hero image, the scroll animations, and fixes; ref `refs/2107473352659239328.jpg`) and https://x.com/viktoroddy/status/2106781795882807317 ("luxury real-estate landing page with 3D parallax"). Also ref `refs/2106783678617825350.jpg`.
- **What it is:** The headline sits mid-depth, behind the house and tower and in front of the sky, so the scene reads as 3D.
- **Build (my implementation):** Split the hero into about 3 depth plates (sky, type, foreground subject). Move them at different rates with GSAP ScrollTrigger (`scrub:true`, foreground `yPercent:-20`, type `-8`, sky `0`) and add a small `pointermove` tilt. Respect `prefers-reduced-motion`.
- **Agave:** Use plates of Sonoran sky, "DRESSED DIFFERENT", and a ridge line of saguaros. Make the type a warm cream color so it glows against the dusk.

### T3. Scroll-driven camera dive into a scene
- **Posts:** https://x.com/viktoroddy/status/2109984169845821651 ("Scroll and the ground opens up"; ref `refs/2109984169845821651.jpg`, plus the companion prompt post https://x.com/viktoroddy/status/2109986125305831589, ref `refs/2109986125305831589.jpg`) and https://x.com/viktoroddy/status/2109456353605587409 ("the camera that dives in as you scroll"; ref `refs/2109456353605587409.jpg`).
- **Build (my implementation):** Use a pinned section (`ScrollTrigger pin:true, end:"+=200%"`). Light version: scrub `scale` from 1 to 1.6 and change `clip-path` on 2 to 3 image plates. Heavy version: a Three.js scene where scroll progress drives `camera.position.z`. Use Lenis for smooth scroll.
- **Agave:** Start the scroll on a wide desert vista. As the visitor scrolls, the ground "opens" into a close-up of the Golden Hour print, which then hands off to the product grid. Use this once per page at most.

### T4. Mixed-case editorial headline (italic serif plus caps)
- **Post:** https://x.com/viktoroddy/status/2109986125305831589 (Moss Valley still: "On-prem THAT FEELS like the PUBLIC CLOUD"). It mixes italic serif lowercase with roman caps in light cream over a green landscape.
- **Build:** Use one display serif with a true italic, such as Fraunces, Instrument Serif, or PP Editorial. Wrap words in `<em>` for italic and `<span class="caps">` for `font-variant: all-small-caps` or uppercase with `letter-spacing:.02em`. Center it in the lower third of a full-bleed image.
- **Agave:** For example, "*Rooted,* PATIENT, *thriving*." Copy that already exists, such as "*Agave.* PATIENCE. *Pour.*", fits this treatment perfectly.

### T5. Glass object refracting the headline (WebGL)
- **Post:** https://x.com/viktoroddy/status/2106062582243344412 (full spec in the post; ref `refs/2106062582243344412.jpg`) and https://x.com/viktoroddy/status/2106061619176620344 ("liquid glass hero section… No Spline. No Blender").
- **What it is:** A rotatable 3D glass cuboid refracts a huge headline with chromatic dispersion. The headline is drawn onto a 2D canvas used as a WebGL texture, and the HTML carries only an `sr-only <h1>` for accessibility.
- **Build (from his spec):** Three.js r169 via importmap, with GLTFLoader and a `RoundedBoxGeometry(1,1,1,8,0.12)` fallback. Add a transmission or refraction shader with per-channel IOR offsets for the dispersion. The canvas uses `cursor:grab` and `touch-action:none`, and the UI overlay uses `pointer-events:none`.
- **Agave:** Use a draggable "agave-glass" object, such as a tequila-glass shape (it ties to "From the Desert to the Glass"), that refracts "AGAVE". Use it only as a signature moment, and keep a static fallback for mobile.

### T6. Small hero UI details: outlined giant numeral and directional underline
- **Post:** https://x.com/viktoroddy/status/2106062582243344412 (same spec).
- **What it is:** A CTA row runs from the button into a hairline and then into a giant outlined "07" that bleeds off the right edge. The nav links have an underline that grows from the left on hover and exits to the right: `transform:scaleX(0); transform-origin:right; transition:transform .35s` changing to `scaleX(1); transform-origin:left`. There is also a vertical pagination-dot column where a hollow ring marks the active dot.
- **Build:** Plain CSS. The numeral uses `-webkit-text-stroke:1.5px currentColor; color:transparent`.
- **Agave:** Show the design count as a giant outlined "22" (or each design's number "07/22") bleeding off the edge. This turns the small-batch count into the brand. Use the underline hover throughout.

### T7. Cursor scratch or tear reveal
- **Post:** https://x.com/viktoroddy/status/2105620114838261853 (ref `refs/2105620114838261853.jpg`): "drag your cursor and the paper rips into ink → inflated chrome letters underneath → it cleans itself up". The still shows a cream page, a black ink "IMAGINE", and chrome letters underneath.
- **Build (my implementation):** Put a top `<canvas>` painted with a paper texture. On `pointermove`, erase along the path with `globalCompositeOperation='destination-out'` using a noisy brush. Fade it back in over time with `requestAnimationFrame` by redrawing at low alpha. The layer underneath is an image or a styled headline.
- **Agave:** Visitors scrape away a sun-bleached desert-dust layer to reveal the full-color print artwork underneath. This would work on the featured-design section or the About strip. It is tactile and reads as screen-print, not as "tech".

### T8. Physics, mouse-reactive elements that "land" on the type
- **Post:** https://x.com/viktoroddy/status/2108728821293965579 (toy store, ref `refs/2108728821293965579.jpg`): "the character lands on the headline, the small figures react to the mouse, and the whole page settles like a real physics scene". The still shows a bold condensed "3D SHAPE" on coral with the character in front. Also https://x.com/viktoroddy/status/2107058718882103388 ("Opus 5.5 + raw WebGL. No Three.js… pick the fruit up, throw it… it all jiggles").
- **Build (my implementation):** Use Matter.js, with the headline letters' bounding boxes as static bodies. Drop 4 to 6 sticker sprites (agave, sun, javelina, river tube) that collide and settle, and let visitors drag and fling them. Keep it to the DOM (Matter.js plus CSS transforms), not WebGL.
- **Agave:** Use this in the footer or the "Pick a design" section, with stickers in the shop's art style. It is playful, matches a graphic-tee brand, and does not conflict with the premium hero.

### T9. ASCII / glyph-built imagery
- **Post:** https://x.com/viktoroddy/status/2109456353605587409 ("the building made of text… the little cube that follows you around"). The ref `refs/2109463155915251954.jpg` (companion post https://x.com/viktoroddy/status/2109463155915251954) shows a building rendered in ASCII glyphs with green highlight blocks on black.
- **Build (my implementation):** Sample an image into a grid on a canvas, then map luminance to a character ramp (`" .:-=+*#%@"`), redrawn in monospace. Make it scroll-reactive. Add a small element that follows the cursor and is eased with a lerp of about 0.12.
- **Agave:** Use sparingly, as a loading state or a 404 page where a saguaro is drawn in glyphs. It works as a secondary texture, not the main look.

### T10. Art-direct with AI-generated imagery, then explore style variants
- **Posts:** https://x.com/viktoroddy/status/2109092526070403094 ("Exploring different style for a design with AI… Made with Seedance 2.5") and its companion https://x.com/viktoroddy/status/2109092984021270706 (ref `refs/2109092984021270706.jpg`: "DRESS THE DREAM BEFORE IT WAKES", dark ornate floral collage, centered serif caps, pill CTA). Tool lists in https://x.com/viktoroddy/status/2107639871934460340 (Nano Banana 2.1 for images). His "Restyles" product post is https://x.com/viktoroddy/status/2108491429131833417.
- **Build:** Generate 2 or 3 hero-background variants of the same layout and pick one. Short looping hero video should be `<video autoplay muted loop playsinline poster>` at under 2 MB, in WebM and MP4.
- **Agave:** Use AI only for **backgrounds and atmosphere**: dusk skies, heat haze, river light. Never use it for the tees, which must be real photos or mockups of Courtney's actual prints. The fashion-collage reference (T10) is the closest of his posts to an apparel brand.

## 3. Art-direction options

**A. "Golden Hour Editorial" (recommended)**
- **Palette:** Warm cream (#F3EBDD), burnt sienna, deep dusk violet, and a single sage green.
- **Type:** A display serif with italics (T4) plus a clean grotesk for UI.
- **Hero:** T1 or T2, with a saguaro silhouette through "DRESSED DIFFERENT", subtle parallax, and the outlined "22" from T6.
- **Product pages:** Each design gets its own full-bleed color world taken from its print.
- **Interaction:** One tactile moment, the dust-scratch reveal (T7).
- **Overall feel:** Like a premium magazine.

**B. "Screenprint Studio"**
- **Look:** Paper-texture backgrounds, misregistered two-color type, and halftone image treatment (an SVG `feTurbulence` grain overlay).
- **Interaction:** The scratch reveal (T7) and the sticker physics footer (T8).
- **Type:** Bolder and condensed (like T8's "3D SHAPE"), with color-blocked sections per design.
- **Overall feel:** Louder and more playful, and true to "wear a conversation".

**C. "Night Desert Cinematic"**
- **Look:** A dark mode: black-violet night sky, starfield, and a cream type glow.
- **Hero:** The scroll camera dive (T3) from the horizon into the Golden Hour print, with optional glass refraction (T5) on "AGAVE".
- **Trade-off:** This is the most impressive option but also the heaviest and riskiest on mobile and performance. It suits a launch or drop page more than the everyday store.

## 4. What to avoid

- **Copying his signature demo looks literally:** chrome blobs, liquid-glass cubes, purple-galaxy palettes. They are already common across AI showcase sites, and this is the "generic AI template" trap in a new form.
- **WebGL on every section:** Pick one signature moment. The store must load fast and work on phones; most tee buyers come from Instagram on mobile.
- **AI-generated product imagery:** Show the real tees, and keep AI to backgrounds only.
- **Scroll-jacking the product grid or checkout:** Pinned or dive effects belong in the editorial sections only.
- **Ignoring `prefers-reduced-motion`, or burying alt text:** Keep an HTML `<h1>` whenever type is drawn into a canvas, as his own spec does.
- **"Model A vs Model B" style uniformity:** Centered pill CTA, Poppins, black background. Choose a typeface with character.
- **Over-literal desert clichés:** Cartoon cacti and Wild West slab fonts. Keep the motifs photographic and textural.

## 5. Downloaded reference images (`/workspace/agave-apparel/design-research/refs/`)

These are post photos or video thumbnails, and each file is named after its post id.

| File | Post |
|---|---|
| 2105620114838261853.jpg | https://x.com/viktoroddy/status/2105620114838261853 (ink-rip "IMAGINE") |
| 2106062582243344412.jpg | https://x.com/viktoroddy/status/2106062582243344412 (glass cube "Explore New Ideas", outlined 07) |
| 2106783678617825350.jpg | https://x.com/viktoroddy/status/2106783678617825350 (Galaxy Home on motionsites) |
| 2107473352659239328.jpg | https://x.com/viktoroddy/status/2107473352659239328 (Galaxy Home comparison) |
| 2107639871934460340.jpg | https://x.com/viktoroddy/status/2107639871934460340 (Octopus Mentality) |
| 2108728821293965579.jpg | https://x.com/viktoroddy/status/2108728821293965579 (toy store "3D SHAPE") |
| 2108893193144315918.jpg | https://x.com/viktoroddy/status/2108893193144315918 (fintech-style dashboard landing, not used above) |
| 2109092984021270706.jpg | https://x.com/viktoroddy/status/2109092984021270706 ("Dress the Dream" collage) |
| 2109456353605587409.jpg | https://x.com/viktoroddy/status/2109456353605587409 (ASCII architecture studio) |
| 2109463155915251954.jpg | https://x.com/viktoroddy/status/2109463155915251954 (ASCII Studio on motionsites) |
| 2109984169845821651.jpg | https://x.com/viktoroddy/status/2109984169845821651 (Moss Valley, ground opens) |
| 2109986125305831589.jpg | https://x.com/viktoroddy/status/2109986125305831589 (Moss Valley on motionsites) |
