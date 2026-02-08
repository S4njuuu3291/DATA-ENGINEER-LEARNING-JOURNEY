# AWS S3 Cheatsheet

Quick reference for S3 CLI and boto3 operations

---

## AWS CLI Commands

### Basic Operations

```bash
# List buckets
aws s3 ls

# List contents
aws s3 ls s3://my-bucket/

# Create bucket
aws s3 mb s3://my-bucket --region us-east-1

# Delete bucket (must be empty)
aws s3 rb s3://my-bucket

# Copy file
aws s3 cp file.txt s3://my-bucket/file.txt

# Sync folder
aws s3 sync ./local-folder s3://my-bucket/remote-folder

# Remove file
aws s3 rm s3://my-bucket/file.txt

# Remove folder
aws s3 rm s3://my-bucket/folder --recursive
```

### S3API Commands (Advanced)

```bash
# Get bucket versioning status
aws s3api get-bucket-versioning --bucket my-bucket

# Enable versioning
aws s3api put-bucket-versioning \
  --bucket my-bucket \
  --versioning-configuration Status=Enabled

# List object versions
aws s3api list-object-versions --bucket my-bucket

# Put object with metadata
aws s3api put-object \
  --bucket my-bucket \
  --key my-file.txt \
  --body file.txt \
  --metadata key1=value1,key2=value2

# Get object ACL
aws s3api get-object-acl \
  --bucket my-bucket \
  --key my-file.txt

# Get bucket encryption
aws s3api get-bucket-encryption --bucket my-bucket

# Put bucket encryption
aws s3api put-bucket-encryption \
  --bucket my-bucket \
  --server-side-encryption-configuration '{
    "Rules": [{
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "AES256"
      }
    }]
  }'

# Get lifecycle configuration
aws s3api get-bucket-lifecycle-configuration --bucket my-bucket

# Put lifecycle configuration
aws s3api put-bucket-lifecycle-configuration \
  --bucket my-bucket \
  --lifecycle-configuration file://lifecycle.json

# Put bucket policy
aws s3api put-bucket-policy \
  --bucket my-bucket \
  --policy file://policy.json

# Get bucket policy
aws s3api get-bucket-policy --bucket my-bucket

# Put public access block
aws s3api put-public-access-block \
  --bucket my-bucket \
  --public-access-block-configuration \
  "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"
```

---

## Boto3 Operations

```python
import boto3

s3 = boto3.client('s3')
s3_resource = boto3.resource('s3')

# List buckets
response = s3.list_buckets()
for bucket in response['Buckets']:
    print(bucket['Name'])

# List objects in bucket
response = s3.list_objects_v2(Bucket='my-bucket', MaxKeys=100)
for obj in response.get('Contents', []):
    print(obj['Key'], obj['Size'])

# Upload file
s3.upload_file('local-file.txt', 'my-bucket', 'remote-file.txt')

# Download file
s3.download_file('my-bucket', 'remote-file.txt', 'local-file.txt')

# Put object
s3.put_object(
    Bucket='my-bucket',
    Key='my-file.txt',
    Body=b'file contents',
    ServerSideEncryption='AES256',
    Metadata={'key': 'value'}
)

# Get object
response = s3.get_object(Bucket='my-bucket', Key='my-file.txt')
data = response['Body'].read()

# Delete object
s3.delete_object(Bucket='my-bucket', Key='my-file.txt')

# Delete multiple objects
s3.delete_objects(
    Bucket='my-bucket',
    Delete={
        'Objects': [
            {'Key': 'file1.txt'},
            {'Key': 'file2.txt'}
        ]
    }
)

# Copy object (server-side)
s3.copy_object(
    CopySource={'Bucket': 'source-bucket', 'Key': 'file.txt'},
    Bucket='dest-bucket',
    Key='file.txt'
)

# Get bucket versioning
s3.get_bucket_versioning(Bucket='my-bucket')

# Enable versioning
s3.put_bucket_versioning(
    Bucket='my-bucket',
    VersioningConfiguration={'Status': 'Enabled'}
)
```

---

## Storage Classes

| Class | Cost | Speed | Min. Duration | Use Case |
|-------|------|-------|---|---|
| **Standard** | $0.023 | Instant | - | Hot data |
| **Standard-IA** | $0.0125 | Instant | 30 days | Warm data |
| **Glacier Instant** | $0.004 | <1 sec | 90 days | Archive (quarterly) |
| **Glacier Flex** | $0.0036 | 1-12 hrs | 90 days | Archive (annual) |
| **Deep Archive** | $0.00099 | 12 hrs | 180 days | Legal archive |

---

## Lifecycle Policy Template

```json
{
  "Rules": [
    {
      "Id": "ArchiveOldData",
      "Status": "Enabled",
      "Filter": {"Prefix": ""},
      "Transitions": [
        {
          "Days": 30,
          "StorageClass": "STANDARD_IA"
        },
        {
          "Days": 90,
          "StorageClass": "GLACIER_IR"
        }
      ],
      "Expiration": {
        "Days": 365
      }
    }
  ]
}
```

---

## Bucket Policy Template

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowGetObject",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::ACCOUNT:role/DataEngineerRole"
      },
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::my-bucket/*"
    }
  ]
}
```

---

## Cost Optimization Tips

⚠️ **Expensive Mistakes:**
- Storing standard forever (use lifecycle transitions)
- No versioning limits (old versions pile up)
- Public buckets (potential egress charges)
- Small frequent uploads (use multipart)

✅ **Cost Savings:**
- Enable lifecycle policies (auto-transition)
- Delete old versions (versioning cleanup)
- Use VPC endpoints (no egress charges)
- Compress data (reduce storage size)
- Intelligent-tiering (auto-optimize)

---

## Common Errors & Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| **NoSuchBucket** | Bucket doesn't exist | Check bucket name (globally unique) |
| **AccessDenied** | No permissions | Check IAM policy, bucket policy |
| **InvalidBucketName** | Name doesn't follow rules | Use lowercase, hyphens, no underscores |
| **BucketAlreadyExists** | Someone else owns the name | Use different name + timestamp |
| **NoSuchVersion** | Version ID doesn't exist | List versions first: `list-object-versions` |

---

## Partition Projection Template

```json
{
  "Classification": "parquet",
  "Parameters": {
    "projection.enabled": "true",
    "projection.date_format": "yyyy-MM-dd",
    "projection.date_range": "2024-01-01,NOW",
    "projection.date_interval": "1",
    "projection.date_interval_unit": "DAYS",
    "storage.location.template": "s3://my-bucket/data/date=${date}"
  }
}
```

---

**Pro Tips:**
- 🔍 Use S3 Select to query parts of objects (avoid downloading entire file)
- 📊 Enable CloudTrail to audit all S3 access
- 💰 Use S3 Storage Lens for cost analysis  
- 🔐 Always enable encryption (SSE-S3 minimum)
- ✅ Test policies with IAM Policy Simulator

