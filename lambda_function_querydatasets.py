import json
import psycopg2
import os

def lambda_handler(event, context):
    try:
        connection = psycopg2.connect(user = os.environ['RDS_USER'],
                                      password = os.environ['RDS_PASSWORD'],
                                      host = os.environ['RDS_HOST'],
                                      port = os.environ['RDS_PORT'],
                                      database = os.environ['RDS_DATABASE'],
                                      options=f"-c search_path={os.environ['RDS_SCHEMA']}")
        cursor = connection.cursor()
        print("PostgreSQL connection established")

        datasetIds = event['multiValueQueryStringParameters']['id']
        withGeojson = 'no'
        if 'withgeojson' in event['multiValueQueryStringParameters']:
            withGeojson = event['multiValueQueryStringParameters']['withgeojson'][0]

        datasetsInfo = []
        nonexistentDatasets = []

        for datasetId in datasetIds:
            print("Checking if dataset with datasetId " + datasetId + " exists")
            if withGeojson == 'yes':
                getDatasetInfo = "SELECT json_data FROM datasets WHERE dataset_id = %s"
            else:
                getDatasetInfo = "SELECT matched_roadlinks, matching_rate, to_char(upload_executed, 'HH24:MI:SS DD-MM-YYYY'), to_char(update_finished, 'HH24:MI:SS DD-MM-YYYY'), error_log FROM datasets WHERE dataset_id = %s"

            cursor.execute(getDatasetInfo, (datasetId,))
            result = cursor.fetchall()

            if result:
                result = result[0]
                resultInfo = {}
                if withGeojson == 'yes':
                    resultInfo["GeoJson"] = result[0]
                else:
                    resultInfo["Matched roadlinks"] = result[0]
                    resultInfo["Matched rate"] = result[1]
                    resultInfo["Upload executed"] = result[2]
                    resultInfo["Update finished"] = result[3]
                    resultInfo["Error log"] = result[4]

                print("Information about dataset with datasetId " + datasetId + " fetched")
                DatasetIdResultDict = {"DatasetId": {datasetId: resultInfo}}
                datasetsInfo.append(DatasetIdResultDict)
            else:
                nonexistentDatasets.append(datasetId)

        print(datasetsInfo)
        if nonexistentDatasets:
            datasetsInfo.append({'Nonexistent datasetsIds': nonexistentDatasets})

        print('datasetsInfo: ' + str(datasetsInfo))
        print('nonexistentDatasets: ' + str(nonexistentDatasets))
    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
        return {
            'statusCode': 400,
            'body': json.dumps("Bad request. Verify ids provided. Acceptable URL format example: .../queryDatasets?id=***&id=***&id=***&withgeojson=yes")
        }
    finally:
        if connection:
            cursor.close()
            connection.close()
            print("PostgreSQL connection closed")

    return {
        'statusCode': 200,
        'body': json.dumps(datasetsInfo)
    }
