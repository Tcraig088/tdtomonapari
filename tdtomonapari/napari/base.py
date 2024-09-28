import napari
from qtpy.QtWidgets import QWidget, QVBoxLayout, QMenu, QAction
from qtpy.QtCore import Qt
from tdtomonapari.napari.log import LogWidget
from tdtomonapari.registration import TDTOMO_NAPARI_MODULE_REGISTRATION

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
        
        self.viewer.window.add_dock_widget(LogWidget(), area='bottom')
        logger.info('Continuous Tomography Plugin Loaded')

        if TDTOMO_NAPARI_MODULE_REGISTRATION.tomoacquire:
            self.menus['Acquisition'] = tomoacquire.napari.AcquistionMenuWidget(self.viewer, self.menu)
            self.menu.addMenu(self.menus['Acquisition'])
            
        if TDTOMO_NAPARI_MODULE_REGISTRATION.tomobase:
            self.menus['Tomography'] = tomobase.napari.TomographyMenuWidget(self.menu)
            self.menu.addMenu(self.menus['Tomography'])

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        