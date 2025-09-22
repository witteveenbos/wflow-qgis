"""
conftest.py for dgeosuite_tools. Required for initializing QGis and loading
its plugins (including the plugin which is being tested).

If you don't know what this is for, just leave it unmodified. Read more
about conftest.py under:
    - https://docs.pytest.org/en/stable/fixture.html
    - https://docs.pytest.org/en/stable/writing_plugins.html
"""

import platform
import sys
from pathlib import Path

from qgis.core import QgsApplication
from qgis.utils import loadPlugin, startPlugin

from pytest import fixture


@fixture()
def plugin_name():
    """
    Returns the name of the plugin to be tested. This is used in the
    test files to load the plugin and run tests on it.
    """
    return "qgis_wflow"


@fixture()
def qgis_app(plugin_name):
    """
    Allows plugins and conftest files to perform initial configuration.
    This hook is called for every plugin and initial conftest
    file after command line options have been parsed.
    """
    # Initialize the QgsApplication
    app = QgsApplication([], False)
    app.initQgis()

    # Initialize the processing toolbox and load all standard plugins
    if platform.system() == "Linux":
        sys.path.append('/usr/share/qgis/python/plugins')
    from processing.core.Processing import Processing
    proc = Processing()
    proc.initialize()

    # Load the plugin to be tested from the source directory
    sys.path.append(str(Path(__file__).parent.parent / "src"))
    
    # Load the plugin to be tested
    assert loadPlugin(plugin_name)
    # assert startPlugin(plugin_name)

    return app
