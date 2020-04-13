# Import dependencies
import numpy as np
from tqdm import tqdm
from laika import AstroDog
from laika.raw_gnss import assemble_GNSSMeasurement, process_measurements, correct_measurements, calc_pos_fix
import laika.coordinates as coord
from kalman.models.gnss_kf import GNSSKalman
from kalman.kalman_helpers import run_car_ekf_offline, ObservationKind
import gmplot, webbrowser, os

# Constants
CACHE_DIRECTORY = "./cache/"
CACHE_DIRECTORY_SUB = CACHE_DIRECTORY + "cors_coord/"

# Load data
with open('example_data/raw_gnss_ublox/t', 'rb') as f:
    raw_ublox_t = np.load(f)
with open('example_data/raw_gnss_ublox/value', 'rb') as f:
    raw_ublox = np.load(f)
with open('example_data/live_gnss_ublox/t', 'rb') as f:
    fixes_ublox_t = np.load(f)
with open('example_data/live_gnss_ublox/value', 'rb') as f:
    fixes_ublox = np.load(f)

# Convert improved raw data to geodetic format
ublox_positions_geodetic = fixes_ublox[:, [0, 1, 4]]

# Initialize an AstroDog with DGPS correction
print("AstroDog instantiated!")
dog = AstroDog(cache_dir=CACHE_DIRECTORY, dgps=True)

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
est_pos = calc_pos_fix(grouped_meas_processed[0])[0][:3]

# Correct all grouped measurements
corrected_meas_arrays = []
# Log counter
cnt = 0
# Use TQDM progress bar
for proc in tqdm(grouped_meas_processed):
    # Log
    cnt = cnt + 1
    print("Processed measurement", cnt, "of", len(grouped_meas_processed))
    # Return corrected measurement
    corrected = correct_measurements(proc, est_pos, dog)
    # Append corrected results as array to list
    corrected_meas_arrays.append(np.array([c.as_array() for c in corrected]))

# Log
print("Raw position data successfully processed.\n")

# Instantiate extended Kalman filter object
ekf = GNSSKalman()
# Get init state
init_state = ekf.x
# Get estimated position for initial state
init_state[:3] = est_pos
# Set init state to init state of EKF object
ekf.init_state(init_state)

# Init empty EKF data
ekf_data = {}
# Fill EKF data with pseudo-range and pseudo-range rate from GPS measurements
ekf_data[ObservationKind.PSEUDORANGE_GPS] = (grouped_t, corrected_meas_arrays)
ekf_data[ObservationKind.PSEUDORANGE_RATE_GPS] = (grouped_t, corrected_meas_arrays)

# Run EKF based on an offline car model
ekf_outputs = run_car_ekf_offline(ekf, ekf_data)
# Get estimated position from EKF
laika_positions_t = ekf_outputs[4]
laika_positions_ecef = ekf_outputs[0][:, :3]
# Convert position from ECEF to geodetic format
laika_positions_geodetic = coord.ecef2geodetic(laika_positions_ecef)

# Plot geodetic position on Google Maps
gmap = gmplot.GoogleMapPlotter(*laika_positions_geodetic[0])
# Plot position from EKF output and improved raw position, both in geodetic format
gmap.plot([x[0] for x in laika_positions_geodetic], [x[1] for x in laika_positions_geodetic], 'blue', edge_width=5)
gmap.plot([x[0] for x in ublox_positions_geodetic], [x[1] for x in ublox_positions_geodetic], 'red', edge_width=5)

# Save plots in HTML file
gmap.draw("laika_quality_check.html")
# Open HTML file with plots
webbrowser.open('file://' + os.path.realpath("laika_quality_check.html"))