"""Stitch the sequential step screenshots (01_*.png, 02_*.png, ...) into an
animated gif for the README. Self-contained: needs only Pillow, no ffmpeg.

Usage:  python tools/make_gif.py [artifacts_dir] [output.gif]
"""
import glob
import os
import sys

from PIL import Image

DEFAULT_DIR = "artifacts"
FRAME_MS = 1400
MAX_WIDTH = 360


def main():
    art_dir = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_DIR
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(art_dir, "run.gif")

    # numbered step shots, in order; ignore FAILURE_* and the gif itself
    paths = sorted(
        p for p in glob.glob(os.path.join(art_dir, "*.png"))
        if os.path.basename(p)[0].isdigit()
    )
    if not paths:
        print(f"no step screenshots found in {art_dir!r}")
        sys.exit(1)

    frames = []
    for p in paths:
        img = Image.open(p).convert("RGB")
        if img.width > MAX_WIDTH:
            h = int(img.height * MAX_WIDTH / img.width)
            img = img.resize((MAX_WIDTH, h))
        frames.append(img)

    frames[0].save(
        out, save_all=True, append_images=frames[1:],
        duration=FRAME_MS, loop=0, optimize=True,
    )
    print(f"wrote {out} ({len(frames)} frames)")


if __name__ == "__main__":
    main()
