export async function matchPolygonWithDigiroad(Feature, pool) {
  const { geometry } = Feature;
  const query = {
    text: `
      SELECT link_id, tienimi_su as name FROM dr_linkki
      WHERE dr_linkki.geom && (SELECT ST_SETSRID(ST_GeomFromGeoJSON($1),3067))`,
    values: [geometry]
  };

  return pool
    .query(query)
    .then(res => {
      if (Feature.properties.name) {
        const rows = res.rows.filter(row => row.name === Feature.properties.name);
        return rows.map(row => row.link_id);
      }
      return res.rows.map(row => row.link_id);
    })
    .catch(e => console.error(e.stack));
}
