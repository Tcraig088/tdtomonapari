import inspect
import numpy as np
from dataclasses import dataclass

from tomobase.log import logger
from typing import Union, get_origin, get_args
from tomobase.data import Data, Sinogram, Image, Volume
from qtpy.QtWidgets import QWidget, QPushButton, QVBoxLayout, QHBoxLayout,  QLabel, QCheckBox, QComboBox, QGridLayout, QSpinBox, QDoubleSpinBox, QLineEdit
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
    def __init__(self, title, layer_types, viewer: 'napari.viewer.Viewer', isfixed=False, parent=None):
        super().__init__(title, parent)
        
        self.viewer = viewer
        #if iterable
        if get_origin(layer_types) is Union:
            layer_types = get_args(layer_types)
            self.layer_types = [typ.get_type_id() for typ in layer_types]
        if layer_types is Data:
            self.layer_types = []
            for key, value in TOMOBASE_DATATYPES.items():
                self.layer_types.append(value.value)
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
        
        if isfixed:
            self.linkLayer()

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
            if layer.name == self.combobox_select.currentText():#get the index of the layer
                index = self.viewer.layers.index(layer)
                layertype_id = layer.metadata['ct metadata']['type']
                layertype = TOMOBASE_DATATYPES.loc(layertype_id).name
                class_ = globals().get(layertype)
                obj = class_.from_data_tuple(index, layer)
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

class LayerMultiSelectWidget(CollapsableWidget):
    def __init__(self, layer_type, viewer,  parent=None):
        super().__init__('Select Layers:', parent)
        self._dict = {}
        self.i = 1
        self.viewer = viewer
        self._layout = QGridLayout()
        self.layer_type = layer_type
        self.widget_list = []
        self.button_add = QPushButton('Add')
        self.button_remove = QPushButton('Remove')

        self.button_add.clicked.connect(self.AddWidget)
        self.button_remove.clicked.connect(self.removeWidget)

        self._layout.addWidget(self.button_add, 0, 0)
        self._layout.addWidget(self.button_remove, 0, 1)
        self.setLayout(self._layout)

    def AddWidget(self):
        widget = LayerSelectWidget('Layer:', self.layer_type, self.viewer)
        self.widget_list.append(widget)
        self._layout.addWidget(widget,self.i,0,1,2)
        self.i += 1

    def removeWidget(self):
        if len(self.widget_list) > 0:
            widget = self.widget_list.pop()
            self._layout.removeWidget(widget)
            widget.deleteLater()
            self.i -= 1
        else:
            logger.warning('No widgets to remove')

    def Parse(self):
        _dict = {}
        for widget in self.widget_list:
            name = widget.combobox_select.currentText().lower().replace(" ", "_")
            _dict[name] = widget.Parse()
        return _dict


def get_function_widgets(func, viewer, **kwargs):
    isfixed = kwargs.get('isfixed', False)
    _list = []
    signature = inspect.signature(func)
    reserved = ['self','cls', 'viewer', 'parent', 'kwargs', 'args']
    logger.debug(f'Function signature: {signature}')
    for name, param in signature.parameters.items():
        if name not in reserved:
            label = name.capitalize().replace("_", " ")
            if param.default == inspect.Parameter.empty:
                widget = get_widget(name, label, param.annotation, None, viewer, isfixed=isfixed)
            else:
                widget = get_widget(name, label, param.annotation, param.default, viewer, isfixed=isfixed)
            _list.append(widget)
    return _list

def get_widget(name, label, annotation, default=None, viewer=None, **kwargs):
    isfixed = kwargs.get('isfixed', True)
    if inspect.isclass(annotation) and issubclass(annotation, Data):
        widget = LayerSelectWidget(label+":", annotation, viewer, isfixed)

    elif get_origin(annotation) is dict:
        key_type, value_type = get_args(annotation)
        widget = LayerMultiSelectWidget( value_type, viewer)

    elif annotation == int:
        widget = QSpinBox()
        widget.setRange(0, 1000000)
        if default is not None:
            widget.setValue(default)

    elif annotation == float:
        widget = QDoubleSpinBox()
        widget.setRange(-10000000, 1000000)
        widget.setSingleStep(0.01) 
        if default is not None:
            widget.setValue(default)

    elif annotation == str:
        widget = QLineEdit()
        if default is not None:
            widget.setText(default)

    elif annotation == bool:
        widget = QCheckBox()
        if default is not None:
            widget.setChecked(default)

    else:
        widget = ObjectSelectWidget(label+":", annotation, viewer)
        return
    
    if not isinstance(widget, ObjectSelectWidget) and not isinstance(widget, LayerSelectWidget) and not isinstance(widget, LayerMultiSelectWidget):
        widget = ItemWidget(label, widget)
    return WidgetStruct(name, widget)

def set_values(widgets, values):
    for widget in widgets:
        for key, value in values.items():
            if widget.name == key:
                if isinstance(widget.widget, LayerSelectWidget):
                    widget.widget.combobox_select.setCurrentText(value.name)

                elif isinstance(widget.widget, ObjectSelectWidget):
                    widget.widget.object_combobox.setCurrentText(value.name)

                elif isinstance(widget, WidgetStruct):
                    if isinstance(widget.widget.widget, QSpinBox):
                        widget.widget.widget.setValue(value)

                    elif isinstance(widget.widget.widget, QDoubleSpinBox):
                        widget.widget.widget.setValue(value)

                    elif isinstance(widget.widget.widget, QLineEdit):
                        widget.widget.widget.setText(value)

                    elif isinstance(widget.widget.widget, QCheckBox):
                        widget.widget.widget.setChecked(value)
                    

def connect_widget(widget, func, viewer):
    logger.debug(type(widget))
    if isinstance(widget.widget, LayerSelectWidget):
        widget.widget.combobox_select.currentIndexChanged.connect(func)

    elif isinstance(widget.widget, ObjectSelectWidget):
        widget.widget.object_combobox.currentIndexChanged.connect(func)

    elif isinstance(widget.widget, ItemWidget):
        if isinstance(widget.widget.widget, QSpinBox):
            widget.widget.widget.valueChanged.connect(func)

        elif isinstance(widget.widget.widget, QDoubleSpinBox):
            widget.widget.widget.valueChanged.connect(func)

        elif isinstance(widget.widget.widget, QLineEdit):
            widget.widget.widget.textChanged.connect(func)

        elif isinstance(widget.widget.widget, QCheckBox):
            widget.widget.widget.stateChanged.connect(func)

def get_values(widgets):
    _dict = {}
    for widget in widgets:
        if isinstance(widget.widget, LayerMultiSelectWidget):
            _dict[widget.name]= widget.widget.Parse()

        elif isinstance(widget.widget, LayerSelectWidget):
            _dict[widget.name]= widget.widget.Parse()

        elif isinstance(widget.widget, ObjectSelectWidget):
            _dict[widget.name]= widget.widget.Parse()

        elif isinstance(widget.widget, ItemWidget):
            _dict[widget.name]= widget.widget.Parse()
        else:
            logger.warning(f'Widget {widget} has an unsupported type')
            return
 
    return _dict

