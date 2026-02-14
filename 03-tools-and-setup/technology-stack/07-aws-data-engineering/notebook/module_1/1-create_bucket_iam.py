import boto3
from mypy_boto3_s3 import S3Client
from mypy_boto3_iam import IAMClient
import logging
from botocore.exceptions import ClientError
from typing import Literal

s3 : S3Client = boto3.client("s3")

def create_bucket(name,region: Literal["ap-southeast-1"] = "ap-southeast-1"):
    try:
        s3.head_bucket(Bucket=name)
        print("f Bucket {name} is already exist")
    except ClientError as e:
        error_code = e.response.get("Error",{}).get("Code")
        if error_code == '404':
            s3.create_bucket(
                Bucket=name,
                CreateBucketConfiguration={
                    'LocationConstraint': region
                }
            )

            print(f"S3 bucket {name} created in {region}")
        else:
            logging.error(e)

iam: IAMClient = boto3.client("iam")

def create_user(name):
    try:
        iam.get_user(UserName=name)
        print(f"User {name} is already exist")
    except ClientError as e:
        error_code = e.response.get("Error",{}).get("Code")
        if error_code == 'NoSuchEntity':
            iam.create_user(UserName=name)
            print(f"User {name} created successfully")
        else:
            logging.error(e)

create_bucket("bucket-latihan-sanju-aws-3291")
create_user("user-latihan")