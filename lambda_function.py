import json
import psycopg2
import uuid

def lambda_handler(event, context):
    try:
        connection = psycopg2.connect(user = os.environ['RDS_USER'],
                                      password = os.environ['RDS_PASSWORD'],
                                      host = os.environ['RDS_HOST'],
                                      port = os.environ['RDS_PORT'],
                                      database = os.environ['RDS_DATABASE'])
        connection.set_isolation_level(0)
        cursor = connection.cursor()

        data = event['body']
        datasetId = str(uuid.uuid4())

        insertDataset = "INSERT INTO datasets(dataset_id, json_data) VALUES(%s, %s);"
        insertVariables = (datasetId, data)
        cursor.execute(insertDataset, insertVariables)

        matchingScript = open("matching_script.sql", "r").read()
        cursor.execute(matchingScript, (datasetId,))
    except (Exception, psycopg2.Error) as error:
        print ("Error while connecting to PostgreSQL", error)
    finally:
        # closing database connection.
        if (connection):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")

    return {
        'statusCode': 200,
        'body': json.dumps(datasetId)
    }