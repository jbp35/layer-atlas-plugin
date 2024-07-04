import os
import json
import tempfile

from qgis.core import QgsProject, QgsLayerDefinition, QgsSettings
from qgis.utils import iface
from qgis.PyQt.QtCore import QObject, pyqtSlot, pyqtSignal, QByteArray, QBuffer, QIODevice
from qgis.PyQt.QtGui import QImage, QPainter


class Backend(QObject):
    """
    Handle communication with the QwebEngineView.
    """

    # Signal to create a layer
    EmitCreateLayer = pyqtSignal(str)

    @pyqtSlot(str, result=bool)
    def addLayerToProject(self, LayerDefinitionXML):
        """
        Adds a layer to the current QGIS project using a layer definition XML string.

        Args:
            LayerDefinitionXML (str): The XML string defining the layer to be added.

        Returns:
            bool: True if the layer was successfully added.
        """
        with tempfile.NamedTemporaryFile(suffix='.qlr', delete=False) as temp_file:
            temp_file.write(LayerDefinitionXML.encode('utf-8'))
            temp_file.flush()
            
            QgsLayerDefinition.loadLayerDefinition(
                temp_file.name,
                QgsProject.instance(), 
                QgsProject.instance().layerTreeRoot()
                )
        
        os.remove(temp_file.name)
        return True
        
    @pyqtSlot(result=str)
    def getMapCanvasImage(self):
        """
        Captures the current map canvas from the QGIS interface.

        Returns:
            str: A Base64 encoded string representing the JPEG image of the current map canvas.
        """
        # Capture the map canvas
        image = QImage(iface.mapCanvas().size(), QImage.Format_ARGB32_Premultiplied)
        painter = QPainter(image)
        iface.mapCanvas().render(painter)
        painter.end()

        # Convert to Base64
        byte_array = QByteArray()
        buffer = QBuffer(byte_array)
        buffer.open(QIODevice.WriteOnly)
        image.save(buffer, "JPEG")
        base64_data = byte_array.toBase64().data().decode("utf-8")
        
        return base64_data
    
    @pyqtSlot(str, result=str)
    def getQgsSetting(self, key):
        """
        Retrieves a setting value from QGIS settings based on the provided key.

        Args:
            key (str): The key for the setting to retrieve.

        Returns:
            str: The value of the setting in JSON string format.
        """
        settings = QgsSettings()
        value = json.dumps(settings.value(key))
        return value