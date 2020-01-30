import { success, failure } from '../libs/response-lib';
import { fetchTenNewestDatasets } from '../datasource/dataset';

export async function main() {
  const datasets = await fetchTenNewestDatasets();
  if (datasets.error) return failure({ message: 'internal server error' });

  return success({ datasets });
}
