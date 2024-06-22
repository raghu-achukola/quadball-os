import json
import snowflake.connector as snowcon
import boto3
import os


creds_secret = os.environ['SNOWFLAKE_CREDS_SECRET']
sm = boto3.client('secretsmanager',region_name = 'us-west-2')
conn_kwargs = json.loads(sm.get_secret_value(SecretId = creds_secret)['SecretString'])

WH_QUERY = "use warehouse compute_wh"
QUERY = "call quadball.reporting.refresh_data_lake();"

def lambda_handler(event, context):
    conn = snowcon.connect(**conn_kwargs)
    print('SF - Connection Successful')
    cur = conn.cursor()
    cur.execute(WH_QUERY)
    cur.execute(QUERY)
    conn.close()
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
