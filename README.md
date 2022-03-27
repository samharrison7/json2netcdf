# json2netcdf

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.4286216.svg)](https://doi.org/10.5281/zenodo.4286216)
[![fair-software.eu](https://img.shields.io/badge/fair--software.eu-%E2%97%8F%20%20%E2%97%8F%20%20%E2%97%8F%20%20%E2%97%8F%20%20%E2%97%8B-yellow)](https://fair-software.eu)
[![PyPI version](https://badge.fury.io/py/json2netcdf.svg)](https://badge.fury.io/py/json2netcdf)

json2netcdf is a Python package to convert JSON data into NetCDF4 data. The motivation? A quick and easy way to write NetCDF input files without having to hand-craft a script to do so. JSON files are simple, easy to understand and write, and, crucially, follow a hierarchical format.

Features:
- Programmatic and command line interfaces.
- Converts well-formatted JSON files and Python dictionaries to NetCDF files.
- NetCDF files can be physical or in-memory (diskless).
- Nested JSON files can be specified.
- Internally uses the Python `netCDF4` package and returns `Dataset` objects.
- Groups, attributes, dimensions, variables and multiple datatypes are supported.

## Getting started

You can use pip to install json2netcdf as a progammatic and command line interface:

```bash
$ pip install json2netcdf
```

A Conda environment file is also provided with the required libraries for developing or extending the package.

```bash
$ conda env create -f environment.yml
$ conda activate json2netcdf
```

## Usage

The package has one main method, `convert`, which does the file/data conversion. See below for the required formating for JSON files.

```python
>>> import json2netcdf
>>> json2netcdf.convert(from_json={'my_var': 42}, diskless=True)
<class 'netCDF4._netCDF4.Dataset'>
root group (NETCDF4 data model, file format HDF5):
    dimensions(sizes):
    variables(dimensions): int64 my_var()
    groups:
```

`from_json` can be a Python dictionary or the path to a JSON file. Set `diskless` to `True` for an in-memory NetCDF dataset to be returned (default is `False`). `to_netcdf` can be used to specify the location of the output NetCDF file you want (defaults to `data.nc`). The `convert` method can be used as a context manager, and if it isn't, the user is responsible for closing the returned dataset (`nc_file.close()`). Using the [example/data.json](https://github.com/samharrison7/json2netcdf/blob/develop/example/data.json) file:

```python
>>> with json2netcdf.convert(from_json='example/data.json', to_netcdf='data.nc') as nc_file:
...     nc_file['var_group']['spatial_var']
...
<class 'netCDF4._netCDF4.Variable'>
int64 spatial_var(x, y)
path = /var_group
unlimited dimensions:
current shape = (2, 2)
filling on, default _FillValue of -9223372036854775806 used
``` 

For more information on using the returned NetCDF `Dataset` object, see the [netCDF4 library documentation](https://unidata.github.io/netcdf4-python/).

### Command line interface

There is a command line interface which acts as a wrapper around `json2netcdf.convert`. It requires you to specify paths to the input JSON file and output NetCDF file:

```
usage: json2netcdf [-h] [-v] input output

Convert JSON to NetCDF files.

positional arguments:
  input          path to the input JSON file
  output         path to store the output NetCDF file to

optional arguments:
  -h, --help     show this help message and exit
  -v, --verbose  make terminal output more verbose
```

## JSON input format

Your JSON data must be well formatted, following the conventions described below. Take a look at the example JSON file at [example/data.json](https://github.com/samharrison7/json2netcdf/blob/develop/example/data.json) for an idea of how to format your JSON file. In this example, we are trying to create a NetCDF file with the following data structure:

```
var_group (group)
    spatial_var = [[1, 2], [3, 4]]
    spatiotemporal_var = [[[1.1, 1.2], [1.3, 1.4]], [[1.5, 1.6], [1.7, 1.8]]]
scalar_var = 42.0
```

### Dimensions

The file will have one group `var_group`, with two variables: `spatial_var` is a 2D array and `spatiotemporal_var` is a 3D array. There is also a scalar variable `scalar_var` which only belongs to the root group. As this is a NetCDF file, we need to specify dimensions for the variables, so let's say that `spatial_var` has `(x,y)` dimensions, and `spatiotemporal_var` has `(x,y,t)` dimensions. In this example, each of these has a size of 2. To define this is the JSON file, we create a `dimensions` object:

```json
{
    "dimensions" : {
        "x" : 2, "y" : 2, "t": 2
    }
}
```

### Groups and variables

We can now create an object for the `var_group` and place these variables in it. The square bracket notation is used to tell the script what dimensions your variables have. We will also create `scalar_var` in the root group, which doesn't have any dimensions associated to it:

```json
{
    "dimensions" : {
        "x" : 2, "y" : 2, "t": 2
    },
    "var_group" : {
        "spatial_var[x,y]" : [[1, 2], [3, 4]],
        "spatiotemporal_var[x,y,t]" : [[[1.1, 1.2], [1.3, 1.4]], [[1.5, 1.6], [1.7, 1.8]]]
    },
    "scalar_var": 42.0
}
```

Here, the dimensions are available from the root group (i.e. to all groups in the NetCDF file's hierarchy). If you want to add dimensions specifically for certain groups, you can include a `dimensions` object within that group.

### Datatype 

The datatype of the variable will be automatically deduced. In this example, `spatial_var` will have a datatype of `int64`, and the other variables will have a datatype of `double`. Internally, NumPy is responsible for deducing the variable type and at this moment in time, there is no way to specify what datatype your variable is ([pull requests are welcome!](https://github.com/samharrison7/json2netcdf/blob/develop/CONTRIBUTING.md))

### Attributes

Attributes can be added to the NetCDF file by creating an `attributes` object in the group you wish to add the attributes to. For example, to add attributes to the root group:

```json
{
    "dimensions" : {
        "x" : 2, "y" : 2, "t": 2
    },
    "attributes" : {
        "description" : "Example data file",
        "author" : "Sam Harrison"
    },
    "var_group" : {
        "spatial_var[x,y]" : [[1, 2], [3, 4]],
        "spatiotemporal_var[x,y,t]" : [[[1.1, 1.2], [1.3, 1.4]], [[1.5, 1.6], [1.7, 1.8]]]
    },
    "scalar_var": 42.0
}
```

Attributes cannot yet be added to variables. [Pull requests are welcome!](https://github.com/samharrison7/json2netcdf/blob/develop/CONTRIBUTING.md).

### Multiple input files

The main input file specified when running the script can contain reference to other JSON files in its JSON data structure, so that large data sets can be split. The path to the external file must be prefixed with `file::` and the contents of that file will be imported in the same place as the path to the file. Therefore, either variables or entire groups can be imported. An example is given at [example/external.json](https://github.com/samharrison7/json2netcdf/blob/develop/example/external.json):

```json
{
    "dimensions" : {
        "x" : 10,
        "y" : 5
    },
    "external_group" : "file::external_group.json",
    "external_var[x,y]" : "file::external_var.json"
}
```

Bear in mind, if importing an array variable, the dimensions of the array must be present in the parent file. Imported files can themselves include file imports.

## Dict to NetCDF, YAML to NetCDF, TOML to NetCDF...

Whilst this library is primarily for JSON to NetCDF4 conversion, you will notice that it is really just a Python dictionary to NetCDF4 converter with the ability to also open JSON files. This means it can be flexibly used to convert other markup languages without too much trouble. For example, say we have the following YAML:

```yaml
dimensions:
  x: 4
var_group:
  my_var[x]: [1, 2, 3, 4]
```

We can use the [PyYAML library](https://pyyaml.org/wiki/PyYAMLDocumentation) to load this as a dict, before converting it to NetCDF:

```python
>>> import yaml
>>> import json2netcdf
>>> data = yaml.load("""
... dimensions:
...   x: 4
... var_group:
...   my_var[x]: [1, 2, 3, 4]
... """)
>>> json2netcdf.convert(data, diskless=True)
<class 'netCDF4._netCDF4.Dataset'>
root group (NETCDF4 data model, file format HDF5):
    dimensions(sizes): x(4)
    variables(dimensions):
    groups: var_group
```

## Limitations

This script is a simple way to create NetCDF files from JSON data, and doesn't support the full feature set that NetCDF offer. A few specific limitations are:
- There is no way to specify attributes for variables, only groups.
- Datatypes are implied and cannot be set explicitly.
- Only NetCDF4 files can be created.