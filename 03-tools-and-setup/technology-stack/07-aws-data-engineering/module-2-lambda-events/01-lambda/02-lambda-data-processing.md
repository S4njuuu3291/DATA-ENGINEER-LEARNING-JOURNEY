# 02: Lambda Data Processing Patterns

> **Duration:** 60 minutes  
> **Difficulty:** ⭐⭐⭐ Intermediate  
> **Key Takeaway:** Production Lambda functions require understanding execution model (cold/warm starts), dependency management (Layers), and idempotency patterns.

---

## 🔄 Lambda Execution Model

### How Lambda Actually Runs Your Code

When AWS receives request to invoke your Lambda:

```
1. Container Initialization ("Cold Start")
   ├─ Download deployment package (your code + dependencies)
   ├─ Start execution environment (runtime: Python 3.11, Node.js 18, etc.)
   ├─ Load dependencies (import pandas, boto3)
   └─ Run initialization code (outside handler function)
      Duration: 100ms - 3 seconds (depends on package size)

2. Handler Execution ("Warm")
   ├─ Run your lambda_handler(event, context) function
   └─ Return result
      Duration: Your code execution time

3. Environment Reuse (if another request arrives soon)
   ├─ Skip step 1 (container still warm!)
   ├─ Rerun step 2 (handler only)
   └─ Much faster: no initialization overhead
```

---

### Cold Start vs Warm Start

**Cold Start:** First invocation or after idle period (>15 min typically)

```python
import pandas as pd  # ← Loaded during cold start (slow)
import boto3

s3 = boto3.client('s3')  # ← Initialized during cold start

def lambda_handler(event, context):
    # This runs on EVERY invocation (cold or warm)
    df = pd.read_csv('data.csv')
    return {'status': 'done'}
```

**Timeline:**
```
Cold Start (first request):
├─ Container init: 500ms
├─ Import pandas: 1,200ms
├─ Handler execution: 300ms
└─ Total: 2,000ms (2 seconds)

Warm Start (subsequent request within 15 min):
├─ Container init: 0ms (reused!)
├─ Import pandas: 0ms (already loaded)
├─ Handler execution: 300ms
└─ Total: 300ms (6x faster!)
```

---

### Optimize for Cold Starts

**Pattern 1: Initialize Outside Handler**

```python
import boto3

# ✅ Good: Initialize client OUTSIDE handler (runs once on cold start)
s3 = boto3.client('s3')
db_connection = None  # Reuse across invocations

def lambda_handler(event, context):
    global db_connection
    
    # Reuse connection if warm
    if db_connection is None:
        db_connection = psycopg2.connect(DB_URL)
    
    # Use connection
    cursor = db_connection.cursor()
    cursor.execute("SELECT * FROM orders")
    return {'rows': cursor.fetchall()}
```

**Why this works:**
- Code outside `lambda_handler` runs ONCE per container (cold start)
- Subsequent invocations reuse `s3` client and `db_connection`
- Saves 100-500ms per invocation

---

**Pattern 2: Lazy Loading (for heavy imports)**

```python
# ❌ Bad: Import heavy library always
import pandas as pd  # 180 MB, takes 1.5 sec to import

def lambda_handler(event, context):
    if event['format'] == 'csv':
        df = pd.read_csv(event['file'])  # Pandas only needed for CSV
    else:
        return process_json(event['file'])  # JSON doesn't need pandas
```

```python
# ✅ Good: Lazy import (only when needed)
def lambda_handler(event, context):
    if event['format'] == 'csv':
        import pandas as pd  # Import ONLY if CSV format
        df = pd.read_csv(event['file'])
    else:
        return process_json(event['file'])
```

**Trade-off:** If CSV format is common, upfront import is better (pay cold start once, fast thereafter).

---

## 💾 Memory & CPU Allocation

### How Memory Affects Performance

**Key insight:** Lambda allocates **CPU proportional to memory**.

| Memory | vCPU | Use Case | Cost Multiplier |
|--------|------|----------|-----------------|
| 128 MB | ~0.08 vCPU | Lightweight API, simple validation | 1x |
| 512 MB | ~0.33 vCPU | CSV processing, small ETL | 4x |
| 1,024 MB (1 GB) | ~0.6 vCPU | Pandas DataFrame operations | 8x |
| 1,792 MB | **1 full vCPU** | Medium data processing | 14x |
| 3,008 MB (3 GB) | ~1.7 vCPU | Large CSV, JSON parsing | 23.5x |
| 10,240 MB (10 GB) | ~6 vCPU | Heavy computation, ML inference | 80x |

**Pricing:** Cost = memory × duration. Doubling memory = 2x cost **BUT** might reduce duration by 2x → same total cost!

---

### Finding Optimal Memory

**Experiment:** Process 50 MB CSV file

```python
import pandas as pd
import time

def lambda_handler(event, context):
    start = time.time()
    
    # Read CSV
    df = pd.read_csv('s3://data-lake/orders.csv')
    
    # Process
    df['processed_date'] = pd.to_datetime(df['date'])
    df = df.drop_duplicates()
    
    duration = time.time() - start
    print(f"Duration: {duration}s, Memory: {context.memory_limit_in_mb}MB")
    
    return {'duration': duration}
```

**Results:**

| Memory | Duration | GB-seconds | Cost | Winner? |
|--------|----------|------------|------|---------|
| 512 MB | 12 sec | 6 GB-sec | $0.0001 | ❌ Slow |
| 1024 MB | 6 sec | 6 GB-sec | $0.0001 | ✅ **Same cost, faster!** |
| 2048 MB | 4 sec | 8 GB-sec | $0.00013 | ❌ More expensive |

**Sweet Spot:** 1024 MB (1 GB) for pandas operations.

**Rule of Thumb:**
- Start with 512 MB
- If execution >10 sec, double memory and test
- Find point where doubling memory doesn't reduce duration proportionally

---

## ⏱️ Timeout Configuration

**Max timeout:** 15 minutes (900 seconds)

**Setting timeout:**
```bash
aws lambda create-function \
  --timeout 300  # 5 minutes
```

**Best Practices:**

1. **Set realistic timeout:** Don't default to 15 min if job finishes in 30 sec
   - Why? Prevents runaway functions (infinite loops costing money)
   - Example: CSV validation should finish in <1 min → set timeout 90 sec

2. **Monitor actual duration:** CloudWatch Logs shows execution time
   ```
   REPORT RequestId: abc-123
   Duration: 1234.56 ms
   Billed Duration: 1300 ms
   Memory Size: 1024 MB
   Max Memory Used: 456 MB
   ```

3. **Handle timeout gracefully:**
   ```python
   def lambda_handler(event, context):
       # Check remaining time
       if context.get_remaining_time_in_millis() < 10000:  # <10 sec left
           print("⚠️ Timeout approaching, saving progress...")
           save_checkpoint()
           raise TimeoutError("Need more time")
   ```

---

## 🌍 Environment Variables

Pass configuration without hardcoding:

```python
import os

# ✅ Good: Configurable via environment variables
BUCKET_NAME = os.environ.get('BUCKET_NAME', 'default-bucket')
DB_HOST = os.environ['DB_HOST']  # Required, will fail if missing
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')

def lambda_handler(event, context):
    print(f"Using bucket: {BUCKET_NAME}")
    # Connect to DB_HOST...
```

**Set via AWS CLI:**
```bash
aws lambda update-function-configuration \
  --function-name csv-processor \
  --environment Variables="{BUCKET_NAME=data-lake,DB_HOST=prod.rds.aws,LOG_LEVEL=DEBUG}"
```

**Security Best Practice:** For secrets (DB passwords, API keys), use **AWS Secrets Manager**:

```python
import boto3
import json

secrets = boto3.client('secretsmanager')

def get_secret(secret_name):
    response = secrets.get_secret_value(SecretId=secret_name)
    return json.loads(response['SecretString'])

def lambda_handler(event, context):
    db_creds = get_secret('prod/db/credentials')
    # db_creds = {'username': 'admin', 'password': 'xxx'}
    
    # Connect to DB with creds...
```

**Cost:** Secrets Manager = $0.40/month per secret + $0.05 per 10,000 API calls.

---

## 📦 Lambda Layers (Sharing Dependencies)

### The Dependency Problem

**Scenario:** You have **5 Lambda functions**, all using pandas.

**Without Layers:**
```
Function 1 (csv-validator):
├─ lambda_code.py (10 KB)
└─ pandas/ (180 MB)
    Total: 180 MB deployment package

Function 2 (json-processor):
├─ lambda_code.py (8 KB)
└─ pandas/ (180 MB)
    Total: 180 MB

... (repeat for 3 more functions)

Total storage: 180 MB × 5 = 900 MB
Upload time: 2 min per deployment × 5 = 10 min
```

**Problem:** Uploading 180 MB pandas for every function is slow & wasteful.

---

### Solution: Lambda Layers

**Layer = Reusable dependency package** shared across functions.

```
Layer: pandas-layer (180 MB)
├─ python/
│   └─ pandas/
└─ (uploaded once, shared by all functions)

Function 1 (csv-validator):
├─ lambda_code.py (10 KB)
└─ [Attached Layer: pandas-layer]
    Deploy size: 10 KB (180x smaller!)

Function 2 (json-processor):
├─ lambda_code.py (8 KB)
└─ [Attached Layer: pandas-layer]
    Deploy size: 8 KB

Total unique storage: 180 MB (layer) + 50 KB (5 functions)
Upload time: 2 min (layer, once) + 5 sec (functions)
```

**Benefits:**
- ✅ Upload dependencies once, reuse everywhere
- ✅ Faster deployments (upload only code changes)
- ✅ Version control layers (rollback if dependency breaks)

---

### Creating a Lambda Layer

**Step 1: Package dependencies**

```bash
# Create folder structure
mkdir -p lambda-layer/python

# Install pandas into layer folder
pip install pandas -t lambda-layer/python/

# Zip layer
cd lambda-layer
zip -r pandas-layer.zip python/
```

**Step 2: Publish layer**

```bash
aws lambda publish-layer-version \
  --layer-name pandas-layer \
  --zip-file fileb://pandas-layer.zip \
  --compatible-runtimes python3.11
```

**Returns:** `LayerVersionArn: arn:aws:lambda:us-east-1:123456789:layer:pandas-layer:1`

**Step 3: Attach to Lambda function**

```bash
aws lambda update-function-configuration \
  --function-name csv-processor \
  --layers arn:aws:lambda:us-east-1:123456789:layer:pandas-layer:1
```

---

### Using Layer in Code

No code changes needed! Import normally:

```python
import pandas as pd  # Loaded from layer

def lambda_handler(event, context):
    df = pd.DataFrame({'a': [1, 2, 3]})
    return {'status': 'ok'}
```

**How it works:**  
Lambda extracts layer contents to `/opt/python/` → Python searches `/opt/python/` for imports.

---

### Layer Best Practices

1. **One layer per major dependency:** `pandas-layer`, `numpy-layer`, `boto3-layer`
2. **Version layers:** Update to `pandas-layer:2` when upgrading pandas
3. **Share layers across AWS account:** Publish layer, give permission to other accounts
4. **Layer size limit:** 250 MB (unzipped), 50 MB (zipped)
   - If pandas (180 MB) + numpy (50 MB) + scipy (80 MB) = 310 MB → split into 2 layers

---

## 🔁 Idempotency (Handling Duplicate Events)

### The Duplicate Event Problem

**Scenario:** File uploaded to S3 triggers Lambda.

**What can go wrong:**

```
1. User uploads file: orders_2024.csv
2. S3 triggers Lambda → processes file
3. Network glitch during Lambda execution
4. S3 retries event (assumes Lambda failed)
5. Lambda processes SAME file again → duplicate data in Silver layer!
```

**Result:** 50,000 rows written twice = 100,000 rows in output (20,000 duplicates).

---

### Solution: Idempotency Pattern

**Idempotent = Processing same input multiple times produces same result (no duplicates)**

**Pattern 1: Check before processing**

```python
import boto3

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('processed-files')

def lambda_handler(event, context):
    # Extract S3 file info
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    file_id = f"{bucket}/{key}"
    
    # Check if already processed
    response = table.get_item(Key={'file_id': file_id})
    if 'Item' in response:
        print(f"⚠️ File {file_id} already processed, skipping")
        return {'status': 'duplicate'}
    
    # Process file
    process_csv(bucket, key)
    
    # Mark as processed
    table.put_item(Item={
        'file_id': file_id,
        'processed_at': datetime.now().isoformat(),
        'status': 'success'
    })
    
    return {'status': 'processed'}
```

**Cost:** DynamoDB write = $0.00000125 per request (basically free for tracking).

---

**Pattern 2: Deterministic output location**

```python
def lambda_handler(event, context):
    input_key = event['Records'][0]['s3']['object']['key']
    # input: bronze/orders/2024-01-15.csv
    
    # Output location derived from input (deterministic)
    output_key = input_key.replace('bronze/', 'silver/').replace('.csv', '.parquet')
    # output: silver/orders/2024-01-15.parquet
    
    # Check if output already exists
    try:
        s3.head_object(Bucket='data-lake', Key=output_key)
        print(f"⚠️ Output {output_key} exists, skipping")
        return {'status': 'duplicate'}
    except s3.exceptions.NoSuchKey:
        pass  # Output doesn't exist, proceed
    
    # Process and write to output_key
    df = pd.read_csv(f's3://data-lake/{input_key}')
    df.to_parquet(f's3://data-lake/{output_key}')
    
    return {'status': 'processed'}
```

**Why this works:** S3 PutObject overwrites existing file → processing twice results in same file (idempotent).

---

## 📊 Real Example: Bronze → Silver ETL

**Requirements:**
- Input: CSV files in `s3://data-lake/bronze/orders/YYYY-MM-DD/`
- Validation: Remove nulls, deduplicate, cast types
- Output: Parquet in `s3://data-lake/silver/orders/YYYY-MM-DD/`

**Code:**

```python
import boto3
import pandas as pd
from datetime import datetime

s3 = boto3.client('s3')

def lambda_handler(event, context):
    # Parse S3 event
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    # key example: bronze/orders/2024-01-15/orders.csv
    
    print(f"📥 Processing: s3://{bucket}/{key}")
    
    # Idempotency check
    output_key = key.replace('bronze/', 'silver/').replace('.csv', '.parquet')
    try:
        s3.head_object(Bucket=bucket, Key=output_key)
        print(f"⚠️ Already processed, skipping")
        return {'statusCode': 200, 'body': 'Duplicate'}
    except:
        pass  # Proceed
    
    try:
        # Read CSV
        obj = s3.get_object(Bucket=bucket, Key=key)
        df = pd.read_csv(obj['Body'])
        print(f"📄 Loaded {len(df)} rows")
        
        # Validate schema
        required = ['order_id', 'customer_id', 'amount', 'order_date']
        missing = set(required) - set(df.columns)
        if missing:
            raise ValueError(f"Missing columns: {missing}")
        
        # Clean data
        initial_count = len(df)
        df = df.dropna(subset=['order_id', 'customer_id'])  # Remove critical nulls
        df = df.drop_duplicates(subset=['order_id'])  # Deduplicate
        df['amount'] = pd.to_numeric(df['amount'], errors='coerce')  # Cast to float
        df['order_date'] = pd.to_datetime(df['order_date'])  # Cast to datetime
        
        cleaned_count = len(df)
        removed = initial_count - cleaned_count
        print(f"🧹 Removed {removed} invalid rows ({removed/initial_count*100:.1f}%)")
        
        # Write Parquet
        df.to_parquet(f's3://{bucket}/{output_key}', index=False)
        print(f"✅ Success: {cleaned_count} rows → s3://{bucket}/{output_key}")
        
        return {
            'statusCode': 200,
            'body': {
                'input': key,
                'output': output_key,
                'rows_processed': cleaned_count,
                'rows_removed': removed
            }
        }
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        raise  # Re-raise to trigger retry/DLQ
```

**Execution Flow:**
1. File uploaded: `bronze/orders/2024-01-15/orders.csv`
2. S3 sends event to Lambda
3. Lambda checks if `silver/orders/2024-01-15/orders.parquet` exists (idempotency)
4. If not exists: read CSV → validate → clean → write Parquet
5. If exists: skip (already processed)

**Memory config:** 1024 MB (good for pandas)  
**Timeout:** 60 seconds (sufficient for <10 MB CSV)  
**Cost per execution:** ~$0.0002 (1024 MB × 5 sec)

---

## 🎯 Hands-On Intuition Check

**Question 1:**  
Your Lambda takes 10 seconds on **cold start** but only 2 seconds on **warm start**. What's causing the 8-second overhead?

<details>
<summary>Answer</summary>

**Cold start overhead:**
- Container initialization (~0.5 sec)
- Downloading deployment package (~1 sec)
- Loading imports (`import pandas` ~6 sec for large libraries)
- Initializing clients (boto3, DB connections ~0.5 sec)

**Fix:**
- Use Lambda Layers to reduce package size
- Lazy-load heavy imports (only when needed)
- Initialize clients outside handler (reuse across invocations)
- Consider Provisioned Concurrency ($$$, keeps functions warm 24/7)
</details>

---

**Question 2:**  
You set Lambda memory to 512 MB. Execution takes 20 seconds. You increase to 1024 MB, execution drops to 12 seconds. Should you increase memory?

<details>
<summary>Answer</summary>

**Yes!** Cost analysis:

512 MB:
- GB-seconds = 0.5 GB × 20 sec = 10 GB-sec
- Cost = 10 × $0.0000166667 = $0.000166

1024 MB:
- GB-seconds = 1 GB × 12 sec = 12 GB-sec
- Cost = 12 × $0.0000166667 = $0.0002

**Verdict:** 1024 MB is 20% more expensive BUT 40% faster. Trade-off depends on priority:
- **Cost-sensitive:** Stick with 512 MB
- **Speed-sensitive:** Use 1024 MB (user sees faster response)

**Pro move:** Try 1536 MB or 1792 MB (1 full vCPU threshold) and see if time drops below 10 sec → might break even on cost.
</details>

---

**Question 3:**  
Same file uploaded to S3 twice (network retry). How do you prevent duplicate processing?

<details>
<summary>Answer</summary>

**Idempotency patterns:**

1. **Check output exists before processing:**
   ```python
   if s3.head_object(output_key):
       return "Already processed"
   ```

2. **Track processed files in DynamoDB:**
   ```python
   if table.get_item(file_id):
       return "Duplicate"
   table.put_item(file_id, timestamp)
   ```

3. **Use S3 conditional writes (atomic):**
   ```python
   s3.put_object(Key=output_key, IfNoneMatch='*')  # Fails if exists
   ```

**Best practice:** Option 1 (check output) is simplest for ETL use cases.
</details>

---

## 📋 Summary

| Concept | Key Insight |
|---------|-------------|
| **Cold Start** | First invocation slow (load deps), reuse container for speed |
| **Memory = CPU** | More memory = more vCPU, find sweet spot (cost vs speed) |
| **Timeout** | Set realistic limit (prevent runaway costs) |
| **Environment Vars** | Config via env vars, secrets via Secrets Manager |
| **Layers** | Share heavy dependencies (pandas) across functions |
| **Idempotency** | Handle duplicate events (check output exists before processing) |

---

## ⏭️ Next Steps

You now know **HOW** to build production Lambda functions (cold starts, memory, layers, idempotency).

**Next:** [03-lambda-error-handling.md](./03-lambda-error-handling.md) → Learn error patterns (retries, DLQ, CloudWatch alerts).

---

**Pro Tip:** Always test cold start time. If >3 sec, move heavy imports to Lambda Layer or use lazy loading.
