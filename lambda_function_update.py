import json
import psycopg2

# Filename changed because github pulls will override the "original" file
# (Both files are "lambda_function" but for two different methods (/convert, /update))
# Important to change the filename to "lamba_function.py" after you send it to aws and delete the one you do not need it
def lambda_handler(event, context):
    try:
        connection = psycopg2.connect(user = os.environ['RDS_USER'],
                                      password = os.environ['RDS_PASSWORD'],
                                      host = os.environ['RDS_HOST'],
                                      port = os.environ['RDS_PORT'],
                                      database = os.environ['RDS_DATABASE'])
        connection.set_isolation_level(0)
        cursor = connection.cursor()
        data = eval(event['body'])

        selectedDatasets = []
        for datasetId in data:
            getDataset = "SELECT dataset_id, json_data, matched_roadlinks FROM datasets WHERE dataset_id = %s;"
            cursor.execute(getDataset, (datasetId,))
            result = cursor.fetchall()
            if result:
                selectedDatasets.append(result)

    except (Exception, psycopg2.Error) as error :
        print ("Error while connecting to PostgreSQL", error)
    finally:
        #closing database connection.
        if(connection):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")

    return {
        'statusCode': 200,
        'body': json.dumps(selectedDatasets)    # Returning selectedDatasets for testing only
    }
