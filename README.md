# lambda-assetmatcher

An AWS-lambda-digiroad API to unify the properties of the Finnish national digital road network data with multiple slightly differing and redundant data sources from municipalities' own databases.

# Installation and requirements (quick guide)

More in-depth installation guide can be found below provided by serverless-stack.com.

### Install AWS CLI

AWS CLI needs Python 🐍 installation and PIP.

```bash
$ sudo pip install awscli
```

Or using Homebrew on macOS:

```bash
$ brew install awscli
```

### Serverless framework installation

Serverless Framework requires NodeJS and NPM which comes bundled with NodeJS installation.

Once NPM is installed Serverless can be installed as global package.

```bash
$ npm install serverless -g
```

### Installing packages

```bash
$ npm install
```

### Setting up environment variables

Database connection

```
RDS_DATABASE=<required>
RDS_HOST=<required>
RDS_USER=<required>
RDS_PASSWORD=<required>
```

Cognito User Pool connections

```
USER_POOL_ID=<required>
USER_POOL_CLIENT_ID=<required>
USER_POOL_REGION=<required>
```

On AWS Cloud the whole operation is running inside VPC.
These varaiables has to be set before deployment.

```
RDS_ACCESS_ROLE=<required>(AWS:ARN:HERE)
SECURITY_GROUP_ID=<required>
VPC_SUBNET_1=<required>
VPC_SUBNET_2=<required>
VPC_SUBNET_3=<required>
```

## How to initialize database:

### PostgreSQL database running inside Docker container
You can also get started developing this project by setting up the database with `docker-compose`. There is a docker-compose file in the root of this project.

```bash
export POSTGRES_PASSWORD=<password>
docker-compose up -d
```

With docker you don't need to create database nor tables manually. Everything is included in the `docker image`.

---

### How to create database manually

Postgres 11, PostGIS and pgRoutign installed, (postgresql, postgis, pgrouting)

```sql
-- This can be done with psql CLI Tool that comes with postgres installation.
CREATE DATABASE dr_r;
\c dr_r;

-- Extensions
CREATE EXTENSION "postGIS";
CREATE EXTENSION "pgRouting";
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
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
	dataset_id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
	user_id uuid NOT NULL,
	json_data jsonb NOT NULL,
	matched_roadlinks text,
	matching_rate decimal(3,2),
	matching_rate_feature double precision[],
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

# Serverless Node.js Starter

A Serverless starter that adds ES7 syntax, serverless-offline, linting, environment variables, and unit test support. Part of the [Serverless Stack](http://serverless-stack.com) guide.

[Serverless Node.js Starter](https://github.com/AnomalyInnovations/serverless-nodejs-starter) uses the [serverless-bundle](https://github.com/AnomalyInnovations/serverless-bundle) plugin (an extension of the [serverless-webpack](https://github.com/serverless-heaven/serverless-webpack) plugin) and the [serverless-offline](https://github.com/dherault/serverless-offline) plugin. It supports:

- **Generating optimized Lambda packages with Webpack**
- **Use ES7 syntax in your handler functions**
  - Use `import` and `export`
- **Run API Gateway locally**
  - Use `serverless offline start`
- **Support for unit tests**
  - Run `npm test` to run your tests
- **Sourcemaps for proper error messages**
  - Error message show the correct line numbers
  - Works in production with CloudWatch
- **Lint your code with ESLint**
- **Add environment variables for your stages**
- **No need to manage Webpack or Babel configs**

---

### Demo

A demo version of this service is hosted on AWS - [`https://z6pv80ao4l.execute-api.us-east-1.amazonaws.com/dev/hello`](https://z6pv80ao4l.execute-api.us-east-1.amazonaws.com/dev/hello)

And here is the ES7 source behind it

```javascript
export const hello = async (event, context) => {
  return {
    statusCode: 200,
    body: JSON.stringify({
      message: `Go Serverless v1.0! ${await message({
        time: 1,
        copy: 'Your function executed successfully!'
      })}`,
      input: event
    })
  };
};

const message = ({ time, ...rest }) =>
  new Promise((resolve, reject) =>
    setTimeout(() => {
      resolve(`${rest.copy} (with a delay)`);
    }, time * 1000)
  );
```

### Upgrading from v1.x

We have detailed instructions on how to upgrade your app to the v2.0 of the starter if you were using v1.x before. [Read about it here](https://github.com/AnomalyInnovations/serverless-nodejs-starter/releases/tag/v2.0).

### Requirements

- [Install the Serverless Framework](https://serverless.com/framework/docs/providers/aws/guide/installation/)
- [Configure your AWS CLI](https://serverless.com/framework/docs/providers/aws/guide/credentials/)

### Installation

To create a new Serverless project.

```bash
$ serverless install --url https://github.com/AnomalyInnovations/serverless-nodejs-starter --name my-project
```

Enter the new directory

```bash
$ cd my-project
```

Install the Node.js packages

```bash
$ npm install
```

### Usage

To run a function on your local

```bash
$ serverless invoke local --function hello
```

To simulate API Gateway locally using [serverless-offline](https://github.com/dherault/serverless-offline)

```bash
$ serverless offline start
```

Deploy your project

```bash
$ serverless deploy
```

Deploy a single function

```bash
$ serverless deploy function --function hello
```

#### Running Tests

Run your tests using

```bash
$ npm test
```

We use Jest to run our tests. You can read more about setting up your tests [here](https://facebook.github.io/jest/docs/en/getting-started.html#content).

#### Environment Variables

To add environment variables to your project

1. Rename `env.example` to `.env`.
2. Add environment variables for your local stage to `.env`.
3. Uncomment `environment:` block in the `serverless.yml` and reference the environment variable as `${env:MY_ENV_VAR}`. Where `MY_ENV_VAR` is added to your `.env` file.
4. Make sure to not commit your `.env`.

#### Linting

We use [ESLint](https://eslint.org) to lint your code via the [serverless-bundle](https://github.com/AnomalyInnovations/serverless-bundle) plugin.

You can turn this off by adding the following to your `serverless.yml`.

```yaml
custom:
  bundle:
    linting: false
```

To [override the default config](https://eslint.org/docs/user-guide/configuring), add a `.eslintrc.json` file. To ignore ESLint for specific files, add it to a `.eslintignore` file.

### Support

- Open a [new issue](https://github.com/AnomalyInnovations/serverless-nodejs-starter/issues/new) if you've found a bug or have some suggestions.
- Or submit a pull request!

---

This repo is maintained by [Anomaly Innovations](https://anoma.ly); makers of [Seed](https://seed.run) and [Serverless Stack](https://serverless-stack.com).
