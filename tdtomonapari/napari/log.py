import logging
from qtpy.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QComboBox, QLabel

class LogSettingsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
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
    def __init__(self, parent=None):
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
        
        # Get the logger and add the custom handler
        self.logger = logging.getLogger('tomobase_logger')
        self.logger.addHandler(self.log_handler)
        self.logger.setLevel(logging.DEBUG)
        
        self.settings_widget.combo_box.currentIndexChanged.connect(self.onchange_loglevel)

    def onchange_loglevel(self, index):
        log_level = self.settings_widget.combo_box.currentText()
        match log_level:
            case "DEBUG":
                self.logger.setLevel(logging.DEBUG)
            case "INFO":
                self.logger.setLevel(logging.INFO)
            case "WARNING":
                self.logger.setLevel(logging.WARNING)
            case "ERROR":
                self.logger.setLevel(logging.ERROR)
            case "CRITICAL":
                self.logger.setLevel(logging.CRITICAL)

