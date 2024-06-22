import json
import argparse
from openpyxl  import load_workbook
from openpyxl.workbook.workbook import Workbook
from openpyxl.worksheet.worksheet import Worksheet
from openpyxl.cell.cell import Cell
import pandas as pd
from typing import Generator
from enum import Enum
import boto3
from io import BytesIO

from statsheet.statsheet import *
from statsheet.handler import StatsheetHandler
import os

MAIN_BUCKET = os.environ['DATA_LAKE_BUCKET']
REFRESH_LAMBDA_NAME = os.environ.get('REFRESH_LAMBDA','quadball-data-lake-refresh')


s3 = boto3.client('s3')
lbd = boto3.client('lambda')
def extract_name(filepath:str) -> str: 
    return filepath.split('/')[-1].split('.xlsx')[0]

def write_json_data(data, filepath:str, title:str):
    bytes = json.dumps(data).encode('utf-8')
    s3.put_object(Body = bytes, Bucket = MAIN_BUCKET, Key = f"{filepath}/{title}.json")
    

    
def process_record(record):
    bucket = record['s3']['bucket']['name']
    key = record['s3']['object']['key']
    
    title = extract_name(key)
    obj = s3.get_object(Bucket = bucket,Key =key)
    bytes = BytesIO(obj['Body'].read())
    ssh = StatsheetHandler(bytes)
    raw_poss = [poss.to_dict() for poss in ssh.possessions]
    
    
    write_json_data(raw_poss,'possessions/raw',title)
    

    hyd = [poss.to_dict() for poss in ssh.get_hydrated()]
    

    tr_name = ssh.get_translator_by_name()
    tr_id = ssh.get_translator_by_id()
    

    id_poss = [poss.translate(tr_id) for poss in ssh.possessions]
    
    mdata = ssh.metadata.__dict__
    OUTPUT_PATHS = {
        'possessions/raw': raw_poss,
        'possessions/hydrated':hyd,
        'possessions/relational':id_poss,
        'rosters/by_name':{'-'.join(k) if type(k)==tuple else k: v for k,v in tr_name.items()},
        'rosters/by_id':{'-'.join(k) if type(k)==tuple else k: v for k,v in tr_id.items()},
        'game-metadata': mdata
    }
    
    for path, data in OUTPUT_PATHS.items(): 
        print(f"Exporting Path: {path}")
        write_json_data(data, path, title)
    
    
def lambda_handler(event, context):
    print(context)
    print(event)
    # TODO implement
    for record in event['Records']:
        process_record(record)
    print("ALL Files processed - Invoking SF data lake refresh")
    lbd.invoke(
        FunctionName = REFRESH_LAMBDA_NAME,
        InvocationType = 'RequestResponse',                  # necessary?
        Payload = json.dumps({}).encode('utf-8')
    )
    print('Invoke Successful')
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
