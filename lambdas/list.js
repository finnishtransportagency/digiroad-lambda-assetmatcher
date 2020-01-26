import { success, failure } from '../libs/response-lib';
import { fetshTenNewestDatasets } from '../datasource/dataset';

export async function main() {
  const datasets = await fetshTenNewestDatasets();
  if (datasets.error) return failure({ message: 'internal server error' });

  return success({ datasets });
}
