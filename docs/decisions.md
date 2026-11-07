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
