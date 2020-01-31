export function success(body) {
  return buildResponse(200, body);
}

export function accepted(body) {
  return buildResponse(202, body);
}

export function badrequest(body) {
  return buildResponse(400, body);
}

export function forbidden(body) {
  return buildResponse(403, body);
}

export function notfound(body) {
  return buildResponse(404, body);
}

export function failure(body) {
  return buildResponse(500, body);
}

function buildResponse(statusCode, body) {
  return {
    statusCode: statusCode,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Credentials': true
    },
    body: JSON.stringify(body)
  };
}
