from qtpy.QtWidgets import QWidget, QComboBox, QLabel, QHBoxLayout, QLineEdit, QVBoxLayout, QPushButton, QGridLayout, QDoubleSpinBox
from qtpy.QtCore import Qt
import importlib
import inspect
import json
import os
import numpy as np

from tomobase import TOMOBASE_DATATYPES
from tomoacquire.states import MicroscopeState
from tomoacquire.controllers.controller import TOMOACQUIRE_CONTROLLER
from tomoacquire.scanwindow import ScanWindow
from tdtomonapari.napari.base.components import CollapsableWidget
from tdtomonapari.napari.base.components import CheckableComboBox
from tomoacquire import config

class CustomConnectionWidget(CollapsableWidget):
    def __init__(self, parent=None):
        super().__init__('Microscope Settings', parent)
        
        self.label_name = QLabel('Name:')
        self.lineedit_name = QLineEdit('Microscope')
        self.label_connection = QLabel('Address:')
        self.lineedit_connection = QLineEdit('localhost')
        self.label_socket_request = QLabel('Port:')
        self.lineedit_request = QLineEdit('50030')
        self.button_save = QPushButton('Save')
        self.button_delete = QPushButton('Delete')

        self.layout = QGridLayout()
        self.layout.addWidget(self.label_name, 0, 0)
        self.layout.addWidget(self.lineedit_name, 0, 1)
        self.layout.addWidget(self.label_connection, 1, 0 )
        self.layout.addWidget(self.lineedit_connection, 1, 1)
        self.layout.addWidget(self.label_socket_request, 2, 0)
        self.layout.addWidget(self.lineedit_request, 2, 1)
        self.layout.addWidget(self.button_save, 3, 0)
        self.layout.addWidget(self.button_delete, 3,1)

        self.layout.setAlignment(Qt.AlignLeft)
        self.setLayout(self.layout)

    def clear(self):
        self.lineedit_name.clear()
        self.lineedit_connection.clear()
        self.lineedit_request.clear()

    def setDefaults(self):
        self.clear()
        self.lineedit_name.setText('Microscope')
        self.lineedit_connection.setText('localhost')
        self.lineedit_request.setText('50030')
        self.button_save.setText('Save')
        self.button_delete.setVisible(False)


    def setFromJSON(self, data):
        self.clear()
        self.lineedit_name.setText(data['name'])
        self.lineedit_connection.setText(data['connection'])
        self.lineedit_request.setText(data['request'])
        self.lineedit_socket_reply.setText(data['subscribe'])
        self.button_save.setText('Update')
        self.button_delete.setVisible(True)

    def onSave(self):
        data = {}
        data['name'] = self.lineedit_name.text()
        data['connection'] = self.lineedit_connection.text()
        data['request'] = self.lineedit_request.text()

        
        spec = importlib.util.find_spec('tomoacquire')
        path = os.path.dirname(spec.origin)
        path = os.path.join(path, 'microscopes')
        filename = data['name'].replace(' ','_') + '.json'
        path = os.path.join(path, filename)

        if os.path.exists(path):
            os.remove(path)
        with open(path, 'w') as f:
            json.dump(data, f)

    def onDelete(self):
        data = {}
        data['name'] = self.lineedit_name.text()
        data['connection'] = self.lineedit_connection.text()
        data['request'] = self.lineedit_request.text()

        spec = importlib.util.find_spec('tomoacquire')
        path = os.path.dirname(spec.origin)
        path = os.path.join(path, 'microscopes')
        filename = data['name'].replace(' ','_') + '.json'
        path = os.path.join(path, filename)

        if os.path.exists(path):
            os.remove(path)

class ConnectWidget(QWidget):
    def __init__(self, viewer=None, parent=None):
        super().__init__(parent)
        self.viewer = viewer
        self.combobox = QComboBox()
        self.updateMicroscopes()

        self.connection_widget = CustomConnectionWidget()
        self.button_connect = QPushButton('Connect')
        self.connection_widget.setVisible(False)        
 
        
        self.layout = QGridLayout()
        self.layout.addWidget(self.combobox, 0, 0)
        self.layout.addWidget(self.connection_widget, 1, 0, 1, 2)
        self.layout.addWidget(self.button_connect, 2, 0)


        self.layout.setAlignment(Qt.AlignTop)
        self.setLayout(self.layout)
        
        self.combobox.setCurrentIndex(0)
        self.combobox.currentIndexChanged.connect(self.onMicroscopeChange)
        self.button_connect.clicked.connect(self.onConnectDisconnect)
        self.connection_widget.button_save.clicked.connect(self.onSave)
        self.connection_widget.button_delete.clicked.connect(self.onDelete)

        if TOMOACQUIRE_CONTROLLER.state != MicroscopeState.DISCONNECTED:
            self.button_connect.setText('Disconnect')
            self.combobox.setCurrentText(TOMOACQUIRE_CONTROLLER.microscope.name)

    def updateMicroscopes(self):  
        self.combobox.clear()
        self.combobox.addItem('Select Microscope') 
        for item in config.get_names():
            self.combobox.addItem(item)
        self.combobox.addItem('Custom')

    def onMicroscopeChange(self, index):
        if self.combobox.currentText() != 'Select Microscope':
            if self.combobox.currentText() == 'Custom':
                self.connection_widget.setDefaults()
            else:
                self.connection_widget.setDefaults()
            self.connection_widget.setVisible(True)
        else:
            self.connection_widget.setVisible(False)

    def onConnectDisconnect(self):
        if TOMOACQUIRE_CONTROLLER.state == MicroscopeState.DISCONNECTED:    
            if self.combobox.currentText() != 'Custom' and self.combobox.currentText() != 'Select Microscope':
                microscope  = config.get_microscope(self.combobox.currentText())
                TOMOACQUIRE_CONTROLLER.connect(microscope)
                self.button_connect.setText('Disconnect')
        else:
            TOMOACQUIRE_CONTROLLER.disconnect()
            self.button_connect.setText('Connect')

        

    def onSave(self):
        """
        Save the current connection settings to a json file and update the combobox
        """
        self.connection_widget.onSave()
        self.updateMicroscopes()

    def onDelete(self):
        """
        Delete the current connection settings and update the combobox
        """
        self.connection_widget.onDelete()
        self.updateMicroscopes()
        