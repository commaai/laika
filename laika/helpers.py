from enum import IntEnum

import numpy as np
from .lib.coordinates import LocalCoord

# From https://gpsd.gitlab.io/gpsd/NMEA.html - Satellite IDs section
CONSTELLATION_TO_NMEA_RANGES = {
  # nmea ranges for each constellation with its svid offset.
  # constellation: [(start, end, svid_offset)]
  # Sv_id = nmeaId + offset
  'GPS': [(1, 32, 0)],
  'SBAS': [(33, 64, -32), (120, 158, -87)],
  'GLONASS': [(65, 96, -64)],
  'IMES': [(173, 182, -172)],
  'QZNSS': [(193, 200, -192)], # todo should be QZSS
  'BEIDOU': [(201, 235, -200), (401, 437, -365)],
  'GALILEO': [(301, 336, -300)]
}

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
  dict([reversed(i) for i in RINEX_CONSTELLATION_IDENTIFIERS.items()])  # type: ignore
)


class UbloxGnssId(IntEnum):
  # For Ublox version 8
  GPS = 0
  SBAS = 1
  GALILEO = 2
  BEIDOU = 3
  QZNSS = 5
  GLONASS = 6

  def to_constellation_id(self):
    return RINEX_CONSTELLATION_IDENTIFIERS[self.name]


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
  return None


def get_prn_from_nmea_id(nmea_id):
  for c, ranges in CONSTELLATION_TO_NMEA_RANGES.items():
    for (start, end, sv_id_offset) in ranges:
      if start <= nmea_id <= end:
        constellation = c
        svid = nmea_id + sv_id_offset

        return "%s%02d" % (RINEX_CONSTELLATION_IDENTIFIERS[constellation], svid)

  raise ValueError(f"constellation not found for nmeaid {nmea_id}")


def get_nmea_id_from_prn(prn):
  constellation = get_constellation(prn)
  if constellation is None:
    raise ValueError(f"Constellation not found for prn {prn}")

  sv_id = int(prn[1:]) # satellite id
  ranges = CONSTELLATION_TO_NMEA_RANGES[constellation]
  for (start,end,sv_id_offset) in ranges:
    new_nmea_id = sv_id - sv_id_offset
    if start <= new_nmea_id <= end:
      return new_nmea_id

  raise ValueError(f"NMEA ID not found for constellation {constellation} with satellite id {sv_id}")


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
