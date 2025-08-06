import re
import shutil
import subprocess
import typing
from pathlib import Path

from qgis import processing
from qgis.core import (
    QgsProcessing,
    QgsProcessingContext,
    QgsProcessingFeedback,
    QgsProcessingParameterEnum,
    QgsProcessingParameterNumber,
    QgsProcessingParameterFeatureSource,
    QgsProcessingParameterField,
    QgsProcessingParameterFile,
    QgsProcessingParameterFileDestination,
    QgsProcessingParameterFolderDestination,
    QgsProcessingParameterRasterLayer,
)

from . import AlgorithmBase


class ApplyTerracingAlgorithm(AlgorithmBase):

    __NAME__ = "Terracing"
    __GROUP__ = "Update model (experimental)"

    BASE = "BASE"
    INPUT = "INPUT"
    TERRACING_VECTOR = "TERRACING_VECTOR"
    TERRACING_FIELD = "TERRACING_FIELD"
    TARGET = "TARGET"

    PROGRESS_REGEX = re.compile(r"(\d+)\% Completed")

    def init_algorithm(self, config):

        # We add the input vector features source. It can have any kind of
        # geometry.
        self.addParameter(
            QgsProcessingParameterFile(
                name=self.INPUT,
                description=self.tr('Input folder of wflow'),
                behavior=QgsProcessingParameterFile.Folder
            )
        )

        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.BASE,
                self.tr('Original slope layer')
            )
        )
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.TERRACING_VECTOR,
                self.tr('Update slope layer with vector layer'),
                [QgsProcessing.TypeVectorPolygon],
                optional=True
            )
        )
        # @Anne: Maybe Daan wants to configute the model with a field that contains the slope value
        # which should be used for terracing.
        self.addParameter(
        QgsProcessingParameterNumber(
                name=self.TERRACING_FIELD,
                description=self.tr('Terracing value to multiply the slope layer'),
                type=QgsProcessingParameterNumber.Double,
                defaultValue=0.5, 
                optional=True
            )
        )
# QgsProcessingParameterField(
            #     name=self.TERRACING_FIELD,
            #     description=self.tr('Field with terracing values'),
            #     parentLayerParameterName=self.TERRACING_VECTOR,
            #     type=QgsProcessingParameterField.Numeric,
            #     optional=True
            # )

        # For now we just add a file destination parameter. Can be nicer when users can select a destination folder
        # and the name of the file is automatically generated (or the name is a parameter as well).
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
        """Process the algorithm.

        Args:
            parameters (typing.Dict[str, typing.Any]): The parameters of the algorithm.
            context (QgsProcessingContext): The processing context.
            feedback (QgsProcessingFeedback): The feedback object to report progress and messages.
       
        Returns:
            typing.Dict[str, typing.Any]: The results of the algorithm.
        """

        # Deferred import to avoid crashing QGis when plugin is not loaded correctly. Users have to
        # install the required packages first.
        try:
            import hydromt_wflow
        except ImportError as e:
            feedback.reportError("Failed to import required libraries. Please run installer (Plugins->WFlow->Configuration)")
            return {}
        
        # # Get the folder to copy the wflow model into
        # base_path = Path(parameters[self.TARGET])

        # # Copy the input file to the target location
        # base_raster = self.parameterAsRasterLayer(parameters, self.BASE, context)
        # base_raster_path = Path(base_raster.dataProvider().dataSourceUri())
        # target_raster_path = base_path / 'shapes' / f'{base_raster_path.stem}_update_landuse{base_raster_path.suffix}'
        # if not target_raster_path.parent.exists():
        #     target_raster_path.parent.mkdir(parents=True, exist_ok=True)
        # feedback.pushInfo(f"Copying {base_raster_path} to {base_path / 'shapes' / f'{base_raster_path.stem}_update_landuse{base_raster_path.suffix}'}")
        # shutil.copy2(base_raster_path, target_raster_path)

        # Get the input folder and target folder paths
        input_folder = Path(parameters[self.INPUT])
        target_folder = Path(parameters[self.TARGET])

        # Copy the entire input folder into the target folder
        if target_folder.exists():
            shutil.rmtree(target_folder)
        shutil.copytree(input_folder, target_folder)

        feedback.pushInfo(f"Copied folder {input_folder} to {target_folder}")
        for file in target_folder.iterdir():
            if file.suffix == ".toml":
                new_file = file.with_name(f"{file.stem}_with_terracing{file.suffix}") 
                file.rename(new_file)

        # @Anne: The code below is the work-horse of the algorithm. It will update the slope layer (a raster layer) with
        # the values from the vector layer. This code should be adapted to work with the terracing vector layer. If Daan
        # wants to use a fixed value for terracing, you have to change the algorithm 'gdal:rasterize_over' to 
        # 'gdal:rasterize_over_fixed_value'. You can run the algorithm in QGIS and select the Advanced (bottom left corner)
        # and then Copy as Python Command. This will give you the code to use in the algorithm.
        base_raster = self.parameterAsRasterLayer(parameters, self.BASE, context)
        base_raster_path = base_raster.dataProvider().dataSourceUri()
        if parameters[self.TERRACING_VECTOR] is not None:
                processing.run(
                    "gdal:rastercalculator", 
                    {
                        'INPUT_A':base_raster_path,
                        'BAND_A':1,
                        'FORMULA':f'A*{parameters[self.TERRACING_FIELD]}',
                        'EXTENT_OPT':2,
                        'RTYPE':5,
                        'OUTPUT':'TEMPORARY_OUTPUT'
                    },
                    context=context,
                    feedback=feedback,
                    is_child_algorithm=True
                )
        # if parameters[self.LAND_USE_VECTOR] is not None:
        #     algresult = processing.run(
        #         "gdal:rasterize_over",
        #         {
        #             'INPUT' : parameters[self.TERRACING_VECTOR],
        #             'FIELD' : parameters[self.TERRACING_FIELD],
        #             'INPUT_RASTER' : str(target_raster_path),
        #             'ADD' : False,
        #             'EXTRA' : '',
        #         },
        #         context=context,
        #         feedback=feedback,
        #         is_child_algorithm=True
        #     )

        # Create the required files
        # @Anne: the code below is not yet implemented. It should create the ini and yml files required by hydromt_wflow.
        #        You can ask Daan what the contents of these files should be.
        # ini_file = target_folder / "build_apply_terracing.ini"
        # with open(ini_file, "w") as f:
        #     f.write("[setup_lulcmaps]\n")
        #     f.write(f"lulc_fn         = {LULC_MAPS[parameters[self.LULC_MAP]]}          # source for lulc maps: {{globcover, vito, corine}})\n")
        # yml_file = target_folder / "data_catalog_apply_terracing.yml"
        # with open(yml_file, "w") as f:
        #     lines = [
        #         f"root: {str(target_folder)}\n",
        #         "meta:\n",
        #         "  version: '2023.11'\n",
        #         "\n",
        #         f"{LULC_MAPS[parameters[self.LULC_MAP]]}:\n",
        #         "  crs: 4326\n",
        #         "  data_type: RasterDataset\n",
        #         "  driver: raster\n",
        #         "  filesystem: local\n",
        #         f"  path: ./shapes/{target_raster_path.name}\n",
        #         "  meta:\n",
        #         *LULC_META[LULC_MAPS[parameters[self.LULC_MAP]]]
        #     ]
        #     f.writelines(lines)
   
        # # Run the hydromt command to update the land use map -> taken from land use. in this case should alter the slope layer in the staticmaps.nc 
        # process = subprocess.Popen(
        #     [
        #         Path(hydromt_wflow.__file__).parent.parent.parent / "Scripts" / "hydromt.exe",
        #         "update",
        #         "wflow",
        #         str(Path(parameters[self.INPUT]).parent),
        #         "-o", str(base_path),
        #         "-i", str(ini_file),
        #         "-d", str(yml_file),
        #         "-vvv",
        #     ],
        #     stdout=subprocess.PIPE,
        #     stderr=subprocess.STDOUT,
        #     shell=True,
        #     encoding='utf-8',
        #     errors='replace'
        # )
        # while (realtime_output := process.stdout.readline()) != '' or process.poll() is None:
        #     if realtime_output:
        #         match = self.PROGRESS_REGEX.search(realtime_output)
        #         if match:
        #             feedback.setProgress(int(match.group(1)))
        #         else:
        #             feedback.pushInfo(realtime_output.strip())

        return {}
