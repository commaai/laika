import numpy as np
from datetime import datetime
from math import sin, cos, sqrt, fabs, atan2

from .gps_time import GPSTime, utc_to_gpst
from .constants import SPEED_OF_LIGHT, SECS_IN_MIN, SECS_IN_HR, SECS_IN_DAY, EARTH_ROTATION_RATE, EARTH_GM
from .helpers import get_constellation


def read4(f, rinex_ver):
  line = f.readline()[:-1]
  if rinex_ver == 2:
    line = ' ' + line  # Shift 1 char to the right
  line = line.replace('D', 'E')  # Handle bizarro float format
  return float(line[4:23]), float(line[23:42]), float(line[42:61]), float(line[61:80])


def convert_ublox_ephem(ublox_ephem):
  ephem = {}
  if ublox_ephem.gpsWeek < 1024:
    week = ublox_ephem.gpsWeek + 1024
  else:
    week = ublox_ephem.gpsWeek
  ephem['toe'] = GPSTime(week, ublox_ephem.toe)
  ephem['toc'] = GPSTime(week, ublox_ephem.toc)
  ephem['af0'] = ublox_ephem.af0
  ephem['af1'] = ublox_ephem.af1
  ephem['af2'] = ublox_ephem.af2
  ephem['tgd'] = ublox_ephem.tgd

  ephem['sqrta'] = np.sqrt(ublox_ephem.a)
  ephem['dn'] = ublox_ephem.deltaN
  ephem['m0'] = ublox_ephem.m0

  ephem['ecc'] = ublox_ephem.ecc
  ephem['w'] = ublox_ephem.omega
  ephem['cus'] = ublox_ephem.cus
  ephem['cuc'] = ublox_ephem.cuc
  ephem['crc'] = ublox_ephem.crc
  ephem['crs'] = ublox_ephem.crs
  ephem['cic'] = ublox_ephem.cic
  ephem['cis'] = ublox_ephem.cis

  ephem['inc'] = ublox_ephem.i0
  ephem['inc_dot'] = ublox_ephem.iDot
  ephem['omegadot'] = ublox_ephem.omegaDot
  ephem['omega0'] = ublox_ephem.omega0

  return ephem


class EphemerisType:
  # TODO this isn't properly supported
  NAV = 0
  FINAL_ORBIT = 1
  RAPID_ORBIT = 2
  ULTRA_RAPID_ORBIT = 3
  QCOM_POLY = 4


class Ephemeris:
  def valid(self, time):
    # TODO: use proper abstract base class to define members
    return abs(time - self.epoch) <= self.max_time_diff  # pylint: disable=no-member


class GLONASSEphemeris(Ephemeris):
  def __init__(self, data, epoch, healthy=True):
    self.prn = data['prn']
    self.epoch = epoch
    self.healthy = healthy
    self.data = data
    self.max_time_diff = 25*SECS_IN_MIN
    self.type = EphemerisType.NAV
    self.channel = data['freq_num']

  def get_sat_info(self, time):
    if not self.healthy:
      return None
    # see the russian doc for this:
    # http://gauss.gge.unb.ca/GLONASS.ICD.pdf

    eph = self.data
    # TODO should handle leap seconds better
    toc_gps_time = utc_to_gpst(eph['toc'])
    tdiff = time - toc_gps_time

    # Clock correction (except for general relativity which is applied later)
    clock_err = eph['min_tauN'] + tdiff * (eph['GammaN'])
    clock_rate_err = eph['GammaN']

    def glonass_diff_eq(state, acc):
      J2 = 1.0826257e-3
      mu = 3.9860044e14
      omega = 7.292115e-5
      ae = 6378136.0
      r = np.sqrt(state[0]**2 + state[1]**2 + state[2]**2)
      ders = np.zeros(6)
      if r**2 < 0:
        return ders
      a = 1.5 * J2 * mu * (ae**2)/ (r**5)
      b = 5 * (state[2]**2) / (r**2)
      c = -mu/(r**3) - a*(1-b)

      ders[0:3] = state[3:6]
      ders[3] = (c + omega**2)*state[0] + 2*omega*state[4] + acc[0]
      ders[4] = (c + omega**2)*state[1] - 2*omega*state[3] + acc[1]
      ders[5] = (c - 2*a)*state[2] + acc[2]
      return ders

    init_state = np.empty(6)
    init_state[0] = eph['x']
    init_state[1] = eph['y']
    init_state[2] = eph['z']
    init_state[3] = eph['x_vel']
    init_state[4] = eph['y_vel']
    init_state[5] = eph['z_vel']
    init_state = 1000*init_state
    acc = 1000*np.array([eph['x_acc'], eph['y_acc'], eph['z_acc']])
    state = init_state
    tstep = 90
    if tdiff < 0:
      tt = -tstep
    elif tdiff > 0:
      tt = tstep
    while abs(tdiff) > 1e-9:
      if abs(tdiff) < tstep:
        tt = tdiff
      k1 = glonass_diff_eq(state, acc)
      k2 = glonass_diff_eq(state + k1*tt/2, -acc)
      k3 = glonass_diff_eq(state + k2*tt/2, -acc)
      k4 = glonass_diff_eq(state + k3*tt, -acc)
      state += (k1 + 2*k2 + 2*k3 + k4)*tt/6.0
      tdiff -= tt

    pos = state[0:3]
    vel = state[3:6]
    return pos, vel, clock_err, clock_rate_err


class PolyEphemeris(Ephemeris):
  def __init__(self, prn, data, epoch, healthy=True, eph_type=None, tgd=0):
    self.prn = prn
    self.epoch = epoch
    self.healthy = healthy
    self.data = data
    self.tgd = tgd
    self.max_time_diff = SECS_IN_HR
    self.type = eph_type

  def get_sat_info(self, time):
    if not self.healthy:
      return None
    dt = time - self.data['t0']
    deg = self.data['deg']
    deg_t = self.data['deg_t']
    sat_pos = np.array([sum((dt**p)*self.data['x'][deg-p] for p in range(deg+1)),
                        sum((dt**p)*self.data['y'][deg-p] for p in range(deg+1)),
                        sum((dt**p)*self.data['z'][deg-p] for p in range(deg+1))])
    sat_vel = np.array([sum(p*(dt**(p-1))*self.data['x'][deg-p] for p in range(1,deg+1)),
                        sum(p*(dt**(p-1))*self.data['y'][deg-p] for p in range(1,deg+1)),
                        sum(p*(dt**(p-1))*self.data['z'][deg-p] for p in range(1,deg+1))])
    time_err = sum((dt**p)*self.data['clock'][deg_t-p] for p in range(deg_t+1))
    time_err_rate = sum(p*(dt**(p-1))*self.data['clock'][deg_t-p] for p in range(1,deg_t+1))
    time_err_with_rel = time_err - 2*np.inner(sat_pos, sat_vel)/SPEED_OF_LIGHT**2
    return sat_pos, sat_vel, time_err_with_rel, time_err_rate


class GPSEphemeris(Ephemeris):
  def __init__(self, data, epoch, healthy=True):
    self.prn = 'G%02i' % data['prn']
    self.epoch = epoch
    self.healthy = healthy
    self.data = data
    self.max_time_diff = 2*SECS_IN_HR
    self.max_time_diff_tgd = SECS_IN_DAY
    self.type = EphemerisType.NAV

  def get_tgd(self):
    return self.data['tgd']

  def get_sat_info(self, time):
    if not self.healthy:
      return None
    eph = self.data
    tdiff = time - eph['toc']  # Time of clock
    clock_err = eph['af0'] + tdiff * (eph['af1'] + tdiff * eph['af2'])
    clock_rate_err = eph['af1'] + 2 * tdiff * eph['af2']

    # Orbit propagation
    tdiff = time - eph['toe']  # Time of ephemeris (might be different from time of clock)

    # Calculate position per IS-GPS-200D p 97 Table 20-IV
    a = eph['sqrta'] * eph['sqrta']  # [m] Semi-major axis
    ma_dot = sqrt(EARTH_GM / (a * a * a)) + eph['dn']  # [rad/sec] Corrected mean motion
    ma = eph['m0'] + ma_dot * tdiff  # [rad] Corrected mean anomaly

    # Iteratively solve for the Eccentric Anomaly (from Keith Alter and David Johnston)
    ea = ma  # Starting value for E

    ea_old = 2222
    while fabs(ea - ea_old) > 1.0E-14:
      ea_old = ea
      tempd1 = 1.0 - eph['ecc'] * cos(ea_old)
      ea = ea + (ma - ea_old + eph['ecc'] * sin(ea_old)) / tempd1
    ea_dot = ma_dot / tempd1

    # Relativistic correction term
    einstein = -4.442807633E-10 * eph['ecc'] * eph['sqrta'] * sin(ea)

    # Begin calc for True Anomaly and Argument of Latitude
    tempd2 = sqrt(1.0 - eph['ecc'] * eph['ecc'])
    # [rad] Argument of Latitude = True Anomaly + Argument of Perigee
    al = atan2(tempd2 * sin(ea), cos(ea) - eph['ecc']) + eph['w']
    al_dot = tempd2 * ea_dot / tempd1

    # Calculate corrected argument of latitude based on position
    cal = al + eph['cus'] * sin(2.0 * al) + eph['cuc'] * cos(2.0 * al)
    cal_dot = al_dot * (1.0 + 2.0 * (eph['cus'] * cos(2.0 * al) -
                                     eph['cuc'] * sin(2.0 * al)))

    # Calculate corrected radius based on argument of latitude
    r = a * tempd1 + eph['crc'] * cos(2.0 * al) + eph['crs'] * sin(2.0 * al)
    r_dot = (a * eph['ecc'] * sin(ea) * ea_dot +
             2.0 * al_dot * (eph['crs'] * cos(2.0 * al) -
                             eph['crc'] * sin(2.0 * al)))

    # Calculate inclination based on argument of latitude
    inc = (eph['inc'] + eph['inc_dot'] * tdiff +
           eph['cic'] * cos(2.0 * al) +
           eph['cis'] * sin(2.0 * al))
    inc_dot = (eph['inc_dot'] +
               2.0 * al_dot * (eph['cis'] * cos(2.0 * al) -
                               eph['cic'] * sin(2.0 * al)))

    # Calculate position and velocity in orbital plane
    x = r * cos(cal)
    y = r * sin(cal)
    x_dot = r_dot * cos(cal) - y * cal_dot
    y_dot = r_dot * sin(cal) + x * cal_dot

    # Corrected longitude of ascending node
    om_dot = eph['omegadot'] - EARTH_ROTATION_RATE
    om = eph['omega0'] + tdiff * om_dot - EARTH_ROTATION_RATE * eph['toe'].tow

    # Compute the satellite's position in Earth-Centered Earth-Fixed coordinates
    pos = np.empty(3)
    pos[0] = x * cos(om) - y * cos(inc) * sin(om)
    pos[1] = x * sin(om) + y * cos(inc) * cos(om)
    pos[2] = y * sin(inc)

    tempd3 = y_dot * cos(inc) - y * sin(inc) * inc_dot

    # Compute the satellite's velocity in Earth-Centered Earth-Fixed coordinates
    vel = np.empty(3)
    vel[0] = -om_dot * pos[1] + x_dot * cos(om) - tempd3 * sin(om)
    vel[1] = om_dot * pos[0] + x_dot * sin(om) + tempd3 * cos(om)
    vel[2] = y * cos(inc) * inc_dot + y_dot * sin(inc)

    clock_err += einstein

    return pos, vel, clock_err, clock_rate_err


def parse_sp3_orbits(file_names, SUPPORTED_CONSTELLATIONS):
  ephems = []
  data = {}
  for file_name in file_names:
    f = open(file_name)
    while True:
      line = f.readline()[:-1]
      if not line:
        break
      # epoch header
      if line[0:2] == '* ':
        year = int(line[3:7])
        month = int(line[8:10])
        day = int(line[11:13])
        hour = int(line[14:16])
        minute = int(line[17:19])
        second = int(float(line[20:31]))
        epoch = GPSTime.from_datetime(datetime(year, month, day, hour, minute, second))
      # pos line
      elif line[0] == 'P':
        prn = line[1:4].replace(' ','0')
        # In old SP3 files vehicle ID doesn't contain constellation
        # identifier. We assume that constellation is GPS when missing.
        if prn[0] == '0':
          prn = 'G' + prn[1:]
        if get_constellation(prn) not in SUPPORTED_CONSTELLATIONS:
          continue
        if prn not in data:
          data[prn] = []
        #TODO this is a crappy way to deal with overlapping ultra rapid
        if len(data[prn]) < 1 or epoch - data[prn][-1][0] > 0:
          parsed = [epoch,
                    1e3*float(line[4:18]),
                    1e3*float(line[18:32]),
                    1e3*float(line[32:46]),
                    1e-6*float(line[46:60])]
          if (np.array(parsed[1:]) != 0).all():
            data[prn].append(parsed)
    f.close()
  deg = 16
  deg_t = 1
  for prn in data:
    # TODO Handle this properly
    # Currently don't even bother with satellites that have unhealthy times
    if (np.array(data[prn])[:,4] > .99).any():
      continue
    for i in range(len(data[prn]) - deg):
      times, x, y, z, clock = [],[],[],[],[]
      epoch = data[prn][i + deg//2][0]
      for j in range(deg + 1):
        times.append(data[prn][i + j][0] - epoch)
        x.append(data[prn][i + j][1])
        y.append(data[prn][i + j][2])
        z.append(data[prn][i + j][3])
        clock.append(data[prn][i + j][4])
      if (np.diff(times) != 900).any():
        continue
      poly_data = {}
      poly_data['t0'] = epoch
      poly_data['x'] = np.polyfit(times, x, deg)
      poly_data['y'] = np.polyfit(times, y, deg)
      poly_data['z'] = np.polyfit(times, z, deg)
      poly_data['clock'] = [(data[prn][i + deg//2 + 1][4] - data[prn][i + deg//2 - 1][4])/1800, data[prn][i + deg//2][4]]
      poly_data['deg'] = deg
      poly_data['deg_t'] = deg_t
      ephems.append(PolyEphemeris(prn, poly_data, epoch, healthy=True, eph_type=EphemerisType.RAPID_ORBIT))
  return ephems


def parse_rinex_nav_msg_gps(file_name):
  ephems = []
  got_header = False
  rinex_ver = None
  #ion_alpha = None
  #ion_beta = None
  f = open(file_name)
  while True:
    line = f.readline()[:-1]
    if not line:
      break
    if not got_header:
      if rinex_ver is None:
        if line[60:80] != "RINEX VERSION / TYPE":
          raise RuntimeError("Doesn't appear to be a RINEX file")
        rinex_ver = int(float(line[0:9]))
        if line[20] != "N":
          raise RuntimeError("Doesn't appear to be a Navigation Message file")
      #if line[60:69] == "ION ALPHA":
      #  line = line.replace('D', 'E')  # Handle bizarro float format
      #  ion_alpha= [float(line[3:14]), float(line[15:26]), float(line[27:38]), float(line[39:50])]
      #if line[60:68] == "ION BETA":
      #  line = line.replace('D', 'E')  # Handle bizarro float format
      #  ion_beta= [float(line[3:14]), float(line[15:26]), float(line[27:38]), float(line[39:50])]
      if line[60:73] == "END OF HEADER":
        #ion = ion_alpha + ion_beta
        got_header = True
      continue
    if rinex_ver == 3:
      if line[0] != 'G':
        continue
    if rinex_ver == 3:
      prn = int(line[1:3])
      epoch = GPSTime.from_datetime(datetime.strptime(line[4:23], "%y %m %d %H %M %S"))
    elif rinex_ver == 2:
      prn = int(line[0:2])
      # 2000 year is in RINEX file as 0, but Python requires two digit year: 00
      epoch_str = line[3:20]
      if epoch_str[0] == ' ':
        epoch_str = '0' + epoch_str[1:]
      epoch = GPSTime.from_datetime(datetime.strptime(epoch_str, "%y %m %d %H %M %S"))
      line = ' ' + line  # Shift 1 char to the right

    line = line.replace('D', 'E')  # Handle bizarro float format
    e = {'epoch': epoch, 'prn': prn}
    e['toc'] = epoch
    e['af0'] = float(line[23:42])
    e['af1'] = float(line[42:61])
    e['af2'] = float(line[61:80])

    e['iode'], e['crs'], e['dn'], e['m0'] = read4(f, rinex_ver)
    e['cuc'], e['ecc'], e['cus'], e['sqrta'] = read4(f, rinex_ver)
    toe_tow, e['cic'], e['omega0'], e['cis'] = read4(f, rinex_ver)
    e['inc'], e['crc'], e['w'], e['omegadot'] = read4(f, rinex_ver)
    e['inc_dot'], e['l2_codes'], toe_week, e['l2_pflag'] = read4(f, rinex_ver)
    e['sv_accuracy'], e['health'], e['tgd'], e['iodc'] = read4(f, rinex_ver)
    f.readline()  # Discard last row

    e['toe'] = GPSTime(toe_week, toe_tow)
    e['healthy'] = (e['health'] == 0.0)

    ephems.append(GPSEphemeris(e, epoch))
  f.close()
  return ephems


def parse_rinex_nav_msg_glonass(file_name):
  ephems = []
  f = open(file_name)
  got_header = False
  rinex_ver = None
  while True:
    line = f.readline()[:-1]
    if not line:
      break
    if not got_header:
      if rinex_ver is None:
        if line[60:80] != "RINEX VERSION / TYPE":
          raise RuntimeError("Doesn't appear to be a RINEX file")
        rinex_ver = int(float(line[0:9]))
        if line[20] != "G":
          raise RuntimeError("Doesn't appear to be a Navigation Message file")
      if line[60:73] == "END OF HEADER":
        got_header = True
      continue
    if rinex_ver == 3:
      prn = line[:3]
      epoch = GPSTime.from_datetime(datetime.strptime(line[4:23], "%y %m %d %H %M %S"))
    elif rinex_ver == 2:
      prn = 'R%02i' % int(line[0:2])
      epoch = GPSTime.from_datetime(datetime.strptime(line[3:20], "%y %m %d %H %M %S"))
      line = ' ' + line  # Shift 1 char to the right

    line = line.replace('D', 'E')  # Handle bizarro float format
    e = {'epoch': epoch, 'prn': prn}
    e['toc'] = epoch
    e['min_tauN'] = float(line[23:42])
    e['GammaN'] = float(line[42:61])
    e['tk'] = float(line[61:80])

    e['x'], e['x_vel'], e['x_acc'], e['health'] = read4(f, rinex_ver)
    e['y'], e['y_vel'], e['y_acc'], e['freq_num'] = read4(f, rinex_ver)
    e['z'], e['z_vel'], e['z_acc'], e['age'] = read4(f, rinex_ver)

    e['healthy'] = (e['health'] == 0.0)

    ephems.append(GLONASSEphemeris(e, epoch))
  f.close()
  return ephems


'''
def parse_ublox_ephems(ublox_ephems):
  ephems = []
  for ublox_ephem in ublox_ephems:
    svId = ublox_ephem.ubloxGnss.ephemeris.svId
    data = convert_ublox_ephem(ublox_ephem.ubloxGnss.ephemeris)
    epoch = data['toe']
    ephems.append(GPSEphemeris(svId, data, epoch))
  return ephems


def parse_qcom_ephems(qcom_polys, current_week):
  ephems = []
  for qcom_poly in qcom_polys:
    svId = qcom_poly.qcomGnss.drSvPoly.svId
    data = qcom_poly.qcomGnss.drSvPoly
    t0 = data.t0
    # fix glonass time
    if get_constellation(svId) == 'GLONASS':
      # TODO should handle leap seconds better
      epoch = GPSTime(current_week, (t0 + 3*SECS_IN_WEEK) % (SECS_IN_WEEK) + 18)
    else:
      epoch = GPSTime(current_week, t0)
    poly_data = {}
    poly_data['t0'] = epoch
    poly_data['x'] = [data.xyzN[2], data.xyzN[1], data.xyzN[0], data.xyz0[0]]
    poly_data['y'] = [data.xyzN[5], data.xyzN[4], data.xyzN[3], data.xyz0[1]]
    poly_data['z'] = [data.xyzN[8], data.xyzN[7], data.xyzN[6], data.xyz0[2]]
    poly_data['clock'] = [1e-3*data.other[3], 1e-3*data.other[2], 1e-3*data.other[1], 1e-3*data.other[0]]
    poly_data['deg'] = 3
    poly_data['deg_t'] = 3
    ephems.append(PolyEphemeris(svId, poly_data, epoch, eph_type=EphemerisType.QCOM_POLY))
  return ephems
'''
