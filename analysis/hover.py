"""Hover power model: actuator-disk momentum theory calibrated to manufacturer bench data.

P_elec = k * T^1.5 / sqrt(2 rho A), with k = 1 / (FM * eta_motor * eta_esc) fitted to the
T-Motor MN3508 KV380 + P14x4.8 6S bench point (710 g at 64.4 W). Hover download from
booms/motor pods under the disk and a battery-voltage-sag allowance are applied explicitly.
"""

import numpy as np

from analysis.common import RHO, G
from quadplane.params import AIRCRAFT as AC

# Manufacturer bench points (6S, 22.2 V): (prop dia in, thrust g, electrical W)
BENCH = {
    13: (810, 82.0),
    14: (710, 64.4),
    15: (820, 79.9),
}
DOWNLOAD = 0.04  # thrust lost to boom + motor pod blockage under the disk (~4%)
AVIONICS_W = 10.0
SAG_FACTOR = 1.04  # mean pack voltage below the 22.2 V bench voltage -> more current


def k_factor(d_in: float) -> float:
    t_g, p = BENCH[int(round(d_in))]
    T = t_g / 1000 * G
    A = np.pi * (d_in * 0.0254 / 2) ** 2
    p_ideal = T ** 1.5 / np.sqrt(2 * RHO * A)
    return p / p_ideal


def hover_power(mass_kg: float, d_in: float = 14.0, n_rotors: int = 4,
                front_share: float = 0.5) -> float:
    """Electrical power (W) to hover, including download, sag and avionics.
    front_share: fraction of weight carried by the front pair (CG offset from lift centroid)."""
    k = k_factor(d_in)
    A = np.pi * (d_in * 0.0254 / 2) ** 2
    W = mass_kg * G * (1 + DOWNLOAD)
    shares = [front_share / 2] * 2 + [(1 - front_share) / 2] * 2
    p = sum(k * (W * s) ** 1.5 / np.sqrt(2 * RHO * A) for s in shares)
    _ = n_rotors
    return float(p * SAG_FACTOR + AVIONICS_W)


if __name__ == "__main__":
    for d in (13, 14, 15):
        print(d, "in: k =", round(k_factor(d), 3), " FM*eta =", round(1 / k_factor(d), 3),
              " hover 2.9 kg =", round(hover_power(2.9, d)), "W")
    _ = AC
