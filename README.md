# Laika localization service with Kalman filtering


![python_shield](https://img.shields.io/badge/Python-3.8.2-yellow)


:hammer: **UNDER DEVELOPMENT** :wrench:


---


Laika is an open-source GNSS processing library.
Laika is similar to projects like [RTKlib](https://github.com/tomojitakasu/RTKLIB) and [GPSTK](https://github.com/SGL-UT/GPSTk),
but in Python and with a strong focus on readibility, usability and easy integration with other optimizers.
The library can process raw GNSS observations with data gathered online from various analysis groups to produce data ready for position/velocity estimation.

This is a fork from the original project [laika](https://github.com/commaai/laika).
Unfortunately, the original source code does not contain explaining code comments or introductory references.
Furthermore, the usage of a filter to improve the estimated position as well as the validation on sample data is mandatory for a full localization service.
Therefore, the Kalman filter example from the original project is restructured and improved.

## The GNSS problem
GNSS satellites orbit the earth broadcasting signals that allow the receiver to determine the distance to each satellite. These satellites have known orbits and so their positions are known. This makes determining the receiver's position a basic 3-dimensional [trilateration](https://en.wikipedia.org/wiki/Trilateration) problem. In practice observed distances to each satellite will be measured with some offset that is caused by the receiver's clock error. This offset also needs to be determined, making it a 4-dimensional trilateration problem. 
<img src="https://upload.wikimedia.org/wikipedia/commons/thumb/c/c3/3spheres.svg/622px-3spheres.svg.png" width="50%">
Since this problem is generally overdetermined (more than 4 satellites to solve the 4d problem) there is a variety of methods to compute a position estimate from the measurements.
Laika provides a basic [weighted least squares](https://en.wikipedia.org/wiki/Weighted_least_squares) solver for experimental purposes.
This is far from optimal due to the dynamic nature of the system
Hence, it is necessary to rely of a filter such as a [Kalman filter](https://en.wikipedia.org/wiki/Kalman_filter) for improved estimations.
However, the above description is over-simplified.
Getting accurate distance estimates to satellites and the satellite's position from the receiver observations is not trivial.
This is what we call _processing of the GNSS observables_ and it is this procedure laika is designed for.

### Further references
- [Concise clear explanations of most concepts (ESA)](https://gssc.esa.int/navipedia/index.php/Main_Page)
- [Comprehensive handbook of all things GNSS (Springer Book)](https://www.springer.com/us/book/9783319429267)

## Astrodog
Astrodog is the main component of the laika.
It is a python object, and like the [soviet space dogs](https://en.wikipedia.org/wiki/Soviet_space_dogs) to which it owes its name,
an Astrodog will do everything to make the life of its owner easier:
It fetches and process all the necessary data to transform raw GNSS observables into usable distance measurements and satellite positions ready for position estimation.

### Satellite info
Astrodog has a `get_sat_info` function that will provide an accurate position, velocity and clock error for any satellite at any time in history. 

### Pseudorange corrections
Astrodog has a `get_delay` function that will provide a pseudorange delay correction for any satellite at any time in history for the requested receiver position.
This delay correction includes a correction for the tropospheric signal delay, ionospheric signal delay and differential code biases (DCBs) of the transmitting satellite.
This delay can either be estimated with mathematical models or with [DGPS station](https://www.ngs.noaa.gov/CORS/) observations,
which is more accurate, but slower and only supported in the continental United States.

#### Architecture
GNSS processing requires getting data from the internet from various analysis groups
such as NASA's [CDDIS](https://cddis.nasa.gov/Data_and_Derived_Products/GNSS/GNSS_data_and_product_archive.html).
Astrodog downloads files from FTP servers from these groups when it needs them. Downloading and parsing all this data can be slow.
Astrodog caches all downloaded files locally to avoid re-downloading.
These files are then parsed by Astrodog and kept in memory.
Every one of these parsed objects (DCBs, ionospheric models, satellite orbit polynomials, etc.) has a valid location area and/or a valid time window. 
Within those windows these objects can provide information relevant to GNSS processing.

## Accuracy
To confirm the quality of Laika's GNSS processing, we ran laika's processing and a simple Kalman filter (procedure described in examples) on 2000 minutes of driving of a regular commute in San Francisco. The data comes from a "u-blox M8" chip. The fixes computed with laika's processed data are compared to the live navigation fixes given by the u-blox chip. They compared by looking at the standard deviation of all measured altitudes within every 5×5 m² in the dataset. There is no way to compare horizontal accuracy without ground truth, but there is no reason to believe that vertical and horizontal accuracy are not equally correlated for laika computed positions and u-blox's live positions. Data with the antenna on the roof and antenna inside the car are compared separately, since the results are significantly different. 
![altitude distributionplot](distplot_laika.png)

## Installation
For all dependencies, see
```bash

```
Afterwards, run
```bash
python setup.py install
```
inside a virtual environment. 