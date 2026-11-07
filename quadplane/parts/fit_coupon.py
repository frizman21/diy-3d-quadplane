"""Calibration coupon: print this first, then tune clearances in printer.py.

Row 1: holes for a 10 mm carbon tube at clearance +0.0 ... +0.5 mm (find the slip-fit hole).
Row 2: M3 heat-set insert holes at 3.9 ... 4.4 mm.
Small notches mark the smallest hole in each row.
"""

from build123d import Box, Cylinder, Location, Part, Pos

from quadplane import hardware, printer

MATERIAL = printer.DEFAULT

TUBE_OD = 10.0
TUBE_STEPS = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5]
INSERT_HOLES = [3.9, 4.0, 4.1, 4.2, 4.3, 4.4]

PITCH = 16.0
THICK = 6.0


def build() -> Part:
    n = len(TUBE_STEPS)
    length = PITCH * n + 4
    width = 34.0
    plate = Box(length, width, THICK)

    x0 = -PITCH * (n - 1) / 2
    for i, extra in enumerate(TUBE_STEPS):
        plate -= Pos(x0 + i * PITCH, 7, 0) * Cylinder((TUBE_OD + extra) / 2, THICK)
    for i, d in enumerate(INSERT_HOLES):
        plate -= Pos(x0 + i * PITCH, -9, THICK / 2 - hardware.M3_INSERT_DEPTH / 2) * Cylinder(
            d / 2, hardware.M3_INSERT_DEPTH
        )

    # orientation notch at the smallest end
    plate -= Location((-length / 2, 0, 0)) * Box(3, 3, THICK)

    # sit on the bed (z = 0)
    return Pos(0, 0, THICK / 2) * plate
