
# Laika

Laika is an open-source GNSS processing library, it will process raw GNSS observations with data gathered online from various analysis groups to produce GNSS data ready for position/velocity estimation. Laika is designed to produce accurate results whilst still being easy to use.
![alt text](https://www.thoughtco.com/thmb/RABYtJPM_H6BS_Wv8sNltm188vY=/768x0/filters:no_upscale():max_bytes(150000):strip_icc()/laika-515031406-58e80f1f3df78c5162a95267.jpg)

## The GNSS problem

GNSS satellites orbit the earth broadcasting signals that allow the receiver to determine the distance to each sattelite. These sattelites have known orbits and so their positions are known. This makes determining the receiver's position a basic 3-dimensional [trilateration](https://en.wikipedia.org/wiki/Trilateration) problem. In practice observed distances to each sattelite will be measured with some offset that is caused by the receiver's clock error. This offset also needs to be determined, making it a 4-dimensional trilateration problem. 
![alt text](https://upload.wikimedia.org/wikipedia/commons/thumb/c/c3/3spheres.svg/622px-3spheres.svg.png)

Since this problem is generally overdetermined (more than 4 sattelites to solve the 4d problem) there is a variety of methods to compute a position estimate from the measurements. Laika provides a basic [weighted least squares](https://en.wikipedia.org/wiki/Weighted_least_squares) solver for experimental purposes. This is far from optimal due to the dynamic nature of the system, this makes a bayesian estimator like a [Kalman filter](https://en.wikipedia.org/wiki/Kalman_filter) the preferred estimator.

However, the above description is over-simplified. Getting accurate distance estimates to sattelites and the sattelite's position from the receiver observations is not trivial. This is what we call processing of the GNSS observables and it is this procedure laika is designed to make easy.

## Astrodog
Astrodog is the main component of the laika. It is a python object, and like the [soviet space dogs](https://en.wikipedia.org/wiki/Soviet_space_dogs) to which it owes it's name, an astrodog will do everything in its power to make the life of its master easier. Which in this case is fetch and process all the neccesary data to transform raw GNSS observables into useable distance measurements and sattelite positions ready for position estimation.

#### Sattelite info
Astrodog has a get_sat_info function that will provide an accurate position, velocity and clock error for any sattelite at any time in history. 


#### Pseudorange corrections
Astrodog has a get_delay function that will provide a pseudorange delay correction for any sattelite at any time in history for the requested receiver position. This delay correction includes a correction for the tropospheric signal delay, ionospehric signal delay and differential code biases (DCBs) of the transmitting sattelite.

This delay can either be estimated with mathematical models or with [DGPS station](https://www.ngs.noaa.gov/CORS/) observations, which is more accurate, but slower and only supported in the continental United States.

#### Architecture
GNSS processing requires getting data from the internet from various analysis groups such as NASA's [CDDIS](https://cddis.nasa.gov/Data_and_Derived_Products/GNSS/GNSS_data_and_product_archive.html). AstroDog downloads files from FTP servers from these groups when it needs them. Downloading and parsing all this data can be slow. AstroDog caches all downloaded files locally to avoid redownloading. AstroDog also keep all parsed files in memory, so subsequent requests can be computed immidiately. Therefore one should always use only one AstroDog object for the processing of measurements, otherwise it will be incredibly slow.


## Design principles of laika
- Should work without configuration or setup
- Nothing is worth compromising accuracy for
- It is preferable to return no solution than a degraded solution





## Examples
A comprehensive walkthrough of the main functions of AstroDog and other useful laika functions can be found in the examples folder. There is also an example of computing a CORS stations's position using laika.


## Useful GNSS references
- [Comphrensive handbook of all things GNSS](https://www.springer.com/us/book/9783319429267)

- [Consice clear explanations of most concepts](https://gssc.esa.int/navipedia/index.php/Main_Page)
