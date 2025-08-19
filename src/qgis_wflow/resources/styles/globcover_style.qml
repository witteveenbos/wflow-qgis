<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis styleCategories="AllStyleCategories" hasScaleBasedVisibilityFlag="0" minScale="1e+08" maxScale="0" version="3.28.3-Firenze">
  <flags>
    <Identifiable>1</Identifiable>
    <Removable>1</Removable>
    <Searchable>1</Searchable>
    <Private>0</Private>
  </flags>
  <temporal enabled="0" fetchMode="0" mode="0">
    <fixedRange>
      <start></start>
      <end></end>
    </fixedRange>
  </temporal>
  <elevation enabled="0" symbology="Line" band="1" zscale="1" zoffset="0">
    <data-defined-properties>
      <Option type="Map">
        <Option type="QString" name="name" value=""/>
        <Option name="properties"/>
        <Option type="QString" name="type" value="collection"/>
      </Option>
    </data-defined-properties>
    <profileLineSymbol>
      <symbol alpha="1" is_animated="0" type="line" name="" frame_rate="10" force_rhr="0" clip_to_extent="1">
        <data_defined_properties>
          <Option type="Map">
            <Option type="QString" name="name" value=""/>
            <Option name="properties"/>
            <Option type="QString" name="type" value="collection"/>
          </Option>
        </data_defined_properties>
        <layer class="SimpleLine" enabled="1" locked="0" pass="0">
          <Option type="Map">
            <Option type="QString" name="align_dash_pattern" value="0"/>
            <Option type="QString" name="capstyle" value="square"/>
            <Option type="QString" name="customdash" value="5;2"/>
            <Option type="QString" name="customdash_map_unit_scale" value="3x:0,0,0,0,0,0"/>
            <Option type="QString" name="customdash_unit" value="MM"/>
            <Option type="QString" name="dash_pattern_offset" value="0"/>
            <Option type="QString" name="dash_pattern_offset_map_unit_scale" value="3x:0,0,0,0,0,0"/>
            <Option type="QString" name="dash_pattern_offset_unit" value="MM"/>
            <Option type="QString" name="draw_inside_polygon" value="0"/>
            <Option type="QString" name="joinstyle" value="bevel"/>
            <Option type="QString" name="line_color" value="183,72,75,255"/>
            <Option type="QString" name="line_style" value="solid"/>
            <Option type="QString" name="line_width" value="0.6"/>
            <Option type="QString" name="line_width_unit" value="MM"/>
            <Option type="QString" name="offset" value="0"/>
            <Option type="QString" name="offset_map_unit_scale" value="3x:0,0,0,0,0,0"/>
            <Option type="QString" name="offset_unit" value="MM"/>
            <Option type="QString" name="ring_filter" value="0"/>
            <Option type="QString" name="trim_distance_end" value="0"/>
            <Option type="QString" name="trim_distance_end_map_unit_scale" value="3x:0,0,0,0,0,0"/>
            <Option type="QString" name="trim_distance_end_unit" value="MM"/>
            <Option type="QString" name="trim_distance_start" value="0"/>
            <Option type="QString" name="trim_distance_start_map_unit_scale" value="3x:0,0,0,0,0,0"/>
            <Option type="QString" name="trim_distance_start_unit" value="MM"/>
            <Option type="QString" name="tweak_dash_pattern_on_corners" value="0"/>
            <Option type="QString" name="use_custom_dash" value="0"/>
            <Option type="QString" name="width_map_unit_scale" value="3x:0,0,0,0,0,0"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" name="name" value=""/>
              <Option name="properties"/>
              <Option type="QString" name="type" value="collection"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
    </profileLineSymbol>
    <profileFillSymbol>
      <symbol alpha="1" is_animated="0" type="fill" name="" frame_rate="10" force_rhr="0" clip_to_extent="1">
        <data_defined_properties>
          <Option type="Map">
            <Option type="QString" name="name" value=""/>
            <Option name="properties"/>
            <Option type="QString" name="type" value="collection"/>
          </Option>
        </data_defined_properties>
        <layer class="SimpleFill" enabled="1" locked="0" pass="0">
          <Option type="Map">
            <Option type="QString" name="border_width_map_unit_scale" value="3x:0,0,0,0,0,0"/>
            <Option type="QString" name="color" value="183,72,75,255"/>
            <Option type="QString" name="joinstyle" value="bevel"/>
            <Option type="QString" name="offset" value="0,0"/>
            <Option type="QString" name="offset_map_unit_scale" value="3x:0,0,0,0,0,0"/>
            <Option type="QString" name="offset_unit" value="MM"/>
            <Option type="QString" name="outline_color" value="35,35,35,255"/>
            <Option type="QString" name="outline_style" value="no"/>
            <Option type="QString" name="outline_width" value="0.26"/>
            <Option type="QString" name="outline_width_unit" value="MM"/>
            <Option type="QString" name="style" value="solid"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" name="name" value=""/>
              <Option name="properties"/>
              <Option type="QString" name="type" value="collection"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
    </profileFillSymbol>
  </elevation>
  <customproperties>
    <Option type="Map">
      <Option type="QString" name="WMSBackgroundLayer" value="false"/>
      <Option type="QString" name="WMSPublishDataSourceUrl" value="false"/>
      <Option type="QString" name="embeddedWidgets/count" value="0"/>
      <Option type="QString" name="identify/format" value="Value"/>
    </Option>
  </customproperties>
  <pipe-data-defined-properties>
    <Option type="Map">
      <Option type="QString" name="name" value=""/>
      <Option name="properties"/>
      <Option type="QString" name="type" value="collection"/>
    </Option>
  </pipe-data-defined-properties>
  <pipe>
    <provider>
      <resampling enabled="false" zoomedInResamplingMethod="nearestNeighbour" zoomedOutResamplingMethod="nearestNeighbour" maxOversampling="2"/>
    </provider>
    <rasterrenderer classificationMin="14" alphaBand="-1" classificationMax="210" opacity="1" band="1" type="singlebandpseudocolor" nodataColor="">
      <rasterTransparency/>
      <minMaxOrigin>
        <limits>MinMax</limits>
        <extent>WholeRaster</extent>
        <statAccuracy>Estimated</statAccuracy>
        <cumulativeCutLower>0.02</cumulativeCutLower>
        <cumulativeCutUpper>0.98</cumulativeCutUpper>
        <stdDevFactor>2</stdDevFactor>
      </minMaxOrigin>
      <rastershader>
        <colorrampshader classificationMode="1" maximumValue="210" minimumValue="14" clip="0" colorRampType="DISCRETE" labelPrecision="0">
          <colorramp type="gradient" name="[source]">
            <Option type="Map">
              <Option type="QString" name="color1" value="0,0,4,255"/>
              <Option type="QString" name="color2" value="252,253,191,255"/>
              <Option type="QString" name="direction" value="ccw"/>
              <Option type="QString" name="discrete" value="0"/>
              <Option type="QString" name="rampType" value="gradient"/>
              <Option type="QString" name="spec" value="rgb"/>
              <Option type="QString" name="stops" value="0.0196078;2,2,11,255;rgb;ccw:0.0392157;5,4,22,255;rgb;ccw:0.0588235;9,7,32,255;rgb;ccw:0.0784314;14,11,43,255;rgb;ccw:0.0980392;20,14,54,255;rgb;ccw:0.117647;26,16,66,255;rgb;ccw:0.137255;33,17,78,255;rgb;ccw:0.156863;41,17,90,255;rgb;ccw:0.176471;49,17,101,255;rgb;ccw:0.196078;57,15,110,255;rgb;ccw:0.215686;66,15,117,255;rgb;ccw:0.235294;74,16,121,255;rgb;ccw:0.254902;82,19,124,255;rgb;ccw:0.27451;90,22,126,255;rgb;ccw:0.294118;98,25,128,255;rgb;ccw:0.313725;106,28,129,255;rgb;ccw:0.333333;114,31,129,255;rgb;ccw:0.352941;121,34,130,255;rgb;ccw:0.372549;129,37,129,255;rgb;ccw:0.392157;137,40,129,255;rgb;ccw:0.411765;145,43,129,255;rgb;ccw:0.431373;153,45,128,255;rgb;ccw:0.45098;161,48,126,255;rgb;ccw:0.470588;170,51,125,255;rgb;ccw:0.490196;178,53,123,255;rgb;ccw:0.509804;186,56,120,255;rgb;ccw:0.529412;194,59,117,255;rgb;ccw:0.54902;202,62,114,255;rgb;ccw:0.568627;210,66,111,255;rgb;ccw:0.588235;217,70,107,255;rgb;ccw:0.607843;224,76,103,255;rgb;ccw:0.627451;231,82,99,255;rgb;ccw:0.647059;236,88,96,255;rgb;ccw:0.666667;241,96,93,255;rgb;ccw:0.686275;244,105,92,255;rgb;ccw:0.705882;247,114,92,255;rgb;ccw:0.72549;249,123,93,255;rgb;ccw:0.745098;251,133,96,255;rgb;ccw:0.764706;252,142,100,255;rgb;ccw:0.784314;253,152,105,255;rgb;ccw:0.803922;254,161,110,255;rgb;ccw:0.823529;254,170,116,255;rgb;ccw:0.843137;254,180,123,255;rgb;ccw:0.862745;254,189,130,255;rgb;ccw:0.882353;254,198,138,255;rgb;ccw:0.901961;254,207,146,255;rgb;ccw:0.921569;254,216,154,255;rgb;ccw:0.941176;253,226,163,255;rgb;ccw:0.960784;253,235,172,255;rgb;ccw:0.980392;252,244,182,255;rgb;ccw"/>
            </Option>
          </colorramp>
          <item alpha="255" label="11 Post-flooding or irrigated croplands (or aquatic)" color="#aaf0f0" value="11"/>
          <item alpha="255" label="14 Rainfed croplands" color="#ffff64" value="14"/>
          <item alpha="255" label="20 Mosaic cropland (50-70%) / vegetation (grassland/shrubland/forest) (20-50%)" color="#dcf064" value="20"/>
          <item alpha="255" label="30 Mosaic vegetation (grassland/shrubland/forest) (50-70%) / cropland (20-50%) " color="#cdcd66" value="30"/>
          <item alpha="255" label="40 Closed to open (>15%) broadleaved evergreen or semi-deciduous forest (>5m)" color="#006400" value="40"/>
          <item alpha="255" label="50 Closed (>40%) broadleaved deciduous forest (>5m)" color="#00a000" value="50"/>
          <item alpha="255" label="60 Open (15-40%) broadleaved deciduous forest/woodland (>5m)" color="#aac800" value="60"/>
          <item alpha="255" label="70 Closed (>40%) needleleaved evergreen forest (>5m)" color="#003c00" value="70"/>
          <item alpha="255" label="90 Open (15-40%) needleleaved deciduous or evergreen forest (>5m)" color="#286400" value="90"/>
          <item alpha="255" label="100 Mosaic forest or shrubland (50-70%) / grassland (20-50%)" color="#788200" value="100"/>
          <item alpha="255" label="110 Mosaic forest or shrubland (50-70%) / grassland (20-50%)" color="#8ca000" value="110"/>
          <item alpha="255" label="120 Mosaic grassland (50-70%) / forest or shrubland (20-50%) " color="#be9600" value="120"/>
          <item alpha="255" label="130 Closed to open (>15%) (broadleaved or needleleaved evergreen or deciduous) shrubland (&lt;5m)" color="#966400" value="130"/>
          <item alpha="255" label="140 Closed to open (>15%) herbaceous vegetation (grassland savannas or lichens/mosses)" color="#ffb432" value="140"/>
          <item alpha="255" label="150 Closed to open (>15%) herbaceous vegetation (grassland savannas or lichens/mosses)" color="#ffebaf" value="150"/>
          <item alpha="255" label="160 Closed to open (>15%) broadleaved forest regularly flooded (semi-permanently or temporarily) - Fresh or brackish water" color="#00785a" value="160"/>
          <item alpha="255" label="170 Closed (>40%) broadleaved forest or shrubland permanently flooded - Saline or brackish water" color="#009678" value="170"/>
          <item alpha="255" label="180 Closed to open (>15%) grassland or woody vegetation on regularly flooded or waterlogged soil -  Fresh brackish or saline water" color="#00dc82" value="180"/>
          <item alpha="255" label="190 Artificial surfaces and associated areas (Urban areas >50%)" color="#c31400" value="190"/>
          <item alpha="255" label="200 Bare areas" color="#fff5d7" value="200"/>
          <item alpha="255" label="210 Water bodies" color="#0046c8" value="210"/>
          <item alpha="255" label="220 Permanent snow and ice" color="#ffffff" value="220"/>
          <item alpha="255" label="230 No Data" color="#000000" value="230"/>
          <rampLegendSettings maximumLabel="" useContinuousLegend="1" orientation="2" prefix="" suffix="" minimumLabel="" direction="0">
            <numericFormat id="basic">
              <Option type="Map">
                <Option type="invalid" name="decimal_separator"/>
                <Option type="int" name="decimals" value="6"/>
                <Option type="int" name="rounding_type" value="0"/>
                <Option type="bool" name="show_plus" value="false"/>
                <Option type="bool" name="show_thousand_separator" value="true"/>
                <Option type="bool" name="show_trailing_zeros" value="false"/>
                <Option type="invalid" name="thousand_separator"/>
              </Option>
            </numericFormat>
          </rampLegendSettings>
        </colorrampshader>
      </rastershader>
    </rasterrenderer>
    <brightnesscontrast brightness="0" gamma="1" contrast="0"/>
    <huesaturation grayscaleMode="0" invertColors="0" colorizeRed="255" colorizeOn="0" saturation="0" colorizeGreen="128" colorizeStrength="100" colorizeBlue="128"/>
    <rasterresampler maxOversampling="2"/>
    <resamplingStage>resamplingFilter</resamplingStage>
  </pipe>
  <blendMode>0</blendMode>
</qgis>
