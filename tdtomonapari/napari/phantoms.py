from functools import partial
from typing import List
from napari.types import LayerData
from tomobase.log import logger
from tomobase.globals import TOMOBASE_PHANTOMS
from napari.qt.threading import thread_worker
import time
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
            self.phantom_select.addItem(item.name.replace('_', ' ').capitalize())
        
        self.type_select = QComboBox()
        self.type_select.addItem('Volume')
        self.type_select.addItem('Sinogram')

        self.phantom_widget = QWidget()
        self.confirm_button = QPushButton('Confirm')   
        
        self.layout = QGridLayout()
        self.layout.addWidget(QLabel('Phantom:'), 0, 0)
        self.layout.addWidget(self.phantom_select, 0, 1)
        self.layout.addWidget(QLabel('Type:'), 1, 0)
        self.layout.addWidget(self.type_select, 1, 1)
        self.layout.addWidget(self.phantom_widget, 2, 0, 1, 2)

        self.setLayout(self.layout)
        self.phantom_select.currentIndexChanged.connect(self.onComboboxChange)

    def onComboboxChange(self, index):
        self.layout.removeWidget(self.phantom_widget)
        self.phantom_widget.deleteLater()
        self.phantom_widget = None

        if self.phantom_select.currentIndex() > 0:
            logger.info(f"Selected phantom: {self.phantom_select.currentText()}")
            process = TOMOBASE_PHANTOMS[self.phantom_select.currentText().replace(' ', '_').upper()]  
            phantom = build_phantoms_widget(process.value)
            self.phantom_widget = phantom.native
            phantom.called.connect(self.Parse)
        else:
            self.phantom_widget = QWidget()
        self.layout.addWidget(self.phantom_widget, 2, 0, 1, 2)  

    def Parse(self, result):
        napari.current_viewer().dims.ndisplay = 3
        if self.type_select.currentText() == 'Sinogram':
            napari.current_viewer().dims.ndisplay = 2
            ts = Incremental(-70, 70,2)
            angles = [ts.get_angle() for i in range(1, 71)]
            result = processes.project(result, angles)
        self.result = result.to_data_tuple()
        self.accept()

def build_phantoms_widget(function):
    # No call button, no auto_call; call must be triggered programmatically
    return magicgui.magicgui(function)


def load_phantom() -> List[LayerData]:
    """Load a phantom from the list of available phantoms."""
    viewer = napari.current_viewer()
    phantom_widget = PhantomSelectWidget(viewer=viewer)
    
    if phantom_widget.exec_() == QDialog.Accepted:
        selected_phantom = phantom_widget.result
    return [selected_phantom]

