"""Wing sizing trade: span x root chord carpet.

For each candidate planform: total mass (mass model with printed-wing and spar mass
scaling), drag polar (AeroSandbox AeroBuildup, NeuralFoil section data, vectorised alpha
sweep), stall speed, minimum cruise power, power at 18 m/s, hover power and hover time.
Constraints: span <= 1.4 m (500 mm tip tubes outboard of the centre spar), overall length
<= 1.4 m (Suburban, estimated), stall speed <= 10.5 m/s at the heaviest mass the motors allow (transition-speed margin), tip chord
>= 150 mm, and take-off mass no more than the lift motors carry at T/W 1.8 (PERF-5).
"""

import dataclasses

import aerosandbox as asb
import numpy as np

from analysis import mass as M
from analysis.common import NU, RHO, G, plt, save_json, savefig
from analysis.model import EXCRESCENCE_CD, airplane
from analysis.hover import DOWNLOAD, OPTIONS, SELECTED, hover_power
from quadplane.params import AIRCRAFT as AC

AC_TW_MIN = 1.8  # PERF-5
SPANS = np.arange(1.10, 1.61, 0.10)
ROOT_CHORDS = np.arange(0.22, 0.295, 0.01)
TAPER_OUTER = 0.66  # fixed outer-panel taper used in the trade
BATTERY_WH = M.BATTERY_WH  # 6S1P Molicel P50B (D-037)
V_GRID = np.linspace(10, 26, 33)
ETA_PUSHER = 0.62  # cruise propulsive x motor x ESC (refined in a3_propulsion)
CLMAX_3D_FACTOR = 0.88  # wing CLmax / section CLmax (taper + washout; Raymer 12.4 range)
BATTERY_WH_USABLE = BATTERY_WH * (1 - AC.mission.reserve_frac)
SPAN_MAX = 1.40  # centre spar plus two 500 mm catalogue tip tubes with 120 mm overlap (D-039)
LIFT = OPTIONS[SELECTED]
MASS_MAX = 4 * LIFT.max_g / 1000 / (AC_TW_MIN * (1 + DOWNLOAD))  # PERF-5 with the hover download
AREA_TOL = 0.02  # planforms within 2% of the smallest feasible area count as the same size
CHORD_MIN = 0.240  # root chord that keeps a 0.9 mm wall around the 20 mm spar (tests/test_parts.py)
TIP_MIN = 0.150  # tip Re >= 1e5 at 10 m/s, spar/print depth (decision D-013)
VS_MAX = 10.5  # stall speed limit incl. 0.5 m/s reserve for further mass growth (D-013)
LENGTH_MAX = AC.limits.length  # SIZE-2 rev C (D-026)
RE_STALL = VS_MAX * AC.wing.mac / NU  # MAC Reynolds number at the stall-speed limit


def section_clmax(airfoil: str, re: float = RE_STALL) -> float:
    a = np.linspace(0, 18, 73)
    r = asb.Airfoil(airfoil).get_aero_from_neuralfoil(alpha=a, Re=re, model_size="large")
    return float(np.max(r["CL"]))


def planform(span, root_chord):
    w = dataclasses.replace(AC.wing, span=float(span), root_chord=float(root_chord),
                            tip_chord=float(root_chord * TAPER_OUTER))
    return w


def mass_for(w) -> float:
    base_items = M.components()
    base_total, _, _ = M.summarize(base_items)
    base_p = M.printed_estimates()
    skin = 0.45e-3 * M.LWPLA_FOAMED * 1000 * 1.35
    d_wing = 2.04 * (w.area - AC.wing.area) * skin
    d_spar = M.tube_mass(AC.wing.tip_spar_od, AC.wing.tip_spar_id, w.span - AC.wing.span)  # span change lands in the tip tube
    _ = base_p
    return base_total + d_wing + d_spar


def length_for(w) -> float:
    R, gap = AC.lift.radius, AC.lift.tip_gap
    front = AC.x_lift_front + R
    tail_le = -(w.root_chord + R + gap) - R - gap
    return front - (tail_le - max(AC.tail.v_root_chord, AC.tail.h_chord))


def polar(w):
    ap = airplane(wing=w)
    alphas = np.linspace(-4, 12, 33)
    op = asb.OperatingPoint(atmosphere=asb.Atmosphere(altitude=0), velocity=16.0, alpha=alphas)
    r = asb.AeroBuildup(ap, op).run()
    return alphas, np.asarray(r["CL"]), np.asarray(r["CD"]) + EXCRESCENCE_CD, ap


def evaluate(span, chord, clmax2d):
    w = planform(span, chord)
    m = mass_for(w)
    W = m * G
    _, CL, CD, _ = polar(w)
    order = np.argsort(CL)
    CL, CD = CL[order], CD[order]
    S = w.area
    clmax = CLMAX_3D_FACTOR * clmax2d
    vs = np.sqrt(2 * W / (RHO * S * clmax))
    p_req = []
    for v in V_GRID:
        cl = W / (0.5 * RHO * v ** 2 * S)
        if cl > min(CL.max(), 0.9 * clmax):
            p_req.append(np.nan)
            continue
        cd = np.interp(cl, CL, CD)
        p_req.append(0.5 * RHO * v ** 3 * S * cd / ETA_PUSHER)
    p_req = np.array(p_req)
    i_min = int(np.nanargmin(p_req))
    p18 = float(np.interp(18.0, V_GRID, p_req))
    ph = hover_power(m)
    return {
        "span": float(span), "root_chord": float(chord), "area": S, "AR": w.aspect_ratio,
        "mass": m, "wing_loading_gdm2": m * 1000 / (S * 100), "vs": float(vs),
        "p_min": float(p_req[i_min]), "v_pmin": float(V_GRID[i_min]), "p18": p18,
        "hover_w": ph, "hover_min": BATTERY_WH_USABLE / ph * 60,
        "cruise_min_at_18": BATTERY_WH_USABLE / p18 * 60, "length": length_for(w),
        "ld_max": float(np.nanmax(W * V_GRID / (p_req * ETA_PUSHER))),
    }


def main():
    clmax2d = section_clmax(AC.wing.airfoil)
    print(f"section CLmax ({AC.wing.airfoil}, Re {RE_STALL:.0f}) = {clmax2d:.2f}")
    rows = []
    for b in SPANS:
        for c in ROOT_CHORDS:
            r = evaluate(b, c, clmax2d)
            r["tip_chord"] = float(c * TAPER_OUTER)
            # the stall-speed limit must hold up to the heaviest mass the lift motors allow
            r["vs_at_mass_max"] = float(r["vs"] * np.sqrt(MASS_MAX / r["mass"]))
            r["feasible"] = bool(r["span"] <= SPAN_MAX + 1e-9 and r["vs_at_mass_max"] <= VS_MAX
                                 and r["length"] <= LENGTH_MAX + 1e-9 and r["tip_chord"] >= TIP_MIN - 1e-9
                                 and r["mass"] <= MASS_MAX and r["root_chord"] >= CHORD_MIN - 1e-9)
            rows.append(r)
            print(f"b={b:.2f} c={c:.2f} S={r['area']:.3f} AR={r['AR']:.1f} m={r['mass']:.3f} "
                  f"Vs={r['vs']:.1f} Pmin={r['p_min']:.0f}W@{r['v_pmin']:.0f} P18={r['p18']:.0f} "
                  f"L/D={r['ld_max']:.1f} len={r['length']:.3f} {'OK' if r['feasible'] else '--'}")
    feas = [r for r in rows if r["feasible"]]
    # selection: the smallest feasible wing (thrust margin, PERF-5, is what binds at this size,
    # so the lightest wing wins), with power at 18 m/s as the tiebreaker between equal areas
    a_min = min(r["area"] for r in feas)
    best = min((r for r in feas if r["area"] <= a_min * (1 + AREA_TOL)), key=lambda r: r["p18"])
    print("best feasible:", best)
    save_json("sizing", {"rows": rows, "best": best, "clmax2d": clmax2d,
                         "clmax3d_factor": CLMAX_3D_FACTOR, "eta_pusher": ETA_PUSHER,
                         "re_stall": RE_STALL, "length_max": LENGTH_MAX, "vs_max": VS_MAX,
                         "span_max": SPAN_MAX, "mass_max": MASS_MAX, "chord_min": CHORD_MIN, "battery_wh": BATTERY_WH,
                         "excrescence_cd": EXCRESCENCE_CD})

    # carpet plots
    fig, axs = plt.subplots(1, 3, figsize=(16, 4.8))
    B, C = np.meshgrid(SPANS, ROOT_CHORDS, indexing="ij")

    def grid(key):
        return np.array([r[key] for r in rows]).reshape(B.shape)

    for ax, key, title in ((axs[0], "p18", "Battery power at 18 m/s (W)"),
                           (axs[1], "vs", "Stall speed (m/s)"),
                           (axs[2], "ld_max", "Max L/D (whole aircraft)")):
        cs = ax.contourf(B, C * 1000, grid(key), 14, cmap="viridis")
        fig.colorbar(cs, ax=ax)
        ax.contour(B, C * 1000, grid("vs"), [VS_MAX], colors="w", linewidths=2, linestyles="--")
        ax.contour(B, C * 1000, grid("length"), [LENGTH_MAX], colors="r", linewidths=2)
        ax.contour(B, C * 1000, C * TAPER_OUTER, [TIP_MIN], colors="orange", linewidths=2)
        ax.axvline(SPAN_MAX, color="m", lw=2)
        ax.plot(best["span"], best["root_chord"] * 1000, "r*", ms=16)
        ax.set(xlabel="span (m)", ylabel="root chord (mm)", title=title)
    savefig(fig, "sizing_carpet")
    return best


if __name__ == "__main__":
    main()
