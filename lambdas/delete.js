import { accepted, notfound } from '../libs/response-lib';
import { deleteDatasetById } from '../datasource/dataset';

export async function main(event) {
  const id = event.pathParameters.id;
  const userId = event.requestContext.authorizer.claims.sub;

  const deleted = await deleteDatasetById(id, userId);

  if (deleted.dataset_id) {
    return accepted();
  } else {
    return notfound({
      message: 'Resource was not found or you might not be the owner of the resource.'
    });
  }
}
