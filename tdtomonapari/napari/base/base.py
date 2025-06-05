import napari
import magicgui
import inspect
import time
import coolname
from napari.qt.threading import thread_worker
from copy import deepcopy
from qtpy.QtWidgets import QMenu
from qtpy.QtCore import Qt
from functools import partial
from tomobase.globals import logger, TOMOBASE_PROCESSES, TOMOBASE_TRANSFORM_CATEGORIES, GPUContext
from tdtomonapari.napari.base.plugins.process import ProcessWidget 
from tdtomonapari.napari.base.plugins.tiltselect import TiltSelectWidget
from tomobase.data import Data
from tdtomonapari.registration import TDTOMONAPARI_VARIABLES


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

    def onProcessTriggered2(self, widget, name):
        logger.info(f"Building widget for {name}")
        docker_widget = self.viewer.window.add_dock_widget(widget, name=name, area='right')

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
                    logger.info(f"Building widget for {process.value}")
                    widget = buildFunctionWidget(process.value, self.viewer)
                    name = process.value.tomobase_name

                def _nested_function(x, y):
                    return lambda: self.onProcessTriggered2(x, y)
                
                action.triggered.connect(_nested_function(widget, name))

    def onCloseWidget(self, widget):
        widget.close()


    def onTiltTriggered(self):
        active_widget = TiltSelectWidget(True, self.viewer)
        docker_widget = self.viewer.window.add_dock_widget(active_widget, name='TiltScheme', area='right')

        docker_widget.setAttribute(Qt.WA_DeleteOnClose)
        active_widget.closed.connect(lambda: self.onCloseWidget(docker_widget))



def buildFunctionWidget(func, viewer):
    widget = magicgui.magicgui(func, call_button='Run', auto_call=False)
    widget.viewer = viewer
    
    logger.info(f"Building widget for {func.__name__}")
    logger.info(f"Function signature: {inspect.signature(func)}")

    @widget.called.connect
    def _run_threaded():
        # Capture inputs here before running
        args = {name: getattr(widget, name).value for name in widget._function.__code__.co_varnames[:widget._function.__code__.co_argcount]}
        start_time = time.perf_counter()

        @thread_worker
        def _run():
            return func(**args)

        def onComplete(result):
            # parseResult must be your external result processor
            if not isinstance(result, tuple):
                result = [result]
            for item in result:
                if isinstance(item, Data):
                    item.set_context(GPUContext.NUMPY, 0)
                    if getattr(widget, "inplace", False):
                        viewer.layers[item._layer_index].metadata = item.layer_metadata()
                        viewer.layers[item._layer_index].data = item.data
                        viewer.layers[item._layer_index].scale = item.layer_scale()
                        viewer.layers[item._layer_index].refresh()
                    else:
                        name = coolname.generate_slug(2).replace('-', ' ').title().replace(' ', '')
                        layerdata = item.to_data_tuple(attributes={'name': name})
                        viewer._add_layer_from_data(*layerdata)
                else:
                    name = coolname.generate_slug(2)
                    TDTOMONAPARI_VARIABLES[name] = item
                    TDTOMONAPARI_VARIABLES.refresh()

            elapsed = time.perf_counter() - start_time
            hours, remainder = divmod(elapsed, 3600)
            minutes, seconds = divmod(remainder, 60)
            logger.info(
                f"{getattr(widget, 'tomobase_name', func.__name__)} Completed - "
                f"Elapsed time: {int(hours):02}:{int(minutes):02}:{int(seconds):02}"
            )

        worker = _run()
        worker.returned.connect(onComplete)
        worker.start()

    return widget

