from qtpy.QtWidgets import QWidget, QComboBox, QLabel, QHBoxLayout, QLineEdit, QVBoxLayout, QPushButton, QGridLayout, QDoubleSpinBox
from qtpy.QtCore import Qt
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

class ScanSettingsWidget(CollapsableWidget):
    def __init__(self, title, parent):
        super().__init__(title, parent)
        self.label_dwell_time = QLabel('Dwell Time (\u03BCs):')
        self.double_spinbox_dwell_time = QDoubleSpinBox()
        self.double_spinbox_dwell_time.setSingleStep(0.01)
        self.double_spinbox_dwell_time.setValue(1.0)
        self.label_frame_size = QLabel('Frame Size (px):')
        self.combobox_frame_size = QComboBox()
        self.combobox_frame_size.addItem('2048')
        self.combobox_frame_size.addItem('1024')
        self.combobox_frame_size.addItem('512')
        self.combobox_frame_size.addItem('256')
        self.label_frame_time= QLabel('Frame Time (s):')
        self.double_spinbox_frame_time = QDoubleSpinBox()
        self.double_spinbox_frame_time.setSingleStep(0.01)
        self.double_spinbox_frame_time.setValue(1.0)
        
        self.layout = QGridLayout()
        self.layout.addWidget(self.label_dwell_time, 0, 0)
        self.layout.addWidget(self.double_spinbox_dwell_time, 0, 1)
        self.layout.addWidget(self.label_frame_size, 1, 0)
        self.layout.addWidget(self.combobox_frame_size, 1, 1)
        self.layout.addWidget(self.label_frame_time, 2, 0)
        self.layout.addWidget(self.double_spinbox_frame_time, 2, 1)
        
        self.setLayout(self.layout)

class InstrumentWidget(QWidget):
    def __init__(self, viewer=None, parent=None):
        super().__init__(parent)
        self.viewer = viewer

        self.combobox_detectors = CheckableComboBox(self)
        self.combobox_detectors.addItem("Select Detectors")
        for detector in TOMOACQUIRE_CONTROLLER.microscope.detector_options:
            self.combobox_detectors.addItem(detector)

        self.screencurrent_label = QLabel('Screen Current:')
        self.screencurrent_lineedit = QLineEdit('0.0')
        self.acquisition_settings = ScanSettingsWidget('Acquisition Settings:', self)  
        self.scan_settings = ScanSettingsWidget('Scanning Settings:', self)
        self.button_confirm = QPushButton('Confirm')   
        
        self.layout = QGridLayout()
        self.layout.addWidget(self.combobox_detectors, 0, 0)
        self.layout.addWidget(self.screencurrent_label, 1, 1)
        self.layout.addWidget(self.screencurrent_lineedit, 1, 2)
        self.layout.addWidget(self.acquisition_settings, 2, 0, 1, 2)
        self.layout.addWidget(self.scan_settings, 3, 0, 1, 2)
        
        self.layout.addWidget(self.button_confirm, 4, 0, 1, 2)

        self.layout.setAlignment(Qt.AlignTop)
        self.setLayout(self.layout)
        
        self.button_confirm.clicked.connect(self.onConfirm) 

    def onConfirm(self):
        if TOMOACQUIRE_CONTROLLER.states != MicroscopeState.CONNECTED:
            TOMOACQUIRE_CONTROLLER.set_scan(self.scan_settings.Parse())
            TOMOACQUIRE_CONTROLLER.set_acquisition(self.acquisition_settings.Parse())
            TOMOACQUIRE_CONTROLLER.set_detectors(self.combobox_detectors.getCheckedItems())
            TOMOACQUIRE_CONTROLLER.states = MicroscopeState.DetectorsInitialized
        else:
            TOMOACQUIRE_CONTROLLER.states = MicroscopeState.CONNECTED

        scan_window = Image(TOMOACQUIRE_CONTROLLER)
        value = scan_window._to_napari_layer(astuple=True)
        self.viewer._add_layer_from_data(*value)

        
    
    