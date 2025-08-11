from qtpy.QtWidgets import QMenu
from qtpy.QtCore import Qt

#from tdtomonapari.napari.acquire.controls import ConnectWidget, buildstagewidget, buildscanwidget, build_start_scan_acquire_widget
from tomobase.log import logger
from tdtomonapari.napari.acquire.devices.new import MagicNewDeviceWidget

class AcquistionMenuWidget(QMenu):  
    def __init__(self, viewer = None ,parent=None):
        super().__init__("Acquisition",parent)
        self.viewer = viewer
        self.actions = {}
        self.menu = {}

        self.menu['Device Management'] = self.addMenu("Device Management")
        self.menu['Device Controls'] = self.addMenu("Device Controls")
        self.menu['Experiments'] = self.addMenu("Experiments")
        
        self.menu['Register Device'] = self.menu['Device Management'].addAction("Register Device")
        self.menu['New Device'] = self.menu['Device Management'].addAction("Edit Device")
        self.menu['Edit Device'] = self.menu['Device Management'].addAction("New Device")
        self.menu['Connect'] = self.menu['Device Management'].addAction("Connect")
        self.menu['Disconnect'] = self.menu['Device Management'].addAction("Disconnect")
        
        # add actions triggers to the menu items use dummy functions for now
        self.menu['Register Device'].triggered.connect(self.NewDevice)
        self.menu['New Device'].triggered.connect(lambda: logger.info("New Device clicked"))
        self.menu['Edit Device'].triggered.connect(lambda: logger.info("Edit Device clicked"))
        self.menu['Connect'].triggered.connect(lambda: logger.info("Connect clicked"))
        self.menu['Disconnect'].triggered.connect(lambda: logger.info("Disconnect clicked"))

    def NewDevice(self):
        # close device if widget closes
        widget = MagicNewDeviceWidget(self.viewer)
        dock_widget = self.viewer.window.add_dock_widget(widget, area='right', name='New Device')
        widget.closed.connect(lambda: self.closeWidget(dock_widget))


    def closeWidget(self, widget):
        """Close the widget and remove it from the viewer."""
        widget.close()

        """_summary_
        
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
        self.actions['Scanning'].triggered.connect(self.onScanningTriggered)


    def onScanningTriggered(self):
        widget1 = buildscanwidget(self.microscope, isscan=False)
        docked_widget1 = self.viewer.window.add_dock_widget(widget1, area='right', name='Acquire Settings')

        widget2 = buildscanwidget(self.microscope, isscan=True)
        docked_widget2 = self.viewer.window.add_dock_widget(widget2, area='right', name='Scan Settings')

        widget3 = build_start_scan_acquire_widget(self.microscope, viewer=self.viewer)
        docked_widget3 = self.viewer.window.add_dock_widget(widget3, area='right', name='Start/Acquire')

        main_window = self.viewer.window._qt_window
        main_window.tabifyDockWidget(docked_widget1, docked_widget2)
        main_window.tabifyDockWidget(docked_widget1, docked_widget3)

    def onConnectTriggered(self):
        active_widget = ConnectWidget(self.microscope, self.viewer)
        docked_widget = self.viewer.window.add_dock_widget(active_widget, area='right', name='Connect')

        active_widget.microscope_updated.connect(self.onSettingsUpdate)
    def onStageTriggered(self):
        if self.microscope is not None:
            active_widget = buildstagewidget(self.microscope)
            docked_widget = self.viewer.window.add_dock_widget(active_widget, area='right', name='Stage')
        else:
            logger.warning("Microscope is not initialized")

    def onSettingsUpdate(self, microscope):
        print("Microscope updated")
        print(microscope)
        self.microscope = microscope

    """


