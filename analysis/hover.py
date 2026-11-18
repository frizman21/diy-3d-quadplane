"""Hover power model: actuator-disk momentum theory calibrated to manufacturer bench data.

P_elec = k * T^1.5 / sqrt(2 rho A), with k = 1 / (FM * eta_motor * eta_esc) fitted to the
manufacturer's bench point nearest the hover thrust (selected: SunnySky V2806 KV400 +
12x5 on 6S, 600 g at 71 W). Hover download from booms/motor pods under the disk and a
battery-voltage-sag allowance are applied explicitly.
"""

from dataclasses import dataclass

import numpy as np

from analysis.common import RHO, G
from quadplane.params import AIRCRAFT as AC


@dataclass(frozen=True)
class LiftOption:
    """One motor + prop combination, manufacturer bench data at 6S (22.2 V)."""
    label: str
    motor: str
    d_in: float
    bench_g: float  # thrust at the bench point nearest hover
    bench_w: float  # electrical power at that point
    bench_rpm: float  # rpm at that point (0 = not published)
    max_g: float  # full-throttle thrust
    max_w: float  # full-throttle electrical power
    motor_kg: float  # incl. cable
    prop_kg: float


# docs/cots-selection.md §2 lists the sources.
OPTIONS = {
    "MN3508-14": LiftOption("MN3508 KV380 + 14x4.8", "MN3508 KV380", 14, 710, 64.4, 0, 1730, 310, 0.103, 0.020),
    # SunnySky V2806 KV400, the seller's bench tables at 22.2 V with EOLO CN props. Motor mass
    # includes 3 g of cable; the 11 and 13 in prop masses are estimates.  # VERIFY
    "V2806-11": LiftOption("V2806 KV400 + 11x4.5", "SunnySky V2806 KV400", 11, 600, 71, 5620, 834, 115, 0.050, 0.011),
    "V2806-12": LiftOption("V2806 KV400 + 12x5", "SunnySky V2806 KV400", 12, 600, 71, 4828, 1120, 190, 0.050, 0.014),
    "V2806-13": LiftOption("V2806 KV400 + 13x5", "SunnySky V2806 KV400", 13, 600, 69, 4140, 1080, 173, 0.050, 0.015),
}
SELECTED = "V2806-12"  # D-037; its diameter must match params.Lift.prop_diameter
assert abs(OPTIONS[SELECTED].d_in * 0.0254 - AC.lift.prop_diameter) < 1e-6

DOWNLOAD = 0.04  # thrust lost to boom + motor pod blockage under the disk (~4%)
AVIONICS_W = 10.0
SAG_FACTOR = 1.04  # mean pack voltage below the 22.2 V bench voltage -> more current


def disk_area(d_in: float) -> float:
    return np.pi * (d_in * 0.0254 / 2) ** 2


def k_factor(option: str = SELECTED) -> float:
    o = OPTIONS[option]
    T = o.bench_g / 1000 * G
    return o.bench_w / (T ** 1.5 / np.sqrt(2 * RHO * disk_area(o.d_in)))


def motor_power(thrust_g: float, option: str = SELECTED) -> float:
    """Electrical power (W) of one motor at a thrust (g), bench voltage, no sag."""
    T = thrust_g / 1000 * G
    return float(k_factor(option) * T ** 1.5 / np.sqrt(2 * RHO * disk_area(OPTIONS[option].d_in)))


def hover_rpm(thrust_g: float, option: str = SELECTED) -> float:
    """rpm at a thrust (g): rpm ~ sqrt(T) from the bench point (fixed-pitch prop, static)."""
    o = OPTIONS[option]
    return float(o.bench_rpm * np.sqrt(thrust_g / o.bench_g))


def hover_power(mass_kg: float, option: str = SELECTED, front_share: float = 0.5) -> float:
    """Electrical power (W) to hover on four rotors, including download, sag and avionics.
    front_share: fraction of weight carried by the front pair (CG offset from lift centroid)."""
    thrust_g = mass_kg * 1000 * (1 + DOWNLOAD)
    shares = [front_share / 2] * 2 + [(1 - front_share) / 2] * 2
    p = sum(motor_power(thrust_g * s, option) for s in shares)
    return float(p * SAG_FACTOR + AVIONICS_W)


if __name__ == "__main__":
    for key, o in OPTIONS.items():
        print(f"{o.label:24s} k = {k_factor(key):.3f}  FM*eta = {1 / k_factor(key):.3f}  "
              f"hover {AC.mission.target_mass:.2f} kg = {hover_power(AC.mission.target_mass, key):.0f} W")
