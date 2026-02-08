# 🌐 API Integration Patterns

Production-ready patterns untuk **REST API integration** dalam data engineering pipelines.

## 🎯 Why API Integration Matters

Modern data engineering = connecting to various APIs:
- ✅ Extract data dari third-party services
- ✅ Push data ke cloud services  
- ✅ Trigger external workflows
- ✅ Real-time data synchronization

---

## 📚 Topics Covered

### 1. REST API Concepts
- HTTP methods (GET, POST, PUT, DELETE)
- Authentication (API keys, OAuth, Bearer tokens)
- Status codes (2xx, 4xx, 5xx)
- Request/response patterns

### 2. Pagination Patterns
- Offset-based pagination
- Cursor-based pagination
- Page-based pagination

### 3. Rate Limiting & Backoff
- Exponential backoff
- Retry strategies
- Rate limit headers

### 4. Error Handling
- Timeout management
- Network failures
- API errors (4xx, 5xx)
- Validation errors

---

## 🚀 Modern HTTP Client (httpx)

```python
import httpx
from typing import List, Dict, Optional
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential

class ModernAPIClient:
    """Production-ready API client dengan best practices."""
    
    def __init__(
        self,
        base_url: str,
        api_key: str,
        timeout: int = 30,
        max_retries: int = 3
    ):
        self.base_url = base_url
        self.timeout = timeout
        self.max_retries = max_retries
        
        # Headers
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'User-Agent': 'DataPipeline/1.0'
        }
        
        # Create client
        self.client = httpx.Client(
            base_url=base_url,
            headers=self.headers,
            timeout=timeout,
            follow_redirects=True
        )
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10)
    )
    def get(self, endpoint: str, params: dict = None) -> dict:
        """GET request dengan retry."""
        try:
            response = self.client.get(endpoint, params=params)
            response.raise_for_status()
            return response.json()
        
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                # Rate limited
                retry_after = int(e.response.headers.get('Retry-After', 60))
                time.sleep(retry_after)
                raise  # Retry
            elif e.response.status_code >= 500:
                # Server error - retry
                raise
            else:
                # Client error - don't retry
                raise ValueError(f"API error: {e.response.text}")
        
        except httpx.TimeoutException:
            raise TimeoutError(f"Request timeout: {endpoint}")
    
    def post(self, endpoint: str, data: dict) -> dict:
        """POST request."""
        response = self.client.post(endpoint, json=data)
        response.raise_for_status()
        return response.json()
    
    def paginate(self, endpoint: str, limit: int = 100) -> List[dict]:
        """Paginate through all results."""
        all_data = []
        page = 1
        
        while True:
            response = self.get(
                endpoint,
                params={'page': page, 'limit': limit}
            )
            
            data = response.get('data', [])
            all_data.extend(data)
            
            if not response.get('has_more', False):
                break
            
            page += 1
        
        return all_data
    
    def close(self):
        """Close client."""
        self.client.close()
```

---

## 📊 Pagination Patterns

### 1. Offset-Based (Simplest)
```python
def fetch_with_offset(base_url: str, limit: int = 100) -> List[dict]:
    """Offset pagination."""
    all_data = []
    offset = 0
    
    while True:
        response = requests.get(
            base_url,
            params={'offset': offset, 'limit': limit}
        )
        
        data = response.json()['results']
        all_data.extend(data)
        
        if len(data) < limit:  # Last page
            break
        
        offset += limit
    
    return all_data
```

### 2. Cursor-Based (Best for large datasets)
```python
def fetch_with_cursor(base_url: str) -> List[dict]:
    """Cursor pagination (stable for real-time data)."""
    all_data = []
    next_cursor = None
    
    while True:
        params = {}
        if next_cursor:
            params['cursor'] = next_cursor
        
        response = requests.get(base_url, params=params)
        data = response.json()
        
        all_data.extend(data['results'])
        
        next_cursor = data.get('next_cursor')
        if not next_cursor:
            break
    
    return all_data
```

### 3. Page-Based (Traditional)
```python
def fetch_with_pages(base_url: str, per_page: int = 100) -> List[dict]:
    """Page-based pagination."""
    all_data = []
    page = 1
    
    while True:
        response = requests.get(
            base_url,
            params={'page': page, 'per_page': per_page}
        )
        
        data = response.json()
        all_data.extend(data['items'])
        
        if page >= data['total_pages']:
            break
        
        page += 1
    
    return all_data
```

---

## 🔐 Authentication Patterns

### 1. API Key (Header)
```python
headers = {
    'X-API-Key': 'your_api_key_here'
}
requests.get(url, headers=headers)
```

### 2. Bearer Token
```python
headers = {
    'Authorization': f'Bearer {access_token}'
}
requests.get(url, headers=headers)
```

### 3. OAuth 2.0
```python
from requests_oauthlib import OAuth2Session

client_id = 'your_client_id'
client_secret = 'your_client_secret'
token_url = 'https://api.example.com/oauth/token'

# Get token
oauth = OAuth2Session(client_id)
token = oauth.fetch_token(
    token_url,
    client_secret=client_secret,
    grant_type='client_credentials'
)

# Use token
response = oauth.get('https://api.example.com/data')
```

---

## ⚡ Rate Limiting & Backoff

### Exponential Backoff
```python
import time
from functools import wraps

def retry_with_backoff(max_retries=3, base_delay=1, max_delay=60):
    """Decorator untuk exponential backoff."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except (requests.HTTPError, requests.Timeout) as e:
                    retries += 1
                    
                    if retries >= max_retries:
                        raise
                    
                    # Exponential backoff: 1s, 2s, 4s, 8s, ...
                    delay = min(base_delay * (2 ** retries), max_delay)
                    
                    print(f"Retry {retries}/{max_retries} after {delay}s")
                    time.sleep(delay)
        
        return wrapper
    return decorator

@retry_with_backoff(max_retries=3)
def fetch_api_data(url):
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.json()
```

---

## 🎯 Best Practices

### ✅ Always Set Timeout
```python
# ❌ Bad - can hang forever
response = requests.get(url)

# ✅ Good - timeout after 30s
response = requests.get(url, timeout=30)

# ✅ Better - separate connect & read timeouts
response = requests.get(url, timeout=(3.05, 27))  # (connect, read)
```

### ✅ Handle Rate Limits
```python
def handle_rate_limit(response):
    """Check rate limit headers."""
    if response.status_code == 429:
        retry_after = int(response.headers.get('Retry-After', 60))
        print(f"Rate limited. Waiting {retry_after}s...")
        time.sleep(retry_after)
        return True
    return False
```

### ✅ Connection Pooling
```python
# Reuse connection untuk multiple requests
session = requests.Session()

for url in urls:
    response = session.get(url)  # Reuses connection!
```

---

## 📖 Complete Example

```python
from typing import List, Dict
import httpx
import logging
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

class ProductionAPIClient:
    """Production-ready API client."""
    
    def __init__(self, base_url: str, api_key: str):
        self.client = httpx.Client(
            base_url=base_url,
            headers={
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            },
            timeout=30.0,
            limits=httpx.Limits(
                max_keepalive_connections=5,
                max_connections=10
            )
        )
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def fetch_data(self, endpoint: str) -> List[dict]:
        """Fetch data dengan pagination."""
        all_data = []
        page = 1
        
        while True:
            try:
                response = self.client.get(
                    endpoint,
                    params={'page': page, 'limit': 100}
                )
                response.raise_for_status()
                
                data = response.json()
                items = data.get('items', [])
                all_data.extend(items)
                
                logger.info(f"Fetched page {page}: {len(items)} items")
                
                if not data.get('has_more'):
                    break
                
                page += 1
                
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:
                    logger.warning("Rate limited, retrying...")
                    raise
                else:
                    logger.error(f"HTTP error: {e}")
                    raise
            
            except httpx.TimeoutException:
                logger.error(f"Timeout on page {page}")
                raise
        
        return all_data
    
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        self.client.close()

# Usage
with ProductionAPIClient('https://api.example.com', 'secret_key') as client:
    data = client.fetch_data('/users')
    print(f"Fetched {len(data)} users")
```

---

**Build robust API integrations! 🌐**
