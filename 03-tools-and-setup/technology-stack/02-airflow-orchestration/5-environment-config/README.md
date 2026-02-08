# 🔐 Environment & Configuration Management

Best practices untuk manage **secrets, variables, dan configuration** dalam Airflow, especially dalam Docker container environments.

## 🎯 Why Configuration Management Matters

Dalam production data engineering:
- ❌ **Never** hardcode credentials
- ❌ **Never** commit secrets to Git
- ✅ **Always** separate config dari code
- ✅ **Always** use environment-specific settings (dev/staging/prod)

---

## 📚 Configuration Methods di Airflow

### 1. Airflow Variables (UI/CLI)
**Best for:** Configuration values yang bisa berubah tanpa code changes

```python
from airflow.models import Variable

# Get single variable
api_key = Variable.get("API_KEY")
database_url = Variable.get("DATABASE_URL")

# Get dengan default value
timeout = Variable.get("API_TIMEOUT", default_var=30)

# Get as JSON
config = Variable.get("app_config", deserialize_json=True)
# Returns: {"host": "api.example.com", "port": 443}
```

**Set via CLI:**
```bash
airflow variables set API_KEY "your-secret-key"
airflow variables set app_config '{"host": "api.example.com"}' --json
```

**Set via UI:**
Admin → Variables → Add Variable

---

### 2. Environment Variables (Docker)
**Best for:** Container-specific configuration, secrets injection

```python
import os

# Access directly
api_key = os.getenv("API_KEY")
database_url = os.getenv("DATABASE_URL", "default_value")

# In DAG
@task
def extract():
    api_key = os.getenv("API_KEY")
    if not api_key:
        raise ValueError("API_KEY not set!")
    # Use api_key...
```

**docker-compose.yml:**
```yaml
services:
  airflow-webserver:
    environment:
      # Direct values
      - AIRFLOW__CORE__EXECUTOR=LocalExecutor
      
      # From .env file
      - API_KEY=${API_KEY}
      - DATABASE_URL=${DATABASE_URL}
      
      # Airflow variables (auto-loaded)
      - AIRFLOW_VAR_API_KEY=${API_KEY}
      - AIRFLOW_VAR_DATABASE_URL=${DATABASE_URL}
    
    env_file:
      - .env  # Load all vars from .env
```

**.env file:**
```bash
# .env (DON'T COMMIT TO GIT!)
API_KEY=your_secret_api_key
DATABASE_URL=postgresql://user:pass@localhost/db
ENV=production
LOG_LEVEL=INFO
```

**.gitignore:**
```
.env
*.env
.env.*
```

---

### 3. Airflow Connections
**Best for:** Database, API, cloud service credentials

```python
from airflow.hooks.base import BaseHook

# Get connection
conn = BaseHook.get_connection('my_postgres_conn')
conn_uri = conn.get_uri()  # postgresql://user:pass@host:5432/db

# Or use directly in operators
from airflow.providers.postgres.operators.postgres import PostgresOperator

task = PostgresOperator(
    task_id='query_db',
    postgres_conn_id='my_postgres_conn',  # Reference connection
    sql='SELECT * FROM users'
)
```

**Set via CLI:**
```bash
airflow connections add 'my_postgres_conn' \
    --conn-type 'postgres' \
    --conn-host 'localhost' \
    --conn-schema 'mydb' \
    --conn-login 'user' \
    --conn-password 'password' \
    --conn-port '5432'
```

---

### 4. External Config Files (YAML/JSON)
**Best for:** Complex, structured configuration

```python
import yaml
from pathlib import Path

@task
def load_config() -> dict:
    config_path = Path(__file__).parent / 'config' / 'app_config.yaml'
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    return config

@task
def use_config(config: dict):
    api_url = config['api']['base_url']
    timeout = config['api']['timeout']
    # Use config...
```

**config/app_config.yaml:**
```yaml
api:
  base_url: https://api.example.com
  timeout: 30
  retry_attempts: 3

database:
  host: localhost
  port: 5432
  name: mydb

features:
  enable_caching: true
  max_batch_size: 1000
```

---

## 🐳 Docker Environment Setup

### Complete docker-compose.yml Example:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:13
    environment:
      POSTGRES_USER: airflow
      POSTGRES_PASSWORD: airflow
      POSTGRES_DB: airflow
    volumes:
      - postgres-db-volume:/var/lib/postgresql/data

  airflow-webserver:
    image: apache/airflow:2.8.0-python3.11
    depends_on:
      - postgres
    environment:
      # Airflow core config
      AIRFLOW__CORE__EXECUTOR: LocalExecutor
      AIRFLOW__DATABASE__SQL_ALCHEMY_CONN: postgresql+psycopg2://airflow:airflow@postgres/airflow
      AIRFLOW__CORE__FERNET_KEY: ${FERNET_KEY}
      AIRFLOW__CORE__DAGS_ARE_PAUSED_AT_CREATION: 'true'
      AIRFLOW__CORE__LOAD_EXAMPLES: 'false'
      
      # API Configuration (as Airflow Variables)
      AIRFLOW_VAR_API_KEY: ${API_KEY}
      AIRFLOW_VAR_API_URL: ${API_URL}
      AIRFLOW_VAR_DATABASE_URL: ${DATABASE_URL}
      
      # Feature flags
      AIRFLOW_VAR_ENABLE_NOTIFICATIONS: ${ENABLE_NOTIFICATIONS:-false}
      
      # Python path (untuk custom modules)
      PYTHONPATH: /opt/airflow/dags:/opt/airflow/include
    
    env_file:
      - .env  # Load additional vars
    
    volumes:
      - ./dags:/opt/airflow/dags
      - ./logs:/opt/airflow/logs
      - ./plugins:/opt/airflow/plugins
      - ./include:/opt/airflow/include  # Shared code
      - ./config:/opt/airflow/config     # Config files
    
    ports:
      - "8080:8080"
    
    command: webserver

  airflow-scheduler:
    image: apache/airflow:2.8.0-python3.11
    depends_on:
      - postgres
    environment:
      AIRFLOW__CORE__EXECUTOR: LocalExecutor
      AIRFLOW__DATABASE__SQL_ALCHEMY_CONN: postgresql+psycopg2://airflow:airflow@postgres/airflow
      AIRFLOW_VAR_API_KEY: ${API_KEY}
      PYTHONPATH: /opt/airflow/dags:/opt/airflow/include
    
    env_file:
      - .env
    
    volumes:
      - ./dags:/opt/airflow/dags
      - ./logs:/opt/airflow/logs
      - ./plugins:/opt/airflow/plugins
      - ./include:/opt/airflow/include
      - ./config:/opt/airflow/config
    
    command: scheduler

volumes:
  postgres-db-volume:
```

---

## 🔐 Secrets Management Best Practices

### Environment-Specific .env Files:

**.env.dev:**
```bash
ENV=development
API_KEY=dev_key_12345
DATABASE_URL=postgresql://dev:dev@localhost/dev_db
LOG_LEVEL=DEBUG
ENABLE_NOTIFICATIONS=false
```

**.env.prod:**
```bash
ENV=production
API_KEY=${SECRET_API_KEY}  # From secure vault
DATABASE_URL=${SECRET_DATABASE_URL}
LOG_LEVEL=INFO
ENABLE_NOTIFICATIONS=true
```

**Usage:**
```bash
# Development
docker-compose --env-file .env.dev up

# Production
docker-compose --env-file .env.prod up
```

---

### Using Secret Management Services:

```python
from airflow.decorators import task
import os

@task
def get_secret_from_vault():
    """
    In production, fetch from:
    - AWS Secrets Manager
    - Google Secret Manager
    - HashiCorp Vault
    - Azure Key Vault
    """
    env = os.getenv("ENV", "development")
    
    if env == "production":
        # Fetch from secret manager
        from google.cloud import secretmanager
        client = secretmanager.SecretManagerServiceClient()
        name = "projects/my-project/secrets/api-key/versions/latest"
        response = client.access_secret_version(request={"name": name})
        api_key = response.payload.data.decode("UTF-8")
    else:
        # Development - use env var
        api_key = os.getenv("API_KEY")
    
    return api_key
```

---

## 🎯 Configuration Patterns

### Pattern 1: Centralized Config Class

```python
# include/config.py
import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class AppConfig:
    """Centralized application configuration."""
    
    # Environment
    env: str = os.getenv("ENV", "development")
    
    # API Config
    api_key: str = os.getenv("API_KEY", "")
    api_url: str = os.getenv("API_URL", "https://api.example.com")
    api_timeout: int = int(os.getenv("API_TIMEOUT", "30"))
    
    # Database
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///airflow.db")
    
    # Features
    enable_cache: bool = os.getenv("ENABLE_CACHE", "false").lower() == "true"
    max_retries: int = int(os.getenv("MAX_RETRIES", "3"))
    
    @property
    def is_production(self) -> bool:
        return self.env == "production"
    
    def validate(self):
        """Validate required fields."""
        if not self.api_key:
            raise ValueError("API_KEY is required!")
        if not self.database_url:
            raise ValueError("DATABASE_URL is required!")

# Usage in DAG
from include.config import AppConfig

@task
def extract():
    config = AppConfig()
    config.validate()
    
    # Use config
    api_key = config.api_key
    url = config.api_url
```

---

### Pattern 2: Environment-Based Config Loading

```python
import os
import yaml
from pathlib import Path

def load_config() -> dict:
    """Load config based on environment."""
    env = os.getenv("ENV", "development")
    config_dir = Path(__file__).parent.parent / 'config'
    
    # Load base config
    base_config_path = config_dir / 'base.yaml'
    with open(base_config_path) as f:
        config = yaml.safe_load(f)
    
    # Override with env-specific config
    env_config_path = config_dir / f'{env}.yaml'
    if env_config_path.exists():
        with open(env_config_path) as f:
            env_config = yaml.safe_load(f)
            config.update(env_config)
    
    return config
```

**config/base.yaml:**
```yaml
api:
  timeout: 30
  retry_attempts: 3

database:
  pool_size: 5
```

**config/production.yaml:**
```yaml
api:
  timeout: 60
  retry_attempts: 5

database:
  pool_size: 20
```

---

## 🚀 DAG Example dengan Complete Config Management

```python
from airflow.decorators import dag, task
from datetime import datetime
import os
from typing import Optional

# ==========================================
# CONFIGURATION
# ==========================================

class Config:
    """Environment-aware configuration."""
    
    # From Airflow Variables
    @staticmethod
    def get_api_key() -> str:
        from airflow.models import Variable
        return Variable.get("API_KEY")
    
    # From Environment Variables
    @staticmethod
    def get_env() -> str:
        return os.getenv("ENV", "development")
    
    # From Connection
    @staticmethod
    def get_db_conn():
        from airflow.hooks.base import BaseHook
        return BaseHook.get_connection('postgres_default')

# ==========================================
# DAG
# ==========================================

@dag(
    dag_id='config_management_example',
    schedule='@daily',
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['example', 'config']
)
def config_demo():
    
    @task
    def extract() -> dict:
        """Extract using config."""
        api_key = Config.get_api_key()
        env = Config.get_env()
        
        print(f"Running in: {env}")
        print(f"API Key (masked): {api_key[:4]}...")
        
        # Use in API call
        return {"data": [1, 2, 3], "env": env}
    
    @task
    def load(data: dict):
        """Load using connection."""
        conn = Config.get_db_conn()
        
        print(f"Loading to: {conn.host}")
        print(f"Database: {conn.schema}")
        # Actual database operations...
    
    data = extract()
    load(data)

config_demo()
```

---

## 📝 Checklist untuk Production

- [ ] All secrets in environment variables or secret manager
- [ ] No hardcoded credentials in code
- [ ] .env files in .gitignore
- [ ] Separate configs untuk dev/staging/prod
- [ ] Config validation at startup
- [ ] Use Airflow Connections untuk external services
- [ ] Document all required environment variables
- [ ] Use PYTHONPATH untuk import resolution
- [ ] Volume mapping untuk config files
- [ ] Proper logging (no secrets in logs!)

---

## 🔗 Next Steps

- **6-import-resolution/** - Solve Python import issues in containers
- **7-operators-comparison/** - Custom vs built-in operators
- **9-docker-compose-setup/** - Production-ready setup

**Keep your secrets safe! 🔐**
