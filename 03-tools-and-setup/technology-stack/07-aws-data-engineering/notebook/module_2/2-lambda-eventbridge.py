import boto3
from mypy_boto3_lambda import LambdaClient

lambda_client: LambdaClient = boto3.client("lambda")