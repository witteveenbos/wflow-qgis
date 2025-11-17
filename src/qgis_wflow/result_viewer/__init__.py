import os
import toml
from pathlib import Path

import pandas as pd
import plotly.graph_objs as go
import plotly.offline as po
import plotly.express as px
from qgis.core import QgsProject, QgsWkbTypes
from qgis.PyQt.QtGui import QIcon, QStandardItem, QStandardItemModel
from qgis.PyQt.QtWidgets import QAbstractItemView, QWidget
import xarray as xr

# RESULTVIEWER_FORM_CLASS = uic.loadUiType(
#     os.path.join(os.path.dirname(__file__), "ui", "result_viewer.ui")
# )[0]

from .ui.result_viewer_ui import ResultViewerUI


class ResultViewer(QWidget, ResultViewerUI):
    """Dialog to show the results of a wflow simulation."""

    def __init__(self):
        """Pseudoconstructor."""
        super().__init__(None)
        self.setupUi(self)
        self.setWindowIcon(QIcon(str(Path(__file__).parent.parent / "resources" / "wflow_logo.png")))
        self.gauges_list_model = QStandardItemModel()
        self.listGauges.setModel(self.gauges_list_model)
        self.listGauges.setSelectionMode(QAbstractItemView.ExtendedSelection)
        # - connect signals / slots
        self.comboLayers.checkedItemsChanged.connect(self.on_comboLayers_checkedItemsChanged)
        self.comboLayersCompareWith.checkedItemsChanged.connect(self.refresh_plot)
        self.listGauges.selectionModel().selectionChanged.connect(self.refresh_plot)
        # Enable or disable comboLayersCompareWith based on checkCompareWith state
        self.comboLayersCompareWith.setEnabled(self.checkCompareWith.isChecked())
        self.checkCompareWith.stateChanged.connect(
            lambda _: self.comboLayersCompareWith.setEnabled(self.checkCompareWith.isChecked())
        )
        # Placeholders for data
        self.data = None
        self.compare_data = None
        # - show the form
        self.show()

    def showEvent(self, event):
        super().showEvent(event)
        self.update_combobox()

    def update_combobox(self):
        """
        Adds all the layers which are a point layer to the combobox
        """
        self.comboLayers.clear()
        self.comboLayersCompareWith.clear()
        for layer in QgsProject.instance().mapLayers().values():
            if (layer.type() == layer.VectorLayer and 
                    QgsWkbTypes.geometryType(layer.wkbType()) == QgsWkbTypes.PointGeometry
                ):
                self.comboLayers.addItem(layer.name(), layer)
                self.comboLayersCompareWith.addItem(layer.name(), layer)

    def get_data(self, layer_path):
        # Find the toml file in the folder
        toml_files = list(layer_path.parent.parent.glob("*.toml"))
        if toml_files:
            toml_file = toml_files[0]
        else:
            return None
        # Read TOML-file
        with open(toml_file, 'r') as f:
            config = toml.load(f)
        if 'netcdf' in config:
            output_data = layer_path.parent.parent / f'./{config['dir_output']}/{config['netcdf']['path']}'
            df = xr.open_dataset(output_data).to_dataframe()
            # Convert to wide format by unstacking if needed
            if df.index.nlevels > 1:
                df = df.unstack(fill_value=0)
                # Flatten column names if they are multi-level
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = ['_'.join(map(str, col)).strip() for col in df.columns.values]
            # TODO: check what the column 'layer' means. At this moment we get the first layer only
            return df.groupby('time').first().reset_index()
        elif 'csv' in config:
            output_data = layer_path.parent.parent / f'./{config['dir_output']}/{config['csv']['path']}'
            return pd.read_csv(output_data)
        else:
            return None

    def on_comboLayers_checkedItemsChanged(self, _):
        self.data = None
        # Clear the list view
        self.gauges_list_model.clear()
        # Load the selected layers
        for index in range(self.comboLayers.count()):
            if not self.comboLayers.itemCheckState(index):
                continue
            layer = self.comboLayers.itemData(index)
            layer_has_name_field = "name" in [field.name() for field in layer.fields()]
            if layer:
                # fields = layer.fields()
                # Fill the list view with the features of the layer
                for feature in layer.getFeatures():
                    item = QStandardItem()
                    if layer_has_name_field:
                        name =f"{layer.name()} - {feature['name']}"
                    else:
                        name = f"{layer.name()} - Gauge {feature.id()}"
                    item.setText(name)  
                    item.setData((name, feature))
                    self.gauges_list_model.appendRow(item)
            # Load the data
            layer_path = Path(layer.dataProvider().dataSourceUri())
            self.data = self.get_data(layer_path)

    def on_comboLayersCompareWith_currentIndexChanged(self, _):
        self.compare_data = None
        # Get the selected layer
        if self.comboLayersCompareWith.currentIndex() < 0:
            return  
        # Get the selected layer,
        layer = self.comboLayersCompareWith.itemData(self.comboLayersCompareWith.currentIndex())
        # Load the data
        if layer:
            # Load the data
            layer_path = Path(layer.dataProvider().dataSourceUri())
            self.compare_data = self.get_data(layer_path)

    def refresh_plot(self, *_):
        """Refreshes the plot
        """
        # Get data        
        # - selected features
        selected_features = [self.gauges_list_model.itemFromIndex(idx).data() for idx in self.listGauges.selectedIndexes()]

        layout = go.Layout(
            title= 'Gauges',
            xaxis= dict(title= 'Time'),
            yaxis=dict(title= 'Discharge (m3/s)'),
            showlegend= True
        )

        # Safe-guard when people don't select anything
        if self.data is None or len(selected_features) == 0:
            self.chartView.setHtml("<html><body><h3>No data to display</h3></body></html>")
            return
        
        # Retrieve a list of features to compare against if needed
        compare_features = []
        if self.checkCompareWith.isChecked() and self.compare_data is not None:
            for index in range(self.comboLayersCompareWith.count()):
                if not self.comboLayersCompareWith.itemCheckState(index):
                    continue
                compare_layer = self.comboLayersCompareWith.itemData(index)
                compare_features.extend(compare_layer.getFeatures())

        plot_data = []
        colors = px.colors.qualitative.Plotly
        for index, (name, gauge) in enumerate(selected_features):
            color = colors[index % len(colors)]
            # Plot the main data
            trace = go.Scatter(
                x=self.data['time'],
                y=self.data[f'Q_{gauge["fid"]}'],
                mode='lines',
                name=name,
                line=dict(color=color),
                legendgroup="Base"
            )
            plot_data.append(trace)
            if self.checkCompareWith.isChecked() and self.compare_data is not None:
                # Find matching features in compare layer within 100m buffer
                matching_gauge = None
                current_geom = gauge.geometry()
                for compare_feature in compare_features:
                    if current_geom.distance(compare_feature.geometry()) <= 1/1130:  # approx. 100m in degrees
                        matching_gauge = compare_feature
                        break
                if matching_gauge is None:
                    continue
                # Plot the comparison data if needed
                trace_compare = go.Scatter(
                    x=self.compare_data['time'],
                    y=self.compare_data[f'Q_{matching_gauge["fid"]}'],
                    mode='lines',
                    name=f'{name} (compare)',
                    line=dict(
                        dash='dash',
                        color=color
                    ),
                    legendgroup="Compare"
                )
                plot_data.append(trace_compare)

        fig= go.Figure(data=plot_data, layout=layout)

        # Convert the figure to HTML
        raw_html = f'''
        <html>
        <head>
            <meta charset="utf-8" />
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        </head>
        <body>
            {po.plot(fig, include_plotlyjs=False, output_type='div')}
        </body>
        </html>
        '''
        # Show the plot in a webview
        self.chartView.setHtml(raw_html)


    def on_gauges_selection_changed(self, *_):
        # Compare with another layer if needed
        self.refresh_plot()
