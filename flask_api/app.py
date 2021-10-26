import os
import uuid
import boto3
import json
import boto3
from boto3.dynamodb.conditions import Key
from datetime import date, timedelta, datetime

from flask import request, jsonify
from flask_lambda import FlaskLambda

#EXEC_ENV = os.environ['EXEC_ENV']
#REGION = os.environ['REGION_NAME']
#TABLE_NAME = os.environ['TABLE_NAME']

app = FlaskLambda(__name__)

#if EXEC_ENV == 'local':
#    dynamodb = boto3.resource('dynamodb', endpoint_url='http://dynamodb:8000')
#else:
#    dynamodb = boto3.resource('dynamodb', region_name=REGION)



@app.route('/hello', methods=('GET',))
def say_hello():
    return jsonify("Hello World")

@app.route('/fetch-s3-buckets', methods=('GET',))
def fetch_s3_buckets():
    s3 = boto3.resource('s3')
    buckets = [bucket.name for bucket in s3.buckets.all()]
    print(buckets)
    return jsonify(buckets)

@app.route('/fetch-cloudwatch-metrics', methods=('GET',))
def fetch_cloudwatch_metrics():
    days = 0
    yesterday=date.today() - timedelta(days=days)
    tomorrow=date.today() + timedelta(days=1)

    client = boto3.client('cloudwatch')
    response = client.get_metric_data(
        MetricDataQueries=[
            {
                'Id': 'getMetricData',
                'MetricStat': {
                    'Metric': {
                        'Namespace': 'AmazonMWAA',
                        'MetricName': 'SchedulerHeartbeat',
                        'Dimensions': [
                            {
                              "Name": "Function",
                              "Value": "Scheduler"
                            },
                            {
                              "Name": "Environment",
                              "Value": "csx-nonprod-dataops"
                            },
                        ]
                    },
                    'Period': 60 * 60,
                    'Stat': 'Sum',
                  },
                'Label': 'human-label',
                'ReturnData': True,
            },
        ],
        StartTime=datetime(yesterday.year, yesterday.month, yesterday.day), 
        EndTime=datetime(tomorrow.year, tomorrow.month, tomorrow.day),
        ScanBy='TimestampDescending',
    )
    print(response)
    return jsonify(response)   
