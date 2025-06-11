import napari
from qtpy.QtWidgets import QWidget, QVBoxLayout, QMenu, QAction, QDockWidget
from qtpy.QtCore import Qt

from tdtomonapari.napari.log import LogWidget
from tdtomonapari.napari.layer import LayerInfo
from tdtomonapari.napari.variables import VariablesWidget
from tdtomonapari.napari.gpu import ContextWidget

from tdtomonapari.registration import TDTOMO_NAPARI_MODULE_REGISTRATION
from tdtomonapari.napari.base.base import TomographyMenuWidget
#import tdtomonapari.magic

from tomobase.globals import logger
if TDTOMO_NAPARI_MODULE_REGISTRATION.tomoacquire:
    import tomoacquire
    from tdtomonapari.napari.acquire.base import AcquistionMenuWidget
    
class EntryWidget(QWidget):    
    def __init__(self, viewer: 'napari.viewer.Viewer', parent=None):
        super().__init__(parent)
        
        self.viewer = viewer
        #self.setAttribute(Qt.WA_DeleteOnClose)
        
        main_menu = self.viewer.window.main_menu.addMenu("Continuous Tomography")
        menu = QMenu('Utilities', main_menu)
        main_menu.addMenu(menu)

        log_action = QAction('Log', menu)
        layer_action = QAction('Layer Info',menu)
        variables_action = QAction('WorkSpace', menu)
        context_action = QAction('Context', menu)
        visualization_action = QAction('Visualization', menu)

        menu.addAction(log_action)
        menu.addAction(layer_action)
        menu.addAction(variables_action)
        menu.addAction(context_action)
        menu.addAction(visualization_action)


        self.addVariablesWidget()
        log_action.triggered.connect(self.addLogWidget)
        layer_action.triggered.connect(self.addLayerInfoWidget)
        variables_action.triggered.connect(self.addVariablesWidget)
        context_action.triggered.connect(self.addContextWidget)
        visualization_action.triggered.connect(self.addVisualizationWidget)

        if TDTOMO_NAPARI_MODULE_REGISTRATION.tomoacquire:
            main_menu.addMenu(AcquistionMenuWidget(self.viewer, main_menu))
        main_menu.addMenu(TomographyMenuWidget(self.viewer, main_menu))


        
    def addLogWidget(self):
        self.viewer.window.add_dock_widget(LogWidget(self.viewer), name='Log', area='bottom')

    def addLayerInfoWidget(self):
        self.viewer.window.add_dock_widget(LayerInfo(self.viewer), name='Layer Info', area='right')

    #def addVariablesWidget(self):
    #    self.viewer.window.add_dock_widget(VariablesWidget(self.viewer), name='Workspace', area='left')

    def addVariablesWidget(self):

        variables_dock = self.viewer.window.add_dock_widget(
            VariablesWidget(self.viewer), name='Workspace', area='left'
        )


        main_window = self.viewer.window._qt_window
        layer_list_widget = None
        for child in main_window.children():
            if child.objectName() == "layer list":
                layer_list_widget = child
                break

        if layer_list_widget is not None:
            self.viewer.window._qt_window.tabifyDockWidget(layer_list_widget, variables_dock)
        return



        

    def addContextWidget(self):
        self.viewer.window.add_dock_widget(ContextWidget(self.viewer), name='Context', area='right')

    def addVisualizationWidget(self):
        self.viewer.window.add_dock_widget(QDockWidget("Data Analysis"), name='Visualization', area='right')
