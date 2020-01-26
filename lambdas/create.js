import { success, failure } from '../libs/response-lib';
import { uploadGeoJSON, executeMatchingScript } from '../datasource/dataset';

export async function main(event) {
  const data = event.body;

  try {
    const dataset_id = await uploadGeoJSON(data);
    await executeMatchingScript(dataset_id);

    return success({ dataset_id });
  } catch (exeption) {
    console.log(exeption);
    return failure({ status: false });
  }
}
