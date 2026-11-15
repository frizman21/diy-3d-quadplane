"""Flight performance: drag polar, power required, characteristic speeds, mission energy.

Uses the selected geometry (params), the mass/CG from the stability run, AeroBuildup drag
(NeuralFoil sections + body/boom drag + excrescence allowance). Trim drag is included via
the tail's share in AeroBuildup at the AVL trim incidence (elevator ~0 at cruise).
"""

import aerosandbox as asb
import numpy as np

from analysis import mass as M
from analysis.common import RHO, G, load_json, plt, save_json, savefig
from analysis.hover import hover_power
from analysis.model import EXCRESCENCE_CD, airplane
from quadplane.params import AIRCRAFT as AC

ETA_CRUISE = 0.55  # prop 0.68 x motor 0.83 x ESC 0.97 at part load (conservative vs sizing 0.62)
BATTERY_WH = 6 * 3.6 * 13.5  # 6S3P Molicel P45B (D-028)
CLMAX_3D_FACTOR = 0.88


def main():
    stab = load_json("stability")
    items = M.components(battery_x=stab["battery_x"])
    m, cg, _ = M.summarize(items)
    W = m * G
    w = AC.wing
    S = w.area
    ap = airplane()
    alphas = np.linspace(-5, 13, 37)
    op = asb.OperatingPoint(atmosphere=asb.Atmosphere(altitude=0), velocity=16.0, alpha=alphas)
    r = asb.AeroBuildup(ap, op, xyz_ref=[-cg[0], 0, cg[2]]).run()
    CL = np.asarray(r["CL"])
    CD = np.asarray(r["CD"]) + EXCRESCENCE_CD
    # drag breakdown at cruise CL via component runs
    sizing = load_json("sizing")
    clmax = CLMAX_3D_FACTOR * sizing["clmax2d"]

    # parabolic fit CD = CD0 + k CL^2 over attached range
    mask = (CL > 0.1) & (CL < 0.9)
    k, _, cd0 = np.polyfit(CL[mask], CD[mask], 2)
    e_eff = 1 / (np.pi * w.aspect_ratio * k)

    v = np.linspace(9, 30, 85)
    q = 0.5 * RHO * v ** 2
    cl_req = W / (q * S)
    order = np.argsort(CL)
    cd_req = np.interp(cl_req, CL[order], CD[order], right=np.nan)
    cd_req[cl_req > 0.92 * clmax] = np.nan
    drag = q * S * cd_req
    p_aero = drag * v
    p_elec = p_aero / ETA_CRUISE + 10.0  # + avionics
    vs = np.sqrt(2 * W / (RHO * S * clmax))
    i_end = np.nanargmin(p_elec)
    i_rng = np.nanargmin(p_elec / v)
    ld = W / drag
    usable = BATTERY_WH * (1 - AC.mission.reserve_frac)

    # mission: 60 s hover takeoff + 20 s transition + cruise + 20 s back-transition + 60 s landing hover
    p_hover = hover_power(m, front_share=stab["hover_front_share"])
    e_vtol = p_hover * (60 + 60 + 0.6 * 40) / 3600  # transitions ~60% hover power for 40 s total
    e_cruise = usable - e_vtol
    t_end = e_cruise / p_elec[i_end] * 60
    v_cruise = 18.0
    p_cruise = float(np.interp(v_cruise, v, p_elec))
    t_cruise = e_cruise / p_cruise * 60
    range_km = e_cruise / p_elec[i_rng] * v[i_rng] * 3.6

    # climb rate at 15 m/s with full pusher (dynamic thrust ~ T0 (1 - V/Vp))
    prop = load_json("propulsion")["pusher"]
    t0 = prop["t_static_req_n"] / 1.0
    vp = 28.0
    thrust = np.clip(t0 * (1 - v / vp), 0, None)
    roc = (thrust - drag) * v / W
    v_max = float(v[np.nanargmax(np.where(thrust - drag > 0, v, np.nan))]) if np.any(thrust > drag) else float("nan")

    res = {
        "mass": m, "mass_lb": m / 0.45359237, "S": S, "AR": w.aspect_ratio, "mac": w.mac, "wing_loading_gdm2": m * 1e3 / (S * 1e2),
        "clmax_3d": clmax, "vs": vs, "cd0": cd0, "k": k, "e_eff": e_eff,
        "ld_max": float(np.nanmax(ld)), "v_ld_max": float(v[np.nanargmax(ld)]),
        "v_min_power": float(v[i_end]), "p_min_elec": float(p_elec[i_end]),
        "v_max_range": float(v[i_rng]), "p_at_range": float(p_elec[i_rng]),
        "v_cruise": v_cruise, "p_cruise_elec": p_cruise, "cl_cruise": float(W / (0.5 * RHO * 18 ** 2 * S)),
        "p_15_elec": float(np.interp(15.0, v, p_elec)), "cruise_endurance_min_at_15": e_cruise / float(np.interp(15.0, v, p_elec)) * 60,
        "usable_wh": usable, "drag_18_n": float(np.interp(18.0, v, drag)),
        "p_hover": p_hover, "hover_min": usable / p_hover * 60,
        "e_vtol_wh": e_vtol, "cruise_endurance_min_at_vmp": t_end, "cruise_endurance_min_at_18": t_cruise,
        "range_km_at_vmr": range_km, "roc_max": float(np.nanmax(roc)), "v_roc_max": float(v[np.nanargmax(roc)]),
        "v_max_level": v_max, "hover_to_cruise_power_ratio": p_hover / p_cruise,
        "transition_speed_rec": 1.25 * vs, "arspd_fbw_min_rec": round(1.25 * vs), "eta_cruise": ETA_CRUISE,
    }
    save_json("performance", res)
    for k_, v_ in res.items():
        print(f"{k_:32s} {v_:.4g}" if isinstance(v_, float) else f"{k_:32s} {v_}")

    fig, axs = plt.subplots(1, 3, figsize=(16, 4.6))
    axs[0].plot(CD * 1e4, CL, "k")
    clf = np.linspace(0, 1.0, 50)
    axs[0].plot((cd0 + k * clf ** 2) * 1e4, clf, "r--", label=f"CD0={cd0:.4f}, e={e_eff:.2f}")
    axs[0].set(xlabel="CD (counts)", ylabel="CL", title="Whole-aircraft drag polar")
    axs[0].legend()
    axs[1].plot(v, p_elec, "k", label="battery power, cruise")
    axs[1].axhline(p_hover, color="r", ls="--", label=f"hover {p_hover:.0f} W")
    axs[1].axvline(vs, color="0.5", ls=":", label=f"Vs {vs:.1f} m/s")
    axs[1].plot(v[i_end], p_elec[i_end], "go", label=f"min power {v[i_end]:.1f} m/s")
    axs[1].plot(v[i_rng], p_elec[i_rng], "bs", label=f"max range {v[i_rng]:.1f} m/s")
    axs[1].set(xlabel="airspeed (m/s)", ylabel="W", title="Power required", ylim=(0, 1.15 * p_hover))
    axs[1].legend(fontsize=8)
    axs[2].plot(v, roc, "k")
    axs[2].set(xlabel="airspeed (m/s)", ylabel="m/s", title="Rate of climb (pusher only)")
    for ax in axs:
        ax.grid(alpha=0.3)
    savefig(fig, "performance")


if __name__ == "__main__":
    main()
