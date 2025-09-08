from __future__ import absolute_import
from enum import IntEnum
import math
import os
import traceback
import numpy as np
# Imports from QT
from qgis.PyQt.QtWidgets import QDialog, QFileDialog, QMessageBox
from qgis.PyQt.QtCore import QMetaType
from qgis.gui import QgsFileWidget
# Imports from QGis
from qgis.core import (
    QgsVectorLayer,
    QgsField,
    QgsProject,
    QgsVectorFileWriter
)
# Import the GUI of the dialog
from .ui.ui_ChooseFile import Ui_chooseFile

class AddCheckDams(QDialog):
     
    def __init__(self, iface):
        '''
        Initializes this tool
        '''
        self.iface = iface
        QDialog.__init__(self)
        
        # Set up the user interface from Designer.
        self.ui = Ui_chooseFile()
        self.ui.setupUi(self)

        #add options to file field
        self.ui.mQgsFileWidget.setStorageMode(QgsFileWidget.SaveFile)
        self.ui.mQgsFileWidget.setFilter("GeoPackage (*.gpkg)")
        # Connect the slots should include the button for exporting to file. 
        self.ui.pushButton.setEnabled(False)
        # Check if an actual filepath is chosen.
        self.ui.mQgsFileWidget.fileChanged.connect(self.on_file_changed)

        self.ui.pushButton.clicked.connect(self.add_check_dams_layer)

    def on_file_changed(self, file_path):
        # Enable button only if a file path is selected (not empty)
        self.ui.pushButton.setEnabled(bool(file_path))

    def add_check_dams_layer(self):
        """
        Creates an (empty) vector layer with the appropriate attribute fields for a CheckDams layer.
        Geometry can be added to the vector layer using the vector tool in qgis. 
        """
        # get all the layers from the input
        file_path = self.ui.mQgsFileWidget.filePath()
        crs = QgsProject.instance().crs()
        # first create virtual layer
        check_dams_layer = QgsVectorLayer(f"Polygon?crs={crs.authid()}", "Temporary CheckDams layer", "memory")
        provider = check_dams_layer.dataProvider()
        # Add the attributes associated with the check_dams to the virtual layer
        check_dams_layer.startEditing()
        provider.addAttributes([
            QgsField("fid", QMetaType.Int)
            ])
        check_dams_layer.commitChanges()
        
        # write the virtual layer to a file
        QgsVectorFileWriter.writeAsVectorFormatV3(
            check_dams_layer,
            file_path,
            QgsProject.instance().transformContext(),
            QgsVectorFileWriter.SaveVectorOptions()
        )
        # Add the written layer to the project
        written_layer = QgsVectorLayer(file_path, "Check Dams Layer", "ogr")
        QgsProject.instance().addMapLayer(written_layer)

        self.accept()  # This closes the dialog