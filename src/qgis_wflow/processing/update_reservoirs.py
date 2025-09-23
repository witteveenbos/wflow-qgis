import re
import subprocess
import typing
from pathlib import Path

from qgis.core import (
    QgsProcessing,
    QgsProcessingContext,
    QgsProcessingFeedback,
    QgsProcessingParameterFeatureSource,
    QgsProcessingParameterFile,
    QgsProcessingParameterFolderDestination,
)
from qgis import processing

from . import AlgorithmBase


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
                self.tr('Target folder for the terraced wflow model')
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
        base_path = Path(parameters[self.TARGET])
        
        # create the file for the reservoirs geopackage and ensure the directory exists
        reservoirs_gpkg = base_path / "shapes" / "update_reservoirs.gpkg"
        if not reservoirs_gpkg.parent.exists():
            reservoirs_gpkg.parent.mkdir(parents=True, exist_ok=True)

        # use the native processing algorithm to save the vector layer with resevoirs to a geopackage
        processing.run(
            "native:savefeatures",
            {
                'INPUT': parameters[self.RESERVOIR_VECTOR],
                'OUTPUT': str(reservoirs_gpkg)
            }
        )
        feedback.pushInfo(f"Saved reservoirs to {reservoirs_gpkg}")
        # Create the required files
        
        RESERVOIR_FN = "hydro_reservoirs" # TODO: parameterize this
        ini_file = base_path / "build_update_reservoirs.ini"
        with open(ini_file, "w") as f:
            f.write("[setup_reservoirs]\n")
            f.write(f"reservoirs_fn   = {RESERVOIR_FN} # source for reservoirs shape and attributes \n")  
            f.write("min_area        = None             # minimum lake area to consider [km2]\n")
        yml_file = base_path / "data_catalog_update_reservoirs.yml"
        with open(yml_file, "w") as f:
            lines = [
                # f"root: {str(base_path)}\n",
                # "meta:\n",
                # "  version: '2023.11'\n",
                # "\n",
                f"{RESERVOIR_FN}:\n"
                "  crs: 4326\n"
                "  data_type: GeoDataFrame\n"
                "  driver: vector\n"
                "  filesystem: local\n"
                f"  path: ./shapes/{reservoirs_gpkg.name}\n"
                "  nodata: -99\n"
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
