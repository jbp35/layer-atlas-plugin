# Getting Started with Layer Atlas

This guide will help you set up Layer Atlas by ensuring all necessary dependencies are installed. Please follow the instructions according to the method you used to install QGIS.


## About Layer Atlas

Discover and share geospatial map layers effortlessly with the new Layer Atlas plugin for QGIS. This powerful tool enables fast and precise searches ensuring you find the layers you need quickly. Preview layers directly within QGIS to assess suitability, and conveniently add them to your project with a simple drag-and-drop interface. Save frequently used layers to your favorites for easy access, streamlining your workflow and enhancing collaboration in geospatial projects.


Watch a short video of Layer Atlas to see the plugin in action:


[![IMAGE ALT TEXT HERE](https://img.youtube.com/vi/k5k74faBJKo/0.jpg)](https://www.youtube.com/watch?v=k5k74faBJKo)



## Prerequisites

Layer Atlas requires the installation of extra dependencies. Ensure you have administrative access on your system to perform these installations.

### For QGIS Standalone Installer Users

1. **Verify QGIS Version**: Open QGIS and check the version under the help menu. Ensure it is at least `QGIS 3.38.0 Grenoble`.
2. **Close QGIS**: Ensure QGIS is completely closed before proceeding.
3. **Open OSGEO4W Shell**: Navigate to the Windows start menu, search for `OSGEO4W Shell`, and open it.
4. **Install PyQtWebEngine**: In the OSGEO4W Shell, execute the command: `python -m pip install PyQtWebEngine`
5. **Verify Installation**: If successful, you should see a message similar to `Successfully installed PyQtWebEngine-5.15.6 PyQtWebEngine-Qt5-5.15.2`.
6. **Restart QGIS**: Open QGIS again to complete the setup.

### For OSGeo4W Network Installer Users

1. **Verify QGIS Version**: Ensure your QGIS version is at least `QGIS 3.38.0 Grenoble` by checking under the help menu.
2. **Close QGIS**: Make sure QGIS is not running.
3. **Run OSGeo4W Network Installer**: Download (if not already done) and execute the OSGeo4W Network installer.
4. **Select Package**: During installation, choose the additional package `python3-pyqtwebengine` from the list of available packages.
5. **Restart QGIS**: After the installation, launch QGIS to finalize the setup.

## Installation of the plugin

Layer Atlas is currently in the development phase and has not been officially released in the QGIS plugin repository. For users interested in testing the plugin, please follow these steps:

1. Download the ZIP file of this repository.
2. Extract the contents of the ZIP file.
3. Copy the extracted folder to your QGIS plugin directory, typically located at:

   `C:\Users\YOUR_USERNAME\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\layer-atlas-plugin`


## Support

For any issues or further assistance, please open an issue in the project's GitHub repository.
