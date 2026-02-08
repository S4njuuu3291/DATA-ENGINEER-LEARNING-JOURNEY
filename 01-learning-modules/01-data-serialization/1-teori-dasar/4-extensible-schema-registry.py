"""
Extensible Schema Registry untuk berbagai use case

Pattern ini memudahkan penambahan schema baru tanpa mengubah kode
(Scalable Schema Management)
"""

import json
from typing import Dict, Any
from pathlib import Path


class ExtensibleSchemaRegistry:
    """
    Schema Registry yang mudah di-extend dengan file JSON
    
    Struktur folder:
    schemas/
    ├── crypto_trade.json
    ├── price_aggregate.json
    ├── user_activity.json
    └── metadata_schema.json
    """
    
    def __init__(self, schema_dir: str = "./schemas"):
        self.schema_dir = Path(schema_dir)
        self._cache = {}
        self._load_all_schemas()
    
    def _load_all_schemas(self):
        """Load semua schema dari folder"""
        if not self.schema_dir.exists():
            self.schema_dir.mkdir(parents=True, exist_ok=True)
        
        for schema_file in self.schema_dir.glob("*.json"):
            schema_name = schema_file.stem
            with open(schema_file, "r") as f:
                self._cache[schema_name] = json.load(f)
            print(f"✅ Loaded schema: {schema_name}")
    
    def get_schema(self, schema_name: str) -> Dict[str, Any]:
        """Get schema by name"""
        if schema_name not in self._cache:
            raise ValueError(f"Schema '{schema_name}' not found")
        return self._cache[schema_name]
    
    def list_schemas(self) -> list:
        """List semua available schemas"""
        return list(self._cache.keys())
    
    def add_schema(self, schema_name: str, schema_dict: Dict[str, Any]):
        """Add schema baru ke registry"""
        self._cache[schema_name] = schema_dict
        
        # Save ke file
        schema_file = self.schema_dir / f"{schema_name}.json"
        with open(schema_file, "w") as f:
            json.dump(schema_dict, f, indent=2)
        
        print(f"✅ Schema '{schema_name}' saved to {schema_file}")


# ============================================================================
# Pre-built Schemas (Can be extended)
# ============================================================================

CRYPTO_TRADE_SCHEMA = {
    "type": "record",
    "name": "CryptoTrade",
    "namespace": "com.dataeng.crypto",
    "doc": "Cryptocurrency trade data",
    "fields": [
        {"name": "symbol", "type": "string", "doc": "Trading pair (e.g., BTCUSDT)"},
        {"name": "price", "type": "double", "doc": "Trade price"},
        {"name": "quantity", "type": "double", "doc": "Trade quantity"},
        {"name": "event_time", "type": "long", "logicalType": "timestamp-millis", "doc": "Epoch milliseconds"},
        {"name": "exchange", "type": "string", "doc": "Exchange name"},
    ]
}

PRICE_AGGREGATE_SCHEMA = {
    "type": "record",
    "name": "PriceAggregate",
    "namespace": "com.dataeng.crypto",
    "doc": "Daily price aggregation",
    "fields": [
        {"name": "symbol", "type": "string"},
        {"name": "avg_price", "type": "double"},
        {"name": "min_price", "type": "double"},
        {"name": "max_price", "type": "double"},
        {"name": "total_quantity", "type": "double"},
        {"name": "record_count", "type": "int"},
        {"name": "batch_date", "type": "string", "logicalType": "date"},
    ]
}

# New schemas untuk Airflow batch
BATCH_METADATA_SCHEMA = {
    "type": "record",
    "name": "BatchMetadata",
    "namespace": "com.dataeng.core",
    "doc": "Batch processing metadata",
    "fields": [
        {"name": "batch_id", "type": "string"},
        {"name": "dag_id", "type": "string"},
        {"name": "run_date", "type": "string", "logicalType": "date"},
        {"name": "start_time", "type": "long", "logicalType": "timestamp-millis"},
        {"name": "end_time", "type": "long", "logicalType": "timestamp-millis"},
        {"name": "record_count", "type": "long"},
        {"name": "status", "type": {"type": "enum", "name": "Status", "symbols": ["PENDING", "RUNNING", "SUCCESS", "FAILED"]}},
    ]
}

DATA_QUALITY_SCHEMA = {
    "type": "record",
    "name": "DataQualityReport",
    "namespace": "com.dataeng.quality",
    "doc": "Data quality metrics report",
    "fields": [
        {"name": "batch_id", "type": "string"},
        {"name": "metric_name", "type": "string"},
        {"name": "metric_value", "type": "double"},
        {"name": "status", "type": {"type": "enum", "name": "QualityStatus", "symbols": ["PASS", "WARN", "FAIL"]}},
        {"name": "checked_at", "type": "long", "logicalType": "timestamp-millis"},
    ]
}


# ============================================================================
# Contoh Extension: User Activity Schema (untuk data lain)
# ============================================================================

USER_ACTIVITY_SCHEMA = {
    "type": "record",
    "name": "UserActivity",
    "namespace": "com.dataeng.analytics",
    "doc": "User interaction tracking",
    "fields": [
        {"name": "user_id", "type": "string"},
        {"name": "event_type", "type": "string"},
        {"name": "event_data", "type": "string"},  # JSON as string
        {"name": "timestamp", "type": "long", "logicalType": "timestamp-millis"},
        {"name": "ip_address", "type": "string"},
        {"name": "user_agent", "type": "string"},
    ]
}


if __name__ == "__main__":
    print("=" * 60)
    print("EXTENSIBLE SCHEMA REGISTRY")
    print("=" * 60)
    
    # Initialize registry
    registry = ExtensibleSchemaRegistry("./schemas")
    
    # Add pre-built schemas
    print("\n📝 Adding pre-built schemas...\n")
    registry.add_schema("crypto_trade", CRYPTO_TRADE_SCHEMA)
    registry.add_schema("price_aggregate", PRICE_AGGREGATE_SCHEMA)
    registry.add_schema("batch_metadata", BATCH_METADATA_SCHEMA)
    registry.add_schema("data_quality", DATA_QUALITY_SCHEMA)
    registry.add_schema("user_activity", USER_ACTIVITY_SCHEMA)
    
    # List available schemas
    print("\n📋 Available Schemas:")
    for schema_name in registry.list_schemas():
        schema = registry.get_schema(schema_name)
        print(f"  • {schema_name}: {schema.get('doc', 'No description')}")
    
    # Show how to use
    print("\n" + "=" * 60)
    print("USAGE EXAMPLE")
    print("=" * 60)
    
    print("""
# In your Python code:

from extensible_schema_registry import ExtensibleSchemaRegistry
from avro_serializer import AvroSerializer

# Initialize
registry = ExtensibleSchemaRegistry()

# Serialize data
data = [{"symbol": "BTCUSDT", "price": 45000, ...}]
avro_bytes = AvroSerializer.serialize(data, registry.get_schema("crypto_trade"))

# Deserialize
recovered = AvroSerializer.deserialize(avro_bytes, registry.get_schema("crypto_trade"))

# Easy to extend:
# 1. Add new .json schema file ke ./schemas/ folder
# 2. Register it: registry.add_schema("my_schema", schema_dict)
# 3. Use it: serialize(data, registry.get_schema("my_schema"))
    """)
