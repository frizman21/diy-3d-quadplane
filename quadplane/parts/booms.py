"""Boom hardware: wing-to-boom saddles, lift-motor mounts (front mounts include the front
landing legs). Booms themselves are COTS 20x18 carbon tubes (see quadplane/cots.py).

Print: PA-CF or ASA (motor heat, vibration). Clamps use M3 bolts + heat-set inserts.
"""

from build123d import Box, Cylinder, Part, Plane, Pos, Rot, mirror

from quadplane import geometry as G
from quadplane import hardware as HW
from quadplane import printer
from quadplane.params import AIRCRAFT as AC, mm

MATERIAL = printer.PACF
B = AC.booms
R_BORE = mm(B.tube_od) / 2 + 0.2
CLAMP_T = 3.5
YB, ZB = mm(B.y), mm(B.z)
Z_GROUND = mm(B.z - AC.tail.v_height)


def _clamp_ring(x_c: float, length: float) -> Part:
    """Split clamp ring around the boom at x_c (mm), with M3 pinch ears underneath."""
    ro = R_BORE + CLAMP_T
    ring = Pos(x_c, YB, ZB) * (Rot(0, 90, 0) * Cylinder(ro, length))
    ears = Pos(x_c, YB, ZB - ro - 3) * Box(length, 10, 10)
    ring += ears
    ring -= Pos(x_c, YB, ZB) * (Rot(0, 90, 0) * Cylinder(R_BORE, length + 2))
    ring -= Pos(x_c, YB, ZB - ro) * Box(length + 2, 1.6, 2 * ro)  # pinch slot
    for dx in (-length / 4, length / 4):
        ring -= Pos(x_c + dx, YB, ZB - ro - 3) * (Rot(90, 0, 0) * Cylinder(1.7, 14))
    return ring


def boom_saddle() -> Part:
    """Wing-to-boom saddle: a 3 mm plate bonded to the wing's lower skin, carried by three
    clamp lands (front, middle, rear) around the boom; open between lands to save mass."""
    c = AC.wing.root_chord
    x0, x1 = -8.0, -mm(c) + 12
    length = x0 - x1
    width = 22.0
    top = max(G.lower_surface_z(x, B.y) for x in (x0, (x0 + x1) / 2, x1)) + 3
    wing = G.wing_solid(B.y - 0.03, B.y + 0.03)
    # top plate following the wing's lower surface (3 mm thick, below the skin)
    plate = Pos((x0 + x1) / 2, YB, top - 4) * Box(length, width, 8)
    plate -= wing
    plate -= Pos((x0 + x1) / 2, YB, top - 4 - 3 - 50) * Box(length + 2, width + 2, 100)  # keep 3 mm under skin
    blk = plate
    land = 26.0
    for xc in (x0 - land / 2, (x0 + x1) / 2, x1 + land / 2):
        h = top - (ZB - R_BORE - CLAMP_T)
        b = Pos(xc, YB, ZB - R_BORE - CLAMP_T + h / 2) * Box(land, width, h)
        b -= wing
        b -= Pos(xc, YB, ZB) * (Rot(0, 90, 0) * Cylinder(R_BORE, land + 2))
        b -= Pos(xc, YB, ZB + R_BORE + 2.5) * Box(5, 40, 2.5)  # zip-tie / strap slot above the boom
        blk += b
    return G.largest_solid(blk)


def motor_mount(x_motor: float, front: bool) -> Part:
    xm = mm(x_motor)
    length = 34.0
    m = _clamp_ring(xm, length)
    pad_top = mm(B.z + AC.lift.motor_height)
    pad = Pos(xm, YB, pad_top - 2.5) * Cylinder(HW.MN3508_BODY_D / 2 + 1, 5)
    ped = Pos(xm, YB, (pad_top + ZB) / 2) * Box(24, 24, pad_top - ZB)
    ped -= Pos(xm, YB, ZB) * (Rot(0, 90, 0) * Cylinder(R_BORE, length + 2))
    m += pad + ped
    import math
    for k in range(4):
        a = math.pi / 4 + k * math.pi / 2
        r = HW.MN3508_BOLT_CIRCLE / 2
        m -= Pos(xm + r * math.cos(a), YB + r * math.sin(a), pad_top - 6) * Cylinder(1.7, 14)
    m -= Pos(xm, YB, pad_top) * Cylinder(5.0, 8)  # shaft / circlip clearance
    if front:
        # end cap (closes the boom tip) and the front landing leg
        m += Pos(mm(B.x_front) + 2.5, YB, ZB) * (Rot(0, 90, 0) * Cylinder(R_BORE + CLAMP_T, 5))
        leg_top = ZB - R_BORE - CLAMP_T
        leg_len = leg_top - Z_GROUND
        leg = Pos(xm - 4, YB, leg_top - leg_len / 2) * Box(16, 8, leg_len)
        leg += Pos(xm - 4, YB, Z_GROUND + 6) * Box(30, 14, 12)  # foot (TPU pad glued under)
        m += leg
    return m


def make() -> dict[str, Part]:
    left = {
        "boom_saddle_L": boom_saddle(),
        "motor_mount_front_L": motor_mount(AC.x_lift_front, True),
        "motor_mount_rear_L": motor_mount(AC.x_lift_rear, False),
    }
    out = dict(left)
    for k, v in left.items():
        out[k.replace("_L", "_R")] = mirror(v, about=Plane.XZ)
    return out


def build() -> dict[str, Part]:
    return {k: G.bed_place(v) for k, v in make().items()}
