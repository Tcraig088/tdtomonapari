from qtpy.QtWidgets import QWidget, QCheckBox, QSlider,QComboBox, QLabel, QHBoxLayout, QLineEdit, QVBoxLayout, QPushButton, QGridLayout, QDoubleSpinBox
from qtpy.QtCore import Qt, QObject, Signal
import importlib
import inspect
import json
import os
import numpy as np


from tomobase import TOMOBASE_DATATYPES
from tomoacquire.controllers.controller import TOMOACQUIRE_CONTROLLER
from tomoacquire.states import MicroscopeState
from tomoacquire.scanwindow import ScanWindow
from tdtomonapari.napari.base.components import CollapsableWidget
from tdtomonapari.napari.base.components import CheckableComboBox
from tomobase.data import Sinogram, Image
 
class ScanWidget(QWidget):
    def __init__(self, viewer=None, parent=None):
        super().__init__(parent)
        self.viewer = viewer
        self.magnifications_slider = QSlider(Qt.Horizontal)
        self.magnifications_slider.setMinimum(0)
        self.magnifications_slider.setMaximum(len(TOMOACQUIRE_CONTROLLER.microscope.magnification_options)-1)
        self.blanked_checkbox = QCheckBox('Blanked') 
        self.blanked_checkbox.setChecked(TOMOACQUIRE_CONTROLLER.microscope.isblank)
        self.acq_button = QPushButton('Acquire')

        self.layout = QGridLayout()
        self.layout.addWidget(QLabel('Magnification'), 0, 0)
        self.layout.addWidget(self.magnifications_slider, 1, 0, 1, 2)
        self.layout.addWidget(self.blanked_checkbox, 2, 0, 1, 2)
        self.layout.addWidget(self.acq_button, 3, 0, 1, 2)
        
        self.layout.setAlignment(Qt.AlignTop)
        self.setLayout(self.layout)
        
        self.acq_button.clicked.connect(self.on_acquire_clicked)
        self.magnifications_slider.valueChanged.connect(self.on_magnification_changed)
        self.blanked_checkbox.stateChanged.connect(self.on_blank_changed)

    def on_magnification_changed(self):
        TOMOACQUIRE_CONTROLLER.microscope.set_magnification(self.magnifications_slider.value())

    def on_blank_changed(self):
        TOMOACQUIRE_CONTROLLER.microscope.isblank = self.blanked_checkbox.isChecked()

    def on_acquire_clicked(self):
        TOMOACQUIRE_CONTROLLER.microscope.set_scan_mode(False)

