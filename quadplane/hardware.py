"""Off-the-shelf hardware dimensions. All units mm. VERIFY against the parts you actually buy."""

# Holes for screws (diameters)
M2_CLEAR = 2.4
M3_CLEAR = 3.4
M3_HEAD_D = 5.8
M3_HEAD_H = 3.0

# Heat-set inserts: hole diameter / depth (M3 x 5.7 "short" type, typical)
M3_INSERT_HOLE = 4.2
M3_INSERT_DEPTH = 6.0

# Carbon tubes stocked by the supplier (docs/cots-selection.md §9): (OD, ID, max length), mm
CARBON_ROLL_WRAPPED = ((8, 6, 500), (10, 8, 500), (14, 12, 500), (20, 18, 1000), (25, 23, 1000))
CARBON_PULTRUDED = ((6, 4, 1000), (8, 6, 1000), (12, 8, 1000), (16, 12, 1000), (20, 16, 1000), (25, 22, 1000))
TAIL_SPAR_OD = 8.0  # 8x6 pultruded
ELEVATOR_ROD_D = 4.0  # solid pultruded rod joining the elevator halves (3 mm is not stocked)

# Motors (VERIFY against the delivered motors before printing mounts)
# Lift motor: SunnySky V2806 KV400 (D-037)
LIFT_MOTOR_BOLT_CIRCLE = 19.0  # 4 x M3 stator mount; VERIFY (not on the product page)
LIFT_MOTOR_BODY_D = 35.0
LIFT_MOTOR_BODY_H = 18.0
# Pusher motor: a fifth V2806 KV400 (D-037)
PUSHER_BOLT_PATTERN = (LIFT_MOTOR_BOLT_CIRCLE, LIFT_MOTOR_BOLT_CIRCLE)  # cross pattern; VERIFY
PUSHER_BODY_D = LIFT_MOTOR_BODY_D
PUSHER_BODY_L = LIFT_MOTOR_BODY_H
PUSHER_PROP_OFFSET = 12.0  # prop plane behind the motor body (adapter + hub); VERIFY

# Camera: Insta360 GO 3S (VERIFY)
GO3S_SIZE = (54.0, 25.5, 24.5)  # L x W x H mm, lens on one end

# Battery: 6S1P 21700 pack, 6 cells as 3 wide x 2 high, lying flat (VERIFY against the purchased pack)
BATTERY = (76.0, 68.0, 46.0)  # L x W x H mm
