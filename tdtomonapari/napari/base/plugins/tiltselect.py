from tomobase.registrations.tiltschemes import TOMOBASE_TILTSCHEMES
from tdtomonapari.napari.base.components.collapsable import CollapsableWidget
from qtpy.QtWidgets import QWidget, QLabel, QComboBox, QGridLayout, QSpinBox
from qtpy.QtCore import Qt
import inspect
from tdtomonapari.napari.base.utils import get_value, get_widget, connect
from tomobase.log import logger

class TiltSchemeWidget(CollapsableWidget):
    def __init__(self, tiltscheme, parent=None):
        super().__init__()
        self.tiltscheme = tiltscheme
        signature = inspect.signature(self.tiltscheme.__init__)
        self.custom_widgets = {
            'Name': [],
            'Label': [],
            'Widget': []
        }
        banned = ['self', 'args', 'kwargs']
        for name, param in signature.parameters.items():
            if name not in banned:
                wname, wlabel, widget = get_widget(name, param)
                if wname is not None:
                    self.custom_widgets['Widget'].append(widget)
                    self.custom_widgets['Name'].append(wname)
                    self.custom_widgets['Label'].append(wlabel)

        self.layout = QGridLayout()
        for j, key in enumerate(self.custom_widgets['Name']):
            self.layout.addWidget(self.custom_widgets['Label'][j], j, 0)
            self.layout.addWidget(self.custom_widgets['Widget'][j], j, 1)

        self.setLayout(self.layout)
        self.layout.setAlignment(Qt.AlignTop)

    def Parse(self):
        _dict = {}
        for j, key in enumerate(self.custom_widgets['Name']):
            _dict[key] = get_value(self.custom_widgets['Widget'][j])
        logger.debug(f'Parsed TiltScheme: {_dict}')
        return _dict

class TiltSelectWidget(CollapsableWidget):
    def __init__(self, viewer: 'napari.viewer.Viewer', parent=None):
        super().__init__('', parent)
        self.viewer = viewer

        self.combobox_select = QComboBox()
        self.combobox_select.addItem('Select TiltScheme')
        for item in TOMOBASE_TILTSCHEMES.keys():
            self.combobox_select.addItem(item)

        self.combobox_select.currentIndexChanged.connect(self.onComboboxChange)
        self.angles_widget = QSpinBox()
        self.angles_widget.setRange(0, 1000000)
        self.angles_widget.setValue(70)
        self.tiltscheme_widget = None

        self.layout = QGridLayout()
        self.layout.addWidget(QLabel('Select TiltScheme'), 0, 0)
        self.layout.addWidget(self.combobox_select, 0, 1)
        self.layout.addWidget(QLabel('Number of Angles'), 1, 0)
        self.layout.addWidget(self.angles_widget, 1, 1)
        
        self.layout.setAlignment(Qt.AlignTop)
        self.setLayout(self.layout)

    def onComboboxChange(self, index):
        if self.tiltscheme_widget is not None:
            self.layout.removeWidget(self.tiltscheme_widget)
            self.tiltscheme_widget.deleteLater()
            self.tiltscheme_widget = None

        if self.combobox_select.currentIndex() > 0:
            self.tiltscheme = TOMOBASE_TILTSCHEMES[self.combobox_select.currentText()].controller
            self.tiltscheme_widget = TiltSchemeWidget(self.tiltscheme, parent=self)
            self.layout.addWidget(self.tiltscheme_widget, 2, 0, 1, 2)
            self.tiltscheme_widget.show()

    def Parse(self):
        logger.debug(f'Entered Parsing:')
        if self.tiltscheme_widget is not None:
            logger.debug(f'Value Obtained:')
            _dict = self.tiltscheme_widget.Parse()
            logger.debug(f'Value Obtained:{_dict}')
            obj = TOMOBASE_TILTSCHEMES[self.combobox_select.currentText()].controller
            logger.debug(f'Parsed TiltScheme:{obj} obj')
            return (obj(**_dict), self.angles_widget.value())
        logger.debug(f'Parsed TiltScheme: None')
        return None