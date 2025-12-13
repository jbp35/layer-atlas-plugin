from qgis.PyQt.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QVBoxLayout,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QLineEdit,
    QDialogButtonBox,
)
from qgis.PyQt.QtCore import Qt


class SelectDatasetLayersDialog(QDialog):
    def __init__(self, requests, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Files to Download")
        self.dialog_layout = QVBoxLayout(self)
        self.resize(400, 300)

        # Search box
        self.searchBox = QLineEdit(self)
        self.searchBox.setPlaceholderText("Search...")
        self.searchBox.textChanged.connect(self.filterList)
        self.dialog_layout.addWidget(self.searchBox)

        self.listWidget = QListWidget(self)

        for request in requests:
            listItem = QListWidgetItem(request["name"])
            listItem.setCheckState(Qt.CheckState.Checked)
            listItem.setData(Qt.ItemDataRole.UserRole, request)
            listItem.setToolTip(request.get("url", ""))
            self.listWidget.addItem(listItem)

        self.dialog_layout.addWidget(self.listWidget)

        # Create check/uncheck all buttons
        buttonLayout = QHBoxLayout()
        self.checkAllButton = QPushButton("Check All", self)
        self.uncheckAllButton = QPushButton("Uncheck All", self)
        self.checkAllButton.clicked.connect(self.checkAll)
        self.uncheckAllButton.clicked.connect(self.uncheckAll)
        buttonLayout.addWidget(self.checkAllButton)
        buttonLayout.addWidget(self.uncheckAllButton)
        self.dialog_layout.addLayout(buttonLayout)

        # Create OK/Cancel buttons
        self.buttonBox = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel, self
        )
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.dialog_layout.addWidget(self.buttonBox)

    def checkAll(self):
        for index in range(self.listWidget.count()):
            item = self.listWidget.item(index)
            item.setCheckState(Qt.CheckState.Checked)

    def uncheckAll(self):
        for index in range(self.listWidget.count()):
            item = self.listWidget.item(index)
            item.setCheckState(Qt.CheckState.Unchecked)

    def selectedRequests(self):
        checked_requests = [
            item.data(Qt.ItemDataRole.UserRole)
            for item in self.listWidget.findItems("*", Qt.MatchFlag.MatchWildcard)
            if item.checkState() == Qt.CheckState.Checked
        ]
        return checked_requests

    def filterList(self, text):
        for index in range(self.listWidget.count()):
            item = self.listWidget.item(index)
            item.setHidden(text.lower() not in item.text().lower())
