from qtpy.QtWidgets import QWidget, QComboBox, QLabel, QHBoxLayout, QLineEdit, QVBoxLayout, QPushButton, QGridLayout, QDoubleSpinBox
from qtpy.QtCore import Qt

from tomobase.napari.components import CheckableComboBox, FileSaveDialog
from tomobase.registrations.tiltschemes import TOMOBASE_TILTSCHEMES
from tomobase.log import logger
  
class ExperimentWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.filedialog = FileSaveDialog()
        self.filedialog.set_extensions(mrc='Medical Research Council', tiff='Tagged Image File Format')
        
        self.label_maginification = QLabel('Magnification:')
        self.combobox_maginification = QComboBox()
        self.combobox_maginification.addItem('Select Magnification')
        self.combobox_maginification.setCurrentIndex(0)
        
        self.label_options = QLabel('Options:')
        self.combobox_options = CheckableComboBox(self)
        self.combobox_options.addItem("Select Options")
        
        self.label_tiltscheme = QLabel('Tilt Scheme:')  
        self.combobox_tiltscheme = QComboBox()
        self.combobox_tiltscheme.addItem('Select Tilt Scheme')
        for key, value in TOMOBASE_TILTSCHEMES.items():
            self.combobox_tiltscheme.addItem(key.lower())
        self.combobox_tiltscheme.setCurrentIndex(0)
        self.widget_tiltscheme = None
        
        self.button_confirm = QPushButton('Confirm')
        
        self.layout = QGridLayout()
        self.layout.addWidget(self.filedialog, 0, 0, 1, 3)
        self.layout.addWidget(self.label_maginification, 1, 0)
        self.layout.addWidget(self.combobox_maginification, 1, 1)
        self.layout.addWidget(self.label_options, 2, 1)
        self.layout.addWidget(self.combobox_options, 2, 1)
        self.layout.addWidget(self.label_tiltscheme, 3, 0)
        self.layout.addWidget(self.combobox_tiltscheme, 3, 1)
        
        self.layout.addWidget(self.button_confirm, 5, 0)

        self.layout.setAlignment(Qt.AlignTop)
        self.setLayout(self.layout)
        
        self.combobox_tiltscheme.currentIndexChanged.connect(self.onTiltschemeChange)
        
    def onTiltschemeChange(self, index):
        if self.widget_tiltscheme is not None:
            self.layout.removeWidget(self.widget_tiltscheme)
            self.widget_tiltscheme.deleteLater()
            self.widget_tiltscheme = None
            
        if self.combobox_tiltscheme.currentIndex() > 0:
            tiltscheme = TOMOBASE_TILTSCHEMES[self.combobox_tiltscheme.currentText().upper()]
            self.widget_tiltscheme = tiltscheme.widget()
            logger.debug(f"Widget: {self.widget_tiltscheme}")
            self.layout.addWidget(self.widget_tiltscheme, 4, 0, 1, 3)
        
    