# Test data for the API

Here can be found test data for the API. We have LineStrings, Points and Polygons. API Consumes GeoJSON as HTTP POST Request body in `/dataset`-endpoint.

API can only handle GeoJSON encoded with EPSG:3067 coordinates. You can draw test data easily on [geojson.io](http://geojson.io). GeoJSON spec expects that coordinates are encoded to EPSG:4326 system but they can be easily transformed with [GDAL](https://gdal.org/).

```bash
ogr2ogr -f GeoJSON <output_3067>.json <input_4326>.json -t_srs EPSG:3067
```

