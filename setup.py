#!/usr/bin/env python
from distutils.core import setup
from setuptools import find_packages

dradis = ["dradis-api @ git+https://github.com/NorthwaveSecurity/dradis-api@v1.2"]
reporter = ['reporter @ git+https://github.com/JJK96/reporter.git']
cookie_flags_browser = ['browser_cookie3']
sslyze = ['sslyze @ git+https://github.com/NorthwaveSecurity/sslyze.git']

default = dradis + cookie_flags_browser + sslyze


setup(name='Verifier',
      version='1.1',
      description='Automatically verify security issues',
      author='Jan-Jaap Korpershoek',
      author_email='janjaap.korpershoek@northwave.nl',
      install_requires=['argcomplete', 'requests', 'cachetools', 'packaging', 'jinja2'],
      entry_points={
        'console_scripts': ['dradis_curl=dradis_curl:main', 'verifier=verifier:main'],
      },
      packages=find_packages(exclude=["tests", "tests.*"]),
      py_modules=["dradis_curl"],
      scripts=['start_test'],
      extras_require={
          "default": default,
          "dradis": dradis,
          'reporter': reporter,
          'cookie-flags-browser': cookie_flags_browser,
          'sslyze': sslyze
      }
      )
