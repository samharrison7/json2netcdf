"""
json2netcdf
===========

Python package for converting JSON data to NetCDF data.

Functions
---------
convert
    Converts JSON data, as a file or Python dictionary, to NetCDF data,
    either in-memory (diskless) or to a physical file.
"""

from .json2netcdf import convert
