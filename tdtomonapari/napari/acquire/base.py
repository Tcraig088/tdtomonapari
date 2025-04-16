from qtpy.QtWidgets import QMenu
from qtpy.QtCore import Qt

from tdtomonapari.napari.acquire.controls import ConnectWidget, StageWidget
from tomobase.log import logger
class AcquistionMenuWidget(QMenu):  
    def __init__(self, viewer = None ,parent=None):
        super().__init__("Acquisition", parent)
        self.actions = {}
        self.viewer = viewer
        self.microscope = None
        
        self.actions['Configs'] = self.addAction('Connect')
        self.actions['Configs'].triggered.connect(self.onConnectTriggered)

        menu = self.addMenu("Controls")
        self.actions['Scanning'] = menu.addAction("Scanning") 
        self.actions['Stage'] = menu.addAction("Stage")

        #self.actions['Scanning'].triggered.connect(self.onScanningTriggered)
        self.actions['Stage'].triggered.connect(self.onStageTriggered)

    def onConnectTriggered(self):
        active_widget = ConnectWidget(self.microscope, self.viewer)
        docked_widget = self.viewer.window.add_dock_widget(active_widget, area='right', name='Connect')

        active_widget.microscope_updated.connect(self.onSettingsUpdate)
    def onStageTriggered(self):
        if self.microscope is not None:
            active_widget = StageWidget(self.microscope, self.viewer)
            docked_widget = self.viewer.window.add_dock_widget(active_widget, area='right', name='Stage')
        else:
            logger.warning("Microscope is not initialized")

    def onSettingsUpdate(self, microscope):
        print("Microscope updated")
        print(microscope)
        self.microscope = microscope




