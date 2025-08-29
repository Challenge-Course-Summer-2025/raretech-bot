import boto3

from app.core.config import settings

db = boto3.resource(
    "dynamodb",
    region_name=settings.AWS_REGION,
    endpoint_url=settings.DYNAMODB_ENDPOINT,
)
