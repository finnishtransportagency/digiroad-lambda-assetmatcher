# lambda-assetmatcher

An AWS-lambda-digiroad API to unify the properties of the Finnish national digital road network data with multiple slightly differing and redundant data sources from municipalities' own databases.

## Current "CI"

Compress the files into a zip file, and upload to aws lambda :)

## How to initialize database:

Postgres 11, PostGIS and pgRoutign installed, (postgresql, postgis, pgrouting)

```sql
-- Initialize database
create database dr_r;
\c dr_r;

-- Add extensions
create extension postGIS;
create extension pgRouting;
```

### Import roadlink shapefiles for Vantaa from digiroad r-extract:

PostGIS install comes with tools shp2pgsql and pgsql2shp which are prefered way
to work between shapefiles and PostGIS.

```bash
wget http://aineistot.vayla.fi/digiroad/2019_02/Maakuntajako_DIGIROAD_R_EUREF-FIN/UUSIMAA.zip
unzip UUSIMAA.zip
shp2pgsql -d -s 3067 -S UUSIMAA/UUSIMAA_2/DR_LINKKI.shp dr_linkki |psql -d dr_r
```

(You can append more data with -a flag)

### Import whole Finland from GeoPackage with GDAL translation library.

more info on https://gdal.org/index.html
Warnig file download is estimated to be 1.6 GT zipped and 5 Gt as unfipped GeoPackage.

```bash
wget https://aineistot.vayla.fi/digiroad/latest/KokoSuomi_DIGIROAD_R_GeoPackage.zip
unzip KokoSuomi_DIGIROAD_R_GeoPackage.zip
ogr2ogr -f "PostgreSQL" PG:"dbname=dr_r" KokoSuomi_Digiroad_R_GeoPackage.gpkg DR_LINKKI
```

### Necessary modifications to table before matching script can be run

```sql
-- Preparing to create the network topology for routing:
alter table public.dr_linkki drop column if exists source;
alter table public.dr_linkki drop column if exists target;
alter table public.dr_linkki add column source integer;
alter table public.dr_linkki add column target integer;
alter table public.dr_linkki alter column link_id type integer using link_id::integer;


-- Adding a column for routing cost for pgr_withPoints()-function in matching prosess
alter table public.dr_linkki drop column if exists cost;
alter table public.dr_linkki add column cost float;
update public.dr_linkki set cost = ST_Length(geom);

-- Create spatial index with PostGIS to enhanche matching (Crucial for perfomance)
create index dr_linkki_spix on public.dr_linkki using gist(geom);

-- Convert the geometry to 2D
alter table public.dr_linkki alter column geom type geometry(LineString,3067) using ST_Force2D(geom);

-- Creating the topology for pgrouting extension
SELECT pgr_createTopology('public.dr_linkki', 0.5,'geom', 'link_id', 'source', 'target');
```

### Create tables for matching script

```sql
-- Creating table for json-data reccived from municipality api
-- and storing matching process and result
CREATE TABLE public.datasets (
	dataset_id uuid PRIMARY KEY,
	json_data jsonb NOT NULL,
	matched_roadlinks text,
	matching_rate decimal(3,2),
	upload_executed timestamptz,
	update_finished timestamptz,
	status_log text
)

-- Temporary table for feature manipulation in matching script.
CREATE TABLE public.temp_points (
    id serial,
    dr_link_id integer,
    fraction float,
    dr_vertex_id integer,
    geom geometry(Point,3067),
    side char(1) default 'b',
    edges text,
    source int,
    target int
);
```
