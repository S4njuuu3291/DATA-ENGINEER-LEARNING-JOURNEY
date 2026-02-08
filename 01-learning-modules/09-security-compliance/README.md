# 🔐 Security & Compliance

Best practices untuk **secure data pipelines** & regulatory compliance.

## 🎯 Topics

### 1. Credential Management
- **Never commit secrets to Git**
- Use Secret Manager (GCP, AWS, Azure)
- Rotate credentials regularly
- Principle of least privilege

**Example:**
```python
from google.cloud import secretmanager

def get_secret(project_id: str, secret_id: str) -> str:
    """Fetch secret from Secret Manager."""
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")

# Usage
api_key = get_secret('my-project', 'api-key')
```

---

### 2. Access Control
- **RBAC** (Role-Based Access Control)
- Service account best practices
- Network security (VPC, firewalls)
- Audit logging

---

### 3. Data Protection
- **Encryption at rest** (stored data)
- **Encryption in transit** (network transfer)
- PII masking/anonymization
- Data retention policies

---

### 4. Compliance
- GDPR (Europe)
- CCPA (California)
- HIPAA (Healthcare)
- SOC 2

---

### 5. Best Practices

**✅ DO's:**
1. Use environment variables untuk secrets
2. Enable audit logging
3. Implement least privilege access
4. Encrypt sensitive data
5. Regular security reviews

**❌ DON'Ts:**
1. ❌ Hardcode credentials
2. ❌ Commit .env files to Git
3. ❌ Use overly permissive IAM roles
4. ❌ Log sensitive data
5. ❌ Store PII without encryption

---

**Example .gitignore:**
```gitignore
# Secrets
.env
*.env
.env.*
*.key
*.pem
service-account*.json

# Sensitive data
data/
*.csv
*.parquet
logs/
```

---

**More content coming soon...**

For now, check:
- GCP [Security Best Practices](https://cloud.google.com/security/best-practices)
- OWASP [Top 10](https://owasp.org/www-project-top-ten/)
