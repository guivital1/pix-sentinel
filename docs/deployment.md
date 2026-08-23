# Controlled deployment runbook

## Prerequisites

- AWS CLI authenticated to the intended learning account
- AWS SAM CLI
- Region `us-east-2`
- An active account-level budget alert

## 1. Validate locally

```bash
python -m pip install -e '.[dev,aws]'
pytest
sam validate --lint
sam build
```

## 2. Deploy with the kill switch on

```bash
sam deploy --guided
```

Use stack name `pix-sentinel-dev`, region `us-east-2`, and keep `EnableSimulation=false`.

## 3. Start a short evidence session

The safest option is a single manual producer invocation while the schedule remains disabled:

```bash
PRODUCER_NAME=$(aws cloudformation describe-stack-resource \
  --stack-name pix-sentinel-dev \
  --logical-resource-id ProducerFunction \
  --query 'StackResourceDetail.PhysicalResourceId' \
  --output text)

aws lambda invoke \
  --function-name "$PRODUCER_NAME" \
  --cli-binary-format raw-in-base64-out \
  --payload '{}' producer-response.json
```

Alternatively, a time-boxed scheduled demonstration can be enabled explicitly:

```bash
sam deploy \
  --parameter-overrides EnableSimulation=true AlertEmail=YOUR_EMAIL
```

Wait for several batches, then inspect SQS monitoring, the Lambda consumer logs, and the `silver/` S3 prefix.

## 4. Query with Athena

Create a database named `pix_sentinel`, replace the bucket placeholder in `infra/athena.sql`, and run the statements individually. Keep the Athena workgroup scan limit configured before querying.

## 5. Stop and remove

```bash
sam deploy \
  --parameter-overrides EnableSimulation=false AlertEmail=YOUR_EMAIL
aws s3 rm "s3://YOUR_BUCKET" --recursive
sam delete --stack-name pix-sentinel-dev --region us-east-2
```

The S3 bucket must be empty before CloudFormation can remove it. Verify that the stack, queues, functions, log groups, and bucket no longer remain.
