# 🐍 Python Engineering Patterns

Modern Python practices untuk **Data Engineering** - dari type safety sampai configuration management.

## 🎯 Why Python Engineering Matters

Sebagai Data Engineer, Python adalah primary tool. Code quality = pipeline quality.

**Good Python Engineering:**
- ✅ Type-safe code (fewer runtime errors)
- ✅ Proper error handling (resilient pipelines)
- ✅ Clean configuration (easy deployment)
- ✅ Testable code (confident releases)

---

## 📚 Learning Path

### 🔴 CRITICAL (Foundation)

#### **1. Type Safety & Validation**
Folder: `1-type-safety/`

**Topics:**
- Type hints (function annotations)
- Generic types (List, Dict, Optional)
- Pydantic models untuk validation
- Runtime vs static type checking
- dataclasses untuk structured data

**Why it matters:**
```python
# ❌ Without types - error at runtime
def process_users(users):  # What type is users?
    return [u['name'] for u in users]  # KeyError if wrong structure!

# ✅ With types - error caught early
def process_users(users: List[Dict[str, any]]) -> List[str]:
    return [u['name'] for u in users]  # IDE helps, mypy checks!
```

---

#### **2. Error Handling**
Folder: `2-error-handling/`

**Topics:**
- Custom exception classes
- Exception chaining
- Retry mechanisms dengan exponential backoff
- Logging untuk debugging
- Error context & tracebacks

**Critical untuk:**
- API failures
- Database connection issues
- Network timeouts
- Data validation errors

---

#### **3. HTTP Client Patterns**
Folder: `3-http-clients/`

**Topics:**
- Modern HTTP libraries (httpx, requests)
- Request timeout configuration
- Rate limiting strategies
- Error response handling
- Pagination patterns
- Connection pooling

**Real-world use:**
- Extracting dari REST APIs
- Webhook integrations
- Cloud service APIs

---

### 🟡 IMPORTANT (Production Skills)

#### **4. Configuration Management**
Folder: `4-configuration/`

**Topics:**
- Environment variables (.env files)
- External config files (YAML, JSON)
- Path management (os.path, pathlib)
- Config validation
- Environment-specific settings

---

#### **5. Async Programming** (Optional tapi powerful)
Folder: `5-async-patterns/`

**Topics:**
- asyncio basics
- Async HTTP requests
- Concurrent data processing
- When to use async vs threading

---

## 📁 Folder Structure

```
Python_Engineering_Patterns/
├── README.md (this file)
├── 1-type-safety/
│   ├── 1-type-hints-basics.md
│   ├── 2-pydantic-models.py
│   ├── 3-dataclasses.py
│   ├── 4-generic-types.py
│   └── README.md
├── 2-error-handling/
│   ├── 1-exceptions-basics.md
│   ├── 2-custom-exceptions.py
│   ├── 3-retry-mechanisms.py
│   ├── 4-logging-patterns.py
│   └── README.md
├── 3-http-clients/
│   ├── 1-requests-basics.md
│   ├── 2-httpx-modern.py
│   ├── 3-rate-limiting.py
│   ├── 4-pagination.py
│   ├── 5-error-handling.py
│   └── README.md
├── 4-configuration/
│   ├── 1-env-variables.md
│   ├── 2-config-files.py
│   ├── 3-pydantic-settings.py
│   ├── 4-path-management.py
│   └── README.md
└── 5-async-patterns/
    ├── 1-asyncio-basics.md
    ├── 2-async-http.py
    ├── 3-concurrent-processing.py
    └── README.md
```

---

## 🚀 Quick Examples

### 1. Type-Safe Data Model
```python
from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional

class User(BaseModel):
    """Type-safe user model."""
    
    id: int
    name: str
    email: str
    score: float = Field(ge=0, le=100)  # 0-100 range
    created_at: datetime
    metadata: Optional[dict] = None
    
    @validator('email')
    def validate_email(cls, v):
        if '@' not in v:
            raise ValueError('Invalid email')
        return v

# Usage
user = User(
    id=1,
    name="Alice",
    email="alice@example.com",
    score=95,
    created_at=datetime.now()
)

# Automatic validation!
# user = User(id=1, name="Alice", email="invalid", score=150)  # ❌ Raises ValidationError
```

---

### 2. Retry with Exponential Backoff
```python
import time
from typing import Callable, TypeVar, Any
from functools import wraps

T = TypeVar('T')

def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2
):
    """Decorator untuk retry dengan exponential backoff."""
    
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            retries = 0
            
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    retries += 1
                    
                    if retries >= max_retries:
                        raise
                    
                    # Calculate delay
                    delay = min(
                        base_delay * (exponential_base ** retries),
                        max_delay
                    )
                    
                    print(f"Retry {retries}/{max_retries} after {delay}s: {e}")
                    time.sleep(delay)
            
        return wrapper
    return decorator

# Usage
@retry_with_backoff(max_retries=3, base_delay=1.0)
def fetch_api_data(url: str) -> dict:
    """Fetch data with automatic retry."""
    import requests
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.json()
```

---

### 3. Modern HTTP Client
```python
import httpx
from typing import Dict, List
import asyncio

class APIClient:
    """Modern async HTTP client."""
    
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        self.client = httpx.AsyncClient(
            base_url=base_url,
            headers=self.headers,
            timeout=30.0
        )
    
    async def get(self, endpoint: str, params: dict = None) -> dict:
        """GET request dengan error handling."""
        try:
            response = await self.client.get(endpoint, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise ValueError(f"API error: {e.response.status_code}")
        except httpx.TimeoutException:
            raise TimeoutError(f"Request timeout: {endpoint}")
    
    async def close(self):
        """Close client connection."""
        await self.client.aclose()

# Usage
async def main():
    client = APIClient('https://api.example.com', 'your_api_key')
    
    try:
        data = await client.get('/users', params={'limit': 10})
        print(data)
    finally:
        await client.close()

# Run
asyncio.run(main())
```

---

### 4. Configuration Management
```python
from pydantic_settings import BaseSettings
from typing import Optional
from pathlib import Path

class AppConfig(BaseSettings):
    """Application configuration from environment."""
    
    # API Settings
    api_key: str
    api_url: str = "https://api.example.com"
    api_timeout: int = 30
    
    # Database
    database_url: str
    db_pool_size: int = 5
    
    # Cloud
    gcp_project_id: str
    gcs_bucket_name: str
    
    # Features
    enable_caching: bool = False
    log_level: str = "INFO"
    
    # Paths
    data_dir: Path = Path("/tmp/data")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

# Usage - auto loads from .env
config = AppConfig()

print(f"API: {config.api_url}")
print(f"Database: {config.database_url}")
```

**.env file:**
```bash
API_KEY=your_secret_key
DATABASE_URL=postgresql://user:pass@localhost/db
GCP_PROJECT_ID=my-project
GCS_BUCKET_NAME=my-bucket
ENABLE_CACHING=true
LOG_LEVEL=DEBUG
```

---

## 🎯 Best Practices

### ✅ Type Hints Everywhere
```python
# ✅ Good
def process_data(
    users: List[Dict[str, any]],
    min_score: float = 0.0
) -> Dict[str, int]:
    """Process user data and return statistics."""
    return {
        'total': len(users),
        'avg_score': sum(u['score'] for u in users) / len(users)
    }

# ❌ Bad
def process_data(users, min_score=0.0):
    return {'total': len(users)}
```

---

### ✅ Use Pydantic for Validation
```python
from pydantic import BaseModel, ValidationError

class DataRecord(BaseModel):
    id: int
    value: float
    timestamp: datetime

try:
    record = DataRecord(**raw_data)  # Auto validation!
except ValidationError as e:
    print(f"Invalid data: {e}")
```

---

### ✅ Structured Logging
```python
import logging
import json

# Setup structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def process_batch(batch_id: str, records: int):
    """Process batch with logging."""
    logger.info(
        "Processing batch",
        extra={
            'batch_id': batch_id,
            'record_count': records,
            'pipeline': 'etl_v1'
        }
    )
```

---

### ✅ Path Management dengan pathlib
```python
from pathlib import Path

# ✅ Good - OS agnostic
data_dir = Path(__file__).parent / 'data'
input_file = data_dir / 'input.csv'

if input_file.exists():
    data = input_file.read_text()

# ❌ Bad - OS specific
import os
data_dir = os.path.join(os.path.dirname(__file__), 'data')
```

---

## 🔗 Integration Patterns

### Pattern: Complete ETL dengan Best Practices
```python
from pydantic import BaseModel
from typing import List, Dict
from pathlib import Path
import httpx
import logging

logger = logging.getLogger(__name__)

# 1. Type-safe models
class User(BaseModel):
    id: int
    name: str
    email: str
    score: float

class ETLConfig(BaseModel):
    api_url: str
    api_key: str
    output_dir: Path
    batch_size: int = 100

# 2. HTTP client with retry
class APIExtractor:
    def __init__(self, config: ETLConfig):
        self.config = config
        self.client = httpx.Client(
            base_url=config.api_url,
            headers={'Authorization': f'Bearer {config.api_key}'},
            timeout=30.0
        )
    
    @retry_with_backoff(max_retries=3)
    def fetch_users(self, page: int = 1) -> List[User]:
        """Fetch users with validation."""
        response = self.client.get('/users', params={'page': page})
        response.raise_for_status()
        
        # Validate with Pydantic
        users = [User(**u) for u in response.json()]
        logger.info(f"Fetched {len(users)} users from page {page}")
        
        return users

# 3. Main pipeline
def run_etl(config: ETLConfig):
    """Run ETL with proper error handling."""
    try:
        extractor = APIExtractor(config)
        users = extractor.fetch_users(page=1)
        
        # Process & save
        output_file = config.output_dir / 'users.json'
        output_file.write_text(
            json.dumps([u.dict() for u in users], indent=2)
        )
        
        logger.info(f"ETL completed: {len(users)} users saved")
        
    except httpx.HTTPError as e:
        logger.error(f"HTTP error: {e}")
        raise
    except ValidationError as e:
        logger.error(f"Data validation failed: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise
```

---

## 🎓 When to Use What?

| Pattern | When to Use |
|---------|------------|
| **Type Hints** | Always! In all functions |
| **Pydantic** | API responses, config, data validation |
| **dataclasses** | Simple data containers |
| **Custom Exceptions** | Domain-specific errors |
| **Retry Decorator** | API calls, network operations |
| **Async/Await** | I/O heavy operations (many API calls) |
| **pathlib** | File/directory operations |
| **Logging** | Always! Debug production issues |

---

## 📖 Next Steps

Setelah menguasai Python patterns:
1. **Apply dalam Airflow DAGs** - Type-safe tasks
2. **Testing** - Test pydantic models, retry logic
3. **API Integration** - Build robust API clients
4. **Cloud Services** - Type-safe cloud operations

**Write better Python! 🐍**
