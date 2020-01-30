const { Client } = require('pg');
import matching_script from './matching_script';

// These are the datacolumns in datasets table (json_data exluded)
const data_columns = `
dataset_id, 
matched_roadlinks, 
matching_rate, 
upload_executed, 
update_finished, 
status_log
`;

export async function uploadGeoJSON(userId, geojson) {
  const client = new Client();
  try {
    client.connect();

    const result = await client.query(
      `
    INSERT INTO datasets (user_id, json_data, upload_executed)
    VALUES ($1, $2, CURRENT_TIMESTAMP) RETURNING dataset_id`,
      [userId, geojson]
    );
    return result.rows[0].dataset_id;
  } catch (exception) {
    throw new Error('Database connection error');
  } finally {
    client.end();
  }
}

export async function getDatasetById(id, fetchGeoJSON = false) {
  const client = new Client();
  try {
    client.connect();

    const attributes = fetchGeoJSON ? data_columns + ', json_data' : data_columns;

    let result;
    if (Array.isArray(id)) {
      result = await client.query(
        `
      SELECT ${attributes} 
      FROM datasets
      WHERE dataset_id IN ('${id.join("','")}');`
      );
    } else {
      result = await client.query(
        `
      SELECT ${attributes} 
      FROM datasets
      WHERE dataset_id = $1;`,
        [id]
      );
    }

    return result.rows;
  } catch (exception) {
    throw new Error('Database connection error');
  } finally {
    client.end();
  }
}

export async function fetchTenNewestDatasets() {
  const client = new Client();
  try {
    client.connect();

    const result = await client.query(
      `
      SELECT ${data_columns} 
      FROM datasets
      ORDER BY upload_executed DESC LIMIT 10
      `
    );

    return result.rows;
  } catch (exception) {
    throw new Error('Database connection error');
  } finally {
    client.end();
  }
}

export async function fetchUsersDatasets(userId) {
  const client = new Client();
  try {
    client.connect();

    const result = await client.query(
      `
      SELECT ${data_columns} 
      FROM datasets
      WHERE user_id = $1
      `,
      [userId]
    );

    return result.rows;
  } catch (exception) {
    throw new Error('Database connection error');
  } finally {
    client.end();
  }
}

export async function executeMatchingScript(id) {
  const client = new Client();
  try {
    client.connect();
    const query = matching_script(id);
    await client.query(query);
    return { message: 'Matching script runned successfully' };
  } catch (exeption) {
    console.log('Error while executing matching script', exeption);
    return 'Error while executing matching script';
  } finally {
    client.end();
  }
}
