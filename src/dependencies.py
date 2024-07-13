import pathlib
import sys
import os
import subprocess
import platform

from qgis.PyQt.QtWidgets import QTextEdit


def confirm_install() -> bool:
    from qgis.PyQt.QtWidgets import QMessageBox

    message = (
        "The following Python packages are required to use the plugin: PyqtWebEngine"
    )
    message += "\n\nWould you like to install them now? After installation please restart QGIS."

    reply = QMessageBox.question(
        None,
        "Missing Dependencies",
        message,
        QMessageBox.Yes | QMessageBox.No,
        QMessageBox.No,
    )

    if reply == QMessageBox.Yes:
        return True
    return False


def install_dependencies():
    plugin_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    operating_system = platform.system()
    try:
        import pip
    except ImportError:
        exec(open(str(pathlib.Path(plugin_dir, "scripts", "get_pip.py"))).read())
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
                    
                    
def get_html_page():
    readme_viewer = QTextEdit()
    readme_viewer.setReadOnly(True)
    current_file_dir = os.path.dirname(os.path.abspath(__file__))
    readme_path = os.path.join(current_file_dir, "missing_QWebEngineView.html")
    with open(readme_path, "r", encoding="utf-8") as file:
        readme_viewer.setHtml(file.read())

    return readme_viewer
