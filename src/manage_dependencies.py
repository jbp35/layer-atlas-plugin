import pathlib
import sys
import os
import subprocess
import platform

from qgis.PyQt.QtWidgets import QTextEdit, QMessageBox

def confirm_install() -> bool:
    """
    Prompts the user with a message to install the 'PyQtWebEngine' package if not already installed.

    Returns:
        bool: True if the user selects 'Yes', indicating they want to install the package. False otherwise.
    """

    message = (
        "To use Layer Atlas plugin, 'PyQtWebEngine' Python package must be installed."
    )
    message += "\n\nWould you like to install it now?"

    reply = QMessageBox.question(
        None,
        "Missing Dependencies",
        message,
        QMessageBox.Yes | QMessageBox.No,
        QMessageBox.Yes,
    )

    if reply == QMessageBox.Yes:
        return True
    return False


def install_dependencies(plugin_dir):
    """
    Installs the required dependencies for a plugin.

    Parameters:
    - plugin_dir (str): The directory path of the plugin for which dependencies are to be installed.
    """
    operating_system = platform.system()
    try:
        import pip
    except ImportError:
        exec(open(str(pathlib.Path(plugin_dir, "scripts", "get-pip.py"))).read())
        import pip

        if operating_system == "Darwin":
            pip.main(["install", "--upgrade", "pip"])
        elif operating_system == "Linux":
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "upgrade", "pip"]
            )
        elif operating_system == "Windows":
            subprocess.check_call(
                ["python3", "-m", "pip", "install", "--upgrade", "pip"]
            )
    sys.path.append(plugin_dir)

    with open(os.path.join(plugin_dir, "requirements.txt"), "r") as requirements:
        for dep in requirements.readlines():
            dep = dep.replace("\n", "")
            dep_noversion = dep.strip().split("==")[0]
            try:
                __import__(dep_noversion)
            except ImportError:
                print("{} not available, installing".format(dep))
                if operating_system == "Darwin":
                    pip.main(["install", dep])
                elif operating_system == "Linux":
                    subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
                elif operating_system == "Windows":
                    subprocess.check_call(["python3", "-m", "pip", "install", dep])
     
     
def restart_qgis(iface):
    """
    Prompts the user with a message to restart QGIS for changes to take effect.

    Args:
        iface: A QGIS interface instance that provides access to QGIS GUI elements.
    """
    
    message = (
        "For the changes to take effect, you need to restart QGIS."
    )
    message += "\n\nWould you like to restart now?"

    reply = QMessageBox.question(
        None,
        "Restart QGIS",
        message,
        QMessageBox.Yes | QMessageBox.No,
        QMessageBox.Yes,
    )

    if reply == QMessageBox.Yes:
        iface.actionExit().trigger()               
                    
def get_html_page(plugin_dir):
    """
    Loads an HTML page from a specified plugin directory and displays it in a read-only QTextEdit widget.

    Args:
        plugin_dir (str): The directory path of the plugin from which the HTML page will be loaded.

    Returns:
        QTextEdit: A QTextEdit widget displaying the HTML content in read-only mode.
    """
    readme_viewer = QTextEdit()
    readme_viewer.setReadOnly(True)
    readme_path = os.path.join(plugin_dir,"src", "templates", "missing_QWebEngineView.html")
    with open(readme_path, "r", encoding="utf-8") as file:
        readme_viewer.setHtml(file.read())

    return readme_viewer

