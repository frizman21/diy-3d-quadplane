"""Structural sizing of the COTS carbon members.

1. Wing spar: Schrenk lift distribution at ultimate load (n_lim x 1.5), bending stress and
   deflection of the roll-wrapped spar tube (params.Wing.spar_od/id) against the candidate
   sizes; check at the spar end (outer panel joint).
2. Booms: motor-overhang bending at max thrust, and the first bending mode of the motor on
   the boom overhang vs the lift-prop 1P/2P excitation band (vibration is the real driver).
3. Hover case: wing centre section bending from lift motors carrying the fuselage mass.
Material: roll-wrapped CF tube, E = 70 GPa (lower bound) / 90 GPa (nominal),
design allowable 400 MPa (knock-down from ~700 MPa flexural strength for local crushing at
clamps and manufacturing variability).
"""

import numpy as np

from analysis.common import G, load_json, plt, save_json, savefig
from quadplane.params import AIRCRAFT as AC

E_LOW, E_NOM = 70e9, 90e9
SIGMA_ALLOW = 400e6
TUBES = {  # od, id (m), source
    "16x14": (0.016, 0.014), "18x16": (0.018, 0.016), "20x18": (0.020, 0.018),
    "22x20": (0.022, 0.020), "25x23": (0.025, 0.023), "28x26": (0.028, 0.026),
    "30x28": (0.030, 0.028), "25x22": (0.025, 0.022),
}
SPAR_CANDIDATES = ("16x14", "18x16", "20x18", "22x20")
RPM_BAND_MARGIN = 0.12  # hover 1P band: rear-motor rpm -12% to front-motor rpm +12% (gusts, light/heavy)
MODE_SEPARATION = 1.25  # first boom mode at least 25% above the top of the 1P band
MOUNT_MASS = 0.040  # printed motor mount on the boom tip (CAD)


def tube_name(od, id_):
    return f"{od * 1000:.0f}x{id_ * 1000:.0f}"

RHO_CF = 1550.0


def I_tube(od, id_):
    return np.pi / 64 * (od ** 4 - id_ ** 4)


def mass_per_m(od, id_):
    return RHO_CF * np.pi / 4 * (od ** 2 - id_ ** 2)


def chord(y):
    w = AC.wing
    y = np.abs(y)
    return np.where(y <= w.center_span / 2, w.root_chord,
                    w.root_chord + (w.tip_chord - w.root_chord) * (y - w.center_span / 2) / w.outer_span)


def spar(mass_design):
    w, ms = AC.wing, AC.mission
    n_ult = ms.load_factor_limit * ms.safety_factor
    y = np.linspace(0, w.semi_span, 400)
    c = chord(y)
    ell = 4 * w.area / (np.pi * w.span) * np.sqrt(1 - (y / w.semi_span) ** 2)
    schrenk = 0.5 * (c + ell)
    L_half = n_ult * mass_design * G / 2
    # inertia relief from boom+motors (conservative: only lift motors+booms at y_boom)
    q = schrenk / np.trapezoid(schrenk, y) * L_half  # N/m
    # shear and moment from tip inward
    V = np.array([np.trapezoid(q[i:], y[i:]) for i in range(len(y))])
    Mb = np.array([np.trapezoid(q[i:] * (y[i:] - y[i]), y[i:]) for i in range(len(y))])
    od, id_ = w.spar_od, w.spar_id
    I = I_tube(od, id_)
    sigma = Mb * (od / 2) / I
    # spar extent from the CAD geometry check (straight spar inside the tapering section)
    y_end = w.spar_half_length
    i_end = int(np.searchsorted(y, y_end))
    # limit-load deflection (integrate curvature), spar only, lower-bound E
    M_lim = Mb / ms.safety_factor
    kappa = M_lim / (E_LOW * I)
    slope = np.concatenate([[0], np.cumsum(0.5 * (kappa[1:] + kappa[:-1]) * np.diff(y))])
    defl = np.concatenate([[0], np.cumsum(0.5 * (slope[1:] + slope[:-1]) * np.diff(y))])
    # outer panel: bending at y_end carried by the tip tube
    od2, id2 = w.tip_spar_od, w.tip_spar_id
    sigma_outer = Mb[i_end] * (od2 / 2) / I_tube(od2, id2)
    res = {
        "n_ultimate": n_ult, "root_moment_ult_nm": float(Mb[0]), "root_shear_ult_n": float(V[0]),
        "root_stress_mpa": float(sigma[0] / 1e6), "ms_root": float(SIGMA_ALLOW / sigma[0] - 1),
        "spar_end_y": y_end, "moment_at_spar_end_nm": float(Mb[i_end]),
        "outer_tube": f"{od2*1000:.0f}x{id2*1000:.0f}", "outer_stress_mpa": float(sigma_outer / 1e6),
        "ms_outer": float(SIGMA_ALLOW / sigma_outer - 1),
        "spar_end_deflection_limit_mm": float(defl[i_end] * 1000),
        "spar_length_m": 2 * y_end, "spar_tube": tube_name(od, id_),
        "spar_i_mm4": float(I * 1e12), "spar_kg": float(mass_per_m(od, id_) * 2 * y_end),
        "candidates": [{"tube": n, "root_stress_mpa": float(Mb[0] * (TUBES[n][0] / 2) / I_tube(*TUBES[n]) / 1e6),
                        "ms_root": float(SIGMA_ALLOW / (Mb[0] * (TUBES[n][0] / 2) / I_tube(*TUBES[n])) - 1),
                        "kg": float(mass_per_m(*TUBES[n]) * 2 * y_end)} for n in SPAR_CANDIDATES],
    }
    return res, (y, Mb, sigma, defl)


def boom_vibration(hover_pt):
    """Front motor on the boom overhang ahead of the wing LE: cantilever with tip mass.
    Rayleigh: f = 1/(2 pi) sqrt(3EI / (L^3 (m_tip + 0.236 m_beam)))."""
    L = AC.x_lift_front  # overhang from wing LE (boom is clamped across the wing chord)
    from analysis import mass as M
    from analysis.hover import OPTIONS, SELECTED
    m_tip = M.LIFT_MOTOR_MASS + M.LIFT_PROP_MASS + MOUNT_MASS  # motor + prop + printed mount
    rpm_hover = (hover_pt["rear_rpm"] * (1 - RPM_BAND_MARGIN), hover_pt["front_rpm"] * (1 + RPM_BAND_MARGIN))
    f1p = np.array(rpm_hover) / 60
    t_max = OPTIONS[SELECTED].max_g / 1000 * G
    out = []
    for name, (od, id_) in TUBES.items():
        I = I_tube(od, id_)
        mb = mass_per_m(od, id_) * L
        f = [1 / (2 * np.pi) * np.sqrt(3 * E * I / (L ** 3 * (m_tip + 0.236 * mb))) for E in (E_LOW, E_NOM)]
        clear = (f[0] > MODE_SEPARATION * f1p[1]) or (f[1] < f1p[0] / MODE_SEPARATION)
        sigma = t_max * L * (od / 2) / I * AC.mission.safety_factor
        out.append({"tube": name, "kg_per_m": mass_per_m(od, id_), "f1_low_hz": f[0], "f1_nom_hz": f[1],
                    "clear_of_1p": bool(clear), "stress_ult_mpa": sigma / 1e6,
                    "separation": f[0] / f1p[1],
                    "selected": name == tube_name(AC.booms.tube_od, AC.booms.tube_id)})
    return out, f1p.tolist(), {"overhang_m": L, "tip_mass_kg": m_tip}


def main():
    stab = load_json("stability")
    m = max(stab["mass"], AC.mission.design_mass)
    sres, (y, Mb, sigma, defl) = spar(m)
    booms, f1p, boom_model = boom_vibration(load_json("propulsion")["hover_point"])
    for k, v in sres.items():
        print(f"{k:32s} {v}")
    for b in booms:
        print(b)
    print("1P band (Hz):", f1p)
    # hover: front/rear motor thrust at 2 g manoeuvre into boom/wing joint
    save_json("structures", {"spar": sres, "booms": booms, "hover_1p_band_hz": f1p,
                             "boom_model": boom_model, "design_mass": m,
                             "E_low": E_LOW, "E_nom": E_NOM, "sigma_allow_mpa": SIGMA_ALLOW / 1e6})

    fig, axs = plt.subplots(1, 3, figsize=(15, 4.3))
    axs[0].plot(y, Mb)
    axs[0].axvline(sres["spar_end_y"], color="r", ls="--", label="main spar end")
    axs[0].set(xlabel="y (m)", ylabel="N m", title=f"Bending moment, ultimate n={sres['n_ultimate']:.0f}")
    axs[1].plot(y, sigma / 1e6)
    axs[1].axhline(SIGMA_ALLOW / 1e6, color="r", ls="--", label="allowable")
    axs[1].set(xlabel="y (m)", ylabel="MPa", title=f"Spar bending stress ({sres['spar_tube']})")
    names = [b["tube"] for b in booms]
    axs[2].bar(names, [b["f1_low_hz"] for b in booms], color="0.7", label="E=70 GPa")
    axs[2].plot(names, [b["f1_nom_hz"] for b in booms], "ko", label="E=90 GPa")
    axs[2].axhspan(*f1p, color="r", alpha=0.2, label="hover 1P band")
    axs[2].axhspan(f1p[1], MODE_SEPARATION * f1p[1], color="orange", alpha=0.2, label="25% margin")
    axs[2].set(ylabel="Hz", title="Front-motor boom mode vs prop 1P")
    for ax in axs:
        ax.grid(alpha=0.3)
        ax.legend(fontsize=8)
    savefig(fig, "structures")


if __name__ == "__main__":
    main()
