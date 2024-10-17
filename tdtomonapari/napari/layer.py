from tomobase.registrations.datatypes import TOMOBASE_DATATYPES

from qtpy.QtWidgets import QWidget, QVBoxLayout, QLabel, QCheckBox, QComboBox, QGridLayout
from qtpy.QtCore import Qt

class LayerInfo(QWidget):
    def __init__(self, viewer, parent=None):
        super().__init__(parent)
        self.viewer = viewer
        
        self.label_name = QLabel("Name:")
        self.label_name_value = QLabel(" None Selected")
        self.label_layer_type = QLabel("Type:")
        self.label_layer_type_value = QLabel(" NA")
        self.widget = None
        
        self.layout = QGridLayout()
        self.layout.addWidget(self.label_name, 0, 0)
        self.layout.addWidget(self.label_name_value, 0, 1)
        self.layout.addWidget(self.label_layer_type, 1, 0)
        self.layout.addWidget(self.label_layer_type_value, 1, 1)

        
        self.layout.setAlignment(Qt.AlignTop)
        self.setLayout(self.layout)
        self.viewer.layers.selection.events.changed.connect(self.GetLayerSelection)
        
        self.GetLayerSelection()
        
    def GetLayerSelection(self):
        layer = self.viewer.layers.selection.active
        #set the layer widget to None and delecte from the layout
        if self.widget is not None:
            self.layout.removeWidget(self.widget)
            self.widget.deleteLater()
            self.widget = None
        if layer is None:
            self.label_name_value.setText(" None Selected")
            self.label_layer_type_value.setText(" NA")
        else:
            self.label_name_value.setText(layer.name)
            if 'ct metadata' not in layer.metadata:
                self.label_layer_type_value.setText("Not Supported")
            else:
                self.label_layer_type_value.setText(TOMOBASE_DATATYPES.key(layer.metadata['ct metadata']['type']))
                self.widget = TOMOBASE_DATATYPES.loc(layer.metadata['ct metadata']['type']).widget(self.viewer, self)
                self.layout.addWidget(self.widget, 2, 0, 1, 2)
        