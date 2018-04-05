# (C) British Crown Copyright 2016, Met Office.
# See LICENSE.md in the top directory for license details.
#

# DREQ JSON Query: rudimentary setuptools config
#

from setuptools import setup, find_packages

setup(name="djq",
      version="0.0",
      description="JSON queries for the CMIP6 data request",
      author="Tim Bradshaw",
      author_email="tim.bradshaw@metoffice.gov.uk",
      url="http://www.metoffice.gov.uk/",
      packages=find_packages("lib"),
      package_dir={"": "lib"},
      scripts=("bin/djq", "bin/cci",
               "bin/all-requests", "bin/scatter-replies"),
      test_suite='nose.collector',
      install_requires=("dreqpy",),
      zip_safe=False)
