import re
import shutil
import typing
from pathlib import Path
import xarray as xr
import rioxarray

from qgis import processing
from qgis.core import (
    QgsProcessing,
    QgsProcessingContext,
    QgsProcessingFeedback,
    QgsProcessingParameterNumber,
    QgsProcessingParameterFeatureSource,
    QgsProcessingParameterFile,
    QgsProcessingParameterFolderDestination,
    QgsProcessingParameterRasterLayer,
)

from . import AlgorithmBase
from ..functions.file_utils import delete_folder


class ApplyTerracingAlgorithm(AlgorithmBase):

    __NAME__ = "Add check dams"
    __GROUP__ = "Add NBS (experimental)"

    BASE = "BASE"
    INPUT = "INPUT"
    DAMS_VECTOR = "DAMS_VECTOR"
    DAMS_FIELD = "DAMS_FIELD"
    TARGET = "TARGET"

    PROGRESS_REGEX = re.compile(r"(\d+)\% Completed")

    def init_algorithm(self, config):

        # We add the input vector features source. It can have any kind of
        # geometry.
        self.addParameter(
            QgsProcessingParameterFile(
                name=self.INPUT,
                description=self.tr('Input folder of wflow'),
                extension="toml"
            )
        )

        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.BASE,
                self.tr('Original N_River layer')
            )
        )
        # Vector layer that gives the areas where check dams should be applied
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.DAMS_VECTOR,
                self.tr('Vector layer (locations to apply check dams)'),
                [QgsProcessing.TypeVectorPolygon],
                optional=True
            )
        )
       
        self.addParameter(
        QgsProcessingParameterNumber(
                name=self.DAMS_FIELD,
                description=self.tr('Factor to adjust N_River values'),
                type=QgsProcessingParameterNumber.Double,
                defaultValue=1.5, 
                optional=True
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
        

        # Get the input and target folder from the parameters
        input_folder = Path(parameters[self.INPUT]).parent
        target_folder = Path(parameters[self.TARGET])

        # Copy the entire input folder into the target folder
        delete_folder(target_folder)
        shutil.copytree(input_folder, target_folder)

        feedback.pushInfo(f"Copied folder {input_folder} to {target_folder}")

        # Find and adjust the .toml file in the target folder
        for file in target_folder.iterdir():
            if file.suffix == ".toml":
                new_file = file.with_name(f"{file.stem}_with_check_dams{file.suffix}") 
                file.rename(new_file)
                with open(new_file, "r") as f:
                    lines = f.readlines()
                with open(new_file, "w") as f:
                    for line in lines:
                        if line.strip().startswith("path_static"):
                            f.write('path_static = "staticmaps_with_check_dams.nc"\n')
                        elif line.strip().startswith("casename ="):
                            f.write('casename = "wflow_sbm_with_check_dams"\n')
                        elif line.strip().startswith("dir_output ="):
                            old_folder = line.split("=")[1].strip().strip('"')
                            old_folder_path = target_folder / old_folder
                            # Delete the old folder if it exists
                            delete_folder(old_folder_path)
                            # Create the new folder
                            new_folder_path = target_folder / "run_with_check_dams"
                            new_folder_path.mkdir(parents=True, exist_ok=True)
                            f.write('dir_output = "run_with_check_dams"\n')
                        else:
                            f.write(line)

        # create mask from vector layer. For the raster calculator to work we need a rasterized mask of the terracing vector layer
        base_raster = self.parameterAsRasterLayer(parameters, self.BASE, context)
        base_raster_path = base_raster.dataProvider().dataSourceUri()
        feedback.pushInfo(f"Raster width: {base_raster.width()}, height: {base_raster.height()}, extent: {base_raster.extent()}")
        # change vector layer to raster layer with the terracing values
        mask_raster = target_folder / "dams_mask.tif"
        processing.run(
            "gdal:rasterize",
            {
                'INPUT': parameters[self.DAMS_VECTOR],
                'FIELD': None, 
                'BURN': 1,
                'UNITS': 0,
                'WIDTH': base_raster.width(),
                'HEIGHT': base_raster.height(),
                'EXTENT': base_raster.extent(),
                'NODATA': -999,
                'DATA_TYPE': 5,  # Float32
                'INIT': 0,
                'OUTPUT': str(mask_raster)
            },
            context=context,
            feedback=feedback,
            is_child_algorithm=True
        )

        # given the mask raster and the base raster, create a new raster with the adjusted terracing values
        # hardcoded that the target rasterpath is put into staticmaps.nc":Slope 
        feedback.pushInfo(f"Base raster path: {base_raster_path}")
        orig_nc = target_folder / "staticmaps.nc"
        output_nc = target_folder / "N_River_with_check_dams.tif"
        if parameters[self.DAMS_VECTOR] is not None:
               algresult = processing.run(
                    "gdal:rastercalculator", 
                    {
                        'INPUT_A':base_raster_path,
                        'BAND_A':1,
                        'INPUT_B': str(mask_raster),
                        'BAND_B': 1,
                        'FORMULA': f'A*(1-B)+A*B*{parameters[self.DAMS_FIELD]}',
                        'RTYPE':5,
                        'OUTPUT': str(output_nc)
                    },
                    context=context,
                    feedback=feedback,
                    is_child_algorithm=True
                )
        
        # Open the original netCDF file and add the new slope layer
        ds = xr.open_dataset(orig_nc)
        new_slope = rioxarray.open_rasterio(str(output_nc)).squeeze()
        ds['N_River'] = new_slope
        out_nc = target_folder / "staticmaps_with_check_dams.nc"
        ds.to_netcdf(out_nc)
        ds.close()
        new_slope.close()

        return {}
