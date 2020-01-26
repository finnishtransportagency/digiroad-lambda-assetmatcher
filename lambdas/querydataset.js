import { success, failure, badRequest } from '../libs/response-lib';
import { getDatasetById } from '../datasource/dataset';
import uuidValidate from '../libs/uuidValidator-lib';

export async function main(event) {
  const ids = event.multiValueQueryStringParameters.id;

  if (!uuidValidate(ids)) return badRequest({ message: 'malformed UUID' });

  const include_geojson =
    event.queryStringParameters && event.queryStringParameters.geojson === 'yes';

  try {
    const dataset = await getDatasetById(ids, include_geojson);
    return success({ dataset });
  } catch (exeption) {
    console.log({ error: 'Error while getting datasets by id from database', details: exeption });
    return failure({ status: false });
  }
}
