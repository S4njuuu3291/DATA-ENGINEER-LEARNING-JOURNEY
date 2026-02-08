# Module 2 Exercises: AWS Lambda & EventBridge

Hands-on practice for serverless data processing and event-driven pipelines.

> **Estimated Total Time:** 4 hours  
> **Difficulty:** ⭐⭐⭐ Intermediate  
> **Prerequisites:** Module 1 (S3 + IAM + VPC)

---

## 🧰 Setup Checklist (Before Starting)

- [ ] AWS CLI configured (`aws configure`)
- [ ] S3 bucket exists (from Module 1)
- [ ] Sample data uploaded to `bronze/`
- [ ] IAM permissions: `lambda:*`, `iam:*`, `events:*`, `s3:*`, `logs:*`
- [ ] Region set (use one region consistently, e.g., `us-east-1`)

---

## ✅ Exercise 1: Create Hello World Lambda (15 min)

**Goal:** Create your first Lambda function and invoke it.

**Steps:**
1. Create execution role:
   ```bash
   aws iam create-role \
     --role-name lambda-basic-role \
     --assume-role-policy-document file://trust-policy.json
   ```
2. Attach AWS managed policy:
   ```bash
   aws iam attach-role-policy \
     --role-name lambda-basic-role \
     --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
   ```
3. Create Lambda function (Python):
   ```bash
   aws lambda create-function \
     --function-name hello-world \
     --runtime python3.11 \
     --role arn:aws:iam::ACCOUNT:role/lambda-basic-role \
     --handler lambda_function.lambda_handler \
     --zip-file fileb://hello-world.zip
   ```
4. Invoke Lambda:
   ```bash
   aws lambda invoke \
     --function-name hello-world \
     --payload '{"message":"hello"}' \
     response.json
   ```

**Deliverable:** `response.json` contains `Hello from Lambda`.

---

## ✅ Exercise 2: CSV Validation Lambda (30 min)

**Goal:** Process S3 CSV file and validate schema.

**Steps:**
1. Upload `orders.csv` to bronze:
   ```bash
   aws s3 cp ../data/raw/ecommerce/2024-01-15/orders.csv \
     s3://<your-bucket>/bronze/orders/2024-01-15/orders.csv
   ```
2. Create Lambda function `csv-validator` using sample code:
   - Use [data/lambda-code/csv_validator.py](../data/lambda-code/csv_validator.py)
3. Deploy function with pandas layer (see Exercise 3).
4. Test Lambda with S3 event payload (sample in `event_s3.json`).

**Deliverable:**
- Logs show `rows_processed` and output path
- Silver file written: `s3://<bucket>/silver/orders/2024-01-15/orders.parquet`

---

## ✅ Exercise 3: Lambda Layers for Pandas (25 min)

**Goal:** Create a reusable layer for pandas to reduce package size.

**Steps:**
1. Build layer locally:
   ```bash
   cd ../data/lambda-code/layer
   ./build_layer.sh
   ```
2. Publish layer:
   ```bash
   aws lambda publish-layer-version \
     --layer-name pandas-layer \
     --zip-file fileb://pandas-layer.zip \
     --compatible-runtimes python3.11
   ```
3. Attach layer to `csv-validator` function:
   ```bash
   aws lambda update-function-configuration \
     --function-name csv-validator \
     --layers arn:aws:lambda:REGION:ACCOUNT:layer:pandas-layer:1
   ```

**Deliverable:** Lambda runs successfully with pandas imported from layer.

---

## ✅ Exercise 4: Error Handling + DLQ (20 min)

**Goal:** Send failed events to DLQ (SQS) and inspect them.

**Steps:**
1. Create SQS DLQ:
   ```bash
   aws sqs create-queue --queue-name csv-validator-dlq
   ```
2. Attach DLQ to Lambda:
   ```bash
   aws lambda update-function-configuration \
     --function-name csv-validator \
     --dead-letter-config TargetArn=arn:aws:sqs:REGION:ACCOUNT:csv-validator-dlq
   ```
3. Upload a malformed CSV to trigger error.
4. Check DLQ:
   ```bash
   aws sqs receive-message --queue-url <DLQ_URL>
   ```

**Deliverable:** Failed S3 event appears in DLQ.

---

## ✅ Exercise 5: EventBridge Schedule (15 min)

**Goal:** Trigger Lambda every 5 minutes.

**Steps:**
1. Create EventBridge rule:
   ```bash
   aws events put-rule \
     --name lambda-schedule-test \
     --schedule-expression "rate(5 minutes)"
   ```
2. Add Lambda target:
   ```bash
   aws events put-targets \
     --rule lambda-schedule-test \
     --targets Id=1,Arn=arn:aws:lambda:REGION:ACCOUNT:function:hello-world
   ```
3. Grant permission:
   ```bash
   aws lambda add-permission \
     --function-name hello-world \
     --statement-id allow-eventbridge \
     --action lambda:InvokeFunction \
     --principal events.amazonaws.com \
     --source-arn arn:aws:events:REGION:ACCOUNT:rule/lambda-schedule-test
   ```

**Deliverable:** CloudWatch logs show function invoked every 5 minutes.

---

## ✅ Exercise 6: EventBridge Filtering (20 min)

**Goal:** Trigger Lambda only for `.csv` in `bronze/orders/`.

**Steps:**
1. Create EventBridge rule with event pattern:
   ```bash
   aws events put-rule \
     --name s3-csv-filter \
     --event-pattern '{
       "source": ["aws.s3"],
       "detail-type": ["Object Created"],
       "detail": {
         "bucket": {"name": ["<your-bucket>"]},
         "object": {
           "key": [{"prefix": "bronze/orders/", "suffix": ".csv"}]
         }
       }
     }'
   ```
2. Add Lambda target (`csv-validator`).
3. Upload files:
   - `bronze/orders/test.csv` → should trigger
   - `bronze/customers/test.csv` → should NOT trigger

**Deliverable:** Only matching files trigger Lambda.

---

## ✅ Exercise 7: End-to-End Bronze → Silver Pipeline (30 min)

**Goal:** Full pipeline with validation + transformation.

**Steps:**
1. Upload new file to bronze.
2. EventBridge triggers Lambda.
3. Lambda validates and writes to silver.
4. Verify output in silver:
   ```bash
   aws s3 ls s3://<bucket>/silver/orders/2024-01-15/
   ```

**Deliverable:** Parquet file exists in silver.

---

## ✅ Exercise 8: Fan-Out Pattern (25 min)

**Goal:** One S3 upload triggers multiple Lambdas.

**Steps:**
1. Create 3 simple Lambdas:
   - `validate-csv`
   - `update-catalog` (placeholder log)
   - `notify-team` (placeholder log)
2. Create EventBridge rule for S3 upload.
3. Attach all 3 Lambdas as targets (fan-out).
4. Upload a file.

**Deliverable:** All 3 Lambdas triggered (check CloudWatch logs).

---

## ✅ Completion Checklist

- [ ] Hello World Lambda created and invoked
- [ ] CSV validator processes S3 file
- [ ] Pandas Layer published and attached
- [ ] DLQ receives failed event
- [ ] EventBridge schedule works
- [ ] EventBridge filter works
- [ ] End-to-end Bronze → Silver pipeline works
- [ ] Fan-out triggers multiple Lambdas

---

**Next:** Continue to Module 3 (Glue Data Catalog).
