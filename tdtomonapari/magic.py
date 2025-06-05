import magicgui
from typing import Union, get_origin, get_args
from itertools import combinations
from functools import partial

from tdtomonapari.napari.base.components.collapsable import CollapsableWidget
from tomobase.data import Data, Sinogram, Volume, Image 
from tomobase.globals import TOMOBASE_DATATYPES, TOMOBASE_TILTSCHEMES

from qtpy.QtWidgets import (
    QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel,
    QCheckBox, QComboBox, QGridLayout, QSpinBox, QDoubleSpinBox, QLineEdit, QWidget
)
from qtpy.QtCore import Qt


class TiltSelectWidget(QWidget):
    def __init__(self, title='TiltScheme Select', get_angles=False, viewer=None, parent=None):
        super().__init__(title, parent)
        if viewer is None and parent is not None:
            viewer = getattr(parent, "viewer", None)
        self.viewer = viewer

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
         
        self.tiltscheme_widget = QWidget()
        

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

class LayerSelectWidget(CollapsableWidget):
    def __init__(self, title, type_, isfixed=False, viewer=None, parent=None):
        super().__init__(title, parent)
        if viewer is None and parent is not None:
            viewer = getattr(parent, "viewer", None)
        self.viewer = viewer
        self.isfixed = isfixed

        if get_origin(type_) is Union:
            type_ = get_args(type_)
            self._types = [typ.get_type_id() for typ in type_]
        elif type_ is Data:
            self._types = [value.value for key, value in TOMOBASE_DATATYPES.items()]
        else:
            type_ = [type_]
            self._types = [typ.get_type_id() for typ in type_]

        self.combobox_select = QComboBox()
        self.combobox_types = QComboBox()

        self.layout = QGridLayout()
        self.layout.addWidget(QLabel('Selected:'), 0, 0)
        self.layout.addWidget(self.combobox_select, 0, 1)
        self.layout.addWidget(self.combobox_types, 0, 2)
        self.layout.setAlignment(Qt.AlignTop)
        self.setLayout(self.layout)

        self.combobox_types.addItem('Selectable Datatypes')
        for id in self._types:
            self.combobox_types.addItem(TOMOBASE_DATATYPES.loc(id).name)
        self.combobox_types.setCurrentIndex(0)

        self.viewer.layers.events.inserted.connect(self.onLayerNumberChange)
        self.viewer.layers.events.removed.connect(self.onLayerNumberChange)
        self.combobox_select.currentIndexChanged.connect(self.onLayerComboboxChange)

        self.onLayerNumberChange()
        if self.isfixed:
            self.linkLayer()

    def linkLayer(self):
        self.onLayerSelectChange()
        self.viewer.layers.selection.events.changed.connect(self.onLayerSelectChange)

    def onLayerNumberChange(self):
        self.combobox_select.clear()
        self.combobox_select.addItem('Select Layer')
        for layer in self.viewer.layers:
            if 'ct metadata' in layer.metadata:
                if layer.metadata['ct metadata']['type'] in self._types:
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
            if self.isfixed and self.viewer.layers.selection.active is not None:
                self.viewer.layers.selection.active = None

    def onLayerSelectChange(self):
        active_layer = self.viewer.layers.selection.active
        if active_layer is None:
            self.combobox_select.setCurrentIndex(0)
            return

        if 'ct metadata' in active_layer.metadata:
            if active_layer.metadata['ct metadata']['type'] in self._types:
                if active_layer.name != self.combobox_select.currentText():
                    self.combobox_select.setCurrentText(active_layer.name)
            else:
                self.combobox_select.setCurrentIndex(0)
        else:
            self.combobox_select.setCurrentIndex(0)

    def getLayerName(self):
        return self.combobox_select.currentText()

    @property
    def value(self):
        name = self.getLayerName()
        for layer in self.viewer.layers:
            if layer.name == name:
                return layer
        return None

    @classmethod
    def getLayerIndex(cls, viewer, names):
        if not isinstance(names, list):
            names = [names]
        layer_name_to_index = {layer.name: i for i, layer in enumerate(viewer.layers)}
        return [layer_name_to_index.get(name) for name in names]


def _from_data_layer(layer):
    layertype_id = layer.metadata['ct metadata']['type']
    layertype = TOMOBASE_DATATYPES.loc(layertype_id).name
    class_ = globals().get(layertype)
    obj = class_.from_data_tuple(layer)
    return obj


def _flat_union(*types):
    flat_types = []
    for typ in types:
        if get_origin(typ) is Union:
            flat_types.extend(get_args(typ))
        else:
            flat_types.append(typ)
    seen = set()
    result = []
    for typ in flat_types:
        if typ not in seen:
            seen.add(typ)
            result.append(typ)
    return Union[tuple(result)]


def layer_widget_factory(annotation=None, options=None, isfixed=False):
    return LayerSelectWidget(
        title=options.get("name", "Unnamed"),
        type_=annotation,
        isfixed=isfixed,
        viewer=options.get("viewer", None),
        parent=options.get("parent", None)
    )


def build_return_callback():
    return lambda w: _from_data_layer(w.value)


# ---- Dynamic Registration ----
# Collect all registered data classes
_type_classes = []
for id in TOMOBASE_DATATYPES.values():
    type_name = TOMOBASE_DATATYPES.loc(id).name
    class_ = globals().get(type_name)
    _type_classes.append(class_)

# Register individual types
for type_ in _type_classes:
    magicgui.register_type(
        type_=type_,
        widget_type=partial(layer_widget_factory, isfixed=False),
        return_callback=build_return_callback()
    )

# Register all Union combinations of 2 or more types
for r in range(2, len(_type_classes) + 1):
    for combo in combinations(_type_classes, r):
        union_type = _flat_union(*combo)
        magicgui.register_type(
            type_=union_type,
            widget_type=partial(layer_widget_factory, isfixed=False),
            return_callback=build_return_callback()
        )
