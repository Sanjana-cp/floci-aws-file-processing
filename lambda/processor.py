import json
import boto3
from datetime import datetime, timezone
from urllib.parse import unquote_plus

ENDPOINT = "http://floci:4566"

s3 = boto3.client(
    "s3",
    endpoint_url=ENDPOINT,
    region_name="us-east-1"
)

dynamodb = boto3.resource(
    "dynamodb",
    endpoint_url=ENDPOINT,
    region_name="us-east-1"
)

table = dynamodb.Table("FileProcessingMetadata")


def lambda_handler(event, context):
    for record in event["Records"]:
        message = json.loads(record["body"])

        if "Records" in message:
            s3_record = message["Records"][0]["s3"]
            bucket = s3_record["bucket"]["name"]
            filename = unquote_plus(s3_record["object"]["key"])
        else:
            bucket = message["bucket"]
            filename = message["file"]

        response = s3.get_object(
            Bucket=bucket,
            Key=filename
        )

        content = response["Body"].read().decode("utf-8")

        word_count = len(content.split())
        character_count = len(content)

        table.put_item(
            Item={
                "file_id": f"{bucket}/{filename}",
                "filename": filename,
                "bucket": bucket,
                "status": "COMPLETED",
                "word_count": word_count,
                "character_count": character_count,
                "processed_at": datetime.now(
                    timezone.utc
                ).isoformat()
            }
        )

        print(f"Processed: {filename}")
        print(f"Words: {word_count}")
        print(f"Characters: {character_count}")

    return {
        "statusCode": 200,
        "body": "Processing completed"
    }
