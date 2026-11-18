# QP-1 manufacturing and build instructions

Status: **Draft for review**, 2026-11-18, for the 5 lb design around SunnySky V2806 motors (report revision D)
Related: [requirements](requirements.md) · [Aerodynamics report](AerodynamicsReport.md) · [COTS selection](cots-selection.md) · [decision log](decisions.md)

This document takes you from an empty printer to an aircraft that is weighed, balanced
and ready for its first hover. Dimensions quoted here come from `quadplane/params.py` and
the CAD. If the parameters change, rerun the chain in the [README](../README.md) and
check the numbers here against the new output.

**What the CAD does not model.** The CAD covers the printed airframe and envelope shapes
for the bought parts. It has no hinges, control horns, pushrods, wiring, ESC mounts,
elevator servo mount, GPS mast, hatch latch, or TPU feet. Steps that depend on those are
marked **builder's choice**, with a suggested method. Nothing in this document has been
built yet, so treat it as a plan and correct it as you go.

---

## 1. Before you print anything

Do these in order. Each one can change the CAD.

1. **Buy and bench-test one motor first** (open item C-10): one SunnySky V2806 KV400, one
   12x4.5 prop pair, the pusher prop adapter and an APC 12x8E. On 6S the lift prop must
   give at least 1120 g at full throttle without overheating. The whole design depends on
   that figure, and it leaves only 2% of margin. If the thrust is short, stop and revisit
   the design before buying or printing anything else.
2. **Print the fit coupon** (`build/fit_coupon.stl`, PETG). It has six tube holes and six
   heat-set insert holes in graded sizes. Find the hole that gives a slip fit on a carbon
   tube and the one that takes an M3 insert cleanly, then update the clearances in
   `quadplane/printer.py`.
3. **Print and weigh an LW-PLA density coupon.** The mass estimate assumes a foamed
   density of 0.75 g/cm³ (about 230 °C nozzle temperature). Print a simple block with the
   wing profile below, weigh it, and update `printer.LWPLA`. The printed airframe is 36%
   of the take-off mass, and 50 g of extra weight uses up the whole thrust margin.
4. **Receive and measure the bought parts**, then update `quadplane/hardware.py`:
   - motor bolt pattern (assumed 4 × M3 on a 19 mm circle), body size and prop mount; the
     same motor is used in all five positions;
   - battery pack size (assumed 76 × 68 × 46 mm) and mass (assumed 450 g);
   - camera size.
5. **Bench-test the pusher**: static thrust, current and motor temperature with the APC
   12x8E. It needs 1.11 kg at about 230 W (open item C-1). The motor is rated 250 W.
6. **Rerun the chain** and confirm `make test` passes:

   ```sh
   docker compose run --rm cad python scripts/assemble.py
   make analysis-fast
   docker compose run --rm cad python scripts/assemble.py
   make build && make test
   ```

---

## 2. What you need

### 2.1 Bought parts
The full list with reasons and sources is in [cots-selection.md](cots-selection.md) §1.
The parts that affect the build:

| Part | Qty | Note |
|---|---|---|
| SunnySky V2806 KV400 | 5 | four lift motors and the pusher |
| 12x4.5 carbon props, normal + reverse pairs | 2 pairs | plus spares |
| APC 12x8E + SunnySky pusher prop adapter | 1 | pusher; fixed prop, not folding |
| AM32 ESC, 6S (45 A selected; 20 A is enough) | 5 | one per motor |
| 6S1P 21700 Li-ion pack (Molicel P50B, 5 Ah), XT60 | 1 | about 450 g; a second pack is worth having |
| Holybro Kakute H743-Wing, Micro M10 GPS + compass, DroneCAN DLVR airspeed sensor + pitot, DBR4 receiver, db120 Remote ID | 1 each | avionics |
| EMAX ES08MD II servo | 3 | two ailerons, one elevator |
| Carbon tube 20x18 roll-wrapped, 500 mm | 1 | main spar, used uncut |
| Carbon tube 25x23 roll-wrapped, 1000 mm | 2 | booms, cut to 840 mm |
| Carbon tube 10x8 roll-wrapped, 500 mm | 2 | tip spars, used uncut |
| Carbon tube 8x6 pultruded, 1000 mm | 1 | tail spar, cut to 600 mm |
| Carbon rod 4 mm pultruded, 1000 mm | 1 | elevator joiner, cut to about 550 mm |
| Insta360 GO 3S | 1 | camera |

All the carbon comes from carbonkevlarsupply.com; the exact listings and prices are in
[cots-selection.md](cots-selection.md) §9.1. Buy the plain carbon tubes, not the
"Carbon Fiber Kevlar" hybrids.

### 2.2 Hardware and consumables

| Item | Use |
|---|---|
| M4 heat-set inserts × 4, M4 screws × 4 (about 45 mm, check on the parts) | wing to pod |
| M3 screws and nuts | motor mount pinch bolts (2 per mount), lift motors (4 each), pusher motor (4), camera cradle (2) |
| Zip ties or straps, 5 mm wide | boom saddle lands |
| Pushrods, clevises, control horns | **builder's choice**, 3 control surfaces |
| Hinge tape | ailerons and elevators |
| Epoxy (30 min) | carbon to printed parts, saddles to the wing |
| Medium CA glue and activator | LW-PLA to LW-PLA joints |
| Silicone wire: 14 AWG battery leads, 18–20 AWG ESC power, servo extensions | wiring |
| TPU for skid shoes and front feet | printed or cut; not in the CAD |

### 2.3 Tools
Soldering iron with a heat-set insert tip, hex drivers, fine saw or rotary tool with a
diamond disc for carbon (wear a mask and wet-cut), sanding block, scale reading to 1 g,
tape measure, a balance stand or two rounded supports for the CG check.

---

## 3. Printing

Printer: QIDI Max 4, 0.4 mm nozzle, 0.2 mm layers. `make build` writes every part to
`build/` as STL and STEP, already in print orientation and resting on the bed.

### 3.1 Print profiles

| Part group | Material | Wall | Infill | Notes |
|---|---|---|---|---|
| Wing segments, ailerons, stab halves, elevators | LW-PLA | 0.5 mm (one perimeter) | 2–3% gyroid | the STL is a solid; the slicer turns it into a thin shell |
| Fins | LW-PLA | 0.8 mm | 5% | |
| Pod nose, pod rear, battery hatch | LW-PLA | 0.9 mm (two perimeters) | the wall is already modelled; print solid | |
| Pod collar | PETG | 1.2 mm | solid | |
| Boom saddles | PA-CF | 1.2 mm | 15% | dry the filament; hardened nozzle |
| Motor mounts | PA-CF | 1.6 mm | 25% | dry the filament; hardened nozzle |
| Camera cradle | TPU 95A | 1.2 mm | 30% | |
| Fit coupon | PETG | 1.2 mm | 20% | |

These are the profiles the mass estimate assumes (`scripts/build_all.py`). If you change
one, change it there too so the analysis follows.

### 3.2 Part list

Sizes are in print orientation (X × Y × Z, mm). Masses are CAD estimates.

| Part | Qty | Size | Mass each | Orientation |
|---|---|---|---|---|
| `wing_root_L/R` | 2 | 240 × 24 × 290 | 75 g | standing on the root rib, span vertical |
| `wing_mid_L/R` | 2 | 240 × 24 × 180 | 38 g | span vertical |
| `wing_tip_L/R` | 2 | 174 × 21 × 180 | 28 g | span vertical |
| `aileron_L/R` | 2 | 85 × 258 × 12 | 11 g | flat |
| `fuselage_nose` | 1 | 90 × 95 × 265 | 49 g | standing on the split face, nose up |
| `fuselage_rear` | 1 | 87 × 95 × 265 | 49 g | standing on the split face, tail up |
| `fuselage_collar` | 1 | 20 × 93 × 88 | 12 g | flat |
| `battery_hatch` | 1 | 184 × 78 × 20 | 13 g | flat |
| `camera_cradle` | 1 | 60 × 32 × 28 | 19 g | flat |
| `boom_saddle_L/R` | 2 | 220 × 32 × 49 | 51 g | as exported |
| `motor_mount_front_L/R` | 2 | 38 × 37 × 230 | 47 g | as exported (includes the landing leg) |
| `motor_mount_rear_L/R` | 2 | 37 × 37 × 54 | 24 g | as exported |
| `fin_L/R` | 2 | 120 × 228 × 30 | 39 g | on its side; print the sleeve and root solid (see section 7) |
| `hstab_L/R` | 2 | 77 × 273 × 11 | 23 g | flat |
| `elevator_L/R` | 2 | 42 × 269 × 8 | 11 g | flat |

Total printed mass is about 0.84 kg.

**Nothing is close to the bed limits.** The tallest parts are the wing root segments
(290 mm) and the pod halves (265 mm), against a 335 mm limit.

### 3.3 After each print
- **Weigh the part** and write the mass down next to the CAD estimate. Put the measured
  masses into `analysis/results/cad_mass.json` and rerun `make analysis-fast`.
- Test-fit the carbon tube in each bore before gluing anything. Ream or sand a tight
  bore; don't force a tube into a thin LW-PLA shell.
- Tall single-wall prints (wing segments, pod halves) are fragile until assembled.
  Handle them by the ends.

---

## 4. Carbon tubes

| Tube | Cut length | Note |
|---|---|---|
| 20x18 spar | none: 500 mm as delivered | one piece, centred on the aircraft centreline |
| 25x23 boom × 2 | 840 mm | check both are the same length within 1 mm |
| 10x8 tip spar × 2 | none: 500 mm as delivered | |
| 8x6 pultruded tail spar | 600 mm | |
| 4 mm rod | about 550 mm | elevator joiner |

Four cuts are needed. Wrap the cut line in masking tape, cut wet, and seal the cut
ends with thin CA.

**Check the tubes before using them.** The supplier publishes no material data, so:
- Weigh each tube: the 500 mm 20x18 should be about 46 g, each 1000 mm 25x23 about 117 g
  and each 10x8 about 22 g. A tube more than 10% light has a thinner wall or more resin
  than assumed.
- Measure the outside diameter and the wall with calipers. Put the real diameters into
  the fit-coupon check and `printer.py` clearances.

**Tip-spar sleeves.** Each 10 mm tip spar runs 120 mm inside the 18 mm bore of the main
spar. Make sleeves with a 10 mm bore and 18 mm outside (one 120 mm piece, or two 20 mm
rings at the ends of the overlap) to centre it.
This part is not in the CAD: print it in PETG.

---

## 5. Wing

The wing is one piece, 1.30 m span, built on the spars. Work on a flat table at least
1.5 m long.

Where the tubes and joints are, measured from the aircraft centreline on each side:

| Item | Position |
|---|---|
| Main spar (20x18) | centreline to 250 mm |
| Tip spar (10x8) | 130 mm to 630 mm; its first 120 mm is inside the main spar |
| Root-to-mid segment joint (also the boom station) | 290 mm |
| Mid-to-tip segment joint | 470 mm |
| Aileron servo pocket | 392 mm, lower surface of the mid segment |
| Wing tip | 650 mm |

**The main spar stops 40 mm short of the first joint.** Both segment joints are carried by
the 10 mm tip spar (and the first one also by the boom saddle), so the tip spar must be
bonded along its whole length.

1. **Install the aileron servos first.** Each `wing_mid` segment has a servo pocket in
   its lower surface, 392 mm from the centreline. **The servo lies on its side** (the wing
   is about 17 mm deep here): the pocket is 24 × 22 mm and 12.5 mm deep. Fit the servo and
   run its lead inboard through the channel. The channel ends at the inboard face of the
   mid segment. Getting the lead from there to the pod is **builder's choice**: the
   simplest route is along the lower surface under tape to the root.
2. **Dry-fit everything** before any glue: the main spar through both root segments, a
   sleeved tip spar pushed 120 mm into each end of the main spar, then the mid and tip
   segments over the tip spars. Check that the segment faces close up and the trailing
   edges line up.
3. **Glue the two root segments** to each other at the centreline and to the main spar,
   with epoxy in the bore. Keep the lower surfaces flat on the table while it cures, so
   the wing has no twist.
4. **Fit the tip spars.** Glue the sleeve onto the inboard 120 mm of each 10 mm tube.
   Slide the tube into the outboard face of the root segment until it seats 120 mm inside
   the main spar, with epoxy on the sleeve and in the 40 mm of root-segment bore outboard
   of the main spar.
5. **Add the mid segments, then the tip segments**, one joint at a time: CA on the mating
   faces, epoxy along the whole tip-spar bore. The tube ends 20 mm inside the wing tip.
6. **Check the washout.** The tips should be twisted 2° nose-down relative to the root.
   This is printed into the segments; confirm no joint has rotated.
7. **Hinge the ailerons** with hinge tape along the top surface. The CAD leaves a 1 mm
   gap. Fit the horn and pushrod (**builder's choice**) and check for free travel of at
   least ±20°.
8. **Hand-load the wing** before going further: support it at the root and press down at
   each tip with about 1 kg. The joints at 290 mm and 470 mm should not open.

---

## 6. Booms, motor mounts and saddles

Reference dimensions, measured from the wing-root leading edge (LE):

| Item | Position |
|---|---|
| Boom centrelines | 290 mm left and right of the aircraft centreline |
| Boom front end | 231 mm ahead of the LE |
| Boom rear end | 609 mm behind the LE |
| Front motor axis | 217.4 mm ahead of the LE |
| Rear motor axis | 407.4 mm behind the LE (167.4 mm behind the trailing edge) |
| Boom centreline height | 34 mm below the wing chord line |

1. **Slide the saddle onto the boom.** Each `boom_saddle` has three lands with a bore
   for the boom. Position it so the saddle spans the wing chord, from 8 mm behind the LE
   to 12 mm ahead of the trailing edge.
2. **Bond the saddles to the wing's lower skin** with epoxy, at 290 mm from the
   centreline on each side, across the joint between the root and mid segments. Use a square and a tape measure: **the two booms must be
   parallel to each other and to the aircraft centreline**, and level with each other.
   Sight along them from the tail before the epoxy cures.
3. **Lock the boom in the saddle.** Epoxy the boom into the lands and add a strap
   through the slot above the boom at each land. Set the fore-aft position from the
   table above before it cures.
4. **Fit the rear motor mounts**: slide each onto its boom from the rear, to 407.4 mm
   behind the LE, motor pad up and level. Tighten the two M3 pinch bolts.
5. **Fit the front motor mounts**: these carry the front landing legs and cap the boom
   end. Slide each on until the boom seats against the end cap, leg pointing straight
   down, and tighten the pinch bolts.
6. **Check all four motor pads are level and in one plane.** A tilted pad gives a
   permanent yaw trim in hover. **Check the front and rear motor positions too:** they set
   how the weight is shared between the motors, and the design relies on an equal share.
7. **Mount the lift motors** with 4 × M3 screws each and thread-lock. Check the screws
   don't touch the windings.
8. **Mount the lift ESCs** on the booms about 80 mm inboard of each motor
   (**builder's choice**: zip ties over heat-shrink works). Keep them in the prop wash for
   cooling.

Don't fit the props yet.

---

## 7. Tail

1. **Tap-test the booms now**, before the tail goes on (section 11, step 5). It is much
   easier to change a boom at this stage.
2. **Slide a fin onto each boom's rear end.** Each fin has one sleeve, 85 mm deep, that
   pushes over the boom until the boom seats against the end of the bore. The fin's
   leading edge then sits 524 mm behind the wing LE and the fin hangs straight down.
   The stab-spar socket sits over the last few millimetres of the boom, and about 35 mm
   of the fin root is **behind** the boom end. Don't glue yet.
   - **The fin root is structure**: it carries the stabiliser and the rear landing
     loads. Print the sleeve and the root solid (a slicer modifier over the top 40 mm of
     the fin), and use PETG if a test fin in LW-PLA flexes at the sleeve.
3. **Assemble the stabiliser.** Slide both `hstab` halves onto the 0.60 m tail spar, and
   push the spar ends into the sockets on the inboard side of each fin.
4. **Square it up.** The stabiliser should be level with the wing and the fins vertical.
   Then epoxy the fins to the booms and the spar into the fin sockets, and CA the two
   stab halves together at the centreline.
5. **Elevators.** Glue the 4 mm carbon rod into the bore of both elevator halves so they
   move as one. Hinge them to the stabiliser with tape along the top surface.
6. **Elevator servo.** The mass model places it on the left boom just ahead of the tail,
   but there is no printed mount. **Builder's choice**: strap it to the boom on a small
   printed cradle, with a short pushrod to a horn on the elevator.
7. **Skid shoes.** Before this, load-test one fin: with the tail assembled, press down on
   the boom above the fin until a scale under the skid reads about 1.5 kg (three times its
   static load). Nothing should crack or shift. Then glue a TPU shoe under each fin tip pad and under each front leg foot.

---

## 8. Fuselage pod

1. **Set the heat-set inserts** before joining the halves: four M4 inserts into the
   bosses under the wing saddle. The bosses are 30 mm either side of the centreline, at
   25 mm and 96 mm behind the LE. Go slowly: the pod is LW-PLA and softens quickly.
2. **Join the halves.** Glue the PETG collar 10 mm into the nose half, then glue the
   rear half over it. Keep the saddle rails in line.
3. **Mount the pusher motor** (the fifth V2806) on the rear firewall with four M3 screws
   and thread-lock, wires fed in through the centre hole. Fit SunnySky's pusher prop
   adapter and the APC 12x8E. Fit the pusher ESC inside the tail cone, next to
   the cooling slot in the pod floor.
4. **Camera cradle.** Glue and screw (2 × M3) the TPU cradle under the nose. The camera
   slides in from the front; the window underneath reaches the button and SD card.
5. **Battery hatch.** The hatch drops into the floor opening and sits on its two lip
   strips. The CAD has no latch. **Builder's choice**: tape for the first flights, or
   two small magnets at each end.
6. **Battery tray.** The pack slides fore and aft on the pod floor to set the CG. Line
   the floor with hook-and-loop and add a strap, so the pack can't move in flight.

---

## 9. Final assembly

1. **Bolt the wing to the pod** with four M4 screws through the root segments into the
   pod inserts. Tighten gently; the screws clamp a printed shell.
2. **Check the pusher prop** swings clear of the wing trailing edge, the rear lift props
   and the ground. The design gives 37 mm of ground clearance and 20 mm between the pusher
   prop tip and the rear lift-prop disks seen from above. Turn all three props by hand
   through a full turn to confirm it.

### 9.1 Avionics placement
The balance calculation assumes these positions (x measured from the wing LE, positive
forward). Keep to them where you can; if you move something heavy, update
`analysis/mass.py` and rerun.

| Item | Position |
|---|---|
| Flight controller | in the pod, 30 mm behind the LE, arrow forward |
| GPS + compass | on a 60 mm mast on the nose top, 120 mm ahead of the LE, away from power wiring |
| Remote ID module | in the nose, 80 mm ahead of the LE (beside or above the battery; the pod is tight here) |
| Airspeed sensor and pitot | at the nose, pitot clear of the front prop wash |
| Receiver | in the pod, 150 mm behind the LE, antennas clear of carbon |
| Battery | centre about 92 mm ahead of the LE (final position from the CG check) |

### 9.2 Wiring outline
The electrical design is not part of the analysis. This is the outline it assumes:

- Battery (XT60) → flight controller's current sensor → power distribution to five ESCs.
- Lift ESC power runs out along the wing and the booms. Twist the pairs and keep them
  away from the GPS and compass.
- Signal: DShot from the flight controller to each ESC (bidirectional DShot for RPM
  telemetry, which the harmonic notch filter uses).
- Three servos on the flight controller's servo rail.
- Receiver on one UART (CRSF), GPS and compass on another UART plus I²C, airspeed on I²C.

Peak current with all five motors at full throttle is about 45 A. Size the battery
leads and the main joint for that. Keep the wiring light: every gram counts at this size.

---

## 10. Weigh and balance

1. **Weigh the finished aircraft**, ready to fly, with the battery and camera fitted.
   - Expected: **2.34 kg (5.17 lb)**.
   - **Limit: 2.39 kg.** Above that the lift motors no longer have the 1.8 thrust-to-weight
     margin (PERF-5). If it weighs more, take weight out or rerun the analysis with the
     measured masses before flying; don't fit a bigger battery.
2. **Check the balance point.** Support the aircraft under the wing at the balance
   point, measured back from the wing-root LE:
   - **Target: 82–95 mm behind the LE** (34.1–39.7% of the root chord).
   - **Never fly with it further aft than 95 mm.**
   - Slide the battery to set it. For the first flights, put the battery well forward
     (balance point between 82 and 88 mm).
   - At 95 mm the four lift motors share the weight equally. Further forward, the front
     pair carries more: 1.6% of the weight for every 10 mm.
3. **Mark the battery position** inside the pod once it balances.
4. **Check lateral balance**: it should not drop a wing when supported on the centreline.

---

## 11. Checks before the first hover

Props off for steps 1–5.

1. **Flight controller setup**: ArduPilot QuadPlane, quad-X lift frame plus pusher. Start
   from the settings in [AerodynamicsReport.md](AerodynamicsReport.md) §7.4.
2. **Motor order and direction**: test each motor alone and confirm it matches
   ArduPilot's quad-X numbering and rotation. Then fit each prop to match its direction.
3. **Control surfaces**: correct sense in MANUAL and in FBWA (stabilising direction).
4. **Failsafes**: radio-loss and low-battery failsafes set and tested (SYS-7).
5. **Boom tap test** (open item C-5): tap each boom tip with the motor fitted and record
   it with a phone accelerometer. The first bending mode should be **above 113 Hz**
   (predicted 155–176 Hz). If it is lower, don't hover until the notch filter is set up
   and the cause is understood.
6. **Fit the props**, tether or restrain the aircraft, and run each lift motor to about
   50% to check for vibration.
7. **Regulatory**: FAA registration number on the outside, Remote ID module on and
   broadcasting (REG-1, REG-2).
8. **First hover**: calm air, battery fully forward, a short flight. Then review the log
   for hover throttle (about 50% expected), the front/rear motor split (about 50/50, or up
   to 52/48 with the battery forward), the battery current (about 15 A) and the vibration
   spectrum, and set the harmonic notch (near 81 Hz). Plan on 12–13 min of hover per pack.

---

## 12. Open build questions

These are gaps in the design, not in this document. Each needs a decision or a CAD
addition before or during the build.

| # | Gap | Suggested resolution |
|---|---|---|
| B-1 | No elevator servo mount in the CAD | small printed cradle strapped to the left boom |
| B-2 | No control horns or pushrod exits | bought horns glued into the surfaces |
| B-3 | Aileron servo lead has no channel inboard of the mid segment | surface run under tape, or add a channel to `wing_root` |
| B-4 | No battery hatch latch | magnets or tape |
| B-5 | Tip-spar centring sleeve not modelled | print or turn (section 4) |
| B-6 | No ESC mounts, GPS mast or pitot mount | strap-on mounts; add to the CAD once positions are proven |
| B-7 | TPU skid shoes and front feet not modelled | cut from TPU sheet or print simple pads |
| B-8 | Front legs, clamp rings, wing bolts and the 0.9 mm pod wall not strength-checked (report R-11) | hand-check, and drop-test the pod with the battery in before the first flight |
| B-10 | Prop hub and pusher adapter fit on the V2806 not confirmed (COTS C-9) | check on the first motor, before ordering the rest |
| B-9 | Glue types are recommendations, not tested on LW-PLA from this printer | test a lap joint on scrap first |
