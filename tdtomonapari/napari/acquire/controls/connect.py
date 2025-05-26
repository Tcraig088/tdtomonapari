from qtpy.QtWidgets import QWidget, QComboBox, QLabel, QHBoxLayout, QLineEdit, QVBoxLayout, QPushButton, QGridLayout, QDoubleSpinBox
from qtpy.QtCore import Qt, Signal
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
from tdtomonapari.napari.base.utils import get_function_widgets, get_values
from tomoacquire import config
from tomobase.log import logger
import threading
from tomobase.data import Sinogram, Image

class ConnectSettingsWidget(CollapsableWidget):
    def __init__(self, title, microscope, viewer, parent):
        super().__init__(title, parent)
        self.viewer = viewer
        self.microscope = microscope
        self.isconnected = False
        self.widget_list = get_function_widgets(self.microscope.__init__, self.viewer)
        self.button = QPushButton('Connect')

        self.layout = QVBoxLayout()
        for i, item in enumerate(self.widget_list):
            self.layout.addWidget(item.widget)

        self.layout.addWidget(self.button)
        self.setLayout(self.layout)

    def onConnect(self):
        if not self.isconnected:
            _dict = {}
            values = get_values(self.widget_list)
            self.microscope = self.microscope( **values)
            self.button.setText('Disconnect')
            for widget in self.widget_list:
                widget.widget.setEnabled(False)
            msg = self.microscope.connect()
            logger.info(msg)
            self.isconnected = True
        else:
            self.microscope.disconnect()
            for widget in self.widget_list:
                widget.widget.setEnabled(True)
            self.button.setText('Connect')

        return self.microscope
    
class ConnectWidget(QWidget):
    microscope_updated = Signal(object)
    def __init__(self, microscope, viewer=None, parent=None):
        super().__init__(parent)
        self.viewer = viewer
        self.microscope = microscope
        self.microscope_combobox = QComboBox(self)
        self.microscope_combobox.addItem("Select Microscope")
        for key, value in TOMOACQUIRE_MICROSCOPES.items():
            self.microscope_combobox.addItem(value.name)

        self.microscope_combobox.currentTextChanged.connect(self.onSelect)
        if self.microscope is None:
            self.microscope_combobox.setCurrentText("Select Microscope")
        else:
            self.microscope_combobox.setCurrentText(self.microscope.tomobase_name)
        
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
        self.microscope_updated.emit(self.microscope)
        

