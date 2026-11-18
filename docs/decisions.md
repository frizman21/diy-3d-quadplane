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

## Scale-up to the 10 lb class (2026-11-15, at the owner's request; the details are **to be reviewed**)

The owner asked for the aircraft to be scaled to about 10 lb, batteries and electronics
included. The entries below replace the sizing decisions above. The supporting analysis is
[AerodynamicsReport.md](AerodynamicsReport.md) revision B.

| ID | Decision | Why | Alternatives considered |
|---|---|---|---|
| D-025 | Take-off mass target **≈ 10 lb (4.54 kg)**. Analysed mass **4.65 kg (10.25 lb)**; design mass for structure and propulsion **4.8 kg**. Replaces D-023 | Stated by the owner. The CAD build-up lands 2.5% over the target (§2) | Trimming to exactly 10.0 lb (−115 g; candidates in §2.2) |
| D-026 | **Overall length limit raised from 1.2 m to 1.4 m**; the aircraft is 1.357 m long. Planform: **1.80 m span, 0.34 m root / 0.219 m tip**, same taper and centre section; stall ≤ 10.5 m/s and span ≤ 1.80 m kept. Replaces the length in D-004 and the planform in D-013 | 10 lb needs 15 in props and a 0.34 m chord, and both add to length (§4.1). 1.2 m was the floor width between the Suburban's wheel wells; 1.4 m uses the estimated 1.6 m above them, on a cradle. **Not measured: verify before printing** | Keeping 1.2 m (stall ≈ 14 m/s); 0.36 m chord (fallback if heavy); 1.9 m span (no doorway margin) |
| D-027 | Lift props **15x5**, motors **T-Motor MN4014 KV400**. Replaces D-014 | Front-motor T/W 1.87 with the shortest aircraft; the MN3508 would hover at 76% of full thrust (§5.2) | MN4014 + 16x5.4 (T/W 2.15, 29 W less hover power, but 1.408 m long: first upgrade if the vehicle has room); 17x5.8 (no gain) |
| D-028 | Battery **6S3P Li-ion 21700** (Molicel P45B, or P50B), ≈ 292 Wh, ≈ 1.29 kg, XT90. Replaces D-008 and D-019 | 27 min hover (81% margin) and 34 A per cell at full throttle; brings the aircraft to 10 lb (§5.3) | 6S2P (9.3 lb, 21 min, but 103 A peak vs 90 A continuous: valid light configuration with the pusher limited); 6S4P (T/W fails); 6S LiPo 10 Ah |
| D-029 | **Spar 20x18 CF, 1.30 m** one piece; **booms 28x26 CF, 1.14 m**. Replaces the tube sizes in D-015 and D-018 | Spar margin +0.92 at n = 6 (16x14 would be +0.18). Boom mode 130–147 Hz against a 60–89 Hz hover 1P band; a 20x18 boom would sit inside the band with the heavier motors (§9) | Spar 18x16; booms 25x23 (23% above the band, −34 g), 30x28 |
| D-030 | Tail: **stab 0.60 × 0.18 m (V_H 0.46), fins 0.22 m tall, stab incidence −0.3°**; still a U-tail with no rudder. Replaces the dimensions in D-017 | Tail chord adds to length, so V_H was allowed to fall into the middle of the typical range; taller fins keep V_V and give the 12 in pusher prop ground clearance (§6.3) | 0.20 m stab chord (V_H 0.51, +20 mm length) |
| D-031 | Pusher **SunnySky X3520 520KV + 12x8 folding**, provisional pending a bench test. Replaces D-020 | 2.19 kg static needed with the 30% margin; ≈ 2.4 kg estimated (§5.4) | X2820 + 11x7 (≈ 1.9 kg, under the margin); 13x8 |
| D-032 | Recommended cruise **16 m/s**; operating limit **18 m/s in strong turbulence**; aft CG limit **32.0% root chord** (10% static margin). Replaces D-024 and the CG figure in D-021 | Maximum-range speed is 16.25 m/s; gust n = 4.2 at 22 m/s with a 7.5 m/s gust, 3.6 at 18 m/s (§7, §8) | — |

## Carbon tubes from one supplier (2026-11-15, at the owner's request; the details are **to be reviewed**)

The owner asked that all composite parts come from carbonkevlarsupply.com. Its catalogue
(checked 2026-11-15) has no tube longer than 1000 mm and no round roll-wrapped tube larger
than 25x23. The supporting analysis is [AerodynamicsReport.md](AerodynamicsReport.md)
revision C; the part list is in [cots-selection.md](cots-selection.md) §9.

| ID | Decision | Why | Alternatives considered |
|---|---|---|---|
| D-033 | **All carbon from the supplier's stock sizes, used at catalogue length where possible.** Spar: **20x18 roll-wrapped, 1000 mm uncut** (ends 500 mm from the centreline). Tip spars: **14x12 roll-wrapped, 500 mm uncut**, from 380 mm to 880 mm. Booms: **25x23 roll-wrapped, 1000 mm uncut**. Tail spar: 8x6 pultruded, cut to 620 mm. Elevator joiner: 4 mm pultruded rod. Replaces the tube sizes in D-029 | Stated by the owner (one supplier). The 1.30 m spar, the 1.14 m 28x26 booms and the 3 mm rod are not stocked. Margins: spar root +0.92, tip tube +4.6, boom mode 29% above the 1P band (§9). `make test` now checks every tube against the stock list | 10x8 tip tubes (−19 g, tip deflection 48 mm vs 40 mm); 25x22 pultruded booms (stiffer, +55 g each, but pultruded tube splits under clamps); 20x16 pultruded spar (+82 g) |
| D-034 | **Layout changes that make 1000 mm booms work.** Prop-tip to wing gap **15 mm** (was 25 mm). Each **fin sleeves over the last 85 mm of the boom** and the rest of its root overhangs the boom end, so the fin leading edge is 55 mm ahead of the stab leading edge. Overall length **1.327 m**. Adds to D-030 | The gap sets the front boom overhang, and the shorter overhang lifts the 25x23 boom mode from 23% to 29% above the 1P band. The boom now ends 30 mm behind the stab leading edge, so the fin root has to carry the stab spar (§6.3, R-15). V_V falls from 0.039 to 0.035 | Splicing a boom extension with an internal 20x18 joiner (two more tubes, +50 g); a detachable tail; keeping the 25 mm gap with pultruded booms |
| D-035 | Aft CG limit **31.4% root chord** (10% static margin); balance point 93–107 mm behind the leading edge. Replaces the CG figure in D-032 | Neutral point moved 2 mm with the tail changes (§6.2) | — |

## US and dollar sourcing (2026-11-15, at the owner's request; the details are **to be reviewed**)

The owner asked for every price to link to its source, and for parts to be bought in
dollars or from US sellers instead of the UK listings cited before. The price list is
[cots-selection.md](cots-selection.md) §1, checked 2026-11-15.

| ID | Decision | Why | Alternatives considered |
|---|---|---|---|
| D-036 | **Parts are bought in US dollars, from a US seller where one has stock (BUILD-1b).** Flight controller **Holybro Kakute H743-Wing**, replacing the Matek H7A3-WING of D-016. GPS **Holybro Micro M10**, airspeed **Holybro DroneCAN DLVR-L10D** with the PT40 pitot, ESCs **Lumenier Razor Pro F4 45A**. Ready-made battery: **Upgrade Energy RED V3 6S3P P50B** (within D-028) | Matek marks the H7A3-WING end of life and no US shop has it; Matek GPS and airspeed sensors are also out of stock in the US. The Kakute is the same class of board (H743, 14 outputs, CAN, 90 A current sensor, ArduPilot `KakuteH7-Wing`) at about the same mass, so the mass model and CAD do not change. The Holybro store is in dollars but ships from overseas | Importing an H7A3-WING from the UK or Canada (a discontinued board); Pixhawk 6C Mini ($179, needs a separate power module and servo supply); SpeedyBee F405 Wing (out of stock in the US, 1 MB flash); waiting for US stock of the Kakute at $72.99 |

## 5 lb class around $29 lift motors (2026-11-18, at the owner's request; the details are **to be reviewed**)

The owner asked for the project to be resized around lift motors that cost about $100 for
the set of four, and chose the 5 lb, 6S option from three that were offered (5 lb on 6S,
9 lb on 4S, 7.5 lb on 4S). The supporting analysis is
[AerodynamicsReport.md](AerodynamicsReport.md) revision D; the parts are in
[cots-selection.md](cots-selection.md) rev E.

| ID | Decision | Why | Alternatives considered |
|---|---|---|---|
| D-037 | **Take-off weight about 5 lb (2.3 kg)**, set by the lift motors. Lift: **SunnySky V2806 KV400 with 12x4.5 carbon props** on 6S ($28.99 each, $116 for four). Pusher: **a fifth V2806 KV400 with an APC 12x8E**. Battery: **6S1P Molicel P50B** (108 Wh, about 450 g). Replaces D-025 (10 lb), D-027 (MN4014), D-028 (6S3P pack) and D-031 (X3520 pusher) | Stated by the owner (motor budget). The V2806's bench table gives 1120 g at full throttle with a 12 in prop, so four of them carry at most 2.39 kg at the 1.8 thrust-to-weight rule (PERF-5) with the hover download. Result: 2.34 kg, hover 16.6 min, thrust-to-weight 1.84 (§5). Keeping 6S keeps the ESCs, flight controller and sensors already chosen. One motor type for all five positions means one spare covers everything | **SunnySky X2814 KV900 on 4S** ($30, about 9 lb): hover near 820 W needs a large custom 4S pack, a new cruise motor, and the 11 in props turn near the boom resonance. **SunnySky X2216 KV880 on 4S** ($25, about 7.5 lb): hover near 650 W and the motors at 90% of their power rating at full throttle. **13x5 prop on the V2806**: 4% less maximum thrust and the seller's table shows 101 °C after 30 s at full throttle. **6S2P pack**: 26 min of hover but 2.75 kg, where thrust-to-weight falls to 1.57 |
| D-038 | **Airframe for 5 lb.** Span **1.30 m**, root chord **240 mm**, tip chord 158 mm, area 0.283 m². Booms at **y = ±290 mm**. **Front motors 65 mm ahead of the leading edge (prop tip to wing), rear gap 15 mm**, so the rotor centre sits on the CG and all four motors share the weight equally. Stab 580 × 120 mm, fins 200 mm tall. Pod 530 × 95 × 90 mm with a two-perimeter (0.9 mm) wall. Aft CG limit **39.7% root chord** (10% static margin). In strong turbulence fly at **16 m/s or less** (§8). Overall length **1.065 m**. Replaces D-026, D-030, D-032, D-034 and D-035 | The wing is the smallest that keeps the stall speed at or under 10.5 m/s at the heaviest mass the motors allow, with the root chord just deep enough for the 20 mm spar (§4). With equal prop gaps the front motors carried 57% of the weight and their thrust-to-weight was 1.63; moving them forward gives 50% and 1.84 (§6.4). The 290 mm boom spacing keeps the 12 in pusher prop 20 mm clear of the rear lift-prop disks in plan view; at 240 mm they overlapped (`make test` now checks this) | 1.40 m span (lower cruise power, 30 g heavier, no thrust margin left); 1.20 m × 250 mm (stall limit fails at the heaviest allowed mass); equal prop gaps with a lighter aircraft (needs 2.10 kg, not achievable) |
| D-039 | **Carbon for 5 lb, all from the same supplier (BUILD-1a).** Spar **20x18 roll-wrapped, 500 mm uncut**. Tip spars **10x8 roll-wrapped, 500 mm uncut**, from 130 mm to 630 mm. Booms **25x23 roll-wrapped, cut to 840 mm**. Tail spar 8x6 pultruded cut to 600 mm; 4 mm rod for the elevator. The spar axis height is now chosen for both tubes together. Replaces the sizes in D-033 | Spar root margin +4.3 and tip tube +2.4 at 6 g ultimate and 2.4 kg (§9). **The booms stay 25x23 for vibration, not strength:** the first bending mode is 155–176 Hz, 71% above the top of the 71–91 Hz hover 1P band. A 20x18 boom gives only 21% and fails the 25% rule. The 14x12 tip tube left only 0.3 mm of skin at the tip | 20x18 booms (−40 g, fails the vibration rule); 14x12 tip tubes (do not fit the tip section); 8x6 tip tubes (+1.0 margin, 24 mm tip deflection at limit load) |
