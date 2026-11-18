"""Reference geometry for COTS (bought) parts, aircraft frame, mm. Assembly/visualisation only;
dimensions are envelope-level (VERIFY against delivered hardware)."""

import math

from build123d import Box, Cylinder, Part, Pos, Rot

from quadplane import geometry as G
from quadplane import hardware as HW
from quadplane.params import AIRCRAFT as AC, mm

W, B, T = AC.wing, AC.booms, AC.tail


def make() -> dict[str, Part]:
    out: dict[str, Part] = {}
    # main spar (one piece) + tip tubes
    out["spar_main"] = G.spar_bore(-W.spar_half_length, W.spar_half_length, W.spar_od, clearance=0) \
        - G.spar_bore(-W.spar_half_length - 0.01, W.spar_half_length + 0.01, W.spar_id, clearance=0)
    for s, n in ((1, "L"), (-1, "R")):
        y0, y1 = sorted((s * W.tip_spar_start, s * (W.semi_span - 0.02)))
        out[f"tip_tube_{n}"] = G.spar_bore(y0, y1, W.tip_spar_od, clearance=0)
        out[f"boom_{n}"] = G.tube_along_x(B.x_front, B.x_rear, s * B.y, B.z, B.tube_od, B.tube_id)
        for x, tag in ((AC.x_lift_front, "front"), (AC.x_lift_rear, "rear")):
            z0 = mm(B.z + AC.lift.motor_height)
            out[f"motor_{tag}_{n}"] = Pos(mm(x), mm(s * B.y), z0 + HW.LIFT_MOTOR_BODY_H / 2) * \
                Cylinder(HW.LIFT_MOTOR_BODY_D / 2, HW.LIFT_MOTOR_BODY_H)
            out[f"prop_{tag}_{n}"] = Pos(mm(x), mm(s * B.y), z0 + HW.LIFT_MOTOR_BODY_H + 8) * \
                Cylinder(mm(AC.lift.radius), 1.0)
    out["tail_spar_8x6"] = Pos(mm(AC.x_tail_le - 0.25 * T.h_chord), 0, mm(T.h_z)) * \
        (Rot(90, 0, 0) * Cylinder(HW.TAIL_SPAR_OD / 2, mm(T.h_span) + 20))
    # pusher motor + prop disk
    xf = mm(AC.fuselage.x_tail)
    zt = mm(AC.pusher.z_thrust)
    out["pusher_motor"] = Pos(xf - HW.PUSHER_BODY_L / 2, 0, zt) * (Rot(0, 90, 0) * Cylinder(HW.PUSHER_BODY_D / 2, HW.PUSHER_BODY_L))
    out["pusher_prop"] = Pos(xf - HW.PUSHER_BODY_L - HW.PUSHER_PROP_OFFSET, 0, zt) * (Rot(0, 90, 0) * Cylinder(mm(AC.pusher.prop_diameter) / 2, 1.0))
    # battery (at the analysis CG position if available)
    try:
        from analysis.common import load_json
        xb = load_json("stability")["battery_x"]
    except Exception:  # noqa: BLE001
        xb = 0.10
    L, Wd, H = HW.BATTERY
    zb = mm(AC.fuselage.z_top) - 12 - H / 2
    out["battery"] = Pos(mm(xb), 0, zb) * Box(L, Wd, H)
    # camera
    from quadplane.parts.fuselage import camera_station
    l_, w_, h_ = HW.GO3S_SIZE
    xc, z_cradle = camera_station()
    out["camera"] = Pos(xc + 3, 0, z_cradle - h_ / 2 - 2) * Box(l_, w_, h_)
    _ = math
    return out
