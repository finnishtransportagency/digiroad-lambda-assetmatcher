import json
import psycopg2
import base64


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
        insert_query="INSERT into datasets (json_data) values ('%s')" %(data)
        cursor.execute(insert_query)
        script=open("matching_script.sql","r").read()
        cursor.execute(script)
        fetch_query="SELECT edges FROM temp_points limit 1;"
        cursor.execute(fetch_query)
        result=cursor.fetchall()
        truncate_query="truncate temp_points;"
        cursor.execute(truncate_query)
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
        'body': json.dumps(result[0])
        }
