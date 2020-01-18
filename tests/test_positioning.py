import numpy as np
import seaborn as sns
from tqdm import tqdm
from laika.lib.coordinates import LocalCoord, ecef2geodetic
from laika import AstroDog
from shutil import copyfile
import os
from datetime import datetime
from laika.gps_time import GPSTime
from laika.downloader import download_cors_station
from laika.rinex_file import RINEXFile
from laika.dgps import get_station_position
import laika.raw_gnss as raw
from laika.helpers import get_constellation

import matplotlib.pyplot as plt


# A practical way to confirm the accuracy of laika's processing
# is by downloading some observation data from a CORS station
# and confirming our position estimate to the known position
# of the station.
# We begin by initializing an AstroDog
dog = AstroDog()

# Building this cache takes forever just copy it from repo
cache_directory = '/tmp/gnss/cors_coord/'
try:
  os.mkdir('/tmp/gnss/')
except:
  pass
try:
  os.mkdir(cache_directory)
except:
  pass
copyfile('cors_station_positions', cache_directory + 'cors_station_positions')


# We can use helper functions in laika to download  the station's observation
# data for a certain time and its known exact position.
# Todo: Handle hatakana compressed files more gracefully
station_name = 'sc01'
time = GPSTime.from_datetime(datetime(2020, 1, 11))
slac_rinex_obs_file = download_cors_station(time, station_name, dog.cache_dir)
obs_data = RINEXFile(slac_rinex_obs_file)
slac_exact_postition = get_station_position('sc01')


# Now we have the observation data for the station we can process
# it with the astrodog.

rinex_meas_grouped = raw.read_rinex_obs(obs_data)
rinex_corr_grouped = []
# print(rinex_meas_grouped)
for meas in tqdm(rinex_meas_grouped):
  proc = raw.process_measurements(meas, dog=dog)
  corr = raw.correct_measurements(meas, slac_exact_postition, dog=dog)
  rinex_corr_grouped.append(corr)

# Using laika's WLS solver we can now calculate position
# fixes for every epoch (every 30s) over 24h.

ests = []
for corr in tqdm(rinex_corr_grouped[:]):
  # print("Corr: ")
  # print
  fix, _ = raw.calc_pos_fix(corr)
  ests.append(fix)
ests = np.array(ests)

# Now we plot the error of every fix in NED (North, East, Down)
# coordinates, we see clearly that the Down axis is noisier,
# this is to be expected as the VDOP is generally much larger
# than the HDOP.

conv = LocalCoord.from_ecef(slac_exact_postition)
print(slac_exact_postition)
print(fix)
errors_ned = conv.ecef2ned(ests[:,:3])

print(errors_ned)


# figsize(10,10)

# title('Error of estation estimated by C1C signal', fontsize=25);
# ylim(-10,10);
# xlabel('Epoch (#)', fontsize=15);
# ylabel('Error (m)', fontsize=15);
# legend(fontsize=15);


# The error of the median position compared to the true
# position is ~0.5m with this technique. This is about what
# we would expect. Without using carrier phase measurements
# we do not expect better results.
#
# plt.plot(errors_ned[:,2], label='Down');
# plt.plot(errors_ned[:,1], label='East');
# plt.plot(errors_ned[:,0], label='North');
# print('The error of the median position is NED:')
# print(np.median(errors_ned, axis=0))

