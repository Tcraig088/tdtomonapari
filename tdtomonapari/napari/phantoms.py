from functools import partial
from typing import List
from napari.types import LayerData
from tomobase.log import logger
from tomobase.tiltschemes import GRS, Incremental
from tomobase import phantoms
from tomobase import processes
import napari
import magicgui
from qtpy.QtWidgets import (
    QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel, QDialog,
    QCheckBox, QComboBox, QGridLayout, QSpinBox, QDoubleSpinBox, QLineEdit
)
from qtpy.QtCore import Qt

class PhantomSelectWidget(QDialog):
    def __init__(self, viewer=None, parent=None):
        super().__init__(parent)
        self.viewer = viewer
        self.setWindowTitle("Select Phantom")
        self.setModal(True)
        
        self.phantom_select = QComboBox()
        self.phantom_select.addItem('Select Phantom')
        for key, item in TOMOBASE_PHANTOMS.items():
            self.combobox_select.addItem(item.name.replace('_', ' ').capitalize())
        
        self.phantom_widget = QWidget()
        self.confirm_button = QPushButton('Confirm')   
        
        self.layout = QGridLayout()
        self.layout.addWidget(QLabel('Phantom:'), 0, 0)
        self.layout.addWidget(self.phantom_select, 0, 1)
        self.layout.addWidget(self.phantom_widget, 1, 0, 1, 2)
        self.layout.addWidget(self.confirm_button, 2, 0)

        
        self.setLayout(self.layout)
        
        self.confirm_button.clicked.connect(self.parse_phantom)

    def onComboboxChange(self, index):
        self.layout.removeWidget(self.phantom_widget)
        self.phantom_widget.deleteLater()
        self.phantom_widget = None

        if self.phantom_select.currentIndex() > 0:
            process = TOMOBASE_PHANTOMS[self.phantom_select.currentText()]  
            phantom = build_phantoms_widget(self.phantom_select.currentText())
            self.phantom_widget = phantom.viewer()
        else:
            self.phantom_widget = QWidget()
        self.layout.addWidget(self.phantom_widget, 1, 0, 1, 2)  

def build_phantoms_widget(function):
    return magicgui.magicgui(function)

def _load_data(name, **kwargs) -> List[LayerData]:
    match name:
        case 'nanocage':
            obj = phantoms.nanocage()
            _dict =  kwargs
            _dict['name'] = 'Nanocage'
            napari.current_viewer().dims.ndisplay = 3
            layer = [obj.to_data_tuple(_dict)]
            return layer
        case 'nanocage2d':
            vol = phantoms.nanocage()
            grs = Incremental(-70, 70,2)
            angles = [grs.get_angle() for i in range(1, 71)]
            sino = processes.project(vol, angles)
            
            _dict =  kwargs
            _dict['name'] = 'Nanocage 2D'
            napari.current_viewer().dims.ndisplay = 2
            layer = [sino.to_data_tuple(_dict)]
            return layer
        case 'nanorod':
            obj = phantoms.nanorod()
            _dict =  kwargs
            _dict['name'] = 'Nanorod'
            napari.current_viewer().dims.ndisplay = 3
            layer = [obj.to_data_tuple(_dict)]
            return layer

# fmt: off
TDTOMO_NAPARI_SAMPLE_DATA = [
    'nanocage', 'nanocage2d', 'nanorod'
]

globals().update({key: partial(_load_data, key) for key in TDTOMO_NAPARI_SAMPLE_DATA})