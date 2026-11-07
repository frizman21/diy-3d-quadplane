"""Printer and material profile. All units mm.

Values tagged VERIFY should be confirmed against the actual machine / test prints
(print parts/fit_coupon first and adjust the clearances here).
"""

from dataclasses import dataclass

# QIDI Max 4 build volume. VERIFY against the spec sheet / slicer profile.
BED_X = 390.0
BED_Y = 390.0
BED_Z = 340.0
BED_MARGIN = 5.0  # keep parts this far inside the bed edges

NOZZLE = 0.4
LAYER = 0.2


@dataclass(frozen=True)
class Material:
    name: str
    density_g_cm3: float
    clearance_sliding: float  # hole-vs-shaft extra diameter for a slip fit
    clearance_press: float  # extra diameter for a press fit
    min_wall: float


PLA = Material("PLA Basic", 1.24, clearance_sliding=0.30, clearance_press=0.10, min_wall=0.8)
PETG = Material("PETG Basic", 1.27, clearance_sliding=0.35, clearance_press=0.15, min_wall=0.8)

DEFAULT = PETG
