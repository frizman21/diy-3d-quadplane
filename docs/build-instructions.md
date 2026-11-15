# QP-1 manufacturing and build instructions

Status: **Draft for review**, 2026-11-15, for the 10 lb design with supplier-catalogue carbon (report revision C)
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

1. **Measure the Suburban.** The aircraft is 1.327 m long and 1.80 m in span. It needs
   about 1.4 m of cargo width above the wheel wells (SIZE-2, open item C-8). If the space
   isn't there, stop and revisit the design.
2. **Print the fit coupon** (`build/fit_coupon.stl`, PETG). It has six tube holes and six
   heat-set insert holes in graded sizes. Find the hole that gives a slip fit on a carbon
   tube and the one that takes an M3 insert cleanly, then update the clearances in
   `quadplane/printer.py`.
3. **Print and weigh an LW-PLA density coupon.** The mass estimate assumes a foamed
   density of 0.75 g/cm³ (about 230 °C nozzle temperature). Print a simple block with the
   wing profile below, weigh it, and update `printer.LWPLA`. The printed airframe is 30%
   of the take-off mass, so this number matters.
4. **Receive and measure the bought parts**, then update `quadplane/hardware.py`:
   - lift motor bolt pattern (assumed 4 × M3 on a 25 mm circle) and body size;
   - pusher motor bolt pattern (assumed 25 mm cross), body size and mass;
   - battery pack size (assumed 140 × 68 × 75 mm) and mass;
   - camera size.
5. **Bench-test the pusher** static thrust with the 12x8 folding prop. It needs 2.2 kg
   (open item C-1).
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
| T-Motor MN4014 KV400 | 4 | lift motors |
| T-Motor P15x5 carbon props | 2 CW + 2 CCW | plus spares |
| SunnySky X3520 520KV + 12x8 folding prop, hub and spinner | 1 | pusher |
| AM32 ESC, 40–45 A, 6S | 5 | one per motor |
| 6S3P 21700 Li-ion pack, XT90 | 1 | about 1.29 kg |
| Holybro Kakute H743-Wing, Micro M10 GPS + compass, DroneCAN DLVR airspeed sensor + pitot, DBR4 receiver, db120 Remote ID | 1 each | avionics |
| EMAX ES08MD II servo | 3 | two ailerons, one elevator |
| Carbon tube 20x18 roll-wrapped, 1000 mm | 1 | main spar, used uncut |
| Carbon tube 25x23 roll-wrapped, 1000 mm | 2 | booms, used uncut |
| Carbon tube 14x12 roll-wrapped, 500 mm | 2 | tip spars, used uncut |
| Carbon tube 8x6 pultruded, 1000 mm | 1 | tail spar, cut to 620 mm |
| Carbon rod 4 mm pultruded, 1000 mm | 1 | elevator joiner, cut to about 570 mm |
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
| Silicone wire: 12 AWG battery leads, 16–18 AWG ESC power, servo extensions | wiring |
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
| Pod nose, pod rear, battery hatch | LW-PLA | 1.2 mm | the wall is already modelled; print solid | |
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
| `wing_root_L/R` | 2 | 340 × 34 × 300 | 117 g | standing on the root rib, span vertical |
| `wing_mid_L/R` | 2 | 340 × 34 × 300 | 106 g | span vertical |
| `wing_tip_L/R` | 2 | 241 × 29 × 300 | 67 g | span vertical |
| `aileron_L/R` | 2 | 111 × 358 × 15 | 22 g | flat |
| `fuselage_nose` | 1 | 120 × 115 × 335 | 107 g | standing on the split face, nose up |
| `fuselage_rear` | 1 | 116 × 116 × 335 | 97 g | standing on the split face, tail up |
| `fuselage_collar` | 1 | 20 × 112 × 117 | 16 g | flat |
| `battery_hatch` | 1 | 245 × 78 × 20 | 20 g | flat |
| `camera_cradle` | 1 | 60 × 32 × 28 | 19 g | flat |
| `boom_saddle_L/R` | 2 | 320 × 32 × 48 | 58 g | as exported |
| `motor_mount_front_L/R` | 2 | 47 × 47 × 250 | 53 g | as exported (includes the landing leg) |
| `motor_mount_rear_L/R` | 2 | 47 × 47 × 54 | 27 g | as exported |
| `fin_L/R` | 2 | 140 × 248 × 30 | 49 g | on its side; print the sleeve and root solid (see section 7) |
| `hstab_L/R` | 2 | 116 × 283 × 16 | 39 g | flat |
| `elevator_L/R` | 2 | 63 × 279 × 11 | 18 g | flat |

Total printed mass is about 1.37 kg.

**Close to the bed limits:** the pod halves are 335 mm tall (limit 340 mm), the ailerons
358 mm long and the wing segments 340 mm in chord (limit 380 mm). Check the slicer's
real printable volume before starting these.

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
| 20x18 spar | none: 1000 mm as delivered | one piece, centred on the aircraft centreline |
| 25x23 boom × 2 | none: 1000 mm as delivered | check both are the same length within 1 mm; trim the longer one if not |
| 14x12 tip spar × 2 | none: 500 mm as delivered | |
| 8x6 pultruded tail spar | 620 mm | |
| 4 mm rod | about 570 mm | elevator joiner |

Only two cuts are needed. Wrap the cut line in masking tape, cut wet, and seal the cut
ends with thin CA.

**Check the tubes before using them.** The supplier publishes no material data, so:
- Weigh each tube: the 20x18 should be about 93 g and each 25x23 about 117 g. A tube
  more than 10% light has a thinner wall or more resin than assumed.
- Measure the outside diameter and the wall with calipers. Put the real diameters into
  the fit-coupon check and `printer.py` clearances.
- Bend-test the spar: support it 0.90 m apart and hang 10 kg from the middle. It should
  deflect 6–8 mm and spring back fully. More than 8 mm means it is softer than the
  analysis assumes; don't use it.

**Tip-spar sleeves.** Each 14 mm tip spar runs 120 mm inside the 18 mm bore of the main
spar. Make sleeves with a 14 mm bore and 18 mm outside (one 120 mm piece, or two 20 mm
rings at the ends of the overlap) to centre it.
This part is not in the CAD: print it in PETG.

---

## 5. Wing

The wing is one piece, 1.80 m span, built on the spar. Work on a flat table at least 2 m
long.

1. **Install the aileron servos first.** Each `wing_mid` segment has a servo pocket in
   its lower surface, 530 mm from the centreline. Fit the servo and run its lead inboard
   through the channel. The channel ends at the inboard face of the mid segment.
   Getting the lead from there to the pod is **builder's choice**: the simplest route is
   along the lower surface under tape to the root.
2. **Dry-fit everything on the spar** before any glue: root, mid and tip segments for
   both sides. The spar runs from 500 mm left to 500 mm right, so it ends inside
   each mid segment, 100 mm short of the tip segment. Check that the segment faces close up and the trailing edges line up.
3. **Glue the two root segments** to each other at the centreline and to the spar, with
   epoxy in the bore. Keep the lower surfaces flat on the table while it cures, so the
   wing has no twist.
4. **Add the mid segments**, one joint at a time. CA on the mating faces, epoxy in the
   spar bore. Leave the tip segments off until step 5.
5. **Fit the tip spars before gluing the tip segments on.** Glue the sleeve onto the
   inboard 120 mm of each 14 mm tube. Slide the tube into the mid segment until it seats
   120 mm inside the main spar, and epoxy it there and along the mid segment bore. The
   tube runs from 380 mm to 880 mm from the centreline. Then slide the tip segment over
   the tube with epoxy along the whole bore: **this tube is the only structure across the
   mid-to-tip joint**, so bond its full length.
6. **Check the washout.** The tips should be twisted 2° nose-down relative to the root.
   This is printed into the segments; confirm no joint has rotated.
7. **Hinge the ailerons** with hinge tape along the top surface. The CAD leaves a 1 mm
   gap. Fit the horn and pushrod (**builder's choice**) and check for free travel of at
   least ±20°.

---

## 6. Booms, motor mounts and saddles

Reference dimensions, measured from the wing-root leading edge (LE):

| Item | Position |
|---|---|
| Boom centrelines | 300 mm left and right of the aircraft centreline |
| Boom front end | 219 mm ahead of the LE |
| Boom rear end | 781 mm behind the LE |
| Front motor axis | 205.5 mm ahead of the LE |
| Rear motor axis | 545.5 mm behind the LE (205.5 mm behind the trailing edge) |
| Boom centreline height | 34 mm below the wing chord line |

1. **Slide the saddle onto the boom.** Each `boom_saddle` has three lands with a bore
   for the boom. Position it so the saddle spans the wing chord, from 8 mm behind the LE
   to 12 mm ahead of the trailing edge.
2. **Bond the saddles to the wing's lower skin** with epoxy, at 300 mm from the
   centreline on each side. Use a square and a tape measure: **the two booms must be
   parallel to each other and to the aircraft centreline**, and level with each other.
   Sight along them from the tail before the epoxy cures.
3. **Lock the boom in the saddle.** Epoxy the boom into the lands and add a strap
   through the slot above the boom at each land. Set the fore-aft position from the
   table above before it cures.
4. **Fit the rear motor mounts**: slide each onto its boom from the rear, to 545.5 mm
   behind the LE, motor pad up and level. Tighten the two M3 pinch bolts.
5. **Fit the front motor mounts**: these carry the front landing legs and cap the boom
   end. Slide each on until the boom seats against the end cap, leg pointing straight
   down, and tighten the pinch bolts.
6. **Check all four motor pads are level and in one plane.** A tilted pad gives a
   permanent yaw trim in hover.
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
   leading edge then sits 696 mm behind the wing LE and the fin hangs straight down.
   About 55 mm of the fin root, including the stab-spar socket, sits **behind** the boom
   end. Don't glue yet.
   - **The fin root is structure**: it carries the stabiliser and the rear landing
     loads. Print the sleeve and the root solid (a slicer modifier over the top 40 mm of
     the fin), and use PETG if a test fin in LW-PLA flexes at the sleeve.
3. **Assemble the stabiliser.** Slide both `hstab` halves onto the 0.62 m tail spar, and
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
   the boom above the fin until a scale under the skid reads about 3 kg (three times its
   static load). Nothing should crack or shift. Then glue a TPU shoe under each fin tip pad and under each front leg foot.

---

## 8. Fuselage pod

1. **Set the heat-set inserts** before joining the halves: four M4 inserts into the
   bosses under the wing saddle. The bosses are 30 mm either side of the centreline, at
   25 mm and 136 mm behind the LE. Go slowly: the pod is LW-PLA and softens quickly.
2. **Join the halves.** Glue the PETG collar 10 mm into the nose half, then glue the
   rear half over it. Keep the saddle rails in line.
3. **Mount the pusher motor** on the rear firewall with four M3 screws and thread-lock,
   wires fed in through the centre hole. Fit the pusher ESC inside the tail cone, next to
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
   and the ground (47 mm ground clearance with a 12 in prop).

### 9.1 Avionics placement
The balance calculation assumes these positions (x measured from the wing LE, positive
forward). Keep to them where you can; if you move something heavy, update
`analysis/mass.py` and rerun.

| Item | Position |
|---|---|
| Flight controller | in the pod, 30 mm behind the LE, arrow forward |
| GPS + compass | on a 60 mm mast on the nose top, 170 mm ahead of the LE, away from power wiring |
| Remote ID module | in the nose, 130 mm ahead of the LE |
| Airspeed sensor and pitot | at the nose, pitot clear of the front prop wash |
| Receiver | in the pod, 150 mm behind the LE, antennas clear of carbon |
| Battery | centre about 129 mm ahead of the LE (final position from the CG check) |

### 9.2 Wiring outline
The electrical design is not part of the analysis. This is the outline it assumes:

- Battery (XT90) → flight controller's current sensor → power distribution to five ESCs.
- Lift ESC power runs out along the wing and the booms. Twist the pairs and keep them
  away from the GPS and compass.
- Signal: DShot from the flight controller to each ESC (bidirectional DShot for RPM
  telemetry, which the harmonic notch filter uses).
- Three servos on the flight controller's servo rail.
- Receiver on one UART (CRSF), GPS and compass on another UART plus I²C, airspeed on I²C.

Peak current with all five motors at full throttle is about 103 A. Size the battery
leads and the main joint for that.

---

## 10. Weigh and balance

1. **Weigh the finished aircraft**, ready to fly, with the battery and camera fitted.
   - Expected: **4.59 kg (10.12 lb)**.
   - The structure and the hover margin are designed for **4.8 kg**. If it weighs more,
     rerun the analysis with the measured masses before flying.
2. **Check the balance point.** Support the aircraft under the wing at the balance
   point, measured back from the wing-root LE:
   - **Target: 93–107 mm behind the LE** (27.2–31.4% of the root chord).
   - **Never fly with it further aft than 107 mm.**
   - Slide the battery to set it. For the first flights, put the battery fully forward
     (balance point between 93 and 100 mm).
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
   it with a phone accelerometer. The first bending mode should be **above 111 Hz**
   (predicted 114–130 Hz). If it is lower, don't hover until the notch filter is set up
   and the cause is understood.
6. **Fit the props**, tether or restrain the aircraft, and run each lift motor to about
   50% to check for vibration.
7. **Regulatory**: FAA registration number on the outside, Remote ID module on and
   broadcasting (REG-1, REG-2).
8. **First hover**: calm air, battery fully forward, a short flight. Then review the log
   for hover throttle (about 50% expected), the front/rear motor split (about 58/42) and
   the vibration spectrum, and set the harmonic notch (near 73 Hz).

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
| B-8 | Front legs, clamp rings and wing bolts not strength-checked at 4.8 kg (report R-11) | hand-check, and drop-test a front leg before the first flight |
| B-9 | Glue types are recommendations, not tested on LW-PLA from this printer | test a lap joint on scrap first |
