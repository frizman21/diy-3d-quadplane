# COTS subsystem selection: QP-1 (v1 proof of concept)

Status: **Draft for review**, rev B 2026-11-15 (10 lb class, D-025; rev A 2026-11-07)
Related: [requirements](requirements.md) · [decision log](decisions.md) · [Aerodynamics report](AerodynamicsReport.md)

This document records which bought (COTS) parts were selected for each subsystem, the
numbers that drove each choice, and the alternatives that were rejected. Prices and stock
are retailer snapshots from November 2026 (rev B parts were not re-priced; prices marked ~ are estimates). Items marked **VERIFY** must be checked against
the delivered part before the dependent CAD is printed. Mount bolt patterns and envelopes
live in `quadplane/hardware.py`.

**How to read the trade-offs.** Rule D-000 applies: v1 is designed for v1. The future
150 kg aircraft was considered only for the radio, the one expensive purchase that will
carry over.

---

## 1. Summary bill of materials

| # | Subsystem | Selected part | Qty | Mass each | Approx. price | Driving requirement |
|---|---|---|---|---|---|---|
| 1 | Lift motors | T-Motor **MN4014 KV400** (D-027) | 4 | 171 g | $97 | PERF-1, PERF-5 |
| 2 | Lift props | T-Motor **P15x5** carbon (CW/CCW pairs) | 2 pr (+2 spare pr) | 23–27 g | ~$60–80/pr | PERF-5, SIZE-2 |
| 3 | Pusher motor | SunnySky **X3520 520KV** (provisional, D-031) | 1 | ~222 g (**VERIFY**) | ~$60 | PERF-3 (transition) |
| 4 | Pusher prop | Folding **12x8** (Aeronaut CAM Carbon or equivalent); 12x6.5 and 13x8 to bench-test | 1 (+1) | ~30 g with hub | $20–35 | PERF-3 |
| 5 | ESCs | **AM32** single 40–45 A, 6S, DShot (Skystars Talon 40A or Lumenier Razor Pro 45A) | 5 | 3–7 g | $16–31 | — |
| 6 | Battery | **6S3P Molicel P45B 21700 Li-ion** (≈292 Wh, D-028); 6S3P P50B acceptable; 6S2P is the light configuration | 1 (+1) | ~1290 g (**VERIFY**) | ~$100–180 | PERF-1, PERF-7 |
| 7 | Flight controller | **Matek H7A3-WING** (replaces the discontinued H743-WING V3) | 1 | 30 g | ~$90 | SYS-2 |
| 8 | GPS + compass | Matek M10Q-5883 **or its successor** (M10 GNSS + compass) | 1 | 8–15 g | ~$50 | SYS-3 |
| 9 | Airspeed | Matek **ASPD-DLVR** (I²C/DroneCAN) + pitot | 1 | 4 g + tube | $100–130 | QuadPlane transition |
| 10 | RC receiver | RadioMaster **DBR4** (dual-band ExpressLRS Gemini) | 1 | 5.3 g | $30–39 | RC-1…RC-9 |
| 11 | Handset | RadioMaster **TX16S MK3**, dual-band ELRS (D-010) | 1 | — | ~$200 | RC-1…RC-8 |
| 12 | Remote ID | **BlueMark db120** (FAA-declared broadcast module, own GPS and battery) | 1 | 25 g | $119–149 | REG-2 |
| 13 | Servos | **EMAX ES08MD II** (metal gear, digital) | 3 (+1) | 13 g | $12 | — |
| 14 | Wing spar | **20x18 mm roll-wrapped CF tube**, cut to 1.30 m | 1 | 120 g | ~£20–30 | §9 report |
| 15 | Tip spars | **8x6 mm CF tube**, 2 × 0.28 m | 2 | 10 g | £8 | §9 report |
| 16 | Booms | **28x26 mm roll-wrapped CF tube**, cut to 1.14 m (30x28 acceptable) | 2 | 150 g | ~£30–40 | §9 report (vibration) |
| 17 | Tail spar | **8x6 mm CF tube**, 0.62 m | 1 | 21 g | £8 | §9 report |
| 18 | Camera | **Insta360 GO 3S** (D-009) | 1 | 39 g | ~$400 | PAY-1 |
| 19 | Hardware | M3 heat-set inserts, M3/M4 screws, 3 mm CF rod (elevator joiner), pushrods, XT60/XT90 | — | ~50 g | — | BUILD-5 |

Analysed take-off mass with these parts: **4.65 kg (10.25 lb)** (Report §2).

---

## 2. Lift propulsion: motor and prop

**Requirement.** Hover at about 4.65 kg with the front pair carrying 57.9% of the weight
(Report §6.4). That means about 1400 g per front motor and 1020 g per rear motor, download
included. Thrust-to-weight must be at least 1.8 on the most loaded motor (PERF-5), and the
1.4 m overall length limits the prop diameter (SIZE-2).

**Candidates.** All data is manufacturer bench data at 6S (22.2 V):

| Motor | Mass | Prop | Point near hover | g/W | Max thrust | Price |
|---|---|---|---|---|---|---|
| T-Motor MN3508 KV380 (rev A) | 103 g | 14x4.8 CF | 710 g at 64.4 W | 11.0 | 1730 g | $70 |
| **T-Motor MN4014 KV400** | **171 g** | **15x5 CF** | **1250 g at 126.5 W** (50% throttle, 4500 rpm) | **9.9** | **2620 g** (415 W) | $97 |
| T-Motor MN4014 KV400 | 171 g | 16x5.4 CF | 1410 g at 142.1 W (4200 rpm) | 9.9 | 3020 g (500 W) | $97 |
| T-Motor MN4014 KV400 | 171 g | 17x5.8 CF | 1530 g at 168.7 W (4000 rpm) | 9.1 | 3360 g (571 W) | $97 |
| T-Motor MN5008 KV340 | 128 g | 16x5.4 / 17x5.8 CF | 1224–1259 g at 125–138 W | 9.1–9.8 | ≈ 3.5 kg with 17 in | — |

**Decision: MN4014 KV400 with 15x5 carbon props (D-027).**

- The front-motor thrust-to-weight is **1.87**, meeting PERF-5. The rev A MN3508 would give 1.32.
- The 50% bench point (1250 g) sits between the rear and front hover thrusts, so the
  hover-power model is calibrated where it is used.
- With 15 in props the aircraft is **1.357 m long**, within the 1.4 m limit. With 16 in it
  would be 1.408 m. The 16x5.4 prop is otherwise better (T/W 2.15, 29 W less hover power)
  and is the first upgrade if the vehicle turns out to have the room.
- The MN5008 KV340 is 43 g lighter per motor and is rated for larger props, but the
  retailers' tables disagree on which rows belong to which KV, so it stays an option for
  later.

**Risks.**
- The MN4014 is rated 30 A / 900 W for 180 s. At hover each front motor draws about 150 W
  (7 A), under 20% of that rating, so continuous hover is not a thermal risk.
- The stator bolt pattern is **not on the product page**. `hardware.py` assumes 4 × M3 on a
  25 mm circle. **VERIFY** on the delivered motor before printing the mounts (C-2).
- The prop mass differs between sources (21–27 g); 26 g is used.

---

## 3. Pusher motor and prop

**Requirement.** Static thrust of at least **1.68 kg** for the transition (14 m/s in 6 s
while overcoming drag), plus a **30% margin**, giving 2.19 kg (Report §5.4). At 18 m/s the
cruise thrust is about 3.4 N. The thrust line is set by pod geometry at z = −55 mm, with
199 mm from the thrust line to the ground.

**Sizing.** For a 12x8 prop (static C_T ≈ 0.105, C_P ≈ 0.060), 2.19 kg needs about
8,340 rpm. That works out to a motor of about **500 KV** on loaded 6S, drawing about 630 W
at full static thrust.

**Decision (provisional): SunnySky X3520 520KV with a 12x8 folding prop (D-031).**

- At 520 KV the estimated static thrust is about **2.4 kg**, which covers the 30% margin.
- The X3520 class is rated above 1.7 kW, so 630 W is a light load for it.
- The rev A motor (X2820 570KV) with an 11x7 prop was estimated at 1.9–2.0 kg, under the
  margin, so it was not carried over.
- **Bench-test action (C-1):** measure static thrust with the 12x8, and with a 12x6.5 and
  a 13x8 if it is more than 10% off. The 12 in disk has 47 mm of ground clearance; a 13 in
  disk has 34 mm.
- The prop folds back when stopped, to protect it on landing.
- **VERIFY:** no retailer page gave the X3520 520KV's mass or bolt pattern. `mass.py` uses
  222 g and `hardware.py` a 25 mm cross pattern and a 42.5 × 45 mm body.

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

Current check: the most a lift motor draws is about 19 A (415 W at full throttle with the
15x5), and the pusher about 29 A (630 W at 22 V), so a 40 A rating gives at least 1.4×
margin. T-Motor pairs the MN4014 with a 40 A ESC.

---

## 5. Battery

**Requirement.** At least 15 min hover to a 20% reserve (PERF-1), at the hover power of
**515 W** (Report §5.2), and a take-off weight of about 10 lb (PERF-7).

| Option | Energy | Pack mass | Take-off mass | Hover time | Meets PERF-1 | Pack current at full throttle (103 A) |
|---|---|---|---|---|---|---|
| 6S2P Molicel P45B | 194 Wh | 860 g | 4.22 kg (9.3 lb) | 20.9 min | yes, 39% margin | 52 A per cell (limit 45) ✗ |
| 6S LiPo 10000 mAh | 222 Wh | ~1300 g | 4.66 kg | 20.6 min | yes, 37% margin | fine |
| **6S3P Molicel P45B** | **292 Wh** | **~1290 g** | **4.65 kg (10.25 lb)** | **27.2 min** | **yes, 81% margin** | **34 A per cell (limit 45)** |
| 6S3P Molicel P50B | 324 Wh | ~1320 g | 4.68 kg | 29.9 min | yes | 34 A per cell (limit 60) |
| 6S4P Molicel P45B | 389 Wh | ~1720 g | 5.08 kg (11.2 lb) | 31.8 min | yes, but PERF-5 fails (T/W 1.71) | 26 A per cell |

**Decision: 6S3P 21700 Li-ion (Molicel P45B, or P50B if available) (D-028).**

- It is the pack that puts the aircraft at 10 lb, with the same kind of hover margin rev A had.
- 2P is short of current at full throttle on all five motors. That case is brief (a
  transition), so **6S2P remains a valid light configuration** at 9.3 lb if the pusher
  throttle is limited. Both packs fit the bay and the CG range.
- No prebuilt 6S3P P45B pack was found, so this is a pack-builder or DIY spot-welded pack
  (no BMS, balance lead). The mass is scaled from the 6S2P Flywoo pack (860.7 g for 12
  cells); bare cells are 67–70 g each. **VERIFY** the built mass.
- **Connector:** **XT90** (peak current is about 103 A; the flight controller's current
  sensor is rated 100 A continuous, which the hover current of 25 A is far below).
- **Envelope:** 140 × 68 × 75 mm assumed (2 cells long × 3 wide × 3 high; **VERIFY**). The
  pod is 115 mm wide and the hatch opening 74 mm. CG is set by sliding the pack, which ends
  about 151 mm ahead of the wing leading edge, 29 mm short of its forward limit.

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

Load check: the aileron is 0.36 m long with a mean chord of about 66 mm (25% of a ~264 mm
local chord), so its area is about 0.024 m². At 22 m/s (q ≈ 296 Pa) and 20° deflection, with
a hinge-moment coefficient C_h ≈ 0.2, the hinge moment is about 0.09 N·m. The servo gives
0.20 N·m at 6 V, about 2.1× margin with a direct linkage (rev A had 4×). The elevator
(0.56 m × 63 mm) is at about the same load.

If flight loads prove higher, a 17–20 g metal-gear servo (3 kg·cm class) drops into a
slightly larger pocket.

## 9. Carbon tubes

Sizes come from the structural analysis (Report §9):

| Member | Tube | Length | Why this size |
|---|---|---|---|
| Wing spar | 20x18 roll-wrapped | 1.30 m, one piece | +92% ultimate-strength margin at the root (n = 6, 4.8 kg); keeps ≥ 3.3 mm wall inside the wing. 16x14 would be +18% |
| Tip spars | 8x6 | 2 × 0.28 m, running 50 mm inside the main spar on a sleeve (8 mm bore, 18 mm outside) | +350% margin; continues the spar beyond where the 20 mm tube fits |
| Booms | **28x26** roll-wrapped | 2 × 1.14 m (cut from a longer tube) | **Vibration:** the boom's first bending mode is 130–147 Hz, clear of the 60–89 Hz hover 1P band. The rev A 20x18 boom would sit at 77–87 Hz with the heavier motors, inside the band (resonance). |
| Tail spar | 8x6 | 0.62 m | joins the two stab halves and both fins (boom torsion tie) |

**Sources.**
- Easy Composites roll-wrapped metric tubes, 1 m and 2 m lengths. **VERIFY** that 28x26 (or
  30x28) and 20x18 are stocked in a length of 1.2 m or more; the booms no longer fit a 1 m
  tube.
- RMRC and other hobby suppliers for the 8x6 tubes.

If 28x26 is unavailable, **30x28** is acceptable. It adds 11 g per boom and raises the first
mode to 144–164 Hz; `Booms.tube_od` then needs changing so the clamps and saddles follow.
25x23 is 23% above the band, just under the 25% rule.

## 10. Camera (D-009)

**Insta360 GO 3S**, 39 g. It is 4K and IP68 (waterproof to 10 m), and is held in a TPU
cradle under the nose with the button and SD card reachable through a window.

Recording time on its own battery is about 38 min. That is longer than a 27 min hover
session but **shorter than a long cruise flight**, so long-endurance flights need either the
Action Pod or a 5 V tap.

**VERIFY** the camera's outer dimensions (54 × 25.5 × 24.5 mm assumed) before printing the cradle.

---

## 11. Open items

| ID | Item | Owner |
|---|---|---|
| C-1 | Bench-test pusher static thrust with the 12x8 folding prop (12x6.5 and 13x8 as alternatives) | build |
| C-2 | Measure the delivered motors' bolt patterns and the battery envelope; update `hardware.py` | build |
| C-3 | Confirm the BlueMark db120 is on the FAA declared-module list | owner |
| C-4 | Confirm the TX16S MK3 variant has the dual-band (LR1121) internal module | owner |
| C-5 | Tap-test boom natural frequency after assembly (phone accelerometer or ArduPilot FFT log) | build |
| C-6 | Confirm a supplier and a ≥ 1.2 m length for the 28x26 boom tubes and the 20x18 spar | owner |
| C-7 | Find a builder for the 6S3P P45B pack, or build it; weigh and measure it | owner |
| C-8 | Measure the Suburban cargo width above the wheel wells (SIZE-2a): the aircraft needs 1.4 m | owner |

## Sources

- T-Motor MN3508: https://store.tmotor.com/goods-354-MN3508.html
- T-Motor MN4014 KV400 (bench table, 22.2 V): https://store.tmotor.com/product/mn4014-kv400-motor-navigator-type.html
- T-Motor MN5008 KV340: https://www.ligpower.com/product/mn5008-kv340-motor-antigravity-type.html
- T-Motor 15x5 carbon prop (26.5 g): https://uk.robotshop.com/products/t-motor-15-5-carbon-fiber-propeller-pair
- MAD 4006: https://mad-motor.com/products/mad-components-4006-ipe
- T-Motor P15x5: https://irlock.com/products/t-motor-p15x5-prop-2pcs-pair
- T-Motor P14x4.8: https://www.robotshop.com/products/t-motor-14-48-carbon-fiber-propeller-pair
- SunnySky X3520 520KV: https://www.readymaderc.com/products/details/85664-sunnysky-x3520-brushless-motor-520kv
- SunnySky X2820 V3 (rev A): https://www.readymaderc.com/products/details/85632-sunnysky-x-series-v3-x2820-brushless-motor-570kv
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
