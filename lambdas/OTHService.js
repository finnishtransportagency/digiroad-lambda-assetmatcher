import axios from 'axios';

const apiEndpoint = process.env.OTH_MUNICIPALITY_API_URL;
const OTHCredentials = process.env.OTH_MUNICIPALITY_API_AUTH;

export async function uploadToOTH(data) {
  return axios.put(apiEndpoint, JSON.stringify(data), {
    headers: {
      Authorization: OTHCredentials,
      'Content-Type': 'application/json; charset=UTF-8'
    }
  });
}
