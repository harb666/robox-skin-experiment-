"""Generates the Neon Ranger Roblox character assets.

Outputs (relative to roblox-character/):
  upload/  Shirt + Pants classic clothing templates (585x559) and face decal
  preview/ Front view, back view and a full character sheet
Run:  python3 source/generate.py
"""
import math
import os
import random

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD = os.path.join(ROOT, "upload")
PREVIEW = os.path.join(ROOT, "preview")
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
random.seed(7)

# ---------------------------------------------------------------- palette
CLOAK = (30, 74, 58)
CLOAK_D = (16, 42, 34)
CLOAK_L = (58, 116, 86)
BODICE = (20, 46, 40)
BODICE_D = (10, 26, 24)
GOLD = (214, 172, 82)
GOLD_D = (146, 108, 44)
GOLD_L = (252, 226, 150)
LACE = (200, 160, 100)
NEON_G = (70, 255, 170)
NEON_M = (255, 64, 226)
LEATHER = (92, 56, 40)
LEATHER_D = (54, 32, 24)
LEATHER_L = (132, 86, 60)
BLACK = (16, 14, 24)
BLACK_L = (44, 40, 60)
SKIN = (244, 226, 238)
SKIN_D = (218, 190, 214)
HAIR = (34, 56, 178)
HAIR_D = (16, 24, 100)
HAIR_L = (104, 140, 236)
HAIR_RIM = (196, 70, 226)
EYE = (126, 64, 228)
EYE_D = (44, 16, 96)
EYE_L = (206, 172, 255)
LIP = (66, 150, 232)
FEATHER = (222, 40, 162)
FEATHER_L = (255, 120, 214)
EAR = (70, 62, 190)
EAR_IN = (242, 124, 222)
FLUFF = (246, 238, 255)
LEAF = (42, 100, 68)
LEAF_L = (76, 148, 96)
LEAF_V = (20, 52, 38)
GEM = (60, 220, 140)

# ------------------------------------------------- Roblox template layout
# Classic clothing template, 585x559. Each entry: (x, y, w, h).
TORSO = {"F": (231, 74, 128, 128), "B": (427, 74, 128, 128),
         "R": (165, 74, 64, 128), "L": (361, 74, 64, 128),
         "U": (231, 8, 128, 64), "D": (231, 204, 128, 64)}
LIMB_R = {"L": (19, 355, 64, 128), "B": (85, 355, 64, 128),
          "R": (151, 355, 64, 128), "F": (217, 355, 64, 128),
          "U": (217, 289, 64, 64), "D": (217, 485, 64, 64)}
LIMB_L = {"F": (308, 355, 64, 128), "L": (374, 355, 64, 128),
          "B": (440, 355, 64, 128), "R": (506, 355, 64, 128),
          "U": (308, 289, 64, 64), "D": (308, 485, 64, 64)}
TEMPLATE_SIZE = (585, 559)


# ------------------------------------------------------ drawing canvas
class C:
    """Supersampled canvas: all coordinates are in output pixels."""

    def __init__(self, w, h, s=4, bg=(0, 0, 0, 0)):
        self.w, self.h, self.s = w, h, s
        self.im = Image.new("RGBA", (w * s, h * s), bg)
        self.d = ImageDraw.Draw(self.im)

    def P(self, pts):
        return [(x * self.s, y * self.s) for x, y in pts]

    def W(self, w):
        return max(1, round(w * self.s))

    def rect(self, x0, y0, x1, y1, fill):
        self.d.rectangle([x0 * self.s, y0 * self.s, x1 * self.s - 1, y1 * self.s - 1], fill=fill)

    def poly(self, pts, fill=None, outline=None, width=1):
        if fill is not None:
            self.d.polygon(self.P(pts), fill=fill)
        if outline is not None:
            self.d.line(self.P(list(pts) + [pts[0]]), fill=outline, width=self.W(width), joint="curve")

    def line(self, pts, fill, width=1):
        self.d.line(self.P(pts), fill=fill, width=self.W(width), joint="curve")
        r = width / 2
        for x, y in (pts[0], pts[-1]):  # round caps
            self.ell(x, y, r, r, fill)

    def ell(self, cx, cy, rx, ry, fill=None, outline=None, width=1):
        box = [(cx - rx) * self.s, (cy - ry) * self.s, (cx + rx) * self.s, (cy + ry) * self.s]
        self.d.ellipse(box, fill=fill, outline=outline, width=self.W(width) if outline else 0)

    def layer(self):
        return C(self.w, self.h, self.s)

    def comp(self, other, blur=0, mask=None):
        im = other.im
        if blur:
            im = im.filter(ImageFilter.GaussianBlur(blur * self.s))
        if mask is not None:
            a = np.asarray(im).copy()
            a[..., 3] = (a[..., 3].astype(np.float32) * (np.asarray(mask.im)[..., 3] / 255.0)).astype(np.uint8)
            im = Image.fromarray(a)
        self.im.alpha_composite(im)

    def glow(self, fn, blur=3):
        g = self.layer()
        fn(g)
        self.comp(g, blur=blur)
        self.comp(g, blur=blur / 2.5)
        fn(self)

    def out(self, noise=3):
        im = self.im.resize((self.w, self.h), Image.LANCZOS)
        if noise:
            a = np.asarray(im).astype(np.int16)
            n = np.random.default_rng(1).normal(0, noise, a.shape[:2])[..., None]
            a[..., :3] = np.clip(a[..., :3] + n, 0, 255)
            im = Image.fromarray(a.astype(np.uint8))
        return im


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def rgba(c, a):
    return (c[0], c[1], c[2], a)


def bez(p0, p1, p2, n=24):
    out = []
    for i in range(n + 1):
        t = i / n
        out.append(((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0],
                    (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]))
    return out


# ------------------------------------------------------ motif primitives
def fabric(c, pts, base, folds=(), lit=CLOAK_L, dark=CLOAK_D):
    """Fill polygon with base colour plus soft fold shading clipped to it."""
    mask = c.layer()
    mask.poly(pts, fill=(255, 255, 255, 255))
    body = c.layer()
    body.poly(pts, fill=rgba(base, 255))
    c.comp(body)
    sh = c.layer()
    for f in folds:
        sh.line(f, rgba(dark, 170), 4)
        sh.line([(x + 3, y) for x, y in f], rgba(lit, 90), 2)
    sh.im = sh.im.filter(ImageFilter.GaussianBlur(2 * c.s))
    c.comp(sh, mask=mask)


def leaf(c, x, y, L, W, ang, fill, vein=LEAF_V, edge=None):
    a = math.radians(ang)
    ux, uy = math.cos(a), math.sin(a)
    px, py = -uy, ux
    n = 14
    side1, side2 = [], []
    for i in range(n + 1):
        t = i / n
        w = W / 2 * math.sin(math.pi * t) ** 0.75
        side1.append((x + ux * L * t + px * w, y + uy * L * t + py * w))
        side2.append((x + ux * L * t - px * w, y + uy * L * t - py * w))
    pts = side1 + side2[::-1]
    c.poly(pts, fill=fill, outline=edge or LEAF_V, width=max(0.6, W * 0.07))
    c.line([(x + ux * L * 0.1, y + uy * L * 0.1), (x + ux * L * 0.85, y + uy * L * 0.85)], vein, max(0.5, W * 0.08))


def leaf_hem(c, x0, x1, y, L=12, W=8, ang=90):
    """Row of layered leaves hanging from y (the cloak's scalloped trim)."""
    step = W * 0.85
    x = x0 - W / 2
    i = 0
    while x < x1 + W:
        leaf(c, x + step / 2, y - 2, L * 0.9, W, ang + random.uniform(-10, 10), LEAF)
        x += step
        i += 1
    x = x0 - W / 2
    while x < x1 + W:
        leaf(c, x, y, L, W, ang + random.uniform(-8, 8), LEAF_L)
        x += step


def star(c, cx, cy, r, fill, outline=None, width=1, inner=0.45, rot=-90):
    pts = []
    for i in range(10):
        rr = r if i % 2 == 0 else r * inner
        a = math.radians(rot + i * 36)
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    c.poly(pts, fill=fill, outline=outline, width=width)


def brooch(c, cx, cy, r):
    """Gold-framed diamond badge with a neon green star (hat, cloak, quiver)."""
    d = [(cx, cy - r), (cx + r * 0.8, cy), (cx, cy + r), (cx - r * 0.8, cy)]
    c.poly(d, fill=GOLD, outline=GOLD_D, width=max(0.6, r * 0.12))
    d2 = [(cx, cy - r * 0.7), (cx + r * 0.55, cy), (cx, cy + r * 0.7), (cx - r * 0.55, cy)]
    c.poly(d2, fill=(14, 40, 30))
    c.glow(lambda g: star(g, cx, cy, r * 0.5, NEON_G), blur=max(0.8, r * 0.18))


def gold_trim(c, pts, w=2.2):
    c.line(pts, GOLD_D, w + 0.8)
    c.line(pts, GOLD, w)
    c.line([(x - 0.4, y - 0.4) for x, y in pts], GOLD_L, w * 0.3)


def lacing(c, xl, xr, y0, y1, step=8):
    c.rect(xl, y0, xr, y1, BLACK)
    y = y0 + 2
    while y + step <= y1:
        c.line([(xl, y), (xr, y + step)], LACE, 1.4)
        c.line([(xr, y), (xl, y + step)], LACE, 1.4)
        y += step
    y = y0 + 2
    while y <= y1:
        c.ell(xl, y, 1.4, 1.4, GOLD_L)
        c.ell(xr, y, 1.4, 1.4, GOLD_L)
        y += step


def chain(c, pts, r=0.9):
    for i, (x, y) in enumerate(pts):
        c.ell(x, y, r, r, GOLD if i % 2 else GOLD_L)


def strap(c, p0, p1, w, buckle_t=None):
    """Leather strap between two points with stitching and optional buckle."""
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    L = math.hypot(dx, dy)
    ux, uy = dx / L, dy / L
    px, py = -uy * w / 2, ux * w / 2
    pts = [(p0[0] + px, p0[1] + py), (p1[0] + px, p1[1] + py), (p1[0] - px, p1[1] - py), (p0[0] - px, p0[1] - py)]
    c.poly(pts, fill=LEATHER, outline=LEATHER_D, width=1)
    k = 0.32
    for sgn in (1, -1):
        a = (p0[0] + sgn * px * (1 - k * 2), p0[1] + sgn * py * (1 - k * 2))
        b = (p1[0] + sgn * px * (1 - k * 2), p1[1] + sgn * py * (1 - k * 2))
        c.line([a, b], LEATHER_L, 0.6)
    if buckle_t is not None:
        bx, by = p0[0] + dx * buckle_t, p0[1] + dy * buckle_t
        s = w * 0.75
        box = [(bx + (-ux - uy) * s * 0.6, by + (-uy + ux) * s * 0.6),
               (bx + (ux - uy) * s * 0.6, by + (uy + ux) * s * 0.6),
               (bx + (ux + uy) * s * 0.6, by + (uy - ux) * s * 0.6),
               (bx + (-ux + uy) * s * 0.6, by + (-uy - ux) * s * 0.6)]
        c.poly(box, fill=None, outline=GOLD, width=1.6)


def studs(c, x0, x1, y, n):
    for i in range(n):
        x = x0 + (x1 - x0) * (i + 0.5) / n
        c.ell(x, y, 1.1, 1.1, GOLD_L)


# ------------------------------------------------------ torso faces
def torso_front():
    c = C(128, 128)
    fabric(c, [(0, 0), (128, 0), (128, 128), (0, 128)], BODICE,
           folds=[[(47, 44), (46, 110)], [(81, 44), (82, 110)]], lit=(40, 80, 66), dark=BODICE_D)
    # sweetheart neckline skin
    neck = [(40, 0), (88, 0), (91, 18), (85, 37), (72, 43), (64, 39), (56, 43), (43, 37), (37, 18)]
    c.poly(neck, fill=SKIN)
    sh = c.layer()
    sh.ell(64, 4, 20, 8, rgba(SKIN_D, 160))
    c.comp(sh, blur=3)
    gold_trim(c, [(43, 37), (56, 43), (64, 39), (72, 43), (85, 37)], 1.6)
    # gold chain with green gem pendant
    chain(c, bez((47, 2), (64, 34), (81, 2), 26))
    gem = [(64, 20), (68, 26), (64, 33), (60, 26)]
    c.poly(gem, fill=GOLD_D)
    c.glow(lambda g: g.poly([(64, 22), (66.6, 26), (64, 31), (61.4, 26)], fill=GEM), 1.2)
    # corset: seams, lacing, boning
    for x in (46, 82):
        c.line([(x, 42), (x, 110)], GOLD_D, 0.8)
    for x in (38, 54, 74, 90):
        c.line([(x, 46), (x, 108)], BODICE_D, 0.8)
    lacing(c, 58, 70, 44, 110)
    # quiver strap from the character's left shoulder to right hip
    strap(c, (112, -4), (18, 122), 11, buckle_t=0.62)
    # belt
    c.rect(0, 110, 128, 128, LEATHER)
    c.line([(0, 110.5), (128, 110.5)], LEATHER_D, 1.2)
    c.line([(0, 127), (128, 127)], LEATHER_D, 1.2)
    c.line([(0, 113), (128, 113)], LEATHER_L, 0.5)
    c.line([(0, 124.5), (128, 124.5)], LEATHER_L, 0.5)
    c.poly([(56, 111), (72, 111), (72, 127), (56, 127)], outline=GOLD, width=2)
    c.line([(64, 112), (64, 126)], GOLD_L, 1.2)
    # cloak panels with gold trim, leaf trim and star brooches
    for sgn in (1, -1):
        X = (lambda x: x) if sgn == 1 else (lambda x: 128 - x)
        pts = [(X(0), 0), (X(40), 0), (X(37), 18), (X(31), 50), (X(27), 128), (X(0), 128)]
        fabric(c, pts, CLOAK, folds=[[(X(10), 10), (X(8), 128)], [(X(20), 30), (X(18), 128)]])
        gold_trim(c, [(X(40), 0), (X(37), 18), (X(31), 50), (X(27), 128)])
        for i, y in enumerate(range(58, 128, 9)):
            x_edge = 31 - (y - 50) * 4 / 78
            leaf(c, X(x_edge - 4), y, 13, 8, 70 if sgn == 1 else 110, LEAF_L if i % 2 else LEAF)
        brooch(c, X(34), 20, 8)
    return c.out()


def torso_back(with_quiver=True):
    c = C(128, 128)
    fabric(c, [(0, 0), (128, 0), (128, 128), (0, 128)], CLOAK,
           folds=[[(18, 30), (14, 128)], [(42, 50), (40, 128)], [(86, 50), (88, 128)], [(110, 30), (114, 128)]])
    # draped hood with pointed tip
    hood = [(8, 0), (120, 0), (116, 14), (100, 30), (78, 42), (64, 56), (50, 42), (28, 30), (12, 14)]
    fabric(c, hood, CLOAK_L, folds=[[(40, 4), (56, 40)], [(88, 4), (72, 40)], [(64, 6), (64, 48)]],
           lit=(96, 160, 120), dark=CLOAK)
    gold_trim(c, [(12, 14), (28, 30), (50, 42), (64, 56), (78, 42), (100, 30), (116, 14)])
    if with_quiver:
        # strap: character's left shoulder (viewer-left from behind) to right hip
        strap(c, (16, -4), (110, 122), 11)
        # quiver along the strap, arrows pointing up-left
        ang = math.atan2(122 + 4, 110 - 16)
        ux, uy = math.cos(ang), math.sin(ang)
        px, py = -uy, ux
        cx, cy = 50, 50
        L, W = 78, 26
        a0 = (cx - ux * L / 2, cy - uy * L / 2)
        a1 = (cx + ux * L / 2, cy + uy * L / 2)
        # fletchings sticking out of the top
        for k, off in enumerate((-7, 0, 7)):
            bx, by = a0[0] + px * off, a0[1] + py * off
            tx, ty = bx - ux * 14, by - uy * 14
            c.line([(bx, by), (tx, ty)], LEATHER_D, 1.4)
            for sgn in (1, -1):
                c.poly([(tx, ty), (tx + ux * 9 + px * 4 * sgn, ty + uy * 9 + py * 4 * sgn),
                        (tx + ux * 11, ty + uy * 11)], fill=LEAF_L if k != 1 else NEON_G, outline=LEAF_V, width=0.6)
        q = [(a0[0] + px * W / 2, a0[1] + py * W / 2), (a1[0] + px * W * 0.4, a1[1] + py * W * 0.4),
             (a1[0] - px * W * 0.4, a1[1] - py * W * 0.4), (a0[0] - px * W / 2, a0[1] - py * W / 2)]
        c.poly(q, fill=LEATHER, outline=LEATHER_D, width=1.2)
        for t in (0.05, 0.93):
            p = (a0[0] + (a1[0] - a0[0]) * t, a0[1] + (a1[1] - a0[1]) * t)
            w = W / 2 * (1 - 0.2 * t)
            gold_trim(c, [(p[0] + px * w, p[1] + py * w), (p[0] - px * w, p[1] - py * w)], 2.4)
        c.line([(a0[0] + ux * 6 + px * 8, a0[1] + uy * 6 + py * 8), (a1[0] - ux * 6 + px * 7, a1[1] - uy * 6 + py * 7)], LEATHER_L, 0.8)
        brooch(c, cx + ux * 4, cy + uy * 4, 9)
    gold_trim(c, [(0, 113), (128, 113)], 1.8)
    leaf_hem(c, 0, 128, 114, L=13, W=9)
    return c.out()


def torso_side(side):
    c = C(64, 128)
    fabric(c, [(0, 0), (64, 0), (64, 128), (0, 128)], CLOAK, folds=[[(20, 10), (18, 128)], [(44, 10), (46, 128)]])
    gold_trim(c, [(0, 113), (64, 113)], 1.8)
    leaf_hem(c, 0, 64, 114, L=13, W=9)
    return c.out()


def torso_up():
    c = C(128, 64)
    fabric(c, [(0, 0), (128, 0), (128, 64), (0, 64)], CLOAK, folds=[[(20, 0), (24, 64)], [(108, 0), (104, 64)]])
    fabric(c, [(10, 0), (118, 0), (110, 22), (18, 22)], CLOAK_L, lit=(96, 160, 120), dark=CLOAK)
    gold_trim(c, [(18, 22), (110, 22)], 1.6)
    c.ell(64, 64, 24, 18, SKIN)
    strap(c, (100, 22), (112, 66), 11)
    return c.out()


def torso_down():
    c = C(128, 64)
    c.rect(0, 0, 128, 64, LEATHER_D)
    c.rect(0, 0, 128, 10, LEATHER)
    return c.out()


# ------------------------------------------------------ arm faces
def arm_face(face, outer):
    c = C(64, 128)
    fabric(c, [(0, 0), (64, 0), (64, 60), (0, 60)], CLOAK, folds=[[(16, 0), (14, 60)], [(46, 0), (48, 60)]])
    # black glove / gauntlet
    fabric(c, [(0, 60), (64, 60), (64, 128), (0, 128)], BLACK, folds=[[(32, 64), (32, 128)]], lit=BLACK_L, dark=(4, 4, 8))
    # leather bracer
    c.rect(0, 80, 64, 101, LEATHER)
    c.line([(0, 80.5), (64, 80.5)], LEATHER_D, 1.2)
    c.line([(0, 100.5), (64, 100.5)], LEATHER_D, 1.2)
    studs(c, 0, 64, 84, 5)
    studs(c, 0, 64, 97, 5)
    if face == outer:  # neon arrow glyph, echoing the bow markings
        c.glow(lambda g: [g.line([(22, 94), (32, 86), (42, 94)], NEON_G, 2.2), g.line([(32, 86), (32, 96)], NEON_G, 1.8)], 1.2)
    if face == "F":  # knuckle seams
        for x in (16, 28, 40, 52):
            c.line([(x, 114), (x, 128)], BLACK_L, 0.8)
    gold_trim(c, [(0, 58), (64, 58)], 1.8)
    leaf_hem(c, 0, 64, 59, L=12, W=8)
    return c.out()


def arm_up():
    c = C(64, 64)
    fabric(c, [(0, 0), (64, 0), (64, 64), (0, 64)], CLOAK, folds=[[(20, 0), (20, 64)], [(44, 0), (44, 64)]])
    return c.out()


def hand_down():
    c = C(64, 64)
    c.rect(0, 0, 64, 64, BLACK)
    return c.out()


# ------------------------------------------------------ leg faces (pants)
def leg_face(face, outer):
    c = C(64, 128)
    fabric(c, [(0, 0), (64, 0), (64, 74), (0, 74)], BLACK_L, folds=[[(20, 0), (22, 74)], [(44, 0), (42, 74)]], lit=(80, 74, 100), dark=BLACK)
    # boots
    fabric(c, [(0, 74), (64, 74), (64, 128), (0, 128)], LEATHER, folds=[[(14, 80), (16, 120)], [(50, 80), (48, 120)]], lit=LEATHER_L, dark=LEATHER_D)
    c.rect(0, 74, 64, 80, LEATHER_D)
    gold_trim(c, [(0, 74), (64, 74)], 1.8)
    gold_trim(c, [(0, 80), (64, 80)], 1.0)
    if face == "F":
        lacing(c, 27, 37, 83, 118, step=7)
    c.rect(0, 120, 64, 128, BLACK)
    c.line([(0, 120), (64, 120)], GOLD_D, 0.8)
    if face in ("B", outer):  # cloak hem hanging behind the legs
        fabric(c, [(0, 0), (64, 0), (64, 30), (0, 30)], CLOAK, folds=[[(18, 0), (16, 30)], [(46, 0), (48, 30)]])
        gold_trim(c, [(0, 29), (64, 29)], 1.6)
        leaf_hem(c, 0, 64, 30, L=13, W=9)
    return c.out()


def leg_up():
    c = C(64, 64)
    c.rect(0, 0, 64, 64, BLACK_L)
    return c.out()


def sole():
    c = C(64, 64)
    c.rect(0, 0, 64, 64, BLACK)
    c.rect(4, 4, 60, 60, (26, 22, 30))
    return c.out()


# ------------------------------------------------------ templates
def paste(tpl, region, im):
    x, y, w, h = region
    assert im.size == (w, h), (im.size, region)
    tpl.alpha_composite(im, (x, y))


def torso_faces():
    return {"F": torso_front(), "B": torso_back(), "R": torso_side("R"), "L": torso_side("L"),
            "U": torso_up(), "D": torso_down()}


def build_shirt(tf):
    tpl = Image.new("RGBA", TEMPLATE_SIZE, (0, 0, 0, 0))
    for k, im in tf.items():
        paste(tpl, TORSO[k], im)
    for limb, outer in ((LIMB_R, "R"), (LIMB_L, "L")):
        for f in "FBLR":
            paste(tpl, limb[f], arm_face(f, outer))
        paste(tpl, limb["U"], arm_up())
        paste(tpl, limb["D"], hand_down())
    return tpl


def build_pants(tf):
    tpl = Image.new("RGBA", TEMPLATE_SIZE, (0, 0, 0, 0))
    # Pants torso only shows when no shirt is worn; keep it matching the shirt.
    for k, im in tf.items():
        paste(tpl, TORSO[k], im)
    for limb, outer in ((LIMB_R, "R"), (LIMB_L, "L")):
        for f in "FBLR":
            paste(tpl, limb[f], leg_face(f, outer))
        paste(tpl, limb["U"], leg_up())
        paste(tpl, limb["D"], sole())
    return tpl


# ------------------------------------------------------ face decal
def eye(c, cx, cy, flip, k=1.3):
    s = -1 if flip else 1

    def P(dx, dy):
        return (cx + dx * k * s, cy + dy * k)
    # sclera
    c.ell(cx, cy + 6 * k, 50 * k, 58 * k, fill=(255, 250, 255))
    # iris gradient
    ir = c.layer()
    for i in range(40):
        t = i / 39
        ir.ell(cx, cy + 8 * k, 40 * k * (1 - t * 0.35), 52 * k * (1 - t * 0.3), fill=lerp(EYE_D, EYE_L, t * 0.9) + (255,))
    ir.ell(cx, cy - 4 * k, 40 * k, 34 * k, fill=rgba(EYE_D, 110))
    ir.ell(cx, cy + 10 * k, 16 * k, 24 * k, fill=rgba(EYE_D, 255))
    mask = c.layer()
    mask.ell(cx, cy + 6 * k, 50 * k, 58 * k, fill=(255, 255, 255, 255))
    c.comp(ir, mask=mask)
    c.ell(cx, cy + 8 * k, 40 * k, 52 * k, outline=EYE_D, width=3 * k)
    # highlights and sparkle
    c.ell(*P(-14, -14), 13 * k, 16 * k, fill=(255, 255, 255))
    c.ell(*P(16, 30), 6 * k, 6 * k, fill=(255, 255, 255))
    star(c, *P(12, 2), 8 * k, (255, 225, 255), inner=0.3)
    # upper lash line with outer flick
    lash = [P(-54, -14), P(-30, -48), P(10, -56), P(44, -44), P(66, -38), P(54, -30), P(40, -34),
            P(8, -44), P(-28, -38), P(-50, -6)]
    c.poly(lash, fill=(22, 12, 40))
    c.line(bez(P(-40, 54), P(0, 70), P(38, 58)), (60, 30, 90), 3 * k)


def build_face():
    c = C(512, 512, s=2)
    blush = c.layer()
    blush.ell(118, 372, 46, 22, fill=(255, 120, 200, 110))
    blush.ell(394, 372, 46, 22, fill=(255, 120, 200, 110))
    c.comp(blush, blur=8)
    eye(c, 156, 236, flip=False)
    eye(c, 356, 236, flip=True)
    # forehead gem
    c.poly([(256, 146), (272, 168), (256, 194), (240, 168)], fill=GOLD_D)
    c.glow(lambda g: g.poly([(256, 153), (267, 168), (256, 187), (245, 168)], fill=(170, 90, 255)), 4)
    c.ell(252, 162, 3, 4, fill=(245, 225, 255))
    # visor strap across the nose bridge
    band = bez((70, 346), (256, 328), (442, 346), 30)
    c.line(band, (10, 8, 14), 12)
    c.line([(x, y - 4) for x, y in band], (60, 56, 70), 2)
    for x, y in (band[0], band[15], band[-1]):
        c.poly([(x - 8, y - 9), (x + 8, y - 9), (x + 8, y + 9), (x - 8, y + 9)], fill=GOLD, outline=GOLD_D, width=2)
    # mouth: small open smile, blue lips, tongue
    c.poly(bez((222, 392), (256, 436), (290, 392), 20), fill=(60, 16, 50))
    c.poly(bez((238, 410), (256, 434), (274, 410), 12), fill=(90, 190, 240))
    c.line(bez((218, 390), (256, 402), (294, 390), 16), LIP, 6)
    c.line(bez((230, 420), (256, 440), (282, 420), 16), LIP, 3.5)
    return c.out(noise=0)


# ------------------------------------------------------ preview renders
def shade(im):
    a = np.asarray(im).astype(np.float32)
    h, w = a.shape[:2]
    xs = np.linspace(0, 1, w)
    ys = np.linspace(0, 1, h)
    f = (0.78 + 0.22 * np.sin(np.pi * xs))[None, :] * (1.04 - 0.08 * ys)[:, None]
    a[..., :3] = np.clip(a[..., :3] * f[..., None], 0, 255)
    return Image.fromarray(a.astype(np.uint8))


def crop(tpl, region):
    x, y, w, h = region
    return tpl.crop((x, y, x + w, y + h))


def put_part(c, tex, x, y, w, h):
    s = c.s
    im = shade(tex.resize((w * s, h * s), Image.BICUBIC))
    c.im.alpha_composite(im, (x * s, y * s))
    c.d.rectangle([x * s, y * s, (x + w) * s - 1, (y + h) * s - 1], outline=(6, 4, 12), width=2 * s)


def background(c, title):
    W, H = c.w, c.h
    arr = np.zeros((H * c.s, W * c.s, 4), np.uint8)
    ys = np.linspace(0, 1, H * c.s)[:, None]
    arr[..., 0] = (8 + 18 * ys)
    arr[..., 1] = 5
    arr[..., 2] = (14 + 24 * ys)
    arr[..., 3] = 255
    c.im = Image.fromarray(arr)
    c.d = ImageDraw.Draw(c.im)
    g = c.layer()
    g.ell(W / 2, 900, 420, 620, fill=(180, 30, 170, 70))
    c.comp(g, blur=90)
    rnd = random.Random(3)
    for _ in range(60):
        x, y = rnd.uniform(20, W - 20), rnd.uniform(120, H - 60)
        r = rnd.uniform(1.5, 5)
        col = rnd.choice([NEON_M, (255, 200, 255), NEON_G, (150, 120, 255)])
        c.glow(lambda gg, x=x, y=y, r=r, col=col: star(gg, x, y, r * 2, col, inner=0.25), 2)
    for yy in (1455, 1465):
        c.line([(120, yy), (W - 120, yy)], rgba(NEON_M, 90), 2)
    c.glow(lambda gg: gg.ell(W / 2, 1452, 260, 26, outline=NEON_M, width=3), 6)
    font = ImageFont.truetype(FONT, 46 * c.s)
    small = ImageFont.truetype(FONT, 24 * c.s)
    c.d.text((W / 2 * c.s, 60 * c.s), "NEON RANGER", font=font, fill=(255, 220, 250), anchor="mm")
    c.d.text((W / 2 * c.s, 110 * c.s), title, font=small, fill=NEON_M, anchor="mm")


def halo(c):
    def ring(g):
        g.ell(540, 470, 150, 34, outline=NEON_M, width=10)
    c.glow(ring, 10)
    c.ell(540, 470, 150, 34, outline=(255, 200, 250), width=2.5)


def ears(c):
    for sgn in (1, -1):
        X = (lambda x: x) if sgn == 1 else (lambda x: 1080 - x)
        c.poly([(X(446), 596), (X(418), 494), (X(496), 560)], fill=EAR, outline=HAIR_D, width=3)
        c.poly([(X(452), 580), (X(430), 512), (X(482), 560)], fill=EAR_IN)
        for i in range(6):
            x0 = X(452 + i * 5)
            c.line([(x0, 584), (X(446 + i * 6), 556 - i * 2)], FLUFF, 3)
        c.line([(X(418), 494), (X(446), 596)], HAIR_RIM, 2)


def arrows_peek(c, x, flip=False):
    for i, dx in enumerate((0, 16, 32)):
        xx = x + (dx if not flip else -dx)
        c.line([(xx, 830), (xx - (18 if not flip else -18), 748 - i * 6)], LEATHER_D, 4)
        tx, ty = xx - (18 if not flip else -18), 748 - i * 6
        for sgn in (1, -1):
            c.poly([(tx, ty), (tx + 10 * sgn, ty + 22), (tx + (3 if not flip else -3), ty + 30)],
                   fill=NEON_G if i == 1 else LEAF_L, outline=LEAF_V, width=1.5)


def hat(c, back=False):
    flip = (lambda x: 1080 - x) if back else (lambda x: x)
    crown = [(432, 634), (452, 576), (492, 534), (544, 514), (602, 526), (640, 568), (652, 634)]
    fabric(c, [(flip(x), y) for x, y in crown], CLOAK, folds=[[(flip(500), 560), (flip(520), 630)], [(flip(590), 548), (flip(575), 630)]])
    c.poly([(flip(x), y) for x, y in crown], outline=CLOAK_D, width=3)
    brim = [(416, 652), (424, 620), (540, 632), (656, 614), (668, 648), (540, 660)]
    fabric(c, [(flip(x), y) for x, y in brim], CLOAK_L, lit=(110, 170, 130), dark=CLOAK_D)
    gold_trim(c, [(flip(424), 620), (flip(540), 632), (flip(656), 614)], 4)
    gold_trim(c, [(flip(416), 652), (flip(540), 660), (flip(668), 648)], 3)
    # magenta feather sweeping back
    base, tip = (flip(588), 604), (flip(760), 452)
    spine = bez(base, (flip(690), 560), tip, 30)
    for i, (x, y) in enumerate(spine[2:-1]):
        t = i / len(spine)
        L = 34 * math.sin(math.pi * min(1, t * 1.1))
        c.line([(x, y), (x + (L if not back else -L) * 0.4, y - L)], FEATHER, 5)
        c.line([(x, y), (x + (L if not back else -L) * 0.9, y + L * 0.2)], FEATHER_L if i % 3 else FEATHER, 4)
    c.line(spine, (255, 190, 235), 3)
    if not back:
        brooch(c, 500, 616, 22)


def hair_back(c, full=False):
    top = [(412, 700), (414, 626), (448, 578), (540, 560), (632, 578), (666, 626), (668, 700)]
    jag = [(672, 790), (660, 842), (644, 812), (628, 850), (610, 816), (590, 846), (570, 818), (540, 842),
           (510, 818), (490, 846), (470, 816), (452, 850), (436, 812), (420, 842), (408, 790)]
    pts = top + jag
    fabric(c, pts, HAIR, folds=[[(460, 600), (450, 830)], [(540, 580), (540, 830)], [(620, 600), (630, 830)]],
           lit=HAIR_L, dark=HAIR_D)
    c.line(top + [(672, 790), (660, 842)], HAIR_RIM, 3)
    c.line([(408, 790), (412, 700), (414, 626)], HAIR_RIM, 3)
    if full:
        for x0 in (470, 510, 570, 610):
            c.line(bez((x0, 600), (x0 + 10, 720), (x0 - 6, 830), 16), HAIR_L, 3)


def hair_front(c):
    bangs = [(440, 646), (458, 600), (540, 588), (622, 600), (640, 646), (640, 684), (624, 664), (608, 690),
             (588, 662), (568, 686), (550, 660), (530, 688), (512, 660), (492, 686), (474, 662), (458, 690), (440, 676)]
    fabric(c, bangs, HAIR, folds=[[(500, 600), (495, 680)], [(580, 600), (585, 680)]], lit=HAIR_L, dark=HAIR_D)
    for x0 in (478, 532, 596):
        c.line(bez((x0, 646), (x0 + 6, 660), (x0 - 2, 676), 10), HAIR_L, 3)
    for sgn in (1, -1):
        X = (lambda x: x) if sgn == 1 else (lambda x: 1080 - x)
        lock = [(X(444), 640), (X(430), 700), (X(426), 776), (X(440), 830), (X(452), 796), (X(460), 730), (X(466), 660)]
        fabric(c, lock, HAIR, folds=[[(X(446), 660), (X(440), 820)]], lit=HAIR_L, dark=HAIR_D)
        c.line([(X(430), 700), (X(426), 776), (X(440), 830)], HAIR_RIM, 3)


def bow(c, back=False):
    X = (lambda x: x) if not back else (lambda x: 1080 - x)
    top, bot = (X(236), 760), (X(236), 1440)
    limb = bez(top, (X(120), 1100), bot, 40)
    limb = [(X(236) + (x - X(236)) * 1.0, y) for x, y in limb]
    # recurve tips
    limb = [(X(252), 740)] + limb + [(X(252), 1460)]

    def string(g):
        g.line([(X(250), 744), (X(250), 1456)], NEON_M, 3)
    c.glow(string, 6)
    c.line(limb, (8, 6, 12), 16)
    c.line(limb, (38, 32, 50), 10)
    # neon green arrow glyphs on the limbs
    for t in (0.18, 0.3, 0.7, 0.82):
        x, y = limb[int(t * (len(limb) - 1))]

        def glyph(g, x=x, y=y):
            g.line([(x - 7, y + 8), (x, y), (x + 7, y + 8)], NEON_G, 3)
            g.line([(x, y), (x, y + 14)], NEON_G, 2.5)
        c.glow(glyph, 3)
    gx, gy = limb[len(limb) // 2]
    c.rect(gx - 9, gy - 26, gx + 9, gy + 26, LEATHER)
    for yy in range(int(gy) - 22, int(gy) + 24, 8):
        c.line([(gx - 9, yy), (gx + 9, yy + 4)], GOLD_D, 2)


def render(shirt, pants, face, back):
    c = C(1080, 1600, s=2)
    background(c, "BACK VIEW" if back else "FRONT VIEW")
    halo(c)
    if back:
        arrows_peek(c, 392, flip=False)
    else:
        arrows_peek(c, 664, flip=False)
    if back:
        bow(c, back=True)
    hair_back(c)
    ears(c)
    # body parts: (template, region) per slot, left to right as seen by the viewer
    if not back:
        slots = [(shirt, LIMB_R["F"], 220, 810), (shirt, TORSO["F"], 380, 810), (shirt, LIMB_L["F"], 700, 810),
                 (pants, LIMB_R["F"], 380, 1130), (pants, LIMB_L["F"], 540, 1130)]
    else:
        slots = [(shirt, LIMB_L["B"], 220, 810), (shirt, TORSO["B"], 380, 810), (shirt, LIMB_R["B"], 700, 810),
                 (pants, LIMB_L["B"], 380, 1130), (pants, LIMB_R["B"], 540, 1130)]
    for tpl, reg, x, y in slots:
        w = 320 if reg[2] == 128 else 160
        put_part(c, crop(tpl, reg), x, y, w, 320)
    # neck + head
    c.rect(514, 790, 566, 812, SKIN_D)
    head = c.layer()
    head.d.rounded_rectangle([444 * 2, 610 * 2, 636 * 2, 802 * 2], radius=44 * 2, fill=rgba(SKIN, 255))
    head.d.rounded_rectangle([444 * 2, 610 * 2, 636 * 2, 802 * 2], radius=44 * 2, outline=(90, 60, 100, 255), width=4)
    c.comp(head)
    if back:
        hair_back(c, full=True)
    else:
        fc = face.resize((192 * 2, 192 * 2), Image.LANCZOS)
        c.im.alpha_composite(fc, (444 * 2, 616 * 2))
        hair_front(c)
    hat(c, back=back)
    if not back:
        bow(c)
    return c.out(noise=0)


def swatch_row(c, x, y, cols, size=56):
    font = ImageFont.truetype(FONT, 15 * c.s)
    for i, (name, col) in enumerate(cols):
        xx = x + (i % 6) * (size + 70)
        yy = y + (i // 6) * (size + 44)
        c.d.rounded_rectangle([xx * c.s, yy * c.s, (xx + size) * c.s, (yy + size) * c.s], radius=10 * c.s,
                              fill=col + (255,), outline=(255, 255, 255, 120), width=c.s)
        c.d.text(((xx + size / 2) * c.s, (yy + size + 12) * c.s), name, font=font, fill=(235, 220, 245), anchor="mm")
        c.d.text(((xx + size / 2) * c.s, (yy + size + 30) * c.s), "#%02X%02X%02X" % col, font=font,
                 fill=(170, 150, 190), anchor="mm")


def build_sheet(front, back, shirt, pants, face):
    W, H = 1600, 2500
    c = C(W, H, s=1, bg=(10, 6, 18, 255))
    big = ImageFont.truetype(FONT, 54)
    mid = ImageFont.truetype(FONT, 28)
    sm = ImageFont.truetype(FONT, 20)
    c.d.text((W / 2, 70), "NEON RANGER  -  Roblox Character Sheet", font=big, fill=(255, 220, 250), anchor="mm")
    c.d.text((W / 2, 125), "Classic Shirt + Pants + Face decal  |  accessories listed below", font=sm,
             fill=NEON_M, anchor="mm")
    fw = 760
    fh = int(1600 * fw / 1080)
    c.im.alpha_composite(front.resize((fw, fh), Image.LANCZOS), (30, 160))
    c.im.alpha_composite(back.resize((fw, fh), Image.LANCZOS), (810, 160))
    y = 160 + fh + 30
    checker = Image.new("RGBA", (585, 559), (40, 34, 52, 255))
    for (tpl, label, x) in ((shirt, "SHIRT TEMPLATE (upload file)", 60), (pants, "PANTS TEMPLATE (upload file)", 955)):
        bg = checker.copy()
        bg.alpha_composite(tpl)
        c.im.alpha_composite(bg, (x, y + 40))
        c.d.text((x + 292, y + 18), label, font=mid, fill=(255, 220, 250), anchor="mm")
    fbg = Image.new("RGBA", (300, 300), SKIN + (255,))
    fbg.alpha_composite(face.resize((300, 300), Image.LANCZOS))
    c.im.alpha_composite(fbg, (650, y + 60))
    c.d.text((800, y + 18), "FACE DECAL", font=mid, fill=(255, 220, 250), anchor="mm")
    c.d.text((800, y + 385), "(Studio use)", font=sm, fill=(170, 150, 190), anchor="mm")
    y += 640
    c.d.text((60, y), "PALETTE", font=mid, fill=(255, 220, 250))
    swatch_row(c, 60, y + 50, [("Hair", HAIR), ("Hair light", HAIR_L), ("Hair rim", HAIR_RIM), ("Cloak", CLOAK),
                               ("Bodice", BODICE), ("Leaf", LEAF_L), ("Gold", GOLD), ("Leather", LEATHER),
                               ("Glove", BLACK), ("Skin", SKIN), ("Eyes", EYE), ("Neon magenta", NEON_M)])
    x2 = 860
    c.d.text((x2, y), "3D ACCESSORIES (need 3D models)", font=mid, fill=(255, 220, 250))
    lines = ["- Blue bob hair w/ bangs + side locks", "- Blue-violet cat ears, pink inner fluff",
             "- Green Robin Hood cap, gold trim,", "   green-star badge, magenta feather",
             "- Neon magenta halo", "- Dark recurve bow, neon green glyphs,", "   glowing magenta string",
             "- Arrow fletchings above quiver (optional)", "", "Quiver, straps, brooches, leaf trim, corset,",
             "necklace + gloves are painted into the Shirt."]
    for i, t in enumerate(lines):
        c.d.text((x2, y + 50 + i * 30), t, font=sm, fill=(225, 210, 240))
    c.d.text((W / 2, H - 40), "Legs/boots are extrapolated (reference image is cropped at the waist).",
             font=sm, fill=(170, 150, 190), anchor="mm")
    return c.im.convert("RGB")


def main():
    os.makedirs(UPLOAD, exist_ok=True)
    os.makedirs(PREVIEW, exist_ok=True)
    tf = torso_faces()
    shirt = build_shirt(tf)
    random.seed(11)
    pants = build_pants(tf)
    face = build_face()
    shirt.save(os.path.join(UPLOAD, "NeonRanger_Shirt_585x559.png"))
    pants.save(os.path.join(UPLOAD, "NeonRanger_Pants_585x559.png"))
    face.save(os.path.join(UPLOAD, "NeonRanger_Face_512.png"))
    front = render(shirt, pants, face, back=False)
    back = render(shirt, pants, face, back=True)
    front.convert("RGB").save(os.path.join(PREVIEW, "NeonRanger_Front.png"))
    back.convert("RGB").save(os.path.join(PREVIEW, "NeonRanger_Back.png"))
    build_sheet(front, back, shirt, pants, face).save(os.path.join(PREVIEW, "NeonRanger_Character_Sheet.png"))
    print("done")


if __name__ == "__main__":
    main()
