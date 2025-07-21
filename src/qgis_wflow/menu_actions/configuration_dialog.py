
from __future__ import annotations

import os
import sys

from qgis.PyQt import uic
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtCore import QProcess, QProcessEnvironment, Qt
from qgis.PyQt.QtWidgets import QDialog, QWidget, QFileDialog, QMessageBox

from qgis_wflow.functions.configuration import hydromt_version, wflow_path, set_wflow_path, install_hydromt_wflow


CONFIGURAION_FORM_CLASS = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), 'ui', 'configuration.ui'))[0]
INSTALLATION_PROGRESS_FORM_CLASS = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), 'ui', 'hydromt_wflow_installation_progress.ui'))[0]


class HydroMTInstallationProgress(QDialog, INSTALLATION_PROGRESS_FORM_CLASS):
    """Dialog to show the progress of the installation of the hydromt_wflow package."""

    def __init__(self, parent: QWidget):
        """Pseudoconstructor."""
        super().__init__(parent)
        self.setupUi(self)
        # - create a process to install the hydromt_wflow package
        self._process = QProcess(parent=self)
        self._process.readyReadStandardOutput.connect(self.handle_stdout)
        self._process.readyReadStandardError.connect(self.handle_stderr)
        self._process.finished.connect(self.installation_finished)
        self._process_cancelled = False
        self.start()
        # - show the form
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowCloseButtonHint)
        self.show()

    def start(self):
        """Start the installation of the hydromt_wflow package."""
        env = QProcessEnvironment.systemEnvironment()
        env.insert("PATH", ";".join(sys.path))
        self._process.setProcessEnvironment(env)
        self._process.start("python", ["-m", "pip", "install", "-U", "hydromt_wflow<1.0"])
        # - Update label
        self.lblInstallationStatus.setText("Installing hydromt_wflow package...")
        # - Update buttons
        self.buttonBox.button(self.buttonBox.Ok).setEnabled(False)
        self.buttonBox.button(self.buttonBox.Cancel).setEnabled(True)

    def append_log(self, message: str):
        """Appends a message to the log."""
        self.textBrowser.appendPlainText(message.rstrip())

    def handle_stdout(self):
        """Handle the standard output of the process."""
        message = self._process.readAllStandardOutput().data().decode()
        self.append_log(message)

    def handle_stderr(self):
        """Handle the standard error of the process."""
        message = self._process.readAllStandardError().data().decode()
        self.append_log(message)

    def installation_finished(self, exit_code: int):
        """Handle the finishing of the installation."""
        # - Update label
        if exit_code == 0:
            self.lblInstallationStatus.setText("Installation finished.")
        else:
            if self._process_cancelled:
                self.lblInstallationStatus.setText("Installation cancelled by user.")
            else:
                self.lblInstallationStatus.setText("Installation failed.")
        # - Update buttons
        self.buttonBox.button(self.buttonBox.Ok).setEnabled(True)
        self.buttonBox.button(self.buttonBox.Cancel).setEnabled(False)

    def reject(self):
        self._process_cancelled = True
        self._process.kill()


class ConfigurationDialog(QDialog, CONFIGURAION_FORM_CLASS):
    """Plugin Reloader Configuration Window."""

    def __init__(self, parent: QWidget):
        """Pseudoconstructor."""
        super().__init__(parent)
        self.setupUi(self)
        # - connect signals
        self.btnBrowseWFlow.clicked.connect(self.select_wflow_location)
        self.btnInstallUpdateWflow.clicked.connect(self.install_hydromt)
        self.accepted.connect(self.save_settings)
        # - show the stored path to wflow
        if wflow_path() is not None:
            self.editWflowExecutable.setText(wflow_path())
        # - show the installed version of hydromt_wflow
        self.update_version_label()

    def update_version_label(self):
        version = hydromt_version()
        if version is None:
            self.lblHydroMTVersion.setText("HydroMT-wflow is not installed.")
            self.btnInstallUpdateWflow.setText("Install")
        else:
            self.lblHydroMTVersion.setText(f"HydroMT-wflow version: {version}")
            self.btnInstallUpdateWflow.setText("Update")
            
    def select_wflow_location(self):
        fname = QFileDialog.getOpenFileName(
            self,
            'Select WFlow executable', 
            'c:\\',
            "Executable (*.exe)"
        )
        if fname[0]:
            self.editWflowExecutable.setText(fname[0])

    def install_hydromt(self):
        dlg = HydroMTInstallationProgress(self)
        dlg.exec()
        self.update_version_label()

    def save_settings(self):
        set_wflow_path(self.editWflowExecutable.text())
        # Show message box with recommendation to restart QGIS after changing properties
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setText("It is strongly recommended to restart QGis after changing the qgis-wflow configuration.")
        msg.setWindowTitle("Restart QGis")
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()
