
from time import sleep
import subprocess
from qgis.PyQt.QtCore import QProcess

from . import AlgorithmBase
from ..functions.configuration import wflow_path

from qgis.core import (QgsProcessing,
                       QgsFeatureSink,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFeatureSink)


class RunWflowAlgorithm(AlgorithmBase):

    __NAME__ = "run_wflow"
    __GROUP__ = "WFlow"

    INPUT = "INPUT"

    def init_algorithm(self, config):
        pass

        # We add the input vector features source. It can have any kind of
        # geometry.
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT,
                self.tr('Input layer'),
                [QgsProcessing.TypeVectorAnyGeometry],
                optional=True
            )
        )
    
    def process_algorithm(self, parameters, context, feedback):
        
        from winpty import PtyProcess
        import re
        import unicodedata
        import threading
        from queue import Queue

        def remove_control_characters(s):
            return "".join(ch for ch in s if unicodedata.category(ch)[0]!="C")
        
        PROGRESS_REGEX = re.compile(r"Progress:\s+(\d+)")
        
        proc = PtyProcess.spawn([
            wflow_path(),
            r"C:\Users\tolp2\Documents\git\wflow-qgis\data\wflow_Ilek\wflow_sbm.toml"
        ])
        while proc.isalive():
            # Listen whether user wants to cancel the process
            if feedback.isCanceled():
                proc.terminate()
                feedback.reportError("Process was cancelled.")
                break
            # Give feedback to the user
            q = Queue()
            t = threading.Thread(target=lambda q: q.put(proc.readline()), args=(q, ))
            t.start()
            t.join(timeout=1)

            line = remove_control_characters(q.get())
            match = PROGRESS_REGEX.search(line)
            if match:
                feedback.setProgress(int(match.group(1)))
            else:
                feedback.pushInfo(line)

        return {}
