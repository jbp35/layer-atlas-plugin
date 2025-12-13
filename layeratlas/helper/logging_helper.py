import logging
from qgis.core import QgsMessageLog, Qgis

LOG_GROUP = "Layer Atlas"


class QGISLogHandler(logging.Handler):
    """Custom logging handler that sends messages to QGIS message log."""
    
    def __init__(self, group_name=LOG_GROUP):
        super().__init__()
        self.group_name = group_name
        
    def emit(self, record):
        """Emit a log record to QGIS message log."""
        try:
            msg = self.format(record)
            level = self._get_qgis_level(record.levelno)
            QgsMessageLog.logMessage(msg, self.group_name, level=level)
        except Exception:
            # Handle any errors that might occur during logging
            self.handleError(record)
    
    def _get_qgis_level(self, python_level):
        """Convert Python logging level to QGIS message level."""
        if python_level >= logging.ERROR:
            return Qgis.MessageLevel.Critical
        elif python_level >= logging.WARNING:
            return Qgis.MessageLevel.Warning
        elif python_level >= logging.INFO:
            return Qgis.MessageLevel.Info
        else:
            return Qgis.MessageLevel.Info


def setup_logger(name=None, level=logging.DEBUG):
    """Set up a logger with QGIS handler."""
    logger = logging.getLogger(name or LOG_GROUP)
    
    # Avoid adding multiple handlers to the same logger
    if not logger.handlers:
        handler = QGISLogHandler()
        formatter = logging.Formatter('%(name)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(level)
        # Prevent propagation to avoid double logging
        logger.propagate = False
    
    return logger


# Create a default logger for the plugin
logger = setup_logger()