from qtpy.QtWidgets import QWidget, QComboBox, QLabel, QHBoxLayout, QLineEdit, QVBoxLayout, QPushButton, QGridLayout, QDoubleSpinBox
from qtpy.QtCore import Qt
import numpy as np

from tomobase.log import logger
from tomobase.data import Sinogram, Image
import inspect
import numpy as np
import magicgui
from functools import partial

def set_stage(x: float = 0.0, y: float = 0.0, z: float = 0.0, tilt: float = 0.0, microscope=None):
    """Set the stage positions."""
    __dict = {}
    __dict['x'] = x * 1e-6
    __dict['y'] = y * 1e-6
    __dict['z'] = z * 1e-6
    __dict['tilt'] = np.radians(tilt)
    microscope.set_stage_positions(**__dict)

def buildstagewidget(microscope=None, viewer=None, parent=None):
    __dict = microscope.get_stage_positions()
    widget = magicgui.magicgui(
        partial(set_stage, microscope=microscope),
        call_button=False,
        auto_call=True,
        x={"min": -1000.0, "max": 1000.0, "value": __dict['x'] * 10**6},
        y={"min": -1000.0, "max": 1000.0, "value": __dict['y'] * 10**6},
        z={"min": -1000.0, "max": 1000.0, "value": __dict['z'] * 10**6},
        tilt={"min": -90.0, "max": 90.0, "value": np.degrees(__dict['tilt'])},
    )
    return widget

 

