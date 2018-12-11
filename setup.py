#!/home/batman/one/laika/env
#-*- coding: utf-8 -*-

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
  install_requires=[
    'requests',
    'numpy==1.14.5',
    'scipy==1.0.0',
    'tqdm'
  ],
  ext_modules=[],
  description="GNSS library for use with the comma.ai ecosystem",
  long_description='See https://github.com/commaai/laika',
  classifiers=[
    'Development Status :: 2 - Beta',
    "Natural Language :: English",
    "Programming Language :: Python :: 2",
    "Topic :: System :: Hardware",
  ],
  setup_requires=['pytest-runner'],
  tests_require=['pytest'],
)
