# json2netcdf

This is a basic Python script to convert a JSON file to a NetCDF4 file, using the [netCDF4](https://github.com/Unidata/netcdf4-python) Python library. It is very much a *work in progress* and no real error checking occurs - make sure your JSON file follows exactly the structure it should! It only implements a small subset of what is actually possible in creating a NetCDF file. The documentation is also somewhat sparse at the moment - watch this space!

There are numerous NetCDF to JSON parsers, but none that I could find that perform the reverse operation. The motivation? I wanted a quick and easy way to write NetCDF input files without having to write or modify a script for every new input file. JSON files are simple, easy to understand and write, and, crucially, follow a hierarchical format.

## Running

Simply run the script, and if you like, specify the input and output file paths (these default to "data.json" and "data.nc"). Oh, and make sure you have the Python [netCDF4](https://github.com/Unidata/netcdf4-python) library installed.

```bash
$ python netcdf2json.py input.json output.nc
```
## JSON input format

Take a look at the sample `data.json` for an idea of how to format your JSON file. Each hierarchical level in the file contains an array of objects, and each object can either be a group or a variable, as denoted by the `"type"` property. The group/variable needs to be given a `"name"` and optionally some `"attributes"`. Groups can contain definitions of `"dimensions"`, each one having a `"name"` and `"size"` (which default to unlimited; `"size" : "unlimited"` can also be specified to this effect). Variables can contain an array of previously-defined `"dimensions"`, or none at all if the variable is a scalar. `"datatype"` of a variable is a specified datatype (see [netCDF4-python documentation](http://unidata.github.io/netcdf4-python/)). Finally, the `"data"` property is used to nested further groups, or specify the data to be contained in the variable.

The *first level* of the JSON file is the default `root` group and thus does not require `"name"` or `"type"` properties (and if they are specified, they will be ignored).