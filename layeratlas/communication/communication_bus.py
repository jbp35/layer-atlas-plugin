from __future__ import annotations

import os
import json
import tempfile
from qgis.utils import iface

from qgis.core import QgsApplication, QgsProject, QgsLayerDefinition, QgsSettings
from qgis.utils import iface
from qgis.PyQt.QtCore import QObject, pyqtSignal, pyqtSlot,QByteArray, QBuffer, QIODevice
from qgis.PyQt.QtGui import QImage, QPainter
from qgis.PyQt.QtWidgets import QFileDialog, QDialog

from layeratlas.core.download_file_task import DownloadFileTask
from layeratlas.helper.logging_helper import setup_logger

logger = setup_logger(__name__)
from layeratlas.core.load_file import loadFile
from layeratlas.gui.select_dataset_layers import SelectDatasetLayersDialog


class communicationBus(QObject):
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
        logger.info("Starting to add layer to project")
        
        if not LayerDefinitionXML or not LayerDefinitionXML.strip():
            logger.error("LayerDefinitionXML is empty or None")
            return False
            
        try:
            with tempfile.NamedTemporaryFile(suffix=".qlr", delete=False) as temp_file:
                temp_file.write(LayerDefinitionXML.encode("utf-8"))
                temp_file.flush()
                logger.debug(f"Created temporary layer definition file: {temp_file.name}")

                result = QgsLayerDefinition.loadLayerDefinition(
                    temp_file.name,
                    QgsProject.instance(),
                    QgsProject.instance().layerTreeRoot(),
                )
                
                if not result:
                    logger.error("Failed to load layer definition into project")
                    return False

            os.remove(temp_file.name)
            logger.info("Successfully added layer to project and cleaned up temporary file")
            return True
        except Exception as e:
            logger.error(f"Error adding layer to project: {e}")
            return False

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
        logger.info(f"Starting download dataset process with destination folder: {dest_folder}")
        
        if not requests:
            logger.error("No requests provided for download")
            return False
            
        try:
            requests = json.loads(requests)
            logger.debug(f"Successfully parsed {len(requests)} download requests")
        except json.JSONDecodeError as e:
            logger.error("Error decoding JSON string: {}".format(e))
            return False

        # Replace homePath variable with the actual home path
        if dest_folder.startswith("$homePath"):
            logger.debug("Resolving $homePath variable in destination folder")
            project = QgsProject.instance()
            home_path = project.homePath()
            if home_path:
                original_dest = dest_folder
                dest_folder = dest_folder.replace("$homePath", home_path)
                logger.debug(f"Resolved destination folder from '{original_dest}' to '{dest_folder}'")
            else:
                logger.warning("Project home path is not available, destination folder will be empty")
                dest_folder = ""

        # If the destination folder is not specified, ask the user to select one
        if dest_folder == "":
            logger.debug("No destination folder specified, prompting user to select one")
            dest_folder = QFileDialog.getExistingDirectory(
                None, "Select File Download Folder ", "", QFileDialog.Option.ShowDirsOnly
            )
            if dest_folder:
                logger.debug(f"User selected destination folder: {dest_folder}")
            else:
                logger.debug("User cancelled folder selection dialog")

        # Check if path is specified
        if not dest_folder:
            logger.warning("No download folder specified - cancelling download task")
            return False

        # Ensure the destination folder exists
        if not os.path.exists(dest_folder):
            logger.info(f"Destination folder does not exist, creating: {dest_folder}")
            try:
                os.makedirs(dest_folder)
                logger.info(f"Successfully created destination folder: {dest_folder}")
            except Exception as e:
                logger.error(f"Failed to create destination folder '{dest_folder}': {e}")
                return False
        else:
            logger.debug(f"Using existing destination folder: {dest_folder}")

        # If multiple requests are provided, ask the user to select the ones to download
        if len(requests) > 1:
            logger.debug(f"Multiple requests ({len(requests)}) found, prompting user to select")
            dialog = SelectDatasetLayersDialog(requests)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                requests = dialog.selectedRequests()
                logger.debug(f"User selected {len(requests)} requests for download")
            else:
                logger.warning("No requests selected - cancelling download task")
                return False
        else:
            logger.debug(f"Single request found, proceeding with download")

        # Create a download task for each request
        logger.info(f"Creating {len(requests)} download tasks")
        try:
            self.tasks = [DownloadFileTask(request, dest_folder) for request in requests]
            for i, task in enumerate(self.tasks):
                task.taskCompleted.connect(
                    lambda task=task: loadFile(task.dest_path, task.file_name)
                )
                QgsApplication.taskManager().addTask(task)
                logger.debug(f"Added download task {i+1}/{len(self.tasks)} to task manager")
            
            logger.info(f"Successfully initiated {len(self.tasks)} download tasks")
            return True
        except Exception as e:
            logger.error(f"Error creating download tasks: {e}")
            return False

    @pyqtSlot(result=str)
    def getMapCanvasImage(self):
        """
        Captures the current map canvas from the QGIS interface.

        Returns:
            str: A Base64 encoded string representing the JPEG image of the current map canvas.
        """
        logger.info("Starting map canvas image capture")
        
        try:
            if not iface or not iface.mapCanvas():
                logger.error("QGIS interface or map canvas is not available")
                return ""
            
            canvas_size = iface.mapCanvas().size()
            logger.debug(f"Map canvas size: {canvas_size.width()}x{canvas_size.height()}")
            
            # Capture the map canvas
            image = QImage(canvas_size, QImage.Format.Format_ARGB32_Premultiplied)
            
            if image.isNull():
                logger.error("Failed to create QImage for map canvas")
                return ""
                
            painter = QPainter(image)
            if not painter.isActive():
                logger.error("Failed to create QPainter for map canvas")
                return ""
                
            iface.mapCanvas().render(painter)
            painter.end()
            logger.debug("Successfully rendered map canvas to image")

            # Convert to Base64
            byte_array = QByteArray()
            buffer = QBuffer(byte_array)
            buffer.open(QIODevice.OpenModeFlag.WriteOnly)
                
            if not image.save(buffer, "JPEG"):
                logger.error("Failed to save image to buffer")
                return ""
                
            base64_data = byte_array.toBase64().data().decode("utf-8")
            logger.debug(f"Successfully converted map canvas to base64 (length: {len(base64_data)} characters)")
            
            return base64_data
        except Exception as e:
            logger.error(f"Error capturing map canvas image: {e}")
            return ""

    @pyqtSlot(str, result=str)
    def getQgsSetting(self, key):
        """
        Retrieves a setting value from QGIS settings based on the provided key.

        Args:
            key (str): The key for the setting to retrieve.

        Returns:
            str: The value of the setting in JSON string format.
        """
        logger.info(f"Retrieving QGIS setting for key: '{key}'")
        
        if not key:
            logger.error("Setting key is empty or None")
            return json.dumps(None)
            
        try:
            settings = QgsSettings()
            raw_value = settings.value(key)
            value = json.dumps(raw_value)
            logger.debug(f"Successfully retrieved setting '{key}': {raw_value}")
            return value
        except Exception as e:
            logger.error(f"Error retrieving QGIS setting '{key}': {e}")
            return json.dumps(None)

    @pyqtSlot(result=str)
    def getPluginVersion(self):
        """
        Retrieves the version of the plugin from the metadata.txt file.

        Returns:
            str: The version of the plugin.
        """
        logger.info("Retrieving plugin version")
        
        if self.plugin_version is not None:
            logger.debug(f"Using cached plugin version: {self.plugin_version}")
            return self.plugin_version

        try:
            current_dir = os.path.dirname(os.path.dirname(__file__))
            metadata_path = os.path.join(current_dir, "metadata.txt")
            logger.debug(f"Looking for metadata.txt at: {metadata_path}")
            
            if not os.path.exists(metadata_path):
                logger.error(f"metadata.txt file not found at: {metadata_path}")
                return None

            with open(metadata_path, "r") as file:
                for line_num, line in enumerate(file, 1):
                    if line.startswith("version="):
                        version = line.split("=")[1].strip()
                        self.plugin_version = version
                        logger.debug(f"Found plugin version '{version}' at line {line_num}")
                        return version
                        
            logger.warning("No version line found in metadata.txt file")
            return None
        except Exception as e:
            logger.error(f"Error reading plugin version from metadata.txt: {e}")
            return None
