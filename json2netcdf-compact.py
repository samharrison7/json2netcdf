'''Python script for creating a NetCDF file from one or more JSON files'''
from netCDF4 import Dataset
from copy import deepcopy
import numpy as np
import re
import os
import sys
import json
import argparse
import timeit

data_to_fill = []
variables_to_fill = []

# Parse the data and turn into NetCDF file. Parse will only over be called for groups,
# variables within that group are created by the parse method called for that group
def parse(json_group, nc_data, hierarchy=[], root=True, verbose=False):
    # Local names reference the same object, so appending to hierarchy without copying it first
    # alters everything that refers to it. I.e. siblings groups end up as children of their siblings
    hierarchy = deepcopy(hierarchy)
    # If this is a group, loop through its items and see what they are (dimensions, attributes or group/data)
    # if root or isinstance(json_group, dict):
    # Get the NC group we're currently in
    current_group = nc_data['/' + '/'.join(hierarchy)] if not root else nc_data
    # Get the dimensions first, because if they're not first in the json_group, then parsing a var
    # that uses them will fail
    if 'dimensions' in json_group:
        for dim_name, size in json_group['dimensions'].items():
            # Dimension will be specified size if it's an integer, else unlimited
            current_group.createDimension(dim_name, (size if (isinstance(size, int) and size>0) else None))
    # Loop through this group's items
    for name, data in json_group.items():
        # If this item is a list of attributes, create them
        if name == 'attributes':
            for att_name, value in data.items():
                setattr(current_group, att_name, value)
        # If this item is a group
        elif isinstance(data, dict):
            new_group = nc_data.createGroup('/' + '/'.join(hierarchy + [name]))   # Create this group
            # If the verbose option was specified
            if verbose and len(hierarchy) < 2:
                print("Creating group {0}".format(name))
            parse(data, nc_data, hierarchy + [name], False, verbose=verbose)
        # Otherwise, it must be data or an external file
        else:
            # Is this variable referencing an external file?
            if isinstance(data, str) and data[:6] == "file::":
                file_path = data[6:]
                with open(base_dir + file_path) as external_data:
                    external_data = json.loads(external_data.read())
                # If the external data is a group
                if isinstance(external_data, dict):
                    new_group = nc_data.createGroup('/' + '/'.join(hierarchy + [name]))
                    parse(external_data, nc_data, hierarchy + [name], False, verbose=verbose)
                # Otherwise, it must be a variable
                else:

                    parse_var(name, external_data, nc_data, hierarchy)
            # Otherwise, it must be data (not from external file)
            else:
                parse_var(name, data, nc_data, hierarchy)

    # If this is the root group, we must be done creating variables/groups
    # and can eventually fill then. This step is left to last to (hopefully)
    # speed things up
    if root:
        print("Filling variables ({0}) with data".format(len(data_to_fill)))
        for i, data in enumerate(data_to_fill):
            variables_to_fill[i][:] = data


# Parse a variable item, given its name, data and hierarchy
def parse_var(name, data, nc_data, hierarchy):
    # start_time = timeit.default_timer()
    # Get the dimensions from the name, which are between square brackets
    dimensions = re.findall('\[(.*?)\]', name)
    # Then retrieve just the name, without the dimensions (square brackets)
    parsed_name = name.split('[')[0]
    # Convert to numpy array to get dtype object
    np_data = np.array(data)
    # Append the list of data so that we can use it later to fill the
    # variable we're about to create
    data_to_fill.append(np_data)
    # Create the variable
    nc_var = nc_data.createVariable(
        '/' + '/'.join(hierarchy + [parsed_name]),
        np_data.dtype,
        tuple(dimensions)
    )
    # Add the newly created variable to the list of variables to
    # fill later
    variables_to_fill.append(nc_var)
    # elapsed = timeit.default_timer() - start_time
    # print("Time elapsed to create {0}: {1}".format(name, elapsed))


# Parse the command line arguments
parser = argparse.ArgumentParser()
parser.add_argument('input')
parser.add_argument('output')
parser.add_argument('-v', '--verbose', action='store_true')
args = parser.parse_args()
data_filepath = args.input
nc_filepath = args.output

# Create the data file and parse
with open(data_filepath) as data_file:
    data_file = json.loads(data_file.read())
base_dir = os.path.dirname(data_filepath)
if base_dir != "":
    base_dir = base_dir + "/"

nc_data = Dataset(nc_filepath, 'w')
parse(data_file, nc_data, verbose=args.verbose)
nc_data.close()
