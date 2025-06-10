# These are all from IS-GPS-200G unless otherwise noted

SPEED_OF_LIGHT = 2.99792458e8  # m/s

# Physical parameters of the Earth
EARTH_GM = 3.986005e14  # m^3/s^2 (gravitational constant * mass of earth)
EARTH_RADIUS = 6.3781e6  # m
EARTH_ROTATION_RATE = 7.2921151467e-005  # rad/s (WGS84 earth rotation rate)

# GPS system parameters:
GPS_L1 = l1 = 1.57542e9  # Hz
GPS_L2 = l2 = 1.22760e9  # Hz
GPS_L5 = l5 = 1.17645e9  # Hz Also E5

#GLONASS system parameters
#TODO this is old convention
GLONASS_L1 = 1.602e9
GLONASS_L1_DELTA = 0.5625e6
GLONASS_L2 = 1.246e9
GLONASS_L2_DELTA = 0.4375e6
GLONASS_L5 = 1.201e9
GLONASS_L5_DELTA = 0.4375e6

#Galileo system parameters:  # Has additional frequencies on E6
#Source RINEX 2.11 document
GALILEO_E5B = 1.207140e9  # Hz
GALILEO_E5AB = 1.191795e9  # Hz
GALILEO_E6 = 1.27875e9  # Hz

SECS_IN_MIN = 60
SECS_IN_HR = 60*SECS_IN_MIN
SECS_IN_DAY = 24*SECS_IN_HR
SECS_IN_WEEK = 7*SECS_IN_DAY
SECS_IN_YEAR = 365*SECS_IN_DAY


# Glonass channel have not changed between 2018 and 2025 for sats 1-24, assume constant
GLONASS_CHANNELS = {
                    "R01": 1,
                    "R02": -4,
                    "R03": 5,
                    "R04": 6,
                    "R05": 1,
                    "R06": -4,
                    "R07": 5,
                    "R08": 6,
                    "R09": -2,
                    "R10": -7,
                    "R11": 0,
                    "R12": -1,
                    "R13": -2,
                    "R14": -7,
                    "R15": 0,
                    "R16": -1,
                    "R17": 4,
                    "R18": -3,
                    "R19": 3,
                    "R20": 2,
                    "R21": 4,
                    "R22": -3,
                    "R23": 3,
                    "R24": 2,
                    "R25": None,
                    "R26": None,
                    }