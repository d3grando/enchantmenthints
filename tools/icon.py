"""Draws icon.png, the registry icon: an enchanted book, its cover shimmering, and a small tooltip over it with lines
of hint, in a vanilla tooltip's frame (the frame LookAt's icon uses, so the mods look like one family). 32 x 32 pixel
art scaled 8 times to 256 x 256. Needs Pillow.

    python tools/icon.py [icon.png]
"""
import sys

from PIL import Image

SIZE, SCALE = 32, 8
BACKGROUND = (0x10, 0x00, 0x10, 0xF0)
FRAME_TOP = (0x50, 0x00, 0xFF, 0xFF)
FRAME_BOTTOM = (0x28, 0x00, 0x7F, 0xFF)


def lerp(a, b, t):
    return tuple(round(ca + (cb - ca) * t) for ca, cb in zip(a, b))


class Canvas:
    """A 32 x 32 tooltip; drawing stays inside its frame."""

    def __init__(self):
        self.img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
        self.px = self.img.load()
        for y in range(SIZE):
            for x in range(SIZE):
                if x in (0, SIZE - 1) and y in (0, SIZE - 1):
                    continue
                edge = x in (0, SIZE - 1) or y in (0, SIZE - 1)
                frame = x in (1, SIZE - 2) or y in (1, SIZE - 2)
                self.px[x, y] = lerp(FRAME_TOP, FRAME_BOTTOM, (y - 1) / (SIZE - 3)) if frame and not edge else BACKGROUND

    def set(self, x, y, c):
        if not (2 <= x < SIZE - 2 and 2 <= y < SIZE - 2) or c is None:
            return
        if len(c) == 4 and c[3] < 255:
            under, a = self.px[x, y], c[3] / 255
            c = tuple(round(u + (v - u) * a) for u, v in zip(under[:3], c[:3])) + (under[3],)
        self.px[x, y] = c if len(c) == 4 else c + (255,)

    def sprite(self, x0, y0, art, palette):
        for dy, row in enumerate(art):
            for dx, ch in enumerate(row):
                if ch not in ". ":
                    self.set(x0 + dx, y0 + dy, palette[ch])

    def save(self, path):
        self.img.resize((SIZE * SCALE, SIZE * SCALE), Image.NEAREST).save(path, optimize=True)


PALETTE = {
    # the book: cover, its light edge, the spine, the pages and their lines, the gold fittings
    "C": (0x8C, 0x2C, 0x48), "c": (0xB0, 0x44, 0x64), "S": (0x5C, 0x18, 0x30),
    "P": (0xF0, 0xE6, 0xCC), "p": (0xC4, 0xB4, 0x94), "Y": (0xF8, 0xC8, 0x48), "y": (0xB4, 0x84, 0x24),
    # the hint's tooltip: its fill, its text
    "T": (0x24, 0x0C, 0x34), "A": (0x60, 0xF0, 0xF0), "a": (0xB8, 0xB8, 0xC8),
    # the shimmer and its sparkles
    "M": (0xE0, 0x80, 0xFF, 0x70), "m": (0xF0, 0xC0, 0xFF),
}
FRAME_TOP_SMALL, FRAME_BOTTOM_SMALL = (0x90, 0x50, 0xFF), (0x50, 0x20, 0xC0)

# The cover's gold fittings, over its 13 x 16 face.
FITTINGS = [
    ".............",
    ".............",
    "...Yy....Yy..",
    "...y......y..",
    ".............",
    ".......Y.....",
    "......YyY....",
    ".....YyYyY...",
    "......YyY....",
    ".......Y.....",
    ".............",
    ".............",
    "...y......y..",
    "...Yy....Yy..",
    ".............",
    ".............",
]


def book(c, bx, by):
    """A closed book, its cover 13 x 16 at (bx, by), the pages and the back cover showing below and to the right."""
    for y in range(2, 18):
        for x in range(2, 15):
            if x == 14 or y == 17:
                colour = "S"
            elif (x >= 13 and y % 2 == 0) or (y >= 16 and x % 2 == 1):
                colour = "p"
            else:
                colour = "P"
            c.set(bx + x, by + y, PALETTE[colour])
    for y in range(16):
        for x in range(13):
            colour = "S" if x < 2 else "c" if y == 0 or x == 2 else "C"
            if FITTINGS[y][x] != ".":
                colour = FITTINGS[y][x]
            c.set(bx + x, by + y, PALETTE[colour])
            if (x + y) % 9 in (0, 1):
                c.set(bx + x, by + y, PALETTE["M"])


SPARKLE = [
    ".m.",
    "mMm",
    ".m.",
]


def draw():
    c = Canvas()
    book(c, 4, 11)  # the shimmer: bands of light sweeping the cover
    for x, y in [(3, 9), (21, 26)]:
        c.sprite(x - 1, y - 1, SPARKLE, {"m": PALETTE["m"], "M": (0xFF, 0xFF, 0xFF)})
    # the tooltip over the book: a frame fading top to bottom round its fill, a tail pointing at the book
    x0, y0, x1, y1 = 14, 3, 28, 13
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            if x in (x0, x1) and y in (y0, y1):
                continue
            edge = x in (x0, x1) or y in (y0, y1)
            c.set(x, y, lerp(FRAME_TOP_SMALL, FRAME_BOTTOM_SMALL, (y - y0) / (y1 - y0)) + (255,) if edge else PALETTE["T"])
    for x, y in [(16, 14), (17, 14), (16, 15)]:
        c.set(x, y, FRAME_BOTTOM_SMALL + (255,))
    c.set(17, 13, PALETTE["T"])
    for y, (colour, length) in zip((5, 8, 11), (("A", 9), ("a", 11), ("a", 6))):
        for dx in range(length):
            c.set(16 + dx, y, PALETTE[colour])
            if y != 11:
                c.set(16 + dx, y + 1, PALETTE[colour])
    return c


if __name__ == "__main__":
    draw().save(sys.argv[1] if len(sys.argv) > 1 else "icon.png")
