import os

try:
    from qgis.PyQt.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings
except:
    from .dependencies import confirm_install, install_dependencies
    if confirm_install():
        install_dependencies()
        
from PyQt5.QtWebChannel import QWebChannel

from qgis.PyQt.QtCore import QUrl, Qt
from qgis.core import QgsLayerDefinition

from .backend import Backend

class CustomWebEngineView(QWebEngineView):
    def __init__(self, _iface, *args, **kwargs):
        super(CustomWebEngineView, self).__init__(*args, **kwargs)
        self.iface = _iface
        self.setAcceptDrops(True)
        self.setContextMenuPolicy(Qt.NoContextMenu)
        
        settings = self.settings()
        settings.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.LocalStorageEnabled, True)
        settings.setAttribute(QWebEngineSettings.JavascriptCanOpenWindows, True)
        settings.setAttribute(QWebEngineSettings.WebGLEnabled, True)

        # Configure QWebChannel
        self.backend = Backend()
        self.channel = QWebChannel()
        self.page().setWebChannel(self.channel)
        self.channel.registerObject("backend", self.backend)

        # url = QUrl("http://localhost:9000/?qgis=true")
        url = QUrl("https://www.layeratlas.com/?qgis=true")

        self.setUrl(url)

    def dragEnterEvent(self, event):
        event.accept()

    def dropEvent(self, event):
        # TODO: check mimeData type
        layer_definition = event.mimeData().data(
            "application/qgis.layertree.layerdefinitions"
        )
        xml_data = layer_definition.data().decode("utf-8")
        self.backend.EmitCreateLayer.emit(xml_data)

        event.ignore()

    def add_layer_to_layer_atlas(self):
        layerTreeView = self.iface.layerTreeView()
        selectedNodes = layerTreeView.selectedNodes()
        temp_file_path = "temp.qlr"
        QgsLayerDefinition.exportLayerDefinition(temp_file_path, [selectedNodes[0]])
        with open(temp_file_path, "r") as file:
            layer_definition_xml = file.read()
            self.backend.EmitCreateLayer.emit(layer_definition_xml)
        os.remove(temp_file_path)

