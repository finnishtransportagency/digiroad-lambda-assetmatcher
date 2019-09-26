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
Import roadlink shapefiles for Vantaa from digiroad r-extract:

```bash
wget http://aineistot.vayla.fi/digiroad/2019_02/Maakuntajako_DIGIROAD_R_EUREF-FIN/UUSIMAA.zip
unzip UUSIMAA.zip
shp2pgsql -d -s 3067 -S UUSIMAA/UUSIMAA_2/DR_LINKKI.shp dr_linkki |psql -d dr_r
```
(You can append more data with -a flag)
```sql
-- Preparing to create the network topology for routing:
alter table public.dr_linkki drop column if exists source;
alter table public.dr_linkki drop column if exists target;
alter table public.dr_linkki add column source integer;
alter table public.dr_linkki add column target integer;
alter table public.dr_linkki alter column link_id type integer using link_id::integer;

-- Convert the geometry to 2D
alter table public.dr_linkki alter column geom type geometry(LineString,3067) using ST_Force2D(geom);

-- Creating the topology for pgrouting extension
SELECT  pgr_createTopology('public.dr_linkki', 0.5,'geom', 'link_id', 'source', 'target');
```




