import json
import psycopg2
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

        data = set(eval(event['body']))
        nonexistentDatasets = []
        alreadyUploadedDatasets = []
        selectedDatasets = []

        for datasetId in data:
            print("Checking if dataset with datasetId " + datasetId + " exists")
            getDataset = "SELECT dataset_id FROM datasets WHERE dataset_id = %s;"
            cursor.execute(getDataset, (datasetId,))
            result = cursor.fetchall()

            if result:
                print("Checking if dataset with datasetId " + datasetId + " was already updated")
                getDataset = "SELECT dataset_id, json_data, matched_roadlinks FROM datasets WHERE dataset_id = %s AND update_finished IS NULL;"
                cursor.execute(getDataset, (datasetId,))
                result = cursor.fetchall()

                if result:
                    selectedDatasets.append(result)
                    print("Dataset with datasetId " + datasetId + " ready to be send!")
                else:
                    alreadyUploadedDatasets.append(datasetId)
            else:
                nonexistentDatasets.append(datasetId)

        print('Selected: ' + str(selectedDatasets))
        print('Nonexistent: ' + str(nonexistentDatasets))
        print('Already updated: ' + str(alreadyUploadedDatasets))
    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
        return {
            'statusCode': 400,
            'body': json.dumps("Malformed json. Acceptable json format: [<DatasetId>,<DatasetId>,...]")
        }
    finally:
        if(connection):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")

    return {
        'statusCode': 200,
        'body': json.dumps(selectedDatasets)
    }