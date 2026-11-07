# Decision log

The decisions made, newest last. Each entry gives the choice, why it was made, and the
alternatives considered. To change a decision, add a new entry that replaces it. Don't
edit old entries.

**Guiding rule (D-000):** v1 is designed for v1 alone. The future 150 kg aircraft is considered
**only when buying something expensive**. If supporting it costs little or nothing more, buy
the version that supports it.

| ID | Date | Decision | Why | Alternatives considered |
|---|---|---|---|---|
| D-001 | 2026-11-07 | CAD is **build123d** (Python), run in **Docker**; the repo layout and conventions are in CLAUDE.md | Handles lofts, splines and airfoils; exports STEP; keeps the host Mac clean | CadQuery, OpenSCAD |
| D-002 | 2026-11-07 | Printer is the **QIDI Max 4**. Filaments: PLA, PETG on hand; LW-PLA, ASA, PA-CF, TPU to buy | Each material matched to its job (BUILD-4) | — |
| D-003 | 2026-11-07 | **Buy off-the-shelf parts** whenever they significantly save weight (carbon spar, booms, landing gear) | Stated by owner | Fully printed |
| D-004 | 2026-11-07 | **One-piece airframe**, transported assembled. Span ≤ 1.9 m (doorway); length ≤ 1.2 m and height ≤ 0.9 m (estimated Suburban cargo space) | Stated transport needs; no field assembly | Detachable wings |
| D-005 | 2026-11-07 | **15 min hover endurance** with a 20% reserve sizes the battery. Cruise endurance is not a target; it is measured after flights | Proof-of-concept tuning time | — |
| D-006 | 2026-11-07 | Flight software: **ArduPilot QuadPlane**. Flight controller: **Matek H743 class** (e.g. H743-WING) | Owner knows ArduPilot; the board has enough outputs | — |
| D-007 | 2026-11-07 | Layout: **twin booms, 4 fixed lift motors (quad X) + 1 pusher**, tail mounted on the booms | Simplest layout to tune; hover and cruise tune separately; a failed transition can still land in hover; booms are carbon tubes from a shop | "+" with wingtip motors, H frame, tilt-rotor, tilt-wing, tailsitter (see the discussion summary below) |
| D-008 | 2026-11-07 | Battery (preliminary): **6S2P 21700 Li-ion, ≈ 190 Wh** | Meets the 15 min hover with margin for weight growth | 6S1P Li-ion (no margin), 6S LiPo |
| D-009 | 2026-11-07 | Camera: **Insta360 GO 3S** (≈ 39 g) in a **TPU** cradle that releases it in a crash | Light, sealed, better odds of surviving a crash | GoPro HERO13 (≈ 157 g), DJI Osmo Action 5 Pro (≈ 146 g) |
| D-010 | 2026-11-07 | Radio: **RadioMaster TX16S MK3** with built-in **dual-band ExpressLRS** (2.4 GHz + 900 MHz). Video link to be added later when needed | ≈ $200; ≥ 16 channels, MAVLink telemetry, long range on 900 MHz, a backup link via two receivers on different bands; reusable on the 150 kg aircraft (D-000) | Spektrum (limited ArduPilot telemetry and range), SIYI MK15/MK32, Herelink (expensive, reported software problems) |

## Layout options considered for D-007 (ArduPilot-native)

- Fixed lift motors plus a pusher, mounted as twin booms (chosen), "+" with wingtip motors, or an H frame. Frame classes quad, hexa, octa, octaquad, Y6 and tri.
- Tilt-rotor: tri, or quad with the front two or all four tilting; continuous or binary tilt.
- Tilt-wing.
- Tailsitter: duo flying wing, copter-motor, or vectored thrust.

A tilt-rotor is the natural next step after v1, but it is **not** a v1 consideration (D-000).

## Design decisions (2026-11-07, made autonomously while the owner was away; **to be reviewed**)

The supporting analysis is in [AerodynamicsReport.md](AerodynamicsReport.md) (§ references below)
and [cots-selection.md](cots-selection.md).

| ID | Decision | Why | Alternatives considered |
|---|---|---|---|
| D-011 | Analysis toolchain: **XFOIL 6.99 + AVL 3.40** (compiled from MIT sources in Docker), **AeroSandbox AeroBuildup + NeuralFoil**; one parameter file drives CAD and analysis (`make analysis`) | Open source, standard, reproducible; each tool used where it's strongest (Report §1.2) | OpenVSP/VSPAERO (heavier), SU2 CFD (overkill for v1) |
| D-012 | Airfoil **SD7032** (wing), **NACA 0009** (tails) | Lowest drag over C_l 0.3–0.65 with both smooth and rough (printed) transition, gentlest stall, t/c 10% fits the spar (§3) | Clark Y (2nd), NACA 4412, SD7062, SD7037 (too thin), MH114 (C_m0 −0.19) |
| D-013 | Planform: **1.80 m span, 0.26 m root / 0.167 m tip, 0.60 m constant-chord centre**; constraints span ≤ 1.80 m, stall ≤ 10.5 m/s, tip chord ≥ 150 mm | The 1.2 m length limit binds the chord; smallest wing with stall ≤ 10.5 m/s at the CAD mass; 1.9 m saves < 2 W but leaves no doorway margin (§4) | 1.9 m span; 0.24 m chord (stall 10.6 m/s after mass growth) |
| D-014 | Lift props **14x4.8**, motors **T-Motor MN3508 KV380** | The only prop that meets both T/W ≥ 1.8 on the front motor and length ≤ 1.2 m (§5.2) | 13 in (fails T/W), 15 in (fails length), MN4014 (+270 g) |
| D-015 | **Flat wing (0° dihedral), one-piece 16x14 spar 1.30 m** + 8x6 tip tubes | Strongest, simplest joint; spiral time to double 8.4 s (meets Level 2) is acceptable with autopilot (§6.6) | 3° dihedral (time to double 14 s) would need a spar joiner at the highest-moment point |
| D-016 | Flight controller **Matek H7A3-WING** (supersedes the H743-WING in D-006, now discontinued) | Matek's replacement; 11 DShot outputs, built-in current monitor | H743-WING V3 (EOL) |
| D-017 | **Tail: U-tail**: stab 0.60 × 0.15 m between the booms (V_H 0.57), two 0.19 m fins hanging below the booms that double as rear landing skids; **no rudder** | High tail volume for CG tolerance and transition damping; fins as gear save parts (§6.3) | Inverted V (2 mixed servos), H-tail with fins above (separate gear) |
| D-018 | Booms **20x18 CF, 1.000 m** | Boom bending mode 106–121 Hz, clear of the 63–87 Hz hover 1P band; 16x14 would resonate (§9.2) | 16x14, 18x16 (marginal), 20x17 (+42 g each) |
| D-019 | Battery confirmed **6S2P Li-ion 21700** (P45B, or P50B), XT90 | 24.9 min hover at 3.34 kg (66% margin); 6S1P is too marginal, LiPo fails PERF-1 (§5.3) | 6S1P P50B, 6S LiPo 5000 |
| D-020 | Pusher **SunnySky X2820 570KV + 10x7 folding**, provisional; **11x7** if bench thrust < 1.5 kg | 1.2 kg static needed for the transition, 1.57 kg with margin (§5.4) | AT2814 (not 6S), AT3520 (heavier) |
| D-021 | Static margin target **10% MAC**; battery slides to set the CG (aft limit 37.9% root chord) | Low end of 10–15% practice, needed to keep the battery inside the nose (§6.2) | 12% (battery wouldn't fit) |
| D-022 | Materials: **LW-PLA** for wing, tail, fins and pod; **PA-CF** for motor mounts and boom saddles; **TPU** for the camera cradle and skid shoes | Mass (the CAD showed 1.5 kg printed in the first pass, 1.07 kg after lightening; §2.2) | PETG pod and fins (+110 g, tail-heavy) |
| D-023 | Design mass **3.4 kg** for structures and propulsion (was 3.0) | CAD-based take-off mass 3.34 kg (§2) | — |
| D-024 | Operating limit: **15 m/s in turbulence**; recommended cruise 15 m/s | Gust n = 4.9 at 22 m/s with a 7.5 m/s gust exceeds the limit load (§8) | Heavier spar (adds mass to a hover-limited design) |
