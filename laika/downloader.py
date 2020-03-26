# Import dependencies
import gzip
import os
import urllib.request
from datetime import datetime
from .constants import SECS_IN_DAY, SECS_IN_WEEK
from .gps_time import GPSTime
from .unlzw import unlzw

# Download file function
def download_file(url_base, folder_path, cacheDir, filename, compression='', overwrite=False):
    # Assemble absolute folder path
    folder_path_abs = os.path.join(cacheDir, folder_path)
    # Define .zip filename
    filename_zipped = filename + compression
    # Assemble absolute file path
    filepath = os.path.join(folder_path_abs, filename)
    # Assemble absolute .zip file path
    filepath_zipped = os.path.join(folder_path_abs, filename_zipped)
    # Assemble URL from base URL, folder path and .zip filename
    url = url_base + folder_path + filename_zipped
    # Log
    print("\nDownloader | URL is", url)
    # If file path is in use and overwriting was not enabled, print log
    if os.path.isfile(filepath) and not overwrite:
        # Log
        print("Downloader | File path is in use and overwriting is not enabled. Using Cache...")
    # If file path is not used yet or overwriting is allowed, continue
    else:
        # Log
        print("Downloader | Cache cannot/shall not be used. Downloading...")
        # If file path does not exist, create it
        if not os.path.exists(folder_path_abs):
            os.makedirs(folder_path_abs)
        # Log
        print("Downloader | Pulling from", url, "to", filepath)
        # Try to download file
        try:
            # Open URL
            urlf = urllib.request.urlopen(url)
        # If URL is not reachable or file was not found, raise error
        except IOError as e:
            raise IOError("Could not download file from " + url + "!")
        # Read data from URL
        data_zipped = urlf.read()
        urlf.close()
        # Write .zip file to path
        with open(filepath_zipped, 'wb') as wf:
            wf.write(data_zipped)
        # If compressed, decompess - else, return file path
        if compression == '':
            return filepath_zipped
        elif compression == '.gz':
            f = gzip.open(filepath_zipped, 'rb')
            uncompressed_data = f.read()
            f .close()
        elif compression == '.Z':
            f = open(filepath_zipped, 'rb')
            compressed_data = f.read()
            uncompressed_data = unlzw(compressed_data)
            f.close()
        else:
            # If compression is unknown, raise error
            raise NotImplementedError('Unknown compression: ', compression)
        # In case of compressed data, open data
        f = open(filepath, 'wb')
        # Store decompressed data
        f.write(uncompressed_data)
        f.close()
    # Return file path
    return filepath


def download_nav(time, cache_dir, constellation='GPS'):
    t = time.as_datetime()
    try:
        if GPSTime.from_datetime(datetime.utcnow()) - time > SECS_IN_DAY:
            url_base = 'ftp://cddis.gsfc.nasa.gov/gnss/data/daily/'
            cache_subdir = cache_dir + 'daily_nav/'
            if constellation =='GPS':
                filename = t.strftime("brdc%j0.%yn")
                folder_path = t.strftime('%Y/%j/%yn/')
            elif constellation =='GLONASS':
                filename = t.strftime("brdc%j0.%yg")
                folder_path = t.strftime('%Y/%j/%yg/')
            return download_file(url_base, folder_path, cache_subdir, filename, compression='.Z')
        else:
            url_base = 'ftp://cddis.gsfc.nasa.gov/gnss/data/hourly/'
            cache_subdir = cache_dir + 'hourly_nav/'
            if constellation =='GPS':
                filename = t.strftime("hour%j0.%yn")
                folder_path = t.strftime('%Y/%j/')
                return download_file(url_base, folder_path, cache_subdir, filename, compression='.Z', overwrite=True)
    except IOError:
        pass


def download_orbits(time, cache_dir):
    cache_subdir = cache_dir + 'cddis_products/'
    url_base = 'ftp://cddis.gsfc.nasa.gov/gnss/products/'
    downloaded_files = []
    for time in [time - SECS_IN_DAY, time, time + SECS_IN_DAY]:
        folder_path = "%i/" % (time.week)
        if GPSTime.from_datetime(datetime.utcnow()) - time > 3*SECS_IN_WEEK:
            try:
                filename = "igs%i%i.sp3" % (time.week, time.day)
                downloaded_files.append(download_file(url_base, folder_path, cache_subdir, filename, compression='.Z'))
                continue
            except IOError:
                pass
        try:
            filename = "igr%i%i.sp3" % (time.week, time.day)
            downloaded_files.append(download_file(url_base, folder_path, cache_subdir, filename, compression='.Z'))
            continue
        except IOError:
            pass
        try:
            filename = "igu%i%i_18.sp3" % (time.week, time.day)
            downloaded_files.append(download_file(url_base, folder_path, cache_subdir, filename, compression='.Z'))
            continue
        except IOError:
            pass
        try:
            filename = "igu%i%i_12.sp3" % (time.week, time.day)
            downloaded_files.append(download_file(url_base, folder_path, cache_subdir, filename, compression='.Z'))
            continue
        except IOError:
            pass
        try:
            filename = "igu%i%i_06.sp3" % (time.week, time.day)
            downloaded_files.append(download_file(url_base, folder_path, cache_subdir, filename, compression='.Z'))
            continue
        except IOError:
            pass
        try:
            filename = "igu%i%i_00.sp3" % (time.week, time.day)
            downloaded_files.append(download_file(url_base, folder_path, cache_subdir, filename, compression='.Z'))
            continue
        except IOError:
            pass
    return downloaded_files


def download_orbits_russia(time, cache_dir):
    cache_subdir = cache_dir + 'russian_products/'
    url_base = 'ftp://ftp.glonass-iac.ru/MCC/PRODUCTS/'
    downloaded_files = []
    for time in [time - SECS_IN_DAY, time, time + SECS_IN_DAY]:
        t = time.as_datetime()
        if GPSTime.from_datetime(datetime.utcnow()) - time > 2*SECS_IN_WEEK:
            try:
                folder_path = t.strftime('%y%j/final/')
                filename = "Sta%i%i.sp3" % (time.week, time.day)
                downloaded_files.append(download_file(url_base, folder_path, cache_subdir, filename))
                continue
            except IOError:
                pass
        try:
            folder_path = t.strftime('%y%j/rapid/')
            filename = "Sta%i%i.sp3" % (time.week, time.day)
            downloaded_files.append(download_file(url_base, folder_path, cache_subdir, filename))
        except IOError:
            pass
        try:
            folder_path = t.strftime('%y%j/ultra/')
            filename = "Sta%i%i.sp3" % (time.week, time.day)
            downloaded_files.append(download_file(url_base, folder_path, cache_subdir, filename))
        except IOError:
            pass
    return downloaded_files

# Download daily ionospheric fluctuation maps in IONEX format function
def download_ionex(time, cache_dir):
    cache_subdir = cache_dir + 'ionex/'
    t = time.as_datetime()
    url_base = 'ftp://cddis.gsfc.nasa.gov/gnss/products/ionex/'
    folder_path = t.strftime('%Y/%j/')
    for filename in [t.strftime("codg%j0.%yi"), t.strftime("c1pg%j0.%yi"), t.strftime("c2pg%j0.%yi")]:
        try:
            filepath = download_file(url_base, folder_path, cache_subdir, filename, compression='.Z')
            return filepath
        except IOError as e:
            last_err = e
    raise last_err


def download_dcb(time, cache_dir):
    cache_subdir = cache_dir + 'dcb/'
    # Use time range of 14 days/2 weeks
    for time in [time - i*SECS_IN_DAY for i in range(14)]:
        try:
            t = time.as_datetime()
            url_base = 'ftp://cddis.nasa.gov/gnss/products/bias/'
            folder_path = t.strftime('%Y/')
            filename = t.strftime("CAS0MGXRAP_%Y%j0000_01D_01D_DCB.BSX")
            filepath = download_file(url_base, folder_path, cache_subdir, filename, compression='.gz')
            return filepath
        except IOError as e:
            last_err = e
    raise last_err


# Download coordinates of Continuously Operating Reference Station (CORS) function
def download_cors_coords(cache_dir):
    cache_subdir = cache_dir + 'cors_coord/'
    url_base = 'ftp://geodesy.noaa.gov/cors/coord/coord_08/'
    url_path = urllib.request.urlopen(url_base)
    file_names = [file_string.split()[-1] for file_string in str(url_path.read()).split('\\r\\n') if len(file_string) > 5]
    file_names = [file_name for file_name in file_names if file_name[-9:] == 'coord.txt']
    filepaths = []
    for file_name in file_names:
        filepaths.append(download_file(url_base, '', cache_subdir, file_name))
    return filepaths


# Download CORS station coordinates function
def download_cors_station(time, station_name, cache_dir):
    cache_subdir = cache_dir + 'cors_obs/'
    t = time.as_datetime()
    folder_path = t.strftime('%Y/%j/') + station_name + '/'
    filename = station_name + t.strftime("%j0.%yo")
    url_base = 'ftp://geodesy.noaa.gov/cors/rinex/'
    try:
        filepath = download_file(url_base, folder_path, cache_subdir, filename, compression='.gz')
        return filepath
    except IOError:
        print("File not downloaded, check availability on server.")
        return None