from qgis.core import QgsSettings

WFLOW_PATH_SETTING = 'wflow/path'


def wflow_path() -> str | None:
    """Get the path to the WFlow executable (if set).

    Returns:
        str | None: The path of wflow. Will return None if the this property has not been set.
    """
    return QgsSettings().value(WFLOW_PATH_SETTING, defaultValue=None)


def set_wflow_path(path: str) -> None:
    """Sets the path to the WFlow executable

    Args:
        path (str): The path to qflow executable.
    """
    return QgsSettings().setValue(WFLOW_PATH_SETTING, path)


def hydromt_version() -> str | None:
    """Get the version of the hydromt_wflow package if installed.

    Returns:
        str | None: The version of the hydromt_wflow package. Will return None if the package is not installed
        or cannot be imported.
    """
    try:
        from hydromt_wflow import __version__
        return __version__
    except ImportError:
        return None
