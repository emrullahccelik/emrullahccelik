"""Crop git-koi's 512x512 GIF down to the koi and scale it up crisply.

git-koi draws the koi in the middle of a large transparent canvas, so a young
koi looks tiny on the profile. This finds the area the koi covers across every
frame, crops all frames to it (plus a margin), and enlarges by an integer
factor with nearest-neighbour so the pixel art stays sharp.

usage: python3 scripts/crop_koi.py koi/koi.gif [scale] [margin]
"""
import sys

from PIL import GifImagePlugin, Image, ImageSequence

# Keep every frame in palette mode so the GIF's colors and transparency survive.
GifImagePlugin.LOADING_STRATEGY = GifImagePlugin.LoadingStrategy.RGB_AFTER_DIFFERENT_PALETTE_ONLY


def main():
    path = sys.argv[1]
    scale = int(sys.argv[2]) if len(sys.argv) > 2 else 2
    margin = int(sys.argv[3]) if len(sys.argv) > 3 else 12

    gif = Image.open(path)
    loop = gif.info.get("loop", 0)
    frames, durations, box = [], [], None
    for frame in ImageSequence.Iterator(gif):
        frames.append(frame.copy())
        durations.append(frame.info.get("duration", gif.info.get("duration", 70)))
        b = frame.convert("RGBA").getbbox()
        if b:
            box = b if box is None else (min(box[0], b[0]), min(box[1], b[1]),
                                         max(box[2], b[2]), max(box[3], b[3]))
    if box is None:
        print("empty GIF, nothing to crop")
        return

    w, h = gif.size
    box = (max(box[0] - margin, 0), max(box[1] - margin, 0),
           min(box[2] + margin, w), min(box[3] + margin, h))
    size = ((box[2] - box[0]) * scale, (box[3] - box[1]) * scale)

    # Crop in palette mode when possible so no colors are re-quantized.
    palette_ok = all(f.mode == "P" for f in frames)
    out = []
    for frame in frames:
        src = frame if palette_ok else frame.convert("RGBA")
        out.append(src.crop(box).resize(size, Image.NEAREST))

    extra = {}
    if palette_ok and "transparency" in gif.info:
        extra["transparency"] = gif.info["transparency"]
    out[0].save(path, save_all=True, append_images=out[1:], duration=durations,
                loop=loop, disposal=2, optimize=False, **extra)
    print(f"cropped {len(out)} frames to {box}, saved at {size[0]}x{size[1]}")


if __name__ == "__main__":
    main()
