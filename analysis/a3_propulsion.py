"""Propulsion and energy: lift-prop size, battery configuration, pusher sizing.

Hover: calibrated momentum theory (analysis/hover.py) against the seller's 6S bench data
(SunnySky V2806 KV400 + 12x5 selected; MN3508 KV380 kept in the trade as the 3.3 kg choice).
Pusher: static-thrust requirement from the transition, prop/KV selection from
the static thrust coefficient and the cruise pitch-speed ratio.
"""

import numpy as np

from analysis import mass as M
from analysis.common import RHO, G, plt, save_json, savefig
from analysis.hover import OPTIONS, SELECTED, hover_power, hover_rpm, k_factor, motor_power
from quadplane.params import AIRCRAFT as AC

# Battery options: (label, Wh nominal, pack mass kg, continuous A)
BATTERIES = [
    ("6S1P Molicel P30B", 6 * 3.6 * 3.0, 0.330, 36),
    ("6S1P Molicel P50B", M.BATTERY_WH, M.BATTERY_MASS, 60),
    ("6S LiPo 5000 mAh", 111.0, 0.700, 250),
    ("6S2P Molicel P50B", 6 * 3.6 * 10.0, 0.860, 120),
]
SELECTED_BATTERY = "6S1P Molicel P50B"
V_BENCH = 22.2  # bench voltage of the motor tables
KV_LOADED = 0.85  # in-flight prop rpm / no-load rpm at full throttle
SEL = OPTIONS[SELECTED]


def battery_trade(front_share: float, pusher_max_w: float):
    base_items = M.components()
    base_mass, _, _ = M.summarize(base_items)
    rows = []
    peak_a = (4 * SEL.max_w + pusher_max_w) / V_BENCH  # all five motors at full throttle
    for label, wh, mb, amps in BATTERIES:
        m = base_mass - M.BATTERY_MASS + mb
        p = hover_power(m, front_share=front_share)
        usable = wh * (1 - AC.mission.reserve_frac)
        rows.append({"battery": label, "wh": wh, "pack_kg": mb, "auw": m, "auw_lb": m / 0.45359237,
                     "hover_w": p, "hover_min": usable / p * 60, "hover_amps": p / 21.0,
                     "max_cont_a": amps, "peak_a": peak_a, "peak_ok": bool(peak_a <= amps),
                     "tw_front_motor": SEL.max_g / (m * front_share / 2 * 1000),
                     "meets_15min": bool(usable / p * 60 >= 15)})
    return rows


def prop_trade(mass: float, front_share: float):
    rows = []
    for key, o in OPTIONS.items():
        # swapping the motor/prop changes the take-off mass (four motors and props)
        m = mass + 4 * (o.motor_kg + o.prop_kg - SEL.motor_kg - SEL.prop_kg)
        p = hover_power(m, key, front_share=front_share)
        t_front = m * front_share / 2 * 1000  # g per front motor (no download)
        R = o.d_in * 0.0254 / 2
        length = AC.overall_length + 4 * (R - AC.lift.radius)  # each radius step moves front tip and tail
        rows.append({"option": o.label, "selected": key == SELECTED, "prop_in": o.d_in, "auw": m,
                     "hover_w": p, "fm_eta": 1 / k_factor(key), "tw_total": o.max_g * 4 / (m * 1000),
                     "tw_front_motor": o.max_g / t_front, "overall_length": length,
                     "hover_min": M.BATTERY_WH * (1 - AC.mission.reserve_frac) / p * 60,
                     "bench_ratio_front": t_front * 1.04 / o.bench_g,
                     "disk_loading_n_m2": m * G / (4 * np.pi * R ** 2)})
    return rows


def pusher(mass: float, drag_18: float):
    """Size the pusher. Transition: accelerate 0 -> 14 m/s in <= 6 s with drag, plus 30% margin
    -> static thrust requirement. Cruise climb: 3 m/s at 18 m/s."""
    v_tr, t_tr = 14.0, 6.0
    f_transition = mass * v_tr / t_tr + 0.5 * drag_18 * (v_tr / 18) ** 2
    # in-flight pitch speed at full throttle: the thrust falls to zero near this speed
    v_pitch = AC.pusher.prop_pitch * AC.pusher.motor_kv * V_BENCH * KV_LOADED / 60
    t_static_req = 1.3 * f_transition / (1 - v_tr / 2 / v_pitch)  # linear thrust lapse
    climb_thrust = drag_18 + mass * G * 3.0 / 18.0
    D = AC.pusher.prop_diameter
    ct0 = 0.105  # 12x8 static thrust coefficient (UIUC prop database order, APC E props)
    cp0 = 0.060
    n = np.sqrt(t_static_req / (ct0 * RHO * D ** 4))
    rpm = n * 60
    p_shaft = cp0 * RHO * n ** 3 * D ** 5
    kv_needed = rpm / (0.80 * 21.0)
    pitch_speed = AC.pusher.prop_pitch * n
    return {"f_transition_n": f_transition, "t_static_req_n": t_static_req,
            "t_static_req_g": t_static_req / G * 1000, "climb_thrust_n": climb_thrust,
            "static_rpm": rpm, "static_shaft_w": p_shaft, "static_elec_w": p_shaft / 0.82,
            "kv_needed": kv_needed, "kv_selected": AC.pusher.motor_kv, "pitch_speed_static_ms": pitch_speed,
            "pitch_speed_flight_ms": v_pitch,
            "cruise_thrust_n": drag_18}


def main():
    from analysis.common import load_json
    stab = load_json("stability")
    front_share = stab["hover_front_share"]
    items = M.components(battery_x=stab["battery_x"])
    mass, cg, _ = M.summarize(items)

    props = prop_trade(mass, front_share)
    sizing = load_json("sizing")
    drag_18 = sizing["best"]["p18"] * sizing["eta_pusher"] / 18.0
    push = pusher(mass, drag_18)
    batts = battery_trade(front_share, push["static_elec_w"])

    for r in props:
        print("prop", {k: (round(v, 3) if isinstance(v, float) else v) for k, v in r.items()})
    for r in batts:
        print("batt", {k: (round(v, 2) if isinstance(v, float) else v) for k, v in r.items()})
    print("pusher", {k: round(v, 2) for k, v in push.items()})

    # per-motor hover point (front motors carry front_share)
    t_front_g = mass * 1000 * front_share / 2 * 1.04
    t_rear_g = mass * 1000 * (1 - front_share) / 2 * 1.04
    hover_pt = {"front_g": t_front_g, "rear_g": t_rear_g, "front_w": motor_power(t_front_g),
                "rear_w": motor_power(t_rear_g), "front_rpm": hover_rpm(t_front_g),
                "rear_rpm": hover_rpm(t_rear_g), "front_throttle_frac_thrust": t_front_g / SEL.max_g,
                "hover_w": hover_power(mass, front_share=front_share)}
    print("hover per motor", {k_: round(v, 2) for k_, v in hover_pt.items()})

    save_json("propulsion", {"mass": mass, "mass_lb": mass / 0.45359237, "front_share": front_share,
                             "props": props, "batteries": batts, "pusher": push,
                             "hover_point": hover_pt, "selected_lift": SEL.label,
                             "selected_battery": SELECTED_BATTERY,
                             "bench": {k_: [o.bench_g, o.bench_w] for k_, o in OPTIONS.items()}})

    # figure: hover endurance vs battery
    fig, ax = plt.subplots(figsize=(7, 4.5))
    for r in batts:
        ax.bar(r["battery"].replace(" (", "\n("), r["hover_min"],
               color="tab:green" if r["battery"] == SELECTED_BATTERY else "0.6")
        ax.text(r["battery"].replace(" (", "\n("), r["hover_min"] + 0.5,
                f"{r['hover_min']:.1f} min\n{r['auw']:.2f} kg", ha="center", fontsize=8)
    ax.axhline(15, color="r", ls="--", label="PERF-1: 15 min")
    ax.set(ylabel="hover endurance to 20% reserve (min)", title=f"Battery trade ({SEL.label})")
    ax.tick_params(axis="x", labelsize=7)
    ax.legend()
    savefig(fig, "propulsion_battery_trade")

    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    masses = np.linspace(0.75 * mass, 1.15 * mass, 30)
    for key, o in OPTIONS.items():
        ax.plot(masses, [hover_power(m_, key, front_share=front_share) for m_ in masses], label=o.label)
    ax.axvline(mass, color="k", ls=":", label="take-off mass")
    ax.set(xlabel="all-up mass (kg)", ylabel="hover electrical power (W)",
           title="Hover power (calibrated momentum theory)")
    ax.grid(alpha=0.3)
    ax.legend()
    savefig(fig, "propulsion_hover_power")


if __name__ == "__main__":
    main()
