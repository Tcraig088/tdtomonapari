import logging
from qtpy.QtCore import Signal, QObject
from qtpy.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QComboBox, QLabel, QProgressBar, QHBoxLayout
from tomobase.log import tomobase_logger, logger 

class LogSettingsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QHBoxLayout(self)
        self.label = QLabel('Log Level:')
        self.combo_box = QComboBox()
        self.combo_box.addItems(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.combo_box)
        self.setLayout(self.layout)

class ProgressInfoWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.label = QLabel('Progress:')
        self.label_task = QLabel('')
        self.label_eta = QLabel('')

        self.layout = QHBoxLayout(self)
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.label_task)
        self.layout.addWidget(self.label_eta)

class ProgressWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.info = ProgressInfoWidget()

        self.progress = tomobase_logger.progress_bar
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 100)
        self.layout.addWidget(self.info)
        self.layout.addWidget(self.progress_bar)
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
        self.info.label_task.setText(task)

    def update(self, value, eta):
        self.progress_bar.setValue(value)
        self.info.label_eta.setText(eta)

    def finish(self):
        self.progress_bar.setValue(0)
        self.info.label_task.setText('')
        self.info.label_eta.setText('')
    

class QTextEditLogger(logging.Handler):
    def __init__(self, text_edit):
        super().__init__()
        self.text_edit = text_edit

    def emit(self, record):
        msg = self.format(record)
        self.text_edit.append(msg)

class LogWidget(QWidget):
    progress_updated = Signal(int, int)  # Signal to update progress bar

    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.layout = QVBoxLayout(self)

        self.settings_widget = LogSettingsWidget()
        self.log_text_edit = QTextEdit(self)
        self.log_text_edit.setReadOnly(True)
        self.progress_widget = ProgressWidget(self)
        
        self.layout.addWidget(self.settings_widget)
        self.layout.addWidget(self.log_text_edit)
        self.layout.addWidget(self.progress_widget)
        self.setLayout(self.layout)
        
        self.log_handler = QTextEditLogger(self.log_text_edit)
        self.log_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        
        self.logger = logger

        # Ensure no duplicate handlers
        if not any(isinstance(handler, QTextEditLogger) for handler in self.logger.handlers):
            self.logger.addHandler(self.log_handler)
        
        self.settings_widget.combo_box.currentIndexChanged.connect(self.onchange_loglevel)

    def onchange_loglevel(self, index):
        log_level = self.settings_widget.combo_box.currentText()
        self.logger.setLevel(getattr(logging, log_level))


