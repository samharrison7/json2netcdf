#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
import numpy as np
import json2netcdf

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

def test_var():
    with json2netcdf.convert(from_json=os.path.join(root_dir, 'example/data.json'),
                             diskless=True) as nc_file:
        assert nc_file['var_group']['spatial_var'][:].shape == (2,2)
        assert nc_file['var_group']['spatial_var'][:].sum() == 10
        assert nc_file['var_group']['spatiotemporal_var'].dtype == 'float64'

def test_attr():
    with json2netcdf.convert(from_json=os.path.join(root_dir, 'example/data.json'),
                             diskless=True) as nc_file:
        assert nc_file.author == 'Sam Harrison' 

def test_external():
    with json2netcdf.convert(from_json=os.path.join(root_dir, 'example/external.json'),
                             diskless=True) as nc_file:
        assert nc_file['external_group']['string_var'][:] == 'hello'
        assert nc_file['external_var'][:].sum() == 20.9365634

def test_file_creation(tmp_path):
    nc_path = os.path.join(tmp_path, 'test.nc')
    nc_file = json2netcdf.convert(from_json={}, to_netcdf=nc_path)
    assert os.path.isfile(nc_path)
    nc_file.close()

def test_dict_to_nc():
    data = {
        'dimensions': {
            'x': 10
        },
        'var[x]': np.full((10,), 42)
    }
    with json2netcdf.convert(from_json=data, diskless=True) as nc_file:
        assert np.array_equal(nc_file['var'][:], np.full((10,), 42))