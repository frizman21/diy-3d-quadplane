# COTS subsystem selection: QP-1 (v1 proof of concept)

Status: **Draft for review**, rev E 2026-11-18 (5 lb class around $29 lift motors, D-037; rev D: US/dollar sourcing with linked prices, D-036; rev C: 10 lb class, D-025; rev A 2026-11-07)
Related: [requirements](requirements.md) · [decision log](decisions.md) · [Aerodynamics report](AerodynamicsReport.md)

This document records which bought (COTS) parts were selected for each subsystem, the
numbers that drove each choice, and the alternatives that were rejected. Every price in §1 links
to the listing it was read from, and every listing is priced in US dollars (BUILD-1b, D-036).
Prices and stock were read on 2026-11-15 (rows 5, 7–13, 16–19) and 2026-11-18 (the rest) and will drift. Items marked **VERIFY** must be checked against
the delivered part before the dependent CAD is printed. Mount bolt patterns and envelopes
live in `quadplane/hardware.py`.

**How to read the trade-offs.** Rule D-000 applies: v1 is designed for v1. The future
150 kg aircraft was considered only for the radio, the one expensive purchase that will
carry over.

---

## 1. Summary bill of materials

| # | Subsystem | Selected part | Qty | Mass each | Price each (link = listing) | Buy from | Driving requirement |
|---|---|---|---|---|---|---|---|
| 1 | Lift motors | SunnySky **V2806 KV400** (D-037) | 4 | 47 g | [$28.99](https://www.buddyrc.com/products/sunnysky-v2806-motor) | Buddy RC (US), "400" option | BUILD-1c, PERF-5 |
| 2 | Lift props | **12x4.5 carbon**, normal + reverse pair | 2 pr (+2 spare pr) | 14 g | [$8.98/pr](https://www.buddyrc.com/products/carbon-fiber-electric-12x4-5-inch-props-normal-and-reverse-1) | Buddy RC (US). **VERIFY** the hub fits the motor's prop mount | PERF-5 |
| 3 | Pusher motor | A fifth SunnySky **V2806 KV400** (D-037) | 1 | 47 g | [$28.99](https://www.buddyrc.com/products/sunnysky-v2806-motor) | Buddy RC, same order | PERF-3 (transition) |
| 4 | Pusher prop | **APC 12x8E** on SunnySky's pusher prop adapter; 11x7E and 12x6E to bench-test | 1 (+1) | ~30 g with adapter | prop [$4.64](https://www.buddyrc.com/products/apc-12-x-8e-electric), adapter [$5.95](https://www.buddyrc.com/products/sunnysky-v28-and-x28-motor-accessories-for-push-prop) | Buddy RC, same order. The adapter is listed for the V2814; **VERIFY** it fits the V2806 | PERF-3 |
| 5 | ESCs | **Lumenier Razor Pro F4 45A** (AM32, 2–6S, DShot) | 5 | 3–7 g | [$31.49](https://www.racedayquads.com/products/lumenier-razor-pro-f4-45a-2-6s-am32-esc) | RaceDayQuads (US) | — |
| 6 | Battery | **6S1P 21700 Li-ion**: Upgrade Energy RED V3 6S1P 5 Ah, Molicel P50B (108 Wh) (D-037) | 1 (+1) | ~450 g assumed; ships at 500 g (**VERIFY**) | [$120](https://upgradeenergytech.com/products/red-6s1p-5000mah-molicel-p50b) | Upgrade Energy (assembled in the US) | PERF-1, PERF-7 |
| 7 | Flight controller | **Holybro Kakute H743-Wing** (D-036) | 1 | 28 g | [$105](https://holybro.com/products/kakute-h743-wing) | Holybro store (ships from overseas). RaceDayQuads lists it at [$72.99](https://www.racedayquads.com/products/holybro-kakute-3-8s-fixed-wing-flight-controller), out of stock | SYS-2 |
| 8 | GPS + compass | **Holybro Micro M10** (u-blox M10 + IST8308 compass) | 1 | 8–15 g | [$27.99](https://holybro.com/products/micro-m10-gps) | Holybro store, same order as the flight controller | SYS-3 |
| 9 | Airspeed | **Holybro DroneCAN airspeed sensor, DLVR-L10D** + PT40 pitot | 1 | ~5 g + tube (**VERIFY**) | board [$103](https://holybro.com/products/high-precision-dronecan-airspeed-sensor-dlvr) + pitot $7.99 (same listing) | Holybro store, same order | QuadPlane transition |
| 10 | RC receiver | RadioMaster **DBR4** (dual-band ExpressLRS Gemini) | 1 | 5.3 g | [$38.99](https://www.racedayquads.com/products/radiomaster-dbr4-dual-band-xross-gemini-expresslrs-receiver) | RaceDayQuads (US). RadioMaster direct: [$29.99](https://radiomasterrc.com/products/dbr4-dual-band-xross-gemini-expresslrs-receiver) | RC-1…RC-9 |
| 11 | Handset | RadioMaster **TX16S MK3**, dual-band ELRS, FCC version (D-010) | 1 | — | [$229.99](https://www.racedayquads.com/products/radiomaster-tx16s-mk3-radio-controller-elrs-dual-band) | RaceDayQuads (US). RadioMaster direct: [$199.99](https://radiomasterrc.com/products/tx16s-mk3-radio-controller) | RC-1…RC-8 |
| 12 | Remote ID | **BlueMark db120** (FAA-declared broadcast module, own GPS and battery) | 1 | 25 g | [$58.99](https://www.dslrpros.com/products/dronebeacon-db120-remoteid-broadcast-module-with-battery) | DSLRPros (US) | REG-2 |
| 13 | Servos | **EMAX ES08MD II** (metal gear, digital) | 3 (+1) | 13 g | [$12.50](https://alofthobbies.com/products/emax-es08mdii-servo-2kg-27-77-oz-in-10-sec-13-grams) | Aloft Hobbies (US) | — |
| 14 | Wing spar | **20x18 mm roll-wrapped CF tube, 500 mm**, uncut | 1 | 46 g | [$15.53](https://carbonkevlarsupply.com/products/blue-black-carbon-fiber-tubing-20mm-x-18mm-x-500mm-3k-roll-wrapped-glossy) | Carbon Kevlar Supply (§9) | §9 report |
| 15 | Tip spars | **10x8 mm roll-wrapped CF tube, 500 mm**, uncut | 2 | 22 g | [$8.99](https://carbonkevlarsupply.com/products/carbon-fiber-tube-10mm-x-8mm-x-500mm-3k-roll-wrapped-100-carbon-fiber-tube-glossy) | Carbon Kevlar Supply | §9 report |
| 16 | Booms | **25x23 mm roll-wrapped CF tube, 1000 mm**, cut to 840 mm | 2 | 98 g cut | [$38.99 for 2](https://carbonkevlarsupply.com/products/2-carbon-fiber-tubes-25mm-x-23mm-x-1000mm-3k-roll-wrapped-100-carbon-fiber-tube-glossy-surface-2-tubes) | Carbon Kevlar Supply | §9 report (vibration) |
| 17 | Tail spar | **8x6 mm pultruded CF tube, 1000 mm**, cut to 0.60 m | 1 | 20 g | [$8.99](https://carbonkevlarsupply.com/products/1-piece-8mm-x-6mm-x-1000mm-carbon-fiber-tube-pultruded-round-tube-super-high-strength-for-rc-hobbies-drones-special-projects) | Carbon Kevlar Supply | §9 report |
| 18 | Camera | **Insta360 GO 3S**, 128 GB (D-009) | 1 | 39 g | [$379.99](https://store.insta360.com/product/go-3s) | Insta360 store | PAY-1 |
| 19 | Hardware | 4 mm pultruded CF rod (elevator joiner); M3 heat-set inserts, M3/M4 screws, pushrods, XT60 (not priced) | — | ~45 g | rod [$17.99](https://carbonkevlarsupply.com/products/1-piece-4mm-x-1000mm-carbon-fiber-rods-solid-pultruded-round-rods-super-high-strength-for-rc-hobbies-drones-special-projects) | Carbon Kevlar Supply | BUILD-5 |

**Total at these prices: about $1,575** for one aircraft set with the handset and camera,
the spare props and servo, and one battery. That is about $730 less than the 10 lb list
(about $2,300). Shipping, tax, small hardware and filament are not included.

| Where the $730 went | 10 lb list | 5 lb list | Saving |
|---|---|---|---|
| Lift motors (4) | $388 | $116 | $272 |
| Lift props (4 pairs) | $224 | $36 | $188 |
| Battery | $340 | $120 | $220 |
| Pusher motor, prop and hub | $88 | $44 | $44 |
| Carbon | $106 | $99 | $7 |

**The aircraft without the handset and camera is about $970.**

**Where the list is weak:**
- **Everything about the motor beyond its bench table is unverified:** the bolt pattern,
  the prop mount, whether the 12x4.5 prop hub and the pusher adapter fit, and the thrust
  with the prop actually bought (C-2, C-10). Buy one motor, one prop pair and the adapter
  first, test, then order the rest. That is about $50 of risk.
- **Fixed-wing flight controllers, Matek GPS and Matek airspeed sensors are out of stock at
  every US shop checked** (2026-11-15). The Holybro store has rows 7–9 in stock in dollars,
  but ships from overseas.
- **Battery:** the pack's mass and size are from its cell count, not a datasheet (C-7). At
  5 lb, 50 g matters: it is the whole thrust margin.

Analysed take-off mass with these parts: **2.34 kg (5.17 lb)** (Report §2). Items 14–17 and the elevator rod all come from carbonkevlarsupply.com (§9).

---

## 2. Lift propulsion: motor and prop

**Requirement.** The four lift motors together cost about $100 (BUILD-1c), and each must
have a thrust-to-weight ratio of at least 1.8 against the weight it carries (PERF-5). The
aircraft is sized to the motor: its mass is whatever the motor's full-throttle thrust
allows.

**Candidates.** Motors near $25–30 at US shops on 2026-11-18, with the seller's bench data:

| Motor | Price | Mass | Battery, prop | Max thrust | Hover power for the aircraft it can carry | Aircraft it can carry |
|---|---|---|---|---|---|---|
| **SunnySky V2806 KV400** | [$28.99](https://www.buddyrc.com/products/sunnysky-v2806-motor) | **47 g** | **6S, 12x5** | **1120 g** (190 W) | **312 W** | **2.39 kg (5.3 lb)** |
| SunnySky X2814 KV900 | [$29.99](https://www.buddyrc.com/products/sunnysky-x2814-brushless-motors) | 108 g | 4S, 11x7 | 2020 g (509 W) | ≈ 820 W | 4.3 kg (9.5 lb) |
| SunnySky X2216 V3 KV880 | [$24.99](https://www.buddyrc.com/products/sunnysky-x2216) | 68 g | 4S, 10x4.7 | 1650 g (403 W) | ≈ 650 W | 3.5 kg (7.8 lb) |
| SunnySky X3108S KV900 | [$24.99](https://www.buddyrc.com/products/sunnysky-x3108s-motors) | — | — | no data on the listing | — | not assessed |

"Aircraft it can carry" is 4 × max thrust ÷ (1.8 × 1.04 download). The two 4S figures for
hover power are hand estimates from the bench tables, not analysis results.

**Decision: SunnySky V2806 KV400 with 12 in props on 6S (D-037).** The owner chose the
5 lb, 6S option from these three.

- **It is the only one of the three that hovers efficiently.** It is a low-KV multirotor
  motor swinging a 12 in prop; the other two are aeroplane motors with small props, and
  need 2–2.6 times the hover power. That power has to come from a battery that the same
  motors must lift.
- **It keeps 6S**, so the ESCs, flight controller and power wiring chosen earlier stay.
- **Hover:** 609 g per motor at 73 W, 54% of full thrust. Thrust-to-weight **1.84** on
  every motor, because the hover is balanced front to rear (Report §6.4).
- **Prop choice** (Report §5.2): the 11 in prop reaches only 834 g; the 13 in prop reaches
  1080 g and overheats the motor (101 °C after 30 s at full throttle in the seller's table).
  With the 12 in prop the table shows 77 °C after 3 min.

**Risks.**
- **The margin is 2%.** The rule fails at 2.39 kg; the aircraft is 2.34 kg.
- **The prop bought is a 12x4.5, the prop in the bench table a 12x5** (SunnySky's EOLO
  CN12x5, not stocked in the US). **Bench-test before ordering five motors** (C-10).
- The motor is rated 250 W and 10 A for 180 s. Hover is 73 W, so continuous hover is not a
  thermal risk; sustained full throttle is.
- The stator bolt pattern and the prop mount are **not on the product page**.
  `hardware.py` assumes 4 × M3 on a 19 mm circle. **VERIFY** on the delivered motor before
  printing the mounts (C-2).

---

## 3. Pusher motor and prop

**Requirement.** Static thrust of at least **0.85 kg** for the transition (14 m/s in 6 s
while overcoming drag), plus a **30% margin**, giving 1.11 kg (Report §5.4). At 18 m/s the
cruise thrust is about 2.0 N. The thrust line is set by pod geometry at z = −45 mm, with
189 mm from the thrust line to the ground.

**Sizing.** For a 12x8 prop (static C_T ≈ 0.105, C_P ≈ 0.060), 1.11 kg needs about
5,940 rpm. That works out to a motor of about **350 KV** on loaded 6S, drawing about 230 W.

**Decision: a fifth SunnySky V2806 KV400 with an APC 12x8E (D-037).**

- 400 KV is close to the 350 KV the sizing asks for, and the motor is already on the
  order. One spare motor covers all five positions.
- At full throttle the same estimate gives about 1.4 kg and 330 W, over the motor's 250 W
  rating. **Limit the pusher throttle to about 90%.**
- **Top speed is about 20 m/s.** A low-KV motor has a low pitch speed (about 25.6 m/s in
  flight with an 8 in pitch). Cruise at 15 m/s.
- The prop is a fixed APC 12x8E on SunnySky's bolt-on pusher adapter. A folding prop needs
  a shaft, which this motor does not have. The disk has 37 mm of ground clearance, and its
  tip passes 20 mm from the rear lift-prop disks in plan view.
- **Bench-test action (C-1):** measure static thrust, current and motor temperature with
  the 12x8E. If the motor runs hot, try an 11x7E; if thrust is short, a 12x6E.
- **Alternative if the bench test fails:** a purpose-built 6S aeroplane motor near 500 KV.
  The SunnySky X3520 520KV of the 10 lb design ([$46.99](https://www.buddyrc.com/products/sunnysky-x3520-brushless-motor), 222 g) works but adds about 170 g at the tail,
  which the thrust margin cannot absorb; a lighter one would have to be found.

---

## 4. ESCs

BLHeli_32 has reached end of life, so **AM32** firmware is the current choice. It supports
DShot and bidirectional DShot, which gives the flight controller RPM telemetry so
ArduPilot's harmonic notch filter can track motor speed.

**Decision: five single AM32 ESCs (40–45 A, 6S), Lumenier Razor Pro F4 45A**, one at each lift motor on the boom
(close to the motor, short leads) and one in the pod for the pusher.

| ESC | Rating | Mass | Notes |
|---|---|---|---|
| **Lumenier Razor Pro F4 45A AM32** | 2–6S, 45 A | 3 g | **selected**: in stock in the US ($31.49, §1 row 5) |
| Skystars Talon 40A AM32 | 3–6S, 40 A, telemetry | 6.8 g | cheaper, but not stocked by a US shop on 2026-11-15 |
| Holybro Tekko32 F4 50A 4-in-1 | 4–6S | 13.8 g | rejected: a 4-in-1 needs about 0.5 m motor leads on a twin-boom layout |

Current check: the most a lift motor draws is about 9 A (190 W at full throttle with the
12 in prop), and the pusher about 10 A (230 W at 22 V), so a 45 A ESC has more than 4×
margin. SunnySky recommends a 20 A ESC for the V2806. **A lighter, cheaper 20–30 A AM32 ESC
would do** (§12.3); the Razor Pro stays selected because it is in US stock and already
checked.

---

## 5. Battery

**Requirement.** At least 15 min hover to a 20% reserve (PERF-1), at the hover power of
**312 W** (Report §5.2), without taking the aircraft over the 2.39 kg the lift motors can
carry (PERF-5).

| Option | Energy | Pack mass | Take-off mass | Hover time | Lift-motor T/W | Verdict |
|---|---|---|---|---|---|---|
| 6S1P Molicel P30B (3 Ah) | 65 Wh | ~330 g | 2.22 kg | 10.8 min | 1.94 | ✗ hover time; 45 A peak is over its 36 A limit |
| **6S1P Molicel P50B (5 Ah)** | **108 Wh** | **~450 g** | **2.34 kg (5.17 lb)** | **16.6 min** | **1.84** | ✅ **both, with thin margins** |
| 6S LiPo 5000 mAh | 111 Wh | ~700 g | 2.59 kg | 14.8 min | 1.66 | ✗ both |
| 6S2P Molicel P50B (10 Ah) | 216 Wh | ~860 g | 2.75 kg | 26.3 min | 1.57 | ✗ thrust margin |

**Decision: 6S1P Molicel P50B, bought ready-made (D-037).**

- **It is the only pack that meets both requirements.** More energy means more mass than
  the motors can lift with margin; a LiPo of the same energy is 250 g heavier.
- **Ready-made:** Upgrade Energy RED V3 6S1P 5 Ah (P50B, assembled in the US, $120; §1
  row 6). It also comes as a "Long" version at the same price; the standard one is assumed.
- **Hover margin is 11%.** A cold or aged pack will not give 15 min (Report R-18). Buy
  two and plan 12–13 min hovers.
- **Mass and size are assumed.** 450 g is six 70 g cells plus leads and wrap; the seller's
  shipping weight is 500 g. The envelope is assumed to be 76 × 68 × 46 mm (3 cells wide ×
  2 high, lying flat). **VERIFY both** on the first pack before printing the pod (C-7). Each
  10 g over costs 0.4% of take-off mass, and the thrust margin is 2%.
- **Current:** hover 15 A (3C), full-throttle peak 45 A. The P50B is rated 60 A continuous.
- **Connector:** **XT60** is enough at these currents. The flight controller's current
  sensor is rated 90 A continuous.
- **Fit:** the pod is 95 mm wide and the hatch opening 74 mm. CG is set by sliding the
  pack, which ends about 92 mm ahead of the wing leading edge, 70 mm short of its forward
  limit.
- The same shop sells an Amprius-cell 6S1P 5 Ah pack ("RED V4", [$126](https://upgradeenergytech.com/products/red-v4-6s1p-5ah-drone-battery)) that ships 74 g lighter.
  If its real mass is that much lower, it would raise the thrust margin from 2% to 5%. Its
  cell rating and mass were **not checked**; it is not in the analysis.

---

## 6. Flight controller, GPS, airspeed, power

- **Flight controller: Holybro Kakute H743-Wing (D-036).** Matek now lists the H7A3-WING
  chosen in D-016 as end of life, and no US shop has one. The Kakute H743-Wing is the same
  class of board and is in production:
  - STM32H743, ICM-42688-P, microSD logging.
  - 14 PWM outputs. v1 needs 5 motors + 3 servos = 8, leaving 6 spare.
  - 7 UARTs, 1 CAN port, 2 external I²C ports, with plug-in GPS, CAN and I²C sockets.
  - A built-in current sensor (90 A continuous, 220 A peak), so no separate power module.
    Hover draws about 15 A and the full-throttle peak is about 45 A.
  - A 6 A servo supply (6 V or 8 V) and 5 V and 9 V/12 V supplies; input 3–8S.
  - ArduPilot target `KakuteH7-Wing` (4.4+). 45 × 30 × 13.5 mm, 28 g.

  **VERIFY** before wiring: the output numbering against the ArduPilot page for this
  board, and that the four lift motors sit on timer groups that can all run DShot.
- **GPS: Holybro Micro M10** (u-blox M10 with an IST8308 compass, no case). Holybro sells
  it bundled with this flight controller, so the cable matches. Any M10 GNSS + compass
  module of about 10 g works; RaceDayQuads has the Foxeer M10Q-180 V2 in US stock at
  $23.99. It is mounted on a 60 mm mast on the nose top, away from power wiring and the
  motors.
- **Airspeed: Holybro DroneCAN airspeed sensor (DLVR-L10D) with the PT40 pitot.** ArduPilot
  QuadPlane transitions depend on airspeed, and a synthetic airspeed estimate isn't
  acceptable during first flights. It uses the same DLVR pressure sensor as the Matek
  ASPD-DLVR and plugs into the board's CAN port. The L10D range is 2500 Pa; the aircraft
  sees about 245 Pa at 20 m/s. The Matek ASPD-DLVR ($131.99 at RaceDayQuads, out of stock)
  is a drop-in alternative. The pitot sits on the nose, clear of the front prop wash.

## 7. Radio link (D-010) and Remote ID

- **Handset: RadioMaster TX16S MK3** with internal dual-band ExpressLRS (2.4 GHz + 900 MHz).
  **VERIFY:** order the version with the Gemini/LR1121 dual-band module.
- **Receiver: RadioMaster DBR4** (two LR1121 radios in Gemini mode, 5.3 g).
  It connects over CRSF on one UART, carries MAVLink telemetry, and provides link-quality
  information for the failsafe.
- **Remote ID: BlueMark db120.** It is a self-contained broadcast module with its own GPS
  and battery, which suits a hobbyist build. The Holybro/ArduRemoteID option is rejected:
  it would make the builder file their own FAA Declaration of Compliance.
  **VERIFY** the db120 is on the FAA's list of declared modules before buying.

## 8. Servos

Three **EMAX ES08MD II** servos (13 g, 2.0 kg·cm at 6 V, metal gear, 0.10 s): two ailerons
and one elevator.

Load check: the aileron is 0.26 m long with a mean chord of about 49 mm (25% of a ~195 mm
local chord), so its area is about 0.013 m². At 20 m/s (q ≈ 245 Pa) and 20° deflection, with
a hinge-moment coefficient C_h ≈ 0.2, the hinge moment is about 0.03 N·m. The servo gives
0.20 N·m at 6 V, about 6× margin with a direct linkage. The elevator (0.54 m × 42 mm) is at
about 0.05 N·m, 4× margin.

**The aileron servos lie on their sides.** The wing is about 17 mm deep at the pocket and
the servo is 22 mm tall, so the pocket is 24 × 22 mm and 12.5 mm deep. A 9 g servo would
also carry these loads and would save 12 g, but was not checked for stock.

## 9. Carbon tubes and rods

**All of these come from one supplier, carbonkevlarsupply.com (BUILD-1a, D-033).** Its
catalogue was checked on 2026-11-15. What it stocks in round tube:

| Type | Sizes (OD x ID) | Longest |
|---|---|---|
| Roll-wrapped 3K (twill or plain weave) | 8x6, 10x8, 14x12, 16x14 | 500 mm |
| Roll-wrapped 3K | 20x18, 25x23 | 1000 mm |
| Pultruded | 6x4, 8x6, 12x8, 16x12, 20x16, 25x22 | 1000 mm |
| Solid pultruded rod | 2, 4, 8, 10 mm (6, 14, 18 mm out of stock) | 1000 mm |

There is nothing longer than 1000 mm, no 28 mm tube and no 3 mm rod. The 5 lb design
(D-039) uses only these sizes (Report §9). `quadplane/hardware.py` holds this stock list and
`make test` fails if a tube in `params.py` is not on it or is longer than stocked.

### 9.1 Order list

| Member | Buy | Qty | Cut | Listing (in stock 2026-11-18) | Price (link = listing) |
|---|---|---|---|---|---|
| Wing spar | 20x18 x 500 mm, 3K roll-wrapped | 1 | none | "Carbon Fiber Tube - 20mm x 18mm x 500mm - 3K Roll Wrapped Tube Glossy Surface", qty 1 | [$15.53](https://carbonkevlarsupply.com/products/blue-black-carbon-fiber-tubing-20mm-x-18mm-x-500mm-3k-roll-wrapped-glossy) |
| Booms | 25x23 x 1000 mm, 3K roll-wrapped | 2 | each to 840 mm | "(2) Carbon Fiber Tubes - 25mm x 23mm x 1000mm - 3K Roll Wrapped 100% Carbon Fiber Tube" | [$38.99](https://carbonkevlarsupply.com/products/2-carbon-fiber-tubes-25mm-x-23mm-x-1000mm-3k-roll-wrapped-100-carbon-fiber-tube-glossy-surface-2-tubes) |
| Tip spars | 10x8 x 500 mm, 3K roll-wrapped | 2 | none | "Carbon Fiber Tube - 10mm x 8mm x 500mm - 3K Roll Wrapped 100% Carbon Fiber Tube Glossy", qty 2 at $8.99 | [$17.98](https://carbonkevlarsupply.com/products/carbon-fiber-tube-10mm-x-8mm-x-500mm-3k-roll-wrapped-100-carbon-fiber-tube-glossy) |
| Tail spar | 8x6 x 1000 mm, pultruded | 1 | to 600 mm | "(1) Piece - 8mm x 6mm x 1000mm Carbon Fiber Tube - Pultruded Round Tube" | [$8.99](https://carbonkevlarsupply.com/products/1-piece-8mm-x-6mm-x-1000mm-carbon-fiber-tube-pultruded-round-tube-super-high-strength-for-rc-hobbies-drones-special-projects) |
| Elevator joiner | 4 mm x 1000 mm solid rod, pultruded | 1 | to about 550 mm | "(1) Piece - 4mm x 1000mm Carbon Fiber RODS - Solid Pultruded Round Rods" | [$17.99](https://carbonkevlarsupply.com/products/1-piece-4mm-x-1000mm-carbon-fiber-rods-solid-pultruded-round-rods-super-high-strength-for-rc-hobbies-drones-special-projects)
| | | | | **Total** | **about $99** |

- **Buy the plain carbon tubes, not the "Carbon Fiber Kevlar" ones.** The supplier sells
  red and blue hybrid tubes in the same sizes. The analysis assumes all-carbon tube.
- Each boom leaves a 160 mm offcut. Keep them for test-fitting the printed clamps.
- Prices and stock are a snapshot; the supplier has several listings per size, in
  different colours and pack sizes.

### 9.2 Why each size

| Member | Tube | Length | Why this size |
|---|---|---|---|
| Wing spar | 20x18 roll-wrapped | 0.50 m, one piece, uncut | +428% ultimate-strength margin at the root (n = 6, 2.4 kg); keeps 1.2 mm of wall inside the wing. Far stronger than needed: it is this size so the tip tube can sleeve inside it |
| Tip spars | 10x8 roll-wrapped | 2 × 0.50 m, from 130 mm to 630 mm; 120 mm inside the main spar on a sleeve (10 mm bore, 18 mm outside) | +242% margin; tip deflection 15 mm at limit load. The 14x12 tube of the 10 lb design leaves only 0.3 mm of skin at this wing's tip |
| Booms | **25x23** roll-wrapped | 2 × 0.84 m | **Vibration:** first bending mode 155–176 Hz, 71–94% above the 71–91 Hz hover 1P band. A 20x18 boom is 21% above; the rule is 25% |
| Tail spar | 8x6 pultruded | 0.60 m | joins the two stab halves and both fins. Roll-wrapped 8x6 is only stocked in 500 mm. Pultruded is acceptable here: the loads are low and nothing clamps onto it |
| Elevator joiner | 4 mm pultruded rod | about 0.55 m | 3 mm rod is not stocked |

**Material data.** The supplier publishes no modulus, strength or tolerance figures. The
analysis assumes E = 70–90 GPa and a 400 MPa allowable. **Check the tubes on delivery**
(Report R-16): weigh them (20x18 ≈ 93 g/m, 25x23 ≈ 117 g/m, 10x8 ≈ 44 g/m) and measure the
wall.

**If a tube is out of stock or fails the check:**
- Booms: 25x22 pultruded (stiffer, +46 g per boom). Use wider clamp bands; pultruded tube
  splits under point clamping.
- Tip spars: 8x6 roll-wrapped x 500 mm (+103% margin, tip deflection 24 mm); the wing bore
  and the sleeve then need changing (`Wing.tip_spar_od`).
- Spar: 25x23 does not fit this wing. Use a second 20x18.

## 10. Camera (D-009)

**Insta360 GO 3S**, 39 g. It is 4K and IP68 (waterproof to 10 m), and is held in a TPU
cradle under the nose with the button and SD card reachable through a window.

Recording time on its own battery is about 38 min. That is longer than a 17 min hover
session and close to the planning cruise endurance (about 50 min), so only the longest
flights need the Action Pod or a 5 V tap.

**VERIFY** the camera's outer dimensions (54 × 25.5 × 24.5 mm assumed) before printing the cradle.

---

## 11. Open items

| ID | Item | Owner |
|---|---|---|
| C-10 | **First purchase: one V2806 KV400, one 12x4.5 prop pair, the pusher adapter and an APC 12x8E.** Bench-test the lift prop for full-throttle thrust (needs ≥ 1120 g at 22 V), current and motor temperature after 3 min. Then order the rest | owner |
| C-1 | Bench-test pusher static thrust, current and temperature with the 12x8E (needs 1.11 kg at about 230 W); 11x7E and 12x6E as alternatives | build |
| C-2 | Measure the V2806's stator bolt pattern and prop mount, and the battery envelope; update `hardware.py` before printing the mounts and the pod | build |
| C-7 | Weigh and measure the first 6S1P pack against 450 g and 76 × 68 × 46 mm; rerun the analysis with the weighed mass | owner |
| C-9 | Kakute H743-Wing: confirm output numbering and DShot timer groups for the four lift motors. Confirm the 12x4.5 prop hub and the pusher adapter fit the V2806 | build |
| C-3 | Confirm the BlueMark db120 is on the FAA declared-module list | owner |
| C-4 | Confirm the TX16S MK3 variant has the dual-band (LR1121) internal module | owner |
| C-5 | Tap-test boom natural frequency after assembly (phone accelerometer or ArduPilot FFT log) | build |
| C-6 | Order the carbon from carbonkevlarsupply.com (§9.1); on delivery, weigh and measure (Report R-16) | owner |
| C-8 | Test-fit the finished aircraft in the Suburban (1.065 m × 1.30 m; no longer blocks printing) | owner |

## 12. Alternative parts

These are substitutes for the parts selected in §1. None of them is in the design. Each
row says what changes if it is used. Prices and stock were read on 2026-11-15 and
2026-11-18. The alternatives studied for the 10 lb design (SunnySky V4014 and X4110S
motors, EOLO 15x5.5 props) are in rev D of this document in the git history.

### 12.1 Lift motors: what a bigger budget buys

The selected motor leaves 2% of thrust margin and 11% of hover-time margin. If a bench
test or the finished weight shows that is not enough, the fix is a larger motor, and the
airframe has to be re-run for it (heavier motors, larger props, longer booms).

| Motor | Price each | Set of 4 | Mass | Max thrust (6S) | In this airframe | Notes |
|---|---|---|---|---|---|---|
| **SunnySky V2806 KV400** (selected) | $28.99 | $116 | 47 g | 1120 g, 12 in | 2.34 kg, 312 W, 16.6 min, T/W 1.84 | baseline |
| T-Motor MN3508 KV380 | about $70 | $280 | 103 g | 1730 g, 14x4.8 | 2.58 kg, 256 W, 20.3 min, T/W 2.58 | from `analysis/results/propulsion.json`; needs 14 in props, booms 100 mm longer and the layout re-run. Price is the rev A figure, not rechecked |
| SunnySky V3506 | [$37.99](https://www.buddyrc.com/products/sunnysky-v3506-motor) | $152 | — | — | not assessed | the next size up in the same series; bench table not read |
| SunnySky X3508S KV580 | [$34.98](https://www.buddyrc.com/products/sunnysky-x3508s-kv580-brushless-motor-on-sale) | $140 | — | — | not assessed | no bench data on the listing |

### 12.2 Lift props

| Prop | Price per pair | 4 pairs | Notes |
|---|---|---|---|
| 12x4.5 carbon, normal + reverse (selected) | $8.98 | $36 | 14 g each; not the prop in the motor's bench table |
| Eolo foldable 12x5, carbon-reinforced nylon, with adapters | [$29.99](https://www.buddyrc.com/products/eolo-foldable-carbon-fiber-and-nylon-composite-uav-propellers-12x5-inch) | $120 | SunnySky's own brand and the 12x5 size of the bench table, but folding, with a hub. Heavier (not weighed); raises the boom tip mass |
| GemFan carbon-reinforced 12x4.5 | [$5.99 each](https://www.buddyrc.com/products/gemfan-carbon-fiber-reinforced-12x4-5-inch-normal-ccw-propellers) | about $48 | normal and reverse sold separately; slow-flyer hub, softer than carbon |
| MPI 12x4.5 counter-rotating pair | [$6.99](https://www.buddyrc.com/products/mpi-12-electric-counter-rotating-prop-pairs-12x4-5) | $28 | nylon; the cheapest, and the least stiff |

### 12.3 Other subsystems

| Subsystem | Selected (§1) | Alternative | Price | What changes |
|---|---|---|---|---|
| Battery | Upgrade Energy 6S1P P50B, $120 | Upgrade Energy RED V4 6S1P 5 Ah (Amprius cells) | [$126](https://upgradeenergytech.com/products/red-v4-6s1p-5ah-drone-battery) | ships 74 g lighter; would add thrust margin. Cell current rating and real mass not checked |
| Battery | as above | Upgrade Energy RED V3 6S2P P50B (10 Ah) | [$219](https://upgradeenergytech.com/products/red-6s2p-10000mah-molicel-p50b) | 26 min of hover, but 2.75 kg and T/W 1.57: **fails PERF-5**. Only with larger lift motors |
| ESCs | Lumenier Razor Pro 45A, $31.49 | Any 20–30 A AM32 ESC with DShot | not priced | the motors draw 9–10 A at most, so a 45 A ESC is oversized. None was checked for US stock |
| ESCs | as above | Skystars Talon32 Slim 40A | [$23.99](https://www.racedayquads.com/products/skystarsrc-talon32-slim-40a-32-bit-3-6s-esc) | out of stock on 2026-11-15; BLHeli_32 firmware (end of life); saves $37 for five |
| Pusher motor | fifth V2806 KV400, $28.99 | SunnySky X3520 520KV | [$46.99](https://www.buddyrc.com/products/sunnysky-x3520-brushless-motor) | a proper aeroplane motor with ample thrust and speed, but 222 g: about 170 g more, at the tail. The thrust margin cannot absorb it |
| Flight controller | Holybro Kakute H743-Wing, $105 | Same board with pin headers, from RaceDayQuads | [$72.99](https://www.racedayquads.com/products/holybro-kakute-3-8s-fixed-wing-flight-controller) | out of stock; saves $32 and ships from the US |
| Flight controller | as above | Holybro Pixhawk 6C Mini | [$179](https://holybro.com/products/pixhawk-6c-mini) | needs a separate power module and a servo supply; more wiring and mass |
| GPS + compass | Holybro Micro M10, $27.99 | Foxeer M10Q-180 V2 | [$23.99](https://www.racedayquads.com/products/foxeer-gps-m10q-180-gps-compass) | US stock; the cable has to be re-pinned for the board's GPS socket |
| Airspeed | Holybro DroneCAN DLVR, $111 with pitot | Matek ASPD-DLVR | [$131.99](https://www.racedayquads.com/products/matek-digital-airspeed-sensor-aspd-dlvr) | out of stock; same sensor, CAN or I²C |
| Receiver | RaceDayQuads, $38.99 | RadioMaster direct | [$29.99](https://radiomasterrc.com/products/dbr4-dual-band-xross-gemini-expresslrs-receiver) | same part; shipping origin not checked |
| Handset | RaceDayQuads, $229.99 | RadioMaster direct, FCC version | [$199.99](https://radiomasterrc.com/products/tx16s-mk3-radio-controller) | same part; saves $30; shipping origin not checked |
| Servos | Aloft Hobbies, $12.50 | Same servo from RaceDayQuads | [$13.49](https://www.racedayquads.com/products/emax-es08md-ii-12g-digital-metal-gear-servo) | nothing; useful to combine with the ESC order |
| Carbon tubes | — | see §9.2, "If a tube is out of stock" | — | — |

## Sources

Purchase listings are linked from the price column in §1. The links below are the data
sources (bench tables, datasheets, masses) and the listings that were checked and rejected.

- SunnySky V2806 KV400 bench table (22.2 V and 25 V, EOLO CN11/12/13/15 props) and specifications: https://www.buddyrc.com/products/sunnysky-v2806-motor
- SunnySky X2814 KV900 bench table (4S candidate): https://www.buddyrc.com/products/sunnysky-x2814-brushless-motors
- SunnySky X2216 V3 KV880 bench table (4S candidate): https://www.buddyrc.com/products/sunnysky-x2216
- T-Motor MN3508 (reference motor): https://store.tmotor.com/goods-354-MN3508.html
- T-Motor MN4014 KV400 (10 lb design, rev D of this document): https://store.tmotor.com/product/mn4014-kv400-motor-navigator-type.html
- Upgrade Energy 6S1P packs (P50B, P50B Long, RED V4): https://upgradeenergytech.com/products/red-6s1p-5000mah-molicel-p50b
- Molicel P50B datasheet: https://www.fsaeonline.com/content/Molicel-TDS--INR-21700-P50B-80122.pdf
- Molicel P45B datasheet: https://www.imrbatteries.com/content/molicel_p45b.pdf
- Matek H7A3-WING, marked end of life by Matek: https://www.mateksys.com/?p=12747
- Matek ASPD-DLVR (RaceDayQuads, out of stock): https://www.racedayquads.com/products/matek-digital-airspeed-sensor-aspd-dlvr
- Foxeer M10Q-180 V2 GPS + compass (RaceDayQuads, in stock): https://www.racedayquads.com/products/foxeer-gps-m10q-180-gps-compass
- Holybro Remote ID: https://docs.holybro.com/radio/remote-id/overview-and-spec
- Carbon Kevlar Supply (all carbon tubes and rods): https://carbonkevlarsupply.com/

