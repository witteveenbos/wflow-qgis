import os
import shutil
import stat
from pathlib import Path


def delete_folder(folder: Path, feedback=None):
    """Delete a folder and all its contents. Forces deletion of read-only files
    when a PermissionError is encountered.

    Args:
        folder (Path): The folder to delete.
    """
    if folder.exists():
        if not folder.is_dir():
            raise ValueError(f"{folder} is not a directory")
        try:
            shutil.rmtree(folder)
        except PermissionError:
            for root, dirs, files in os.walk(folder, topdown=False):
                for name in files:
                    if feedback is not None:
                        feedback.pushInfo(
                            f"Changing permissions and deleting {os.path.join(root, name)}"
                        )
                    filename = os.path.join(root, name)
                    os.chmod(filename, stat.S_IWUSR)
                    os.remove(filename)
                for name in dirs:
                    if feedback is not None:
                        feedback.pushInfo(
                            f"Changing permissions and deleting {os.path.join(root, name)}"
                        )
                    os.chmod(os.path.join(root, name), stat.S_IWUSR)
                    os.rmdir(os.path.join(root, name))
            os.chmod(folder, stat.S_IWUSR)
            os.rmdir(folder)

def path_from_feature_layer(qgis_layer_source: str) -> str:
    """Return the path of the vector file from a URI. Removes the noice like layer names from the string

    Args:
        qgis_layer_source (str): path returned by <QgsMapLayer>.source()

    Returns:
        str: truncated string
    """
    if ".gpkg" in qgis_layer_source:
        return qgis_layer_source.split("|")[0], qgis_layer_source.split("=")[-1]  # e.g. path/to/file.gpkg|layername=test
    else:
        return qgis_layer_source, None