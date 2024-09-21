from qgis.core import QgsMessageLog, Qgis

LOG_GROUP = "Layer Atlas"


def log(message, level):
    if level == "INFO":
        log_level = Qgis.Info
    elif level == "WARNING":
        log_level = Qgis.Warning
    elif level == "CRITICAL":
        log_level = Qgis.Critical
    elif level == "SUCCESS":
        log_level = Qgis.Success

    QgsMessageLog.logMessage(message, LOG_GROUP, level=log_level)
