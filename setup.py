# Import dependencies
import os
from setuptools import setup, find_packages

# Store current path
here = os.path.abspath(os.path.dirname(__file__))

# Define setup procedure
setup(
    name='laika',
    version='0.0.1',
    url='https://github.com/rwschubert/kalman-laika',
    author='comma.ai, rwschubert',
    packages=find_packages(),
    platforms='any',
    license='MIT',
    setup_requires=['numpy', 'pytest-runner'],
    install_requires=[
        'requests',
        'scipy',
        'tqdm'
    ],
    ext_modules=[],
    description="GNSS library for use with a Kalman filter",
    long_description='See https://github.com/rwschubert/kalman-laika',
    classifiers=[
        'Development Status :: 0.0.1',
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Topic :: System :: Hardware",
    ],
    tests_require=['pytest'],
)