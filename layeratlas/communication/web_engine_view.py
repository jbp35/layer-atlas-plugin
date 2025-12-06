from qgis.core import QgsMapLayerType, QgsMessageLog, Qgis
from qgis.PyQt.QtCore import QUrl

# Try differenct WebEngine implementations in order of preference
import_attempts = [
    ('qgis.gui', 'QgsWebEngineView'),
    ('qgis.PyQt.QtWebEngineWidgets', 'QWebEngineView'),
    ('PyQt5.QtWebEngineWidgets', 'QWebEngineView'),
    ('PyQt6.QtWebEngineWidgets', 'QWebEngineView'),
]

for module_name, class_name in import_attempts:
    try:
        module = __import__(module_name, fromlist=[class_name])
        web_engine_class = getattr(module, class_name)
        break
    except (ImportError, AttributeError):
        QgsMessageLog.logMessage("No WebEngine implementation found. Please install PyQtWebEngine or ensure QGIS WebEngine is available.", "Layer Atlas", Qgis.Critical)
        continue


class WebEngineView(web_engine_class):
    def __init__(self):
        super().__init__()
        
        QgsMessageLog.logMessage("WebEngine implementation found.", "Layer Atlas", Qgis.Info)

        # setup the QWebSocketServer
        try:
            from PyQt6.QtWebSockets import QWebSocketServer
            from PyQt6.QtNetwork import QHostAddress
            ssl_mode = QWebSocketServer.SslMode.NonSecureMode
            host_address = QHostAddress.SpecialAddress.LocalHost
            QgsMessageLog.logMessage("PyQt6 WebSocket modules found", "Layer Atlas", Qgis.Info)
        except ImportError:
            try:
                from PyQt5.QtWebSockets import QWebSocketServer
                from PyQt5.QtNetwork import QHostAddress
                ssl_mode = QWebSocketServer.NonSecureMode
                host_address = QHostAddress.LocalHost
                QgsMessageLog.logMessage("PyQt5 WebSocket modules found", "Layer Atlas", Qgis.Info)
            except ImportError:
                QgsMessageLog.logMessage("QtWebSockets package not found.", "Layer Atlas", Qgis.Critical)
                return

        self.server = QWebSocketServer("QWebChannel Standalone Example Server", ssl_mode)
        if not self.server.listen(host_address, 56346):
            QgsMessageLog.logMessage("Failed to open web socket server.", "Layer Atlas", Qgis.Critical)

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
        QgsMessageLog.logMessage("Web channel set up", "Layer Atlas", Qgis.Info)

        # setup the communicationBus and publish it to the QWebChannel
        from layeratlas.communication.communication_bus import communicationBus
        self.communication_bus = communicationBus()
        self.channel.registerObject("communicationBus", self.communication_bus)
        QgsMessageLog.logMessage("Communication bus registered", "Layer Atlas", Qgis.Info)
    
    def set_url(self, url):
        self.setUrl(QUrl(url))