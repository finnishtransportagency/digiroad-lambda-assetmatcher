import { verify } from 'jsonwebtoken';
import jwkToPem from 'jwk-to-pem';
import axios from 'axios';

const iss = `https://cognito-idp.${process.env.USER_POOL_REGION}.amazonaws.com/${process.env.USER_POOL_ID}`;

// Help function to generate an IAM policy
const generatePolicy = (principalId, effect, resource) => {
  if (effect && resource) {
    return {
      principalId,
      policyDocument: {
        Version: '2012-10-17',
        Statement: [
          {
            Action: 'execute-api:Invoke',
            Effect: effect,
            Resource: resource
          }
        ]
      }
    };
  } else {
    return { principalId, policyDocument: {} };
  }
};

export async function main(event, context, callback) {
  const token = event.authorizationToken;
  if (token) {
    try {
      const response = await axios.get(`${iss}/.well-known/jwks.json`);
      const pem = jwkToPem({ ...response.data.keys[0] });
      const decoded = verify(token, pem, { issuer: iss });
      return generatePolicy(decoded.sub, 'allow', event.methodArn);
    } catch (error) {
      console.log(error);
      return generatePolicy('user', 'deny', event.methodArn);
    }
  } else {
    return generatePolicy('user', 'deny', event.methodArn);
  }
}
