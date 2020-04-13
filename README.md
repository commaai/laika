## Laika GNSS processing library with Kalman filtering for localization


![python_shield](https://img.shields.io/badge/Python-3.8.2-yellow)


:hammer: **UNDER DEVELOPMENT** :wrench:


---


Laika is an open-source GNSS processing library.
Laika is similar to projects like [RTKlib](https://github.com/tomojitakasu/RTKLIB) and [GPSTK](https://github.com/SGL-UT/GPSTk),
but in Python and with a strong focus on readibility, usability and easy integration with other optimizers.
The library can process raw GNSS observations with data gathered online from various analysis groups to produce data ready for position/velocity estimation.
However, in this repository, the focus is on improving stored raw localization data.

This is a fork from the original project [laika](https://github.com/commaai/laika).
Unfortunately, the original source code does not contain explaining code comments or introductory references.
Furthermore, the usage of a filter to improve the estimated position as well as the validation on sample data is mandatory for a full localization service.
Therefore, the Kalman filter example from the original project is restructured and improved.

Additionally, the code was updated to the latest Python 3 version instead and bugs were fixed.

### The GNSS problem
GNSS satellites orbit the earth broadcasting signals that allow the receiver to determine the distance to each satellite.
These satellites have known orbits and so their positions are known.
This makes determining the receiver's position a basic 3-dimensional [trilateration](https://en.wikipedia.org/wiki/Trilateration) problem.
In practice observed distances to each satellite will be measured with some offset that is caused by the receiver's clock error.
This offset also needs to be determined, making it a 4-dimensional trilateration problem.

Since this problem is generally overdetermined (usually more than four satellites to solve a four-dimensional problem),
there is a variety of methods to compute an optimized position estimate from the measurements.
Laika provides a basic [weighted least squares](https://en.wikipedia.org/wiki/Weighted_least_squares) (WLS) optimizer/solver for experimental purposes.
The given WLS optimizer is part of SciPy.
However, it is necessary to rely of a filter such as a [Kalman filter](https://en.wikipedia.org/wiki/Kalman_filter) for improved estimations.

Getting accurate distance estimates to satellites and the satellite's position from the receiver observations is not trivial.
This is what we call _processing of the GNSS observables_ and it is this procedure laika is designed for.
For a concise explanation of most concepts, click [here](https://gssc.esa.int/navipedia/index.php/Main_Page).

### Astrodog :dog:
Astrodog is the main component of the laika.
It is a python object, and like the [soviet space dogs](https://en.wikipedia.org/wiki/Soviet_space_dogs) to which it owes its name,
an Astrodog will do everything to make the life of its owner easier:
It fetches and process all the necessary data to transform raw GNSS observables into usable distance measurements and satellite positions ready for position estimation.

#### Satellite info
Astrodog has a `get_sat_info` function that will provide an accurate position, velocity and clock error for any satellite at any time in history. 

#### Pseudorange corrections
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

### Kalman filter
The Kalman filter framework described here is an incredibly powerful tool for any optimization problem,
but particularly for visual odometry, sensor fusion localization or SLAM. It is designed to provide very
accurate results, work online or offline, be fairly computationally efficient, be easy to design filters with in
python.

#### Extended Kalman Filter with symbolic Jacobian computation
Most dynamic systems can be described as a Hidden Markov Process. To estimate the state of such a system with noisy
measurements one can use a Recursive Bayesian estimator. For a linear Markov Process a regular linear Kalman filter is optimal.
Unfortunately, a lot of systems are non-linear. Extended Kalman Filters can model systems by linearizing the non-linear
system at every step, this provides a close to optimal estimator when the linearization is good enough. If the linearization
introduces too much noise, one can use an Iterated Extended Kalman Filter, Unscented Kalman Filter or a Particle Filter. For
most applications those estimators are overkill and introduce too much complexity and require a lot of additional compute.

Conventionally Extended Kalman Filters are implemented by writing the system's dynamic equations and then manually symbolically 
calculating the Jacobians for the linearization. For complex systems this is time consuming and very prone to calculation errors.
This library symbolically computes the Jacobians using sympy to simplify the system's definition and remove the possiblity of introducing calculation errors.

#### Error State Kalman Filter
3D localization algorithms ussually also require estimating orientation of an object in 3D. Orientation is generally represented
with euler angles or quaternions. 

Euler angles have several problems, there are mulitple ways to represent the same orientation,
gimbal lock can cause the loss of a degree of freedom and lastly their behaviour is very non-linear when errors are large. 
Quaternions with one strictly positive dimension don't suffer from these issues, but have another set of problems.
Quaternions need to be normalized otherwise they will grow unbounded, this is cannot be cleanly enforced in a kalman filter.
Most importantly though a quaternion has 4 dimensions, but only represents 3 degrees of freedom, so there is one redundant dimension.

Kalman filters are designed to minimize the error of the system's state. It is possible to have a kalman filter where state and the error of the state are represented in a different space. As long as there is an error function that can compute the error based on the true state and estimated state. It is problematic to have redundant dimensions in the error of the kalman filter, but not in the state. A good compromise then, is to use the quaternion to represent the system's attitude state and use euler angles to describe the error in attitude. This library supports and defining an arbitrary error that is in  a different space than the state. [Joan Solà](https://arxiv.org/abs/1711.02508) has written a comprehensive description of using ESKFs for robust 3D orientation estimation.

#### Multi-State Constraint Kalman Filter
How do you integrate feature-based visual odometry with a Kalman filter? The problem is that one cannot write an observation equation for 2D feature observations in image space for a localization kalman filter. One needs to give the feature observation a depth so it has a 3D position, then one can write an obvervation equation in the kalman filter. This is possible by tracking the feature across frames and then estimating the depth. However, the solution is not that simple, the depth estimated by tracking the feature across frames depends on the location of the camera at those frames, and thus the state of the kalman filter. This creates a positive feedback loop where the kalman filter wrongly gains confidence in it's position because the feature position updates reinforce it.

The solution is to use an [MSCKF](http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.437.1085&rep=rep1&type=pdf), which this library fully supports.

#### Rauch–Tung–Striebel smoothing
When doing offline estimation with a kalman filter there can be an initialization period where states are badly estimated. 
Global estimators don't suffer from this, to make our kalman filter competitive with global optimizers we can run the filter
backwards using an RTS smoother. Those combined with potentially multiple forward and backwards passes of the data should make
performance very close to global optimization.

#### Mahalanobis distance outlier rejector
A lot of measurements do not come from a Gaussian distribution and as such have outliers that do not fit the statistical model
of the Kalman filter. This can cause a lot of performance issues if not dealt with. This library allows the use of a mahalanobis
distance statistical test on the incoming measurements to deal with this. Note that good initialization is critical to prevent
good measurements from being rejected.

### Deployment with Docker :whale:
The software can be easily deployed using Docker:
```bash
chmod +x run_docker.sh && ./run_docker.sh
```
This also builds the image.