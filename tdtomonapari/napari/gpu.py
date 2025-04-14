from qtpy.QtWidgets import QApplication, QGridLayout, QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QGroupBox, QToolTip, QLabel, QComboBox, QHBoxLayout
from qtpy.QtCore import Qt
from qtpy.QtGui import QCursor

from tdtomonapari.registration import TDTOMONAPARI_VARIABLES
from tomobase.globals import logger, xp, GPUContext

class ContextWidget(QWidget):
    def __init__(self, viewer: 'napari.viewer.Viewer', parent=None):
        super().__init__(parent)
        # I need a table widget to display the variables
        self._viewer = viewer
        self._layout = QHBoxLayout()

        self.label_context = QLabel("Context:")
        self.combobox_context = QComboBox()
        self.combobox_context.addItem(GPUContext.NUMPY.name.capitalize())
        if xp._cupy_available:
            self.combobox_context.addItem(GPUContext.CUPY.name.capitalize())
        self.combobox_context.setCurrentText(xp.context.name.capitalize())

        self.label_device = QLabel("Device:")
        self.combobox_device = QComboBox()
        for i in range(xp.device_count):
            self.combobox_device.addItem(str(i))
        self.combobox_device.setCurrentText(str(xp.device))

        self._layout.addWidget(self.label_context)
        self._layout.addWidget(self.combobox_context)
        self._layout.addWidget(self.label_device)
        self._layout.addWidget(self.combobox_device)

        self.setLayout(self._layout)
        self._layout.setAlignment(Qt.AlignTop)

        self.combobox_context.currentTextChanged.connect(self.onContextChanged)
        self.combobox_device.currentTextChanged.connect(self.onContextChanged)

    def onContextChanged(self, value):
        context = GPUContext[self.combobox_context.currentText().upper()]
        device = int(self.combobox_device.currentText())
        xp.set_context(context, device)
 