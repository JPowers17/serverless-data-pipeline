# Serverless Data Processing Pipeline

## Overview

For this project, a lightweight, fully serverless pipeline was built that automatically records file-upload metadata from Amazon S3 into Amazon DynamoDB using AWS Lambda and Python. AWS CloudWatch captured logs for troubleshooting. ChatGPT was used to produce the JSON and Python code, for educational purposes only.

## Workflow

A CSV file is uploaded to an S3 bucket.

1. The upload event automatically triggers a Lambda function.

2. The Lambda function extracts metadata (filename, size, timestamp, etc.) and writes it to a DynamoDB table.

3. CloudWatch Logs capture every invocation for monitoring and debugging.

### AWS Services Used

| **Service**            | **Purpose** |
|--------------------------|----------------------|
| Amazon S3                | Object storage, source of event trigger |
| AWS Lambda               | Serverless compute for event processing |
| Amazon DynamoDB          | NoSQL database to store metadata |
| Amazon CloudWatch        | Logging & monitoring |
| AWS IAM                  | Access control and execution roles |

### Project Architecture

User uploads a CSV file → S3 bucket (ObjectCreated) → Lambda (Python, Boto3) → DynamoDB (file metadata) → CloudWatch Logs

## Lessons Learned

- Designing a simple, scalable, zero-server architecture.

- How S3 event notifications can trigger Lambda automatically.

- Using environment variables for dynamic configuration.

- Observing real-time logs in CloudWatch.

- Structuring IAM policies with least privilege.

## Repository Structure

```
serverless-data-pipeline/
├─ .gitignore
├─ LICENSE
├─ README.md
├─ iam_policy.json
├─ lambda_function.py
├─ setup_instructions.md
```

## Tags

AWS Lambda • Amazon S3 • Amazon DynamoDB • CloudWatch • Serverless Architecture • Event-Driven Computing • Python • Cloud Automation • Infrastructure as Code • Data Pipeline