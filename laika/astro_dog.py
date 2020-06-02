from collections import defaultdict

from .helpers import get_constellation, get_closest, get_el_az, TimeRangeHolder
from .ephemeris import parse_sp3_orbits, parse_rinex_nav_msg_gps, \
                       parse_rinex_nav_msg_glonass
from .downloader import download_orbits, download_orbits_russia, download_nav, download_ionex, download_dcb
from .downloader import download_cors_station
from .trop import saast
from .iono import parse_ionex
from .dcb import parse_dcbs
from .dgps import get_closest_station_names, parse_dgps
from . import constants

MAX_DGPS_DISTANCE = 100000  # in meters, because we're not barbarians


class AstroDog(object):
  '''
  auto_update: flag indicating whether laika should fetch files from web
  cache_dir:   directory where data files are downloaded to and cached
  pull_orbit:  flag indicating whether laika should fetch sp3 orbits
                 instead of nav files (orbits are more accurate)
  dgps:        flag indicating whether laika should use dgps (CORS)
               data to calculate pseudorange corrections
  valid_const: list of constellation identifiers laika will try process

  '''
  def __init__(self, auto_update=True,
               cache_dir='/tmp/gnss/',
               pull_orbit=True, dgps=False,
               valid_const=['GPS', 'GLONASS']):
    self.auto_update = auto_update
    self.cache_dir = cache_dir
    self.dgps = dgps
    self.dgps_delays = []
    self.ionex_maps = []
    self.pull_orbit = pull_orbit
    self.valid_const = valid_const
    self.cached_ionex = None
    self.cached_dgps = None

    self.orbit_fetched_times = TimeRangeHolder()
    self.nav_fetched_times = TimeRangeHolder()
    self.dcbs_fetched_times = TimeRangeHolder()

    self.orbits = defaultdict(lambda: [])
    self.nav = defaultdict(lambda: [])
    self.dcbs = defaultdict(lambda: [])

    self.cached_orbit = defaultdict(lambda: None)
    self.cached_nav = defaultdict(lambda: None)
    self.cached_dcb = defaultdict(lambda: None)

  def get_ionex(self, time):
    if self.cached_ionex is not None and self.cached_ionex.valid(time):
      return self.cached_ionex

    self.cached_ionex = get_closest(time, self.ionex_maps)
    if self.cached_ionex is not None and self.cached_ionex.valid(time):
      return self.cached_ionex

    self.get_ionex_data(time)
    self.cached_ionex = get_closest(time, self.ionex_maps)
    if self.cached_ionex is not None and self.cached_ionex.valid(time):
      return self.cached_ionex
    elif self.auto_update:
      raise RuntimeError("Pulled ionex, but still can't get valid for time " + str(time))
    else:
      return None

  def get_nav(self, prn, time):
    if self.cached_nav[prn] is not None and self.cached_nav[prn].valid(time):
      return self.cached_nav[prn]

    self.cached_nav[prn] = get_closest(time, self.nav[prn])
    if self.cached_nav[prn] is not None and self.cached_nav[prn].valid(time):
      return self.cached_nav[prn]

    # Already fetched, but no data found
    if time in self.nav_fetched_times:
      return None

    self.get_nav_data(time)
    self.cached_nav[prn] = get_closest(time, self.nav[prn])
    if self.cached_nav[prn] is not None and self.cached_nav[prn].valid(time):
      return self.cached_nav[prn]
    else:
      return None

  @staticmethod
  def _select_valid_temporal_items(item_dict, time, cache):
    '''Returns only valid temporal item for specific time from currently fetched
    data.'''
    result = {}
    for prn, temporal_objects in item_dict.items():
      cached = cache[prn]
      if cached is not None and cached.valid(time):
        obj = cached
      else:
        obj = get_closest(time, temporal_objects)
        if obj is None or not obj.valid(time):
          continue
        cache[prn] = obj
      result[prn] = obj
    return result

  def get_navs(self, time):
    if time in self.nav_fetched_times:
      valid_navs = AstroDog._select_valid_temporal_items(self.nav, time,
                                                         self.cached_nav)
    else:
      self.get_nav_data(time)
      valid_navs = AstroDog._select_valid_temporal_items(self.nav, time,
                                                         self.cached_nav)

    return valid_navs

  def get_orbit(self, prn, time):
    if self.cached_orbit[prn] is not None and self.cached_orbit[prn].valid(time):
      return self.cached_orbit[prn]

    self.cached_orbit[prn] = get_closest(time, self.orbits[prn])
    if self.cached_orbit[prn] is not None and self.cached_orbit[prn].valid(time):
      return self.cached_orbit[prn]

    # Already fetched, but no data found
    if time in self.orbit_fetched_times:
      return None

    self.get_orbit_data(time)
    self.cached_orbit[prn] = get_closest(time, self.orbits[prn])
    if self.cached_orbit[prn] is not None and self.cached_orbit[prn].valid(time):
      return self.cached_orbit[prn]
    else:
      return None

  def get_orbits(self, time):
    if time in self.orbit_fetched_times:
      valid_orbits = AstroDog._select_valid_temporal_items(self.orbits, time,
                                                           self.cached_orbit)
    else:
      self.get_orbit_data(time)
      valid_orbits = AstroDog._select_valid_temporal_items(self.orbits, time,
                                                           self.cached_orbit)

    return valid_orbits

  def get_dcb(self, prn, time):
    if self.cached_dcb[prn] is not None and self.cached_dcb[prn].valid(time):
      return self.cached_dcb[prn]

    self.cached_dcb[prn] = get_closest(time, self.dcbs[prn])
    if self.cached_dcb[prn] is not None and self.cached_dcb[prn].valid(time):
      return self.cached_dcb[prn]

    # Already fetched, but no data found
    if time in self.dcbs_fetched_times:
      return None

    self.get_dcb_data(time)
    self.cached_dcb[prn] = get_closest(time, self.dcbs[prn])
    if self.cached_dcb[prn] is not None and self.cached_dcb[prn].valid(time):
      return self.cached_dcb[prn]
    else:
      return None

  def get_dgps_corrections(self, time, recv_pos):
    if self.cached_dgps is not None and self.cached_dgps.valid(time, recv_pos):
      return self.cached_dgps

    self.cached_dgps = get_closest(time, self.dgps_delays, recv_pos=recv_pos)
    if self.cached_dgps is not None and self.cached_dgps.valid(time, recv_pos):
      return self.cached_dgps

    self.get_dgps_data(time, recv_pos)
    self.cached_dgps = get_closest(time, self.dgps_delays, recv_pos=recv_pos)
    if self.cached_dgps is not None and self.cached_dgps.valid(time, recv_pos):
      return self.cached_dgps
    elif self.auto_update:
      raise RuntimeError("Pulled dgps, but still can't get valid for time " + str(time))
    else:
      return None

  def add_ephem(self, new_ephem, ephems):
    prn = new_ephem.prn
    # TODO make this check work
    # for eph in ephems[prn]:
    #   if eph.type == new_ephem.type and eph.epoch == new_ephem.epoch:
    #     raise RuntimeError('Trying to add an ephemeris that is already there, something is wrong')
    ephems[prn].append(new_ephem)

  def get_nav_data(self, time):
    ephems_gps, ephems_glonass = [], []
    if 'GPS' in self.valid_const:
      file_path_gps = download_nav(time, cache_dir=self.cache_dir, constellation='GPS')
      if file_path_gps:
        ephems_gps = parse_rinex_nav_msg_gps(file_path_gps)
    if 'GLONASS' in self.valid_const:
      file_path_glonass = download_nav(time, cache_dir=self.cache_dir, constellation='GLONASS')
      if file_path_glonass:
         ephems_glonass = parse_rinex_nav_msg_glonass(file_path_glonass)

    fetched_ephems = (ephems_gps + ephems_glonass)

    for ephem in fetched_ephems:
      self.add_ephem(ephem, self.nav)

    if len(fetched_ephems) != 0:
      min_ephem = min(fetched_ephems, key=lambda e: e.epoch)
      max_ephem = max(fetched_ephems, key=lambda e: e.epoch)

      min_epoch = min_ephem.epoch - min_ephem.max_time_diff
      max_epoch = max_ephem.epoch + max_ephem.max_time_diff

      self.nav_fetched_times.add(min_epoch, max_epoch)

  def get_orbit_data(self, time):
    file_paths_sp3_ru = download_orbits_russia(time, cache_dir=self.cache_dir)
    ephems_sp3_ru = parse_sp3_orbits(file_paths_sp3_ru, self.valid_const)
    file_paths_sp3_us = download_orbits(time, cache_dir=self.cache_dir)
    ephems_sp3_us = parse_sp3_orbits(file_paths_sp3_us, self.valid_const)
    ephems_sp3 = ephems_sp3_ru + ephems_sp3_us
    if len(ephems_sp3) < 5:
      raise RuntimeError('No orbit data found on either servers')

    for ephem in ephems_sp3:
      self.add_ephem(ephem, self.orbits)

    if len(ephems_sp3) != 0:
      min_ephem = min(ephems_sp3, key=lambda e: e.epoch)
      max_ephem = max(ephems_sp3, key=lambda e: e.epoch)

      min_epoch = min_ephem.epoch - min_ephem.max_time_diff
      max_epoch = max_ephem.epoch + max_ephem.max_time_diff

      self.orbit_fetched_times.add(min_epoch, max_epoch)

  def get_dcb_data(self, time):
    file_path_dcb = download_dcb(time, cache_dir=self.cache_dir)
    dcbs = parse_dcbs(file_path_dcb, self.valid_const)
    for dcb in dcbs:
      self.dcbs[dcb.prn].append(dcb)

    if len(dcbs) != 0:
      min_dcb = min(dcbs, key=lambda e: e.epoch)
      max_dcb = max(dcbs, key=lambda e: e.epoch)

      min_epoch = min_dcb.epoch - min_dcb.max_time_diff
      max_epoch = max_dcb.epoch + max_dcb.max_time_diff

      self.dcbs_fetched_times.add(min_epoch, max_epoch)

  def get_ionex_data(self, time):
    file_path_ionex = download_ionex(time, cache_dir=self.cache_dir)
    ionex_maps = parse_ionex(file_path_ionex)
    for im in ionex_maps:
      self.ionex_maps.append(im)

  def get_dgps_data(self, time, recv_pos):
    station_names = get_closest_station_names(recv_pos, k=8, max_distance=MAX_DGPS_DISTANCE, cache_dir=self.cache_dir)
    for station_name in station_names:
      file_path_station = download_cors_station(time, station_name, cache_dir=self.cache_dir)
      if file_path_station:
        dgps = parse_dgps(station_name, file_path_station,
                         self, max_distance=MAX_DGPS_DISTANCE,
                         required_constellations=self.valid_const)
        if dgps is not None:
          self.dgps_delays.append(dgps)
          break

  def get_tgd_from_nav(self, prn, time):
    if get_constellation(prn) not in self.valid_const:
      return None

    eph = self.get_nav(prn, time)

    if eph:
      return eph.get_tgd()
    else:
      return None

  def get_sat_info(self, prn, time):
    if get_constellation(prn) not in self.valid_const:
      return None

    if self.pull_orbit:
      eph = self.get_orbit(prn, time)
    else:
      eph = self.get_nav(prn, time)

    if eph:
      return eph.get_sat_info(time)
    else:
      return None

  def get_all_sat_info(self, time):
    if self.pull_orbit:
      ephs = self.get_orbits(time)
    else:
      ephs = self.get_navs(time)

    return {prn: eph.get_sat_info(time) for prn, eph in ephs.items()}

  def get_glonass_channel(self, prn, time):
    nav = self.get_nav(prn, time)
    if nav:
      return nav.channel
    else:
      return None

  def get_frequency(self, prn, time, signal='C1C'):
    if get_constellation(prn) == 'GPS':
      if signal[1] == '1':
        return constants.GPS_L1
      elif signal[1] == '2':
        return constants.GPS_L2
      elif signal[1] == '5':
        return constants.GPS_L5
      elif signal[1] == '6':
        return constants.GALILEO_E6
      elif signal[1] == '7':
        return constants.GALILEO_E5B
      elif signal[1] == '8':
        return constants.GALILEO_E5AB
      else:
        raise NotImplementedError('Dont know this GPS frequency: ', signal, prn)
    elif get_constellation(prn) == 'GLONASS':
      n = self.get_glonass_channel(prn, time)
      if n is None:
        return None
      if signal[1] == '1':
        return constants.GLONASS_L1 + n * constants.GLONASS_L1_DELTA
      if signal[1] == '2':
        return constants.GLONASS_L2 + n * constants.GLONASS_L2_DELTA
      if signal[1] == '5':
        return constants.GLONASS_L5 + n * constants.GLONASS_L5_DELTA
      if signal[1] == '6':
        return constants.GALILEO_E6
      if signal[1] == '7':
        return constants.GALILEO_E5B
      if signal[1] == '8':
        return constants.GALILEO_E5AB
      else:
        raise NotImplementedError('Dont know this GLONASS frequency: ', signal, prn)

  def get_delay(self, prn, time, rcv_pos, no_dgps=False, signal='C1C', freq=None):
    sat_info = self.get_sat_info(prn, time)
    if sat_info is None:
      return None
    sat_pos = sat_info[0]
    el, az = get_el_az(rcv_pos, sat_pos)
    if el < 0.2:
      return None
    if self.dgps and not no_dgps:
      dgps_corrections = self.get_dgps_corrections(time, rcv_pos)
      if dgps_corrections is None:
        return None
      dgps_delay = dgps_corrections.get_delay(prn, time)
      if dgps_delay is None:
        return None
      return dgps_corrections.get_delay(prn, time)
    else:
      if not freq:
        freq = self.get_frequency(prn, time, signal)
      ionex = self.get_ionex(time)
      dcb = self.get_dcb(prn, time)
      if ionex is None or dcb is None or freq is None:
        return None
      iono_delay = ionex.get_delay(rcv_pos, az, el, sat_pos, time, freq)
      trop_delay = saast(rcv_pos, el)
      code_bias = dcb.get_delay(signal)
      return iono_delay + trop_delay + code_bias
