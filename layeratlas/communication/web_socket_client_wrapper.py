from __future__ import annotations
from qgis.PyQt.QtCore import QObject, pyqtSignal as Signal, pyqtSlot
from layeratlas.communication.web_socket_transport import WebSocketTransport

class WebSocketClientWrapper(QObject):
    """Wraps connected QWebSockets clients in WebSocketTransport objects.

       This code is all that is required to connect incoming WebSockets to
       the WebChannel. Any kind of remote JavaScript client that supports
       WebSockets can thus receive messages and access the published objects.
    """
    client_connected = Signal(WebSocketTransport)

    def __init__(self, server, parent=None):
        """Construct the client wrapper with the given parent. All clients
           connecting to the QWebSocketServer will be automatically wrapped
           in WebSocketTransport objects."""
        super().__init__(parent)
        self._server = server
        self._server.newConnection.connect(self.handle_new_connection)
        self._transports = []

    @pyqtSlot()
    def handle_new_connection(self):
        """Wrap an incoming WebSocket connection in a WebSocketTransport
           object."""
        socket = self._server.nextPendingConnection()
        transport = WebSocketTransport(socket)
        self._transports.append(transport)
        self.client_connected.emit(transport)