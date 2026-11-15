"""Aircraft-frame geometry shared by all parts (mm). Derived from quadplane.params only."""

import numpy as np
from build123d import Axis, Box, Cylinder, Part, Pos, Rot

from quadplane.lib.aero import loft_sections, section_points
from quadplane.params import AIRCRAFT as AC, mm

W = AC.wing
T = AC.tail
B = AC.booms

# Wing segment boundaries (left side, y >= 0), m. Each segment <= 300 mm span (prints span-up).
WING_STATIONS = [0.0, 0.30, 0.60, AC.wing.semi_span]
SPAR_X = -mm(0.27 * W.root_chord)  # straight spar line, ~27-28% local chord
# Wing bolts (x, mm): front bolt behind the LE, rear bolt ahead of where the pod tail cone drops away
WING_BOLT_X = (-25.0, -mm(0.40 * W.root_chord))


def chord_at(y: float) -> float:
    y = abs(y)
    if y <= W.center_span / 2:
        return W.root_chord
    f = (y - W.center_span / 2) / W.outer_span
    return W.root_chord + (W.tip_chord - W.root_chord) * f


def le_x_at(y: float) -> float:
    """LE x (body frame, m). Quarter-chord line is unswept, so LE moves aft at the tip."""
    return -0.25 * (W.root_chord - chord_at(y))


def twist_at(y: float) -> float:
    y = abs(y)
    if y <= W.center_span / 2:
        return W.root_incidence_deg
    f = (y - W.center_span / 2) / W.outer_span
    return W.root_incidence_deg + W.tip_twist_deg * f


def wing_section(y: float):
    return section_points(W.airfoil, mm(chord_at(y)), (mm(le_x_at(y)), mm(y), 0.0), twist_at(y))


def wing_solid(y0: float, y1: float) -> Part:
    """Solid wing between stations y0 < y1 (m, left side). Includes the kink if spanned."""
    ys = [y0]
    kink = W.center_span / 2
    if y0 < kink < y1:
        ys.append(kink)
    ys.append(y1)
    return Part(loft_sections([wing_section(y) for y in ys]))


def _depth_at(y: float):
    pts = np.array([[p.X, p.Z] for p in wing_section(y)])
    near = np.abs(pts[:, 0] - SPAR_X) < 4
    return pts[near, 1].max(), pts[near, 1].min()


def spar_z(od: float | None = None, y_end: float | None = None) -> float:
    """Spar centre z (mm) maximising the minimum wall between the bore and the skin over the
    spar's length (straight spar through a tapering, washed-out wing)."""
    od = mm(od or W.spar_od) + 0.3
    y_end = W.spar_half_length if y_end is None else y_end
    ys = np.linspace(0, y_end, 12)
    tops, bots = zip(*[_depth_at(y) for y in ys])
    zs = np.linspace(min(bots), max(tops), 400)
    walls = [min(min(t - (z + od / 2) for t in tops), min((z - od / 2) - b for b in bots)) for z in zs]
    return float(zs[int(np.argmax(walls))])


def spar_min_wall(od: float | None = None, y_end: float | None = None) -> float:
    od_mm = mm(od or W.spar_od) + 0.3
    y_end = W.spar_half_length if y_end is None else y_end
    z = spar_z(od, y_end)
    ys = np.linspace(0, y_end, 12)
    return float(min(min(t - (z + od_mm / 2), (z - od_mm / 2) - b) for t, b in (_depth_at(y) for y in ys)))


_SPAR_Z = None


def spar_bore(y0: float, y1: float, od: float, clearance: float = 0.3) -> Part:
    """Cylinder along Y from y0 to y1 (m) for a tube of diameter od (m), on the spar line."""
    global _SPAR_Z
    if _SPAR_Z is None:
        _SPAR_Z = spar_z()
    r = mm(od) / 2 + clearance / 2
    length = mm(y1 - y0)
    return Pos(SPAR_X, mm(y0 + y1) / 2, _SPAR_Z) * (Rot(90, 0, 0) * Cylinder(r, length))


def tube_along_x(x0: float, x1: float, y: float, z: float, od: float, id_: float | None = None,
                 clearance: float = 0.0) -> Part:
    """Tube/cylinder along X from x0 to x1 (m) at (y, z) (m)."""
    length = mm(abs(x1 - x0))
    c = Pos(mm((x0 + x1) / 2), mm(y), mm(z)) * (Rot(0, 90, 0) * Cylinder(mm(od) / 2 + clearance / 2, length))
    if id_:
        c -= Pos(mm((x0 + x1) / 2), mm(y), mm(z)) * (Rot(0, 90, 0) * Cylinder(mm(id_) / 2, length + 1))
    return c


def lower_surface_z(x_mm: float, y: float = 0.0) -> float:
    """z (mm) of the wing lower surface at chordwise position x (body mm) and station y."""
    pts = np.array([[p.X, p.Z] for p in wing_section(y)])
    i_le = int(np.argmax(pts[:, 0]))  # LE is the most forward point
    lower = pts[i_le:]
    order = np.argsort(lower[:, 0])
    return float(np.interp(x_mm, lower[order, 0], lower[order, 1]))


def largest_solid(part: Part) -> Part:
    """Drop slivers left by boolean cuts against thin trailing edges."""
    sols = part.solids()
    return max(sols, key=lambda s: s.volume) if len(sols) > 1 else part


def bed_place(part: Part, rot=(0, 0, 0)) -> Part:
    """Rotate into print orientation and place centred on the bed at z=0."""
    p = Rot(*rot) * part
    bb = p.bounding_box()
    return Pos(-(bb.min.X + bb.max.X) / 2, -(bb.min.Y + bb.max.Y) / 2, -bb.min.Z) * p


_ = (Axis, Box)
