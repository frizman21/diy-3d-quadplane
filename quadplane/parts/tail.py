"""Tail: U-tail. Two fins (each with a boom sleeve, the stab-spar boss and a skid tip) and a
horizontal stabiliser in two halves on an 8x6 carbon spar, with two elevator halves joined by
a 3 mm carbon torque rod.

Print: LW-PLA throughout (fins carry only ~8 N landing load each); TPU skid shoes on the fin tips.
"""

from build123d import Box, Cylinder, Face, Part, Plane, Pos, Rot, Vector, Wire, loft, mirror

from quadplane import geometry as G
from quadplane import printer
from quadplane.lib.aero import loft_sections, section_points
from quadplane.params import AIRCRAFT as AC, mm

MATERIAL = printer.PETG
T, B = AC.tail, AC.booms
X_LE = mm(AC.x_tail_le)
YB, ZB, ZH = mm(B.y), mm(B.z), mm(T.h_z)
R_BORE = mm(B.tube_od) / 2 + 0.2
SPAR_R = 4.0 + 0.15
X_SPAR = X_LE - 0.25 * mm(T.h_chord)
GAP = 1.0


def _hstab_solid(y0: float, y1: float) -> Part:
    secs = [section_points(T.h_airfoil, mm(T.h_chord), (X_LE, mm(y), ZH), T.h_incidence_deg)
            for y in (y0, y1)]
    return Part(loft_sections(secs))


def _elev_cutter(grow: float, y0: float, y1: float) -> Part:
    xh = X_LE - (1 - T.elevator_chord_frac) * mm(T.h_chord) + grow
    xt = X_LE - mm(T.h_chord) - 10
    return Pos((xh + xt) / 2, mm(y0 + y1) / 2, ZH) * Box(xh - xt, mm(y1 - y0), 60)


def hstab_half() -> Part:
    y0, y1 = 0.0, B.y - (R_BORE + 3.5) / 1000 - 0.001
    p = _hstab_solid(y0, y1)
    p -= Pos(X_SPAR, mm(y0 + y1) / 2, ZH) * (Rot(90, 0, 0) * Cylinder(SPAR_R, mm(y1 - y0) + 2))
    p -= _elev_cutter(GAP / 2, y0 - 0.01, y1 + 0.01)
    return p


def elevator_half() -> Part:
    y0, y1 = 0.002, B.y - (R_BORE + 3.5) / 1000 - 0.003
    p = _hstab_solid(y0, y1) & _elev_cutter(-GAP / 2, y0, y1)
    xh = X_LE - (1 - T.elevator_chord_frac) * mm(T.h_chord) - 4
    p -= Pos(xh, mm(y0 + y1) / 2, ZH) * (Rot(90, 0, 0) * Cylinder(1.6, mm(y1 - y0) + 2))  # 3 mm torque rod
    return p


def fin() -> Part:
    """Fin hanging below the boom + sleeve over the boom end + stab-spar boss + skid."""
    root = section_points(T.v_airfoil, mm(T.v_root_chord), (X_LE, YB, ZB), 0.0, plane="XY")
    tip_le = X_LE - mm(T.v_root_chord - T.v_tip_chord)
    tip = section_points(T.v_airfoil, mm(T.v_tip_chord), (tip_le, YB, ZB - mm(T.v_height)), 0.0,
                         plane="XY")
    f = Part(loft_sections([root, tip]))
    ro = R_BORE + 2.4
    # two clamp bands on the boom (front band carries the stab-spar boss), joined by the fin root
    bands = [(X_LE - 22, 44), (X_LE - mm(T.v_root_chord) + 16, 32)]
    for xc, ln in bands:
        f += Pos(xc, YB, ZB) * (Rot(0, 90, 0) * Cylinder(ro, ln))
    root_fair = Pos(X_LE - mm(T.v_root_chord) / 2, YB, ZB - 6) * Box(mm(T.v_root_chord) - 10, 7, 12)
    f += root_fair
    boss = Pos(X_SPAR, YB, ZH) * (Rot(90, 0, 0) * Cylinder(SPAR_R + 3, 2 * ro))
    f += boss
    f -= Pos(X_LE - mm(T.v_root_chord) / 2 - 2, YB, ZB) * (Rot(0, 90, 0) * Cylinder(R_BORE, mm(T.v_root_chord) + 2))
    f -= Pos(X_SPAR, YB - ro / 2 - 2, ZH) * (Rot(90, 0, 0) * Cylinder(SPAR_R, ro + 4))  # spar socket, inboard
    f -= Pos(X_LE + 4, YB, ZB) * (Rot(0, 90, 0) * Cylinder(R_BORE, 8))  # boom passes the front band
    # skid pad at the tip (TPU shoe glues on)
    f += Pos(tip_le - mm(T.v_tip_chord) / 2, YB, ZB - mm(T.v_height) + 3) * Box(mm(T.v_tip_chord) * 0.8, 8, 6)
    return f


def make() -> dict[str, Part]:
    left = {"fin_L": fin(), "hstab_L": hstab_half(), "elevator_L": elevator_half()}
    out = dict(left)
    for k, v in left.items():
        out[k.replace("_L", "_R")] = mirror(v, about=Plane.XZ)
    return out


def build() -> dict[str, Part]:
    out = {}
    for k, v in make().items():
        if k.startswith("fin"):
            out[k] = G.bed_place(v, rot=(90 if k.endswith("_L") else -90, 0, 0))
        else:
            out[k] = G.bed_place(v)
    return out


_ = (Face, Vector, Wire, loft)
