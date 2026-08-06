import re
import os
import subprocess
import typing
import logging
from pathlib import Path

from ..functions.file_utils import path_from_feature_layer
import geopandas as gpd

from qgis.core import (
    QgsProcessing,
    QgsProcessingContext,
    QgsProcessingFeedback,
    QgsProcessingParameterBoolean,
    QgsProcessingParameterFeatureSource,
    QgsProcessingParameterField,
    QgsProcessingParameterFile,
    QgsProcessingParameterFolderDestination,
    QgsProcessingParameterString
)

from . import AlgorithmBase, QgsFeedbackHandler


class AddGaugesAlgorithm(AlgorithmBase):

    __NAME__ = "Add gauge locations"
    __GROUP__ = "Wflow"

    BASE = "BASE"
    INPUT = "INPUT"
    GAUGE_VECTOR = "GAUGE_VECTOR"
    GAUGE_NAME_FIELD = "GAUGE_NAME_FIELD"
    BASE_NAME = "BASE_NAME"
    SNAP_TO_RIVER = "SNAP_TO_RIVER"
    DERIVE_SUBCATCHMENTS = "DERIVE_SUBCATCHMENTS"
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
                self.GAUGE_VECTOR,
                self.tr('Add gauges from vector layer'),
                [QgsProcessing.TypeVectorPoint],
            )
        )
        self.addParameter(
            QgsProcessingParameterField(
                name=self.GAUGE_NAME_FIELD,
                description=self.tr('Field with the name of the gauges'),
                parentLayerParameterName=self.GAUGE_VECTOR,
                type=QgsProcessingParameterField.String,
            )
        )
        self.addParameter(
            QgsProcessingParameterString(
                name=self.BASE_NAME,
                description=self.tr('Use base name for the gauges function'),
                defaultValue="gauges",
            )
        )
        self.addParameter(
            QgsProcessingParameterBoolean(
                name=self.SNAP_TO_RIVER,
                description=self.tr('Snap to river'),
                defaultValue=True,
            )
        )
        self.addParameter(
            QgsProcessingParameterBoolean(
                name=self.DERIVE_SUBCATCHMENTS,
                description=self.tr('Derive subcatchments'),
                defaultValue=True,
            )
        )

        # Destination folder for the updated wflow model
        self.addParameter(
            QgsProcessingParameterFolderDestination(
                self.TARGET,
                self.tr('Target folder for the wflow model with the gauges')
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
        except ImportError as e:
            feedback.reportError("Failed to import required libraries. Please run installer (Plugins->WFlow->Configuration)")
            return {}
        
        # Get the base path of the updated wflow model
        base_path = Path(parameters[self.TARGET])
        input_path = Path(parameters[self.INPUT])

        # Create a CSV file with the gauges
        # - load data from the vector layer
        gauge_vector = self.parameterAsVectorLayer(parameters, self.GAUGE_VECTOR, context)

        # Create output dir
        output_dir = base_path / f"{input_path.stem}_v1_with_gauges"
        os.makedirs(output_dir, exist_ok=True)

        # # Set up logging
        log.initialize_logging(file_path=Path(f"{output_dir}/logging.log"),
                            level=10) # 10 is debug

        handler = QgsFeedbackHandler(feedback)
        hydromt_logger = logging.getLogger("hydromt")
        hydromt_logger.setLevel(logging.INFO)
        hydromt_logger.addHandler(handler)
        try:
            # Instantiate model
            model = WflowSbmModel(
                root=input_path.parent,
                mode="r",
                config_filename=input_path.name,
            )

            # read model
            model.read()

            gauges_file = path_from_feature_layer(gauge_vector.source())
   
            # Add guages to model
            model.setup_gauges(
                gauges_fn=gauges_file,
                snap_to_river=True,
                derive_subcatch=True
            )

            # set root and write updated model
            model.root.set(path=output_dir, mode="w")
            model.write()
        finally:
            # Remove the handler to avoid duplicate logs in subsequent runs
            hydromt_logger.removeHandler(handler)

        return {}
