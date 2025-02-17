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


def install_hydromt_wflow():
    """Installs or updates the hydromt_wflow package."""
    import os
    import subprocess
    import sys
    # Modify the path, so we can access the Python executable
    env = os.environ.copy()
    env["PATH"] = ";".join(sys.path)
    # Install the package using pip
    res = subprocess.run(["python", "-m", "pip", "install", "hydromt_wflow", "pywinpty"], env=env, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    if res.returncode != 0:
        print(res.stdout)
        print(res.stderr)
        raise RuntimeError("Failed to install hydromt_wflow")


    
    