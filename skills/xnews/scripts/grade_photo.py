#!/usr/bin/env python3
"""Bake a poster-friendly grade into a photo (tonemap + cool tint + vignette).

Usage:
    python grade_photo.py <input> <output> [--gamma 0.88] [--contrast 1.16]
                                [--tint 0.93,0.985,1.06] [--vignette 0.42]

Why bake it instead of CSS filters: chained CSS `contrast()` then `brightness()`
crushed the shadows to pure black on a real news photo (poster rows measured 9/255
where the source was 38/255). Doing the curve here keeps the highlights and gives a
predictable, repeatable result. Never writes over the input file.
"""
import argparse
import os
import sys


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("dst")
    ap.add_argument("--gamma", type=float, default=0.88, help="<1 lifts midtones")
    ap.add_argument("--contrast", type=float, default=1.16)
    ap.add_argument("--tint", default="0.93,0.985,1.06", help="r,g,b multipliers")
    ap.add_argument("--vignette", type=float, default=0.42, help="0 disables")
    a = ap.parse_args()

    if os.path.abspath(a.src) == os.path.abspath(a.dst):
        print("refusing to overwrite the source file", file=sys.stderr)
        return 2

    try:
        import numpy as np
        from PIL import Image
    except ImportError as e:
        print(f"missing dependency: {e}. install Pillow and numpy", file=sys.stderr)
        return 3

    tint = np.array([float(x) for x in a.tint.split(",")], dtype=np.float32)
    if tint.shape != (3,):
        print("--tint needs three comma-separated numbers", file=sys.stderr)
        return 2

    img = Image.open(a.src).convert("RGB")
    arr = np.asarray(img).astype(np.float32) / 255.0
    lum = 0.2126 * arr[:, :, 0] + 0.7152 * arr[:, :, 1] + 0.0722 * arr[:, :, 2]

    g = np.power(lum, a.gamma)
    g = np.clip((g - 0.5) * a.contrast + 0.5, 0.0, 1.0)
    out = np.clip(g[:, :, None] * tint[None, None, :], 0.0, 1.0)

    if a.vignette > 0:
        h, w = g.shape
        yy, xx = np.mgrid[0:h, 0:w]
        cx, cy = w * 0.56, h * 0.34
        dist = np.sqrt(((xx - cx) / (w * 0.62)) ** 2 + ((yy - cy) / (h * 0.72)) ** 2)
        vig = np.clip(1.0 - a.vignette * np.clip(dist - 0.35, 0, None) ** 1.5, 0.0, 1.0)
        out = np.clip(out * vig[:, :, None], 0.0, 1.0)

    os.makedirs(os.path.dirname(os.path.abspath(a.dst)) or ".", exist_ok=True)
    Image.fromarray((out * 255).astype(np.uint8)).save(a.dst, optimize=True)

    prof = (0.2126 * out[:, :, 0] + 0.7152 * out[:, :, 1] + 0.0722 * out[:, :, 2]) * 255
    bands = [prof[int(prof.shape[0] * i / 4):int(prof.shape[0] * (i + 1) / 4)].mean() for i in range(4)]
    print(f"wrote {a.dst} {img.size[0]}x{img.size[1]}")
    print("luminance by quarter:", [round(float(b), 1) for b in bands])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
