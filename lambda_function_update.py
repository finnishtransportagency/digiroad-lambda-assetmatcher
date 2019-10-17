import json
import psycopg2
import os
import requests

def lambda_handler(event, context):
    try:
        connection = psycopg2.connect(user = os.environ['RDS_USER'],
                                      password = os.environ['RDS_PASSWORD'],
                                      host = os.environ['RDS_HOST'],
                                      port = os.environ['RDS_PORT'],
                                      database = os.environ['RDS_DATABASE'],
                                      options = f"-c search_path={os.environ['RDS_SCHEMA']}")
        cursor = connection.cursor()
        print("PostgreSQL connection established")

        data = set(eval(event['body'])['DatasetIds'])
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

    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
        if connection:
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")
        return {
            'statusCode': 400,
            'body': json.dumps("Malformed json. Acceptable json format: [<DatasetId>,<DatasetId>,...]")
        }

    try:
        userMessage = {}
        if selectedDatasets:
            othMessage = sendDataSetsToOTH(selectedDatasets, cursor)
            print('AWS-OTH communication finished')

            for datasetId in othMessage:
                userMessage[datasetId] = othMessage[datasetId]

        if alreadyUploadedDatasets:
            userMessage['Already updated'] = alreadyUploadedDatasets

        if nonexistentDatasets:
            userMessage['Nonexistent datasetsIds'] = nonexistentDatasets

        print('Selected: ' + str(selectedDatasets))
        print('Nonexistent: ' + str(nonexistentDatasets))
        print('Already updated: ' + str(alreadyUploadedDatasets))
        connection.commit()
    except Exception as error:
        print("Error while communicating with OTH or updating AWS db", error)
        return {
            'statusCode': 400,
            'body': json.dumps("Could not process Datasets. Verify information provided.")
        }
    finally:
        if connection:
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")

    return {
        'statusCode': 200,
        'body': json.dumps(userMessage)
    }


def sendDataSetsToOTH(selectedDatasets, dataBaseCursor):
    base_url = os.environ['OTH_MUNICIPALITY_API_URL']
    othHeaders = {'Authorization': os.environ['OTH_MUNICIPALITY_API_AUTH'], 'Content-Type': 'application/json'}
    print('Sending datasets to OTH')

    response = requests.put(base_url, json=selectedDatasets, headers=othHeaders)
    print('Response fetched')
    if response.status_code == 200:
        return storeOTHResponse(response, dataBaseCursor)
    else:
        raise Exception(response)


def storeOTHResponse(othResponse, dataBaseCursor):
    print('Storing response from OTH')
    datasetsStatus = othResponse.json()

    for dataset in datasetsStatus:
        print("Updating status of " + dataset.get("DataSetId"))
        updateDatasetStatus = "UPDATE datasets SET update_finished = CURRENT_TIMESTAMP, error_log = %s WHERE dataset_id = %s;"
        status = dataset.get("Status")
        if status == "Processed successfuly" or status == "Amount of features and roadlinks do not match":
            updateVariables = (status, dataset.get("DataSetId"))
        else:
            updateVariables = (dataset.get("Features with errors"), dataset.get("DataSetId"))
        dataBaseCursor.execute(updateDatasetStatus, updateVariables)

    return datasetsStatus
