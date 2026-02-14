# Chapter 2: S3 Bronze Data Lake

## Konsep Singkat

### Object Storage (S3) vs File System
- S3 menyimpan data sebagai objek (blob) dengan metadata.
- Tidak ada folder nyata, hanya prefix dalam nama objek.
- Cocok untuk data lake karena murah, skalabel, dan durable.

### Bucket Naming: Global Uniqueness
- Nama bucket harus unik secara global di seluruh AWS.
- Gunakan format konsisten + suffix acak.
- Contoh: `sanju-scraper-bronze-data-728451`.

---

## Integration Snippet (Python + boto3)

Gunakan Access Key dari Chapter 1.

```python
import boto3
import json

session = boto3.Session(
    aws_access_key_id="YOUR_ACCESS_KEY",
    aws_secret_access_key="YOUR_SECRET_KEY",
    region_name="ap-southeast-1",
)

s3 = session.client("s3")

payload = {
    "source": "job-board",
    "records": 25,
    "ingested_at": "2026-02-14T00:00:00Z",
}

s3.put_object(
    Bucket="sanju-scraper-bronze-data-728451",
    Key="bronze/job-scrape-2026-02-14.json",
    Body=json.dumps(payload).encode("utf-8"),
    ContentType="application/json",
)
```

---

## Verification

### Terraform

```bash
terraform init
terraform validate
terraform plan
terraform apply
```

### Cek via AWS CLI

```bash
aws s3 ls s3://sanju-scraper-bronze-data-728451/
```

### Cek via AWS Console
- AWS Console  S3
- Cari bucket: `sanju-scraper-bronze-data-728451`
- Pastikan Public access = Blocked
