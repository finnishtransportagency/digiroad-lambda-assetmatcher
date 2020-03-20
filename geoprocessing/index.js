import { matchPointWithDigiroad } from './Point';

export async function geoprocessGeoJSON(GeoJSON) {
  const promises = GeoJSON.features.map(Feature => {
    const { type } = Feature.geometry;
    switch (type) {
      case Point:
        return matchPointWithDigiroad(feature);
      case LineString:
        return { message: 'LineString detected but not yet handled' };
      default:
        return { message: 'not yet handled' };
    }
  });

  const data = await Promise.all(promises);
  return data;
}
