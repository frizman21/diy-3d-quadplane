"""Static and dynamic stability (AVL), with AeroBuildup cross-check of the neutral point.

1. Neutral point from AVL (lifting surfaces) and from AeroBuildup (includes fuselage/booms).
2. CG placement: static margin target 12% MAC (QuadPlane practice: 10-15%).
3. Trim at cruise; elevator deflection; directional/lateral derivatives.
4. Eigenmodes (short period, phugoid, Dutch roll, roll, spiral) from AVL with the
   distributed mass model.
5. Hover balance: front/rear lift-motor load split at that CG.
"""

import aerosandbox as asb
import numpy as np

from analysis import avl
from analysis import mass as M
from analysis.common import RHO, G, plt, save_json, savefig
from analysis.model import airplane
from quadplane.params import AIRCRAFT as AC

SM_TARGET = 0.10  # QuadPlane practice 10-15% MAC; 10% keeps the battery inside the nose
V_CRUISE = 18.0


def distributed(items, n=12):
    """Split wing/spar/tail items into spanwise point masses so AVL inertias are realistic."""
    out = []
    w = AC.wing
    for it in items:
        if it.name.startswith(("printed wing", "wing spar", "wing tip spar")):
            ys = np.linspace(-w.semi_span, w.semi_span, 2 * n + 1)
            ys = 0.5 * (ys[1:] + ys[:-1])
            # wing mass ~ proportional to local chord
            yc = w.center_span / 2
            c = np.where(np.abs(ys) <= yc, w.root_chord, w.root_chord + (w.tip_chord - w.root_chord)
                         * (np.abs(ys) - yc) / w.outer_span)
            frac = c / c.sum()
            for y, f in zip(ys, frac):
                out.append(M.Item(it.name, it.mass * f, it.x, y, it.z, it.group))
        elif it.name.startswith(("printed tail", "tail spar")):
            for y in np.linspace(-AC.tail.h_span / 2, AC.tail.h_span / 2, 6):
                out.append(M.Item(it.name, it.mass / 6, it.x, y, it.z, it.group))
        else:
            out.append(it)
    return out


def neutral_point_aerobuildup(include_bodies=True):
    ap = airplane(include_bodies=include_bodies)
    op = asb.OperatingPoint(atmosphere=asb.Atmosphere(altitude=0), velocity=V_CRUISE, alpha=2.0)
    r = asb.AeroBuildup(ap, op).run_with_stability_derivatives(alpha=True, beta=True, p=False,
                                                                q=False, r=False)
    f = lambda k: float(np.asarray(r[k]).ravel()[0])  # noqa: E731
    return -f("x_np"), {k: f(k) for k in ("CLa", "Cma", "Cnb", "Clb")}


def main():
    w = AC.wing
    items = M.components()
    total, cg0, _ = M.summarize(items)
    q = 0.5 * RHO * V_CRUISE ** 2
    cl_trim = total * G / (q * w.area)

    # pass 1: neutral point (independent of the CG used for the run)
    r1 = avl.stability(distributed(items), cl_trim, V_CRUISE, cg0)
    x_np_avl = -r1["Xnp"]  # body frame
    x_np_ab, ab_derivs = neutral_point_aerobuildup()
    x_np_ab_nobody, _ = neutral_point_aerobuildup(include_bodies=False)
    # AVL models wing downwash at the tail properly but has no bodies; AeroBuildup has bodies
    # (Munk/slender-body) but no wing-tail downwash. Use AVL's NP plus the body increment
    # from AeroBuildup (fuselage pod, booms, motor pods: destabilising, moves NP forward).
    d_body = x_np_ab - x_np_ab_nobody
    x_np = x_np_avl + d_body
    x_cg = x_np + SM_TARGET * w.mac

    # place the battery to hit x_cg (limited by the nose: pack front >= 50 mm behind the tip)
    xb = M.battery_x_for_cg(x_cg)
    xb_max = AC.fuselage.x_nose - 0.050 - 0.070  # pack front 50 mm behind the nose tip (fits 77x85 mm section)
    if xb > xb_max:
        print(f"WARNING: battery x {xb:+.3f} beyond forward limit {xb_max:+.3f}; CG will be aft of target")
        xb = xb_max
    items = M.components(battery_x=xb)
    total, cg, groups = M.summarize(items)

    r2 = avl.stability(distributed(items), cl_trim, V_CRUISE, cg)
    modes = avl.parse_modes(r2["eig_raw"])

    # hover load split
    xf, xr = AC.x_lift_front, AC.x_lift_rear
    front_share = (cg[0] - xr) / (xf - xr)

    def describe(ev):
        re_, im = ev
        wn = np.hypot(re_, im)
        zeta = -re_ / wn if wn > 0 else float("nan")
        t_half = np.log(2) / -re_ if re_ < 0 else float("inf")
        t_double = np.log(2) / re_ if re_ > 0 else float("inf")
        return {"real": re_, "imag": im, "wn": wn, "zeta": zeta, "period_s": 2 * np.pi / im
                if im > 1e-6 else None, "t_half_s": t_half, "t_double_s": t_double}

    mode_list = [describe(m) for m in modes if not (m[1] < -1e-9)]  # keep one of each pair

    res = {
        "mass": total, "cg": cg.tolist(), "groups": groups, "battery_x": xb, "battery_x_max": xb_max,
        "sm_target_pct": SM_TARGET * 100,
        "cl_trim": cl_trim, "v_trim": V_CRUISE,
        "x_np_avl": x_np_avl, "x_np_aerobuildup": x_np_ab, "x_np_design": x_np,
        "x_np_aerobuildup_no_bodies": x_np_ab_nobody, "np_body_shift": d_body,
        "np_pct_mac_avl": (-x_np_avl) / w.mac * 100,
        "x_cg_pct_root": -cg[0] / w.root_chord * 100,
        "static_margin_pct": (cg[0] - x_np) / w.mac * 100,
        "avl_trim": {k: r2[k] for k in r2 if k not in ("eig_raw", "avl_stdout_tail")},
        "aerobuildup_derivs": ab_derivs,
        "modes": mode_list,
        "hover_front_share": front_share,
        "vh": AC.tail.h_span * AC.tail.h_chord * (-(AC.x_tail_le - 0.25 * AC.tail.h_chord) + cg[0])
        / (w.area * w.mac),
        "vv": 2 * AC.tail.v_height * (AC.tail.v_root_chord + AC.tail.v_tip_chord) / 2
        * (-(AC.x_fin_le - 0.25 * AC.tail.v_root_chord) + cg[0]) / (w.area * w.span),
    }
    save_json("stability", res)
    print(f"mass {total:.3f} kg  CL_trim {cl_trim:.3f}")
    print(f"NP: AVL {x_np_avl:+.4f}  AeroBuildup {x_np_ab:+.4f} (no bodies {x_np_ab_nobody:+.4f})"
          f"  body shift {d_body:+.4f} -> design {x_np:+.4f} m")
    print(f"CG {cg[0]:+.4f} m ({res['x_cg_pct_root']:.1f}% root chord), SM {res['static_margin_pct']:.1f}%")
    print(f"battery x {xb:+.3f} m; hover front share {front_share:.3f}")
    print(f"Vh {res['vh']:.3f}  Vv {res['vv']:.4f}")
    print("AVL trim:", {k: round(v, 4) for k, v in res["avl_trim"].items()})
    print("AeroBuildup:", ab_derivs)
    for m in mode_list:
        print("mode", {k: (round(v, 3) if isinstance(v, float) else v) for k, v in m.items()})
    if not modes:
        print(r2["avl_stdout_tail"][-1500:])

    # root-locus style eigenvalue plot
    if modes:
        fig, ax = plt.subplots(figsize=(6.5, 5))
        ev = np.array(modes)
        ax.plot(ev[:, 0], ev[:, 1], "kx", ms=9)
        ax.axvline(0, color="r", lw=1)
        ax.set(xlabel="Real (1/s)", ylabel="Imag (rad/s)", title="AVL eigenvalues at 18 m/s cruise")
        ax.grid(alpha=0.3)
        savefig(fig, "stability_eigenvalues")
    return res


if __name__ == "__main__":
    main()
