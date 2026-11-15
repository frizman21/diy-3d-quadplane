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
    airfoil: str = "sd7032"  # Report §3 (airfoil trade)
    span: float = 1.80  # §4: doorway limit 1.9 m less 0.1 m handling margin
    center_span: float = 0.60  # constant-chord centre section between the booms
    root_chord: float = 0.340  # §4: smallest chord meeting Vs <= 10.5 m/s at the 10 lb CAD mass (D-026)
    tip_chord: float = 0.219  # §4: outer-panel taper 0.643; tip Re >= 1e5
    root_incidence_deg: float = 1.0  # §6: fuselage ~level at 18 m/s cruise
    tip_twist_deg: float = -2.0  # washout at the tip (§4: benign tip stall)
    dihedral_deg: float = 0.0  # §6: flat wing so one straight spar runs tip-to-tip
    aileron_span_frac: tuple = (0.55, 0.95)  # fraction of semi-span
    aileron_chord_frac: float = 0.25
    spar_od: float = 0.020  # §9: 20x18 roll-wrapped CF tube, centre + inner outer panels (D-029)
    spar_id: float = 0.018
    spar_half_length: float = 0.500  # §9: one uncut 1000 mm catalogue tube (D-033)
    spar_x_frac: float = 0.28  # spar centre at 28% local chord (near max thickness)
    tip_spar_od: float = 0.014  # §9: 14x12 CF tube in the outer panels, 500 mm uncut (D-033)
    tip_spar_id: float = 0.012
    tip_spar_start: float = 0.380  # tip tube runs from here to 20 mm inside the tip (120 mm inside the spar)

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
    tube_od: float = 0.025  # §9: 25x23, the largest roll-wrapped tube the supplier stocks (D-033)
    tube_id: float = 0.023
    length: float = 1.000  # uncut catalogue tube; front end inside the front motor clamp
    x_rear: float = -0.7810  # = front motor + clamp overhang - length (checked in tests)
    front_overhang: float = 0.0135  # boom end ahead of the front motor axis (inside the clamp ring)

    @property
    def x_front(self) -> float:
        return self.x_rear + self.length
    z: float = -0.034  # boom centreline below wing root chord line (clamp clears the lower skin)


@dataclass(frozen=True)
class Lift:
    prop_diameter: float = 15 * 0.0254  # §5 propulsion (D-027)
    prop_pitch: float = 5.0 * 0.0254
    tip_gap: float = 0.015  # prop-tip to wing LE/TE clearance (plan view); shortens the boom overhang (D-034)
    motor_height: float = 0.030  # motor mount top above boom centreline

    @property
    def radius(self) -> float:
        return self.prop_diameter / 2


@dataclass(frozen=True)
class Tail:
    # U-tail: horizontal stabiliser between the booms + two fins hanging below the booms
    # (fins double as the rear landing gear). §6 stability.
    h_span: float = 0.60  # between the boom centrelines (stab halves meet the fin sleeves)
    h_chord: float = 0.180  # §6: V_H ~0.45 inside the 1.4 m length limit (D-030)
    h_airfoil: str = "naca0009"
    elevator_chord_frac: float = 0.35
    v_height: float = 0.220  # each fin, below the boom; tips are the rear landing skids
    v_root_chord: float = 0.140  # §6: V_V ~0.03 with the larger wing
    v_tip_chord: float = 0.105
    v_boom_overlap: float = 0.085  # fin root sleeve on the boom; the rest of the root overhangs the boom end (D-034)
    v_airfoil: str = "naca0009"
    h_incidence_deg: float = -0.3  # §6: near-zero elevator at cruise trim
    h_z: float = -0.013  # stab chord plane: on top of the boom sleeves (boom z + 21 mm)


@dataclass(frozen=True)
class Fuselage:
    x_nose: float = 0.30  # nose ahead of wing LE (battery forward travel for CG, §6)
    x_tail: float = -0.37  # pusher mount face, 30 mm behind the TE; pod = two halves under the bed height
    width: float = 0.115  # 6S3P pack (68 mm wide) + the 42.5 mm pusher motor at the firewall
    height: float = 0.120
    z_top: float = 0.002  # pod top; the wing's lower surface is cut into it as a saddle


@dataclass(frozen=True)
class Pusher:
    prop_diameter: float = 12 * 0.0254  # §5 (D-031)
    prop_pitch: float = 8 * 0.0254
    z_thrust: float = -0.055  # thrust line (pod tail-cone centre)


@dataclass(frozen=True)
class Mission:
    hover_time_s: float = 15 * 60  # PERF-1
    reserve_frac: float = 0.20  # PERF-1
    target_mass: float = 4.536  # kg = 10.0 lb take-off target, battery and electronics included (D-025)
    design_mass: float = 4.8  # kg, structural/propulsion design point (§2: CAD mass 4.65 + growth)
    load_factor_limit: float = 4.0  # §8 (gust + pull-up), ultimate = 1.5 x limit
    safety_factor: float = 1.5


@dataclass(frozen=True)
class Limits:
    span: float = 1.90  # SIZE-1: doorway
    length: float = 1.40  # SIZE-2 rev C: Suburban cargo width above the wheel wells (estimated, VERIFY)
    height: float = 0.90  # SIZE-2


@dataclass(frozen=True)
class Aircraft:
    wing: Wing = field(default_factory=Wing)
    booms: Booms = field(default_factory=Booms)
    lift: Lift = field(default_factory=Lift)
    tail: Tail = field(default_factory=Tail)
    fuselage: Fuselage = field(default_factory=Fuselage)
    pusher: Pusher = field(default_factory=Pusher)
    mission: Mission = field(default_factory=Mission)
    limits: Limits = field(default_factory=Limits)

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
    def x_fin_le(self) -> float:
        """Fin root LE: the fin sleeves over the last `v_boom_overlap` of the boom."""
        return self.booms.x_rear + self.tail.v_boom_overlap

    @property
    def overall_length(self) -> float:
        front = max(self.x_lift_front + self.lift.radius, self.fuselage.x_nose)
        rear = min(self.x_tail_le - self.tail.h_chord, self.x_fin_le - self.tail.v_root_chord,
                   self.booms.x_rear)
        return front - rear


AIRCRAFT = Aircraft()

# Carry-over aliases used by earlier code
WING_SPAN = AIRCRAFT.wing.span
TARGET_AUW_G = AIRCRAFT.mission.target_mass * 1000
