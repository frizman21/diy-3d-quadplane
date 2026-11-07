"""AeroSandbox model of the aircraft built from quadplane.params (single source of truth)."""

import aerosandbox as asb
import aerosandbox.numpy as anp
import numpy as np

from quadplane.params import AIRCRAFT as AC


def wing_xsecs(wing=None):
    w = wing or AC.wing
    af = asb.Airfoil(w.airfoil)
    yc = w.center_span / 2
    dz = np.tan(np.radians(w.dihedral_deg)) * w.outer_span
    sweep_te = 0.0  # straight trailing edge? no: straight 25%-chord line on the outer panel
    x_tip = 0.25 * (w.root_chord - w.tip_chord)  # keeps the quarter-chord line unswept
    return [
        asb.WingXSec(xyz_le=[0, 0, 0], chord=w.root_chord, twist=w.root_incidence_deg, airfoil=af),
        asb.WingXSec(xyz_le=[0, yc, 0], chord=w.root_chord, twist=w.root_incidence_deg, airfoil=af),
        asb.WingXSec(xyz_le=[x_tip, w.semi_span, dz], chord=w.tip_chord,
                     twist=w.root_incidence_deg + w.tip_twist_deg, airfoil=af),
    ], sweep_te


def airplane(wing=None, tail=None, include_bodies=True, name="QP1") -> asb.Airplane:
    """ASB geometry uses x aft (geometry axes). Our body frame has +x forward, so x_asb = -x."""
    w = wing or AC.wing
    t = tail or AC.tail
    xsecs, _ = wing_xsecs(w)
    main = asb.Wing(name="wing", symmetric=True, xsecs=xsecs)

    x_tail_le = -AC.x_tail_le  # ASB x (aft positive)
    zb = AC.booms.z
    zh = t.h_z
    h_af = asb.Airfoil(t.h_airfoil)
    htail = asb.Wing(
        name="htail", symmetric=True,
        xsecs=[asb.WingXSec(xyz_le=[x_tail_le, 0, zh], chord=t.h_chord, twist=t.h_incidence_deg,
                            airfoil=h_af),
               asb.WingXSec(xyz_le=[x_tail_le, t.h_span / 2, zh], chord=t.h_chord,
                            twist=t.h_incidence_deg, airfoil=h_af)])
    v_af = asb.Airfoil(t.v_airfoil)
    fins = []
    for s in (+1, -1):
        fins.append(asb.Wing(
            name=f"fin{'L' if s > 0 else 'R'}", symmetric=False,
            xsecs=[asb.WingXSec(xyz_le=[x_tail_le, s * AC.booms.y, zb], chord=t.v_root_chord,
                                airfoil=v_af),
                   asb.WingXSec(xyz_le=[x_tail_le + (t.v_root_chord - t.v_tip_chord),
                                        s * AC.booms.y, zb - t.v_height],
                                chord=t.v_tip_chord, airfoil=v_af)]))

    fuselages = []
    if include_bodies:
        f = AC.fuselage
        L = f.x_nose - f.x_tail
        xs = np.linspace(0, 1, 21)
        # smooth pod: elliptic nose, parallel mid, tapered tail cone
        nose = np.sqrt(np.clip(1 - ((0.25 - xs) / 0.25) ** 2, 0, 1))
        tail = 1 - 0.55 * np.clip((xs - 0.7) / 0.3, 0, 1) ** 1.5
        radius_frac = np.where(xs < 0.25, nose, np.where(xs < 0.7, 1.0, tail))
        r_eq = 0.5 * np.sqrt(f.width * f.height)
        zc = f.z_top - f.height / 2
        fuselages.append(asb.Fuselage(name="pod", xsecs=[
            asb.FuselageXSec(xyz_c=[-f.x_nose + xi * L, 0, zc], radius=max(r_eq * rf, 1e-3))
            for xi, rf in zip(xs, radius_frac)]))
        b = AC.booms
        for s in (+1, -1):
            fuselages.append(asb.Fuselage(name="boom", xsecs=[
                asb.FuselageXSec(xyz_c=[-b.x_front, s * b.y, b.z], radius=b.tube_od / 2),
                asb.FuselageXSec(xyz_c=[-b.x_rear, s * b.y, b.z], radius=b.tube_od / 2)]))
            # motor pods: short stubby bodies at each lift motor (drag only)
            for xm in (AC.x_lift_front, AC.x_lift_rear):
                fuselages.append(asb.Fuselage(name="motorpod", xsecs=[
                    asb.FuselageXSec(xyz_c=[-xm - 0.03, s * b.y, b.z], radius=0.004),
                    asb.FuselageXSec(xyz_c=[-xm, s * b.y, b.z + 0.01], radius=0.020),
                    asb.FuselageXSec(xyz_c=[-xm + 0.03, s * b.y, b.z], radius=0.004)]))

    return asb.Airplane(name=name, xyz_ref=[0.25 * w.root_chord, 0, 0], wings=[main, htail, *fins],
                        fuselages=fuselages, s_ref=w.area, c_ref=w.mac, b_ref=w.span)


# Drag allowances not captured by AeroBuildup (fraction of computed CD0 or absolute counts)
EXCRESCENCE_CD = 0.0035  # stopped lift props (2 blades x4, aligned fore-aft), motor bells,
#                          landing feet, pitot, camera, print-surface steps. §3/§7 of report.


def trim_alpha(ap: asb.Airplane, v: float, mass: float, rho: float = 1.225, xyz_ref=None):
    """Find alpha giving L = W (ignores tail trim lift; tail is near-zero-lift at trim)."""
    from scipy.optimize import brentq

    def lift_err(a):
        op = asb.OperatingPoint(atmosphere=asb.Atmosphere(altitude=0), velocity=v, alpha=a)
        r = asb.AeroBuildup(ap, op, xyz_ref=xyz_ref or ap.xyz_ref).run()
        return float(r["L"]) - mass * 9.81

    return brentq(lift_err, -6, 14)


def aero_at(ap: asb.Airplane, v: float, alpha: float, xyz_ref=None):
    op = asb.OperatingPoint(atmosphere=asb.Atmosphere(altitude=0), velocity=v, alpha=alpha)
    r = asb.AeroBuildup(ap, op, xyz_ref=xyz_ref or ap.xyz_ref).run()
    q = op.dynamic_pressure()
    out = {k: float(np.asarray(r[k]).squeeze()) for k in ("L", "D", "CL", "CD", "Cm")}
    out["D"] += EXCRESCENCE_CD * q * ap.s_ref
    out["CD"] += EXCRESCENCE_CD
    return out


_ = anp  # keep import (ASB numpy used by callers)
