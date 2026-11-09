"""Give git-bonsai's leaves a purple/blue night palette.

git-bonsai draws every GIF from one fixed palette stored as the GIF's global
color table, so swapping the leaf slots there recolors every frame without
touching the pixels. Running it twice gives the same result.

usage: python3 scripts/recolor_bonsai.py output/bonsai.gif [more.gif ...]
"""
import sys
from pathlib import Path

# palette slot -> new color, dark -> light within each leaf ramp
PALETTE = {
    17: "#4a1f4f", 18: "#73306f", 19: "#a04c8e", 20: "#d27fb6",  # rose
    21: "#0b2f7a", 22: "#1257ab", 23: "#2a8bd8", 24: "#7ccdf2",  # blue
    28: "#2b1d6b", 29: "#4a32a6", 30: "#7253dc", 31: "#a98ff7",  # violet
}

TABLE = 13  # 6-byte header + 7-byte logical screen descriptor


def recolor(path):
    data = bytearray(path.read_bytes())
    if data[:3] != b"GIF" or not data[10] & 0x80:
        sys.exit(f"{path}: not a GIF with a global color table")
    slots = 2 << (data[10] & 0x07)
    for slot, color in PALETTE.items():
        if slot < slots:
            data[TABLE + slot * 3:TABLE + slot * 3 + 3] = bytes.fromhex(color[1:])
    path.write_bytes(data)
    print(f"recolored {path}")


if __name__ == "__main__":
    for arg in sys.argv[1:] or ["output/bonsai.gif"]:
        if Path(arg).exists():
            recolor(Path(arg))
