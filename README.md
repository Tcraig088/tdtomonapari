# Time-Dependent Tomography Napari Plugin
![OS](https://img.shields.io/badge/os-Windows%20|%20Linux-lightgray)
![Code](https://img.shields.io/badge/python-3.10%20|%203.11%20|%203.12-yellow)
![License](https://img.shields.io/badge/license-GPL3.0-blue)
![Version](https://img.shields.io/badge/version-v0.0.1-blue)
![Testing](https://img.shields.io/badge/test-Experimental-orange)
![build](https://img.shields.io/badge/tested%20build-Windows%2011%20|%20Ubuntu%2024.04-orange)

## Table of Contents

 - **Overview**
   - [**Section 1. Description**](#1-description)
   - [**Section 2. Installation**](#2-installation)
   - [**Section 3. Usage**](#3-usage)
   - [**Section 3. Usage**](#4-license)
  
## 1. Description

The Time-Dependent Tomography Napari Plugin (tdtomonapari) is a Napari plugin allowing the usage of a number of python libraries for scanning transmission electron tomography (STEM) with time-resolution in Napari. It is part of the [Time-Depenedent Tomography](https://google.co.nz) Library. As a Napari plugin it is the only library in the project that does not have extensive APIs for usage in a Juypter Notebook. The library is intended for providing a hook for create a Napari gui for the following libraries.

1. [**TomoBase:**](https://google.co.nz) A base library for common tomography tasks such as alignment, reconstruction and post processing.
2. [**TomoAcquire:**](https://google.co.nz) A library for connecting to the microscope and acquiring tomography data.
3. [**TomoNDT:**](https://google.co.nz) A library for GPU accelerated processing of volume-time data with support for BLOSC compressed data storage.


## 2. Installation

This library can be installed independently of all other projects except tomobase. Unlike other libraries this one is dependent on backend gui support. Hence, either  [PyQt5](https://google.co.nz) **or** [PySide2](https://google.co.nz) must be installed with it. For conda installation, run the following in your environment (replace X.X with the Cuda Toolkit Version supported by your device):


```bash
conda install tdtomonapari cudatoolkit=X.X pyqt -c TCraig088 -c conda-forge
```

Equally, the tdtomonapari can be installed through the Napari Plugins Market.

## 3. Usage
To use the library open Napari and Select Time-Dependent Tomography from the plugins window. 

## 4. License
This code is licensed under GNU general public license version 3.0.



