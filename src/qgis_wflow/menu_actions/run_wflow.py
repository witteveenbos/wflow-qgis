
from __future__ import annotations

import os
import sys

from qgis.PyQt import uic
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtCore import QProcess, QProcessEnvironment, Qt
from qgis.PyQt.QtWidgets import QDialog, QWidget, QFileDialog, QMessageBox


RUN_WFLOW_FORM_CLASS = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), 'ui', 'run_wflow.ui'))[0]


class RunWFlowProgress(QDialog, RUN_WFLOW_FORM_CLASS):
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
        self._process.start("python", ["-c", "import time, sys;print('hello');sys.stdout.flush();time.sleep(5);print('world')"])
        # - Update label
        self.lblCalculationStatus.setText("Calculating ...")
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
            self.lblCalculationStatus.setText("Calculation finished.")
        else:
            if self._process_cancelled:
                self.lblCalculationStatus.setText("Calculation cancelled by user.")
            else:
                self.lblCalculationStatus.setText("Calculation failed.")
        # - Update buttons
        self.buttonBox.button(self.buttonBox.Ok).setEnabled(True)
        self.buttonBox.button(self.buttonBox.Cancel).setEnabled(False)

    def reject(self):
        self._process_cancelled = True
        self._process.kill()

