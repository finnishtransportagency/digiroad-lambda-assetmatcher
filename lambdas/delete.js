import { success } from '../libs/response-lib';

export async function main(event) {
  const id = event.pathParameters.id;
  return success({
    message: `Delete function is not implemented yet. id: ${id}`
  });
}
