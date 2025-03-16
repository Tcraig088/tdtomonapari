from qtpy.QtWidgets import QMenu
from qtpy.QtCore import Qt

from tdtomonapari.napari.acquire.processes import ScanWidget, InstrumentWidget, ExperimentWidget, ConnectWidget

class AcquistionMenuWidget(QMenu):  
    def __init__(self, viewer = None ,parent=None):
        super().__init__("Acquisition", parent)
        self.actions = {}
        self.viewer = viewer
        self.actions['Configs'] = self.addAction('Configurations')
        self.actions['Connect'] = self.addAction('Connect')
        self.actions['Instrument'] = self.addAction('Instrument')
        self.actions['Scan Controls'] = self.addAction('Scan Controls')
        self.actions['Callibration'] = self.addAction('Callibration')
        self.actions['Experiment'] = self.addAction('Experiment')

        self.actions['Connect'].triggered.connect(self.on_connect_triggered)
        self.actions['Instrument'].triggered.connect(self.on_instrument_triggered)
        self.actions['Scan Controls'].triggered.connect(self.on_scan_controls_triggered)
        self.actions['Experiment'].triggered.connect(self.on_experiment_triggered)
        
    def on_connect_triggered(self):
        if self.viewer is not None:
            self.viewer.window.add_dock_widget(ConnectWidget(self.viewer), area='right', name='Connection Settings')

    def on_instrument_triggered(self):
        if self.viewer is not None:
            self.viewer.window.add_dock_widget(InstrumentWidget(self.viewer), area='right', name='Instrument Settings')

    def on_scan_controls_triggered(self):
        if self.viewer is not None:
            self.viewer.window.add_dock_widget(ScanWidget(self.viewer), area='right', name='Scan Controls')

    def on_experiment_triggered(self):
        if self.viewer is not None:
            self.viewer.window.add_dock_widget(ExperimentWidget(), area='right', name='Experiment Settings')