"""Propulsion and energy: lift-prop size, battery configuration, pusher sizing.

Hover: calibrated momentum theory (analysis/hover.py) against T-Motor MN3508 KV380 6S
bench data. Pusher: static-thrust requirement from the transition, prop/KV selection from
the static thrust coefficient and the cruise pitch-speed ratio.
"""

import numpy as np

from analysis import mass as M
from analysis.common import RHO, G, plt, save_json, savefig
from analysis.hover import BENCH, hover_power, k_factor
from quadplane.params import AIRCRAFT as AC

# Battery options: (label, Wh nominal, pack mass kg, continuous A)
BATTERIES = [
    ("6S1P Molicel P50B", 6 * 3.6 * 5.0, 0.455, 60),
    ("6S LiPo 5000 mAh (CNHL G+)", 111.0, 0.811, 500),
    ("6S2P Molicel P45B", 6 * 3.6 * 9.0, 0.860, 90),
    ("6S2P Molicel P50B", 6 * 3.6 * 10.0, 0.880, 120),
]
BASE_BATTERY = 0.860
MAX_THRUST_G = {13: 1380, 14: 1730, 15: 1880}  # 6S full throttle, manufacturer data
LIFT_MOTOR_LIMIT_W = 310  # MN3508 KV380 rated 180 s max


def battery_trade(front_share: float):
    base_items = M.components()
    base_mass, _, _ = M.summarize(base_items)
    rows = []
    for label, wh, mb, amps in BATTERIES:
        m = base_mass - BASE_BATTERY + mb
        p = hover_power(m, 14, front_share=front_share)
        usable = wh * (1 - AC.mission.reserve_frac)
        rows.append({"battery": label, "wh": wh, "pack_kg": mb, "auw": m, "hover_w": p,
                     "hover_min": usable / p * 60, "hover_amps": p / 21.0,
                     "max_cont_a": amps, "meets_15min": usable / p * 60 >= 15})
    return rows


def prop_trade(mass: float, front_share: float):
    rows = []
    for d in (13, 14, 15):
        p = hover_power(mass, d, front_share=front_share)
        t_front = mass * front_share / 2 * 1000  # g per front motor (no download)
        tw = MAX_THRUST_G[d] * 4 / (mass * 1000)
        tw_front = MAX_THRUST_G[d] / t_front
        R = d * 0.0254 / 2
        length = (R + AC.lift.tip_gap) + R + (AC.wing.root_chord + R + AC.lift.tip_gap) + R \
            + AC.lift.tip_gap + AC.tail.v_root_chord
        rows.append({"prop_in": d, "hover_w": p, "fm_eta": 1 / k_factor(d), "tw_total": tw,
                     "tw_front_motor": tw_front, "overall_length": length,
                     "disk_loading_n_m2": mass * G / (4 * np.pi * R ** 2)})
    return rows


def pusher(mass: float, drag_18: float):
    """Size the pusher. Transition: accelerate 0 -> 14 m/s in <= 6 s with drag, plus 30% margin
    -> static thrust requirement. Cruise climb: 3 m/s at 18 m/s."""
    v_tr, t_tr = 14.0, 6.0
    f_transition = mass * v_tr / t_tr + 0.5 * drag_18 * (v_tr / 18) ** 2
    t_static_req = 1.3 * f_transition / (1 - v_tr / 2 / 25.0)  # linear thrust lapse, V_pitch 25
    climb_thrust = drag_18 + mass * G * 3.0 / 18.0
    D = AC.pusher.prop_diameter
    ct0 = 0.105  # APC 10x7E static thrust coefficient (UIUC prop database order)
    cp0 = 0.065
    n = np.sqrt(t_static_req / (ct0 * RHO * D ** 4))
    rpm = n * 60
    p_shaft = cp0 * RHO * n ** 3 * D ** 5
    kv_needed = rpm / (0.80 * 21.0)
    pitch_speed = AC.pusher.prop_pitch * n
    return {"f_transition_n": f_transition, "t_static_req_n": t_static_req,
            "t_static_req_g": t_static_req / G * 1000, "climb_thrust_n": climb_thrust,
            "static_rpm": rpm, "static_shaft_w": p_shaft, "static_elec_w": p_shaft / 0.82,
            "kv_needed": kv_needed, "pitch_speed_static_ms": pitch_speed,
            "cruise_thrust_n": drag_18}


def main():
    from analysis.common import load_json
    stab = load_json("stability")
    front_share = stab["hover_front_share"]
    items = M.components(battery_x=stab["battery_x"])
    mass, cg, _ = M.summarize(items)

    props = prop_trade(mass, front_share)
    batts = battery_trade(front_share)
    sizing = load_json("sizing")
    drag_18 = sizing["best"]["p18"] * sizing["eta_pusher"] / 18.0
    push = pusher(mass, drag_18)

    for r in props:
        print("prop", {k: round(v, 3) for k, v in r.items()})
    for r in batts:
        print("batt", {k: (round(v, 2) if isinstance(v, float) else v) for k, v in r.items()})
    print("pusher", {k: round(v, 2) for k, v in push.items()})

    # per-motor hover point (front motors carry front_share)
    t_front_g = mass * 1000 * front_share / 2 * 1.04
    t_rear_g = mass * 1000 * (1 - front_share) / 2 * 1.04
    k = k_factor(14)
    A = np.pi * (14 * 0.0254 / 2) ** 2

    def p_motor(tg):
        T = tg / 1000 * G
        return k * T ** 1.5 / np.sqrt(2 * RHO * A)

    hover_pt = {"front_g": t_front_g, "rear_g": t_rear_g, "front_w": p_motor(t_front_g),
                "rear_w": p_motor(t_rear_g), "front_throttle_frac_thrust": t_front_g / 1730}
    print("hover per motor", {k_: round(v, 2) for k_, v in hover_pt.items()})

    save_json("propulsion", {"mass": mass, "front_share": front_share, "props": props,
                             "batteries": batts, "pusher": push, "hover_point": hover_pt,
                             "bench": BENCH})

    # figure: hover endurance vs battery
    fig, ax = plt.subplots(figsize=(7, 4.5))
    for r in batts:
        ax.bar(r["battery"].replace(" (", "\n("), r["hover_min"],
               color="tab:green" if r["battery"].startswith("6S2P Molicel P45B") else "0.6")
        ax.text(r["battery"].replace(" (", "\n("), r["hover_min"] + 0.5,
                f"{r['hover_min']:.1f} min\n{r['auw']:.2f} kg", ha="center", fontsize=8)
    ax.axhline(15, color="r", ls="--", label="PERF-1: 15 min")
    ax.set(ylabel="hover endurance to 20% reserve (min)", title="Battery trade (14 in props)")
    ax.tick_params(axis="x", labelsize=7)
    ax.legend()
    savefig(fig, "propulsion_battery_trade")

    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    masses = np.linspace(2.2, 3.6, 30)
    for d in (13, 14, 15):
        ax.plot(masses, [hover_power(m_, d, front_share=front_share) for m_ in masses], label=f"{d} in")
    ax.axvline(mass, color="k", ls=":", label="design mass")
    ax.set(xlabel="all-up mass (kg)", ylabel="hover electrical power (W)",
           title="Hover power, MN3508 KV380 (calibrated momentum theory)")
    ax.grid(alpha=0.3)
    ax.legend()
    savefig(fig, "propulsion_hover_power")


if __name__ == "__main__":
    main()
