"""Aircraft-level design parameters: the single source of truth for analysis and CAD.

Units: m, kg, s, N (SI) in this file. CAD converts to mm via `mm()`.
Body frame: +X forward, +Y left, +Z up. Origin: wing root leading edge, centreline.
The wing chord line at the root is at z = 0.

Values are set by the analysis in analysis/ and documented in docs/AerodynamicsReport.md.
Each value notes the section of the report that justifies it.
"""

from dataclasses import dataclass, field


def mm(x_m: float) -> float:
    return x_m * 1000.0


@dataclass(frozen=True)
class Wing:
    airfoil: str = "sd7062"  # Report §3 (airfoil trade)
    span: float = 1.80  # §4: doorway limit 1.9 m, transport margin
    center_span: float = 0.60  # constant-chord centre section between the booms
    root_chord: float = 0.280  # §4
    tip_chord: float = 0.180  # §4: taper 0.64 on the outer panels
    root_incidence_deg: float = 1.0  # §6: fuselage ~level at 18 m/s cruise
    tip_twist_deg: float = -2.0  # washout at the tip (§4: benign tip stall)
    dihedral_deg: float = 3.0  # outer panels only (§6: spiral/Dutch-roll balance)
    aileron_span_frac: tuple = (0.55, 0.95)  # fraction of semi-span
    aileron_chord_frac: float = 0.25

    @property
    def semi_span(self) -> float:
        return self.span / 2

    @property
    def outer_span(self) -> float:
        return (self.span - self.center_span) / 2

    @property
    def area(self) -> float:
        return self.center_span * self.root_chord + 2 * self.outer_span * (
            self.root_chord + self.tip_chord) / 2

    @property
    def aspect_ratio(self) -> float:
        return self.span ** 2 / self.area

    @property
    def mac(self) -> float:
        """Mean aerodynamic chord (exact for the piecewise planform)."""
        import numpy as np
        y = np.linspace(0, self.semi_span, 2001)
        c = np.where(y <= self.center_span / 2, self.root_chord,
                     self.root_chord + (self.tip_chord - self.root_chord)
                     * (y - self.center_span / 2) / self.outer_span)
        return float(np.trapezoid(c ** 2, y) / np.trapezoid(c, y))


@dataclass(frozen=True)
class Booms:
    y: float = 0.30  # lateral position of each boom (§5: prop clearance)
    tube_od: float = 0.016  # §8 structures
    tube_id: float = 0.014
    x_front: float = 0.26  # boom front end (ahead of wing LE), m
    x_rear: float = -0.76  # boom rear end (tail), m
    z: float = -0.030  # boom centreline below wing root chord line


@dataclass(frozen=True)
class Lift:
    prop_diameter: float = 14 * 0.0254  # §5 propulsion
    prop_pitch: float = 4.8 * 0.0254
    tip_gap: float = 0.025  # prop-tip to wing LE/TE clearance
    motor_height: float = 0.030  # motor mount top above boom centreline

    @property
    def radius(self) -> float:
        return self.prop_diameter / 2


@dataclass(frozen=True)
class Tail:
    # U-tail: horizontal stabiliser between the booms + two fins hanging below the booms
    # (fins double as the rear landing gear). §6 stability.
    h_span: float = 0.66  # tip-to-tip (extends 30 mm outboard of each boom)
    h_chord: float = 0.140
    h_airfoil: str = "naca0009"
    elevator_chord_frac: float = 0.35
    v_height: float = 0.170  # each fin, below the boom
    v_root_chord: float = 0.160
    v_tip_chord: float = 0.110
    v_airfoil: str = "naca0009"
    h_incidence_deg: float = 1.0  # §6: near-zero elevator at cruise trim


@dataclass(frozen=True)
class Fuselage:
    x_nose: float = 0.22  # nose ahead of wing LE
    x_tail: float = -0.40  # fuselage end (pusher motor mount face)
    width: float = 0.105
    height: float = 0.115
    z_top: float = 0.012  # fuselage top relative to wing root chord line (wing sits on pod)


@dataclass(frozen=True)
class Pusher:
    prop_diameter: float = 10 * 0.0254  # §5
    prop_pitch: float = 7 * 0.0254
    z_thrust: float = -0.050  # thrust line


@dataclass(frozen=True)
class Mission:
    hover_time_s: float = 15 * 60  # PERF-1
    reserve_frac: float = 0.20  # PERF-1
    design_mass: float = 3.0  # kg, structural and propulsion design point (§2)
    load_factor_limit: float = 4.0  # §8 (gust + pull-up), ultimate = 1.5 x limit
    safety_factor: float = 1.5


@dataclass(frozen=True)
class Aircraft:
    wing: Wing = field(default_factory=Wing)
    booms: Booms = field(default_factory=Booms)
    lift: Lift = field(default_factory=Lift)
    tail: Tail = field(default_factory=Tail)
    fuselage: Fuselage = field(default_factory=Fuselage)
    pusher: Pusher = field(default_factory=Pusher)
    mission: Mission = field(default_factory=Mission)

    # --- derived layout ---
    @property
    def x_lift_front(self) -> float:
        return self.lift.radius + self.lift.tip_gap  # ahead of root LE

    @property
    def x_lift_rear(self) -> float:
        return -(self.wing.root_chord + self.lift.radius + self.lift.tip_gap)

    @property
    def x_tail_le(self) -> float:
        return self.x_lift_rear - self.lift.radius - self.lift.tip_gap

    @property
    def overall_length(self) -> float:
        front = max(self.x_lift_front + self.lift.radius, self.fuselage.x_nose)
        rear = min(self.x_tail_le - self.tail.v_root_chord, self.booms.x_rear)
        return front - rear


AIRCRAFT = Aircraft()

# Carry-over aliases used by earlier code
WING_SPAN = AIRCRAFT.wing.span
TARGET_AUW_G = 2800.0
