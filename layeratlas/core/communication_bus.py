import os
import json
import tempfile

from qgis.core import QgsApplication, QgsProject, QgsLayerDefinition, QgsSettings
from qgis.utils import iface
from qgis.PyQt.QtCore import (
    QObject,
    pyqtSlot,
    pyqtSignal,
    QByteArray,
    QBuffer,
    QIODevice,
)
from qgis.PyQt.QtGui import QImage, QPainter
from qgis.PyQt.QtWidgets import QFileDialog, QDialog

from layeratlas.core.download_file_task import DownloadFileTask
from layeratlas.helper.logging_helper import log
from layeratlas.core.load_file import loadFile
from layeratlas.gui.select_dataset_layers import SelectDatasetLayersDialog


class CommunicationBus(QObject):
    """
    Handle communication with the QwebEngineView.
    """

    def __init__(self):
        super().__init__()
        self.plugin_version = None

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
        with tempfile.NamedTemporaryFile(suffix=".qlr", delete=False) as temp_file:
            temp_file.write(LayerDefinitionXML.encode("utf-8"))
            temp_file.flush()

            QgsLayerDefinition.loadLayerDefinition(
                temp_file.name,
                QgsProject.instance(),
                QgsProject.instance().layerTreeRoot(),
            )

        os.remove(temp_file.name)
        return True

    @pyqtSlot(str, str, result=bool)
    def downloadDataset(self, requests, dest_folder):
        """
        Initiates a download tasks for a list of requests

        Args:
            requests (str): JSON string of requests to download.
            dest_folder (str): The destination folder where the file will be saved.

        Returns:
            bool: True if the task was successfully added to the task manager.
        """
        try:
            requests = json.loads(requests)
        except json.JSONDecodeError as e:
            log("Error decoding JSON string: {}".format(e), "ERROR")
            return False

        # Replace homePath variable with the actual home path
        if dest_folder.startswith("$homePath"):
            project = QgsProject.instance()
            home_path = project.homePath()
            if home_path:
                dest_folder = dest_folder.replace("$homePath", home_path)
            else:
                dest_folder = ""

        # If the destination folder is not specified, ask the user to select one
        if dest_folder == "":
            dest_folder = QFileDialog.getExistingDirectory(
                None, "Select File Download Folder ", "", QFileDialog.ShowDirsOnly
            )

        # Check if path is specified
        if not dest_folder:
            log("No download folder specified - cancelling download task", "WARNING")
            return False

        # Ensure the destination folder exists
        if not os.path.exists(dest_folder):
            os.makedirs(dest_folder)

        # If multiple requests are provided, ask the user to select the ones to download
        if len(requests) > 1:
            dialog = SelectDatasetLayersDialog(requests)
            if dialog.exec_() == QDialog.Accepted:
                requests = dialog.selectedRequests()
            else:
                log("No requests selected - cancelling download task", "WARNING")
                return False

        # Create a download task for each request
        self.tasks = [DownloadFileTask(request, dest_folder) for request in requests]
        for task in self.tasks:
            task.taskCompleted.connect(
                lambda task=task: loadFile(task.dest_path, task.file_name)
            )
            QgsApplication.taskManager().addTask(task)

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

    @pyqtSlot(result=str)
    def getPluginVersion(self):
        """
        Retrieves the version of the plugin from the metadata.txt file.

        Returns:
            str: The version of the plugin.
        """
        if self.plugin_version is not None:
            return self.plugin_version

        current_dir = os.path.dirname(os.path.dirname(__file__))
        metadata_path = os.path.join(current_dir, "metadata.txt")

        with open(metadata_path, "r") as file:
            for line in file:
                if line.startswith("version="):
                    version = line.split("=")[1].strip()
                    return version
        return None
