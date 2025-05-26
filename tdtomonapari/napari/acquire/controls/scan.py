from qtpy.QtWidgets import QWidget, QComboBox, QLabel, QHBoxLayout, QLineEdit, QVBoxLayout, QPushButton, QGridLayout, QDoubleSpinBox
from qtpy.QtCore import Qt
import numpy as np

from tomobase.log import logger
from tomobase.data import Sinogram, Image
import inspect
import numpy as np
import magicgui
from functools import partial
from typing import List

def set_scan(detectors:List[str], dwell_time:float=0.0, frame_size:int=1024, frame_time:float=0.0, microscope=None, isscan=True):
    """Set the stage positions."""
    __dict = {}
    __dict['isscan'] = isscan
    __dict['dwell_time'] = dwell_time * 10**(-6)  # convert to seconds
    __dict['frame_size'] = frame_size
    __dict['scan_time'] = frame_time
    __dict['detectors'] = detectors
    microscope.set_scan(**__dict)

def buildscanwidget(microscope=None, isscan=True, viewer=None, parent=None):
    if isscan:
        button = 'Scan'
    else:
        button = 'Acquire'
    detector_keys = list(microscope.detector_options.keys())
    widget = magicgui.magicgui(
        partial(set_scan, microscope=microscope, isscan=isscan),
        call_button=button,
        dwell_time={"min": 0.0, "max": 100.0, "value": 0.5},
        frame_size={"choices": [256, 512, 1024, 2048, 4096], "value": 1024},
        frame_time={"min": 0.0, "max": 100.0, "value": 0.63},
        detectors={"choices": detector_keys, "value": detector_keys[0]})
    return widget