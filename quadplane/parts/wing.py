"""Wing: 3 segments per side (root to the boom, then mid and tip; printed span-up),
plus one aileron per side.

Features: main-spar bore (y 0 -> 0.25 m), coaxial 10 mm tip-tube bore (0.13 -> 0.63 m),
aileron cut-out with 1 mm hinge gap, aileron servo pocket (EMAX ES08MD II class, on its side),
2 x M4 wing-bolt holes in the root segment.
Print: LW-PLA, 1-2 walls, 0-3% gyroid infill (slicer turns the solid into a light shell).
"""

from build123d import Box, Cylinder, Mode, Part, Pos, Rot, mirror, Plane

from quadplane import geometry as G
from quadplane.lib.aero import loft_sections
from quadplane.params import AIRCRAFT as AC, mm
from quadplane import printer

MATERIAL = printer.LWPLA
W = AC.wing
Y_ROOT, Y_KINK, Y_MID, Y_TIP = G.WING_STATIONS
TIP_TUBE_START, TIP_TUBE_END = W.tip_spar_start, W.semi_span - 0.02
HINGE_GAP = 1.0  # mm
SERVO = (24.0, 22.0, 12.5)  # pocket L x W x depth (mm): ES08MD II lying on its side (the wing is ~17 mm deep here)
SERVO_Y = W.aileron_span_frac[0] * W.semi_span + 0.035  # 35 mm outboard of the aileron root


def _aileron_cutter(grow: float) -> Part:
    """Prism covering the region aft of the hinge line between the aileron end stations."""
    y0 = W.aileron_span_frac[0] * W.semi_span
    y1 = W.aileron_span_frac[1] * W.semi_span
    secs = []
    for y, dy in ((y0, -grow / 1000), (y1, grow / 1000)):
        c = G.chord_at(y)
        x_hinge = mm(G.le_x_at(y) - (1 - W.aileron_chord_frac) * c) + grow
        x_te = mm(G.le_x_at(y) - c) - 20
        from build123d import Vector
        z0, z1 = -40.0, 40.0
        yy = mm(y + dy)
        secs.append([Vector(x_hinge, yy, z0), Vector(x_hinge, yy, z1), Vector(x_te, yy, z1),
                     Vector(x_te, yy, z0)])
    from build123d import Face, Wire, loft
    faces = [Face(Wire.make_polygon(p, close=True)) for p in secs]
    return Part(loft(faces, ruled=True))


def segment(y0: float, y1: float) -> Part:
    p = G.wing_solid(y0, y1)
    # main spar
    if y0 < W.spar_half_length:
        p -= G.spar_bore(y0 - 0.001, min(y1, W.spar_half_length) + 0.001, W.spar_od)
    # tip tube (coaxial with the spar line)
    if y1 > TIP_TUBE_START and y0 < TIP_TUBE_END:
        p -= G.spar_bore(max(y0, TIP_TUBE_START) - 0.001, min(y1, TIP_TUBE_END), W.tip_spar_od)
    # aileron cut-out
    p -= _aileron_cutter(+HINGE_GAP / 2)
    # servo pocket in the lower surface (mid segment)
    if y0 < SERVO_Y < y1:
        xs = mm(G.le_x_at(SERVO_Y) - 0.52 * G.chord_at(SERVO_Y))
        zb = G.lower_surface_z(xs, SERVO_Y)
        p -= Pos(xs, mm(SERVO_Y), zb - 1 + SERVO[2] / 2) * Box(SERVO[0], SERVO[1], SERVO[2])
        # wire channel to the root along the spar (6 mm) is cut by the slicer-free path:
        p -= Pos(xs, mm(SERVO_Y + y0) / 2 - 1, zb + 6) * Box(6, mm(SERVO_Y - y0) + 4, 6)
    # wing bolts through the root segment into the fuselage saddle
    if y0 == 0.0:
        for x in G.WING_BOLT_X:
            p -= Pos(x, 30.0, 0) * Cylinder(2.2, 100)
    return p


def aileron() -> Part:
    y0 = W.aileron_span_frac[0] * W.semi_span
    y1 = W.aileron_span_frac[1] * W.semi_span
    full = G.wing_solid(y0 + 0.001, y1 - 0.001)
    return full & _aileron_cutter(-HINGE_GAP / 2)


def make() -> dict[str, Part]:
    """Aircraft-frame parts (left side y>0 and mirrored right side)."""
    left = {
        "wing_root_L": segment(Y_ROOT, Y_KINK),
        "wing_mid_L": segment(Y_KINK, Y_MID),
        "wing_tip_L": segment(Y_MID, Y_TIP),
        "aileron_L": aileron(),
    }
    out = dict(left)
    for k, v in left.items():
        out[k.replace("_L", "_R")] = mirror(v, about=Plane.XZ)
    return out


def build() -> dict[str, Part]:
    """Print orientation: span vertical (Y -> Z) for wing segments; aileron lying flat."""
    parts = make()
    out = {}
    for k, v in parts.items():
        if not k.endswith("_L"):
            continue  # right side = mirrored copy; slicer can mirror, but export both anyway below
    for k, v in parts.items():
        if k.startswith("aileron"):
            out[k] = G.bed_place(v, rot=(0, 0, 0))
        else:
            out[k] = G.bed_place(v, rot=(-90, 0, 0) if k.endswith("_L") else (90, 0, 0))
    return out


_ = (Mode, Rot, loft_sections)
