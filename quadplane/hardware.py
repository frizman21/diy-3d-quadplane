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
MN3508_BOLT_CIRCLE = 25.0  # 4 x M3 (T-Motor MN3508 stator mount)
MN3508_BODY_D = 42.0
MN3508_BODY_H = 27.0
X2820_BOLT_PATTERN = (16.0, 19.0)  # cross pattern, M3 (SunnySky X28xx)
X2820_BODY_D = 35.0
X2820_BODY_L = 40.0

# Camera: Insta360 GO 3S (VERIFY)
GO3S_SIZE = (54.0, 25.5, 24.5)  # L x W x H mm, lens on one end

# Battery: 6S2P 21700 pack (VERIFY against the purchased pack)
BATTERY_6S2P = (140.0, 46.0, 75.0)  # L x W x H mm
