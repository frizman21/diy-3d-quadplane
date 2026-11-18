"""Mass and balance model.

Every item carries its mass and position (body frame, m, origin at the wing root LE).
COTS masses come from manufacturer data (docs/cots-selection.md). Printed-structure
masses are estimates from areal densities until the CAD exists; `printed_from_cad()`
replaces them with CAD volumes x material density.
"""

from dataclasses import dataclass

import numpy as np

from quadplane import hardware as HW
from quadplane.params import AIRCRAFT as AC

CARBON_DENSITY = 1550.0  # kg/m^3, roll-wrapped CF/epoxy tube
LWPLA_FOAMED = 0.75  # g/cm^3: LW-PLA printed at ~230 C (≈40% foaming); VERIFY on coupon
PLA_PETG = 1.25

# COTS masses (kg), docs/cots-selection.md. VERIFY on a scale when the parts arrive.
BATTERY_MASS = 0.450  # 6S1P Molicel P50B: 6 cells at 70 g plus leads and wrap (the seller ships it at 500 g)
BATTERY_WH = 6 * 3.6 * 5.0  # nominal energy of that pack (D-037)
LIFT_MOTOR_MASS = 0.050  # SunnySky V2806 KV400: 47 g on the listing, plus cable
LIFT_PROP_MASS = 0.013  # 12 in carbon-nylon multirotor prop
PUSHER_MOTOR_MASS = LIFT_MOTOR_MASS + 0.008  # a fifth V2806 KV400 with its prop adapter (D-037)
ESC_MASS = 0.008
# pack centre: its top sits 12 mm under the pod top (quadplane/cots.py)
BATTERY_Z = AC.fuselage.z_top - 0.012 - HW.BATTERY[2] / 2000


@dataclass
class Item:
    name: str
    mass: float  # kg
    x: float
    y: float = 0.0
    z: float = 0.0
    group: str = "misc"


def tube_mass(od: float, id_: float, length: float) -> float:
    return CARBON_DENSITY * np.pi / 4 * (od ** 2 - id_ ** 2) * length


def components(battery_mass: float = BATTERY_MASS, battery_x: float = -0.06,
               lift_motor_mass: float = LIFT_MOTOR_MASS, pusher_motor_mass: float = PUSHER_MOTOR_MASS,
               printed: dict | None = None) -> list[Item]:
    w, b, t = AC.wing, AC.booms, AC.tail
    xf, xr = AC.x_lift_front, AC.x_lift_rear
    zm = b.z + AC.lift.motor_height
    items: list[Item] = []

    # --- propulsion ---
    for s in (+1, -1):
        items += [
            Item("lift motor front", lift_motor_mass, xf, s * b.y, zm, "propulsion"),
            Item("lift motor rear", lift_motor_mass, xr, s * b.y, zm, "propulsion"),
            Item("lift prop front", LIFT_PROP_MASS, xf, s * b.y, zm + 0.02, "propulsion"),
            Item("lift prop rear", LIFT_PROP_MASS, xr, s * b.y, zm + 0.02, "propulsion"),
            Item("lift ESC front", ESC_MASS, xf - 0.08, s * b.y, b.z, "propulsion"),
            Item("lift ESC rear", ESC_MASS, xr + 0.08, s * b.y, b.z, "propulsion"),
        ]
    xp = AC.fuselage.x_tail
    items += [
        Item("pusher motor", pusher_motor_mass, xp - 0.02, 0, AC.pusher.z_thrust, "propulsion"),
        Item("pusher prop", 0.030, xp - 0.05, 0, AC.pusher.z_thrust, "propulsion"),
        Item("pusher ESC", ESC_MASS, xp + 0.06, 0, AC.pusher.z_thrust, "propulsion"),
    ]

    # --- energy ---
    items.append(Item("battery 6S1P Li-ion", battery_mass, battery_x, 0, BATTERY_Z, "battery"))

    # --- avionics ---
    items += [
        Item("flight controller", 0.030, -0.03, 0, -0.04, "avionics"),
        Item("GPS + compass (on a 60 mm mast, nose top)", 0.015, AC.fuselage.x_nose - 0.13, 0, 0.06, "avionics"),
        Item("ELRS receiver DBR4", 0.006, -0.15, 0, -0.03, "avionics"),
        Item("Remote ID module", 0.025, AC.fuselage.x_nose - 0.17, 0, -0.03, "avionics"),
        Item("airspeed sensor + pitot", 0.010, AC.fuselage.x_nose - 0.10, 0, -0.02, "avionics"),
        Item("camera Insta360 GO 3S", 0.039, AC.fuselage.x_nose - 0.04, 0, -0.06, "payload"),
    ]
    # servos: 2 aileron (in wing), 1 elevator (in boom end at tail)
    ya = np.mean(w.aileron_span_frac) * w.semi_span
    items += [
        Item("aileron servo", 0.013, -0.15, ya, 0.0, "avionics"),
        Item("aileron servo", 0.013, -0.15, -ya, 0.0, "avionics"),
        Item("elevator servo", 0.013, AC.x_tail_le + 0.02, b.y, b.z, "avionics"),
        Item("wiring, connectors", 0.110, -0.12, 0, -0.03, "misc"),
        Item("hardware: inserts, screws, glue", 0.045, -0.12, 0, 0, "misc"),
    ]

    # --- carbon (COTS) ---
    items.append(Item("wing spar tube", tube_mass(w.spar_od, w.spar_id, 2 * w.spar_half_length),
                      -w.spar_x_frac * w.root_chord, 0, 0, "carbon"))
    tip_len = 2 * (w.semi_span - 0.02 - w.tip_spar_start)
    items.append(Item("wing tip spar", tube_mass(w.tip_spar_od, w.tip_spar_id, tip_len),
                      -w.spar_x_frac * w.tip_chord, 0, 0, "carbon"))
    boom_len = b.x_front - b.x_rear
    for s in (+1, -1):
        items.append(Item("boom tube", tube_mass(b.tube_od, b.tube_id, boom_len),
                          (b.x_front + b.x_rear) / 2, s * b.y, b.z, "carbon"))
    items.append(Item("tail spar tube 8x6", tube_mass(0.008, 0.006, t.h_span + 0.02),
                      AC.x_tail_le - 0.25 * t.h_chord, 0, t.h_z, "carbon"))

    # --- printed structure: CAD masses (scripts/assemble.py) when available, else estimates ---
    cad = printed_from_cad() if printed is None else None
    if cad:
        items += cad
        items.append(Item("TPU feet / skid shoes", 0.016, (xf + xr) / 2, 0, -0.2, "printed"))
        items.append(Item("glue, paint, hinge tape (printed-part allowance)", 0.030, -0.12, 0, 0, "printed"))
        return items
    p = printed or printed_estimates()
    xw = -0.40 * w.mac
    items += [
        Item("printed wing (LW-PLA)", p["wing"], xw, 0, 0.01, "printed"),
        Item("printed tail (LW-PLA)", p["tail"], AC.x_tail_le - 0.45 * t.h_chord, 0, b.z - 0.05,
             "printed"),
        Item("printed fuselage pod", p["fuselage"], -0.07, 0, -0.05, "printed"),
        Item("motor mounts + boom clamps (PA-CF)", p["mounts"], (xf + xr) / 2, 0, b.z, "printed"),
        Item("landing feet (TPU)", p["feet"], (xf + xr) / 2, 0, -0.2, "printed"),
    ]
    return items


def printed_from_cad() -> list[Item] | None:
    import json
    from pathlib import Path
    f = Path(__file__).resolve().parent / "results" / "cad_mass.json"
    if not f.exists():
        return None
    data = json.loads(f.read_text())
    return [Item(f"printed: {k}", v["g"] / 1000, v["x"], v["y"], v["z"], "printed") for k, v in data.items()]


def printed_estimates() -> dict:
    """Areal-density estimates (pre-CAD). Wing: single-wall LW-PLA skin 0.45 mm + internal
    ribs/spar sleeve ~ +35%. Validated later against CAD volumes."""
    w, t = AC.wing, AC.tail
    skin_t = 0.45e-3  # m
    wet_wing = 2.04 * w.area
    wing = wet_wing * skin_t * LWPLA_FOAMED * 1000 * 1.35
    wet_tail = 2.04 * (t.h_span * t.h_chord + 2 * t.v_height * (t.v_root_chord + t.v_tip_chord) / 2)
    tail = wet_tail * skin_t * LWPLA_FOAMED * 1000 * 1.35
    return {"wing": wing, "tail": tail, "fuselage": 0.170, "mounts": 0.070, "feet": 0.016,
            "camera_mount": 0.012}


def summarize(items: list[Item]):
    m = np.array([i.mass for i in items])
    pos = np.array([[i.x, i.y, i.z] for i in items])
    total = m.sum()
    cg = (m[:, None] * pos).sum(0) / total
    groups: dict[str, float] = {}
    for i in items:
        groups[i.group] = groups.get(i.group, 0) + i.mass
    return total, cg, groups


def battery_x_for_cg(target_x: float, **kw) -> float:
    """Battery x that puts the CG at target_x (linear in battery x)."""
    items0 = components(battery_x=0.0, **kw)
    tot, cg0, _ = summarize(items0)
    mb = kw.get("battery_mass", BATTERY_MASS)
    return (target_x * tot - cg0[0] * tot) / mb
