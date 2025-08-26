import re
import subprocess
import typing
from pathlib import Path

from qgis.core import (
    QgsProcessing,
    QgsProcessingContext,
    QgsProcessingFeedback,
    QgsProcessingParameterFeatureSource,
    QgsProcessingParameterField,
    QgsProcessingParameterFile,
    QgsProcessingParameterFileDestination,
)

from . import AlgorithmBase


class AddGaugesAlgorithm(AlgorithmBase):

    __NAME__ = "Add gauge locations"
    __GROUP__ = "Wflow"

    BASE = "BASE"
    INPUT = "INPUT"
    GAUGE_VECTOR = "GAUGE_VECTOR"
    GAUGE_NAME_FIELD = "GAUGE_NAME_FIELD"
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

        # For now we just add a file destination parameter. Can be nicer when users can select a destination folder
        # and the name of the file is automatically generated (or the name is a parameter as well).
        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.TARGET,
                self.tr('Target toml-file for wflow (should be placed in an empty folder)'),
                fileFilter="*.toml"
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
            import hydromt_wflow
        except ImportError as e:
            feedback.reportError("Failed to import required libraries. Please run installer (Plugins->WFlow->Configuration)")
            return {}
        
        # Get the base path of the updated wflow model
        base_path = Path(parameters[self.TARGET]).parent

        # Create a CSV file with the gauges
        # - load data from the vector layer
        gauge_vector = self.parameterAsSource(parameters, self.GAUGE_VECTOR, context)
        gauges = gauge_vector.getFeatures()
        # - print the gauges to a CSV file
        gauge_csv = base_path / "shapes" / "update_gauges.csv"
        if not gauge_csv.parent.exists():
            gauge_csv.parent.mkdir(parents=True, exist_ok=True)
        with open(gauge_csv, "w") as f:
            # write the header
            f.write("fid,Name,x,y")
            # write the data
            for gauge_fid, gauge in enumerate(gauges, 2):
                gauge_geom = gauge.geometry().asPoint()
                f.write(f"\n{gauge_fid},{gauge[parameters[self.GAUGE_NAME_FIELD]]},{gauge_geom.x()},{gauge_geom.y()}")

        # Create the required files
        GAUGE_FN = "kazhydromet_gauges" # TODO: parameterize this
        ini_file = base_path / "build_update_gauges.ini"
        with open(ini_file, "w") as f:
            f.write("[setup_gauges]\n")
            f.write(f"gauges_fn        = {GAUGE_FN}\n")  
            f.write("snap_to_river   = True\n")  # TODO: parameterize this
            f.write("derive_subcatch = True\n")  # TODO: parameterize this
        yml_file = base_path / "data_catalog_update_gauges.yml"
        with open(yml_file, "w") as f:
            lines = [
                f"root: {str(base_path)}\n",
                "meta:\n",
                "  version: '2023.11'\n",
                "\n",
                f"{GAUGE_FN}:\n"
                "  crs: 4326\n"
                "  data_type: GeoDataFrame\n"
                "  driver: vector\n"
                f"  path: ./shapes/{gauge_csv.name}\n"
            ]
            f.writelines(lines)
        
        # Run the hydromt command to update the land use map
        process = subprocess.Popen(
            [
                Path(hydromt_wflow.__file__).parent.parent.parent / "Scripts" / "hydromt.exe",
                "update",
                "wflow",
                str(Path(parameters[self.INPUT]).parent),
                "-o", str(base_path),
                "-i", str(ini_file),
                "-d", str(yml_file),
                "-vvv",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            shell=True,
            encoding='utf-8',
            errors='replace'
        )
        while (realtime_output := process.stdout.readline()) != '' or process.poll() is None:
            if realtime_output:
                match = self.PROGRESS_REGEX.search(realtime_output)
                if match:
                    feedback.setProgress(int(match.group(1)))
                else:
                    feedback.pushInfo(realtime_output.strip())

        return {}
