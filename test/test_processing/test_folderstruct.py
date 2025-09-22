
def test_algorithms_loaded(qgis_app, plugin_name):
    """
    Tests whether all algorithms which have been defined are being loaded
    in the Qgis processingRegistry.capitalize()
    """
    # Create a list of all algorithms currently registered in QGis. Our
    # newly developed plugin is automatically added to QGis by the means
    # of the `conftest.py` file
    alg_ids = [alg.id() for alg in qgis_app.processingRegistry().algorithms()]
    print(alg_ids)
    # Now assert whether all plugins are successfuly loaded by the QGis
    # processing registry. The name of the plugin is equal to the __NAME__
    # field of the algorithm, however take into mind that it is reduced
    # to lower-case alphanumerical characters only. For example:
    #  MyAwesomePlugin_Test1 => myawesomeplugintest1
    assert f"{plugin_name}:addgaugelocations" in alg_ids
    assert f"{plugin_name}:addreservoirs" in alg_ids
    assert f"{plugin_name}:changelanduse" in alg_ids
    assert f"{plugin_name}:addcheckdams" in alg_ids
    assert f"{plugin_name}:addterracing" in alg_ids
    assert f"{plugin_name}:loadlayers" in alg_ids
    assert f"{plugin_name}:runcalculation" in alg_ids


