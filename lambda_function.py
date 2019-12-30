import os
import sys

# Way found to put all packages on a folder and import them. We should try to put this in a __init__.py file somehow
root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, root + "/packages")

import json
import psycopg2
import uuid
import jsonSchemaValidator


def lambda_handler(event, context):
    try:
        connection = psycopg2.connect(user=os.environ['RDS_USER'],
                                      password=os.environ['RDS_PASSWORD'],
                                      host=os.environ['RDS_HOST'],
                                      port=os.environ['RDS_PORT'],
                                      database=os.environ['RDS_DATABASE'],
                                      options=f"-c search_path={os.environ['RDS_SCHEMA']}")
        cursor = connection.cursor()
        print("PostgreSQL connection established")

        data = event['body']
        json_errors = validate_geojson(json.loads(data))

        if json_errors:
            return {
                'statusCode': 400,
                'body': json.dumps(json_errors)
            }

        datasetId = str(uuid.uuid4())
        print("DatasetId: " + datasetId)

        insertDataset = "INSERT INTO datasets(dataset_id, json_data, upload_executed) VALUES(%s, %s, CURRENT_TIMESTAMP);"
        insertVariables = (datasetId, data)
        cursor.execute(insertDataset, insertVariables)
        print("Insert dataset into PostgreSQL")

        matchingScript = open("matching_script.sql", "r").read()
        cursor.execute(matchingScript, (datasetId,))
        print("Matching script executed")

        connection.commit()
    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
        return {
            'statusCode': 400,
            'body': json.dumps(
                "Malformed geojson. Check geojson. In addition to the xy-coordinate pairs, all delivered information "
                "must have the name of the road (if available), and information whether it is a road, or used as a "
                "cycling or walking path.")
        }
    finally:
        if connection:
            cursor.close()
            connection.close()
            print("PostgreSQL connection closed")

    return {
        'statusCode': 200,
        'body': json.dumps({"DatasetId": datasetId})
    }


def validate_geojson(json):
    errors = jsonSchemaValidator.validate_json(json)
    json_response_errors = {}

    if errors:
        for feature_number, error_message in errors:
            if feature_number == 0:
                json_response_errors["Error"] = error_message
            else:
                json_response_errors["Feature " + str(feature_number)] = error_message

        print(json_response_errors)
        return json_response_errors
