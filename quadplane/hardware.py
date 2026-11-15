"""Off-the-shelf hardware dimensions. All units mm. VERIFY against the parts you actually buy."""

# Holes for screws (diameters)
M2_CLEAR = 2.4
M3_CLEAR = 3.4
M3_HEAD_D = 5.8
M3_HEAD_H = 3.0

# Heat-set inserts: hole diameter / depth (M3 x 5.7 "short" type, typical)
M3_INSERT_HOLE = 4.2
M3_INSERT_DEPTH = 6.0

# Carbon tubes (outer diameter); candidate spar/boom sizes
CARBON_TUBES_OD = (8.0, 10.0, 12.0, 16.0)

# Motors (VERIFY against the delivered motors before printing mounts)
# Lift motor: T-Motor MN4014 KV400 (D-027)
LIFT_MOTOR_BOLT_CIRCLE = 25.0  # 4 x M3 stator mount; VERIFY (not on the product page)
LIFT_MOTOR_BODY_D = 44.7
LIFT_MOTOR_BODY_H = 34.5
# Pusher motor: SunnySky X3520 520KV (D-031)
PUSHER_BOLT_PATTERN = (25.0, 25.0)  # cross pattern; VERIFY (not published by the retailers)
PUSHER_BODY_D = 42.5
PUSHER_BODY_L = 45.0  # VERIFY (64 mm overall with the shaft)

# Camera: Insta360 GO 3S (VERIFY)
GO3S_SIZE = (54.0, 25.5, 24.5)  # L x W x H mm, lens on one end

# Battery: 6S3P 21700 pack, 18 cells as 2 long x 3 wide x 3 high (VERIFY against the purchased pack)
BATTERY = (140.0, 68.0, 75.0)  # L x W x H mm
