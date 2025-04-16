import napari
import inspect
from copy import deepcopy
from qtpy.QtWidgets import QMenu
from qtpy.QtCore import Qt
from functools import partial
from tomobase.globals import logger, TOMOBASE_PROCESSES, TOMOBASE_TRANSFORM_CATEGORIES
from tdtomonapari.napari.base.plugins.process import ProcessWidget 
from tdtomonapari.napari.base.plugins.tiltselect import TiltSelectWidget

class TomographyMenuWidget(QMenu):  
    def __init__(self, viewer: 'napari.viewer.Viewer', parent=None):
        super().__init__("Tomography", parent)
        self.menu = {}
        self.viewer = viewer

        tiltmenu = self.addAction("TiltSchemes")
        for key, value in TOMOBASE_TRANSFORM_CATEGORIES.items():
            self.menu[key] = self.addMenu(value.name.replace("_", " ").capitalize())
            self.traverseMenu(key, self.menu[key], value.categories)   

        tiltmenu.triggered.connect(self.onTiltTriggered)

    def onProcessTriggered(self, widget, process):
        active_widget = widget(process, self.viewer)
        docker_widget = self.viewer.window.add_dock_widget(active_widget, name=process.name, area='right')

        docker_widget.setAttribute(Qt.WA_DeleteOnClose)
        active_widget.closed.connect(lambda: self.onCloseWidget(docker_widget))

    def traverseMenu(self, base, menu, element):
        for key, value in element.items():
            if isinstance(value, dict):
                submenu  = menu.addMenu(key)
                self.traverseMenu(base, submenu, value)
            else:
                action = menu.addAction(value)
                process = TOMOBASE_PROCESSES[base][value.upper().replace(" ", "_")]
                if inspect.isclass(process):
                    widget = ProcessClassWidget
                else:
                    widget = ProcessWidget

                def _nested_function(x, y):
                    return lambda: self.onProcessTriggered(x, y)
                
                action.triggered.connect(_nested_function(widget, process))

    def onCloseWidget(self, widget):
        widget.close()


    def onTiltTriggered(self):
        active_widget = TiltSelectWidget(True, self.viewer)
        docker_widget = self.viewer.window.add_dock_widget(active_widget, name='TiltScheme', area='right')

        docker_widget.setAttribute(Qt.WA_DeleteOnClose)
        active_widget.closed.connect(lambda: self.onCloseWidget(docker_widget))



                
        