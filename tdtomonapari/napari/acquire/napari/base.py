from qtpy.QtWidgets import QMenu
from qtpy.QtCore import Qt

from tomoacquire.napari.processes import InstrumentWidget, ExperimentWidget

class AcquistionMenuWidget(QMenu):  
    def __init__(self, viewer = None ,parent=None):
        super().__init__("Acquisition", parent)
        self.actions = {}
        self.viewer = viewer
        self.actions['Configs'] = self.addAction('Configurations')
        self.actions['Instrument'] = self.addAction('Instrument')
        self.actions['Callibration'] = self.addAction('Callibration')
        self.actions['Experiment'] = self.addAction('Experiment')

        self.actions['Instrument'].triggered.connect(self.on_instrument_triggered)
        self.actions['Experiment'].triggered.connect(self.on_experiment_triggered)
        
    def on_instrument_triggered(self):
        if self.viewer is not None:
            self.viewer.window.add_dock_widget(InstrumentWidget(self.viewer), area='right', name='Instrument Settings')

    def on_experiment_triggered(self):
        if self.viewer is not None:
            self.viewer.window.add_dock_widget(ExperimentWidget(), area='right', name='Experiment Settings')