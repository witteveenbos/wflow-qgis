import configparser
import os
import re

from PyQt5.QtCore import QCoreApplication
from qgis.core import (
    QgsProcessingAlgorithm,
    QgsProcessingProvider
)


class AlgorithmBase(QgsProcessingAlgorithm):
    """
    Base-class for an Algorithm. Implements the most basic functions, so
    a developer can focus on defining the parameters and the script.
    """
    __ABSTRACT__ = False

    # `QgsProcessingAlgorithm` does not use snake_case, as it is partly written
    # in C. We must use the names as defined in QGis in order to interface
    # with the classes defined there. We do encourage developers to use
    # snake_case, so the warnings of PyLint are silenced on a per instance
    # basis.
    def init_algorithm(self, config):
        """
        In this function all input and output (sink) parameters should
        be defined. This function MUST be implemented in a sub-class,
        directly calling this function will raise a NotImplementedError.

        A full list of all parameters types can be found at:
            https://qgis.org/pyqgis/3.0/core/Processing/index.html
        """
        raise NotImplementedError(
            "The function `init_algorithm` must be implemented in a sub-class."
        )

    def initAlgorithm(self, config): #pylint: disable=invalid-name
        """
        Function required by the implementation of QgsProcessingAlgorithm. The name
        does not conform to snake_case. We pass the function on to the function
        `init_algorithm`, which uses snake_case.
        """
        return self.init_algorithm(config)

    def process_algorithm(self, parameters, context, feedback):
        """
        In this function the algorithm or script should be defined. This
        function MUST be implemented in a sub-class, directly calling
        this function will raise a NotImplementedError.
        """
        raise NotImplementedError(
            "The function `process_algorithm` must be implemented in a sub-class."
        )

    def processAlgorithm(self, parameters, context, feedback): #pylint: disable=invalid-name
        """
        In this function the algorithm or script should be defined. This
        function MUST be implemented in a sub-class, directly calling
        this function will raise a NotImplementedError.
        """
        return self.process_algorithm(parameters, context, feedback)

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return re.sub(r'\W+', '', self.__NAME__).lower()

    def displayName(self): #pylint: disable=invalid-name
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr(self.__NAME__)

    def group(self):
        """
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
        """
        return self.tr(self.__GROUP__)

    def groupId(self): #pylint: disable=invalid-name
        """
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return re.sub(r'\W+', '', self.__GROUP__).lower()

    def tr(self, string): #pylint: disable=invalid-name
        '''
        Translates the given string to the current locale setting. Will return
        the original string when there are no translations available.
        '''
        return QCoreApplication.translate('Processing', string)

    def createInstance(self): #pylint: disable=invalid-name
        '''
        Creates a new instance of this class. Mandatory method for QGis.
        '''
        return self.__class__()


class AutoProcessingProvider(QgsProcessingProvider):
    """
    Algorithm provider for this plugin. This provider will import any algortihm inside this
    module, provided that the algortihm is a sub-class of the QgsProcessingAlgorithm. Also,
    the provider will set the name of the processing pluging as displayed in the QGis Processing
    Toolbox. This name is derived from `metadata.txt`, thus normally this class does not
    require any modification.
    """

    def __init__(self):
        QgsProcessingProvider.__init__(self)

        # Create a list for the algorithms
        self.alglist = []

        # Import all classes
        modules = [
            f[:-3]
            for f 
            in os.listdir(os.path.dirname(os.path.abspath(__file__))) 
            if f.endswith('.py') and not f.startswith('__')]
        for module in modules:
            # Import the module
            mod = __import__(
                f"{__name__}.{module}",
                fromlist=[module]
            )
            # Get all sub-classes of AlgorithmBase, but not AlgorithmBase
            # itself. The import will import all classes, also when they are imported in the
            # module. What we really need are the algorithms defined in the file which are not
            # abstract.
            classes = [
                getattr(mod, x)
                for x
                in dir(mod)
                if isinstance(getattr(mod, x), type)
                and issubclass(getattr(mod, x), AlgorithmBase)
                and not getattr(mod, x) is AlgorithmBase
                and not getattr(mod, x).__ABSTRACT__
            ]
            for cls in classes:
                # Add the class to the file (NOTE: a user might define multiple classes within a
                # single file!)
                self.alglist.append(cls())

    def unload(self):
        """
        Unloads the provider. Any tear-down steps required by the provider
        should be implemented here.
        """
        return None

    def loadAlgorithms(self): #pylint: disable=invalid-name
        """
        Loads all algorithms belonging to this provider.
        """
        for alg in self.alglist:
            self.addAlgorithm(alg)

    def id(self):
        """
        Returns the unique provider id, used for identifying the provider. This
        string should be a unique, short, character only string, eg "qgis" or
        "gdal". This string should not be localised.

        As default it will return the folder-name where this plugin is installed.
        The folder name is equal to the name of the package when looked at it from
        the Python point of view.
        """
        return __name__.split('.', maxsplit=1)[0]

    def name(self):
        """
        Returns the provider name, which is used to describe the provider
        within the GUI.

        This string should be short (e.g. "Lastools") and localised.
        """
        path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        parser = configparser.ConfigParser()
        parser.read(os.path.join(path, 'metadata.txt'))
        return parser['general']['name']

    def longName(self): #pylint: disable=invalid-name
        """
        Returns the a longer version of the provider name, which can include
        extra details such as version numbers. E.g. "Lastools LIDAR tools
        (version 2.2.1)". This string should be localised. The default
        implementation returns the same string as name().
        """
        return self.name()
