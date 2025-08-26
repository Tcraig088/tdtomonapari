# Time-Dependent Tomography Napari Plugin
![OS](https://img.shields.io/badge/os-Windows%20|%20Linux-lightgray)
![Code](https://img.shields.io/badge/python-3.10%20|%203.11%20|%203.12-yellow)
![License](https://img.shields.io/badge/license-GPL3.0-blue)
![Version](https://img.shields.io/badge/version-v0.0.1-blue)
![Testing](https://img.shields.io/badge/test-Experimental-orange)
![build](https://img.shields.io/badge/tested%20build-Windows%2011%20|%20Ubuntu%2024.04-orange)

## Description

This package is a Napari plugin allowing the usage of a number of python libraries for scanning transmission electron tomography (STEM) with time-resolution in Napari. The library is intended for providing a hook for create a Napari gui for the following libraries.

1. [**TomoBase:**](https://google.co.nz) A base library for common tomography tasks such as alignment, reconstruction and post processing.
2. [**TomoAcquire:**](https://google.co.nz) A library for connecting to the microscope and acquiring tomography data.
3. [**TomoNDT:**](https://google.co.nz) A library for GPU accelerated processing of volume-time data with support for BLOSC compressed data storage.


## nstallation

This library can be installed independently of all other projects except tomobase. Unlike other libraries this one is dependent on backend gui support. Follow the instructions for the installation of (Tomo Base)[https://tomobase.readthedocs.io/en/latest/] and install Napari before installing the library. TomoAcquire and TomoNDT can be installed optionally


```bash
conda install napari -c conda-forge
pip install -e . 
```

## Usage
All data classes inherited from Tomo Base support viewing as a napari layer using the to_data_tuple() and from_data_tuple() methods.


```python
import tomobase.data as data
import tomobase.phantoms as phantoms
import napari

# Initialize Viewer
viewer = napari.Viewer()

#get volume and convert tot layer tuple
vol = phantoms.get_nanocage()
data_tuple = vol.to_data_tuple()

viewer.add_image(data_tuple[0], data_tuple[1])

#export Volume from napari layer
vol2 = data.Volume.from_data_tuple(napari.layers[0])

```

To use with the napari browser. Open "Continous Tomography" in plugins this will create a Continous Tomography menu in the toolbar with access to all functions in the supported libraries 

## License
This code is licensed under GNU general public license version 3.0.



