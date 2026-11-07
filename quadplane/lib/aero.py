"""Aerodynamic-surface geometry: airfoil sections placed in the aircraft frame and lofted.

Aircraft frame (mm in CAD): +X forward, +Y left, +Z up; origin at wing root LE.
A section is defined by its leading-edge point, chord, incidence (LE up positive, about the
quarter chord) and an airfoil name. Airfoil coordinates come from the UIUC database via
AeroSandbox and are resampled with a minimum trailing-edge thickness for printing.
"""

from functools import lru_cache

import numpy as np
from build123d import Edge, Face, Solid, Vector, Wire, loft

MIN_TE_MM = 0.6  # printable trailing edge


@lru_cache(maxsize=32)
def airfoil_coords(name: str, n: int = 70) -> np.ndarray:
    """Return (2n-1, 2) array TE(upper) -> LE -> TE(lower), chord 1."""
    import aerosandbox as asb

    af = asb.Airfoil(name).repanel(n)
    return np.asarray(af.coordinates, float)


def section_points(name: str, chord_mm: float, le: tuple[float, float, float],
                   incidence_deg: float, plane: str = "XZ") -> list[Vector]:
    """3D points of an airfoil section. plane 'XZ' for wings (span along Y),
    'XY' for vertical fins (span along Z, thickness along Y)."""
    c = airfoil_coords(name).copy()
    # thicken the trailing edge to MIN_TE: open the TE symmetrically by a linear ramp
    te_half = 0.5 * MIN_TE_MM / chord_mm
    upper = np.arange(len(c)) < np.argmin(c[:, 0])
    ramp = np.clip((c[:, 0] - 0.3) / 0.7, 0, 1)
    c[:, 1] += np.where(upper, 1, -1) * te_half * ramp
    i = np.radians(incidence_deg)
    dx = -(c[:, 0] - 0.25) * chord_mm  # forward positive
    dz = c[:, 1] * chord_mm
    xr = dx * np.cos(i) - dz * np.sin(i)
    zr = dz * np.cos(i) + dx * np.sin(i)
    x0, y0, z0 = le
    xq = x0 - 0.25 * chord_mm
    pts = []
    for a, b in zip(xr, zr):
        if plane == "XZ":
            pts.append(Vector(xq + a, y0, z0 + b))
        else:  # XY: thickness along Y
            pts.append(Vector(xq + a, y0 + b, z0))
    return pts


def section_wire(pts: list[Vector]) -> Wire:
    spline = Edge.make_spline(pts)
    te = Edge.make_line(pts[-1], pts[0])
    return Wire([spline, te])


def loft_sections(sections: list[list[Vector]], ruled: bool = True) -> Solid:
    faces = [Face(section_wire(p)) for p in sections]
    return loft(faces, ruled=ruled)
