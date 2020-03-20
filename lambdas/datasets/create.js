import { success, failure } from '../../libs/response-lib';
import { uploadGeoJSON } from '../../datasource/dataset';
import { geoprocessGeoJSON } from '../../geoprocessing';

export async function main(event) {
  const userId = event.requestContext.authorizer.principalId;
  const data = event.body;

  try {
    const dataset_id = await uploadGeoJSON(userId, data);
    // const result = await executeMatchingScript(dataset_id);
    const GeoJSON = JSON.parse(data);
    geoprocessGeoJSON(GeoJSON)
      .then(() => console.log('Matching done'))
      .catch(err => console.error(err.stack));
    return success({ message: 'Matching started...', dataset_id });
  } catch (exeption) {
    console.log(exeption);
    return failure({ status: false });
  }
}
