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

@app.route('/fetch-specific-cloudwatch-metrics', methods=('GET',))
def fetch_specific_cloudwatch_metrics():
    days = 0
    yesterday=date.today() - timedelta(days=days)
    tomorrow=date.today() + timedelta(days=1)

    client = boto3.client('cloudwatch')
    response = client.get_metric_data(
        MetricDataQueries=[
            {
                'Id': 'getSpecificMetricData',
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

@app.route('/fetch-cloudwatch-metrics', methods=('POST',))
def fetch_cloudwatch_metrics():
    if 'namespace' not in request.args or 'metricName' not in request.args:
      return 'bad request! Namespace or metricName are not specified', 400

    namespace = request.args['namespace'] 
    metricName = request.args['metricName']     
    period = int(request.args['period']) if 'period' in request.args else 60 
    stat = request.args['stat'] if 'stat' in request.args else 'Sum'      
    label = request.args['label'] if 'label' in request.args else 'label'  
    scanBy = request.args['scanBy'] if 'scanBy' in request.args else 'TimestampDescending'  
    previousDays = int(request.args['previousDays']) if 'previousDays' in request.args else 0  
    
    dimensions = request.get_json()

    yesterday=date.today() - timedelta(days=previousDays)
    tomorrow=date.today() + timedelta(days=1)

    client = boto3.client('cloudwatch')
    response = client.get_metric_data(
        MetricDataQueries=[
            {
                'Id': 'getMetricData',
                'MetricStat': {
                    'Metric': {
                        'Namespace': namespace,
                        'MetricName': metricName,
                        'Dimensions': dimensions
                    },
                    'Period': period,
                    'Stat': stat,
                  },
                'Label': label,
                'ReturnData': True,
            },
        ],
        StartTime=datetime(yesterday.year, yesterday.month, yesterday.day), 
        EndTime=datetime(tomorrow.year, tomorrow.month, tomorrow.day),
        ScanBy=scanBy,
    )
    print(response)
    return jsonify(response) 