import os
from qgis.core import QgsMapLayerType, QgsLayerDefinition
from qgis.PyQt.QtCore import Qt
from layeratlas.helper.logging_helper import setup_logger


logger = setup_logger(__name__)


class WebEngineView(QWebEngineView):
    def __init__(self, _iface):
        super().__init__()
        self.iface = _iface

        self.setAcceptDrops(True)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)

        from layeratlas.communication import QWebEngineView, QWebChannel, QWebSocketServer, QHostAddress
        from layeratlas.communication.web_socket_client_wrapper import WebSocketClientWrapper
        from layeratlas.communication.communication_bus import communicationBus

        # setup the QWebSocketServer
        ssl_mode = QWebSocketServer.SslMode.NonSecureMode
        host_address = QHostAddress.SpecialAddress.LocalHost
        self.server = QWebSocketServer("QWebChannel Layer Atlas Server", ssl_mode)
        if not self.server.listen(host_address, 56346):
            logger.critical(f"Failed to start WebSocket server on {host_address}:56346. Error: {self.server.errorString()}")
            return
        else:
            logger.info(f"WebSocket server started successfully on {self.server.serverAddress().toString()}:{self.server.serverPort()}")

        # wrap WebSocket clients in QWebChannelAbstractTransport objects
        self.client_wrapper = WebSocketClientWrapper(self.server)
        self.channel = QWebChannel()
        self.client_wrapper.client_connected.connect(self.channel.connectTo)
        logger.debug("QWebChannel initialized and connected to WebSocket client wrapper")

        # setup the communicationBus and publish it to the QWebChannel
        self.communication_bus = communicationBus()
        self.channel.registerObject("communicationBus", self.communication_bus)
        logger.info("Communication bus registered with QWebChannel")


    def dragEnterEvent(self, event):
        logger.debug(f"Drag enter event - MIME types: {[fmt for fmt in event.mimeData().formats()]}")
        event.accept()


    def dropEvent(self, event):
        logger.debug("Drop event received - processing layer definition")

        # TODO: check mimeData type
        layer_definition = event.mimeData().data(
            "application/qgis.layertree.layerdefinitions"
        )
        xml_data = layer_definition.data().decode("utf-8")
        self.communication_bus.EmitCreateLayer.emit(xml_data)
        event.ignore()


    def add_layer_to_layer_atlas(self):
        layerTreeView = self.iface.layerTreeView()
        selectedNodes = layerTreeView.selectedNodes()
        if not selectedNodes:
            logger.warning("No layers selected for adding to Layer Atlas")
            return
        
        logger.info(f"Adding layer '{selectedNodes[0].name()}' to Layer Atlas")
        temp_file_path = "temp.qlr"
        QgsLayerDefinition.exportLayerDefinition(temp_file_path, [selectedNodes[0]])
        try:
            with open(temp_file_path, "r") as file:
                layer_definition_xml = file.read()
                self.communication_bus.EmitCreateLayer.emit(layer_definition_xml)
            os.remove(temp_file_path)
            logger.debug("Layer definition successfully sent to communication bus")
        except Exception as e:
            logger.error(f"Failed to process layer definition: {e}")
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
