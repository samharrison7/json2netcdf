#!/usr/bin/env python3
"""Command line interface to the JSON to NetCDF4 converter"""
import argparse
import json2netcdf


def main():
    # Parse the command line arguments
    parser = argparse.ArgumentParser(description='Convert JSON to NetCDF files.')
    parser.add_argument('input', help='path to the input JSON file')
    parser.add_argument('output', help='path to store the output NetCDF file to')
    parser.add_argument('-v', '--verbose', action='store_true', help='make terminal output more verbose')
    args = parser.parse_args()
    # Do the conversion
    nc_file = json2netcdf.convert(args.input, args.output, log_level=1 if not args.verbose else 2)
    nc_file.close()


if __name__ == '__main__':
    main()