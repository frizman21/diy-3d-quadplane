# Requirements: Quadplane v1 (proof of concept)

Status: **Draft**, 2026-11-07
Owner: Mike

Each requirement has an ID so the design and tests can refer to it. **Source** says
where it came from: **Stated** means the owner said it directly; **Derived** means it
follows from a stated requirement, with the reasoning given. Items marked **VERIFY**
need a measurement or a check before the design is fixed.

---

## 1. Purpose and scope

v1 is a **proof of concept**. It should show that a 3D-printed VTOL quadplane can be
designed, built, tuned and flown, including the transition from hover to wingborne
flight and back. When a design choice is close, choose the simpler one.

Out of scope for v1: long range, autonomy beyond standard ArduPilot features, retractable
landing gear, folding or detachable wings, and payloads other than the camera.

## 2. Mission and performance

| ID | Requirement | Source |
|---|---|---|
| PERF-1 | Hover endurance of **at least 15 min** on one battery, at full takeoff weight with the camera fitted, landing with **at least 20% capacity left**. | Stated (hover time for tuning); the 20% reserve is Derived (standard practice to protect the battery) |
| PERF-2 | Vertical takeoff and landing. No runway or hand launch needed. | Stated (quadplane) |
| PERF-3 | Transition from hover to wingborne cruise and back. | Stated (proof-of-concept goal) |
| PERF-4 | Wingborne endurance is whatever the design gives, not a design target. Report it after test flights. Expected to be several times the hover endurance. | Stated |
| PERF-5 | Hover thrust-to-weight ratio of **at least 1.8** (all four lift motors at full throttle vs. takeoff weight), for control margin in gusts and during tuning. | Derived |
| PERF-6 | Hover must stay controllable with no more than ~70% throttle at full takeoff weight. | Derived (from PERF-5) |

## 3. Payload

| ID | Requirement | Source |
|---|---|---|
| PAY-1 | Carries one GoPro-class camera (about 125–160 g including mount) that records the flight. | Stated |
| PAY-2 | The camera faces forward with an unobstructed view: no props or landing gear in the frame during cruise. | Derived |
| PAY-3 | The camera can be removed, and its record button and SD card reached without tools. | Derived (recording every flight) |
| PAY-4 | The camera mount is protected from ground contact during landing, including a tip-over. | Derived |
| PAY-5 | The camera's weight is included in balance (centre of gravity) planning. It shifts the balance point, so the battery position must be adjustable to compensate. | Derived |

## 4. Size and transport

| ID | Requirement | Source |
|---|---|---|
| SIZE-1 | The assembled aircraft fits through a standard **80 in × 36 in (2032 × 914 mm)** doorway, carried sideways. This limits the overall wingspan to **1.9 m or less** (about 130 mm of margin for hands and handling). | Stated (doorway); the span limit is Derived |
| SIZE-2 | The assembled aircraft fits in the back of a Chevrolet Suburban with the 2nd and 3rd rows folded down and the tailgate closed. **VERIFY:** measure the usable floor length (tailgate to the back of the front seats), the width between the wheel wells, the width above them, and the height of the tailgate opening. | Stated |
| SIZE-3 | One-piece airframe: no field assembly. Printed sections can be glued together permanently. | Stated (coming apart not required) |
| SIZE-4 | The aircraft can rest on its landing gear or on a simple cradle in the vehicle without loading the props or the camera. | Derived |

## 5. Construction and materials

| ID | Requirement | Source |
|---|---|---|
| BUILD-1 | **Buy off-the-shelf (COTS) parts** whenever they make the aircraft noticeably lighter or stronger than a printed part would. Expected COTS parts: carbon tubes for the wing spar and motor booms, motors, ESCs, props, flight controller, GPS, radio receiver, battery, and possibly carbon landing-gear legs. | Stated |
| BUILD-2 | Printed parts must fit on a QIDI Max 4 bed (390 × 390 × 340 mm, minus a 5 mm margin; **VERIFY**). Anything larger is split into keyed segments. | Stated (printer) |
| BUILD-3 | Available materials: PLA Basic, PETG Basic, plus any others needed (LW-PLA, ASA and PA-CF are planned). | Stated |
| BUILD-4 | Assign materials by job: **LW-PLA** for thin aerodynamic skins; **PETG/ASA** for general structure; **ASA or PA-CF** for motor mounts and parts near heat sources (motors, ESCs, battery). PLA is not used for load-bearing parts near heat. | Derived |
| BUILD-5 | Hardware uses M2/M3 screws into **heat-set inserts** for every part that gets removed or serviced. Sizes come from the fit-coupon print. | Derived |
| BUILD-6 | All CAD is parametric build123d code in this repo, following CLAUDE.md. | Stated (project setup) |

## 6. Systems

| ID | Requirement | Source |
|---|---|---|
| SYS-1 | **Layout:** quadplane with 4 lift motors on two booms running fore and aft, plus 1 pusher motor for cruise. Conventional tail on the booms. | Derived (simplest common layout, well supported by ArduPilot); **open for review** |
| SYS-2 | **Flight software:** ArduPilot QuadPlane (owner has used ArduPilot before). **Flight controller board:** TBD (e.g. a Matek H743 class board). | Stated (ArduPilot); board **open** |
| SYS-3 | GPS with compass, needed for position hold in hover tuning and for return-to-launch. | Derived |
| SYS-4 | Telemetry to a ground station for tuning and log review. Onboard logging enabled. | Derived (tuning goal) |
| SYS-5 | **Battery:** preliminary choice is a **6S Li-ion pack** (e.g. 6S2P 21700, about 190 Wh, about 900 g) to meet PERF-1 with margin; 6S LiPo is the fallback. Final choice after the weight and power estimate. | Derived (see §9) |
| SYS-6 | The battery is reachable through a hatch without tools and can slide fore and aft to set the balance point. | Derived |
| SYS-7 | Arming safety: a safety switch or an equivalent arming procedure, and failsafes configured for loss of radio control link and low battery. | Derived |

## 7. Regulatory (USA, FAA)

| ID | Requirement | Source |
|---|---|---|
| REG-1 | The aircraft is over 250 g, so it **must be registered with the FAA** and show its registration number on the outside. | Derived (FAA rules) |
| REG-2 | **Remote ID:** a standard Remote ID build or a broadcast module, unless it only flies inside a FAA-Recognized Identification Area (FRIA). | Derived (FAA rules) |
| REG-3 | The pilot holds a TRUST certificate (recreational) or a Part 107 certificate, as applicable. | Derived (FAA rules) |

## 8. Verification

| ID | How it's verified |
|---|---|
| PERF-1 | Hover test with a full battery at takeoff weight; flight log shows ≥ 15 min and ≥ 20% left. |
| PERF-5 | Bench thrust test of one motor/prop pair, or the manufacturer's thrust data, × 4 compared with the measured takeoff weight. |
| SIZE-1/2 | The CAD bounding box checked against the limits; then a physical test fit through a doorway and in the Suburban. |
| BUILD-2 | `make test` (bed-fit check on every part). |
| PAY-2 | Camera footage from the first hover and the first cruise. |

## 9. Preliminary sizing (to be refined)

This first estimate checks that PERF-1 is achievable. These numbers become `quadplane/params.py`
once the layout is reviewed.

**Weight estimate**

| Item | g |
|---|---|
| 4 lift motors + 1 pusher | 320 |
| 5 ESCs | 100 |
| Props | 60 |
| Flight controller, GPS, receiver, telemetry, Remote ID | 120 |
| GoPro + mount | 150 |
| Battery, 6S2P 21700 Li-ion | 900 |
| Carbon spar, booms, landing gear | 200 |
| Printed airframe (mostly LW-PLA) | 700 |
| Wiring, connectors, hardware | 200 |
| **Total takeoff weight** | **≈ 2.75 kg** |

**Hover power.** Four 13 in props give 0.34 m² of disk area. Ideal hover power is
about 150 W. After prop losses (figure of merit 0.6) and motor/ESC losses (efficiency 0.8),
real hover power is about **310 W**.

**Energy needed.** 15 min × 310 W ≈ 78 Wh. With the 20% reserve, the battery must hold
at least about 97 Wh. A 6S2P Li-ion pack holds about 190 Wh, so it meets this with a
large margin, which also leaves room for the airframe to come in heavier than estimated.
A 6S1P pack (≈ 97 Wh) has no margin.

**Wing.** At about 2.75 kg and a wing loading of about 55 g/dm², the wing needs about
50 dm² of area, for example a 1.8 m span with a 280 mm mean chord. That fits SIZE-1.

## 10. Open questions

1. Suburban cargo measurements (SIZE-2). Owner to measure.
2. Flight controller board and radio system: anything already owned?
3. Which GoPro model (it sets the mount and the weight)?
4. Confirm the layout (SYS-1) before the CAD starts.
