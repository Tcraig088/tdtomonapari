import napari
from qtpy.QtWidgets import QWidget, QVBoxLayout, QMenu, QAction
from qtpy.QtCore import Qt
from tdtomonapari.napari.log import LogWidget
from tdtomonapari.napari.layer import LayerInfo
from tdtomonapari.registration import TDTOMO_NAPARI_MODULE_REGISTRATION
from tdtomonapari.napari.base.base import TomographyMenuWidget
from tdtomonapari.napari.acquire.base import AcquistionMenuWidget

import logging
logger = logging.getLogger('tomobase_logger')
if TDTOMO_NAPARI_MODULE_REGISTRATION.tomobase:
    import tomobase
if TDTOMO_NAPARI_MODULE_REGISTRATION.tomoacquire:
    import tomoacquire
    
    
def napari_enter(viewer: 'napari.viewer.Viewer'):
    menu = viewer.window.main_menu.addMenu("Continuous Tomography")
    menus = {}
    
    if TDTOMO_NAPARI_MODULE_REGISTRATION.tomoacquire:
        menus['Acquisition'] = tomoacquire.napari.AcquistionMenuWidget(menu)
        menu.addMenu(menus['Acquisition'])

        
    if TDTOMO_NAPARI_MODULE_REGISTRATION.tomobase:
        menus['Tomography'] = tomobase.napari.TomographyMenuWidget(menu)
        menu.addMenu(menus['Tomography'])

    
class EntryWidget(QWidget):    
    def __init__(self, viewer: 'napari.viewer.Viewer', parent=None):
        super().__init__(parent)
        
        self.viewer = viewer
        
        self.menu = self.viewer.window.main_menu.addMenu("Continuous Tomography")
        self.menus = {}
        
        self.menus['Utilities'] = {}
        self.menus['Utilities']['Menu'] = QMenu('Utilities', self.menu)
        self.menus['Utilities']['Log'] = QAction('Log', self.menus['Utilities']['Menu'])
        self.menus['Utilities']['Layer Info'] = QAction('Layer Info',self.menus['Utilities']['Menu'])
        
        self.menus['Utilities']['Menu'].addAction(self.menus['Utilities']['Log'])
        self.menus['Utilities']['Menu'].addAction(self.menus['Utilities']['Layer Info'])
        
        self.menu.addMenu(self.menus['Utilities']['Menu'])

        
        self.menus['Utilities']['Log'].triggered.connect(self.addLogWidget)
        self.menus['Utilities']['Layer Info'].triggered.connect(self.addLayerInfoWidget)
        
        self.viewer.window.add_dock_widget(LogWidget(), area='bottom')
        logger.info('Continuous Tomography Plugin Loaded')

        if TDTOMO_NAPARI_MODULE_REGISTRATION.tomoacquire:
            self.menus['Acquisition'] = AcquistionMenuWidget(self.viewer, self.menu)
            self.menu.addMenu(self.menus['Acquisition'])
            pass
        
        if TDTOMO_NAPARI_MODULE_REGISTRATION.tomobase:
            self.menus['Tomography'] = TomographyMenuWidget(self.viewer, self.menu)
            self.menu.addMenu(self.menus['Tomography'])

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
    def addLogWidget(self):
        self.viewer.window.add_dock_widget(LogWidget(), name='Log', area='bottom')
        
    def addLayerInfoWidget(self):
        self.viewer.window.add_dock_widget(LayerInfo(self.viewer), name='Layer Info', area='right')