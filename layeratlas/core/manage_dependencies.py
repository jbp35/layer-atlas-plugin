import sys
import os
import subprocess
import platform

from qgis.PyQt.QtWidgets import QMessageBox
from qgis.PyQt.QtCore import QT_VERSION_STR
from layeratlas.helper.logging_helper import setup_logger

logger = setup_logger(__name__)
plugin_dir = os.path.dirname(os.path.dirname(__file__))


def confirm_install(iface) -> bool:
    """
    Prompts the user with a message to install the 'PyQtWebEngine' package if not already installed.

    """
    # Detect PyQt version to show appropriate message
    qt_major = QT_VERSION_STR[0]
    if qt_major == "6":
        package_name = "PyQt6-WebEngine"
    else:
        package_name = "PyQtWebEngine"

    mbox = QMessageBox()
    mbox.setIcon(QMessageBox.Icon.Information)
    mbox.setText(
        f"To use Layer Atlas plugin, '{package_name}' Python package must be installed.\n\nWould you like to install it now?"
    )
    mbox.setWindowTitle("Missing Dependencies")
    mbox.setStandardButtons(
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
    )
    mbox.setDefaultButton(QMessageBox.StandardButton.Yes)

    def button_clicked():
        logger.info(mbox.clickedButton().text())
        if mbox.clickedButton().text() == "&Yes":
            install_dependencies()
            restart_qgis(iface)

    mbox.open(button_clicked)


def install_dependencies():
    """
    Installs PyQtWebEngine using pip.

    """
    import pip

    operating_system = platform.system()
    qt_major = QT_VERSION_STR[0]

    if qt_major == "5":
        dependency = "PyQtWebEngine"
        webengine_module = "PyQt5.QtWebEngineWidgets"
    elif qt_major == "6":
        dependency = "PyQt6-WebEngine"
        webengine_module = "PyQt6.QtWebEngineWidgets"
    else:
        logger.warning("Unable to detect PyQt version. Defaulting to PyQt5.")
        dependency = "PyQtWebEngine"
        webengine_module = "PyQt5.QtWebEngineWidgets"

    # Check if the appropriate WebEngine module is already available
    try:
        __import__(webengine_module)
        logger.info("{} is already available".format(dependency))
        return
    except ImportError:
        logger.info("{} not available, installing {}".format(webengine_module, dependency))

        # Install the dependency based on the operating system
        if operating_system == "Darwin":
            pip.main(["install", dependency])
        elif operating_system == "Linux":
            subprocess.check_call([sys.executable, "-m", "pip", "install", dependency])
        elif operating_system == "Windows":
            subprocess.check_call(["python3", "-m", "pip", "install", dependency])


def restart_qgis(iface):
    """
    Prompts the user with a message to restart QGIS for changes to take effect.

    Args:
        iface: A QGIS interface instance that provides access to QGIS GUI elements.
    """

    message = "For the changes to take effect, you need to restart QGIS."
    message += "\n\nWould you like to close QGIS now?"

    reply = QMessageBox.question(
        None,
        "Restart QGIS",
        message,
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        QMessageBox.StandardButton.Yes,
    )

    if reply == QMessageBox.StandardButton.Yes:
        iface.actionExit().trigger()