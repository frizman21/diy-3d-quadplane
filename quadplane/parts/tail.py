"""Tail: U-tail. Two fins (each with a boom sleeve, the stab-spar boss and a skid tip) and a
horizontal stabiliser in two halves on an 8x6 carbon spar, with two elevator halves joined by
a 4 mm carbon torque rod.

The boom ends about 30 mm behind the stab LE. Each fin sleeves over the last 85 mm of the boom
and continues aft of the boom end as a solid stub; the stab-spar boss sits on the sleeve.

Print: LW-PLA throughout (fins carry only ~4 N landing load each); TPU skid shoes on the fin tips.
"""

from build123d import Box, Cylinder, Face, Part, Plane, Pos, Rot, Vector, Wire, loft, mirror

from quadplane import geometry as G
from quadplane import hardware as HW
from quadplane import printer
from quadplane.lib.aero import loft_sections, section_points
from quadplane.params import AIRCRAFT as AC, mm

MATERIAL = printer.PETG
T, B = AC.tail, AC.booms
X_LE = mm(AC.x_tail_le)
YB, ZB, ZH = mm(B.y), mm(B.z), mm(T.h_z)
R_BORE = mm(B.tube_od) / 2 + 0.2
SPAR_R = HW.TAIL_SPAR_OD / 2 + 0.15
X_SPAR = X_LE - 0.25 * mm(T.h_chord)
X_FIN = mm(AC.x_fin_le)  # fin root LE
X_BOOM_END = mm(B.x_rear)
ROD_R = HW.ELEVATOR_ROD_D / 2 + 0.1
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
    p -= Pos(xh, mm(y0 + y1) / 2, ZH) * (Rot(90, 0, 0) * Cylinder(ROD_R, mm(y1 - y0) + 2))  # torque rod
    return p


def fin() -> Part:
    """Fin hanging below the boom + sleeve over the boom end + stab-spar boss + skid."""
    root = section_points(T.v_airfoil, mm(T.v_root_chord), (X_FIN, YB, ZB), 0.0, plane="XY")
    tip_le = X_FIN - mm(T.v_root_chord - T.v_tip_chord)
    tip = section_points(T.v_airfoil, mm(T.v_tip_chord), (tip_le, YB, ZB - mm(T.v_height)), 0.0,
                         plane="XY")
    f = Part(loft_sections([root, tip]))
    ro = R_BORE + 2.4
    # one sleeve from the fin LE to just behind the stab-spar boss; solid aft of the boom end
    x_stub = X_SPAR - (SPAR_R + 3) - 2
    f += Pos((X_FIN + x_stub) / 2, YB, ZB) * (Rot(0, 90, 0) * Cylinder(ro, X_FIN - x_stub))
    root_fair = Pos(X_FIN - mm(T.v_root_chord) / 2, YB, ZB - 6) * Box(mm(T.v_root_chord) - 10, 7, 12)
    f += root_fair
    boss = Pos(X_SPAR, YB, ZH) * (Rot(90, 0, 0) * Cylinder(SPAR_R + 3, 2 * ro))
    f += boss
    # boom bore: open at the front, closed at the boom end
    f -= Pos((X_FIN + 4 + X_BOOM_END) / 2, YB, ZB) * (Rot(0, 90, 0) * Cylinder(R_BORE, X_FIN + 4 - X_BOOM_END))
    f -= Pos(X_SPAR, YB - ro / 2 - 2, ZH) * (Rot(90, 0, 0) * Cylinder(SPAR_R, ro + 4))  # spar socket, inboard
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
