# json2netcdf

json2netcdf is a Python script to convert one or more JSON files to a NetCDF4 file. There are numerous NetCDF to JSON parsers, but few that perform the reverse operation. The motivation? A quick and easy way to write NetCDF input files without having to write or modify a script to do so. JSON files are simple, easy to understand and write, and, crucially, follow a hierarchical format.

## Getting started

First up, clone this repo:

```bash
$ git clone https://github.com/samharrison7/json2netcdf
$ cd json2netcdf
```

json2netcdf is a Python script which relies on NumPy and netCDF4. If you've got relatively recent versions of these packages in your environment, then the script will probably work out of the box. If not, or if you'd like to keep things clean, then you can use the provided Conda [environment.yaml](./environment.yaml) file to create an environment to run json2netcdf from:

```bash
$ conda env create -f environment.yaml
$ conda activate json2netcdf
```

You can then run the `json2netcdf` script from this directory, or copy it to somewhere on your `$PATH` to make it globally available:

```bash
(json2netcdf) $ cp ./json2netcdf ~/bin      # For example, if ~/bin is in your $PATH
```

## Usage

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

Take a look at the example JSON file at [example/data.json](./example/data.json) for an idea of how to format your JSON file. In this example, we are trying to create a NetCDF file with the following data structure:

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

The datatype of the variable will be automatically deduced. In this example, `spatial_var` will have a datatype of `int64`, and the other variables will have a datatype of `double`. Internally, NumPy is responsible for deducing the variable type and at this moment in time, there is no way to specify what datatype your variable is ([pull requests are welcome!](./CONTRIBUTING.md))

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

### Multiple input files

The main input file specified when running the script can contain reference to other JSON files in its JSON data structure, so that large data sets can be split. The path to the external file must be prefixed with `file::` and the contents of that file will be imported in the same place as the path to the file. Therefore, either variables or entire groups can be imported. An example is given at [example/external.json](external.json):

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

## Limitations

This script is a simple way to create NetCDF files from JSON data, and doesn't support the full feature set that NetCDF offer. A few specific limitations are:
- There is no way to specify attributes for variables, only groups.
- Datatypes are implied and cannot be set explicitly.
- Only NetCDF4 files can be created.