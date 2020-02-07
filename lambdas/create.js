import { success, failure } from '../libs/response-lib';
import { uploadGeoJSON, executeMatchingScript } from '../datasource/dataset';

export async function main(event) {
  const userId = event.requestContext.authorizer.principalId;
  const data = event.body;

  try {
    const dataset_id = await uploadGeoJSON(userId, data);
    const result = await executeMatchingScript(dataset_id);
    return success({ result, dataset_id });
  } catch (exeption) {
    console.log(exeption);
    return failure({ status: false });
  }
}
