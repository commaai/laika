#-*- coding: utf-8 -*-

import codecs
import os
import re
from setuptools import setup, Extension

here = os.path.abspath(os.path.dirname(__file__))

setup(
  name='laika',
  version='0.0.1',
  url='https://github.com/commaai/laika',
  author='comma.ai',
  author_email='harald@comma.ai',
  packages=[
    'gnss',
    ],
  package_dir = {'laika': 'gnss'},
  platforms='any',
  license='MIT',
  install_requires=[
    'libusb1 >= 1.6.4',
    'hexdump >= 3.3',
    'pycrypto >= 2.6.1',
    'tqdm >= 4.14.0',
    'requests'
  ],
  ext_modules = [],
  description="GNSS library for use with the comma.ai ecosystem",
  long_description='See https://github.com/commaai/laika',
  classifiers=[
    'Development Status :: 2 - Pre-Alpha',
    "Natural Language :: English",
    "Programming Language :: Python :: 2",
    "Programming Language :: Python :: 3",
    "Topic :: System :: Hardware",
  ],
  setup_requires=['pytest-runner'],
  tests_require=['pytest'],
)

