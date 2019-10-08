ogr2ogr \ 
    -f GeoJSON test_file_vantaa_version_epsg_3067.geojson \
    -s_srs EPSG:4326 \
    -t_srs EPSG:3067 \
    test_file_vantaa_version_epsg_4326.geojson 