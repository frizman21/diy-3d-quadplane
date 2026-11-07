"""Aircraft-level design parameters: the single source of truth. All units mm, g.

Coordinate frame (aircraft body): +X forward, +Y left wing, +Z up. Origin at wing
root leading edge on the centreline unless a part says otherwise.

Everything here is a placeholder (TBD) until the requirements are settled.
"""

# --- Wing (TBD) ---
WING_SPAN = 1600.0
WING_ROOT_CHORD = 240.0
WING_TIP_CHORD = 160.0
WING_AIRFOIL = "TBD"  # .dat file in data/airfoils/

# --- VTOL booms / lift motors (TBD) ---
BOOM_TUBE_OD = 16.0
LIFT_MOTOR_SPACING_X = 600.0  # fore-aft distance between lift motors
LIFT_PROP_DIAMETER = 254.0  # 10 in

# --- Mass budget (TBD) ---
TARGET_AUW_G = 2500.0
