import magicgui
from magicgui.widgets import Combobox
from qtpy.QtWidgets import QWidget, QComboBox, QLabel, QHBoxLayout, QLineEdit, QVBoxLayout, QPushButton, QGridLayout, QDoubleSpinBox
from qtpy.QtCore import Qt, Signal

from tomoacquire.registrations import TOMOACQUIRE_DEVICE_TYPES

class MagicNewDeviceWidget(QWidget):
    closed = Signal()  # Custom signal to emit when the widget is closed
    
    def __init__(self, viewer, parent=None):
        super().__init__(parent)
        self.setWindowTitle("New Device")
        self.viewer = viewer

        self.combobox = Combobox(label='Device Type:', choices = self.getChoices())
        self.widget = None
        
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.combobox.native)
        self.setLayout(self.layout)
        self.layout.setAlignment(Qt.AlignTop)
        
        self.combobox.changed.connect(self.onComboboxChanged)

    def getChoices(self):
        choices = []
        choices.append(('Select Device Type', None))
        for key, item in TOMOACQUIRE_DEVICE_TYPES.items():
            choices.append((item.name, item.value))
        return choices
        
    def onComboboxChanged(self, value):
        if value is None:
            return
        
        if self.widget is not None:
            self.layout.removeWidget(self.widget)
            self.widget.deleteLater()
        
        controller = self.combobox.value
        self.widget = magicgui.magicgui(controller.register, auto_call=False, call_button='Save Device')
        self.layout.addWidget(self.widget.native)
        self.setLayout(self.layout)
        

    def closeEvent(self, event):
        self.closed.emit()
        super().closeEvent(event)