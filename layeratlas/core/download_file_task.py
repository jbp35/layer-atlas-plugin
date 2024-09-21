import os
import re
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
from urllib.parse import urlparse

from qgis.core import QgsProject, QgsTask
from qgis.PyQt.QtWidgets import QFileDialog

from layeratlas.helper.logging_helper import log
from layeratlas.core.load_file import loadFile


# Define the retry strategy
retry_strategy = Retry(
    total=4,  # Maximum number of retries
    backoff_factor=2,  # Exponential backoff factor
    status_forcelist=[429, 500, 502, 503, 504],  # HTTP status codes to retry on
)

# Create an HTTP adapter with the retry strategy and mount it to session
adapter = HTTPAdapter(max_retries=retry_strategy)
session = requests.Session()
session.mount("http://", adapter)
session.mount("https://", adapter)


class DownloadFileTask(QgsTask):
    def __init__(self, url, dest_folder, chunk_size=1024, headers=None, params=None):
        super().__init__("Download File:", QgsTask.CanCancel)
        self.url = url
        self.dest_folder = dest_folder
        self.dest_path = ""
        self.chunk_size = chunk_size
        self.total_size = 0
        self.downloaded_size = 0
        self.file_name = None
        self.headers = headers
        self.params = params

        # Try to parse response header
        self.parse_response_header()

        # If could not get filename from header, use the last part of the URL
        if not self.file_name:
            self.file_name = os.path.basename(urlparse(self.url).path)

        # Replace homePath variable with the actual home path
        if self.dest_folder.startswith("$homePath"):
            project = QgsProject.instance()
            home_path = project.homePath()
            if home_path:
                self.dest_folder = dest_folder.replace("$homePath", home_path)
            else:
                self.dest_folder = ""

        # If the destination folder is not specified, ask the user to select one
        if self.dest_folder == "":
            self.dest_folder = QFileDialog.getExistingDirectory(
                None, "Select File Download Folder ", "", QFileDialog.ShowDirsOnly
            )

        # Normalize the destination path
        self.dest_path = os.path.normpath(
            os.path.join(self.dest_folder, self.file_name)
        ).replace("\\", "/")

        self.setDescription(f"Downloading File: {self.file_name}")

    def run(self):

        # Check if path is specified
        if not self.dest_folder:
            log("No download folder specified - cancelling download task", "WARNING")
            return False

        # Ensure the destination folder exists
        if not os.path.exists(self.dest_folder):
            os.makedirs(self.dest_folder)

        # Check if the file already exists
        if os.path.exists(self.dest_path):
            log(f"Skipping download - File already exists: {self.dest_path}", "INFO")
            return True

        # Download the file
        try:
            response = session.get(
                self.url, stream=True, headers=self.headers, params=self.params
            )
            response.raise_for_status()

            with open(self.dest_path, "wb") as file:
                for chunk in response.iter_content(chunk_size=self.chunk_size):
                    if self.isCanceled():
                        return False
                    if chunk:
                        file.write(chunk)
                        self.downloaded_size += len(chunk)
                        if self.total_size:
                            progress = (self.downloaded_size / self.total_size) * 100
                            self.setProgress(progress)

            log(f"File downloaded successfully: {self.dest_path}", "SUCCESS")

            return True

        except requests.exceptions.RequestException as e:
            log(f"An error occurred during download: {e}", "CRITICAL")
            return False

    def cancel(self):
        log("Download task canceled by the user", "WARNING")
        super().cancel()

    def finished(self, result):
        if result:
            log("Download completed successfully", "SUCCESS")
            loadFile(self.dest_path, self.file_name)
        else:
            if os.path.exists(self.dest_path):
                log("Removing temporary files", "INFO")
                os.remove(self.dest_path)

    def parse_response_header(self) -> bool:
        """
        Parses the response header to extract the filename and total size of the file to be downloaded.

        Returns:
            bool: True if the headers were successfully parsed

        """
        try:
            response = session.head(
                self.url, allow_redirects=True, headers=self.headers, params=self.params
            )
            content_disposition = response.headers.get("content-disposition")
            self.total_size = int(response.headers.get("content-length", 0))
        except requests.exceptions.RequestException as e:
            log(f"Failed to get filename from content-disposition header: {e}", "INFO")
            return False

        if content_disposition:
            filename_match = re.findall('filename="(.+)"', content_disposition)
            if filename_match:
                self.file_name = filename_match[0]

        return True
