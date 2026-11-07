"""Airfoil trade study (XFOIL primary, NeuralFoil cross-check).

Evaluates candidate sections at the wing's operating Reynolds numbers, with free
transition (Ncrit 9, smooth) and an early-transition case (Ncrit 5) representing a
sanded 3D-printed surface. Produces polars, a scoring table and results JSON.
"""

import numpy as np
import aerosandbox as asb
import neuralfoil as nf

from analysis import xfoil
from analysis.common import plt, save_json, savefig

CANDIDATES = [
    "clarky", "sd7062", "sd7037", "sd7032", "e205", "e374",
    "naca2412", "naca4412", "mh114", "naca23012",
]
RE_LIST = [1.5e5, 2.5e5, 3.5e5]
NCRIT = [9.0, 5.0]
ALPHA = np.arange(-4, 18.01, 0.5)
CL_BAND = (0.30, 0.65)  # design CL band: fast cruise to loiter
MIN_TC = 0.10  # minimum t/c: spar depth + printability of the trailing region


def run_xfoil(af, re, ncrit):
    out = xfoil.polar(af.coordinates, re, ALPHA, ncrit=ncrit)
    return out["alpha"], out["CL"], out["CD"], out["CM"]


def metrics(a, cl, cd, cm):
    m = {}
    if len(a) < 10:
        return None
    i_max = int(np.argmax(cl))
    m["clmax"] = float(cl[i_max])
    m["alpha_stall"] = float(a[i_max])
    ld = cl / cd
    m["ld_max"] = float(ld.max())
    m["cl_at_ld_max"] = float(cl[np.argmax(ld)])
    pos = cl > 0
    m["endurance_max"] = float((cl[pos] ** 1.5 / cd[pos]).max())
    m["cm0"] = float(np.interp(0.0, a, cm))
    # mean drag in the design CL band (only on the pre-stall branch)
    pre = slice(0, i_max + 1)
    clp, cdp = cl[pre], cd[pre]
    band = np.linspace(*CL_BAND, 15)
    if clp.min() <= CL_BAND[0] and clp.max() >= CL_BAND[1]:
        idx = np.argsort(clp)
        m["cd_band"] = float(np.mean(np.interp(band, clp[idx], cdp[idx])))
    else:
        m["cd_band"] = float("nan")
    # post-stall gentleness: CL drop within 3 deg after the peak
    after = (a > a[i_max]) & (a <= a[i_max] + 3)
    m["stall_drop"] = float(cl[i_max] - cl[after].min()) if after.any() else float("nan")
    return m


def main():
    results = {}
    polars = {}
    for name in CANDIDATES:
        af = asb.Airfoil(name).repanel(160)
        tc = float(af.max_thickness())
        results[name] = {"tc": tc}
        for ncrit in NCRIT:
            for re in RE_LIST:
                try:
                    a, cl, cd, cm = run_xfoil(af, re, ncrit)
                except Exception as e:  # noqa: BLE001
                    print(f"  {name} Re={re:.0f} Ncrit={ncrit}: XFOIL failed ({e})")
                    continue
                key = f"Re{int(re/1e3)}k_N{int(ncrit)}"
                results[name][key] = metrics(a, cl, cd, cm)
                polars[(name, re, ncrit)] = (a, cl, cd, cm)
                mm = results[name][key]
                if mm:
                    print(f"{name:10s} {key:12s} CLmax={mm['clmax']:.2f} L/Dmax={mm['ld_max']:5.1f} "
                          f"Cd_band={mm['cd_band']:.4f} Cm0={mm['cm0']:+.3f}")

    # ---- scoring at the cruise Reynolds number (Re 250k), both transition cases ----
    rows = []
    for name, r in results.items():
        c9, c5 = r.get("Re250k_N9"), r.get("Re250k_N5")
        s150 = r.get("Re150k_N9")
        if not (c9 and c5 and s150):
            continue
        rows.append({
            "name": name,
            "tc": r["tc"],
            "cd_band_N9": c9["cd_band"],
            "cd_band_N5": c5["cd_band"],
            "clmax_150k": s150["clmax"],
            "endurance_N9": c9["endurance_max"],
            "ld_max_N9": c9["ld_max"],
            "cm0": c9["cm0"],
            "stall_drop": s150["stall_drop"],
        })

    def norm(vals, higher_better):
        v = np.asarray(vals, float)
        lo, hi = np.nanmin(v), np.nanmax(v)
        s = (v - lo) / (hi - lo) if hi > lo else np.ones_like(v)
        return s if higher_better else 1 - s

    # weights: cruise drag (smooth+rough) 40%, CLmax 20%, endurance 15%, |Cm0| 15%, stall 10%
    w = {"cd_band_N9": 0.20, "cd_band_N5": 0.20, "clmax_150k": 0.20, "endurance_N9": 0.15,
         "cm0abs": 0.15, "stall_drop": 0.10}
    cols = {
        "cd_band_N9": norm([x["cd_band_N9"] for x in rows], False),
        "cd_band_N5": norm([x["cd_band_N5"] for x in rows], False),
        "clmax_150k": norm([x["clmax_150k"] for x in rows], True),
        "endurance_N9": norm([x["endurance_N9"] for x in rows], True),
        "cm0abs": norm([abs(x["cm0"]) for x in rows], False),
        "stall_drop": norm([x["stall_drop"] for x in rows], False),
    }
    for i, x in enumerate(rows):
        x["score"] = float(sum(w[k] * cols[k][i] for k in w))
        x["eligible"] = x["tc"] >= MIN_TC - 1e-3
    rows.sort(key=lambda x: (not x["eligible"], -x["score"]))
    winner = rows[0]["name"]
    print("\nRanking:")
    for x in rows:
        print(f"  {x['name']:10s} score={x['score']:.3f} t/c={x['tc']:.3f} eligible={x['eligible']}")

    # ---- NeuralFoil cross-check on the top 3 ----
    nf_check = {}
    for x in rows[:3]:
        af = asb.Airfoil(x["name"])
        aero = nf.get_aero_from_airfoil(af, alpha=ALPHA, Re=2.5e5, model_size="large", n_crit=9)
        nf_check[x["name"]] = {"alpha": ALPHA.tolist(), "CL": aero["CL"].tolist(),
                               "CD": aero["CD"].tolist(), "confidence": aero["analysis_confidence"].tolist()}

    save_json("airfoils", {"metrics": results, "ranking": rows, "winner": winner,
                           "weights": w, "cl_band": CL_BAND, "re_list": RE_LIST, "nf_check": nf_check})

    # ---- figures ----
    top = [x["name"] for x in rows[:5]]
    fig, axs = plt.subplots(1, 3, figsize=(15, 4.8))
    for name in top:
        p = polars.get((name, 2.5e5, 9.0))
        if p is None:
            continue
        a, cl, cd, cm = p
        lw = 2.5 if name == winner else 1.2
        axs[0].plot(cd * 1e4, cl, lw=lw, label=name)
        axs[1].plot(a, cl, lw=lw, label=name)
        axs[2].plot(a, cl / cd, lw=lw, label=name)
    axs[0].axhspan(*CL_BAND, color="0.9", zorder=0)
    axs[0].set(xlabel="Cd (counts)", ylabel="Cl", title="Drag polar, Re 250k, Ncrit 9", xlim=(0, 300))
    axs[1].set(xlabel="alpha (deg)", ylabel="Cl", title="Lift curve")
    axs[2].set(xlabel="alpha (deg)", ylabel="L/D", title="Lift-to-drag")
    for ax in axs:
        ax.grid(alpha=0.3)
        ax.legend(fontsize=8)
    savefig(fig, "airfoil_polars_top5")

    # Re and roughness sensitivity of the winner
    fig, ax = plt.subplots(figsize=(6.5, 4.8))
    for re in RE_LIST:
        for ncrit, ls in ((9.0, "-"), (5.0, "--")):
            p = polars.get((winner, re, ncrit))
            if p is not None:
                ax.plot(p[2] * 1e4, p[1], ls, label=f"Re {re/1e3:.0f}k, Ncrit {ncrit:.0f}")
    nfw = nf_check.get(winner)
    if nfw:
        ax.plot(np.array(nfw["CD"]) * 1e4, nfw["CL"], ":", color="k", label="NeuralFoil Re 250k")
    ax.set(xlabel="Cd (counts)", ylabel="Cl", title=f"{winner}: Reynolds and transition sensitivity",
           xlim=(0, 300))
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8)
    savefig(fig, "airfoil_winner_sensitivity")

    # airfoil shapes
    fig, ax = plt.subplots(figsize=(9, 3))
    for name in top:
        c = asb.Airfoil(name).coordinates
        ax.plot(c[:, 0], c[:, 1], lw=2.5 if name == winner else 1, label=name)
    ax.set_aspect("equal")
    ax.legend(fontsize=8, ncol=5)
    ax.grid(alpha=0.3)
    savefig(fig, "airfoil_shapes")


if __name__ == "__main__":
    main()
