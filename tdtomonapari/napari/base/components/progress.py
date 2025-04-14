from qtpy.QtCore import Signal, QObject, Qt
from qtpy.QtWidgets import QWidget, QGridLayout,  QVBoxLayout, QTextEdit, QComboBox, QLabel, QProgressBar, QHBoxLayout
from tomobase.globals import progresshandler



class ProgressWidget(QWidget):
    def __init__(self, signal, viewer: 'napari.viewer.Viewer', parent=None):
        super().__init__(parent)
        self.viewer = viewer    
        self.layout = QGridLayout(self)
        signal = signal.upper().replace(' ', '_')
        self.progress = progresshandler[signal].value

        self.label = QLabel('Progress:')
        self.task_label = QLabel('progress')
        self.eta_label = QLabel('Elapsed 00:00:00 (0) | ETA 00:00:00 (0)')


        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 100)

        self.layout.addWidget(self.label, 0, 0)
        self.layout.addWidget(self.task_label, 0, 1)
        self.layout.addWidget(self.progress_bar,1,0,1,2)
        self.layout.addWidget(self.eta_label, 2, 0,1,2)
        self.setLayout(self.layout)

        self.progress.started.connect(self.start)
        self.progress.updated.connect(self.update)
        self.progress.finished.connect(self.finish)
        self.progress.maxupdated.connect(self.progress_bar.setMaximum)    

    def setMaximum(self, max_value):
        self.progress_bar.setRange(0, max_value)
        
    def start(self, max_value, task):
        self.progress_bar.setRange(0, max_value)
        self.progress_bar.setValue(0)
        self.task_label.setText(task)

    def update(self, value, eta):
        self.progress_bar.setValue(value)
        self.eta_label.setText(eta)

    def finish(self):
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.close()