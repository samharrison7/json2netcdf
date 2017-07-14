'''Python script for creating, reading and manipulating NetCDF files'''
from netCDF4 import Dataset
import sys
import json

'''Parse the data and turn into NetCDF file'''
def parse(json_data, nc_data, hierarchy = []):
    # If this is a group, add it and its dimensions
    if (json_data['type'] == 'group'):
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
        for nested_data in json_data['data']:
            parse(nested_data, nc_data, hierarchy)

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
        nc_var[:] = json_data['data']

# Input file
data_filepath = sys.argv[1] if len(sys.argv)>1 else 'data.json'
nc_filepath = sys.argv[2] if len(sys.argv)>2 else 'data.nc'

# Create the data file and parse
with open(data_filepath) as data_file:
    data_file = json.loads(data_file.read())

nc_data = Dataset(nc_filepath,'w')
parse(data_file, nc_data)
nc_data.close()