import { success, badRequest, notfound, failure } from '../../libs/response-lib';
import uuidValidate from '../../libs/uuidValidator-lib';
import { getUsersDatasetById, setUpdateExecuted } from '../../datasource/dataset';
//import { uploadToOTH } from '../OTHService';

export async function main(event) {
  const datasetId = event.pathParameters.id;
  const userId = event.requestContext.authorizer.principalId;
  if (!uuidValidate(datasetId)) return badRequest({ message: 'malformed UUID' });

  const dataset = await getUsersDatasetById(datasetId, userId);
  if (dataset.length === 0 && dataset[0].dataset_id) {
    return notfound({
      message: 'Resource was not found or you might not be the owner of the resource.'
    });
  }

  try {
    //await uploadToOTH(dataset);
    const updated = await setUpdateExecuted(datasetId);
    return success({
      message:
        'Success: Upload method is not fully implemented. In future this method will upload data to Digiroad.',
      updated
    });
  } catch (exeption) {
    return failure({
      message: 'internal server error. Uplpad to Digiroad database was not successfull.'
    });
  }
}
