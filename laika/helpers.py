import numpy as np
from .lib.coordinates import LocalCoord

GPS_OFFSET = 0
GLONASS_OFFSET = 64
GALILEO_OFFSET = 96
QZNSS_OFFSET = 192
BEIDOU_OFFSET = 200

GPS_SIZE = 32
GLONASS_SIZE = 28
GALILEO_SIZE = 36
QZNSS_SIZE = 4
BEIDOU_SIZE = 14


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
  if prn[0] == 'G':
    return 'GPS'
  elif prn[0] == 'R':
    return 'GLONASS'
  elif prn[0] == 'E':
    return 'GALILEO'
  elif prn[0] == 'J':
    return 'QZNSS'
  elif prn[0] == 'C':
    return 'BEIDOU'
  else:
    raise NotImplementedError('The constellation of RINEX3 constellation identifier: %s not known' % prn[0])


def get_prn_from_nmea_id(nmea_id):
  if nmea_id in np.arange(1,GPS_SIZE + 1) + GPS_OFFSET:
    return 'G%02i' % (nmea_id - GPS_OFFSET)
  elif nmea_id in (np.arange(1,GLONASS_SIZE + 1) + GLONASS_OFFSET):
    return 'R%02i' % (nmea_id - GLONASS_OFFSET)
  elif nmea_id in (np.arange(1,GALILEO_SIZE + 1) + GALILEO_OFFSET):
    return 'E%02i' % (nmea_id - GALILEO_OFFSET)
  elif nmea_id in (np.arange(1,QZNSS_SIZE + 1) + QZNSS_OFFSET):
    return 'J%02i' % (nmea_id - QZNSS_OFFSET)
  elif nmea_id in (np.arange(1,BEIDOU_SIZE + 1) + BEIDOU_OFFSET):
    return 'C%02i' % (nmea_id - BEIDOU_OFFSET)
  else:
    raise NotImplementedError("RINEX PRN for nmea id %i not known" % nmea_id)


def get_nmea_id_from_prn(prn):
  if prn[0] == 'G':
    nmea_id = int(prn[1:]) + GPS_OFFSET
  # glonass record
  elif prn[0] == 'R':
    nmea_id = int(prn[1:]) + GLONASS_OFFSET
  # galileo record
  elif prn[0] == 'E':
    nmea_id = int(prn[1:]) + GALILEO_OFFSET
  # QZNSS record
  elif prn[0] == 'J':
      nmea_id = int(prn[1:]) + QZNSS_OFFSET
  # Beidou record
  elif prn[0] == 'C':
    nmea_id = int(prn[1:]) + BEIDOU_OFFSET
  else:
    raise NotImplementedError("RINEX constelletion identifier %s not supported by laika" % prn[0])
  return nmea_id


def get_prns_from_constellation(constellation):
  if constellation == 'GPS':
    return ['G' + str(n).zfill(2) for n in range(1, GPS_SIZE + 1)]
  elif constellation == 'GLONASS':
    return ['R' + str(n).zfill(2) for n in range(1, GLONASS_SIZE + 1)]
  elif constellation == 'GALILEO':
    return ['E' + str(n).zfill(2) for n in range(1, GALILEO_SIZE + 1)]
  elif constellation == 'QZNSS':
    return ['J' + str(n).zfill(2) for n in range(1, QZNSS_SIZE + 1)]
  elif constellation == 'BEIDOU':
    return ['C' + str(n).zfill(2) for n in range(1, BEIDOU_SIZE + 1)]


def rinex3_obs_from_rinex2_obs(observable):
  if observable == 'P2':
    return 'C2P'
  if len(observable) == 2:
    return observable + 'C'
  else:
      raise NotImplementedError("Don't know this: " + observable)
