import warnings
from enum import IntEnum

import numpy as np
from .lib.coordinates import LocalCoord

RINEX_CONSTELLATION_IDENTIFIERS = {
  'GPS': 'G',
  'GLONASS': 'R',
  'SBAS': 'S',
  'GALILEO': 'E',
  'BEIDOU': 'C',
  'QZNSS': 'J',
  'IRNSS': 'I',
  'IMES': 'M'
}

# Make above dictionary bidirectional map:
# Now you can ask for constellation using:
# >>> RINEX_CONSTELLATION_IDENTIFIERS['R']
#     "GLONASS"
RINEX_CONSTELLATION_IDENTIFIERS.update(
  dict([reversed(i) for i in RINEX_CONSTELLATION_IDENTIFIERS.items()])  # type: ignore
)


class ConstellationId(IntEnum):
  # Int values match Ublox version 8
  GPS = 0
  SBAS = 1
  GALILEO = 2
  IMES = 4
  BEIDOU = 3
  QZNSS = 5
  GLONASS = 6
  # Not supported by Ublox:
  IRNSS = 7

  def to_rinex_char(self):
    # returns single character id
    return RINEX_CONSTELLATION_IDENTIFIERS[self.name]


# From https://gpsd.gitlab.io/gpsd/NMEA.html - Satellite IDs section
NMEA_ID_RANGES = (
  {
    'range': (1, 32),
    'constellation': ConstellationId.GPS,
  },
  {
    'range': (33, 54),
    'constellation': ConstellationId.SBAS,
  },
  {
    'range': (55, 64),
    'constellation': ConstellationId.SBAS,
  },
  {
    'range': (65, 88),
    'constellation': ConstellationId.GLONASS,
  },
  {
    'range': (89, 96),
    'constellation': ConstellationId.GLONASS,
  },
  {
    'range': (120, 151),
    'constellation': ConstellationId.SBAS,
  },
  {
    'range': (152, 158),
    'constellation': ConstellationId.SBAS,
  },
  {
    'range': (173, 182),
    'constellation': ConstellationId.IMES
  },
  {
    'range': (193, 197),
    'constellation': ConstellationId.QZNSS,
  },
  {
    'range': (198, 200),
    'constellation': ConstellationId.QZNSS,
  },
  {
    'range': (201, 235),
    'constellation': ConstellationId.BEIDOU,
  },
  {
    'range': (301, 336),
    'constellation': ConstellationId.GALILEO,
  },
  {
    'range': (401, 437),
    'constellation': ConstellationId.BEIDOU,
  }
)


def get_el_az(pos, sat_pos):
  converter = LocalCoord.from_ecef(pos)
  sat_ned = converter.ecef2ned(sat_pos)
  sat_range = np.linalg.norm(sat_ned)

  el = np.arcsin(-sat_ned[2] / sat_range)  # pylint: disable=unsubscriptable-object
  az = np.arctan2(sat_ned[1], sat_ned[0])  # pylint: disable=unsubscriptable-object
  return el, az


def get_closest(time, candidates, recv_pos=None):
  if recv_pos is None:
    # Takes a list of object that have an epoch(GPSTime) value
    # and return the one that is closest the given time (GPSTime)
    return min(candidates, key=lambda candidate: abs(time - candidate.epoch), default=None)

  return min(
    (candidate for candidate in candidates if candidate.valid(time, recv_pos)),
    key=lambda candidate: np.linalg.norm(recv_pos - candidate.pos),
    default=None,
  )


def get_constellation(prn):
  identifier = prn[0]

  if identifier in RINEX_CONSTELLATION_IDENTIFIERS:
    return RINEX_CONSTELLATION_IDENTIFIERS[identifier]
  warnings.warn(f"Unknown constellation for PRN {prn}")
  return None


def get_unknown_prn_from_nmea_id(nmea_id):
  return "?%d" % nmea_id


def get_nmea_id_from_unknown_prn(prn):
  return int(prn[1:])


def is_unknown_prn(prn):
  return prn[0] == '?'


def get_prn_from_nmea_id(nmea_id):
  constellation_offsets = {}

  for entry in NMEA_ID_RANGES:
    start, end = entry['range']
    constellation = entry['constellation']

    if nmea_id < start:
      warnings.warn("RINEX PRN for nmea id %i not known" % nmea_id)
      return get_unknown_prn_from_nmea_id(nmea_id)

    constellation_offset = constellation_offsets.get(constellation, 0)

    if nmea_id <= end:
      if constellation is None:
        warnings.warn("Constellation for nmea id "
                      "%i not known" % nmea_id)
        return get_unknown_prn_from_nmea_id(nmea_id)

      identifier = constellation.to_rinex_char()
      if identifier is None:
        warnings.warn("RINEX3 constellation identifier for "
                      "constellation %s is not known" % constellation)
        return get_unknown_prn_from_nmea_id(nmea_id)

      number = nmea_id - start + 1 + constellation_offset
      return "%s%02d" % (identifier, number)
    else:
      range_width = end - start + 1
      constellation_offsets[constellation] = constellation_offset + range_width

  warnings.warn("RINEX PRN for nmea id %i not known" % nmea_id)
  return get_unknown_prn_from_nmea_id(nmea_id)


def get_nmea_id_from_prn(prn):
  if is_unknown_prn(prn):
    return get_nmea_id_from_unknown_prn(prn)

  prn_constellation = get_constellation(prn)
  satellite_id = int(prn[1:])
  if satellite_id < 1:
    raise ValueError("PRN must contains number greater then 0")
  constellation_offset = 0
  for entry in NMEA_ID_RANGES:
    if entry['constellation'] != prn_constellation:
      continue
    start, end = entry['range']
    range_width = end - start + 1
    index_in_range = satellite_id - constellation_offset - 1
    if range_width > index_in_range:
      return start + index_in_range
    else:
      constellation_offset += range_width
  raise NotImplementedError(f"NMEA ID not found for PRN {prn}")


def rinex3_obs_from_rinex2_obs(observable):
  if observable == 'P2':
    return 'C2P'
  if len(observable) == 2:
    return observable + 'C'
  raise NotImplementedError("Don't know this: " + observable)


class TimeRangeHolder:
  '''Class to support test if date is in any of the multiple, sparse ranges'''

  def __init__(self):
    # Sorted list
    self._ranges = []

  def _previous_and_contains_index(self, time):
    prev = None
    current = None

    for idx, (start, end) in enumerate(self._ranges):
      # Time may be in next range
      if time > end:
        continue

      # Time isn't in any next range
      if time < start:
        prev = idx - 1
        current = None
      # Time is in current range
      else:
        prev = idx - 1
        current = idx
      break

    # Break in last loop
    if prev is None:
      prev = len(self._ranges) - 1

    return prev, current

  def add(self, start_time, end_time):
    prev_start, current_start = self._previous_and_contains_index(start_time)
    _, current_end = self._previous_and_contains_index(end_time)

    # Merge ranges
    if current_start is not None and current_end is not None:
      # If ranges are different then merge
      if current_start != current_end:
        new_start, _ = self._ranges[current_start]
        _, new_end = self._ranges[current_end]
        new_range = (new_start, new_end)
        # Required reversed order to correct remove
        del self._ranges[current_end]
        del self._ranges[current_start]
        self._ranges.insert(current_start, new_range)
    # Extend range - left
    elif current_start is not None:
      new_start, _ = self._ranges[current_start]
      new_range = (new_start, end_time)
      del self._ranges[current_start]
      self._ranges.insert(current_start, new_range)
    # Extend range - right
    elif current_end is not None:
      _, new_end = self._ranges[current_end]
      new_range = (start_time, new_end)
      del self._ranges[current_end]
      self._ranges.insert(prev_start + 1, new_range)
    # Create new range
    else:
      new_range = (start_time, end_time)
      self._ranges.insert(prev_start + 1, new_range)

  def __contains__(self, time):
    for start, end in self._ranges:
      # Time may be in next range
      if time > end:
        continue

      # Time isn't in any next range
      if time < start:
        return False
      # Time is in current range
      return True
    return False
