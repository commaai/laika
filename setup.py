#!/home/batman/one/laika/env

import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

setup(
  name='laika',
  version='0.0.1',
  url='https://github.com/commaai/laika',
  author='comma.ai',
  author_email='harald@comma.ai',
  packages=find_packages(),
  platforms='any',
  license='MIT',
  setup_requires=['numpy', 'pytest-runner'],
  install_requires=[
    'certifi',
    'requests',
    'scipy',
    'pycurl',
    'tqdm',
    'hatanaka',
    'pycapnp',
  ],
  ext_modules=[],
  package_data={'': ['*.capnp']},
  description="GNSS library for use with the comma.ai ecosystem",
  long_description='See https://github.com/commaai/laika',
  classifiers=[
    'Development Status :: 2 - Beta',
    "Natural Language :: English",
    "Programming Language :: Python :: 3",
    "Topic :: System :: Hardware",
  ],
  python_requires='>= 3.6',
  tests_require=['pytest'],
)
