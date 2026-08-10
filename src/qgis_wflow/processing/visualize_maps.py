import typing
from pathlib import Path
import tomllib

from . import AlgorithmBase
from ..functions.configuration import wflow_path

from qgis.core import (
    QgsProcessingAlgorithm,
    QgsProcessingContext,
    QgsProcessingFeedback,
    QgsProcessingParameterEnum,
    QgsProcessingParameterFile,
    QgsRasterLayer,
    QgsVectorLayer,
    QgsProject,
    QgsProcessingParameterBoolean,
)
from qgis.utils import iface

LULC_MAPS = [
    "globcover",
    "esa_worldcover",
    "vito",
    "corine"
]


STATIC_MAPS = [
    "cf_soil",
    "Cfmax",
    "EoverR",
    "G_Cfmax",
    "G_SIfrac",
    "G_TT",
    "InfiltCapPath",
    "InfiltCapSoil",
    "KsatHorFrac",
    "land_elevation",
    "land_manning_n",
    "land_slope",
    "land_water_fraction",
    "local_drain_direction",
    "M_",
    "M_original_",
    "M_original",
    "M",
    "MaxLeakage",
    "meta_landuse",
    "meta_soil_texture", 
    "meta_soilgrids_ksat_vertical_10.0cm",
    "meta_soilgrids_ksat_vertical_150.0cm",
    "meta_soilgrids_ksat_vertical_2.5cm",
    "meta_soilgrids_ksat_vertical_22.5cm",
    "meta_soilgrids_ksat_vertical_45.0cm",
    "meta_soilgrids_ksat_vertical_80.0cm",
    "meta_streamorder",
    "meta_upstream_area",
    "outlets",
    "reservoir_area_id",
    "reservoir_area",
    "reservoir_demand",
    "reservoir_max_release",
    "reservoir_max_volume",
    "reservoir_outlet_id",
    "reservoir_target_full_fraction",
    "reservoir_target_min_fraction",
    "river_depth",
    "river_length",
    "river_manning_n",
    "river_mask",
    "river_slope",
    "river_width",
    "rootdistpar",
    "soil_brooks_corey_c",
    "soil_compated_fraction",
    "soil_f_",
    "soil_f",
    "soil_ksat_vertical",
    "soil_theta_r",
    "soil_theta_s",
    "soil_thickness",
    "SoilMinThickness",
    "subcatchment",
    "TT",
    "TTI",
    "TTM",
    "vegetation_feddes_alpha_h1",
    "vegetation_kext",
    "vegetation_leaf_area_index",
    "vegetation_leaf_storage",
    "vegetation_root_depth",
    "vegetation_wood_storage",
    "WHC",
]
# dem landuse soil, subcatch slope LAI volgorde
DEFAULT_STATIC_MAPS = [
    "land_elevation",
    "meta_landuse",
    "meta_soil_texture",
    "subcatchment",
    "land_slope",
    "vegetation_leaf_area_index",
    "river_manning_n",
]

# outlets (allemaal), rivers, reservoirs, subcatch, basins, highres, region
STATIC_GEOMS = ["outlets","rivers", "reservoirs", "meta_reservoirs_simple_control", "subcatchment", "basins", "meta_basins_highres",  "region"]
DEFAULT_STATIC_GEOMS = ["outlets","rivers","basins"]
STATIC_GEOM_STYLE = ["outlets","rivers","basins", "subcatchment", "reservoirs"]


class LoadLayersAlgorithm(AlgorithmBase):

    __NAME__ = "Load layers"
    __GROUP__ = "Wflow"

    INPUT = "INPUT"
    STATIC_MAPS = "STATIC_MAPS"
    STATIC_GEOMS = "STATIC_GEOMS"
    APPLY_STYLING = "APPLY_STYLING"
    LULC_MAPPING = "LULC_MAPPING"

    def flags(self):
        # NOTE: possibly breaking change in version 3.40
        return super().flags() | QgsProcessingAlgorithm.FlagNoThreading

    def init_algorithm(self, config):

        # Let the user select the .toml-file of wflow
        self.addParameter(
            QgsProcessingParameterFile(
                name=self.INPUT,
                description=self.tr("Input .toml-file of wflow"),
                extension="toml",
            )
        )

        # Let the user select the layers of the static maps to visualize
        self.addParameter(
            QgsProcessingParameterEnum(
                name=self.STATIC_MAPS,
                description=self.tr("Static maps to import"),
                options=STATIC_MAPS,
                defaultValue=[
                    i
                    for i in range(len(STATIC_MAPS))
                    if STATIC_MAPS[i] in DEFAULT_STATIC_MAPS
                ],
                allowMultiple=True,
                optional=True,
            )
        )

        # Let the user select the layers of static geoms to visualize
        self.addParameter(
            QgsProcessingParameterEnum(
                name=self.STATIC_GEOMS,
                description=self.tr("Static geometries to import"),
                options=STATIC_GEOMS,
                defaultValue=[
                    i
                    for i in range(len(STATIC_GEOMS))
                    if STATIC_GEOMS[i] in DEFAULT_STATIC_GEOMS
                ],
                allowMultiple=True,
                optional=True,
            )
        )
        # Let the user select whether to apply styling to the imported layers
        self.addParameter(
            QgsProcessingParameterBoolean(
                name=self.APPLY_STYLING,
                description=self.tr("Apply styling to imported layers"),
                defaultValue=False
            )
        )

        # Let the user select the LULC mapping to apply to the land use layer
        self.addParameter(
            QgsProcessingParameterEnum(
                name=self.LULC_MAPPING,
                description=self.tr("LULC mapping to apply"),
                options=LULC_MAPS,
                defaultValue=None,
                optional=True
            )
        )

    def apply_styling(layer_group, present_styles):
        """
        Apply styling to the layers in the group that correspond to the list of present styles.
        The styles are expected to be in the resources/styles directory with the same names as the layer.
        """

    def process_algorithm(
        self,
        parameters: typing.Dict[str, typing.Any],
        context: QgsProcessingContext,
        feedback: typing.Optional[QgsProcessingFeedback],
    ) -> typing.Dict[str, typing.Any]:

        # Process the selected static maps
        # wflow_data = toml.load(parameters[self.INPUT])
        with open(parameters[self.INPUT], 'r') as file:
            file_content = file.read()
        wflow_data = tomllib.loads(file_content)

        # Import static maps
        path_static_maps = (
            Path(parameters[self.INPUT]).parent / wflow_data["input"]["path_static"]
        )
        if parameters[self.STATIC_MAPS]:
            feedback.pushInfo(f"Importing static maps from {path_static_maps}")
            # - create a group in the layer tree for the static maps
            insertion_point = iface.layerTreeInsertionPoint().group
            group_maps = insertion_point.addGroup("Static maps")
            # - create the layers
            for map_id in parameters[self.STATIC_MAPS]:
                # NOTE: the layers are added using the QgsProject instance. This is required to set
                # the name of the layer. The context.temporaryLayerStore() ignores the name of the layer
                # and uses the name of the file instead.
                feedback.pushInfo(f" - importing static map: {STATIC_MAPS[map_id]}")
                layer = QgsRasterLayer(
                    f'NETCDF:"{str(path_static_maps)}":{STATIC_MAPS[map_id]}',
                    STATIC_MAPS[map_id],
                )
                crs = layer.crs()
                crs.createFromId(4326)
                layer.setCrs(crs)
                layer.setName(STATIC_MAPS[map_id])
                QgsProject.instance().addMapLayer(layer, False)
                group_maps.addLayer(layer)

        # Import static geoms
        path_static_geoms = Path(parameters[self.INPUT]).parent / "staticgeoms"
        if parameters[self.STATIC_GEOMS]:
            feedback.pushInfo(f"Importing static geoms from {path_static_geoms}")
            # - create a group in the layer tree for the static geometries
            insertion_point = iface.layerTreeInsertionPoint().group
            group_geoms = insertion_point.addGroup("Static geometries")
            # - get the entries, convert from index to name and add named items to the list
            static_geoms = [
                STATIC_GEOMS[geom_id] for geom_id in parameters[self.STATIC_GEOMS]
            ]
            if "outlets" in static_geoms:
                static_geoms.extend(
                    [
                        file.stem
                        for file in path_static_geoms.glob("gauges*.geojson")
                        if file.stem not in static_geoms
                    ]
                )
            if "subcatchment" in static_geoms:
                static_geoms.remove("subcatchment")
                static_geoms.extend(
                    [
                        file.stem
                        for file in path_static_geoms.glob("subcatch*.geojson")
                        if file.stem not in static_geoms
                    ]
                )
            # - create the layers
            for static_geom in static_geoms:
                if Path(path_static_geoms / f"{static_geom}.geojson").exists():
                    feedback.pushInfo(f" - importing static map: {static_geom}.geojson")
                    layer = QgsVectorLayer(
                        str(path_static_geoms / f"{static_geom}.geojson"),
                        static_geom,
                        "ogr",
                    )
                    layer.setName(static_geom)

                    QgsProject.instance().addMapLayer(layer, False)
                    group_geoms.addLayer(layer)
                else:
                    feedback.pushWarning(f" - {static_geom} selected by no geojson is found")
            
            # Apply styling to the static geometries if checkbox is clicked
            if parameters[self.APPLY_STYLING]:

                # get directory of the plugin gives -> ../src/qgis_wflow/
                current_dir = Path(__file__).parents[1].resolve()
                
                # get standard layers to style
                feedback.pushInfo("Applying style for static maps")
                for layer in group_maps.findLayers():
                    if layer.name() in DEFAULT_STATIC_MAPS:
                        feedback.pushInfo(f" - Applying style for layer: {layer.name()}")
                        #special case for land use layer
                        if layer.name() == "meta_landuse":
                            if parameters[self.LULC_MAPPING] is not None:
                                style_path = current_dir / f"resources/styles/{LULC_MAPS[parameters[self.LULC_MAPPING]]}_style.qml"
                            else:
                                feedback.pushWarning(" -- No LULC mapping selected")
                                style_path = None
                        else:
                            # else the qmd file has the same name as the layer
                            style_path = current_dir / f"resources/styles/{layer.name()}_style.qml"
                        #apply the style to the layer only if the path to the qmd file exists
                        if style_path and style_path.exists():
                            layer.layer().loadNamedStyle(str(style_path))
                            layer.layer().triggerRepaint()
                            
                # do the same for the geojson static geometries (@peter is the repetition of the code here acceptable or should I write a seperate function)
                feedback.pushInfo("Applying style for static geoms")
                for layer in group_geoms.findLayers():
                    if layer.name() in STATIC_GEOM_STYLE:
                        feedback.pushInfo(f" - Applying style for layer: {layer.name()}")
                        style_path = current_dir / f"resources/styles/{layer.name()}_style.qml"
                    elif "gauges_" in layer.name():
                        feedback.pushInfo(f" - Applying style for layer: {layer.name()}")
                        style_path = current_dir / "resources/styles/outlets_style.qml"
                    elif "subcatchment_" in layer.name():
                        feedback.pushInfo(f" - Applying style for layer: {layer.name()}")
                        style_path = current_dir / "resources/styles/subcatchment_sg_style.qml"
                    else:
                        style_path = None

                    if style_path and style_path.exists():
                        layer.layer().loadNamedStyle(str(style_path))
                        layer.layer().triggerRepaint()
        return {}


