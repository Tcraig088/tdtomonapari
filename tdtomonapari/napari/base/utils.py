import inspect
import numpy as np
from dataclasses import dataclass

from tomobase.log import logger
from typing import Union, get_origin, get_args
from tomobase.data import Data, Sinogram, Image, Volume
from qtpy.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout,  QLabel, QCheckBox, QComboBox, QGridLayout, QSpinBox, QDoubleSpinBox, QLineEdit
from tomobase.typehints import TILTANGLETYPE
from collections.abc import Iterable
from tomobase.data import Data
from tomobase.registrations.datatypes import TOMOBASE_DATATYPES
from tdtomonapari.napari.base.components.collapsable import CollapsableWidget
from qtpy.QtWidgets import QWidget, QLabel, QComboBox, QGridLayout
from qtpy.QtCore import Qt
from tdtomonapari.registration import TDTOMONAPARI_VARIABLES

@dataclass
class WidgetStruct:
    name:str
    widget:object

class ItemWidget(QWidget):
    def __init__(self, label, widget, parent=None):
        super().__init__(parent)
        self.label = QLabel(label)
        self.widget = widget
        self.layout = QHBoxLayout()
        
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.widget)

        self.layout.setAlignment(Qt.AlignTop)
        self.setLayout(self.layout)

    def Parse(self):
        if isinstance(self.widget, QSpinBox):
            return self.widget.value()

        elif isinstance(self.widget, QDoubleSpinBox):
            return self.widget.value()

        elif isinstance(self.widget, QLineEdit):
            return self.widget.text()

        elif isinstance(self.widget, QCheckBox):
            return self.widget.isChecked()

        else:
            logger.warning(f'Widget {self} has an unsupported type')
            return



class LayerSelectWidget(CollapsableWidget):
    def __init__(self, title, layer_types, viewer: 'napari.viewer.Viewer', parent=None):
        super().__init__(title, parent)
        
        self.viewer = viewer
        #if iterable
        if get_origin(layer_types) is Union:
            layer_types = get_args(layer_types)
        if layer_types is Data:
            layer_types = []
            for key, value in TOMOBASE_DATATYPES.items():
                layer_types.append(value.name)
        else:
            layer_types = [layer_types]


        self.layer_types = [typ.get_type_id() for typ in layer_types]
        self.isfixed = False

        self.label_data = QLabel('Selected:')
        self.combobox_select = QComboBox()
        self.onLayerNumberChange()
        
        self.combobox_types = QComboBox()
        self.combobox_types.addItem('Selectable Datatypes')

        for id in self.layer_types:
            self.combobox_types.addItem(TOMOBASE_DATATYPES.loc(id).name)
        self.combobox_types.setCurrentIndex(0)
        
        self.layout = QGridLayout()
        self.layout.addWidget(self.label_data, 0, 0)
        self.layout.addWidget(self.combobox_select, 0, 1)
        self.layout.addWidget(self.combobox_types, 0, 2)
        
        self.layout.setAlignment(Qt.AlignTop)
        self.setLayout(self.layout)
        
        self.viewer.layers.events.inserted.connect(self.onLayerNumberChange)
        self.viewer.layers.events.removed.connect(self.onLayerNumberChange)
        self.combobox_select.currentIndexChanged.connect(self.onLayerComboboxChange)
        

    def linkLayer(self):
        self.onLayerSelectChange()
        self.viewer.layers.selection.events.changed.connect(self.onLayerSelectChange)
        
    def onLayerNumberChange(self):  
        self.combobox_select.clear()
        self.combobox_select.addItem('Select Layer')
        for layer in self.viewer.layers:
            if layer is not None:
                if 'ct metadata' in layer.metadata:
                    if layer.metadata['ct metadata']['type'] in self.layer_types:
                        self.combobox_select.addItem(layer.name)
        self.combobox_select.setCurrentIndex(0)
        active_layer = self.viewer.layers.selection.active
        if active_layer is not None:
            self.onLayerSelectChange()
            
    def onLayerComboboxChange(self, index):
        if self.combobox_select.currentIndex() > 0:
            text = self.combobox_select.currentText()
            if self.isfixed:
                for layer in self.viewer.layers:
                    if layer.name == text:
                        self.viewer.layers.selection.active = layer
        else:
            if self.isfixed:
                if self.viewer.layers.selection.active is not None:
                    self.viewer.layers.selection.active = None

    def onLayerSelectChange(self):
        active_layer = self.viewer.layers.selection.active
        if active_layer is None:
            self.combobox_select.setCurrentIndex(0)
            return 
        
        if 'ct metadata' in active_layer.metadata:
            if active_layer.metadata['ct metadata']['type'] in self.layer_types:
                if active_layer.name != self.combobox_select.currentText():
                    self.combobox_select.setCurrentText(active_layer.name)
            else:
                self.combobox_select.setCurrentIndex(0)
        else:
            self.combobox_select.setCurrentIndex(0)


    def getLayerName(self):
        return self.combobox_select.currentText()
    
    @classmethod
    def getLayerIndex(cls, viewer, names):
        if not isinstance(names, list):
            names = [names]

        layer_name_to_index = {layer.name: i for i, layer in enumerate(viewer.layers)}
        indices = []
        for name in names:
            index = layer_name_to_index.get(name)  
            indices.append(index)

        return indices


    def Parse(self):
        for layer in self.viewer.layers:
            if layer.name == self.combobox_select.currentText():
                layertype_id = layer.metadata['ct metadata']['type']
                layertype = TOMOBASE_DATATYPES.loc(layertype_id).name
                logger.info(f'Parsing layer {layertype_id} of type {layertype}')
                class_ = globals().get(layertype)
                obj = class_.from_data_tuple(layer)
                return obj

class ObjectSelectWidget(CollapsableWidget):
    def __init__(self, title, data_types,  viewer: 'napari.viewer.Viewer', parent=None):
        super().__init__(title, parent)
        self.viewer = viewer
        self.object_combobox = QComboBox()
        self.object_combobox.addItem('Select WorkSpace Object')
        self.data_type_combobox = QComboBox()
        self.data_type_combobox.addItem('Selectable Datatypes')

         
        if get_origin(data_types) is Union:
            self.datatype_list = get_args(data_types)
        else:
            self.datatype_list = [data_types]

        for data_type in self.datatype_list:
            self.data_type_combobox.addItem(str(data_type.__name__))
        self.data_type_combobox.setCurrentIndex(0)
        self.current_datatype_list = self.datatype_list
        self.setObjectCombobox()


        self.label_data = QLabel('Selected:')
        self.label_type = QLabel('Data Type:')

        self.layout = QHBoxLayout()
        self.layout.addWidget(self.label_data)
        self.layout.addWidget(self.object_combobox)
        self.layout.addWidget(self.label_type)
        self.layout.addWidget(self.data_type_combobox)
        self.layout.setAlignment(Qt.AlignTop)
        self.setLayout(self.layout)

        self.data_type_combobox.currentIndexChanged.connect(self.onDataTypeChange)
        TDTOMONAPARI_VARIABLES.refreshed.connect(self.setObjectCombobox)

    def onDataTypeChange(self, index):
        if self.data_type_combobox.currentIndex() > 0:
            text = self.data_type_combobox.currentText()
            self.current_datatype_list = [text]
        else:
            self.current_datatype_list = self.datatype_list


    def setObjectCombobox(self):
        self.object_combobox.clear()
        self.object_combobox.addItem('Select WorkSpace Object')
        for key, value in TDTOMONAPARI_VARIABLES.items():
            for datatype in self.current_datatype_list:
                if isinstance(value.value, datatype) or issubclass(value.value, datatype):
                    self.object_combobox.addItem(value.name)

    def Parse(self):
        if self.object_combobox.currentIndex() == 0:
            logger.warning('No object selected')
            return None
        name = self.object_combobox.currentText()
        for key, value in TDTOMONAPARI_VARIABLES.items():
            if value.name == name:
                return value.value




def get_widgets(func, viewer):
    _list = []
    signature = inspect.signature(func)
    reserved = ['self','cls', 'viewer', 'parent', 'kwargs', 'args']
    for name, param in signature.parameters.items():
        if name not in reserved:
            label = name.capitalize().replace("_", " ")
            isdefault = True

            if param.default == inspect.Parameter.empty:
                isdefault = False

            if inspect.isclass(param.annotation) and issubclass(param.annotation, Data):
                widget = LayerSelectWidget(label+":", param.annotation, viewer)

            elif param.annotation == int:
                widget = QSpinBox()
                widget.setRange(0, 1000000)
                if isdefault:
                    widget.setValue(param.default)

            elif param.annotation == float:
                widget = QDoubleSpinBox()
                widget.setRange(-10000000, 1000000)
                widget.setSingleStep(0.01) 
                if isdefault:
                    widget.setValue(param.default)

            elif param.annotation == str:
                widget = QLineEdit()
                widget.setText(param.default)
                if isdefault:
                    widget.setText(param.default)

            elif param.annotation == bool:
                widget = QCheckBox()
                widget.setChecked(param.default)
                if isdefault:
                    widget.setChecked(param.default)

            else:
                widget = ObjectSelectWidget(label+":",param.annotation,viewer)

            if not isinstance(widget, ObjectSelectWidget): 
                if not isinstance(widget, LayerSelectWidget):
                    widget = ItemWidget(label, widget)
            _list.append(WidgetStruct(name, widget))
    return _list

def get_values(widgets):
    _dict = {}
    for widget in widgets:
        if isinstance(widget.widget, LayerSelectWidget):
            _dict[widget.name]= widget.widget.Parse()

        elif isinstance(widget.widget, ObjectSelectWidget):
            _dict[widget.name]= widget.widget.Parse()

        elif isinstance(widget.widget, ItemWidget):
            _dict[widget.name]= widget.widget.Parse()
        else:
            logger.warning(f'Widget {widget} has an unsupported type')
            return
 
    return _dict

