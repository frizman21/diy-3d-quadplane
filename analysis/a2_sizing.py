"""Wing sizing trade: span x root chord carpet.

For each candidate planform: total mass (mass model with printed-wing and spar mass
scaling), drag polar (AeroSandbox AeroBuildup, NeuralFoil section data, vectorised alpha
sweep), stall speed, minimum cruise power, power at 18 m/s, hover power and hover time.
Constraints: span <= 1.9 m (doorway), overall length <= 1.2 m (Suburban, estimated),
stall speed <= 11 m/s (transition-speed margin).
"""

import dataclasses

import aerosandbox as asb
import numpy as np

from analysis import mass as M
from analysis.common import RHO, G, plt, save_json, savefig
from analysis.model import EXCRESCENCE_CD, airplane
from analysis.hover import hover_power
from quadplane.params import AIRCRAFT as AC

SPANS = np.arange(1.40, 1.91, 0.10)
ROOT_CHORDS = np.arange(0.22, 0.345, 0.02)
TAPER_OUTER = 0.18 / 0.28  # fixed outer-panel taper used in the trade
V_GRID = np.linspace(10, 26, 33)
ETA_PUSHER = 0.62  # cruise propulsive x motor x ESC (refined in a3_propulsion)
CLMAX_3D_FACTOR = 0.88  # wing CLmax / section CLmax (taper + washout; Raymer 12.4 range)
BATTERY_WH_USABLE = 194 * (1 - AC.mission.reserve_frac)
SPAN_MAX = 1.80  # 1.9 m doorway limit less 0.1 m handling margin (decision D-013)
TIP_MIN = 0.150  # tip Re >= 1e5 at 10 m/s, spar/print depth (decision D-013)
VS_MAX = 10.5  # stall speed limit incl. 0.5 m/s reserve for further mass growth (D-013)


def section_clmax(airfoil: str, re: float = 1.6e5) -> float:
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
    d_spar = M.tube_mass(0.006, 0.004, w.span - AC.wing.span)  # span change lands in the tip tube
    _ = base_p
    return base_total + d_wing + d_spar


def length_for(w) -> float:
    R, gap = AC.lift.radius, AC.lift.tip_gap
    front = R + gap + R
    tail_le = -(w.root_chord + R + gap) - R - gap
    return front - (tail_le - AC.tail.v_root_chord)


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
    print(f"section CLmax ({AC.wing.airfoil}, Re 160k) = {clmax2d:.2f}")
    rows = []
    for b in SPANS:
        for c in ROOT_CHORDS:
            r = evaluate(b, c, clmax2d)
            r["tip_chord"] = float(c * TAPER_OUTER)
            r["feasible"] = bool(r["span"] <= SPAN_MAX + 1e-9 and r["vs"] <= VS_MAX
                                 and r["length"] <= 1.20 + 1e-9 and r["tip_chord"] >= TIP_MIN - 1e-9)
            rows.append(r)
            print(f"b={b:.2f} c={c:.2f} S={r['area']:.3f} AR={r['AR']:.1f} m={r['mass']:.3f} "
                  f"Vs={r['vs']:.1f} Pmin={r['p_min']:.0f}W@{r['v_pmin']:.0f} P18={r['p18']:.0f} "
                  f"L/D={r['ld_max']:.1f} len={r['length']:.3f} {'OK' if r['feasible'] else '--'}")
    feas = [r for r in rows if r["feasible"]]
    # selection: minimise P18 (cruise demo) with minimum-power as tiebreaker, among feasible
    best = min(feas, key=lambda r: (r["p18"] + 0.5 * r["p_min"]))
    print("best feasible:", best)
    save_json("sizing", {"rows": rows, "best": best, "clmax2d": clmax2d,
                         "clmax3d_factor": CLMAX_3D_FACTOR, "eta_pusher": ETA_PUSHER,
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
        ax.contour(B, C * 1000, grid("length"), [1.20], colors="r", linewidths=2)
        ax.contour(B, C * 1000, C * TAPER_OUTER, [TIP_MIN], colors="orange", linewidths=2)
        ax.axvline(SPAN_MAX, color="m", lw=2)
        ax.plot(best["span"], best["root_chord"] * 1000, "r*", ms=16)
        ax.set(xlabel="span (m)", ylabel="root chord (mm)", title=title)
    savefig(fig, "sizing_carpet")
    return best


if __name__ == "__main__":
    main()
