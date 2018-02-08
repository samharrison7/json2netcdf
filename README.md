# json2netcdf

This is a basic Python script to convert a JSON file to a NetCDF4 file, using the [netCDF4](https://github.com/Unidata/netcdf4-python) Python library. It is very much a *work in progress* and no real error checking occurs (though netCDF4-python contains its own error checking) - make sure your JSON file follows exactly the structure it should! It only implements a small subset of what is actually possible in creating a NetCDF file.

There are numerous NetCDF to JSON parsers, but none that I could find that perform the reverse operation. The motivation? I wanted a quick and easy way to write NetCDF input files without having to write or modify a script for every new input file. JSON files are simple, easy to understand and write, and, crucially, follow a hierarchical format.

## Running

Simply run the script, and if you like, specify the input and output file paths (these default to "data.json" and "data.nc"). Oh, and make sure you have the Python [netCDF4](https://github.com/Unidata/netcdf4-python) library installed.

```bash
$ python json2netcdf.py input.json output.nc
```

## JSON input format

Take a look at the sample `data.json` for an idea of how to format your JSON file. The hierarchy mimics that of a NetCDF file, and each hierarchical level is represented by a `data` property, which contains an array of objects that are either groups or variables.

### Example

For example, say we wanted to mimic the following data structure:

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

The next level of the hierarchy is another group called "positions". Thus, the `data` property will be an array containing only one object, and that object will contain information about the "positions" group. Crucially, we need to give the group a `name` and tell the script that it is a group (and not a variable) by defining a `type`. Let's also put a `data` array in there, as we know "positions" will contain some variables:

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

NetCDF variables that aren't scalars need pre-defined dimensions given to them, and these dimensions can be defined by any group in the hierarchy. The "x" and "y" variables of the hierarchy we're trying to build both need a 1D array, of sizes 5 and 10, respectively. Let's define these dimensions in the root group (so they can be used in any sub-group), by the use of a `dimensions` property that contains an array of objects, each object representing a dimension with a `name` and `size`. Either omitting or setting `"size" : "unlimited"` will create an unlimited-size dimension.

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

Now, we can add those variables along with the "time" scalar to the positions group. Like groups, variables need a `name` and a `type`, the latter now being equal to "variable". Additionally, `dimensions` can be specified as an array of dimension names, as well as a `datatype` property, which represents the data type of the variable. These follow the [numpy data type](https://docs.scipy.org/doc/numpy/reference/arrays.dtypes.html) character code convention, in exactly the same fashion as the netcdf4-python library - [see here](http://unidata.github.io/netcdf4-python/#netCDF4.Dataset). For example, "f8" represents a 64-bit floating point number and "i4" a 32-bit signed integer. Scalars, like "time", don't need any dimensions specified. The variable value itself is represented in the `data` property.

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

We've now fully built the data structure originally specified. As a final flourish, we can assign some NetCDF attributes to the groups and variables, by specifying an `attributes` property, which contains an array of objects, each object representing a different attribute and containing a `name` and `value` property. These allow us to add metadata (e.g., description of a variable) to the data:

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

### Multiple input files

The main input file specified when running the script can contain reference to other JSON files in the JSON data structure, so that large data sets can be split. The external JSON file can either be specified as a separate item in the array of data objects (for groups or variables), or directly as a data object itself (only for variables). For example:

```json
"data" : [
    {
        "json" : "external.json"
    },
    {
        "name" : "a_variable",
        "type" : "variable",
        "datatype" : "f8",
        "data" : 100
    }
]
```

The above will replace that particular element of the data array with the data structure in the external.json file. A `name` property can be specified in the parent JSON file to override that in external.json:

```json
{
    "json" : "external.json",
    "name" : "name_to_override_group_name_in_external_file"
},
```

Alternatively, external data can be passed directly to the `data` property:

```json
{
    "name" : "a_variable",
    "type" : "variable",
    "datatype" : "f8",
    "data" : "external_data.json"
}
```

In this case, external_data.json would contain a real scalar. Obviously, this will be more useful with complex multi-dimensional data structures. See the [example data.json](example/data.json) file for example of this in action.

### List of group properties

For completeness, here is the list of available properties for each group object:

- `type`: Equal to "group" for groups.
- `name`: Name of the group.
- `dimensions`: Define dimensions available to variables in the group. Array of objects, each object representing a different dimension, and containing the properties:
    - `name`: Name of the dimension.
    - `size`: Size of the dimension. Set to "unlimited" or omit for unlimited-size dimension.
- `attributes`: Define attributes of the group. Array of objects, each object representing a different attribute, and containing the properties:
    - `name`: Name of the attribute.
    - `value`: Value of the attribute.
- `data`: Array of objects that represent either variables or sub-groups within the group.
- `json`: Path to external data file with further groups/variables. The top-level group/variable in the external file overrides any of the other properties specified in this group.

### List of variable properties

- `type`: Equal to "variable" for variables.
- `name`: Name of the group
- `dimensions`: An array of pre-defined dimension names that the variable has, the length of the array thus equalling the dimensionality of the variable. Omit for scalar variables.
- `datatype`: The data type of the variable, which is a character string following numpy data type character reference conventions, in the same way as the [netcdf4-python library does](http://unidata.github.io/netcdf4-python/#netCDF4.Dataset).
- `attributes`: Define attributes of the variable. Array of objects, each object representing a different attribute, and containing the properties:
    - `name`: Name of the attribute.
    - `value`: Value of the attribute.
- `data`: The data to be stored in the variable, or path to an external JSON file where the data are stored.

## json2netcdf-compact
A version of the script exists ([json2netcdf-compact.py](/json2netcdf-compact.py)) that allows much more "compact" and logical JSON structure to be converted than that documented above. This is the beginnings of the next version of json2netcdf but is currently undocumented. Use with caution! Here's a quick JSON example, which will result in an almost identical NetCDF file to the full JSON example above:

```json
{   
    "dimensions" : {
        "x_dim" : 5,
        "y_dim" : 10
    },
    "attributes" : {
        "description" : "Example data file.",
        "author" : "Sam Harrison"
    },
    "positions" : {
        "x[x_dim]" : [ 1.0, 1.1, 1.2, 1.3, 1.4 ],
        "y[y_dim]" : [ 1, 2, 3, 4, 5, 6, 7, 8, 9, 10 ]
    },
    "time" : 100
}
```