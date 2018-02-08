'''Python script for creating a NetCDF file from one or more JSON files'''
from netCDF4 import Dataset
from copy import deepcopy
import numpy as np
import re
import os
import sys
import json


# Parse the data and turn into NetCDF file. Parse will only over be called for groups,
# variables within that group are created by the parse method called for that group
def parse(json_group, nc_data, hierarchy=[], root=True):
    # Local names reference the same object, so appending to hierarchy without copying it first
    # alters everything that refers to it. I.e. siblings groups end up as children of their siblings
    hierarchy = deepcopy(hierarchy)
    # If this is a group, loop through its items and see what they are (dimensions, attributes or group/data)
    # if root or isinstance(json_group, dict):
    # Get the NC group we're currently in
    current_group = nc_data['/' + '/'.join(hierarchy)] if not root else nc_data
    # Loop through this group's items
    for name, data in json_group.items():
        # If this item is a list of dimensions, create them
        if name == 'dimensions':
            for dim_name, size in data.items():
                # Dimension will be specified size if it's an integer, else unlimited
                current_group.createDimension(dim_name, (size if (isinstance(size, int) and size>0) else None))
        # If this item is a list of attributes, create them
        elif name == 'attributes':
            for att_name, value in data.items():
                setattr(current_group, att_name, value)
        # If this item is a group
        elif isinstance(data, dict):
            new_group = nc_data.createGroup('/' + '/'.join(hierarchy + [name]))   # Create this group
            parse(data, nc_data, hierarchy + [name], False)
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
                    parse(external_data, nc_data, hierarchy + [name], False)
                # Otherwise, it must be a variable
                else:
                    # Get the dimensions from the name, which are between square brackets
                    dimensions = re.findall('\[(.*?)\]', name)
                    # Then retrieve just the name, without the dimensions (square brackets)
                    parsed_name = name.split('[')[0]
                    # Convert to numpy array to get dtype object
                    np_data = np.array(external_data)
                    # Create the variable
                    nc_var = nc_data.createVariable(
                        '/' + '/'.join(hierarchy + [parsed_name]),
                        np_data.dtype,
                        tuple(dimensions)
                    )
                    # Fill the variable
                    nc_var[:] = np_data
            # Otherwise, it must be data (not from external file)
            else:
                # Get the dimensions from the name, which are between square brackets
                dimensions = re.findall('\[(.*?)\]', name)
                # Then retrieve just the name, without the dimensions (square brackets)
                parsed_name = name.split('[')[0]
                # Convert to numpy array to get dtype object
                np_data = np.array(data)
                # Create the variable
                nc_var = nc_data.createVariable(
                    '/' + '/'.join(hierarchy + [parsed_name]),
                    np_data.dtype,
                    tuple(dimensions)
                )
                # Fill the variable
                nc_var[:] = np_data

            

    #     # If this is the root group, don't create new group for it.
    #     # Any name specified will be ignored.
    #     if root:
    #         nc_group = nc_data
    #     else:
    #         hierarchy.append(json_data['name'])                             # Build the hierarchy
    #         nc_group = nc_data.createGroup('/' + '/'.join(hierarchy))       # Create the group (with correct hierarchy)
    #     # Does the group have dimensions?
    #     if 'dimensions' in json_data:
    #         for dimension in json_data['dimensions']:
    #             # Create a dimension with either given or unlimited size
    #             if ('size' not in dimension) or dimension['size'] == 'unlimited':
    #                 nc_group.createDimension(dimension['name'], None)   # Unlimited
    #             else:
    #                 nc_group.createDimension(dimension['name'], dimension['size'])  # Specified size
    #     # Does the group have attributes?
    #     if 'attributes' in json_data:
    #         for attribute in json_data['attributes']:
    #             setattr(nc_group, attribute['name'], attribute['value'])                                                                         
    #     # As we're in a group, recursively call this function until we reach variable
    #     if 'data' in json_data:
    #         for nested_data in json_data['data']:
    #             parse(nested_data, nc_data, hierarchy, False)

    # # If this is a variable, add it and its dimensions
    # elif json_data['type'] == 'variable':
    #     # If we're trying to get data from external file
    #     if isinstance(json_data['data'], str) and ".json" in json_data['data']:
    #         with open(base_dir + json_data['data']) as external_data:
    #             external_data = json.loads(external_data.read())
    #         json_data['data'] = external_data
    #     # Have dimensions been specified or are we dealing with a scalar?
    #     if 'dimensions' in json_data:
    #         nc_var = nc_data.createVariable('/' + '/'.join(hierarchy) + '/' + json_data['name'],
    #                                         json_data['datatype'],
    #                                         tuple(json_data['dimensions']))
    #     else:
    #         nc_var = nc_data.createVariable('/' + '/'.join(hierarchy) + '/' + json_data['name'],
    #                                         json_data['datatype'])
    #     # Does the variable have attributes?
    #     if 'attributes' in json_data:       
    #         for attribute in json_data['attributes']:
    #             setattr(nc_var, attribute['name'], attribute['value'])
    #     # Put the data into the newly created variable
    #     if 'data' in json_data:
    #         nc_var[:] = json_data['data']


# Input file
data_filepath = sys.argv[1] if len(sys.argv) > 1 else 'data.json'
nc_filepath = sys.argv[2] if len(sys.argv) > 2 else 'data.nc'

# Create the data file and parse
with open(data_filepath) as data_file:
    data_file = json.loads(data_file.read())
base_dir = os.path.dirname(data_filepath)
if base_dir != "":
    base_dir = base_dir + "/"

nc_data = Dataset(nc_filepath, 'w')
parse(data_file, nc_data)
nc_data.close()
