# json2netcdf

This is a basic Python script to convert a JSON file to a NetCDF4 file, using the [netCDF4](https://github.com/Unidata/netcdf4-python) Python library. It is very much a *work in progress* and no real error checking occurs - make sure your JSON file follows exactly the structure it should! It only implements a small subset of what is actually possible in creating a NetCDF file. The documentation is also somewhat sparse at the moment - watch this space!

There are numerous NetCDF to JSON parsers, but none that I could find that perform the reverse operation. The motivation? I wanted a quick and easy way to write NetCDF input files without having to write or modify a script for every new input file. JSON files are simple, easy to understand and write, and, crucially, follow a hierarchical format.

## Running

Simply run the script, and if you like, specify the input and output file paths (these default to "data.json" and "data.nc"). Oh, and make sure you have the Python [netCDF4](https://github.com/Unidata/netcdf4-python) library installed.

```bash
$ python netcdf2json.py input.json output.nc
```
## JSON input format

Take a look at the sample `data.json` for an idea of how to format your JSON file. The hierarchy mimics that of a NetCDF file, and each hierarchical level is represented by a `data` property, which contains an array of objects that are either groups or variables.

### Example

For example, say we wanted to mimics the following data structure:

- **root** (group)
    - **positions** (group)
        - **x** = [1.0, 1.1, 1.2, 1.3, 1.4]
        - **y** = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        - **time** = 100

First, we must create the root group, which is present in any NetCDF file. The first hierarchical level of any JSON file is *always* the root group and thus a `name` or `type` doesn't have to be specified (and will be ignored if they are). Thus, the root group is simply an empty object. We know we're going to add further levels to the hierarchy, so let's put an empty `data` array in there to represent that:

```json
{
    "data" : []
}
```

The next level of the hierarchy is another group called "positions". Thus, the `data` property will be an array containing only one object, and that object will contain information about the "positions" group. Crucially, we need to give the group a `name` and tell the script that is it a group (and not a variable) by defining a `type`. Let's also put a data array in there, as we know "positions" will contain some variables:

```json
{
    "data" : [
        {
            "name" : "positions",
            "type" : "group",
            "data" : []
        }
    ]
}
```

NetCDF variables that aren't scalars need pre-defined dimensions given to them, and these dimensions can be defined by any group in the hierarchy. The "x" and "y" variables of the hierarchy we're trying to build both need a 1D array, of sizes 5 and 10, respectively. Let's define these dimensions in the root group (so they can be used in any sub-group), by the use of a `dimensions` property that contains an array of objects, each object representing a dimension with a `name` and `size` (omit size for unlimited-size dimensions):

```json
{   
    "dimensions" : [
        { "name" : "x_dim", "size" : 5 },
        { "name" : "y_dim", "size" : 10 }
    ],
    "data" : [
        {
            "name" : "positions",
            "type" : "group",
            "data" : []
        }
    ]
}
```

Now, we can add those variables along with the "time" scalar to the positions group. Like groups, variables need a `name` and a `type`, which is now equal to "variable". Additionally, `dimensions` can be specified as an array of dimension names, as well as a `datatype` property, which represents the data type of the variable. These follow the [numpy data type](https://docs.scipy.org/doc/numpy/reference/arrays.dtypes.html) character code convention, in exactly the same fashion as the netcdf4-python library - [see here](http://unidata.github.io/netcdf4-python/#netCDF4.Dataset). For example, "f8" represents a 64-bit floating point number and "i4" a 32-bit signed integer. Scalars, like "time", don't need an dimensions specified. The variable value itself is represented in the `data` property.

```json
{   
    "dimensions" : [
        { "name" : "x_dim", "size" : 5 },
        { "name" : "y_dim", "size" : 10 }
    ],
    "data" : [
        {
            "name" : "positions",
            "type" : "group",
            "data" : [
                {
                    "name" : "x",
                    "type" : "variable",
                    "dimensions" : [ "x_dim" ],
                    "datatype" : "f8",
                    "data" : [ [1.0, 1.1, 1.2, 1.3, 1.4] ]
                },
                {
                    "name" : "y",
                    "type" : "variable",
                    "dimensions" : [ "y_dim" ],
                    "datatype" : "i4",
                    "data" : [ [1,2,3,4,5,6,7,8,9,10] ]
                },
                {
                    "name" : "time",
                    "type" : "variable",
                    "datatype" : "f8",
                    "data" : 100
                },
            ]
        }
    ]
}
```

We've now completely mimicked the data structure originally specified. As a final flourish, we can assign some NetCDF attributes to the groups and variables, by specifying an `attributes` property, which contains an array of objects, each object representing a different attribute and containing a `name` and `value` property. These allow us to add metadata (e.g., description of a variable) to the data:

```json
{   
    "dimensions" : [
        { "name" : "x_dim", "size" : 5 },
        { "name" : "y_dim", "size" : 10 }
    ],
    "attributes" : [
        {
            "name" : "description",
            "value" : "Example data file."
        },
        {
            "name" : "author",
            "value" : "Sam Harrison"
        }
    ],
    "data" : [
        {
            "name" : "positions",
            "type" : "group",
            "data" : [
                {
                    "name" : "x",
                    "type" : "variable",
                    "dimensions" : [ "x_dim" ],
                    "attributes" : [
                        {
                            "name" : "description",
                            "value" : "Positions on x-direction at a given time."
                        }
                    ],
                    "datatype" : "f8",
                    "data" : [ [1.0, 1.1, 1.2, 1.3, 1.4] ]
                },
                {
                    "name" : "y",
                    "type" : "variable",
                    "dimensions" : [ "y_dim" ],
                    "attributes" : [
                        {
                            "name" : "description",
                            "value" : "Positions on y-direction at a given time."
                        }
                    ],
                    "datatype" : "i4",
                    "data" : [ [1,2,3,4,5,6,7,8,9,10] ]
                },
                {
                    "name" : "time",
                    "type" : "variable",
                    "datatype" : "f8",
                    "data" : 100
                },
            ]
        }
    ]
}
```

### List of group properties

For completeness, here is the list of available properties for each group object:

- `type`: Equal to "group" for groups.
- `name`: Name of the group.
- `dimensions`: Define dimensions available to variables in the group. Array of objects, each object representing a different dimension, and containing the properties:
    - `name`: Name of the dimension.
    - `size`: Size of the dimension. Omit size for unlimited dimensions.
- `attributes`: Define attributes of the group. Array of objects, each object representing a different attribute, and containing the properties:
    - `name`: Name of the attribute.
    - `value`: Value of the attribute.
- `data`: Array of objects that represent either variables or sub-groups within the group.

### List of variable properties

- `type`: Equal to "variable" for variables.
- `name`: Name of the group
- `dimensions`: An array of pre-defined dimension names that the variable has, the length of the array thus equalling the dimensionality of the variable. Omit for scalar variables.
- `datatype`: The data type of the variable, which is a character string following numpy data type character reference conventions, in the same way as the [netcdf4-python library does](http://unidata.github.io/netcdf4-python/#netCDF4.Dataset).
- `attributes`: Define attributes of the variable. Array of objects, each object representing a different attribute, and containing the properties:
    - `name`: Name of the attribute.
    - `value`: Value of the attribute.
- `data`: The data to the stored in the variable.