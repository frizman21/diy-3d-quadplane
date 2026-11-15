# Requirements: Quadplane v1 (proof of concept)

Status: **Draft rev C**, 2026-11-15 (10 lb class, D-025; sizing is in the [Aerodynamics report](AerodynamicsReport.md))
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
| PERF-7 | Takeoff weight of **approximately 10 lb (4.5 kg)**, battery and electronics included. | Stated (rev C, D-025) |

## 3. Payload

| ID | Requirement | Source |
|---|---|---|
| PAY-1 | Carries one lightweight, rugged action camera that records the flight. **Selected: Insta360 GO 3S** (about 39 g, 4K, waterproof to 10 m (IP68), sealed body with no protruding parts; **VERIFY** the weight when it arrives). Allow about 60 g including the mount. | Stated (rugged and lightweight); the model is Derived |
| PAY-1a | The camera mount is a printed **TPU** cradle that absorbs crash shock and frame vibration, and releases the camera rather than breaking it in a crash. | Derived (crash survival) |
| PAY-2 | The camera faces forward with an unobstructed view: no props or landing gear in the frame during cruise. | Derived |
| PAY-3 | The camera can be removed, and its record button and SD card reached without tools. | Derived (recording every flight) |
| PAY-4 | The camera mount is protected from ground contact during landing, including a tip-over. | Derived |
| PAY-5 | The camera's weight is included in balance (centre of gravity) planning. It shifts the balance point, so the battery position must be adjustable to compensate. | Derived |

## 4. Size and transport

| ID | Requirement | Source |
|---|---|---|
| SIZE-1 | The assembled aircraft fits through a standard **80 in × 36 in (2032 × 914 mm)** doorway, carried sideways. This limits the overall wingspan to **1.9 m or less** (about 130 mm of margin for hands and handling). | Stated (doorway); the span limit is Derived |
| SIZE-2 | The assembled aircraft fits in the back of a Chevrolet Suburban with the 2nd and 3rd rows folded down and the tailgate closed. Load it with the wings running lengthwise. Working limits, **estimated** (see note below): overall length (nose to tail) **≤ 1.4 m** (rev C; was 1.2 m), overall height including props and landing gear **≤ 0.9 m**. The span limit is set by SIZE-1. | Stated; the limits are Derived and estimated |
| SIZE-2a | **How the Suburban limits were estimated:** stated cargo volume of 144.7 ft³ (4.1 m³) behind the 1st row, opening at least 39 in (990 mm) tall, exterior width 81 in. That implies a floor about 2.3–2.5 m long and about 1.25 m wide between the wheel wells (≈ 1.6 m above them). A 1.8–1.9 m span fits along the length. Rev B used the conservative 1.2 m width between the wheel wells as the length limit. **Rev C (D-026) raises it to 1.4 m**, because a 10 lb aircraft can't be made shorter than about 1.36 m (Report §4.1). That uses the estimated ≈ 1.6 m above the wheel wells, so the aircraft rides on a cradle that carries the nose or tail over a wheel well (SIZE-4). **This number is not measured. VERIFY with a tape measure before anything is printed.** | Derived (estimate) |
| SIZE-3 | One-piece airframe: no field assembly. Printed sections can be glued together permanently. | Stated (coming apart not required) |
| SIZE-4 | The aircraft can rest on its landing gear or on a simple cradle in the vehicle without loading the props or the camera. | Derived |

## 5. Construction and materials

| ID | Requirement | Source |
|---|---|---|
| BUILD-1 | **Buy off-the-shelf (COTS) parts** whenever they make the aircraft noticeably lighter or stronger than a printed part would. Expected COTS parts: carbon tubes for the wing spar and motor booms, motors, ESCs, props, flight controller, GPS, radio receiver, battery, and possibly carbon landing-gear legs. | Stated |
| BUILD-2 | Printed parts must fit on a QIDI Max 4 bed (390 × 390 × 340 mm, minus a 5 mm margin; **VERIFY**). Anything larger is split into keyed segments. | Stated (printer) |
| BUILD-3 | Available materials: PLA Basic, PETG Basic, plus any others needed (LW-PLA, ASA, PA-CF and TPU are planned). | Stated |
| BUILD-4 | Assign materials by job: **LW-PLA** for thin aerodynamic skins; **PETG/ASA** for general structure; **ASA or PA-CF** for motor mounts and parts near heat sources (motors, ESCs, battery). PLA is not used for load-bearing parts near heat. | Derived |
| BUILD-5 | Hardware uses M2/M3 screws into **heat-set inserts** for every part that gets removed or serviced. Sizes come from the fit-coupon print. | Derived |
| BUILD-6 | All CAD is parametric build123d code in this repo, following CLAUDE.md. | Stated (project setup) |

## 6. Systems

| ID | Requirement | Source |
|---|---|---|
| SYS-1 | **Layout:** quadplane with 4 fixed lift motors (quad X) on two booms running fore and aft, plus 1 pusher motor for cruise. Tail mounted on the booms. | Decided (D-007) |
| SYS-2 | **Flight software:** ArduPilot QuadPlane (owner has used ArduPilot before). **Flight controller:** Matek H7A3-WING (replaces the discontinued H743-WING; D-016). | Stated |
| SYS-3 | GPS with compass, needed for position hold in hover tuning and for return-to-launch. | Derived |
| SYS-4 | Telemetry to a ground station for tuning and log review. Onboard logging enabled. | Derived (tuning goal) |
| SYS-5 | **Battery:** a **6S3P 21700 Li-ion pack** (about 292 Wh, about 1.3 kg; D-028) meets PERF-1 with margin at 10 lb. The 6S2P pack (about 194 Wh, 860 g) is the light configuration. | Derived (Report §5.3) |
| SYS-6 | The battery is reachable through a hatch without tools and can slide fore and aft to set the balance point. | Derived |
| SYS-7 | Arming safety: a safety switch or an equivalent arming procedure, and failsafes configured for loss of radio control link and low battery. | Derived |

## 6a. Radio control link (shared across iterations)

The handset and radio system bought for v1 will be **reused on later aircraft**,
up to about a **150 kg (330 lb)** drone with tilting rotors or wings, lights, flaps and a
pneumatic gimbal (up/down). Choose it for that future aircraft, not for v1.

| ID | Requirement | Source |
|---|---|---|
| RC-1 | One handset and radio system is used for v1 and all later iterations. | Stated |
| RC-2 | **At least 16 RC channels**, plus switches, sliders and knobs for modes, flaps, tilt, lights and the gimbal. | Derived (future function list) |
| RC-3 | **Two-way MAVLink telemetry** over the same link, so the ground station (on the handset or a laptop) shows flight data, logs and parameters. | Derived (tuning, and larger aircraft) |
| RC-4 | **Range of at least 10 km** line of sight, with a link-quality indication and an RC failsafe that ArduPilot recognises. | Derived (over-spec margin) |
| RC-5 | Preferred: a **digital HD video downlink** for the camera or gimbal on the same system. | Derived (gimbal on future aircraft) |
| RC-6 | Supported by ArduPilot without custom firmware. | Derived |
| RC-7 | The air unit (on the aircraft) weighs **150 g or less** so it can fly on v1. | Derived (fits the v1 weight budget) |
| RC-8 | Has a path to a **redundant link** (for example a second receiver or a second band) for the 150 kg aircraft. | Derived (safety at that mass) |
| RC-9 | **Selected:** RadioMaster TX16S MK3 with built-in dual-band ExpressLRS (2.4 GHz + 900 MHz). v1 uses one ELRS receiver connected over CRSF with MAVLink telemetry. A video link is added later. | Decided (D-010) |

## 7. Regulatory (USA, FAA)

| ID | Requirement | Source |
|---|---|---|
| REG-1 | The aircraft is over 250 g, so it **must be registered with the FAA** and show its registration number on the outside. | Derived (FAA rules) |
| REG-2 | **Remote ID:** a standard Remote ID build or a broadcast module, unless it only flies inside a FAA-Recognized Identification Area (FRIA). | Derived (FAA rules) |
| REG-3 | The pilot holds a TRUST certificate (recreational) or a Part 107 certificate, as applicable. | Derived (FAA rules) |
| REG-4 | *Future, not v1:* an aircraft over 55 lb (25 kg) is outside Part 107 and needs FAA approval (for example a 49 U.S.C. 44807 exemption, or flying under a community-based organisation's large-model program). Plan for this before the 150 kg iteration. | Derived (FAA rules) |

## 8. Verification

| ID | How it's verified |
|---|---|
| PERF-1 | Hover test with a full battery at takeoff weight; flight log shows ≥ 15 min and ≥ 20% left. |
| PERF-5 | Bench thrust test of one motor/prop pair, or the manufacturer's thrust data, × 4 compared with the measured takeoff weight. |
| PERF-7 | Weigh the finished aircraft, ready to fly. |
| SIZE-1/2 | The CAD bounding box checked against the limits; then a physical test fit through a doorway and in the Suburban. |
| BUILD-2 | `make test` (bed-fit check on every part). |
| PAY-2 | Camera footage from the first hover and the first cruise. |

## 9. Preliminary sizing (superseded)

> **Superseded** by [AerodynamicsReport.md](AerodynamicsReport.md). The analysed design
> (rev C, 10 lb class) is 4.65 kg / 10.25 lb (PERF-7 ✅), hovers 27.2 min (PERF-1 ✅), has a
> 1.80 m span and 1.357 m length (SIZE-1 ✅; SIZE-2 against the unmeasured 1.4 m limit), and
> a front-motor T/W of 1.87 (PERF-5 ✅). The original 2.75 kg estimate is kept below for
> traceability.

This first estimate checks that PERF-1 is achievable. These numbers become `quadplane/params.py`
once the layout is reviewed.

**Weight estimate**

| Item | g |
|---|---|
| 4 lift motors + 1 pusher | 320 |
| 5 ESCs | 100 |
| Props | 60 |
| Flight controller, GPS, receiver, telemetry, Remote ID | 120 |
| Insta360 GO 3S + TPU mount | 60 |
| Battery, 6S2P 21700 Li-ion | 900 |
| Carbon spar, booms, landing gear | 200 |
| Printed airframe (mostly LW-PLA) | 700 |
| Wiring, connectors, hardware | 200 |
| **Total takeoff weight** | **≈ 2.65 kg** (2.75 kg is used below as margin) |

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

1. **Suburban cargo measurements (SIZE-2).** Using estimates for now. The rev C aircraft (1.357 m long) depends on about 1.4 m of usable width above the wheel wells; measure before printing.
2. ~~Radio~~: decided (D-010).
3. ~~Camera model~~: decided (D-009).
4. ~~Layout~~: decided (D-007).

All decisions are recorded in `docs/decisions.md`.
