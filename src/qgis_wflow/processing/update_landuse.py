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
    QgsProcessingParameterFeatureSource,
    QgsProcessingParameterField,
    QgsProcessingParameterFile,
    QgsProcessingParameterFolderDestination,
    QgsProcessingParameterRasterLayer,
)

from . import AlgorithmBase


LULC_MAPS = [
    "globcover",
    "esa_worldcover",
    "vito",
    "corine"
]

LULC_META = {
    "esa_worldcover": [
        "    category: landuse\n",
        "    source_license: CC BY 4.0\n",
        "    source_url: https://doi.org/10.5281/zenodo.5571936\n",
        "    source_version: v100\n",
    ],
    "globcover": [
        "    category: landuse\n",
        "    paper_doi: 10.1594/PANGAEA.787668\n",
        "    paper_ref: Arino et al (2012)\n",
        "    source_license: CC-BY-3.0\n",
        "    source_url: http://due.esrin.esa.int/page_globcover.php\n",
        "    source_version: v2.3\n",
    ],
    "vito": [
        "    category: landuse\n",
        "    paper_doi: 10.5281/zenodo.3939038\n",
        "    paper_ref: Buchhorn et al (2020)\n",
        "    source_url: https://land.copernicus.eu/global/products/lc\n",
        "    source_version: v2.0.2\n",
    ],
    "corine": [
        "    category: landuse\n",
        "    source_author: European Environment Agency\n",
        "    source_license: https://land.copernicus.eu/pan-european/corine-land-cover/clc2018?tab=metadata\n",
        "    source_url: https://land.copernicus.eu/pan-european/corine-land-cover/clc2018\n",
        "    source_version: v.2020_20u1\n",
    ]
}


class UpdateLandUseAlgorithm(AlgorithmBase):

    __NAME__ = "Change landuse"
    __GROUP__ = "Add NBS"

    BASE = "BASE"
    INPUT = "INPUT"
    # which area of the raster will be updated
    LAND_USE_VECTOR = "LAND_USE_VECTOR"
    # what should be the new value of the cells that are updated
    LAND_USE_FIELD = "LAND_USE_FIELD"
    LULC_MAP = "LULC_MAP"
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
            QgsProcessingParameterEnum(
                name=self.LULC_MAP,
                description=self.tr('lulc mapping'),
                options=LULC_MAPS,
                defaultValue=0,
            )
        )
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.BASE,
                self.tr('Original land use layer')
            )
        )
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.LAND_USE_VECTOR,
                self.tr('Update land use with vector layer'),
                [QgsProcessing.TypeVectorPolygon],
                optional=True
            )
        )
        self.addParameter(
            QgsProcessingParameterField(
                name=self.LAND_USE_FIELD,
                description=self.tr('Field with land use values'),
                parentLayerParameterName=self.LAND_USE_VECTOR,
                # type=QgsProcessingParameterField.Numeric,
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


        # Deferred import to avoid crashing QGis when plugin is not loaded correctly. Users have to
        # install the required packages first.
        try:
            import hydromt_wflow
        except ImportError as e:
            feedback.reportError("Failed to import required libraries. Please run installer (Plugins->WFlow->Configuration)")
            return {}
        
        # Get the base path of the updated wflow model
        base_path = Path(parameters[self.TARGET])
        # Copy the input file to the target location
        base_raster = self.parameterAsRasterLayer(parameters, self.BASE, context)
        base_raster_path = Path(base_raster.dataProvider().dataSourceUri())
        target_raster_path = base_path / 'shapes' / f'{base_raster_path.stem}_update_landuse{base_raster_path.suffix}'
        if not target_raster_path.parent.exists():
            target_raster_path.parent.mkdir(parents=True, exist_ok=True)
        feedback.pushInfo(f"Copying {base_raster_path} to {base_path / 'shapes' / f'{base_raster_path.stem}_update_landuse{base_raster_path.suffix}'}")
        shutil.copy2(base_raster_path, target_raster_path)

        if parameters[self.LAND_USE_VECTOR] is not None:
            algresult = processing.run(
                "gdal:rasterize_over",
                {
                    'INPUT' : parameters[self.LAND_USE_VECTOR],
                    'FIELD' : parameters[self.LAND_USE_FIELD],
                    'INPUT_RASTER' : str(target_raster_path),
                    'ADD' : False,
                    'EXTRA' : '',
                },
                context=context,
                feedback=feedback,
                is_child_algorithm=True
            )

        # Create the required files
        ini_file = base_path / "build_update_landuse.ini"
        with open(ini_file, "w") as f:
            f.write("[setup_lulcmaps]\n")
            f.write(f"lulc_fn         = {LULC_MAPS[parameters[self.LULC_MAP]]}          # source for lulc maps: {{globcover, vito, corine}})\n")
        yml_file = base_path / "data_catalog_update_landuse.yml"
        with open(yml_file, "w") as f:
            lines = [
                f"root: {str(base_path)}\n",
                "meta:\n",
                "  version: '2023.11'\n",
                "\n",
                f"{LULC_MAPS[parameters[self.LULC_MAP]]}:\n",
                "  crs: 4326\n",
                "  data_type: RasterDataset\n",
                "  driver: raster\n",
                "  filesystem: local\n",
                f"  path: ./shapes/{target_raster_path.name}\n",
                "  meta:\n",
                *LULC_META[LULC_MAPS[parameters[self.LULC_MAP]]]
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
