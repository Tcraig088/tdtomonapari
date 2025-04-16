from tomobase.registrations.tiltschemes import TOMOBASE_TILTSCHEMES
from tdtomonapari.napari.base.components.collapsable import CollapsableWidget
from qtpy.QtWidgets import QWidget, QLabel, QComboBox, QGridLayout, QSpinBox, QVBoxLayout, QPushButton
from qtpy.QtCore import Qt, Signal
import inspect
from tdtomonapari.napari.base.utils import get_values, get_widgets
from tomobase.log import logger
import numpy as np
from tdtomonapari.registration import TDTOMONAPARI_VARIABLES
import coolname

class TiltSchemeWidget(CollapsableWidget):
    

    def __init__(self, tiltscheme, viewer, parent=None):
        super().__init__()
        self.viewer = viewer
        self.tiltscheme = tiltscheme
        self.widget_list = get_widgets(self.tiltscheme.__init__, self.viewer)

        self.layout = QVBoxLayout()
        for i, item in enumerate(self.widget_list):
            self.layout.addWidget(item.widget)

        self.layout.setAlignment(Qt.AlignTop)
        self.setLayout(self.layout)

class TiltSelectWidget(QWidget):
    closed  = Signal()

    
    def __init__(self, get_angles,  viewer: 'napari.viewer.Viewer', parent=None):
        super().__init__(parent)
        self.viewer = viewer
        self.setAttribute(Qt.WA_DeleteOnClose)

        self.get_angles = get_angles
        self.combobox_select = QComboBox()
        self.combobox_select.addItem('Select TiltScheme')
        for key, item in TOMOBASE_TILTSCHEMES.items():
            self.combobox_select.addItem(item.name.replace('_', ' ').capitalize())

        self.combobox_select.currentIndexChanged.connect(self.onComboboxChange)
        if get_angles:
            self.angles_widget = QSpinBox() 
            self.angles_widget.setRange(0, 1000000)
            self.angles_widget.setValue(70)
            self.tiltscheme_widget = None
        self.confirm_button = QPushButton('Confirm')   

        self.layout = QGridLayout()
        self.layout.addWidget(QLabel('Select TiltScheme'), 0, 0)
        self.layout.addWidget(self.combobox_select, 0, 1)
        if get_angles:
            self.layout.addWidget(QLabel('Number of Angles'), 1, 0)
            self.layout.addWidget(self.angles_widget, 1, 1)
        self.layout.addWidget(self.confirm_button, 3, 0, 1, 2)
        self.layout.setAlignment(Qt.AlignTop)
        self.setLayout(self.layout)

         
        self.confirm_button.clicked.connect(self.Parse)

    def onComboboxChange(self, index):
        if self.tiltscheme_widget is not None:
            self.layout.removeWidget(self.tiltscheme_widget)
            self.tiltscheme_widget.deleteLater()
            self.tiltscheme_widget = None

        if self.combobox_select.currentIndex() > 0:
            self.tiltscheme = TOMOBASE_TILTSCHEMES[self.combobox_select.currentText().upper().replace(' ', '_')].value
            self.tiltscheme_widget = TiltSchemeWidget(self.tiltscheme, self.viewer)
            self.layout.addWidget(self.tiltscheme_widget, 2, 0, 1, 2)
            self.tiltscheme_widget.show()

    def Parse(self):
        values = get_values(self.tiltscheme_widget.widget_list)
        obj = self.tiltscheme(**values)
        if self.get_angles:
            angles = np.array([obj.get_angle() for i in range(self.angles_widget.value())])
        else:
            angles = obj
        name = coolname.generate_slug(2)
        TDTOMONAPARI_VARIABLES[name] = angles
        TDTOMONAPARI_VARIABLES.refresh()

        self.close()
        self.closed.emit()