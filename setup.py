""""
Deployment tool for QGis Processing tools.

This tool copies the folder where it is contained in to the QGis plugin folder.

Copyright 2018 Witteveen+Bos N.V., all rights reserved

FOR INTERNAL USE ONLY!
"""
import os
import shutil

PLUGIN_NAME = 'qgis_wflow'

# A list with files to be ignored 
list_ignore = ['deploy.py', ]

# Create the plugin folder
plugins_path = os.path.expanduser("~/AppData/Roaming/QGIS/QGIS3/profiles/default/python/plugins")

# Get the plugin name (the name of this folder) and create a folder in the 
# plugin directory when it does not exist
# - get reference to the folder the deploy resides in
root = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'src', PLUGIN_NAME)
# - get the name of the plugin folder of QGis and create it when not exists
plugin_path = os.path.join(plugins_path, PLUGIN_NAME) 
if os.path.exists(plugin_path):
    try:
        shutil.rmtree(plugin_path)
    except PermissionError:
        print('QGis is running! Don\'t forget to reload the plugin!')
if not os.path.exists(plugin_path):       
    os.makedirs(plugin_path)

# Copy all the files from this folder to the plugin folder of QGis
for roots, dirs, files in os.walk(root):
    for file in files:
        if not file in list_ignore:
            # Create the folder (when required)
            os.makedirs(os.path.dirname(
                            os.path.join(plugin_path, 
                                         os.path.join(roots, file)[len(root)+1:])), 
                            exist_ok=True)
            # Copy the file
            shutil.copy2(os.path.join(roots, file),
                         os.path.join(plugin_path, 
                                      os.path.join(roots, file)[len(root)+1:]))

# Copy metadata
shutil.copy2(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), 'metadata.txt'),
    os.path.join(plugin_path, 'metadata.txt')
)
