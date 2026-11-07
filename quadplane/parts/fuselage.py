"""Fuselage pod: lofted rounded-rectangle shell hung under the wing centre section.

- Wing saddle: the wing root's lower surface is cut into the pod top; 2 x M4 heat-set
  inserts take the wing bolts.
- Split into nose and rear halves (each ~310 mm) joined by a glued internal collar.
- Battery bay in the nose with a bottom hatch; the battery slides fore-aft on the floor to set CG.
- Rear firewall carries the pusher motor (cross pattern M3).
- Camera cradle (TPU) under the nose for the Insta360 GO 3S.
Print: PETG (rear, firewall loads) / LW-PLA or PETG (nose), 2 walls, 10% gyroid.
"""

import numpy as np
from build123d import (Box, Cylinder, Face, Part, Plane, Pos, RectangleRounded, Rot, Vector,
                       loft, mirror)

from quadplane import geometry as G
from quadplane import hardware as HW
from quadplane import printer
from quadplane.params import AIRCRAFT as AC, mm

MATERIAL = printer.PETG
F = AC.fuselage
WALL = 1.2
X_SPLIT = -0.073
HATCH = (0.20, -0.04, 0.072)  # x_front, x_rear, width (m)


def _profile(xs):
    """Section (width, height, z-centre) vs x, all m. Top stays at z_top over the wing."""
    L = F.x_nose - F.x_tail
    s = (F.x_nose - xs) / L  # 0 at nose, 1 at tail
    nose = np.sqrt(np.clip(1 - ((0.22 - np.minimum(s, 0.22)) / 0.22) ** 2, 0.05, 1))
    tail = 1 - 0.58 * np.clip((s - 0.62) / 0.38, 0, 1) ** 1.3
    f = np.minimum(nose, tail)
    w = F.width * np.maximum(f, 0.32)
    h = F.height * np.maximum(f, 0.40)
    z_top = F.z_top - (1 - f) * 0.5 * (F.height - h) * 0  # keep the top flat on the wing
    zc = np.where(s > 0.62, AC.pusher.z_thrust * (s - 0.62) / 0.38 + (z_top - h / 2) * (1 - (s - 0.62) / 0.38),
                  z_top - h / 2)
    return w, h, zc


def _loft(inset_mm: float, x_from: float, x_to: float, n: int = 14) -> Part:
    xs = np.linspace(x_from, x_to, n)
    w, h, zc = _profile(xs)
    faces = []
    for x, wi, hi, z in zip(xs, w, h, zc):
        ww, hh = mm(wi) - 2 * inset_mm, mm(hi) - 2 * inset_mm
        r = min(ww, hh) * 0.35
        pl = Plane(origin=(mm(x), 0, mm(z)), x_dir=(0, 1, 0), z_dir=(-1, 0, 0))
        faces.append(pl * RectangleRounded(ww, hh, r))
    return Part(loft(faces, ruled=False))


def pod_shell() -> Part:
    outer = _loft(0.0, F.x_nose, F.x_tail)
    inner = _loft(WALL, F.x_nose - 0.004, F.x_tail + 0.004)
    shell = outer - inner
    # wing saddle: cut the wing root (both halves) out of the pod top
    wing_root = G.wing_solid(0.0, 0.08)
    wing_root += mirror(wing_root, about=Plane.XZ)
    shell -= wing_root
    # saddle: two longitudinal rails under the wing + bolt bosses for the M4 wing bolts
    saddle = None
    for y in (mm(F.width) / 2 - 5, -mm(F.width) / 2 + 5):
        r = Pos(mm(-0.12), y, mm(F.z_top) - 5) * Box(mm(0.22), 6, 10)
        saddle = r if saddle is None else saddle + r
    for x in (-25.0, mm(-0.80 * AC.wing.root_chord)):
        for y in (30.0, -30.0):
            saddle += Pos(x, y, mm(F.z_top) - 7) * Cylinder(6.0, 14)
    saddle -= wing_root
    shell += saddle & outer
    for x in (-25.0, mm(-0.80 * AC.wing.root_chord)):
        for y in (30.0, -30.0):
            shell -= Pos(x, y, mm(F.z_top) - 8) * Cylinder(HW.M3_INSERT_HOLE / 2 + 0.6, 14)  # M4 insert
    # pusher firewall (closed end) with motor pattern and centre hole
    xf = mm(F.x_tail)
    zt = mm(AC.pusher.z_thrust)
    wall = Pos(xf + 1.5, 0, zt) * Box(3.0, 60, 60)
    shell += wall & outer
    a, b = HW.X2820_BOLT_PATTERN
    for dy, dz in ((a / 2, 0), (-a / 2, 0), (0, b / 2), (0, -b / 2)):
        shell -= Pos(xf + 1.5, dy, zt + dz) * (Rot(0, 90, 0) * Cylinder(1.7, 10))
    shell -= Pos(xf + 1.5, 0, zt) * (Rot(0, 90, 0) * Cylinder(5.0, 10))
    # bottom hatch opening
    hx0, hx1, hw = HATCH
    shell -= Pos(mm((hx0 + hx1) / 2), 0, mm(F.z_top - F.height)) * Box(mm(hx0 - hx1), mm(hw), 40)
    # cooling / wiring holes in the rear cone (ESC air)
    shell -= Pos(mm(-0.32), 0, mm(F.z_top - F.height) + 5) * Box(30, 12, 20)
    return shell


def hatch() -> Part:
    hx0, hx1, hw = HATCH
    outer = _loft(0.0, F.x_nose, F.x_tail)
    inner = _loft(WALL, F.x_nose - 0.004, F.x_tail + 0.004)
    shell = outer - inner
    cut = Pos(mm((hx0 + hx1) / 2), 0, mm(F.z_top - F.height)) * Box(mm(hx0 - hx1) - 0.6, mm(hw) - 0.6, 40)
    h = shell & cut
    # lip strips that sit under the opening edges
    for y in (mm(hw) / 2 - 2, -mm(hw) / 2 + 2):
        h += Pos(mm((hx0 + hx1) / 2), y, mm(F.z_top - F.height) + WALL + 2.5) * Box(mm(hx0 - hx1) - 20, 8, 1.6)
    return h


def camera_cradle() -> Part:
    L, Wd, H = HW.GO3S_SIZE
    x0 = mm(F.x_nose) - 30 - L / 2
    w_, h_, zc_ = _profile(np.array([x0 / 1000]))
    zb = mm(zc_[0] - h_[0] / 2) + 1.0  # pod bottom at the cradle station (+1 mm embed for gluing)
    body = Pos(x0, 0, zb - H / 2 - 2) * Box(L + 6, Wd + 6, H + 4)
    body -= Pos(x0 + 3, 0, zb - H / 2 - 2) * Box(L + 6, Wd + 0.4, H + 0.4)  # pocket, open at the front
    body -= Pos(x0, 0, zb - H - 3) * Box(L - 14, Wd - 8, 6)  # bottom window (button / SD access)
    for dx in (-L / 3, L / 3):
        body -= Pos(x0 + dx, 0, zb) * Cylinder(1.7, 12)
    return body


def make() -> dict[str, Part]:
    shell = pod_shell()
    split = Plane.YZ.offset(mm(X_SPLIT))
    from build123d import Keep, split as bsplit
    nose = bsplit(shell, bisect_by=split, keep=Keep.TOP)
    rear = bsplit(shell, bisect_by=split, keep=Keep.BOTTOM)
    # joining collar: separate ring glued 10 mm into each half
    w, h, zc = _profile(np.array([X_SPLIT]))
    pl = Plane(origin=(mm(X_SPLIT), 0, mm(zc[0])), x_dir=(0, 1, 0), z_dir=(-1, 0, 0))
    ww, hh = mm(w[0]) - 2 * WALL - 0.4, mm(h[0]) - 2 * WALL - 0.4
    from build123d import extrude
    collar = extrude(pl * RectangleRounded(ww, hh, min(ww, hh) * 0.35), amount=10, both=True)
    collar -= extrude(pl * RectangleRounded(ww - 3.2, hh - 3.2, min(ww, hh) * 0.3), amount=11, both=True)
    return {"fuselage_nose": nose, "fuselage_rear": rear, "fuselage_collar": collar, "battery_hatch": hatch(),
            "camera_cradle": camera_cradle()}


def build() -> dict[str, Part]:
    out = {}
    for k, v in make().items():
        if k == "fuselage_nose":
            out[k] = G.bed_place(v, rot=(0, -90, 0))  # stand on the split face
        elif k == "fuselage_rear":
            out[k] = G.bed_place(v, rot=(0, 90, 0))
        else:
            out[k] = G.bed_place(v)
    return out


_ = (Face, Vector)
