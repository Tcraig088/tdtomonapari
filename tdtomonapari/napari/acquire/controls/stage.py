from qtpy.QtWidgets import QWidget, QComboBox, QLabel, QHBoxLayout, QLineEdit, QVBoxLayout, QPushButton, QGridLayout, QDoubleSpinBox
from qtpy.QtCore import Qt
import importlib
import inspect
import json
import os
import numpy as np
import copy
from tomoacquire.registrations import TOMOACQUIRE_MICROSCOPES
from tomoacquire.microscopes.temscript import TEMScriptMicroscope
from tomobase import TOMOBASE_DATATYPES
from tomoacquire.states import MicroscopeState
from tomoacquire.controllers.controller import TOMOACQUIRE_CONTROLLER
from tomoacquire.scanwindow import ScanWindow
from tdtomonapari.napari.base.components import CollapsableWidget
from tdtomonapari.napari.base.components import CheckableComboBox
from tdtomonapari.napari.base.utils import get_function_widgets, set_values, connect_widget, get_values
from tomoacquire import config
from tomobase.log import logger
import threading
from tomobase.data import Sinogram, Image
import inspect
import numpy as np
  
class StageWidget(QWidget):
    def __init__(self, microscope, viewer=None, parent=None):
        super().__init__(parent)
        self.viewer = viewer
        if not inspect.isclass(microscope) and microscope is not None:
            self.microscope = microscope
            self.widgets_list = get_function_widgets(self.microscope.set_stage_positions, self.viewer)
            values = self.microscope.get_stage_positions()  
            set_values(self.widgets_list, self.convertValues(values, reverse=True))
            for item in self.widgets_list:
                connect_widget(item, self.onStageChanged, self.viewer)

            self.layout = QVBoxLayout()
            for i, item in enumerate(self.widgets_list):
                self.layout.addWidget(item.widget)

            self.setLayout(self.layout)
            self.layout.setAlignment(Qt.AlignTop)
        else:
            logger.warning("Microscope is not initialized")

    def onStageChanged(self, value):
        values = get_values(self.widgets_list)
        values = self.convertValues(values, reverse=False)
        positions = self.microscope.get_stage_positions()
        _dict = {}
        for key, value in values.items():
            if not np.isclose(positions[key], value, atol=1e-6):
                _dict[key] = value
        self.microscope.set_stage_positions(_dict)

    def convertValues(self, values, reverse=False):
        if reverse:
            for key, value in values.items():
                if key == 'x':
                    values[key] = value * 10**(6)
                elif key == 'y':
                    values[key] = value * 10**(6)
                elif key == 'z':
                    values[key] = value * 10**(6)
                elif key == 'tilt':
                    values[key] = np.radians(value)
        else:
            for key, value in values.items():
                if key == 'x':
                    values[key] = value * 10**(-6)
                elif key == 'y':
                    values[key] = value * 10**(-6)
                elif key == 'z':
                    values[key] = value * 10**(-6)
                elif key == 'tilt':
                    values[key] = np.degrees(value)

        return values


        

