import re
import subprocess
import os
import typing
from pathlib import Path
import logging

from qgis.core import (
    QgsProcessing,
    QgsProcessingContext,
    QgsProcessingFeedback,
    QgsProcessingParameterFeatureSource,
    QgsProcessingParameterFile,
    QgsProcessingParameterFolderDestination,
)
from qgis import processing
import geopandas as gpd

from . import AlgorithmBase, QgsFeedbackHandler
from ..functions.file_utils import path_from_feature_layer

class UpdateReservoirsAlgorithm(AlgorithmBase):

    __NAME__ = "Add reservoirs"
    __GROUP__ = "Add NBS"

    BASE = "BASE"
    INPUT = "INPUT"
    RESERVOIR_VECTOR = "RESERVOIR_VECTOR"
    TARGET = "TARGET"


    PROGRESS_REGEX = re.compile(r"(\d+)\% Completed")


    def init_algorithm(self, config):

        # We add the input vector features source. It can have any kind of
        # geometry.
        self.addParameter(
            QgsProcessingParameterFile(
                name=self.INPUT,
                description=self.tr('Input .toml-file of wflow'),
                extension="toml"
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.RESERVOIR_VECTOR,
                self.tr('Add reservoirs from vector layer'),
                [QgsProcessing.TypeVectorPolygon],
            )
        )

        # Destination folder for the updated wflow model
        self.addParameter(
            QgsProcessingParameterFolderDestination(
                self.TARGET,
                self.tr('Target folder for the wflow model with the updated reservoirs')
            )
        )

    def process_algorithm(
            self,
            parameters: typing.Dict[str, typing.Any],
            context: QgsProcessingContext,
            feedback: typing.Optional[QgsProcessingFeedback]
        ) -> typing.Dict[str, typing.Any]:


        # Deferred import to avoid crashing QGis when plugin is not loaded correctly. Users have to
        # install the required packages first.
        try:
            from hydromt_wflow import WflowSbmModel
            from hydromt import log
            import xarray as xr
        except ImportError as e:
            feedback.reportError("Failed to import required libraries. Please run installer (Plugins->WFlow->Configuration)")
            return {}
        
        # Get the base path of the updated wflow model
        base_path = Path(parameters[self.TARGET])
        input_path = Path(parameters[self.INPUT])
        reservoir_layer = self.parameterAsVectorLayer(parameters, self.RESERVOIR_VECTOR, context)

        # Set up logging
        log.initialize_logging(file_path=Path(f"{base_path}/logging.log"),
                            level=10) # 10 is debug
        
        handler = QgsFeedbackHandler(feedback)
        hydromt_logger = logging.getLogger("hydromt")
        hydromt_logger.setLevel(logging.INFO)
        hydromt_logger.addHandler(handler)
        try:
            # Read model
            model = WflowSbmModel(root=input_path.parent, mode="r", config_filename=input_path.name)
            model.read()

            reservoirs_gpkg = path_from_feature_layer(reservoir_layer.source())

            # update model with reservoirs
            model.setup_reservoirs_simple_control(reservoirs_fn=reservoirs_gpkg, min_area=0.0)
            model.root.set(path=base_path, mode="w")
            model.write()
        finally:
            # Remove the handler to avoid duplicate logs in subsequent runs
            hydromt_logger.removeHandler(handler)

        return {}
