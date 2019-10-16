-- The matching process.
-- 1. Fetch stored data from dataset table.
-- 2. Transform fetched JSON to PostGIS points and store it to temp_points table.
-- 3. Buffering new temp_points and getting a link_id from nearest dr_linkki
-- 4. Selecting nearest vertexes from pgRouting topology
-- 5. Slecting the the A and B for routing
-- 6. Using the topology to get all edges in the route between features A and B
-- 7. Storing the final result on datasets table

-- Running the script from terminal
-- psql -d dr_r -f matching_script.sql
-- running this in terminal requires changes for 'WHERE dataset_id = %s' on line 22

DO
$BODY$
DECLARE
  -- 1. Datafetch
  -- Fetches GeoJSON data and stores it for variable. 
  geojson_data jsonb := (
    SELECT json_data->'features' 
    FROM datasets 
    WHERE dataset_id = %s
  );
  feature jsonb;
	point_coordinates jsonb;
	point_temp_store geometry;
	
BEGIN
  
  -- Script prosesses one map featureat at a time.
  FOR feature IN SELECT * FROM jsonb_array_elements(geojson_data)
    LOOP

    -- for every feature temp_points tabel is emptied and serial reset.
    -- below script is designed to use serial id.
    TRUNCATE TABLE temp_points RESTART IDENTITY CASCADE;
    
    -- 2. line feature is made to points in order to be used in pgRouting.
    FOR point_coordinates IN 
    SELECT * FROM jsonb_array_elements(feature->'geometry'->'coordinates')
      
      LOOP
        point_temp_store = ST_SETSRID(
          ST_MAKEPOINT(
            cast(point_coordinates->0 as double precision), 
            cast(point_coordinates->1 as double precision)
          ), 
          3067);
          
        INSERT INTO temp_points (geom) VALUES (point_temp_store);			
      END LOOP;



      -- This might enhance performance but more important is that dr_linkki has spatial index.
      CREATE INDEX temp_points_spix ON temp_points USING GIST(geom);


      -- 3. Buffering new temp_points and getting a link_id from nearest dr_linkki


      -- The && operator returns TRUE if the 2D bounding box of geometry 
      -- A intersects the 2D bounding box of geometry B.

      -- <-> — Returns the 2D distance between A and B.

      UPDATE temp_points
      SET dr_link_id =(
        SELECT dr_linkki.link_id
        FROM dr_linkki
        WHERE ST_Buffer(temp_points.geom,50) && dr_linkki.geom
        ORDER BY temp_points.geom <-> dr_linkki.geom ASC
        LIMIT 1
      );

      UPDATE temp_points
      SET fraction = (
        SELECT ST_LineLocatePoint(dr_linkki.geom,temp_points.geom)
        FROM dr_linkki
        WHERE temp_points.dr_link_id = dr_linkki.link_id
      );

      -- 4. Selecting nearest vertexes from pgRouting topology

      -- this is same procedure as in part 3 but instead of dr_linkki ids here
      -- temp_points are connected to nearest vertex which were made by 
      -- pgr_createTopology-function in pgRouting
      UPDATE temp_points 
      SET dr_vertex_id = (
        SELECT lnk_vrx.id
        FROM dr_linkki_vertices_pgr lnk_vrx
        WHERE ST_Buffer(temp_points.geom, 5) && lnk_vrx.the_geom -- 50m might be overkill?
        ORDER BY temp_points.geom <-> lnk_vrx.the_geom ASC
        LIMIT 1
      );

      -- 5. Slecting the the A and B for routing
      -- this prosess depends on tables id column which has to be serial

      -- pgr_withPoints()-function doesn't understand NULL-values thats why
      -- temp_points tabel's id is used in case when vertex is missing.
      UPDATE temp_points 
      SET source = (
        SELECT 
        CASE
          WHEN temp_points.dr_vertex_id IS NOT NULL THEN temp_points.dr_vertex_id
          ELSE -1 * temp_points.id
        END
      );

      UPDATE temp_points
      SET target = (
        SELECT 
        CASE
          WHEN temp_points.dr_vertex_id IS NOT NULL 
            THEN temp_points.dr_vertex_id
          ELSE -1 * temp_points.id
        END
      );


      -- pgRouting uses first & last points for routing from A to B
      -- but the route can also contain more points alongside the route

      WITH first_point AS (
        SELECT * 
        FROM temp_points 
        ORDER BY id ASC 
        LIMIT 1
      ),
      last_point AS (
        SELECT * 
        FROM temp_points 
        ORDER BY id DESC 
        LIMIT 1
      )

      -- 6. Using the topology to get all edges in the route between features A and B
      -- pgr_withPoints(edges_sql, points_sql, from_vid,  to_vid  [, directed] [, driving_side] [, details])

      UPDATE temp_points 
      SET edges = (
        SELECT string_agg(edge,',') 
        FROM (
          SELECT DISTINCT edge::text 
          FROM pgr_withPoints(
          'SELECT 
              link_id AS id, 
              source, 
              target, 
              cost, 
              cost AS reverse_cost 
            FROM public.dr_linkki 
            ORDER BY id',
            
          'SELECT 
              id AS pid, 
              dr_link_id AS edge_id, 
              fraction, 
              side 
            FROM public.temp_points 
            WHERE dr_link_id IS NOT NULL',
            
          (SELECT source FROM first_point),
            (SELECT target FROM last_point),
            details := true) 
        WHERE edge != -1) 
        RETURN 
      );

      -- 7. Datastoring with manuall text array

      -- PostgeSQL was not fuctioning as we hoped for storing multidimentional arrays.
      -- Cause of the problems were empty arrays and arrays with only single value.
      -- We decided to do this with text/string and parcing it elsewhere.

      WITH edges AS (
	      SELECT 
		      CONCAT('[', edges, ']') AS link_ids 
	      FROM temp_points 
	      LIMIT 1
      )

      UPDATE datasets 
      SET matched_roadlinks = concat_ws(
	        ',',matched_roadlinks,(SELECT link_ids FROM edges)
      ); 

      -- TRUNCATE datasets;

      DROP INDEX temp_points_spix;
  END LOOP;
END;
$BODY$
