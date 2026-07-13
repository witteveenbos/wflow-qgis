=========================================
Functionalities for schematization of NbS
=========================================


Add reservoirs
==============

The add reservoirs functionality adds reservoirs to a wflow model. 
The add reservoirs functionality can be found in the wflow NBS design tool in the Processing Toolbox under 'Add NBS'. 
The reservoirs to be added to a wflow model need to be prepared as a vector layer in QGIS.
This vector layer should contain the polygons of the reservoirs and the following fields: 

- Lake_name (opt.) : name of the reservoir

- Country (opt.) : country of the reservoir

- Continent (opt.) : continent of the reservoir

- Depth_avg (opt.) : average depth of the reservoir in meters

- waterbody_id (req.) : unique id of the reservoir

- ResSimpleArea (req.) : area of the reservoir in square meters
 
- ResMaxVolume (req.) : maximum volume of the reservoir in cubic meters

- ResTargetMinFrac (req.) : minimum fraction of the maximum volume of the reservoir [0-1]

- ResDemand (req.) : water demand of the reservoir in cubic meters per second

- ResMaxRelease (req.) : maximum release of the reservoir in cubic meters per second

- ResTargetFullFrac (req.) : maximum fraction of the maximum volume of the reservoir [0-1]


A template vector layer containing all these fields can be generated using the 'Create reservoir' function. 
This functionality can be found in the wflow toolbar, see the figure below: 

.. figure:: ./_static/wflow_toolbar_add_reservoir.png
  :width: 200px
  :alt: some alt text

``Create reservoir`` functionality in the wflow NBS design tool toolbar 

To run the add reservoirs functionality, provide the path to the .toml-file of the wflow model you want to add the reservoirs to, 
provide the vector layer with the reservoirs and a target folder for the model with the new reservoirs. 
Press ``Run`` to execute the functionality. See the figure below:

.. figure:: ./_static/add_reservoirs_panel.png
  :width: 200px
  :alt: some alt text

``Add reservoir`` panel in the wflow NBS design tool 

The plugin makes use of the python package HydroMT-wflow to add the reservoirs to the wflow model. 
The plugin will also return the logging of HydroMT-wflow in the Processing Log panel. See the figure below:

.. figure:: ./_static/add_reservoirs_result.png
  :width: 200px
  :alt: some alt text

Result of the ``Add reservoir`` functionality in the wflow NBS design tool 


Change landuse
==============

The change landuse functionality changes the landuse of a wflow model. 
The change landuse functionality can be found in the wflow NBS design tool in the Processing Toolbox under 'Add NBS'.
The area in which the landuse needs to be changed should be prepared as a vector layer in QGIS. 
This vector layer should contain one ore more polygon of the area in which the landuse needs to be changed, 
together with the new landuse class for that area. 
This landuse class should be provided as the landuse value in the orignal landuse map, in a separate field in the vector layer.
A template vector layer containing these fields can be generated using the 'Create landuse' function.
This functionality can be found in the wflow toolbar, see the figure below:

.. figure:: ./_static/wflow_toolbar_change_landuse.png
  :width: 200px
  :alt: some alt text

``Create landuse`` functionality in the wflow NBS design tool toolbar

When this functionality is used, you also need to provide the landuse mapping that is used in the wflow model. 
This enables the plugin to let you choose directly from the landuse classes, instead of from their landuse values. 

To run the change landuse functionality, provide the path to the .toml-file of the wflow model you want to change the landuse of,
provide the landuse mapping that was used in the wflow model, 
provide the orignal landuse map from which the wflow model was derived, 
provide the vector layer with the polygon(s) in which the landuse needs to be changed, 
provide the field in this vector layer that contains the new landuse class for the area,
and a target folder for the model with the new landuse. 
Press ``Run`` to execute the functionality. See the figure below:

.. figure:: ./_static/change_landuse_panel.png
  :width: 200px
  :alt: some alt text

``Change landuse`` panel in the wflow NBS design tool
 
The plugin makes use of the python package HydroMT-wflow to update the landuse of the wflow model. 
The plugin will also return the logging of HydroMT-wflow in the Processing Log panel. See the figure below:

.. figure:: ./_static/change_landuse_result.png
  :width: 200px
  :alt: some alt text

Result of the ``Change landuse`` functionality in the wflow NBS design tool 


Add check dams
==============

TODO

Add terracing
=============

TODO