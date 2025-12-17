# -*- coding: utf-8 -*-
"""
/***************************************************************************
 FallbackWidget
                                 A QGIS plugin
 Fallback widget when WebEngine is not available
                             -------------------
        begin                : 2024-07-04
        git sha              : $Format:%H$
        copyright            : (C) 2024 by Layer Atlas
        email                : contact@layeratlas.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
import os

from qgis.gui import QgisInterface
from qgis.PyQt import QtWidgets
from qgis.PyQt.QtWidgets import QTextEdit


class FallbackWidget(QtWidgets.QWidget):
    """Widget to display when WebEngine is not available."""
    
    def __init__(self, iface: QgisInterface, parent=None):
        """Constructor."""
        super().__init__(parent)
        self.iface = iface
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the user interface."""
        self.page_layout = QtWidgets.QVBoxLayout(self)
       
        from qgis.PyQt.QtCore import QT_VERSION_STR
        qt_major = QT_VERSION_STR[0]
        plugin_dir = os.path.dirname(os.path.dirname(__file__))

        self.fallback_view = QTextEdit()
        self.fallback_view.setReadOnly(True)
        readme_path = os.path.join(
            plugin_dir, "resources", "templates", f"missing_pyqtwebengine_qt{qt_major}.html"
        )
        with open(readme_path, "r", encoding="utf-8") as file:
            self.fallback_view.setHtml(file.read())
        
        self.page_layout.addWidget(self.fallback_view)