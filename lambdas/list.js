import { success, failure } from '../libs/response-lib';
import { fetchUsersDatasets } from '../datasource/dataset';

export async function main(event) {
  const userId = event.requestContext.authorizer.claims.sub;
  const datasets = await fetchUsersDatasets(userId);
  if (datasets.error) return failure({ message: 'internal server error' });

  return success({ datasets });
}
