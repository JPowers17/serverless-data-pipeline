Can all be done in the Console.

- Create the S3 Bucket
  - Name: data-ingest-pipeline-yourname

- Create the DynamoDB Table
  - Name: file_metadata
  - Partition Key: filename (String)

- Create the IAM Role for Lambda
  - Trusted Entity Type: AWS Service
  - Use Case: Lambda
  - Role Name: LambdaS3DynamoDBRole
  - Policy Name: LambdaS3DynamoDBPolicy
  - Attach or copy and paste the iam_policy.json inline policy file
  - Replace placeholders with your bucket name, region, and account ID

- Create and Deploy the Lambda Function
  - Name: process_s3_upload
  - Runtime: Python 3.12
  - Under Change Default Execution Role, select Use an Existing Role and select LambdaS3DynamoDBRole
  - After creation, click on the function
  - Under Code, attach or copy and paste the lambda_function.py file
  - Under Configuration, click on Environmental Variables
  - Add: TABLE_NAME = file_metadata and FETCH_OBJECT = false
  - Click Deploy

- Create the S3 Event Trigger
  - Click on data-ingest-pipeline-yourname bucket
  - Click on Properties, then Event Notifications
  - Name: LambdaFileUploadTrigger
  - Under Event Types, check All Object Create Events
  - Under Specify Lambda Function, select process_s3_upload

- Test the Function
  - Upload a test file to the S3 bucket, e.g. test.csv
  - In CloudWatch, check Log Groups for /aws/lambda/process_s3_upload
  - In DynamoDB, look for the test file

- Some Extra Ideas to Add
  - Add an API Gateway endpoint to query DynamoDB items and return results
  - Add SNS notifications to confirm successful processing
  - Use S3 object tags or add a processed prefix, e.g.processed/ to mark processed objects

- Cost and Cleanup
  - DynamoDB: small table on on-demand or free tier
  - Lambda: free up to 1M requests/month + compute time
  - S3: small storage costs for test files
  - Cleanup: delete Lambda, S3 bucket and contents, DynamoDB table, and IAM role