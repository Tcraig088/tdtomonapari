from qtpy.QtWidgets import QWidget, QComboBox, QLabel, QHBoxLayout, QLineEdit, QVBoxLayout, QPushButton, QGridLayout, QDoubleSpinBox
from qtpy.QtCore import Qt
import importlib
import inspect
import json
import os
import numpy as np
import copy
from tomoacquire.registrations import TOMOACQUIRE_MICROSCOPES
from tomobase import TOMOBASE_DATATYPES
from tomoacquire.states import MicroscopeState
from tomoacquire.controllers.controller import TOMOACQUIRE_CONTROLLER
from tomoacquire.scanwindow import ScanWindow
from tdtomonapari.napari.base.components import CollapsableWidget
from tdtomonapari.napari.base.components import CheckableComboBox
from tdtomonapari.napari.base.utils import get_widgets, get_values
from tomoacquire import config
from tomobase.log import logger
import threading
from tomobase.data import Sinogram, Image

class ScanSettingsWidget(CollapsableWidget):
    def __init__(self, title, microscope, isscan, detectors, parent):
        super().__init__(title, parent)
        self.microscope = microscope
        self.isscan = isscan
        self.detectors_combobox = CheckableComboBox(self)
        self.detectors_label = QLabel('Select Detectors:')
        self.detectors_combobox.addItem("Select Detectors")
        for detector in detectors:
            self.detectors_combobox.addItem(detector)

        self.dwell_time_label = QLabel('Dwell Time (\u03BCs):')
        self.dwell_time_spinbox = QDoubleSpinBox()
        self.dwell_time_spinbox.setSingleStep(0.01)
        self.dwell_time_spinbox.setValue(0.5)

        self.frame_size_label = QLabel('Frame Size (px):')
        self.frame_size_combobox = QComboBox()
        self.frame_size_combobox.addItem('2048')
        self.frame_size_combobox.addItem('1024')
        self.frame_size_combobox.addItem('512')
        self.frame_size_combobox.addItem('256')

        self.frame_size_combobox.setCurrentText('1024')

        self.frame_time_label = QLabel('Frame Time (s):')
        self.frame_time_spinbox = QDoubleSpinBox()
        self.frame_time_spinbox.setSingleStep(0.01)
        self.frame_time_spinbox.setValue(0.63)

        self._layout = QGridLayout()
        self._layout.addWidget(self.detectors_label, 0, 0)
        self._layout.addWidget(self.detectors_combobox, 0, 1)
        self._layout.addWidget(self.dwell_time_label, 1, 0)
        self._layout.addWidget(self.dwell_time_spinbox, 1, 1)
        self._layout.addWidget(self.frame_size_label, 2, 0)
        self._layout.addWidget(self.frame_size_combobox, 2, 1)
        self._layout.addWidget(self.frame_time_label, 3, 0)
        self._layout.addWidget(self.frame_time_spinbox, 3, 1)

        self.setLayout(self._layout)


    def on_confirm(self):
        scan_dict = {}
        scan_dict['isscan'] = self.isscan
        scan_dict['dwell_time'] = self.dwell_time_spinbox.value() * 10**(-6)
        scan_dict['frame_size'] = int(self.frame_size_combobox.currentText())
        scan_dict['scan_time'] = self.frame_time_spinbox.value()
        scan_dict['detectors'] = self.detectors_combobox.getCheckedItems()
        
        self.microscope.set_scan(**scan_dict)


class MicroscopeWidget(QWidget):
    def __init__(self, viewer=None, parent=None):
        super().__init__(parent)
        self.viewer = viewer
        self.microscope_combobox = QComboBox(self)
        self.microscope_combobox.addItem("Select Microscope")
        for key, value in TOMOACQUIRE_MICROSCOPES.items():
            self.microscope_combobox.addItem(value.name)

        self.microscope_combobox.setCurrentText("Select Microscope")
        self.microscope_combobox.currentTextChanged.connect(self.onSelect)

        self.layout = QGridLayout()
        self.layout.addWidget(self.microscope_combobox, 0, 0 ,1, 2)
        self.setLayout(self.layout)
        #set alignment to top
        self.layout.setAlignment(Qt.AlignTop)

        self.connection_widget = None

    def onSelect(self):
        name = self.microscope_combobox.currentText()
        key = name.upper().replace(" ", "_")

        if self.connection_widget is not None:
            self.layout.removeWidget(self.connection_widget)
            self.connection_widget.deleteLater()
            self.connection_widget = None

        if key not in TOMOACQUIRE_MICROSCOPES._dict:
            logger.warning(f"Must Select a microscope")
        else:
            logger.debug(f"Selected {key} microscope")
            self.microscope = TOMOACQUIRE_MICROSCOPES[key].value
            self.connection_widget = ConnectSettingsWidget(f"Connection Settings", self.microscope, self.viewer, self)
            self.layout.addWidget(self.connection_widget, 1, 0, 1, 2)
            self.connection_widget.button.clicked.connect(self.onConnect)

    def onConnect(self):
        self.microscope = self.connection_widget.onConnect()
        msg = self.microscope.connect()
        self.detector_options = msg['detectors']
        detectors = []
        for key, value in self.detector_options.items():
            detectors.append(key)


        self.scan_button = QPushButton('Scan')
        self.acq_button = QPushButton('Acquire')
        self.scan_widget = ScanSettingsWidget('Scanning Settings:', self.microscope, isscan=True, detectors=detectors, parent=self)
        self.acqwidget = ScanSettingsWidget('Acquisition Settings:', self.microscope, isscan=False, detectors=detectors, parent=self)

        self.layout.addWidget(self.scan_widget, 2, 0, 1, 2)
        self.layout.addWidget(self.acqwidget, 3, 0, 1, 2)
        self.layout.addWidget(self.scan_button, 4, 0, 1, 1)
        self.layout.addWidget(self.acq_button, 4, 1, 1, 1)

        #set on_scan 1 or 0 to use acquisition or scanning settings
        self.scan_button.clicked.connect(lambda x: self.on_scan(True))
        self.acq_button.clicked.connect(lambda x: self.on_scan(False))

        self.thread_active = True
        self.threading = threading.Thread(target=self.observe, daemon=True)
        self.threading.start()

    def on_scan(self, value):
        if value:
            self.scan_widget.on_confirm()
            self.scan_button.setStyleSheet("background-color: green")

        else:
            self.acqwidget.on_confirm()
            self.acq_button.setStyleSheet("background-color: green")


    def observe(self):
        while self.thread_active:
            msg = self.microscope.subscribe_socket.recv_json()
            data = msg['data']
            shape = msg['shape']
            channels = msg['channels']
            img_data = np.zeros(channels, shape[0], shape[1])
            i=0
            for key, value in data.items():
                img = np.array(value).reshape(shape)
                img_data[i,:,:] = img
                i+=1
            
            layer_found = False
            if msg['isscan']:
                for layer in self.viewer.layers:
                    if layer.name == 'Scan Window':
                        layer.data = img_data
                        layer.refresh()
                        layer_found = True
                if not layer_found:
                    img = Image(img_data, pixelsize=1.0)
                    layerdata = img.to_data_tuple(attributes={'name': 'Scan Window'})
                    self.viewer._add_layer_from_data(*layerdata)
            else:
                self.on_scan(True)
                for layer in self.viewer.layers:
                    if layer.name == 'Acquisition Window':
                        layer.data = img_data
                        layer.refresh()
                        layer_found = True
                if not layer_found:
                    img = Image(img_data, pixelsize=1.0)
                    layerdata = img.to_data_tuple(attributes={'name': 'Acquisition Window'})
                    self.viewer._add_layer_from_data(*layerdata)

        self.microscope.observe(self.update_scan, self.update_acq)

    