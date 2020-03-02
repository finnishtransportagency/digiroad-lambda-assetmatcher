import { success, badRequest, notfound } from '../../libs/response-lib';
import uuidValidate from '../../libs/uuidValidator-lib';
import { getUsersDatasetById, setUpdateExecuted } from '../../datasource/dataset';

export async function main(event) {
  const datasetId = event.pathParameters.id;
  const userId = event.requestContext.authorizer.principalId;
  if (!uuidValidate(datasetId)) return badRequest({ message: 'malformed UUID' });

  const result = await getUsersDatasetById(datasetId, userId);
  if (result.length === 0 && result[0].dataset_id) {
    return notfound({
      message: 'Resource was not found or you might not be the owner of the resource.'
    });
  }

  const updated = await setUpdateExecuted(datasetId);

  return success({ message: 'Update not fully implemented yet.', updated });
}
