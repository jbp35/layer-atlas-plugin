from layeratlas.helper.logging_helper import setup_logger

logger = setup_logger(__name__)


def import_from_paths(import_paths, class_name_error=None):
    """Try to import a class from the first available module in the given paths.
    
    Args:
        import_paths (list): List of tuples containing (module_name, class_name)
        error_message (str, optional): Custom error message if all imports fail
        
    Returns:
        The imported class
        
    Raises:
        ImportError: If none of the import paths succeed
    """
    for module_name, class_name in import_paths:
        try:
            module = __import__(module_name, fromlist=[class_name])
            class_obj = getattr(module, class_name)
            logger.info(f"{class_name} : Found in {module_name}")
            return class_obj
        except (ImportError, AttributeError):
            continue
    
    logger.critical(f"{class_name_error} : NOT FOUND")
    raise ImportError(f"{class_name_error} : NOT FOUND")


"""Import QWebEngineView from the first available library."""
import_qwebengineview = [
    ('qgis.gui', 'QgsWebEngineView'),
    ('qgis.PyQt.QtWebEngineWidgets', 'QWebEngineView'),
    ('PyQt6.QtWebEngineWidgets', 'QWebEngineView'),
    ('PyQt5.QtWebEngineWidgets', 'QWebEngineView'),
]

QWebEngineView = import_from_paths(import_qwebengineview, class_name_error="QWebEngineView")

"""Import QWebChannel from the first available library."""
import_qwebchannel = [
    ('PyQt6.QtWebChannel', 'QWebChannel'),
    ('PyQt5.QtWebChannel', 'QWebChannel'),
]

QWebChannel = import_from_paths(import_qwebchannel, class_name_error="QWebChannel")

"""Import QWebSocketServer from the first available library."""
import_qwebsocketserver = [
    ('PyQt6.QtWebSockets', 'QWebSocketServer'),
    ('PyQt5.QtWebSockets', 'QWebSocketServer'),
]

QWebSocketServer = import_from_paths(import_qwebsocketserver, class_name_error="QWebSocketServer")

"""Import QHostAddress from the first available library."""
import_qhostaddress = [
    ('PyQt6.QtNetwork', 'QHostAddress'),
    ('PyQt5.QtNetwork', 'QHostAddress'),
]
QHostAddress = import_from_paths(import_qhostaddress, class_name_error="QHostAddress")


"""Import QWebChannelAbstractTransport from the first available library."""
import_qwebchannelabstracttransport = [
    ('PyQt6.QtWebChannel', 'QWebChannelAbstractTransport'),
    ('PyQt5.QtWebChannel', 'QWebChannelAbstractTransport'),
]

QWebChannelAbstractTransport = import_from_paths(
    import_qwebchannelabstracttransport,
    class_name_error="QWebChannelAbstractTransport"
)