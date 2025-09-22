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
    QgsVectorFileWriter,
    QgsEditorWidgetSetup
)
from requests import options
# Import the GUI of the dialog
from .ui.ui_landuseChooseFile import Ui_landuseChooseFile

class ChangeLanduse(QDialog):
    mapping_options = {
        'globcover':{'map': 
                     {"Post-flooding or irrigated croplands (or aquatic)": 11, 
                      "Rainfed croplands": 14,
                      "Mosaic cropland (50-70%) / vegetation (grassland/shrubland/forest) (20-50%)": 20,
                      "Mosaic vegetation (grassland/shrubland/forest) (50-70%) / cropland (20-50%)":30,
                      "Closed to open (>15%) broadleaved evergreen or semi-deciduous forest (>5m)":40,
                      "Closed (>40%) broadleaved deciduous forest (>5m)":50,
                      "Open (15-40%) broadleaved deciduous forest/woodland (>5m)":60,
                      "Closed (>40%) needleleaved evergreen forest (>5m)":70,
                      "Open (15-40%) needleleaved deciduous or evergreen forest (>5m)":90,
                      "Closed to open (>15%) mixed broadleaved and needleleaved forest (>5m)":100,
                      "Mosaic forest or shrubland (50-70%) / grassland (20-50%)":110,
                      "Mosaic grassland (50-70%) / forest or shrubland (20-50%)":120,
                      "Closed to open (>15%) (broadleaved or needleleaved, evergreen or deciduous) shrubland (<5m)":130,
                      "Closed to open (>15%) herbaceous vegetation (grassland, savannas or lichens/mosses)":140,
                      "Sparse (<15%) vegetation":150,
                      "Closed to open (>15%) broadleaved forest regularly flooded (semi-permanently or temporarily) - Fresh or brackish water":160,
                      "Closed (>40%) broadleaved forest or shrubland permanently flooded - Saline or brackish water":170,
                      "Closed to open (>15%) grassland or woody vegetation on regularly flooded or waterlogged soil - Fresh, brackish or saline water":180,
                      "Artificial surfaces and associated areas (Urban areas >50%)":190,
                      "Bare areas":200,
                      "Water bodies":210,
                      "Permanent snow and ice":220,
                      "No data (burnt areas, clouds,...)":230}},
        'esa_worldcover':{'map': 
                          {"Tree cover": 10, 
                           "Shrubland": 20,
                           "Grassland": 30,
                           "Cropland": 40,
                           "Built-up": 50,
                           "Bare / sparse vegetation": 60,
                           "Snow and Ice":70,
                           "Permanent water bodies": 80,
                           "Herbaceous wetland":90,
                           "Mangroves": 95,
                           "Moss and lichen": 96}},
        'vito' : {'map': 
              {"No input data available":0,
               "Closed forest, evergreen needle leaf":111,
               "Closed forest, deciduous needle leaf":113,
               "Closed forest, evergreen broad leaf":112,
               "Closed forest, deciduous broad leaf":114,
               "Closed forest, mixed":115,
               "Closed forest, unknown":116,
               "Open forest, evergreen needle leaf":121,
               "Open forest, deciduous needle leaf":123,
               "Open forest, evergreen broad leaf":122,
               "Open forest deciduous broad leaf":124,
               "Open forest, mixed":125,
               "Open forest, unknown":126,
               "Shrubs":20,
               "Herbaceous vegetation":30,
               "Herbaceous wetland":90,
               "Moss and lichen":100,
               "Bare / sparse vegetation":60,
               "Cultivated and managed vegetation/argiculture (cropland)":40,
               "Urban / built up":50,
               "Snow and Ice":70,
               "Permanent water bodies":80,
               "Open sea":200
               }},
        'corine': {'map': {
            "Continuous urban fabric":111,
            "Discontinuous urban fabric":112,
            "Industrial or commercial units":121,
            "Road and rail networks and associated land":122,
            "Port areas":123,
            "Airports":124,
            "Mineral extraction sites":131,
            "Dump sites":132,
            "Construction sites":133,
            "Green urban areas":141,
            "Sport and leisure facilities":142,
            "Non-irrigated arable land":211,
            "Permanently irrigated land":212,
            "Rice fields":213,
            "Vineyards":221,
            "Fruit trees and berry plantations":222,
            "Olive groves":223,
            "Pastures":231,
            "Annual crops associated with permanent crops":241,
            "Complex cultivation patterns":242,
            "Land principally occupied by agriculture, with significant areas of natural vegetation":243,
            "Agro-forestry areas":244,
            "Broad-leaved forest":311,
            "Coniferous forest":312,
            "Mixed forest":313,
            "Natural grassland":321,
            "Moors and heathland":322,
            "Sclerophyllous vegetation":323,
            "Transitional woodland-scrub":324,
            "Beaches, dunes, sands":331,
            "Bare rocks":332,
            "Sparsely vegetated areas":333,
            "Burnt areas":334,
            "Glaciers and perpetual snow":335,
            "Inland marshes":411,
            "Peat bogs":412,
            "Salt marshes":421,
            "Salines":422,
            "Intertidal flats":423,
            "Water courses":511,
            "Water bodies":512,
            "Coastal lagoons":521,
            "Estuaries":522,
            "Sea and ocean":523
        }}}


    def __init__(self, iface):
        '''
        Initializes this tool
        '''
        self.iface = iface
        QDialog.__init__(self)
        
        # Set up the user interface from Designer.
        self.ui = Ui_landuseChooseFile()
        self.ui.setupUi(self)

        #add options to file field
        self.ui.mQgsFileWidget.setStorageMode(QgsFileWidget.SaveFile)
        self.ui.mQgsFileWidget.setFilter("GeoPackage (*.gpkg)")
        # Connect the slots should include the button for exporting to file. 
        self.ui.pushButton.setEnabled(False)
        # Check if an actual filepath is chosen.
        self.ui.mQgsFileWidget.fileChanged.connect(self.update_button_state)
        self.ui.comboBox.addItems(['globcover', 'esa_worldcover', 'vito', 'corine'])
        self.ui.comboBox.setCurrentIndex(-1)
        self.ui.comboBox.currentIndexChanged.connect(self.update_button_state)
        self.ui.pushButton.clicked.connect(self.change_landuse)

    def update_button_state(self):
        file_ok = bool(self.ui.mQgsFileWidget.filePath())
        combo_ok = self.ui.comboBox.currentIndex() != -1
        self.ui.pushButton.setEnabled(file_ok and combo_ok)

    def change_landuse(self):
        """
        Creates an (empty) vector layer with the appropriate attribute fields for a landuse layer.
        Geometry can be added to the vector layer using the vector tool in qgis. 
        """
        # get all the layers from the input
        file_path = self.ui.mQgsFileWidget.filePath()
        crs = QgsProject.instance().crs()
        # first create virtual layer
        landuse_layer = QgsVectorLayer(f"Polygon?crs={crs.authid()}", "Temporary landuse layer", "memory")
        provider = landuse_layer.dataProvider()
        # Add the attributes associated with the reseservoir to the virtual layer
        landuse_layer.startEditing()
        provider.addAttributes([
            QgsField("fid", QMetaType.Int),
            QgsField("land use value", QMetaType.Int),
            ])
        landuse_layer.commitChanges()
        
        # write the virtual layer to a file
        QgsVectorFileWriter.writeAsVectorFormatV3(
            landuse_layer,
            file_path,
            QgsProject.instance().transformContext(),
            QgsVectorFileWriter.SaveVectorOptions()
        )
        # Add the written layer to the project
        layer_name = os.path.splitext(os.path.basename(file_path))[0]
        written_layer = QgsVectorLayer(file_path, layer_name, "ogr")
        QgsProject.instance().addMapLayer(written_layer)
        # Mapping of the legend values (landuse names) is only present in QGIS
        # The field value saved in the geopackage is the number corresponding to the class. 
        idx_change = written_layer.fields().indexFromName('land use value')
        mapping = self.ui.comboBox.currentText()
        written_layer.setEditorWidgetSetup(idx_change, QgsEditorWidgetSetup('ValueMap', self.mapping_options[mapping]))
        self.accept()  # This closes the dialog