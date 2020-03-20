const { Client } = require('pg');

export async function matchPointWithDigiroad(Feature) {
  const client = new Client();
  const { coordinates } = Feature.geometry;
  try {
    client.connect();

    return client.query(
      `
      WITH ref_point AS (
        SELECT ST_SetSRID(ST_Point($1, $2),3067) AS geom
      )
      
      SELECT link_id
        FROM dr_linkki, ref_point
      WHERE ST_BUFFER(ref_point.geom, 50) && dr_linkki.geom
      ORDER BY ref_point.geom <-> dr_linkki.geom ASC
      LIMIT 1`,
      [coordinates[0], coordinates[1]]
    );
  } catch (exception) {
    console.log(exeption);
    throw new Error('Database connection error');
  } finally {
    client.end();
  }
}
