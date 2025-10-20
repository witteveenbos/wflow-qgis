import typing
from pathlib import Path

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
    "wflow_ldd",
    "wflow_uparea",
    "wflow_streamorder",
    "wflow_dem",
    
    "wflow_river",
    "wflow_riverlength",
    "RiverSlope",
    "N_River",
    "wflow_riverwidth",
    "RiverDepth",
    "wflow_landuse",
    "Kext",
    "N",
    "PathFrac",
    "RootingDepth",
    "Sl",
    "Swood",
    "WaterFrac",
    "alpha_h1",
    
    "thetaS",
    "thetaR",
    "SoilThickness",
    "SoilMinThickness",
    "c",
    "KsatVer",
    "KsatVer_2.5cm",
    "KsatVer_10.0cm",
    "KsatVer_22.5cm",
    "KsatVer_45.0cm",
    "KsatVer_80.0cm",
    "KsatVer_150.0cm",
    "M_original_",
    "M_",
    "f_",
    "M_original",
    "M",
    "f",
    "wflow_soil", 
    "wflow_subcatch",
    "Slope",
    "LAI",
    "wflow_gauges",
    "KsatHorFrac",
    "Cfmax",
    "cf_soil",
    "EoverR",
    "InfiltCapPath",
    "InfiltCapSoil",
    "MaxLeakage",
    "rootdistpar",
    "TT",
    "TTI",
    "TTM",
    "WHC",
    "G_Cfmax",
    "G_SIfrac",
    "G_TT",
    "ResDemand",
    "ResMaxRelease",
    "ResMaxVolume",
    "ResSimpleArea",
    "ResTargetFullFrac",
    "ResTargetMinFrac",
    "wflow_reservoirareas",
    "wflow_reservoirlocs",
]
# dem landuse soil, subcatch slope LAI volgorde
DEFAULT_STATIC_MAPS = [
    "wflow_dem",
    "wflow_landuse",
    "wflow_soil",
    "wflow_subcatch",
    "Slope",
    "LAI",
]

# gauges (allemaal), rivers, reservoirs, subcatch, basins, highres, region
STATIC_GEOMS = ["gauges","rivers", "reservoirs", "subcatch", "basins", "basins_highres",  "region"]
DEFAULT_STATIC_GEOMS = ["gauges","rivers","subcatch","basins"]


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

    @staticmethod
    def set_gauge_action(layer):
        """Set the action for the gauges layer."""
        from qgis.core import Qgis, QgsAction
        layer.actions().addAction(
            QgsAction(
                Qgis.AttributeActionType.GenericPython,
                description="Opens a chart showing the discharge time series for the selected location(s). "
                "Clicking on the map will add the selected location to the to the current selection and thus "
                "to the time series for comparison.",
                action=(
                    "from pathlib import Path\n"
                    "import pandas as pd\n"
                    "import plotly.express as px\n"
                    "import plotly.offline as po\n"
                    "from qgis.PyQt import QtWidgets\n"
                    "from qgis.PyQt.QtWebKitWidgets import QWebView\n"
                    "# Determine the location of the file `output.csv` and load the file\n"
                    "# in a DataFrame for further processing\n"
                    "layer = QgsProject.instance().mapLayer('[% @layer_id %]')\n"
                    "layer_path = Path(layer.dataProvider().dataSourceUri())\n"
                    "output_data = layer_path.parent / '../run_default/output.csv'\n"
                    "df_output = pd.read_csv(output_data)\n"
                    "\n"
                    "# Add the clicked points to the selection\n"
                    "layer.selectByExpression(f'\"fid\" = \\'[%fid%]\\'', QgsVectorLayer.AddToSelection)\n"
                    "\n"
                    "# Show the discharge for the selected points\n"
                    "fig = px.line(df_output, x='time', y=[f'Q_{feature[\"fid\"]}' for feature in layer.selectedFeatures()], title='Discharge')\n"
                    "# Rename the traces to the names of the gauges\n"
                    "newnames = {\n"
                    "    f'Q_{feature[\"fid\"]}': feature[\"name\"]\n"
                    "    for feature\n"
                    "    in layer.selectedFeatures()\n"
                    "}\n"
                    "fig.for_each_trace(\n"
                    "    lambda t: t.update(\n"
                    "        name = newnames[t.name],\n"
                    "        legendgroup = newnames[t.name],\n"
                    "        hovertemplate = t.hovertemplate.replace(t.name, newnames[t.name])\n"
                    "    )\n"
                    ")\n"
                    "\n"
                    "# Convert the figure to HTML\n"
                    "raw_html = f'''\n"
                    "<html>\n"
                    "<head>\n"
                    "    <meta charset=\"utf-8\" />\n"
                    "    <script src=\"https://cdn.plot.ly/plotly-latest.min.js\"></script>\n"
                    "</head>\n"
                    "<body>\n"
                    "    {po.plot(fig, include_plotlyjs=False, output_type='div')}\n"
                    "</body>\n"
                    "</html>\n"
                    "'''\n"
                    "# Show the plot in a webview\n"
                    "webview = QWebView(None)\n"
                    "webview.setHtml(raw_html)\n"
                    "webview.show()\n"
                ),
                icon=None,
                capture=False,
                shortTitle="Show discharge time series",
                actionScopes=["Canvas"],
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

        try:
            import toml
        except ImportError:
            feedback.reportError("Please configure wflow plugin to use this algorithm.")

        # Process the selected static maps
        wflow_data = toml.load(parameters[self.INPUT])

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
            if "gauges" in static_geoms:
                static_geoms.extend(
                    [
                        file.stem
                        for file in path_static_geoms.glob("gauges*.geojson")
                        if file.stem not in static_geoms
                    ]
                )
            if "subcatch" in static_geoms:
                static_geoms.remove("subcatch")
                static_geoms.extend(
                    [
                        file.stem
                        for file in path_static_geoms.glob("subcatch*.geojson")
                        if file.stem not in static_geoms
                    ]
                )
            # - create the layers
            for static_geom in static_geoms:
                feedback.pushInfo(f" - importing static map: {static_geom}.geojson")
                layer = QgsVectorLayer(
                    str(path_static_geoms / f"{static_geom}.geojson"),
                    static_geom,
                    "ogr",
                )
                layer.setName(static_geom)
                if static_geom.startswith("gauges"):
                    self.set_gauge_action(layer)

                QgsProject.instance().addMapLayer(layer, False)
                group_geoms.addLayer(layer)
            
            # Apply styling to the static geometries if checkbox is clicked
            if parameters[self.APPLY_STYLING]:
                # get directory of the plugin gives -> ../src/qgis_wflow/
                current_dir = Path(__file__).parents[1].resolve()
                
                # get standard layers to style
                for layer in group_maps.findLayers():
                    if layer.name() in DEFAULT_STATIC_MAPS:
                        #special case for land use layer
                        if layer.name() == "wflow_landuse":
                            style_path = current_dir / f"resources/styles/{LULC_MAPS[parameters[self.LULC_MAPPING]]}_style.qml"
                        else:
                            # else the qmd file has the same name as the layer
                            style_path = current_dir / f"resources/styles/{layer.name()}_style.qml"
                        #apply the style to the layer only if the path to the qmd file exists
                        if style_path.exists():
                            layer.layer().loadNamedStyle(str(style_path))  
                            layer.layer().triggerRepaint()
                            
                # do the same for the geojson static geometries (@peter is the repetition of the code here acceptable or should I write a seperate function)
                for layer in group_geoms.findLayers():
                    if layer.name() in DEFAULT_STATIC_GEOMS:
                        style_path = current_dir / f"resources/styles/{layer.name()}_style.qml"
                    if style_path.exists():
                        layer.layer().loadNamedStyle(str(style_path))
                        layer.layer().triggerRepaint()
        return {}


