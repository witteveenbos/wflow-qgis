
import re
import subprocess
import typing

from . import AlgorithmBase
from ..functions.configuration import wflow_path

from qgis.core import (
    QgsProcessingContext,
    QgsProcessingFeedback,
    QgsProcessingParameterFile,
)


class RunWflowAlgorithm(AlgorithmBase):

    __NAME__ = "Run calculation"
    __GROUP__ = "Wflow"

    INPUT = "INPUT"

    PROGRESS_REGEX = re.compile(r"Progress:\s+(\d+)")

    def init_algorithm(self, config):

        # We add the input vector features source. It can have any kind of
        # geometry.
        self.addParameter(
            QgsProcessingParameterFile(
                name=self.INPUT,
                description=self.tr('Input .toml-file of wflow'),
                extension="toml"
            )
        )
    
    def process_algorithm(
            self,
            parameters: typing.Dict[str, typing.Any],
            context: QgsProcessingContext,
            feedback: typing.Optional[QgsProcessingFeedback]
        ) -> typing.Dict[str, typing.Any]:
        
        # Run the calculation in a subprocess
        process = subprocess.Popen(
            [wflow_path(), parameters[self.INPUT]],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            shell=True,
            encoding='utf-8',
            errors='replace'
        )
        while (realtime_output := process.stdout.readline()) != '' or process.poll() is None:
            if realtime_output:
                match = self.PROGRESS_REGEX.search(realtime_output)
                if match:
                    feedback.setProgress(int(match.group(1)))
                else:
                    feedback.pushInfo(realtime_output.strip())

        return {}
