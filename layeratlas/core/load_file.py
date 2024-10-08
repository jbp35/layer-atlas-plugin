import os

from qgis.core import (
    QgsProject,
    QgsProviderRegistry,
    QgsCoordinateTransformContext,
    QgsWkbTypes,
    QgsVectorLayer,
)

from layeratlas.helper.logging_helper import log


def loadFile(dest_path: str, file_name: str) -> bool:
    """
    Load a file into the QGIS project.

    Parameters:
    dest_path (str): The destination path of the file to be loaded.
    file_name (str): The name of the file to be loaded.

    Returns:
    True if the file was successfully loaded, False otherwise.
    """
    try:
        provider = QgsProviderRegistry.instance()
        QgsProviderSublayerDetails = provider.querySublayers(dest_path)

        transform_context = QgsCoordinateTransformContext()
        file_name_trimmed = os.path.splitext(file_name)[0]

        # If multiple sublayers are found, add them to a group
        group = None
        if len(QgsProviderSublayerDetails) > 1:
            root = QgsProject.instance().layerTreeRoot()
            group = root.addGroup(file_name_trimmed)

        layers = []
        for QgsProviderSublayerDetail in QgsProviderSublayerDetails:
            options = QgsProviderSublayerDetail.LayerOptions(transform_context)
            layer = QgsProviderSublayerDetail.toLayer(options)
            if layer.name() == "Layer1":
                layer.setName(file_name_trimmed)
            layers.append(layer)

        ordered_layers = order_layers_by_geometry_type(layers)

        if group is None:
            QgsProject.instance().addMapLayers(ordered_layers)
        else:
            QgsProject.instance().addMapLayers(ordered_layers, False)
            for layer in ordered_layers:
                group.addLayer(layer)

        log(f"Successfully loaded: {dest_path}", "SUCCESS")
        return True

    except Exception as e:
        log(f"Failed to load file: {dest_path} - {e}", "CRITICAL")
        return False


def order_layers_by_geometry_type(layers):
    """
    Orders layers by their geometry type.

    Parameters:
    layers: A list of layers to be ordered.

    Returns:
    A list of layers ordered by points, lines, polygons, and others.
    """
    polygons = []
    lines = []
    points = []
    others = []

    for layer in layers:
        if isinstance(layer, QgsVectorLayer):
            if layer.geometryType() == QgsWkbTypes.PolygonGeometry:
                polygons.append(layer)
            elif layer.geometryType() == QgsWkbTypes.LineGeometry:
                lines.append(layer)
            elif layer.geometryType() == QgsWkbTypes.PointGeometry:
                points.append(layer)
            else:
                others.append(layer)
        else:
            others.append(layer)

    return points + lines + polygons + others
