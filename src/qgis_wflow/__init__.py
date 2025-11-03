import os
from pathlib import Path

from qgis.PyQt.QtCore import QCoreApplication, QLocale, QSettings, QTranslator
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction

from qgis.core import QgsApplication
from qgis.gui import QgisInterface

from .processing import AutoProcessingProvider

class WFlowAction(object):

    def __init__(
            self,
            iface,
            name,
            icon,
            dialog,
            menu=None,
            toolbar=None):
        self.iface = iface
        self.name = name
        self.icon = icon
        self.dialog = dialog
        self.menu = menu
        self.toolbar = toolbar

    def add_action(self):
        """
        Add action to toolbar/menu
        :rtype: QAction
        """
        icon = QIcon(os.path.join(os.path.dirname(__file__), 'resources', self.icon))
        action = QAction(icon, self.name)
        action.triggered.connect(self.dialog)
        
        if self.toolbar is not None:
            # Adds plugin icon to Plugins toolbar
            self.toolbar.addAction(action)
        if self.menu is not None:
            self.iface.addPluginToMenu(self.menu, action)
        return action
    
class Plugin():
    '''
    Minimal implementation of a Plugin for QGis. Responsible for adding and removing
    the provider to the QGis Processing Toolbox.
    '''

    def __init__(self, iface: QgisInterface):
        # Initialize the plugin, make sure the stderr is redirected to logging
        # because hydromt_plugin has faulthandler enabled
        from qgis_wflow.functions.faulthandler import stderr_to_logging
        stderr_to_logging()
        # Processing
        self.provider = AutoProcessingProvider()
        # Dialogs / UI-based
        self.iface = iface
        self.actions = []
        self.results_viewer = None

        self.menu = None
        if QSettings().value('locale/overrideFlag', type=bool):
            locale = QSettings().value('locale/userLocale')
        else:
            locale = QLocale.system().name()

        locale_path = os.path.join(
            os.path.dirname(__file__),
            'i18n',
            f'qgis_wflow_{locale[:2]}.qm')

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)


    def initGui(self): #pylint: disable=invalid-name
        '''
        Adds the plugin to the QGis Processing Toolbox.
        '''
        # Processing
        QgsApplication.processingRegistry().addProvider(self.provider)
        
        # Dialogs / UI-based
        icon = QIcon(str(Path(__file__).parent / "resources" / "wflow_logo.png"))
        self.menu = self.iface.pluginMenu().addMenu(icon, self.tr("&wflow"))
        self.toolbar = self.iface.addToolBar("wflow")
        # - config
        icon_gears = QIcon(str(Path(__file__).parent / "resources" / "settings-gears.png"))
        self.action_configure_plugin = QAction(icon_gears, self.tr("Configuration"))
        self.action_configure_plugin.triggered.connect(self.openConfigWindow)
        self.menu.addAction(self.action_configure_plugin)
        self.menu.addSeparator()

        self.action_run_wflow = QAction(icon_gears, self.tr("Run wflow"))
        self.action_run_wflow.triggered.connect(self.runWFlowDialog)
        self.menu.addAction(self.action_run_wflow)

        # Diaglogs -> toolbar
        self.actions.append(WFlowAction(
                self.iface,
                self.tr("Create Reservoir"),
                r"reservoir-icon.png",
                self.runCreateReservoirDialog,
                toolbar=self.toolbar,
            ).add_action())
        self.actions.append(WFlowAction(
                self.iface,
                self.tr("Create Terracing"),
                r"terracing-icon.png",
                self.runAddTerracingDialog,
                toolbar=self.toolbar,
            ).add_action())
        self.actions.append(WFlowAction(
                self.iface,
                self.tr("Create Check Dams"),
                r"dams-icon.png",
                self.runAddCheckDamsDialog,
                toolbar=self.toolbar,
            ).add_action())
        self.actions.append(WFlowAction(
                self.iface,
                self.tr("Change landuse"),
                r"landuse-icon.png",
                self.runChangeLanduseDialog,
                toolbar=self.toolbar,
            ).add_action())
        self.toolbar.addSeparator()
        self.actions.append(WFlowAction(
                self.iface,
                self.tr("Result viewer"),
                r"result-viewer.png",
                self.openResultViewer,
                toolbar=self.toolbar,
            ).add_action())

    def openConfigWindow(self):
        """Open the configuration dialog."""
        from .menu_actions.configuration_dialog import ConfigurationDialog
        dlg = ConfigurationDialog(self.iface.mainWindow())
        dlg.exec()

    def runWFlowDialog(self):
        """Open the dialog to run WFlow (DEBUG)."""
        from .menu_actions.run_wflow import RunWFlowProgress
        dlg = RunWFlowProgress(self.iface.mainWindow())
        dlg.exec()
    
    def openResultViewer(self):
        """Open the dialog to run WFlow (DEBUG)."""
        from .result_viewer import ResultViewer
        if self.results_viewer is None:
            self.results_viewer = ResultViewer()
        self.results_viewer.show()

    def runCreateReservoirDialog(self):
        from .add_field.gui.create_reservoir_dialog import CreateReservoir
        dlg = CreateReservoir(self.iface.mainWindow())
        dlg.exec()

    def runAddTerracingDialog(self):
        from .add_field.gui.add_terracing_dialog import AddTerracing
        dlg = AddTerracing(self.iface.mainWindow())
        dlg.exec()

    def runAddCheckDamsDialog(self):
        from .add_field.gui.add_check_dams_dialog import AddCheckDams
        dlg = AddCheckDams(self.iface.mainWindow())
        dlg.exec()

    def runChangeLanduseDialog(self):
        from .add_field.gui.change_landuse_dialog import ChangeLanduse
        dlg = ChangeLanduse(self.iface.mainWindow())
        dlg.exec()

    

    
        # self.toolButton = QToolButton()
        # self.toolButton.setMenu(QMenu())
        # self.toolButton.setToolButtonStyle(Settings.toolButtonStyle())
        # self.toolButton.setPopupMode(
        #     QToolButton.ToolButtonPopupMode.MenuButtonPopup)
        # toolButtonMenu = self.toolButton.menu()

        # # Create default action for the tool button
        # # NOTE The action text must be constant due to the assigned
        # # keybord shortcut. However, the button text and action tooltip
        # # will be later updated according to the current plugin name.
        # self.actionReloadRecentPlugin = QAction(
        #     icon, self.tr("Reload recent plugin"))
        # self.actionReloadRecentPlugin.setObjectName(
        #     "PluginReloader_ReloadRecentPlugin")
        # self.iface.registerMainWindowAction(
        #     self.actionReloadRecentPlugin, "Ctrl+F5")

        # # Create actions for recently processed plugins
        # self.actionForPlugin = {}
        # for plugin in Settings.recentPlugins():
        #     self.actionForPlugin[plugin] = self.createActionForPlugin(plugin)

        # # Create action for adding a new plugin
        # self.actionAddNewPlugin = QAction(icon, self.tr("Reload a plugin..."))
        # run = partial(self.run, None)
        # self.actionAddNewPlugin.triggered.connect(run)
        # # Append it to the acions dictionary under a NULL key
        # self.actionForPlugin[None] = self.actionAddNewPlugin

        # # Create action for opening the settings window
        # self.actionSettings = QAction(iconConf, self.tr("Configure"))
        # self.actionSettings.triggered.connect(self.openConfigWindow)

        # # Add the actionReloadRecentPlugin to menu (to present its shortcut)
        # # and set it to the tool buttton as the default action
        # self.toolButton.setDefaultAction(self.actionReloadRecentPlugin)
        # self.menu.addAction(self.actionReloadRecentPlugin)
        # self.menu.addSeparator()

        # # Update the default action's icon and tooltip and the tool button
        # # text to the most recent plugin. The action text stays constant.
        # recentPlugin = list(self.actionForPlugin.keys())[0]
        # # NOTE Updating the button text must be done after setting the button's
        # # default action!
        # self.updateDefaultAction(recentPlugin)

        # # Add all the rest of the actions to the menu and the toolbar
        # for action in self.actionForPlugin.values():
        #     toolButtonMenu.addAction(action)
        #     self.menu.addAction(action)

        # toolButtonMenu.addSeparator()
        # self.menu.addSeparator()

        # toolButtonMenu.addAction(self.actionSettings)
        # self.menu.addAction(self.actionSettings)

        # self.iface.addToolBarWidget(self.toolButton)

        # self.iface.initializationCompleted.connect(self.updatePluginIcons)


    def unload(self):
        '''
        Removes the plugin to the QGis Processing Toolbox.
        '''
        # Processing
        QgsApplication.processingRegistry().removeProvider(self.provider)
        # Dialogs / UI-based
        self.iface.pluginMenu().removeAction(self.menu.menuAction())
        for action in self.actions:
            self.iface.removeToolBarIcon(action)


    def tr(self, message: str) -> str:
        """Translate a string."""
        return QCoreApplication.translate('Plugin', message)


def classFactory(iface: QgisInterface):  # pylint: disable=invalid-name
    """Load WB_ProfielGenerator_Processing class from file WB_ProfielGenerator_Processing.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    # Loads the plugin and returns the instance
    return Plugin(iface)
