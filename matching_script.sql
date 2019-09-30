TRUNCATE TABLE temp_points RESTART IDENTITY CASCADE;

-- Retrieves GeoJSON data and converts lines it contains to points
-- This query reads only the first geometry. this needs improvement in the future
WITH make_points AS ( 
  SELECT 
	json_data->'features'->0->'geometry' AS geom_json
  FROM datasets 
),

transform_points AS (
  SELECT
  ST_DumpPoints(
	  ST_Force2D(
	    ST_GeomFromGeoJSON(geom_json)
	  )
  ) AS dump_geom 
  FROM make_points
) 

INSERT INTO temp_points (geom) (
  SELECT 
    (dump_geom).geom AS geom 
  FROM transform_points
);

CREATE INDEX temp_points_spix ON temp_points USING GIST(geom);

-- this query expects that dr_linkki column data type is integer.
-- By default it is VARCHAR(20) it can be altered with this query:
-- ALTER TABLE dr_linkki
-- 	ALTER COLUMN link_id TYPE int
-- 	USING link_id::int;
update temp_points point set dr_link_id =
(select v.link_id
from dr_linkki v, temp_points p
where p.id = point.id and ST_Buffer(point.geom,50) && v.geom
order by p.geom <-> v.geom asc limit 1);

update temp_points point set fraction =
(select ST_LineLocatePoint(v.geom,point.geom)
from dr_linkki v
where point.dr_link_id = v.link_id);

update temp_points point set dr_vertex_id =
(select v.id
from dr_linkki_vertices_pgr v, temp_points p
where p.id = point.id and ST_Buffer(p.geom, 50) && v.the_geom
order by p.geom <-> v.the_geom asc limit 1);

update temp_points p set source =
(select case
  when p.dr_vertex_id is not null then p.dr_vertex_id
  else -1*p.id
end as source);

update temp_points p set target =
(select case
  when p.dr_vertex_id is not null then p.dr_vertex_id
  else -1*p.id
end as target);

with first_point as (select * from temp_points order by id limit 1),
last_point as (select * from temp_points order by id desc limit 1)
update temp_points set edges =
(SELECT string_agg(edge,',') from
(SELECT distinct edge::text FROM pgr_withPoints(
  'SELECT link_id as id, source, target, cost, cost as reverse_cost FROM public.dr_linkki ORDER BY id',
  'SELECT id as pid, dr_link_id edge_id, fraction, side from public.temp_points where dr_link_id IS NOT Null',
  (select source from first_point),(select target from last_point),
 details := true) where edge != -1) foo);
 
truncate datasets;

drop index temp_points_spix;