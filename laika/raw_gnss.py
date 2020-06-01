import scipy.optimize as opt
import numpy as np
import datetime
from . import constants
from .lib.coordinates import LocalCoord
from .gps_time import GPSTime
from .helpers import rinex3_obs_from_rinex2_obs, \
                    get_nmea_id_from_prn, \
                    get_prn_from_nmea_id, \
                    get_constellation


def array_from_normal_meas(meas):
  return np.concatenate(([get_nmea_id_from_prn(meas.prn)],
                         [meas.recv_time_week],
                         [meas.recv_time_sec],
                         [meas.glonass_freq],
                         [meas.observables['C1C']],
                         [meas.observables_std['C1C']],
                         [meas.observables['D1C']],
                         [meas.observables_std['D1C']],
                         [meas.observables['S1C']],
                         [meas.observables['L1C']]))


def normal_meas_from_array(arr):
  observables, observables_std = {}, {}
  observables['C1C'] = arr[4]
  observables_std['C1C'] = arr[5]
  observables['D1C'] = arr[6]
  observables_std['D1C'] = arr[7]
  observables['S1C'] = arr[8]
  observables['L1C'] = arr[9]
  return GNSSMeasurement(get_prn_from_nmea_id(arr[0]), arr[1], arr[2],
                         observables, observables_std, arr[3])


class GNSSMeasurement(object):
  PRN = 0
  RECV_TIME_WEEK = 1
  RECV_TIME_SEC = 2
  GLONASS_FREQ = 3

  PR = 4
  PR_STD = 5
  PRR = 6
  PRR_STD = 7

  SAT_POS = slice(8, 11)
  SAT_VEL = slice(11, 14)

  def __init__(self, prn, recv_time_week, recv_time_sec,
               observables, observables_std, glonass_freq=np.nan):

    # Metadata
    self.prn = prn  # sattelite ID in rinex convention
    self.recv_time_week = recv_time_week
    self.recv_time_sec = recv_time_sec
    self.recv_time = GPSTime(recv_time_week, recv_time_sec)
    self.glonass_freq = glonass_freq  # glonass channel

    # Measurements
    self.observables = observables
    self.observables_std = observables_std

    # flags
    self.processed = False
    self.corrected = False

    # sat info
    self.sat_pos = np.nan * np.ones(3)
    self.sat_vel = np.nan * np.ones(3)
    self.sat_clock_err = np.nan

    self.sat_pos_final = np.nan * np.ones(3)  # sat_pos in receiver time's ECEF frame instead of sattelite time's ECEF frame
    self.observables_final = {}

  def process(self, dog):
    sat_time = self.recv_time - self.observables['C1C']/constants.SPEED_OF_LIGHT
    sat_info = dog.get_sat_info(self.prn, sat_time)
    if sat_info is None:
      return False
    else:
      self.sat_pos = sat_info[0]
      self.sat_vel = sat_info[1]
      self.sat_clock_err = sat_info[2]
      self.processed = True
      return True

  def correct(self, est_pos, dog):
    for obs in self.observables:
      if obs[0] == 'C':  # or obs[0] == 'L':
        delay = dog.get_delay(self.prn, self.recv_time, est_pos, signal=obs)
        if delay:
          self.observables_final[obs] = (self.observables[obs] +
                                         self.sat_clock_err*constants.SPEED_OF_LIGHT -
                                         delay)
      else:
        self.observables_final[obs] = self.observables[obs]
    if 'C1C' in self.observables_final and 'C2P' in self.observables_final:
      self.observables_final['IOF'] = (((constants.GPS_L1**2)*self.observables_final['C1C'] -
                                        (constants.GPS_L2**2)*self.observables_final['C2P'])/
                                       (constants.GPS_L1**2 - constants.GPS_L2**2))

    geometric_range = np.linalg.norm(self.sat_pos - est_pos)
    theta_1 = constants.EARTH_ROTATION_RATE*(geometric_range)/constants.SPEED_OF_LIGHT
    self.sat_pos_final = [self.sat_pos[0]*np.cos(theta_1) + self.sat_pos[1]*np.sin(theta_1),
                          self.sat_pos[1]*np.cos(theta_1) - self.sat_pos[0]*np.sin(theta_1),
                          self.sat_pos[2]]
    if 'C1C' in self.observables_final and np.isfinite(self.observables_final['C1C']):
      self.corrected = True
      return True
    else:
      return False

  def as_array(self):
    if not self.corrected:
      raise NotImplementedError('Only corrected measurements can be put into arrays')
    else:
      ret = np.array([get_nmea_id_from_prn(self.prn), self.recv_time_week, self.recv_time_sec, self.glonass_freq,
                    self.observables_final['C1C'], self.observables_std['C1C'],
                    self.observables_final['D1C'], self.observables_std['D1C']])
      ret = np.concatenate((ret, self.sat_pos_final, self.sat_vel))
      return ret


def process_measurements(measurements, dog=None):
  proc_measurements = []
  for meas in measurements:
    if meas.process(dog):
      proc_measurements.append(meas)
  return proc_measurements


def correct_measurements(measurements, est_pos, dog=None):
  corrected_measurements = []
  for meas in measurements:
    if meas.correct(est_pos, dog):
      corrected_measurements.append(meas)
  return corrected_measurements


def group_measurements_by_epoch(measurements):
  meas_filt_by_t = [[measurements[0]]]
  for m in measurements[1:]:
    if abs(m.recv_time - meas_filt_by_t[-1][-1].recv_time) > 1e-9:
      meas_filt_by_t.append([])
    meas_filt_by_t[-1].append(m)
  return meas_filt_by_t


def group_measurements_by_sat(measurements):
  measurements_by_sat = {}
  sats = set([m.prn for m in measurements])
  for sat in sats:
    measurements_by_sat[sat] = [m for m in measurements if m.prn == sat]
  return measurements_by_sat


def read_raw_qcom(report):
  recv_tow = (report.gpsMilliseconds) * 1.0 / 1000.0  # seconds
  recv_week = report.gpsWeek
  recv_time = GPSTime(recv_week, recv_tow)
  measurements = []
  for i in report.sv:
    svId = i.svId
    if not i.measurementStatus.measurementNotUsable and i.measurementStatus.satelliteTimeIsKnown:
      sat_tow = (
        i.unfilteredMeasurementIntegral + i.unfilteredMeasurementFraction) / 1000
      sat_time = GPSTime(recv_week, sat_tow)
      observables, observables_std = {}, {}
      observables['C1C'] = (recv_time - sat_time)*constants.SPEED_OF_LIGHT
      observables_std['C1C'] = i.unfilteredTimeUncertainty * 1e-3 * constants.SPEED_OF_LIGHT
      observables['D1C'] = i.unfilteredSpeed
      observables_std['D1C'] = i.unfilteredSpeedUncertainty
      observables['S1C'] = np.nan
      observables['L1C'] = np.nan
      measurements.append(GNSSMeasurement(get_prn_from_nmea_id(svId),
                                  recv_time.week,
                                  recv_time.tow,
                                  observables,
                                  observables_std))
  return measurements


def read_raw_ublox(report):
  recv_tow = (report.rcvTow)  # seconds
  recv_week = report.gpsWeek
  recv_time = GPSTime(recv_week, recv_tow)
  measurements = []
  for i in report.measurements:
    # only add gps and glonass fixes
    if (i.gnssId == 0 or i.gnssId==6):
      if i.svId > 32 or i.pseudorange > 2**32:
        continue
      if i.gnssId == 0:
        prn = 'G%02i' % i.svId
      else:
        prn = 'R%02i' % i.svId
      observables = {}
      observables_std = {}
      if i.trackingStatus.pseudorangeValid and i.sigId==0:
        observables['C1C'] = i.pseudorange
        # Empirically it seems obvious ublox's std is
        # actually a variation
        observables_std['C1C'] = np.sqrt(i.pseudorangeStdev)*10
        if i.gnssId==6:
          glonass_freq = i.glonassFrequencyIndex - 7
          observables['D1C'] = -(constants.SPEED_OF_LIGHT / (constants.GLONASS_L1 + glonass_freq*constants.GLONASS_L1_DELTA)) * (i.doppler)
        elif i.gnssId==0:
          glonass_freq = np.nan
          observables['D1C'] = -(constants.SPEED_OF_LIGHT / constants.GPS_L1) * (i.doppler)
        observables_std['D1C'] = (constants.SPEED_OF_LIGHT / constants.GPS_L1) * i.dopplerStdev * 1
        observables['S1C'] = i.cno
        if i.trackingStatus.carrierPhaseValid:
          observables['L1C'] = i.carrierCycles
        else:
          observables['L1C'] = np.nan
        measurements.append(GNSSMeasurement(prn,
                                    recv_time.week,
                                    recv_time.tow,
                                    observables,
                                    observables_std,
                                    glonass_freq))
  return measurements


def read_rinex_obs(obsdata):
  measurements = []
  first_sat = list(obsdata.data.keys())[0]
  n = len(obsdata.data[first_sat]['Epochs'])
  for i in range(0, n):
    recv_time_datetime = obsdata.data[first_sat]['Epochs'][i]
    recv_time_datetime = recv_time_datetime.astype(datetime.datetime)
    recv_time = GPSTime.from_datetime(recv_time_datetime)
    measurements.append([])
    for sat_str in list(obsdata.data.keys()):
      if np.isnan(obsdata.data[sat_str]['C1'][i]):
        continue
      observables, observables_std = {}, {}
      for obs in obsdata.data[sat_str]:
        if obs == 'Epochs':
          continue
        observables[rinex3_obs_from_rinex2_obs(obs)] = obsdata.data[sat_str][obs][i]
        observables_std[rinex3_obs_from_rinex2_obs(obs)] = 1
      measurements[-1].append(GNSSMeasurement(get_prn_from_nmea_id(int(sat_str)),
                              recv_time.week,
                              recv_time.tow,
                              observables,
                              observables_std))
  return measurements


def calc_pos_fix(measurements, x0=[0, 0, 0, 0, 0], no_weight=False, signal='C1C'):
  '''
  Calculates gps fix with WLS optimizer

  returns:
  0 -> list with positions
  1 -> pseudorange errs
  '''
  n = len(measurements)
  if n < 6:
      return []

  Fx_pos = pr_residual(measurements, signal=signal, no_weight=no_weight, no_nans=True)
  opt_pos = opt.least_squares(Fx_pos, x0).x
  return opt_pos, Fx_pos(opt_pos, no_weight=True)


def calc_vel_fix(measurements, est_pos, v0=[0, 0, 0, 0], no_weight=False, signal='D1C'):
  '''
  Calculates gps velocity fix with WLS optimizer

  returns:
  0 -> list with velocities
  1 -> pseudorange_rate errs
  '''
  n = len(measurements)
  if n < 6:
      return []

  Fx_vel = prr_residual(measurements, est_pos, no_weight=no_weight, no_nans=True)
  opt_vel = opt.least_squares(Fx_vel, v0).x
  return opt_vel, Fx_vel(opt_vel, no_weight=True)


def pr_residual(measurements, signal='C1C', no_weight=False, no_nans=False):
  # solve for pos
  def Fx_pos(xxx_todo_changeme, no_weight=no_weight):
    (x, y, z, bc, bg) = xxx_todo_changeme
    rows = []

    for meas in measurements:
      if signal in meas.observables_final and np.isfinite(meas.observables_final[signal]):
        pr = meas.observables_final[signal]
        sat_pos = meas.sat_pos_final
        theta = 0
      elif signal in meas.observables and np.isfinite(meas.observables[signal]) and meas.processed:
        pr = meas.observables[signal]
        pr += meas.sat_clock_err * constants.SPEED_OF_LIGHT
        sat_pos = meas.sat_pos
        theta = constants.EARTH_ROTATION_RATE * (pr - bc) / constants.SPEED_OF_LIGHT
      else:
        if not no_nans:
          rows.append(np.nan)
        continue
      if no_weight:
        weight = 1
      else:
        weight = (1 / meas.observables_std[signal])

      if get_constellation(meas.prn) == 'GLONASS':
        rows.append(weight * (np.sqrt(
          (sat_pos[0] * np.cos(theta) + sat_pos[1] * np.sin(theta) - x)**2 +
          (sat_pos[1] * np.cos(theta) - sat_pos[0] * np.sin(theta) - y)**2 +
          (sat_pos[2] - z)**2) - (pr - bc - bg)))
      elif get_constellation(meas.prn) == 'GPS':
        rows.append(weight * (np.sqrt(
          (sat_pos[0] * np.cos(theta) + sat_pos[1] * np.sin(theta) - x)**2 +
          (sat_pos[1] * np.cos(theta) - sat_pos[0] * np.sin(theta) - y)**2 +
          (sat_pos[2] - z)**2) - (pr - bc)))
    return rows
  return Fx_pos


def prr_residual(measurements, est_pos, signal='D1C', no_weight=False, no_nans=False):
  # solve for vel
  def Fx_vel(vel, no_weight=no_weight):
    rows = []
    for meas in measurements:
      if signal not in meas.observables or not np.isfinite(meas.observables[signal]):
        if not no_nans:
          rows.append(np.nan)
        continue
      if meas.corrected:
        sat_pos = meas.sat_pos_final
      else:
        sat_pos = meas.sat_pos
      if no_weight:
        weight = 1
      else:
        weight = (1 / meas.observables[signal])
      los_vector = (sat_pos - est_pos[0:3]
                    ) / np.linalg.norm(sat_pos - est_pos[0:3])
      rows.append(
        weight * ((meas.sat_vel - vel[0:3]).dot(los_vector) -
                  (meas.observables[signal] - vel[3])))
    return rows
  return Fx_vel


def get_Q(recv_pos, sat_positions):
  local = LocalCoord.from_ecef(recv_pos)
  sat_positions_rel = local.ecef2ned(sat_positions)
  sat_distances = np.linalg.norm(sat_positions_rel, axis=1)
  A = np.column_stack((sat_positions_rel[:,0]/sat_distances,  # pylint: disable=unsubscriptable-object
                       sat_positions_rel[:,1]/sat_distances,  # pylint: disable=unsubscriptable-object
                       sat_positions_rel[:,2]/sat_distances,  # pylint: disable=unsubscriptable-object
                       -np.ones(len(sat_distances))))
  if A.shape[0] < 4 or np.linalg.matrix_rank(A) < 4:
    return np.inf*np.ones((4,4))
  else:
    Q = np.linalg.inv(A.T.dot(A))
    return Q


def get_DOP(recv_pos, sat_positions):
  Q = get_Q(recv_pos, sat_positions)
  return np.sqrt(np.trace(Q))


def get_HDOP(recv_pos, sat_positions):
  Q = get_Q(recv_pos, sat_positions)
  return np.sqrt(np.trace(Q[:2,:2]))


def get_VDOP(recv_pos, sat_positions):
  Q = get_Q(recv_pos, sat_positions)
  return np.sqrt(Q[2,2])


def get_TDOP(recv_pos, sat_positions):
  Q = get_Q(recv_pos, sat_positions)
  return np.sqrt(Q[3,3])


def get_PDOP(recv_pos, sat_positions):
  Q = get_Q(recv_pos, sat_positions)
  return np.sqrt(np.trace(Q[:3,:3]))
