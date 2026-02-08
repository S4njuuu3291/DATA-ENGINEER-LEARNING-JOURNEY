# 🐳 DevOps & Infrastructure

Essential **DevOps practices** untuk Data Engineers - containerization, IaC, dan CI/CD.

## 🎯 Why DevOps for Data Engineers?

Modern data pipelines = code + infrastructure:
- ✅ Reproducible environments (Docker)
- ✅ Infrastructure as Code (declarative config)
- ✅ Automated testing & deployment (CI/CD)
- ✅ Version control untuk everything

---

## 📚 Core Topics

### 🔴 CRITICAL

#### 1. Containerization (Docker)
**Why Docker?**
- Same environment dev → prod
- Dependency isolation
- Easy deployment

**Dockerfile Best Practices:**
```dockerfile
# Multi-stage build
FROM python:3.11-slim as builder

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM python:3.11-slim

WORKDIR /app

# Copy only necessary files
COPY --from=builder /root/.local /root/.local
COPY . .

# Set path
ENV PATH=/root/.local/bin:$PATH

# Non-root user
RUN useradd -m appuser
USER appuser

CMD ["python", "main.py"]
```

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  airflow:
    build: .
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - API_KEY=${API_KEY}
    volumes:
      - ./dags:/opt/airflow/dags
      - ./logs:/opt/airflow/logs
    ports:
      - "8080:8080"
    depends_on:
      - postgres
  
  postgres:
    image: postgres:13
    environment:
      POSTGRES_USER: airflow
      POSTGRES_PASSWORD: airflow
      POSTGRES_DB: airflow
    volumes:
      - postgres-data:/var/lib/postgresql/data

volumes:
  postgres-data:
```

---

#### 2. Version Control (Git)

**.gitignore for Data Projects:**
```gitignore
# Secrets
.env
*.env
.env.*
*.key
*.pem

# Python
__pycache__/
*.py[cod]
.venv/
venv/
.pytest_cache/

# Data
data/
*.csv
*.parquet
*.avro

# Logs
logs/
*.log

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db

# Build artifacts
dist/
build/
*.egg-info/
```

**Conventional Commits:**
```bash
feat: add BigQuery data loader
fix: resolve null handling in transform
docs: update pipeline architecture diagram
test: add integration tests for API client
refactor: extract config loading to separate module
```

---

#### 3. Infrastructure as Code

**Config Files (YAML):**
```yaml
# config/production.yaml
environment: production

api:
  base_url: https://api.example.com
  timeout: 30
  max_retries: 3

database:
  host: prod-db.example.com
  port: 5432
  name: analytics
  pool_size: 20

cloud:
  project_id: my-prod-project
  bucket: prod-data-bucket
  dataset: analytics

features:
  enable_caching: true
  enable_monitoring: true
```

---

### 🟡 IMPORTANT

#### 4. CI/CD Patterns

**GitHub Actions Example:**
```yaml
# .github/workflows/test.yml
name: Test Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov
      
      - name: Run tests
        run: pytest tests/ --cov=src/
      
      - name: Lint code
        run: |
          pip install ruff
          ruff check src/
      
      - name: Type check
        run: |
          pip install mypy
          mypy src/
```

---

#### 5. Environment Management

```bash
# .env.dev
ENV=development
LOG_LEVEL=DEBUG
API_KEY=dev_key_123
DATABASE_URL=postgresql://localhost/dev_db

# .env.prod
ENV=production
LOG_LEVEL=INFO
API_KEY=${SECRET_API_KEY}
DATABASE_URL=${SECRET_DATABASE_URL}
```

**Load in Code:**
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    env: str = "development"
    log_level: str = "INFO"
    api_key: str
    database_url: str
    
    class Config:
        env_file = ".env"

settings = Settings()
```

---

## 🎯 Best Practices

### ✅ Docker

1. **Multi-stage builds** - smaller images
2. **Layer caching** - faster builds
3. **Non-root user** - security
4. **.dockerignore** - exclude unnecessary files
5. **Health checks** - container monitoring

```dockerfile
# .dockerignore
.git
.venv
__pycache__
*.pyc
.env
logs/
data/
```

---

### ✅ Git Workflow

```bash
# Feature branch
git checkout -b feature/add-new-api

# Make changes
git add .
git commit -m "feat: add CoinGecko API integration"

# Push
git push origin feature/add-new-api

# Create PR → Review → Merge to main
```

---

### ✅ Configuration

1. **Separate config from code**
2. **Environment-specific configs**
3. **Validate configuration on startup**
4. **Document all required variables**

---

## 📊 Project Structure

```
data-pipeline/
├── .github/
│   └── workflows/
│       ├── test.yml
│       └── deploy.yml
├── src/
│   ├── __init__.py
│   ├── extract.py
│   ├── transform.py
│   └── load.py
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── config/
│   ├── base.yaml
│   ├── development.yaml
│   └── production.yaml
├── dags/
│   └── data_pipeline.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
├── .gitignore
├── .dockerignore
├── README.md
└── pyproject.toml
```

---

## 🚀 Complete Example

**Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Application
COPY src/ ./src/
COPY config/ ./config/

# Environment
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Run
CMD ["python", "-m", "src.main"]
```

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  pipeline:
    build: .
    env_file:
      - .env
    volumes:
      - ./src:/app/src
      - ./config:/app/config
    depends_on:
      - postgres
  
  postgres:
    image: postgres:13
    environment:
      POSTGRES_DB: analytics
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
```

**Run:**
```bash
# Development
docker-compose up

# Production
docker-compose -f docker-compose.prod.yml up -d
```

---

**Automate everything! 🐳**
