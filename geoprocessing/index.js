const { Pool } = require('pg');
import { matchPointWithDigiroad } from './Point';
import { matchLineStringWithDigiroad } from './LineString';

export async function geoprocessGeoJSON(GeoJSON) {
  const pool = new Pool();

  const promises = GeoJSON.features.map(Feature => {
    const { type } = Feature.geometry;
    switch (type) {
      case 'Point':
        return matchPointWithDigiroad(Feature, pool);
      case 'LineString':
        return matchLineStringWithDigiroad(Feature, pool);
      default:
        return [];
    }
  });
  return Promise.all(promises).then(result => {
    result.map((ids, index) => {
      GeoJSON.features[index].properties['link_ids'] = ids;
    });
    return GeoJSON;
  });
}
