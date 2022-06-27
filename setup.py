#!/usr/bin/env python
from distutils.core import setup
from setuptools import find_packages

setup(name='Verifier',
      version='1.0',
      description='Automatically verify security issues',
      author='Jan-Jaap Korpershoek',
      author_email='janjaap.korpershoek@northwave.nl',
      install_requires=['argcomplete', 'requests'],
      entry_points={
        'console_scripts': ['dradis_curl=dradis_curl:main', 'verifier=verifier.verifier:main'],
      },
      packages=find_packages(exclude=["tests", "tests.*"]),
      py_modules=["dradis_curl"],
      scripts=['start_test'],
      extras_require={
          "dradis": "dradis-api @ git+https://github.com/NorthwaveSecurity/dradis-api.git",
          'reporter': 'reporter @ git+https://github.com/JJK96/reporter.git',
      }
      )
