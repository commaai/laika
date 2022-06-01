from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from typing import DefaultDict, Iterable, List, Optional, Union

from .constants import SECS_IN_DAY
from .helpers import ConstellationId, get_constellation, get_closest, get_el_az, TimeRangeHolder
from .ephemeris import EphemerisType, GLONASSEphemeris, GPSEphemeris, PolyEphemeris, parse_sp3_orbits, parse_rinex_nav_msg_gps, \
  parse_rinex_nav_msg_glonass
from .downloader import download_orbits_gps, download_orbits_others, download_nav, download_ionex, download_dcb
from .downloader import download_cors_station
from .trop import saast
from .iono import IonexMap, parse_ionex
from .dcb import DCB, parse_dcbs
from .gps_time import GPSTime
from .dgps import get_closest_station_names, parse_dgps
from . import constants

MAX_DGPS_DISTANCE = 100_000  # in meters, because we're not barbarians


class AstroDog:
  '''
  use_internet: flag indicating whether laika should fetch files from web
  cache_dir:   directory where data files are downloaded to and cached
  dgps:        flag indicating whether laika should use dgps (CORS)
               data to calculate pseudorange corrections
  valid_const: list of constellation identifiers laika will try process
  valid_ephem_types: set of ephemeris types that are allowed to use and download.
                Default is set to use all orbit ephemeris types (orbits are more accurate)
  '''

  def __init__(self, use_internet=True,
               cache_dir='/tmp/gnss/',
               dgps=False,
               valid_const=('GPS', 'GLONASS'),
               valid_ephem_types=EphemerisType.orbits()):
    self.use_internet = use_internet
    self.cache_dir = cache_dir
    self.dgps = dgps
    if not isinstance(valid_ephem_types, Iterable):
      valid_ephem_types = [valid_ephem_types]
    self.pull_orbit = len(set(EphemerisType.orbits()) & set(valid_ephem_types)) > 0
    self.pull_nav = EphemerisType.NAV in valid_ephem_types
    self.valid_const = valid_const
    self.valid_ephem_types = valid_ephem_types

    self.orbit_fetched_times = TimeRangeHolder()
    self.nav_fetched_times = TimeRangeHolder()
    self.dcbs_fetched_times = TimeRangeHolder()

    self.dgps_delays = []
    self.ionex_maps: List[IonexMap] = []
    self.orbits: DefaultDict[str, List[PolyEphemeris]] = defaultdict(list)
    self.nav: DefaultDict[str, List[Union[GPSEphemeris, GLONASSEphemeris]]] = defaultdict(list)
    self.dcbs: DefaultDict[str, List[DCB]] = defaultdict(list)

    self.cached_ionex: Optional[IonexMap] = None
    self.cached_dgps = None
    self.cached_orbit: DefaultDict[str, Optional[PolyEphemeris]] = defaultdict(lambda: None)
    self.cached_nav: DefaultDict[str, Union[GPSEphemeris, GLONASSEphemeris, None]] = defaultdict(lambda: None)
    self.cached_dcb: DefaultDict[str, Optional[DCB]] = defaultdict(lambda: None)

  def get_ionex(self, time) -> Optional[IonexMap]:
    ionex: Optional[IonexMap] = self._get_latest_valid_data(self.ionex_maps, self.cached_ionex, self.get_ionex_data, time)
    if ionex is None:
      if self.use_internet:
        raise RuntimeError("Pulled ionex, but still can't get valid for time " + str(time))
    else:
      self.cached_ionex = ionex
    return ionex

  def get_nav(self, prn, time):
    skip_download = time in self.nav_fetched_times
    nav = self._get_latest_valid_data(self.nav[prn], self.cached_nav[prn], self.get_nav_data, time, skip_download)
    if nav is not None:
      self.cached_nav[prn] = nav
    return nav

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
    if time not in self.nav_fetched_times and self.use_internet:
      self.get_nav_data(time)
    return AstroDog._select_valid_temporal_items(self.nav, time, self.cached_nav)

  def get_orbit(self, prn: str, time: GPSTime) -> PolyEphemeris:
    skip_download = time in self.orbit_fetched_times
    orbit = self._get_latest_valid_data(self.orbits[prn], self.cached_orbit[prn], self.get_orbit_data, time, skip_download)
    if orbit is not None:
      self.cached_orbit[prn] = orbit
    return orbit

  def get_orbits(self, time):
    if time not in self.orbit_fetched_times:
      self.get_orbit_data(time)
    return AstroDog._select_valid_temporal_items(self.orbits, time, self.cached_orbit)

  def get_dcb(self, prn, time):
    skip_download = time in self.dcbs_fetched_times
    dcb = self._get_latest_valid_data(self.dcbs[prn], self.cached_dcb[prn], self.get_dcb_data, time, skip_download)
    if dcb is not None:
      self.cached_dcb[prn] = dcb
    return dcb

  def get_dgps_corrections(self, time, recv_pos):
    latest_data = self._get_latest_valid_data(self.dgps_delays, self.cached_dgps, self.get_dgps_data, time, recv_pos=recv_pos)
    if latest_data is None:
      if self.use_internet:
        raise RuntimeError("Pulled dgps, but still can't get valid for time " + str(time))
    else:
      self.cached_dgps = latest_data
    return latest_data

  def add_ephems(self, new_ephems, ephems):
    for e in new_ephems:
      # TODO make this check work
      # for eph in ephems[prn]:
      #   if eph.type == new_ephem.type and eph.epoch == new_ephem.epoch:
      #     raise RuntimeError('Trying to add an ephemeris that is already there, something is wrong')
      ephems[e.prn].append(e)

  def get_nav_data(self, time):
    def download_and_parse(constellation, parse_rinex_nav_func):
      file_path = download_nav(time, cache_dir=self.cache_dir, constellation=constellation)
      return parse_rinex_nav_func(file_path) if file_path else []

    fetched_ephems = []

    if 'GPS' in self.valid_const:
      fetched_ephems += download_and_parse(ConstellationId.GPS, parse_rinex_nav_msg_gps)
    if 'GLONASS' in self.valid_const:
      fetched_ephems += download_and_parse(ConstellationId.GLONASS, parse_rinex_nav_msg_glonass)

    self.add_ephems(fetched_ephems, self.nav)

    if len(fetched_ephems) != 0:
      min_ephem = min(fetched_ephems, key=lambda e: e.epoch)
      max_ephem = max(fetched_ephems, key=lambda e: e.epoch)
      min_epoch = min_ephem.epoch - min_ephem.max_time_diff
      max_epoch = max_ephem.epoch + max_ephem.max_time_diff
      self.nav_fetched_times.add(min_epoch, max_epoch)
    else:
      begin_day = GPSTime(time.week, SECS_IN_DAY * (time.tow // SECS_IN_DAY))
      end_day = GPSTime(time.week, SECS_IN_DAY * (1 + (time.tow // SECS_IN_DAY)))
      self.nav_fetched_times.add(begin_day, end_day)

  def download_parse_orbit_data(self, gps_time: GPSTime, skip_before_epoch=None) -> List[PolyEphemeris]:
    def parse_orbits(file_futures):
      return parse_sp3_orbits([f.result() for f in file_futures if f.result()], self.valid_const, skip_before_epoch)

    time_steps = [gps_time - SECS_IN_DAY, gps_time, gps_time + SECS_IN_DAY]
    with ThreadPoolExecutor() as executor:
      futures_other = futures_gps = None
      if len(set(self.valid_const).difference(["GPS"])) > 0:
        futures_other = [executor.submit(download_orbits_others, t, self.cache_dir, self.valid_ephem_types) for t in time_steps]
      if "GPS" in self.valid_const:
        futures_gps = [executor.submit(download_orbits_gps, t, self.cache_dir, self.valid_ephem_types) for t in time_steps]

      ephems_sp3_other = parse_orbits(futures_other) if futures_other else []
      ephems_sp3_us = parse_orbits(futures_gps) if futures_gps else []

    return ephems_sp3_other + ephems_sp3_us

  def get_orbit_data(self, time: GPSTime):
    ephems_sp3 = self.download_parse_orbit_data(time)
    if len(ephems_sp3) < 5:
      raise RuntimeError('No orbit data found on either servers')

    self.add_ephems(ephems_sp3, self.orbits)

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
    return None

  def get_sat_info(self, prn, time):
    if get_constellation(prn) not in self.valid_const:
      return None
    eph = None
    if self.pull_orbit:
      eph = self.get_orbit(prn, time)
    if not eph and self.pull_nav:
      eph = self.get_nav(prn, time)

    if eph:
      return eph.get_sat_info(time)
    return None

  def get_all_sat_info(self, time):
    ephs = {}
    if self.pull_orbit:
      ephs = self.get_orbits(time)
    if len(ephs) == 0 and self.pull_nav:
      ephs = self.get_navs(time)

    return {prn: eph.get_sat_info(time) for prn, eph in ephs.items()}

  def get_glonass_channel(self, prn, time):
    nav = self.get_nav(prn, time)
    if nav:
      return nav.channel
    return None

  def get_frequency(self, prn, time, signal='C1C'):
    if get_constellation(prn) == 'GPS':
      switch = {'1': constants.GPS_L1,
                '2': constants.GPS_L2,
                '5': constants.GPS_L5,
                '6': constants.GALILEO_E6,
                '7': constants.GALILEO_E5B,
                '8': constants.GALILEO_E5AB}
      freq = switch.get(signal[1])
      if freq:
        return freq
      raise NotImplementedError("Dont know this GPS frequency: ", signal, prn)
    elif get_constellation(prn) == 'GLONASS':
      n = self.get_glonass_channel(prn, time)
      if n is None:
        return None
      switch = {'1': constants.GLONASS_L1 + n * constants.GLONASS_L1_DELTA,
                '2': constants.GLONASS_L2 + n * constants.GLONASS_L2_DELTA,
                '5': constants.GLONASS_L5 + n * constants.GLONASS_L5_DELTA,
                '6': constants.GALILEO_E6,
                '7': constants.GALILEO_E5B,
                '8': constants.GALILEO_E5AB}
      freq = switch.get(signal[1])
      if freq:
        return freq
      raise NotImplementedError("Dont know this GLONASS frequency: ", signal, prn)

  def get_delay(self, prn, time, rcv_pos, no_dgps=False, signal='C1C', freq=None):
    sat_info = self.get_sat_info(prn, time)
    if sat_info is None:
      return None
    sat_pos = sat_info[0]
    el, az = get_el_az(rcv_pos, sat_pos)
    if el < 0.2:
      return None

    if self.dgps and not no_dgps:
      return self._get_delay_dgps(prn, rcv_pos, time)

    ionex = self.get_ionex(time)
    if not freq and ionex is not None:
      freq = self.get_frequency(prn, time, signal)
    dcb = self.get_dcb(prn, time)
    # When using internet we expect all data or return None
    if self.use_internet and (ionex is None or dcb is None or freq is None):
      return None
    iono_delay = ionex.get_delay(rcv_pos, az, el, sat_pos, time, freq) if ionex is not None else 0.
    trop_delay = saast(rcv_pos, el)
    code_bias = dcb.get_delay(signal) if dcb is not None else 0.
    return iono_delay + trop_delay + code_bias

  def _get_delay_dgps(self, prn, rcv_pos, time):
    dgps_corrections = self.get_dgps_corrections(time, rcv_pos)
    if dgps_corrections is None:
      return None
    return dgps_corrections.get_delay(prn, time)

  def _get_latest_valid_data(self, data, latest_data, download_data_func, time, skip_download=False, recv_pos=None):
    def is_valid(latest_data):
        if recv_pos is None:
          return latest_data is not None and latest_data.valid(time)
        else:
          return latest_data is not None and latest_data.valid(time, recv_pos)
    if is_valid(latest_data):
      return latest_data

    latest_data = get_closest(time, data, recv_pos=recv_pos)
    if is_valid(latest_data):
      return latest_data
    if skip_download or not self.use_internet:
      return None
    if recv_pos is not None:
      download_data_func(time, recv_pos)
    else:
      download_data_func(time)
    latest_data = get_closest(time, data, recv_pos=recv_pos)
    if is_valid(latest_data):
      return latest_data
    return None
