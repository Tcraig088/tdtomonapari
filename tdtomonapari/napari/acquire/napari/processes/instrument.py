from qtpy.QtWidgets import QWidget, QComboBox, QLabel, QHBoxLayout, QLineEdit, QVBoxLayout, QPushButton, QGridLayout, QDoubleSpinBox
from qtpy.QtCore import Qt
import importlib
import inspect
import json
import os
import numpy as np


from tomobase import TOMOBASE_DATATYPES
from tomoacquire.scanwindow import ScanWindow

class ScanSettingsWidget(CollapsableWidget):
    def __init__(self, title, parent):
        super().__init__(title, parent)
        self.label_dwell_time = QLabel('Dwell Time (\u03BCs):')
        self.double_spinbox_dwell_time = QDoubleSpinBox()
        self.double_spinbox_dwell_time.setSingleStep(0.01)
        self.double_spinbox_dwell_time.setValue(1.0)
        self.label_frame_size = QLabel('Frame Size (px):')
        self.combobox_frame_size = QComboBox()
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
        
        
class CustomConnectionWidget(CollapsableWidget):
    def __init__(self, parent=None):
        super().__init__('Microscope Settings', parent)
        
        self.label_name = QLabel('Name:')
        self.lineedit_name = QLineEdit('Microscope')
        self.label_connection = QLabel('Address:')
        self.lineedit_connection = QLineEdit('localhost')
        self.label_socket_request = QLabel('Request Socket:')
        self.lineedit_request = QLineEdit('50030')
        self.label_socket_reply = QLabel('Reply Socket:')
        self.lineedit_socket_reply = QLineEdit('50031')
        self.button_save = QPushButton('Save')
        self.button_delete = QPushButton('Delete')

        self.layout = QGridLayout()
        self.layout.addWidget(self.label_name, 0, 0)
        self.layout.addWidget(self.lineedit_name, 0, 1)
        self.layout.addWidget(self.label_connection, 0, 2 )
        self.layout.addWidget(self.lineedit_connection, 0, 3)
        self.layout.addWidget(self.label_socket_request, 1, 0)
        self.layout.addWidget(self.lineedit_request, 1, 1)
        self.layout.addWidget(self.label_socket_reply, 1, 2)
        self.layout.addWidget(self.lineedit_socket_reply, 1, 3)
        self.layout.addWidget(self.button_save, 2, 0)
        self.layout.addWidget(self.button_delete, 2,1)

        self.layout.setAlignment(Qt.AlignLeft)
        self.setLayout(self.layout)

    def clear(self):
        self.lineedit_name.clear()
        self.lineedit_connection.clear()
        self.lineedit_request.clear()
        self.lineedit_socket_reply.clear()

    def setDefaults(self):
        self.clear()
        self.lineedit_name.setText('Microscope')
        self.lineedit_connection.setText('localhost')
        self.lineedit_request.setText('50030')
        self.lineedit_socket_reply.setText('50031')
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
        data['subscribe'] = self.lineedit_socket_reply.text()
        
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
        data['subscribe'] = self.lineedit_socket_reply.text()

        spec = importlib.util.find_spec('tomoacquire')
        path = os.path.dirname(spec.origin)
        path = os.path.join(path, 'microscopes')
        filename = data['name'].replace(' ','_') + '.json'
        path = os.path.join(path, filename)

        if os.path.exists(path):
            os.remove(path)

class InstrumentWidget(QWidget):
    def __init__(self, viewer=None, parent=None):
        super().__init__(parent)
        self.combobox = QComboBox()
        self.viewer = viewer
        #TODO: check for registed microscope configs
        self.updateMicroscopes()

        self.connection_widget = CustomConnectionWidget()
        self.button_connect = QPushButton('Connect')
        
        self.connection_widget.setVisible(False)
        
        self.combobox_options = CheckableComboBox(self)
        self.combobox_options.addItem("Select Options")
        self.combobox_options.addItem("Manual Frame Time")
        self.combobox_options.addItem("Correct Backlash")
        self.combobox_options.addItem("Manual Screen Current")
        
        self.combobox_detectors = CheckableComboBox(self)
        self.combobox_detectors.addItem("Select Detectors")

        self.acquisition_settings = ScanSettingsWidget('Acquisition Settings:', self)  
        self.scan_settings = ScanSettingsWidget('Scanning Settings:', self)
        
        self.button_confirm = QPushButton('Confirm')   
        
        self.layout = QGridLayout()
        self.layout.addWidget(self.combobox, 0, 0)
        self.layout.addWidget(self.connection_widget, 1, 0, 1, 2)
        self.layout.addWidget(self.button_connect, 2, 0)

        self.layout.addWidget(self.combobox_options, 3, 0)
        self.layout.addWidget(self.combobox_detectors, 4, 0)
        
        self.layout.addWidget(self.acquisition_settings, 5, 0, 1, 2)
        self.layout.addWidget(self.scan_settings, 6, 0, 1, 2)
        
        self.layout.addWidget(self.button_confirm, 7, 0, 1, 2)

        self.layout.setAlignment(Qt.AlignTop)
        self.setLayout(self.layout)
        
        self.combobox.setCurrentIndex(0)
        self.combobox.currentIndexChanged.connect(self.onMicroscopeChange)
        self.button_connect.clicked.connect(self.onConnect)
        self.connection_widget.button_save.clicked.connect(self.onSave)
        self.connection_widget.button_delete.clicked.connect(self.onDelete)
        self.button_confirm.clicked.connect(self.onConfirm) 

    def updateMicroscopes(self):  
        self.combobox.clear()
        self.combobox.addItem('Select Microscope') 
        spec = importlib.util.find_spec('tomoacquire')
        path = os.path.dirname(spec.origin)
        path = os.path.join(path, 'microscopes')

        for files in os.listdir(path):
            if files.endswith('.json'):
                with open(os.path.join(path, files)) as f:
                    data = json.load(f)
                    self.combobox.addItem(data['name'])
        self.combobox.addItem('Custom')

    def onMicroscopeChange(self, index):
        if self.combobox.currentText() != 'Select Microscope':
            if self.combobox.currentText() == 'Custom':
                self.connection_widget.setDefaults()
            else:
                spec = importlib.util.find_spec('tomoacquire')
                path = os.path.dirname(spec.origin)
                path = os.path.join(path, 'microscopes')
                filename = self.combobox.currentText().replace(' ','_') + '.json'
                path = os.path.join(path, filename)
                if filename != '.json':
                    with open(path) as f:
                        data = json.load(f)
                        self.connection_widget.setFromJSON(data)
            self.connection_widget.setVisible(True)
        else:
            self.connection_widget.setVisible(False)

    def onConnect(self):    
        pass

    def onConfirm(self):
        data = np.zeros((1024,1024, 2))
        scan_window = ScanWindow(data, 1.0)
        value = scan_window._to_napari_layer(astuple=True)
        self.viewer._add_layer_from_data(*value)

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
        
    
    