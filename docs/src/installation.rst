============
Installation
============

.. note::
    This installation guide assumes you have a working installation of QGIS on your machine. If you don't have QGIS installed, please visit
    the `QGIS website <https://qgis.org/en/site/forusers/download.html>`_ to download and install the latest version of QGIS.

.. note::
    Python is in the heart of QGIS (or in the guts if you prefer), which enables us to use tons of third party Python libraries. In Linux systems,
    QGIS will use the main Python installation, but in Windows things get more complicated. QGIS has it’s own Python, which means we end up with 
    various Pythons on our machine.

    In order to use HydroMT-Wflow from within QGIS, we need to install the HydroMT plugin within the correct Python environment. This guide will
    help you to install the HydroMT plugin in the correct Python environment. This manual is written for Windows users, and will be updated later
    for Linux and MacOS users.

Obtaining the HydroMT plugin (development version)
--------------------------------------------------

The QGis-Wflow plugin is under active development and is not yet available in the QGIS plugin repository. To install the plugin, you can clone
the repository from GitHub and install it manually. To do this, follow the steps below:

- Clone the repository from GitHub by running the following command in your terminal:
  ``git clone ...``
- Navigate to the cloned repository and install the plugin by running the following command in your terminal:
  ``python setup.py install``
- Restart QGis after the installation is complete.

This will install the QGis-Wflow plugin in the correct folder (``%USERPROFILE%\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\QGis-Wflow``)
on your system.

.. info::
    You can also install the plugin ``Plugin Reloader`` from the `QGIS plugin repository <https://plugins.qgis.org/plugins/plugin_reloade>`_. This plugin
    allows you to reload the QGis-Wflow plugin. This is useful when you are developing the plugin and want to see the changes you made. See
    `Experimental Plugins  <https://www.qgistutorials.com/en/docs/using_plugins.html#experimental-plugins>`_ for more details on how to install
    this plugin.


Configuration
-------------

After installing the plugin, you need to configure the plugin to set the correct path to your ``wflow`` installation and to install or update
`hydromt-wflow` and its dependencies. To do this, follow the steps below:

- Open QGIS and navigate to the ``Plugins`` menu.
- Click on the ``Wflow`` sub-menu.
- Select the ``Configuration`` option.

In the configuration window, you can set the path to your ``wflow`` installation and install or update the ``hydromt-wflow`` package and its
dependencies by using the button. When ``hydromt-wflow`` is installed, its version will be displayed in the configuration window.

.. note::
    When ``hydromt-wflow`` is installed or updated, it is required to restart QGIS to make the changes effective. After the installation a 
    message will be displayed in the configuration window to remind you to restart QGIS.
