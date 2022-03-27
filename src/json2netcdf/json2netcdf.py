import os
import re
import json
from copy import deepcopy
import numpy as np
from netCDF4 import Dataset


def convert(from_json, to_netcdf='data.nc', diskless=False, log_level=0):
    """
    Converts JSON data, as a file or Python dictionary, to NetCDF data,
    either in-memory (diskless) or to a physical file.

    Parameters
    ----------
    from_json : str or dict
        Either the path to the JSON file to convert, or a dictionary of
        data to convert.
    to_netcdf : str, default 'data.nc'
        Path to create the output NetCDF file. Ignored if `diskless=True`.
    diskless : bool, default False
        If `True`, create the NetCDF dataset in-memory only.
    log_level : {0, 1, 2}
        Controls the verbosity of terminal output, with 0 being no output
        and 2 being the most output.

    Returns
    -------
    netCDF4._netCDF4.Dataset
        NetCDF4 Dataset object containing the converted data.
    """

    # Is "from" a file path, in which case open it
    if type(from_json) is not dict:
        with open(from_json) as json_file:
            json_data = json.loads(json_file.read())
            base_dir = os.path.dirname(from_json)
    else:
        json_data = from_json
        base_dir = None
    # Create the NetCDF file
    nc_data = Dataset(to_netcdf, 'w', diskless=diskless)
    # Do the conversion
    _, _, nc_data = __parse(json_data, nc_data, log_level=log_level, base_dir=base_dir)
    # Return the dataset
    return nc_data


def __parse(json_group, nc_data, hierarchy=[], root=True, log_level=0, base_dir=None,
          data_to_fill=[], variables_to_fill=[]):
    """Parse the data and turn into NetCDF file. Parse will only over be called for groups,
    variables within that group are created by the parse method called for that group.
    The parse function is called recursively"""
    # Local names reference the same object, so appending to hierarchy without copying it first
    # alters everything that refers to it. I.e. siblings groups end up as children of their siblings
    hierarchy = deepcopy(hierarchy)
    data_to_fill = deepcopy(data_to_fill)
    variables_to_fill = deepcopy(variables_to_fill)
    # Get the NC group we're currently in
    current_group = nc_data['/' + '/'.join(hierarchy)] if not root else nc_data
    # Get the dimensions first, because if they're not first in the json_group, then parsing a var
    # that uses them will fail
    if 'dimensions' in json_group:
        for dim_name, size in json_group['dimensions'].items():
            # Dimension will be specified size if it's an integer, else unlimited
            current_group.createDimension(dim_name, (size if (isinstance(size, int) and size>0) else None))
    # Loop through this group's items and check if they're attributes, dimensions or data/groups
    for name, data in json_group.items():
        # If this item is a list of attributes, create them
        if name == 'attributes':
            for att_name, value in data.items():
                setattr(current_group, att_name, value)
        # If this item is the dimensions, ignore it (as we already created dimensions above)
        elif name == 'dimensions':
            pass
        # If this item is a group
        elif isinstance(data, dict):
            # Create this group
            _ = nc_data.createGroup('/' + '/'.join(hierarchy + [name]))
            # If the verbose option was specified, print that we're creating this group
            if (log_level > 1) and len(hierarchy) < 2:
                print(f'Creating group {name}')
            data_to_fill, variables_to_fill, _ = __parse(data, nc_data, hierarchy + [name], root=False,
                                                         log_level=log_level, base_dir=base_dir,
                                                         data_to_fill=data_to_fill,
                                                         variables_to_fill=variables_to_fill)
        # Otherwise, it must be data or an external file
        else:
            # Is this variable referencing an external file?
            if isinstance(data, str) and data[:6] == "file::":
                file_path = data[6:]
                with open(os.path.join(base_dir, file_path)) as external_data:
                    external_data = json.loads(external_data.read())
                # If the external data is a group
                if isinstance(external_data, dict):
                    _ = nc_data.createGroup('/' + '/'.join(hierarchy + [name]))
                    data_to_fill, variables_to_fill, _ = __parse(external_data, nc_data, hierarchy + [name],
                                                                 root=False, log_level=log_level, base_dir=base_dir,
                                                                 data_to_fill=data_to_fill,
                                                                 variables_to_fill=variables_to_fill)
                # Otherwise, it must be a variable
                else:
                    data_to_fill, variables_to_fill = __parse_var(name, external_data, nc_data, hierarchy, log_level,
                                                                  data_to_fill=data_to_fill,
                                                                  variables_to_fill=variables_to_fill)
            # Otherwise, it must be data (not from external file)
            else:
                data_to_fill, variables_to_fill = __parse_var(name, data, nc_data, hierarchy, log_level,
                                                              data_to_fill=data_to_fill,
                                                              variables_to_fill=variables_to_fill)

    # If this is the root group and have got this far, we must be done creating variables/groups
    # and can eventually fill then. This step is left to last to speed things up
    if root:
        if log_level > 0:
            print(f'Filling variables ({len(data_to_fill)}) with data')
        for i, data in enumerate(data_to_fill):
            try:
                variables_to_fill[i][:] = data
            except (IndexError, ValueError) as err:
                print(f'{err}. Variable: {variables_to_fill[i].group().path}/{variables_to_fill[i].name}')

    # Finally, return the NetCDF database
    return data_to_fill, variables_to_fill, nc_data


def __parse_var(name, data, nc_data, hierarchy, log_level, data_to_fill, variables_to_fill):
    """Parse a variable item, given its name, data and hierarchy"""
    # Get the dimensions from the name, which are between square brackets
    dimensions = re.findall(r'\[(.*?)\]', name)
    if len(dimensions) > 0:
        dimensions = dimensions[0].split(',')
    # Then retrieve just the name, without the dimensions (square brackets)
    parsed_name = name.split('[')[0]
    # Convert to numpy array to get dtype object
    np_data = np.array(data)
    # Append the list of data so that we can use it later to fill the
    # variable we're about to create
    data_to_fill.append(np_data)
    # Try and create the variable
    try:
        nc_var = nc_data.createVariable(
            '/' + '/'.join(hierarchy + [parsed_name]),
            np_data.dtype,
            tuple(dimensions)
        )
        if (log_level > 1) and len(hierarchy) < 2:
            print(f'Creating variable {parsed_name}')
    except TypeError as err:
        print(f'{err}. Variable: / {"/".join(hierarchy + [parsed_name])}')

    # Add the newly created variable to the list of variables to fill later
    variables_to_fill.append(nc_var)

    return data_to_fill, variables_to_fill
