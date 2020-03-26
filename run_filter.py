# Import dependencies
import numpy as np
from tqdm import tqdm
from laika import AstroDog
from laika.raw_gnss import assemble_GNSSMeasurement, process_measurements, correct_measurements, calc_pos_fix

# Constants
CACHE_DIRECTORY = '/tmp/gnss/'
CACHE_DIRECTORY_SUB = '/tmp/gnss/cors_coord/'

# Load data
with open('example_data/raw_gnss_ublox/t', 'rb') as f:
    raw_ublox_t = np.load(f)
with open('example_data/raw_gnss_ublox/value', 'rb') as f:
    raw_ublox = np.load(f)
with open('example_data/live_gnss_ublox/t', 'rb') as f:
    fixes_ublox_t = np.load(f)
with open('example_data/live_gnss_ublox/value', 'rb') as f:
    fixes_ublox = np.load(f)

# Initialize an AstroDog with DGPS correction
print("AstroDog instantiated!")
dog = AstroDog(dgps=True)

# Group measurements by measurement epoch (to make Kalman filter faster)
# Get unique timestamps from measurement data, return as sorted list
grouped_t = sorted(list(set(raw_ublox_t)))
print("Number of grouped measurements:", len(grouped_t), '\n')

# Get measurements from data as NumPy array GNSS measurements
measurements = np.array([assemble_GNSSMeasurement(measurement_values_set) for measurement_values_set in raw_ublox])

# Create process measurement group
grouped_meas_processed, cnt = [], 0
for t in grouped_t:
    # Increase counter
    cnt = cnt + 1
    # Log
    print(cnt, "of", len(grouped_t), "| Timestamp", t)
    # Get measurement data list index for current timestamp according to raw_ublox_t
    meas = measurements[raw_ublox_t == t]
    # Process measurements corresponding to current timestamp, append them to list of measurement groups
    grouped_meas_processed.append(process_measurements(meas, dog))

# Correct measurement groups with an estimate position (weighted-least-squares)
wls_estimate = calc_pos_fix(grouped_meas_processed[0])
est_pos = wls_estimate[0][:3]
# Log
print('\n', "Initially estimated position:", est_pos)

# Correct all grouped measurements
corrected_meas_arrays = []
# Use TQDM progress bar
for proc in tqdm(grouped_meas_processed):
    # Return corrected measurement
    corrected = correct_measurements(proc, est_pos, dog)
    # Append corrected results as array to list
    corrected_meas_arrays.append(np.array([c.as_array() for c in corrected]))