# Agave Apparel: print-ready artwork (scope: 02 and 08 only; the other 8 are on hold)

Sources: ChatGPT images in `designs-v2/originals/`. 02 = `02-e2f0c477.png` (flat art on cream, 1024²). 08 = `08-5c8b9068.png` (a photo of a tee; the patch edit doesn't matter for print). Graphic regions cropped from the originals: 02 is about 825×775 px, 08 about 380×400 px.
Tools, all free and local: Real-ESRGAN ncnn-vulkan (x4plus, CPU via Mesa lavapipe), scikit-learn k-means palette, vtracer, cairosvg. Total cost $0.

Both methods were tried on both designs (Real-ESRGAN trial outputs are in `method-trials/`):
- **(a) Upscale:** Real-ESRGAN 4×, then Lanczos to 4500 px on the long side, then a soft colour key on the shirt/cream colour with un-premultiplied edges.
- **(b) Vector:** 2× Lanczos, then a median filter, then a 7-colour k-means palette with cream keyed out, then vtracer (spline, stacked), then a 4500 px PNG rendered from the SVG.

| Design | Method chosen | Final px | Print size @300 DPI | Verdict | Why |
|---|---|---|---|---|---|
| 02 Agave Apparel bandana triangle | Vector (vtracer, 5 ink colours) | 4500×4227 | 15.0×14.1 in | **Holds up** | The source is clean flat art, so the vector gives crisp, solid lettering ("AGAVE / APPAREL" reads correctly; no AI garbling). Real-ESRGAN kept the fake paper emboss texture and left a light halo around every letter, so it lost. Small caveats: the cream sky inside the triangle is now transparent (shirt colour shows through, which is fine on cream/natural tees but looks different on dark ones), and the tiny cacti are slightly simplified. |
| 08 Patterned (Aztec) agave diamond | Vector (vtracer, 6 ink colours) | 4275×4500 | 14.25×15.0 in | **Borderline (agave leaves won't hold up close-up)** | This was a photo of a printed tee at only about 380 px across. The geometric frame vectorizes well, but the rust inlay chevrons came out blobby with uneven edges, because fabric shading blurred the rust/orange boundary. The agave's fine leaf hatching is lost to the shirt texture: the vector posterizes it into blocky two-tone leaves, and Real-ESRGAN turns it into mushy "embroidery" with holes and halos. The thin cream highlight lines were keyed out with the shirt. Fine at arm's length on a cream tee; for a true reproduction the agave and inlays need a manual redraw or cleanup in Inkscape. A stronger-smoothing 8-colour vector variant was worse (the leaves melted together). |

Before/after crops (100% zoom; panels are source upscaled nearest-neighbour | Real-ESRGAN+key | vtracer SVG):
- `crops/02-before-after.png`: lettering. `crops/02-before-after-sun.png`: sun rays and border.
- `crops/08-before-after.png`: agave leaves. `crops/08-before-after-border.png`: chevron and inlay edges.

Not uploaded anywhere; preview site untouched; nothing committed.

## 11 Agave → tequila icon row (redone 2026-10-14 from the 1536×1024 source)
Cropped to the art (1365×405 px), keyed out the white and cream, snapped to a 6-colour k-means palette, upscaled 4× with per-colour smoothing (σ5), traced with vtracer (spline) and rendered with cairosvg. Real-ESRGAN not used. Output 4500×1335 px = 15.0×4.45 in @300 DPI. Verdict: **holds up**. The edges and arrows are clean, the bottle and jug read well, the jug liquid tone and the bottle base lines are kept, and there is no halo. The cream highlights inside the bottle are now transparent, so the shirt colour shows through them. Bottle and jug symmetry comes from the source, not enforced. Script: `method-trials/11/v11-hires.py`.
