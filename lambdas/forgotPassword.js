import { success, forbidden } from '../libs/response-lib';
import Amplify, { Auth } from 'aws-amplify';
import fetch from 'node-fetch';
global.fetch = fetch;

Amplify.configure({
  Auth: {
    region: process.env.USER_POOL_REGION,
    userPoolId: process.env.USER_POOL_ID,
    userPoolWebClientId: process.env.USER_POOL_CLIENT_ID
  }
});

export async function main(event) {
  const { username, code, newPassword } = JSON.parse(event.body);
  try {
    if (!code) {
      const result = await Auth.forgotPassword(username);
      return success({ message: result });
    } else {
      await Auth.forgotPasswordSubmit(username, code, newPassword);
      return success();
    }
  } catch (exeption) {
    return forbidden(exeption);
  }
}
