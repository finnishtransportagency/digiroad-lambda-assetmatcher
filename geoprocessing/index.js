const { Pool } = require('pg');
import { matchPointWithDigiroad } from './Point';
import { matchLineStringWithDigiroad } from './LineString';
import { matchPolygonWithDigiroad } from './Polygon';
import LineMatcher from './MatchingRateLineString';

export async function geoprocessGeoJSON(GeoJSON) {
  const pool = new Pool();

  const promises = GeoJSON.features.map(Feature => {
    const { type } = Feature.geometry;
    switch (type) {
      case 'Point':
        return matchPointWithDigiroad(Feature, pool);
      case 'LineString':
        return matchLineStringWithDigiroad(Feature, pool);
      case 'Polygon':
        return matchPolygonWithDigiroad(Feature, pool);
      default:
        return [];
    }
  });
  return Promise.all(promises).then(async result => {
    result.map((ids, index) => {
      GeoJSON.features[index].properties['link_ids'] = ids;
    });
    await generateMatchingRate(GeoJSON);
    return GeoJSON;
  });
}

export async function generateMatchingRate(GeoJSON) {
  const pool = new Pool();

  const promises = GeoJSON.features.map(Feature => {
    const { type } = Feature.geometry;
    switch (type) {
      case 'LineString':
        return LineMatcher.calculateMatchingRate(Feature, pool);
      default:
        return;
    }
  });

  return Promise.all(promises).then(result => {
    const matches = result.filter(match => match);
    if (!matches) return 0;
    const totalMatchingRate = matches.reduce((previous, current) => previous + current, 0);
    GeoJSON['matchingRate'] = totalMatchingRate / matches.length;
    return GeoJSON;
  });
}
