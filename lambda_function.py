import os
import json
import logging
import boto3
from datetime import datetime
from botocore.exceptions import ClientError

# Configure logging: CloudWatch receives stdout/stderr; logging module is fine
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Read environment variables (set these in Lambda configuration)
TABLE_NAME = os.environ.get("TABLE_NAME", "file_metadata")
FETCH_OBJECT = os.environ.get("FETCH_OBJECT", "false").lower() == "true"

# AWS clients (reuse across invocations)
s3 = boto3.client("s3")
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(TABLE_NAME)

def extract_metadata_from_record(record):
    """Return (bucket, key, size, etag) from the S3 event record"""
    s3_info = record.get("s3", {})
    bucket = s3_info.get("bucket", {}).get("name")
    obj = s3_info.get("object", {})
    key = obj.get("key")
    size = obj.get("size", 0)
    etag = obj.get("eTag")
    return bucket, key, size, etag

def parse_csv_content(content_bytes):
    """Simple CSV parsing example. Returns list of rows (as lists)."""
    try:
        text = content_bytes.decode("utf-8")
    except UnicodeDecodeError:
        text = content_bytes.decode("latin-1", errors="replace")
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    rows = [line.split(",") for line in lines]
    return rows

def put_metadata_item(filename, bucket, size, etag, extra=None):
    """Write item to DynamoDB"""
    item = {
        "filename": filename,
        "bucket": bucket,
        "size": int(size),
        "etag": etag or "unknown",
        "uploaded_at": datetime.utcnow().isoformat() + "Z"
    }
    if extra:
        item["extra"] = extra
    try:
        table.put_item(Item=item)
        logger.info("Wrote metadata to DynamoDB for %s", filename)
    except ClientError as e:
        logger.exception("Failed to write to DynamoDB: %s", e)
        raise

def lambda_handler(event, context):
    logger.info("Received event: %s", json.dumps(event))
    records = event.get("Records", [])
    responses = []
    for record in records:
        try:
            bucket, key, size, etag = extract_metadata_from_record(record)
            logger.info("Processing s3://%s/%s (size=%s)", bucket, key, size)

            extra = None
            if FETCH_OBJECT:
                # Example: fetch small object and parse if CSV/JSON
                try:
                    resp = s3.get_object(Bucket=bucket, Key=key)
                    body = resp["Body"].read()
                    content_type = resp.get("ContentType", "")
                    logger.info("Fetched object, ContentType=%s", content_type)
                    if key.lower().endswith(".csv") or "text/csv" in content_type:
                        rows = parse_csv_content(body)
                        extra = {"rows_count": len(rows)}
                    elif key.lower().endswith(".json") or "application/json" in content_type:
                        try:
                            parsed = json.loads(body.decode("utf-8"))
                            # store only lightweight summary
                            extra = {
                                "json_keys": list(parsed.keys())[:10] if isinstance(parsed, dict) else None
                            }
                        except Exception:
                            extra = {"json_parse_error": True}
                except ClientError as e:
                    logger.exception("Failed to fetch object from S3: %s", e)
                    # continue and still store metadata
            # Write record to DynamoDB
            put_metadata_item(filename=key, bucket=bucket, size=size, etag=etag, extra=extra)
            responses.append({"filename": key, "status": "ok"})
        except Exception as e:
            logger.exception("Error processing record: %s", e)
            responses.append({"error": str(e)})
    return {
        "statusCode": 200,
        "body": json.dumps(responses)
    }
