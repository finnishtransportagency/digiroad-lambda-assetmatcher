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
  const { username, oldPassword, newPassword } = JSON.parse(event.body);
  try {
    const user = await Auth.signIn({ username, password: oldPassword });
    await Auth.changePassword(user, oldPassword, newPassword);
    return success({ SUCCESS: 'password changed successfully' });
  } catch (exeption) {
    return forbidden(exeption);
  }
}
