import logging
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

class QTextEditLogger(logging.Handler):
    def __init__(self, text_edit):
        super().__init__()
        self.text_edit = text_edit

    def emit(self, record):
        msg = self.format(record)
        self.text_edit.append(msg)

class LogWidget(QWidget):
    def __init__(self, viewer: 'napari.viewer.Viewer',parent=None):
        super().__init__(parent)
        
        self.layout = QVBoxLayout(self)

        self.settings_widget = LogSettingsWidget()
        self.log_text_edit = QTextEdit(self)
        self.log_text_edit.setReadOnly(True)
        
        self.layout.addWidget(self.settings_widget)
        self.layout.addWidget(self.log_text_edit)
        self.setLayout(self.layout)
        
        self.log_handler = QTextEditLogger(self.log_text_edit)
        self.log_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        
        self.logger = logger

        if not any(isinstance(handler, QTextEditLogger) for handler in self.logger.handlers):
            self.logger.addHandler(self.log_handler)
        
        self.settings_widget.combo_box.currentIndexChanged.connect(self.onchange_loglevel)

    def onchange_loglevel(self, index):
        log_level = self.settings_widget.combo_box.currentText()
        self.logger.setLevel(getattr(logging, log_level))


