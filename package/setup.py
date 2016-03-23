from setuptools import setup, find_packages

setup(name="dqi",
      version="0.1",
      description="An interface to the CMIP6 data request",
      author="Tim Bradshaw",
      author_email="tim.bradshaw@metoffice.gov.uk",
      packages=find_packages(),
      scripts=("bin/jwalk", "bin/twalk",
               "bin/m2v", "bin/v2m",
               "bin/dqcsv"),
      zip_safe=False)
