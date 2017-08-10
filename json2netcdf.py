'''Python script for creating, reading and manipulating NetCDF files'''
from netCDF4 import Dataset
from copy import deepcopy
import sys
import json

'''Parse the data and turn into NetCDF file'''
def parse(json_data, nc_data, hierarchy = [], root = True):
    # Local names reference the same object, so appending to hierarchy without copying it first
    # alters everything that refers to it. I.e. siblings groups end up as children of their siblings
    hierarchy = deepcopy(hierarchy)
    # If this is a group, add it and its dimensions
    if (root == True or json_data['type'] == 'group'):
        # If this is the root group, don't create new group for it.
        # Any name specified will be ignored.
        if (root == True):
            nc_group = nc_data
        else:
            hierarchy.append(json_data['name'])                             # Build the hierarchy
            nc_group = nc_data.createGroup('/' + '/'.join(hierarchy))       # Create the group (with correct hierarchy)
        # Does the group have dimensions?
        if 'dimensions' in json_data:
            for dimension in json_data['dimensions']:
                # Create a dimension with either given or unlimited size
                if (('size' not in dimension) or dimension['size'] == 'unlimited'):
                    nc_group.createDimension(dimension['name'], None)   # Unlimited
                else:
                    nc_group.createDimension(dimension['name'], dimension['size'])  # Specified size
        # Does the group have attributes?
        if 'attributes' in json_data:
            for attribute in json_data['attributes']:
                setattr(nc_group, attribute['name'], attribute['value'])                                                                         
        # As we're in a group, recursively call this function until we reach variable
        if 'data' in json_data:
            for nested_data in json_data['data']:
                parse(nested_data, nc_data, hierarchy, False)

    # If this is a variable, add it and its dimensions
    elif (json_data['type'] == 'variable'):
        # Have dimensions been specified or are we dealing with a scalar?
        if ('dimensions' in json_data):
            nc_var = nc_data.createVariable('/' + '/'.join(hierarchy) + '/' + json_data['name'],
                json_data['datatype'], 
                tuple(json_data['dimensions']))
        else:
            nc_var = nc_data.createVariable('/' + '/'.join(hierarchy) + '/' + json_data['name'],
                json_data['datatype'])
        # Does the variable have attributes?
        if 'attributes' in json_data:       
            for attribute in json_data['attributes']:
                setattr(nc_var, attribute['name'], attribute['value'])
        # Put the data into the newly created variable
        if 'data' in json_data: nc_var[:] = json_data['data']

# Input file
data_filepath = sys.argv[1] if len(sys.argv)>1 else 'data.json'
nc_filepath = sys.argv[2] if len(sys.argv)>2 else 'data.nc'

# Create the data file and parse
with open(data_filepath) as data_file:
    data_file = json.loads(data_file.read())

nc_data = Dataset(nc_filepath,'w')
parse(data_file, nc_data)
nc_data.close()