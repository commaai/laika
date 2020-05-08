import numpy as np
from .lib.coordinates import LocalCoord

# From https://gpsd.gitlab.io/gpsd/NMEA.html - Satellite IDs section
NMEA_ID_RANGES = [
  {
    'range': [1, 32],
    'constellation': 'GPS'
  },
  {
    'range': [33, 54],
    'constellation': 'SBAS'
  },
  {
    'range': [55, 64],
    'constellation': 'SBAS'
  },
  {
    'range': [65, 88],
    'constellation': 'GLONASS'
  },
  {
    'range': [89, 96],
    'constellation': 'GLONASS'
  },
  {
    'range': [120, 151],
    'constellation': 'SBAS'
  },
  {
    'range': [152, 158],
    'constellation': 'SBAS'
  },
  {
    'range': [173, 182],
    'constellation': 'IMES'
  },
  {
    'range': [193, 197],
    'constellation': 'QZNSS'
  },
  {
    'range': [198, 200],
    'constellation': 'QZNSS'
  },
  {
    'range': [201, 235],
    'constellation': 'BEIDOU'
  },
  {
    'range': [301, 336],
    'constellation': 'GALILEO'
  },
  {
    'range': [401, 437],
    'constellation': 'BEIDOU'
  }
]

# Source: RINEX 3.04
RINEX_CONSTELLATION_IDENTIFIERS = {
  'GPS': 'G',
  'GLONASS': 'R',
  'SBAS': 'S',
  'GALILEO': 'E',
  'BEIDOU': 'C',
  'QZNSS': 'J',
  'IRNSS': 'I'
}
# Make above dictionary bidirectional map:
# Now you can ask for constellation using:
# >>> RINEX_CONSTELLATION_IDENTIFIERS['R']
#     "GLONASS"
RINEX_CONSTELLATION_IDENTIFIERS.update(
  dict([reversed(i) for i in RINEX_CONSTELLATION_IDENTIFIERS.items()])
)


def get_el_az(pos, sat_pos):
  converter = LocalCoord.from_ecef(pos)
  sat_ned = converter.ecef2ned(sat_pos)
  sat_range = np.linalg.norm(sat_ned)

  el = np.arcsin(-sat_ned[2]/sat_range)
  az = np.arctan2(sat_ned[1], sat_ned[0])
  return el, az


def get_closest(time, candidates, recv_pos=None):
  if recv_pos is None:
    # Takes a list of object that have an epoch(GPSTime) value
    # and return the one that is closest the given time (GPSTime)
    tdiff = np.inf
    closest = None
    for candidate in candidates:
      if abs(time - candidate.epoch) < tdiff:
        closest = candidate
        tdiff = abs(time - candidate.epoch)
    return closest
  else:
    pdiff = np.inf
    closest = None
    for candidate in candidates:
      cand_diff = np.linalg.norm(recv_pos - candidate.pos)
      if cand_diff < pdiff and candidate.valid(time, recv_pos):
        pdiff = cand_diff
        closest = candidate
    return closest


def get_constellation(prn):
  identifier = prn[0]

  if identifier in RINEX_CONSTELLATION_IDENTIFIERS:
    return RINEX_CONSTELLATION_IDENTIFIERS[identifier]
  else:
    raise NotImplementedError('The constellation of RINEX3 constellation '
                              'identifier: %s not known' % identifier)


def get_prn_from_nmea_id(nmea_id):
  constellation_offsets = {}
  for entry in NMEA_ID_RANGES:
    start, end = entry['range']
    constellation = entry['constellation']
    if nmea_id < start:
      raise NotImplementedError("RINEX PRN for nmea id %i not known" % nmea_id)

    constellation_offset = constellation_offsets.get(constellation, 0)

    if nmea_id <= end:
      if constellation is None:
        raise NotImplementedError("Constellation for nmea id "
                                  "%i not known" % nmea_id)
      identifier = RINEX_CONSTELLATION_IDENTIFIERS.get(constellation)
      if identifier is None:
        raise NotImplementedError("RINEX3 constellation identifier for "
                                  "constellation %s is not known"
                                  % constellation)
      number = nmea_id - start + 1 + constellation_offset
      return "%s%02d" % (identifier, number)
    else:
      range_width = end - start + 1
      constellation_offsets[constellation] = constellation_offset + range_width

  raise NotImplementedError("RINEX PRN for nmea id %i not known" % nmea_id)


def get_nmea_id_from_prn(prn):
  prn_constellation = get_constellation(prn)
  satellite_id = int(prn[1:])
  if satellite_id < 1:
    raise ValueError("PRN must contains number greater then 0")
  constellation_offset = 0
  for entry in NMEA_ID_RANGES:
    start, end = entry['range']
    constellation = entry['constellation']
    if constellation != prn_constellation:
      continue
    range_width = end - start + 1
    index_in_range = satellite_id - constellation_offset - 1
    if range_width > index_in_range:
      return start + index_in_range
    else:
      constellation_offset += range_width
  raise NotImplementedError("NMEA ID not found for PRN %s" % prn)


def rinex3_obs_from_rinex2_obs(observable):
  if observable == 'P2':
    return 'C2P'
  if len(observable) == 2:
    return observable + 'C'
  else:
      raise NotImplementedError("Don't know this: " + observable)
