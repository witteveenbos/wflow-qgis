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
)
from qgis.utils import iface


STATIC_MAPS = [
    "wflow_ldd",
    "wflow_subcatch",
    "wflow_uparea",
    "wflow_streamorder",
    "wflow_dem",
    "Slope",
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
    "LAI",
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
]
DEFAULT_STATIC_MAPS = [
    "wflow_subcatch",
    "wflow_dem",
    "Slope",
    "wflow_landuse",
    "LAI",
    "wflow_soil",
]


STATIC_GEOMS = ["basins", "basins_highres", "gauges", "region", "rivers", "subcatch"]
DEFAULT_STATIC_GEOMS = ["basins", "gauges", "rivers", "subcatch"]


class LoadLayersAlgorithm(AlgorithmBase):

    __NAME__ = "Load layers"
    __GROUP__ = "Wflow"

    INPUT = "INPUT"
    STATIC_MAPS = "STATIC_MAPS"
    STATIC_GEOMS = "STATIC_GEOMS"

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
                    "# Show the discharge\n"
                    "fig = px.line(df_output, x='time', y=f'Q_[%fid%]', title='Discharge')\n"
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
            group = insertion_point.addGroup("Static maps")
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
                layer.setName(STATIC_MAPS[map_id])
                QgsProject.instance().addMapLayer(layer, False)
                group.addLayer(layer)

        # Import static geoms
        path_static_geoms = Path(parameters[self.INPUT]).parent / "staticgeoms"
        if parameters[self.STATIC_GEOMS]:
            feedback.pushInfo(f"Importing static geoms from {path_static_geoms}")
            # - create a group in the layer tree for the static geometries
            insertion_point = iface.layerTreeInsertionPoint().group
            group = insertion_point.addGroup("Static geometries")
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
                group.addLayer(layer)

        return {}


