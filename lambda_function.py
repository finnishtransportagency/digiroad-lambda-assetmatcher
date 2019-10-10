import json
import psycopg2
import uuid
import os

def lambda_handler(event, context):
    try:
        connection = psycopg2.connect(user = os.environ['RDS_USER'],
                                      password = os.environ['RDS_PASSWORD'],
                                      host = os.environ['RDS_HOST'],
                                      port = os.environ['RDS_PORT'],
                                      database = os.environ['RDS_DATABASE'])
        cursor = connection.cursor()
        print("PostgreSQL connection established")

        data = event['body']
        datasetId = str(uuid.uuid4())

        insert_query="INSERT INTO datasets(dataset_id, json_data, upload_executed) VALUES(%s, %s, CURRENT_TIMESTAMP);"
        insertVariables = (datasetId, data)
        cursor.execute(insert_query, insertVariables)
        print("Inserted dataset into PostgreSQL")

        matchingScript = open("matching_script.sql", "r").read()
        cursor.execute(matchingScript, (datasetId,))
        print("Matching script executed")

        connection.commit()
    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
        return {
            'statusCode': 400,
            'body': json.dumps("Malformed geojson. Check geojson.")
        }
    finally:
        if connection:
            cursor.close()
            connection.close()
            print("PostgreSQL connection closed")

    return {
        'statusCode': 200,
        'body': json.dumps(datasetId)
    }