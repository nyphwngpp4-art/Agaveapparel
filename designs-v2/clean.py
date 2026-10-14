"""Clean Courtney's 10 design photos onto the site's bone #E6E2DB.

Background = pixels connected to the image border that are close to the backdrop colour AND sit in a
flat region (low gradient). The gradient barrier is what separates a cream tee from a cream backdrop.
Subject mask is then closed, hole-filled and reduced to its largest piece, feathered, and composited
over flat bone on a 1600px square at a consistent scale. Run with qa/.venv/bin/python (needs scipy).
"""
from pathlib import Path
from PIL import Image, ImageFilter
import numpy as np
from scipy import ndimage

BONE = np.array([230, 226, 219], dtype=np.float32)
CANVAS, FILL = 1600, 0.82
SRC, DST = Path(__file__).parent / "originals", Path(__file__).parent / "clean"
DST.mkdir(exist_ok=True)


ART = {"02", "03", "04"}   # flat artwork, not shirt photos


def art_mask(rgb, dist_tol=22):
    """Flat art: every backdrop-coloured pixel becomes bone (letter counters and the paper inside the
    triangle included), so there is no leftover cream box. Colour distance only; no hole filling."""
    f = rgb.astype(np.float32)
    rim = np.concatenate([f[:12].reshape(-1, 3), f[-12:].reshape(-1, 3), f[:, :12].reshape(-1, 3), f[:, -12:].reshape(-1, 3)])
    bg = np.median(rim, 0)
    paper = np.sqrt(((f - bg) ** 2).sum(-1)) < dist_tol
    paper |= (f.mean(-1) > 244) & (f.std(-1) < 6)
    subj = ndimage.binary_opening(~paper, iterations=1)
    return subj, bg


def subject_mask(rgb, dist_tol=14, grad_tol=10, close=9):
    f = rgb.astype(np.float32)
    rim = np.concatenate([f[:12].reshape(-1, 3), f[-12:].reshape(-1, 3), f[:, :12].reshape(-1, 3), f[:, -12:].reshape(-1, 3)])
    bg = np.median(rim, 0)
    lum = np.array(Image.fromarray(rgb).convert("L").filter(ImageFilter.GaussianBlur(1.5))).astype(np.float32)
    grad = np.hypot(ndimage.sobel(lum, 1), ndimage.sobel(lum, 0))
    white = (f.mean(-1) > 244) & (f.std(-1) < 6)                     # baked white edges count as backdrop
    seed = ((np.sqrt(((f - bg) ** 2).sum(-1)) < dist_tol) & (grad < grad_tol)) | white
    lab, _ = ndimage.label(seed)
    border = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
    bgmask = np.isin(lab, border[border > 0])
    subj = ~bgmask
    subj = ndimage.binary_closing(subj, iterations=close)
    subj = ndimage.binary_fill_holes(subj)
    subj = ndimage.binary_opening(subj, iterations=3)
    lab, n = ndimage.label(subj)
    if n > 1:                                                         # keep the main piece (+ any piece >2% of it, e.g. separate art parts)
        sizes = ndimage.sum(subj, lab, range(1, n + 1)); big = sizes.max()
        subj = np.isin(lab, [i + 1 for i, s in enumerate(sizes) if s > 0.02 * big])
    return subj, bg


def clean(path, art=False):
    rgb = np.array(Image.open(path).convert("RGB"))
    subj, bg = art_mask(rgb) if art else subject_mask(rgb)
    a = Image.fromarray((subj * 255).astype(np.uint8))
    a = a.filter(ImageFilter.GaussianBlur(1.0)) if art else a.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(2.2))
    a = np.array(a).astype(np.float32)[..., None] / 255
    out = rgb.astype(np.float32) * a + BONE * (1 - a)
    ys, xs = np.where(subj)
    sub = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))
    s = CANVAS * FILL / max(sub.size)
    sub = sub.resize((round(sub.width * s), round(sub.height * s)), Image.LANCZOS)
    canvas = Image.new("RGB", (CANVAS, CANVAS), tuple(int(v) for v in BONE))
    canvas.paste(sub, ((CANVAS - sub.width) // 2, (CANVAS - sub.height) // 2))
    # seam check: compare a 6px ring just outside the subject box with pure bone
    arr = np.array(canvas).astype(int); x0, y0 = (CANVAS - sub.width) // 2, (CANVAS - sub.height) // 2
    ring = np.concatenate([arr[y0:y0 + sub.height, max(0, x0 - 6):x0].reshape(-1, 3), arr[y0:y0 + sub.height, x0 + sub.width:x0 + sub.width + 6].reshape(-1, 3)])
    seam = float(np.abs(ring - BONE).max()) if len(ring) else 0
    edge = np.concatenate([arr[y0 + 2, x0:x0 + sub.width], arr[y0 + sub.height - 3, x0:x0 + sub.width], arr[y0:y0 + sub.height, x0 + 2], arr[y0:y0 + sub.height, x0 + sub.width - 3]])
    edge_err = float(np.abs(edge - BONE).sum(-1).max())   # the subject box edge: bone unless the subject touches it
    return canvas, bg, s, seam, edge_err, subj.mean()


if __name__ == "__main__":
    rows = []
    for p in sorted(SRC.glob("??-????????.png")):
        k = p.name[:2]
        edited = SRC / f"{p.stem}-patch-edited.png"     # Jay: image 8's patch text removed (originals stay untouched)
        if edited.exists(): p = edited
        canvas, bg, s, seam, edge_err, frac = clean(p, art=k in ART)
        canvas.save(DST / f"{k}.png"); canvas.save(DST / f"{k}.jpg", quality=92, optimize=True)
        for size in (960, 600):
            canvas.resize((size, size), Image.LANCZOS).save(DST / f"{k}-{size}.webp", quality=86 if size == 960 else 82)
        rows.append(f"{k} backdrop={tuple(int(v) for v in bg)} upscale={s:.2f} subject={frac:.2f} seam_ring_maxdiff={seam:.0f} box_edge_maxdiff={edge_err:.0f}")
        print(rows[-1])
    (DST / "NOTES.txt").write_text("\n".join(rows) + "\n")
    sheet = Image.new("RGB", (5 * 400 + 6 * 12, 2 * 400 + 3 * 12), (37, 9, 9))  # ink gutters make any seam visible
    for i, p in enumerate(sorted(DST.glob("??.png"))):
        sheet.paste(Image.open(p).resize((400, 400), Image.LANCZOS), (12 + (i % 5) * 412, 12 + (i // 5) * 412))
    sheet.save(DST / "contact-sheet.jpg", quality=90)
