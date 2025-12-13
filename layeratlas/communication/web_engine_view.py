import os
from qgis.core import QgsMapLayerType, QgsLayerDefinition
from qgis.PyQt.QtCore import QUrl, Qt
from layeratlas.helper.logging_helper import setup_logger

logger = setup_logger(__name__)

# Try different WebEngine implementations in order of preference
import_attempts = [
    ('qgis.gui', 'QgsWebEngineView'),
    ('qgis.PyQt.QtWebEngineWidgets', 'QWebEngineView'),
    ('PyQt5.QtWebEngineWidgets', 'QWebEngineView'),
    ('PyQt6.QtWebEngineWidgets', 'QWebEngineView'),
]

web_engine_class = None
web_engine_module = None

for module_name, class_name in import_attempts:
    try:
        module = __import__(module_name, fromlist=[class_name])
        web_engine_class = getattr(module, class_name)
        web_engine_module = module_name
        logger.debug(f"Successfully imported {class_name} from {module_name}")
        break
    except (ImportError, AttributeError) as e:
        logger.debug(f"Failed to import {class_name} from {module_name}: {e}")
        continue

if web_engine_class is None:
    logger.critical("No WebEngine implementation found. Please install PyQtWebEngine (pip install PyQtWebEngine) or ensure QGIS WebEngine is available.")
    raise ImportError("No WebEngine implementation available")


class WebEngineView(web_engine_class):
    def __init__(self, _iface):
        super().__init__()
        self.iface = _iface
        class_name = getattr(web_engine_class, '__name__', 'Unknown')
        logger.info(f"WebEngine initialized using {web_engine_module}.{class_name}")

        self.setAcceptDrops(True)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        self.start_web_channel()

    def start_web_channel(self):
        # setup the QWebSocketServer
        try:
            from PyQt6.QtWebSockets import QWebSocketServer
            from PyQt6.QtNetwork import QHostAddress
            ssl_mode = QWebSocketServer.SslMode.NonSecureMode
            host_address = QHostAddress.SpecialAddress.LocalHost
            logger.debug("Using PyQt6 WebSocket implementation")
        except ImportError:
            try:
                from PyQt5.QtWebSockets import QWebSocketServer
                from PyQt5.QtNetwork import QHostAddress
                ssl_mode = QWebSocketServer.NonSecureMode
                host_address = QHostAddress.LocalHost
                logger.debug("Using PyQt5 WebSocket implementation (PyQt6 not available)")
            except ImportError as e:
                logger.critical(f"QtWebSockets package not found. Please install PyQt5/PyQt6 with WebSockets support. Error: {e}")
                return

        self.server = QWebSocketServer("QWebChannel Standalone Example Server", ssl_mode)
        if not self.server.listen(host_address, 56346):
            logger.critical(f"Failed to start WebSocket server on {host_address}:56346. Error: {self.server.errorString()}")
            return
        else:
            logger.info(f"WebSocket server started successfully on {self.server.serverAddress().toString()}:{self.server.serverPort()}")

        # wrap WebSocket clients in QWebChannelAbstractTransport objects
        from layeratlas.communication.web_socket_client_wrapper import WebSocketClientWrapper
        self.client_wrapper = WebSocketClientWrapper(self.server)

        # setup the WebChannel
        try:
            from PyQt6.QtWebChannel import QWebChannel
        except ImportError:
            from PyQt5.QtWebChannel import QWebChannel
        self.channel = QWebChannel()
        self.client_wrapper.client_connected.connect(self.channel.connectTo)
        logger.debug("QWebChannel initialized and connected to WebSocket client wrapper")

        # setup the communicationBus and publish it to the QWebChannel
        from layeratlas.communication.communication_bus import communicationBus
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
