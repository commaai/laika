#!/home/batman/one/laika/env
#-*- coding: utf-8 -*-

import os
from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))

setup(
  name='laika',
  version='0.0.1',
  url='https://github.com/commaai/laika',
  author='comma.ai',
  author_email='harald@comma.ai',
  packages=['gnss'],
  package_dir={'laika': 'gnss'},
  platforms='any',
  license='MIT',
  install_requires=[
    'requests',
    'numpy==1.14.5',
    'scipy==1.0.0',
    'IPython<6.0',
    'ipykernel<5.0',
    'jupyter-console==5.1.0',
    'tqdm',
    'jupyter',
    'seaborn',
    'pillow',
    'matplotlib<3.0'
  ],
  ext_modules=[],
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
