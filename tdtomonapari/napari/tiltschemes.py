
from qtpy.QtWidgets import QDoubleSpinBox, QSpinBox, QGridLayout, QLabel

from tomobase.tiltschemes.tiltscheme  import TiltScheme
from tomobase.hooks import tomobase_hook_tiltscheme
from tdtomonapari.napari.base.components import CollapsableWidget

@tomobase_hook_tiltscheme('BINARY')
class BinaryWidget(CollapsableWidget):
    def __init__(self, parent=None):
        super().__init__('Binary Decomposition TiltScheme', parent)
        
        self.angle_max = QDoubleSpinBox()
        self.angle_max.setRange(-90, 90)
        self.angle_max.setValue(70)
        
        self.angle_min = QDoubleSpinBox()
        self.angle_min.setRange(-90, 90)
        self.angle_min.setValue(-70)
        
        self.index = QSpinBox()
        self.index.setRange(1, 1000)
        self.index.setValue(1)
        
        self.layout = QGridLayout()
        self.layout.addWidget(QLabel("Angle Max ('\u00B0')"), 0, 0)
        self.layout.addWidget(self.angle_max, 0, 1)
        self.layout.addWidget(QLabel("Angle Min ('\u00B0')"), 1, 0)
        self.layout.addWidget(self.angle_min, 1, 1)
        self.layout.addWidget(QLabel("Index"), 2, 0)
        self.layout.addWidget(self.index, 2, 1)
        
        self.setLayout(self.layout)
        
    def setTiltScheme(self):
        return Binary(self.angle_max.value(), self.angle_min.value(), self.index.value())

@tomobase_hook_tiltscheme('INCREMENTAL')
class IncrementalWidget(CollapsableWidget):
    def __init__(self, parent=None):
        super().__init__('Incremental TiltScheme', parent)
        
        self.angle_start = QDoubleSpinBox()
        self.angle_start.setRange(-90, 90)
        self.angle_start.setValue(-70)
        
        self.angle_end = QDoubleSpinBox()
        self.angle_end.setRange(-90, 90)
        self.angle_end.setValue(70)
        
        self.step = QDoubleSpinBox()
        self.step.setRange(0, 90)
        self.step.setValue(2)

        self.layout = QGridLayout()
        self.layout.addWidget(QLabel("Angle Start ('\u00B0')"), 0, 0)
        self.layout.addWidget(self.angle_start, 0, 1)
        self.layout.addWidget(QLabel("Angle End ('\u00B0')"), 1, 0)
        self.layout.addWidget(self.angle_end, 1, 1)
        self.layout.addWidget(QLabel("Step ('\u00B0')"), 2, 0)
        self.layout.addWidget(self.step, 2, 1)

        self.setLayout(self.layout)
        
    def setTiltScheme(self):
        return Incremental(self.angle_start.value(), self.angle_end.value(), self.step.value())
    
    
@tomobase_hook_tiltscheme('GRS')
class GRSWidget(CollapsableWidget):
    def __init__(self, parent=None):
        super().__init__('GRS TiltScheme', parent)
        
        self.angle_max = QDoubleSpinBox()
        self.angle_max.setRange(-90, 90)
        self.angle_max.setValue(70)
        
        self.angle_min = QDoubleSpinBox()
        self.angle_min.setRange(-90, 90)
        self.angle_min.setValue(-70)
        
        self.index = QSpinBox()
        self.index.setRange(1, 1000)
        self.index.setValue(1)
        
        self.layout = QGridLayout()
        self.layout.addWidget(QLabel("Angle Max ('\u00B0')"), 0, 0)
        self.layout.addWidget(self.angle_max, 0, 1)
        self.layout.addWidget(QLabel("Angle Min ('\u00B0')"), 1, 0)
        self.layout.addWidget(self.angle_min, 1, 1)
        self.layout.addWidget(QLabel("Index"), 2, 0)
        self.layout.addWidget(self.index, 2, 1)
        
        self.setLayout(self.layout)
        
    def setTiltScheme(self):
        return GRS(self.angle_max.value(), self.angle_min.value(), self.index.value())
    