from qtpy.QtWidgets import QApplication, QGridLayout, QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QGroupBox, QToolTip, QMenu, QAction
from qtpy.QtCore import Qt
from qtpy.QtGui import QCursor


from tdtomonapari.registration import TDTOMONAPARI_VARIABLES
from tomobase.globals import logger

class VariablesWidget(QWidget):
    def __init__(self, viewer: 'napari.viewer.Viewer', parent=None):
        super().__init__(parent)
        # I need a table widget to display the variables
        self._viewer = viewer
        self._layout = QGridLayout()

        self.save_button = QPushButton("Save")
        self.load_button = QPushButton("Load")

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(['Name', 'Type', 'Value'])
        self.table.setEditTriggers(QTableWidget.NoEditTriggers) 

        self._layout.addWidget(self.save_button, 0, 0)
        self._layout.addWidget(self.load_button, 0, 1)
        self._layout.addWidget(self.table, 1,0, 1,2)
        self.setLayout(self._layout)

        self.populateTable()

        self.save_button.clicked.connect(self.onSave)
        self.load_button.clicked.connect(self.onLoad)
        TDTOMONAPARI_VARIABLES.refreshed.connect(self.populateTable)

        self.table.setMouseTracking(True)
        self.table.itemEntered.connect(self.onHoverOverItem)

        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.onRightClickMenu)

    def populateTable(self):
        self.table.setRowCount(len(TDTOMONAPARI_VARIABLES))
        for i, (key, item) in enumerate(TDTOMONAPARI_VARIABLES.items()):
            name_item = QTableWidgetItem(item.name)
            type_item = QTableWidgetItem(str(type(item.value).__name__))
            value_item = QTableWidgetItem(str(item.value))
            self.table.setItem(i, 0, name_item)
            self.table.setItem(i, 1, type_item)
            self.table.setItem(i, 2, value_item)

    def onSave(self):
        pass

    def onLoad(self):
        pass 

    def onHoverOverItem(self, item):
        item_name = item.text()
        QToolTip.showText(self.mapToGlobal(self.table.viewport().mapFromGlobal(QCursor.pos())), item_name)

    def onRightClickMenu(self, position):
        index = self.table.indexAt(position)
        if not index.isValid():
            return  
        row = index.row()
        menu = QMenu(self)

        delete_action = QAction("Delete", self)
        edit_action = QAction("Rename", self)
        plot_action = QAction("Plot", self)
        save_action = QAction("Save", self)

        # Connect actions to methods
        delete_action.triggered.connect(lambda: self.onDeleteRow(row))
        edit_action.triggered.connect(lambda: self.onEditRow(row))
        plot_action.triggered.connect(lambda: self.onPlotRow(row))
        save_action.triggered.connect(lambda: self.onSaveRow(row))

        # Add actions to the menu
        menu.addAction(delete_action)
        menu.addAction(edit_action)
        menu.addAction(plot_action)
        menu.addAction(save_action)

        # Show the menu at the cursor position
        menu.exec_(self.table.viewport().mapToGlobal(position))

    def onDeleteRow(self, row):
        pass

    def onEditRow(self, row):
        pass

    def onPlotRow(self, row):
        pass

    def onSaveRow(self, row):
        pass