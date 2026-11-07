# COTS subsystem selection: QP-1 (v1 proof of concept)

Status: **Draft for review**, 2026-11-07
Related: [requirements](requirements.md) · [decision log](decisions.md) · [Aerodynamics report](AerodynamicsReport.md)

This document records which bought (COTS) parts were selected for each subsystem, the
numbers that drove each choice, and the alternatives that were rejected. Prices and stock
are retailer snapshots from November 2026. Items marked **VERIFY** must be checked against
the delivered part before the dependent CAD is printed. Mount bolt patterns and envelopes
live in `quadplane/hardware.py`.

**How to read the trade-offs.** Rule D-000 applies: v1 is designed for v1. The future
150 kg aircraft was considered only for the radio, the one expensive purchase that will
carry over.

---

## 1. Summary bill of materials

| # | Subsystem | Selected part | Qty | Mass each | Approx. price | Driving requirement |
|---|---|---|---|---|---|---|
| 1 | Lift motors | T-Motor **MN3508 KV380** | 4 | 103 g | $70 | PERF-1, PERF-5 |
| 2 | Lift props | T-Motor **P14x4.8** carbon (CW/CCW pairs) | 2 pr (+2 spare pr) | 19–20 g | $49–70/pr | PERF-1, SIZE-2 |
| 3 | Pusher motor | SunnySky **X2820 V3 570KV** (provisional) | 1 | 143 g | $45 | PERF-3 (transition) |
| 4 | Pusher prop | Folding **10x7** (Aeronaut CAM Carbon or equivalent); **11x7** fallback | 1 (+1) | ~20 g | $15–30 | PERF-3 |
| 5 | ESCs | **AM32** single 40–45 A, 6S, DShot (Skystars Talon 40A or Lumenier Razor Pro 45A) | 5 | 3–7 g | $16–31 | — |
| 6 | Battery | **6S2P Molicel P45B 21700 Li-ion** (≈194 Wh); 6S2P P50B acceptable | 1 (+1) | 860 g | $65–120 | PERF-1 |
| 7 | Flight controller | **Matek H7A3-WING** (replaces the discontinued H743-WING V3) | 1 | 30 g | ~$90 | SYS-2 |
| 8 | GPS + compass | Matek M10Q-5883 **or its successor** (M10 GNSS + compass) | 1 | 8–15 g | ~$50 | SYS-3 |
| 9 | Airspeed | Matek **ASPD-DLVR** (I²C/DroneCAN) + pitot | 1 | 4 g + tube | $100–130 | QuadPlane transition |
| 10 | RC receiver | RadioMaster **DBR4** (dual-band ExpressLRS Gemini) | 1 | 5.3 g | $30–39 | RC-1…RC-9 |
| 11 | Handset | RadioMaster **TX16S MK3**, dual-band ELRS (D-010) | 1 | — | ~$200 | RC-1…RC-8 |
| 12 | Remote ID | **BlueMark db120** (FAA-declared broadcast module, own GPS and battery) | 1 | 25 g | $119–149 | REG-2 |
| 13 | Servos | **EMAX ES08MD II** (metal gear, digital) | 3 (+1) | 13 g | $12 | — |
| 14 | Wing spar | **16x14 mm roll-wrapped CF tube**, cut to 1.30 m | 1 | 95 g | £15–27 | §9 report |
| 15 | Tip spars | **8x6 mm CF tube**, 2 × 0.28 m | 2 | 10 g | £8 | §9 report |
| 16 | Booms | **20x18 mm roll-wrapped CF tube**, 1.000 m (20x17 acceptable) | 2 | 93 g | £18 | §9 report (vibration) |
| 17 | Tail spar | **8x6 mm CF tube**, 0.62 m | 1 | 21 g | £8 | §8 report |
| 18 | Camera | **Insta360 GO 3S** (D-009) | 1 | 39 g | ~$400 | PAY-1 |
| 19 | Hardware | M3 heat-set inserts, M3/M4 screws, 3 mm CF rod (elevator joiner), pushrods, XT60/XT90 | — | ~50 g | — | BUILD-5 |

Analysed take-off mass with these parts: **3.34 kg** (Report §2).

---

## 2. Lift propulsion: motor and prop

**Requirement.** Hover at about 3.35 kg with the front pair carrying 54.7% of the weight
(Report §6.4). That means about 950 g per front motor and 790 g per rear motor. Thrust-to-weight
must be at least 1.8 on the most loaded motor (PERF-5), and the 1.2 m overall length limits
the prop diameter (SIZE-2).

**Candidates.** All data is manufacturer bench data at 6S (22.2 V):

| Motor | Mass | Prop | Point near hover | g/W | Max thrust | Price |
|---|---|---|---|---|---|---|
| T-Motor MN3508 KV380 | 103 g | 14x4.8 CF | 710 g at 64.4 W | **11.0** | 1730 g | $70 |
| T-Motor MN3508 KV380 | 103 g | 15x5 CF | 820 g at 79.9 W | 10.3 | 1880 g | $70 |
| T-Motor MN3508 KV380 | 103 g | 13x4.4 CF | 810 g at 82 W | 9.9 | 1380 g | $70 |
| T-Motor MN4014 KV400 | 171 g | 15x5 CF | lowest point 1250 g at 126 W | 9.9 | 2620 g | $97 |
| MAD 4006 IPE 380KV | 79 g | 13–16 in | no thrust table published | — | 2.2 kg (claimed) | $68 |

**Decision: MN3508 KV380 with 14x4.8 carbon props.**

- It has the best published efficiency near the hover point.
- The front-motor thrust-to-weight is **1.82**, meeting PERF-5.
- With 14 in props the aircraft is **1.196 m long**, within SIZE-2. With 15 in it would be 1.217 m, which fails SIZE-2.
- The MN4014 adds 270 g across four motors for thrust v1 doesn't need.
- The MAD 4006 is lighter but has no published data, so it remains an option for a later version.

**Risks.** The MN3508 is rated 14 A / 310 W for 180 s. At hover each front motor draws about
100 W (4.5 A), roughly 30% of that rating, so continuous hover is not a thermal risk.

---

## 3. Pusher motor and prop

**Requirement.** Static thrust of at least **1.2 kg** for the transition (14 m/s in 6 s while
overcoming drag), plus a **30% margin**, giving 1.56 kg (Report §5.4). At 18 m/s the cruise
thrust is about 2.5 N. The thrust line is set by pod geometry at z = −55 mm, with 220 mm of
ground clearance below the booms.

**Sizing.** For a 10x7 prop (static C_T ≈ 0.105), 1.56 kg needs about 10,200 rpm. That works
out to a motor of about **600 KV** on loaded 6S, drawing about 500 W at full static thrust.

**Candidates.** No manufacturer publishes a 6S/10 in thrust table for a motor of this class.
I checked the SunnySky X2820 V3 570KV (143 g, 960 W rating), the T-Motor AT2814 KV900
(3–4S only, which rules it out) and the T-Motor AT3520 KV550 (heavier).

**Decision (provisional): SunnySky X2820 V3 570KV with a 10x7 folding prop.**

- At 570 KV the estimated static thrust is about **1.39 kg**. That meets the 1.2 kg
  requirement but not the 30% margin.
- **Bench-test action:** measure static thrust with 10x7 and 11x7 folding props. Use the
  11x7 if the 10x7 gives less than 1.5 kg. The 11x7 has 25 mm of ground clearance, and its
  extra load stays well inside the motor's 960 W rating.
- The prop folds back when stopped, to protect it on landing. The motor mass is **VERIFY**.

---

## 4. ESCs

BLHeli_32 has reached end of life, so **AM32** firmware is the current choice. It supports
DShot and bidirectional DShot, which gives the flight controller RPM telemetry so
ArduPilot's harmonic notch filter can track motor speed.

**Decision: five single AM32 ESCs (40–45 A, 6S)**, one at each lift motor on the boom
(close to the motor, short leads) and one in the pod for the pusher.

| ESC | Rating | Mass | Notes |
|---|---|---|---|
| Skystars Talon 40A AM32 | 3–6S, 40 A, telemetry | 6.8 g | preferred: cheap, has telemetry |
| Lumenier Razor Pro F4 45A AM32 | 2–6S | 3 g | alternative |
| Holybro Tekko32 F4 50A 4-in-1 | 4–6S | 13.8 g | rejected: a 4-in-1 needs about 0.5 m motor leads on a twin-boom layout |

Current check: the most a lift motor draws is about 14 A, and the pusher about 23 A
(500 W at 22 V), so a 40 A rating gives at least 1.7× margin.

---

## 5. Battery

**Requirement.** At least 15 min hover to a 20% reserve (PERF-1), at the hover power of
**376 W** (Report §5.2).

| Option | Energy | Pack mass | Take-off mass | Hover time | Meets PERF-1 | Cell current at max thrust |
|---|---|---|---|---|---|---|
| 6S1P Molicel P50B | 108 Wh | 455 g | 2.94 kg | 16.6 min | barely (11% margin) | 62 A per cell (limit 60) ✗ |
| 6S LiPo 5000 mAh (CNHL G+) | 111 Wh | 811 g | 3.29 kg | 14.5 min | **no** | — |
| **6S2P Molicel P45B** | **194 Wh** | **860 g** | **3.34 kg** | **24.9 min** | **yes, 66% margin** | **31 A per cell (limit 45)** |
| 6S2P Molicel P50B | 216 Wh | 880 g | 3.36 kg | 27.3 min | yes | 31 A per cell (limit 60) |

**Decision: 6S2P 21700 Li-ion (Molicel P45B, or P50B if available).**

- The 6S1P pack meets the hover time only by 11%. That margin would disappear in cold
  weather or as the cells age, and the pack can't supply full-thrust current.
- The LiPo fails PERF-1.
- 2P Li-ion gives a 66% hover margin and a long cruise (Report §7).
- The prebuilt Flywoo Explorer 6S2P P45B (XT60, 860.7 g) was out of stock at the time of
  writing. A pack builder or a DIY spot-welded pack (no BMS, balance lead) is equivalent.
- **Connector:** use **XT90** rather than XT60 (peak current is about 62 A).
- **Envelope:** 140 × 46 × 75 mm (**VERIFY**). The nose bay takes it with the pack's front
  50 mm or more behind the nose tip. CG is set by sliding the pack, which ends about 126 mm
  ahead of the wing leading edge.

---

## 6. Flight controller, GPS, airspeed, power

- **Flight controller: Matek H7A3-WING.** The H743-WING V3 named in D-006 is discontinued
  (2026), and the H7A3-WING is Matek's replacement. It has:
  - 11 PWM outputs, all DShot-capable. v1 needs 5 motors + 3 servos = 8, leaving 3 spare.
  - 6 UARTs.
  - A built-in current monitor (100 A continuous), so no separate power module.
  - An 8 A servo power supply and 9 V/12 V supplies.
  - ArduPilot target `MatekH7A3-Wing` (4.7+).

  **This updates D-006** (logged as D-016).
- **GPS: Matek M10Q-5883 or successor.** One reseller lists the M10Q-5883 as end of life.
  Any M10 GNSS + QMC5883/IST8310 compass module of about 10 g works. It is mounted on a
  60 mm mast on the nose top, away from power wiring and the motors.
- **Airspeed: Matek ASPD-DLVR.** ArduPilot QuadPlane transitions depend on airspeed, and a
  synthetic airspeed estimate isn't acceptable during first flights. The pitot sits on the
  nose, clear of the front prop wash.

## 7. Radio link (D-010) and Remote ID

- **Handset: RadioMaster TX16S MK3** with internal dual-band ExpressLRS (2.4 GHz + 900 MHz).
  **VERIFY:** order the version with the Gemini/LR1121 dual-band module.
- **Receiver: RadioMaster DBR4** (two LR1121 radios in Gemini mode, 5.3 g, about $30).
  It connects over CRSF on one UART, carries MAVLink telemetry, and provides link-quality
  information for the failsafe.
- **Remote ID: BlueMark db120.** It is a self-contained broadcast module with its own GPS
  and battery, which suits a hobbyist build. The Holybro/ArduRemoteID option is rejected:
  it would make the builder file their own FAA Declaration of Compliance.
  **VERIFY** the db120 is on the FAA's list of declared modules before buying.

## 8. Servos

Three **EMAX ES08MD II** servos (13 g, 2.0 kg·cm at 6 V, metal gear, 0.10 s): two ailerons
and one elevator.

Load check: the aileron is 0.36 m long with a mean chord of about 47 mm (25% of a ~190 mm
local chord), so its area is about 0.017 m². At 22 m/s (q ≈ 296 Pa) and 20° deflection, with
a hinge-moment coefficient C_h ≈ 0.2, the hinge moment is about 0.05 N·m. The servo gives
0.20 N·m at 6 V, about 4× margin with a direct linkage.

The KST X08 (8 g, $45) is the weight-optimised upgrade if needed later.

## 9. Carbon tubes

Sizes come from the structural analysis (Report §9):

| Member | Tube | Length | Why this size |
|---|---|---|---|
| Wing spar | 16x14 roll-wrapped | 1.30 m, one piece | +67% ultimate-strength margin at the root (n = 6, 3.4 kg); the deepest tube that keeps ≥ 2.1 mm wall inside the wing |
| Tip spars | 8x6 | 2 × 0.28 m, slid 50 mm into the main spar | +530% margin; continues the spar beyond where the 16 mm tube fits |
| Booms | **20x18** roll-wrapped | 2 × 1.000 m (catalogue length) | **Vibration:** the boom's first bending mode is 106–121 Hz, clear of the 63–87 Hz hover 1P band. A 16x14 boom would sit at 75–85 Hz, inside the band (resonance). |
| Tail spar | 8x6 | 0.62 m | joins the two stab halves and both fins (boom torsion tie) |

**Sources.**
- Easy Composites roll-wrapped metric tubes: 18x15 and 20x17, 1 m and 2 m.
- RMRC: 16x14.
- R&G: 12/10 pultruded.

If 20x18 is unavailable, **20x17** is acceptable. It adds 42 g per boom and raises the
first mode to 125–141 Hz.

## 10. Camera (D-009)

**Insta360 GO 3S**, 39 g. It is 4K and IP68 (waterproof to 10 m), and is held in a TPU
cradle under the nose with the button and SD card reachable through a window.

Recording time on its own battery is about 38 min. That is longer than a 25 min hover
session but **shorter than a long cruise flight**, so long-endurance flights need either the
Action Pod or a 5 V tap.

**VERIFY** the camera's outer dimensions (54 × 25.5 × 24.5 mm assumed) before printing the cradle.

---

## 11. Open items

| ID | Item | Owner |
|---|---|---|
| C-1 | Bench-test pusher static thrust with 10x7 vs 11x7 folding props | build |
| C-2 | Measure the delivered motors' bolt patterns and the battery envelope; update `hardware.py` | build |
| C-3 | Confirm the BlueMark db120 is on the FAA declared-module list | owner |
| C-4 | Confirm the TX16S MK3 variant has the dual-band (LR1121) internal module | owner |
| C-5 | Tap-test boom natural frequency after assembly (phone accelerometer or ArduPilot FFT log) | build |

## Sources

- T-Motor MN3508: https://store.tmotor.com/goods-354-MN3508.html
- T-Motor MN4014: https://store.tmotor.com/product/mn4014-kv400-motor-navigator-type.html
- MAD 4006: https://mad-motor.com/products/mad-components-4006-ipe
- T-Motor P15x5: https://irlock.com/products/t-motor-p15x5-prop-2pcs-pair
- T-Motor P14x4.8: https://www.robotshop.com/products/t-motor-14-48-carbon-fiber-propeller-pair
- SunnySky X2820 V3: https://www.readymaderc.com/products/details/85632-sunnysky-x-series-v3-x2820-brushless-motor-570kv
- T-Motor AT2814: https://store.tmotor.com/product/at2814-long-shaft-fixed-wing-motor.html
- Aeronaut CAM folding blades: https://modelflight.com.au/aeronaut-cam-c-folding-blades-10x6in-pair
- Skystars Talon 40A: https://www.rotorama.com/product/skystars-talon-40a-esc-blheli-32
- Lumenier Razor Pro 45A: https://www.lumenier.com/products/lumenier-razor-pro-f4-45a-2-6s-am32-esc
- Molicel P50B datasheet: https://www.fsaeonline.com/content/Molicel-TDS--INR-21700-P50B-80122.pdf
- Molicel P45B datasheet: https://www.imrbatteries.com/content/molicel_p45b.pdf
- Flywoo 6S2P P45B: https://www.unmannedtechshop.co.uk/product/flywoo-explorer-molicell-p45b-21700-6s2p-9000mah-lionpack-battery
- Matek H7A3-WING: https://www.mateksys.com/?p=12747
- Matek M10Q-5883: https://www.flyingtech.co.uk/product/matek-gnss-gps-compass-module-m10-5883
- Matek ASPD-DLVR: https://www.racedayquads.com/products/matek-digital-airspeed-sensor-aspd-dlvr
- RadioMaster DBR4: https://radiomasterrc.com/collections/popular-products/products/dbr4-dual-band-xross-gemini-expresslrs-receiver
- BlueMark db120: https://www.dslrpros.com/products/dronebeacon-db120-remoteid-broadcast-module-with-battery
- Holybro Remote ID: https://docs.holybro.com/radio/remote-id/overview-and-spec
- EMAX ES08MD II: https://alofthobbies.com/products/emax-es08mdii-servo-2kg-27-77-oz-in-10-sec-13-grams
- Easy Composites tubes: https://www.easycomposites.co.uk/roll-wrapped-carbon-fibre-tube-metric
- RMRC tubes: https://www.readymaderc.com/collections/hardware/build-hardware/carbon-fiber-strips-tubes-spars/carbon-fiber-tubes
