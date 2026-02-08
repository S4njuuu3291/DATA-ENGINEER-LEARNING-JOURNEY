# 🎨 dbt (Data Build Tool) - Advanced Patterns

Comprehensive guide untuk **data transformation** dalam data warehouse menggunakan dbt.

## 🎯 What is dbt?

**dbt** = Data Build Tool - framework untuk transform data dalam warehouse (BigQuery, Snowflake, Redshift, dll).

### Core Philosophy:
- ✅ SQL-first (familiar untuk data analysts)
- ✅ Version control untuk transformations
- ✅ Testing & documentation built-in
- ✅ Modular & reusable code

---

## 📚 Learning Path

### 🔴 CRITICAL (Must Learn)

#### **1. Project Organization**
Folder: `1-project-structure/`

**Layered Architecture:**
```
models/
├── staging/           # Clean, normalized source data
│   ├── stg_users.sql
│   └── stg_orders.sql
├── intermediate/      # Business logic, joins
│   └── int_user_orders.sql
├── marts/            # Final output (facts & dimensions)
│   ├── dim_users.sql
│   ├── dim_products.sql
│   └── fct_orders.sql
```

**Topics:**
- Staging → Dimension → Fact → Mart layers
- Source definitions
- Project config (dbt_project.yml)
- Connection profiles

---

#### **2. Data Modeling**
Folder: `2-data-modeling/`

**Topics:**
- Dimensional modeling (star/snowflake schema)
- Incremental models
- Materialization strategies (table, view, incremental, ephemeral)
- CTEs (Common Table Expressions)
- Jinja templating

**Example - Fact Table:**
```sql
-- models/marts/fct_orders.sql
{{ config(
    materialized='incremental',
    unique_key='order_id',
    partition_by={
        'field': 'order_date',
        'data_type': 'date'
    }
) }}

with orders as (
    select * from {{ ref('stg_orders') }}
),

users as (
    select * from {{ ref('dim_users') }}
),

final as (
    select
        orders.order_id,
        orders.user_id,
        users.user_name,
        orders.amount,
        orders.order_date
    from orders
    left join users using (user_id)
    
    {% if is_incremental() %}
    where order_date > (select max(order_date) from {{ this }})
    {% endif %}
)

select * from final
```

---

#### **3. Data Quality**
Folder: `3-data-quality/`

**Topics:**
- Type casting (CAST vs SAFE_CAST)
- NULL handling
- Date/timestamp parsing
- Schema tests (not_null, unique, relationships)
- Custom data tests

**Schema Tests:**
```yaml
# models/schema.yml
version: 2

models:
  - name: dim_users
    description: User dimension table
    columns:
      - name: user_id
        description: Primary key
        tests:
          - unique
          - not_null
      
      - name: email
        tests:
          - unique
          - not_null
      
      - name: created_date
        tests:
          - not_null
```

---

### 🟡 IMPORTANT (Production Skills)

#### **4. Advanced Patterns**
Folder: `4-advanced-patterns/`

**Topics:**
- Type mismatch resolution
- Bad data handling
- Column aliasing dalam CTEs
- Partition field optimization
- Slowly Changing Dimensions (SCD Type 2)

---

#### **5. Testing & Documentation**
Folder: `5-testing-docs/`

**Topics:**
- Custom generic tests
- Singular tests
- Documentation generation
- Data lineage

---

## 📁 Complete Folder Structure

```
tools/phase5-dbt/
├── README.md (this file)
├── 1-project-structure/
│   ├── 1-layered-architecture.md
│   ├── 2-sources-and-refs.md
│   ├── 3-project-config.md
│   └── example_project/
├── 2-data-modeling/
│   ├── 1-dimensional-modeling.md
│   ├── 2-incremental-models.sql
│   ├── 3-materialization.md
│   ├── 4-ctes-and-jinja.sql
│   └── README.md
├── 3-data-quality/
│   ├── 1-type-casting.sql
│   ├── 2-null-handling.sql
│   ├── 3-schema-tests.yml
│   ├── 4-custom-tests.sql
│   └── README.md
├── 4-advanced-patterns/
│   ├── 1-type-mismatches.sql
│   ├── 2-scd-type2.sql
│   ├── 3-partitioning.sql
│   └── README.md
└── 5-testing-docs/
    ├── 1-custom-tests.sql
    ├── 2-documentation.md
    └── README.md
```

---

## 🚀 Quick Start

### 1. Basic Model (Staging)
```sql
-- models/staging/stg_users.sql
with source as (
    select * from {{ source('raw', 'users') }}
),

renamed as (
    select
        id as user_id,
        name as user_name,
        email,
        cast(created_at as date) as created_date,
        current_timestamp() as dbt_updated_at
    from source
)

select * from renamed
```

### 2. Dimension Table
```sql
-- models/marts/dim_users.sql
{{ config(materialized='table') }}

with users as (
    select * from {{ ref('stg_users') }}
),

final as (
    select
        user_id,
        user_name,
        email,
        created_date,
        case
            when created_date >= current_date() - interval '30' day
                then 'New'
            else 'Existing'
        end as user_status
    from users
)

select * from final
```

### 3. Fact Table (Incremental)
```sql
-- models/marts/fct_orders.sql
{{ config(
    materialized='incremental',
    unique_key='order_id',
    partition_by={'field': 'order_date', 'data_type': 'date'}
) }}

with orders as (
    select * from {{ ref('stg_orders') }}
),

users as (
    select * from {{ ref('dim_users') }}
),

products as (
    select * from {{ ref('dim_products') }}
),

final as (
    select
        orders.order_id,
        orders.user_id,
        orders.product_id,
        users.user_name,
        products.product_name,
        orders.quantity,
        orders.amount,
        orders.order_date
    from orders
    left join users using (user_id)
    left join products using (product_id)
    
    {% if is_incremental() %}
    -- Only process new records
    where order_date > (select max(order_date) from {{ this }})
    {% endif %}
)

select * from final
```

---

## 🎯 Common Patterns

### Pattern 1: SAFE_CAST untuk Handle Bad Data
```sql
-- models/staging/stg_sales.sql
with source as (
    select * from {{ source('raw', 'sales') }}
),

cleaned as (
    select
        id as sale_id,
        
        -- Safe cast - returns NULL if conversion fails
        safe_cast(amount as float64) as amount,
        safe_cast(quantity as int64) as quantity,
        
        -- Parse dates with error handling
        safe.parse_date('%Y-%m-%d', date_string) as sale_date,
        
        -- Handle NULLs
        coalesce(customer_id, 0) as customer_id,
        
        -- Validate ranges
        case
            when safe_cast(amount as float64) < 0 then null
            else safe_cast(amount as float64)
        end as validated_amount
        
    from source
)

select * from cleaned
where sale_date is not null  -- Filter out bad dates
```

### Pattern 2: Incremental dengan Delete+Insert
```sql
{{ config(
    materialized='incremental',
    unique_key='id',
    on_schema_change='fail'
) }}

select
    id,
    value,
    updated_at,
    current_timestamp() as dbt_loaded_at
from {{ source('raw', 'data') }}

{% if is_incremental() %}
where updated_at > (select max(updated_at) from {{ this }})
{% endif %}
```

### Pattern 3: SCD Type 2 (Slowly Changing Dimension)
```sql
-- models/marts/dim_products_scd.sql
{{ config(materialized='table') }}

with source_data as (
    select * from {{ ref('stg_products') }}
),

existing_data as (
    select * from {{ this }}
    where is_current = true
),

changes as (
    select
        source_data.*,
        existing_data.product_key,
        existing_data.valid_from
    from source_data
    left join existing_data using (product_id)
    where
        -- New record
        existing_data.product_key is null
        
        -- Or changed record
        or (
            source_data.product_name != existing_data.product_name
            or source_data.price != existing_data.price
        )
),

new_records as (
    select
        {{ dbt_utils.generate_surrogate_key(['product_id', 'current_timestamp()']) }} as product_key,
        product_id,
        product_name,
        price,
        current_timestamp() as valid_from,
        cast(null as timestamp) as valid_to,
        true as is_current
    from changes
    where product_key is null
),

updated_records as (
    -- Close old records
    select
        product_key,
        product_id,
        product_name,
        price,
        valid_from,
        current_timestamp() as valid_to,
        false as is_current
    from changes
    where product_key is not null
    
    union all
    
    -- Open new records
    select
        {{ dbt_utils.generate_surrogate_key(['product_id', 'current_timestamp()']) }} as product_key,
        product_id,
        product_name,
        price,
        current_timestamp() as valid_from,
        cast(null as timestamp) as valid_to,
        true as is_current
    from changes
    where product_key is not null
)

select * from new_records
union all
select * from updated_records
union all
select * from existing_data
where product_id not in (select product_id from changes)
```

---

## 🎓 Best Practices

### ✅ DO's:

1. **Use CTEs:**
   ```sql
   with step_1 as (...),
   step_2 as (...),
   final as (...)
   select * from final
   ```

2. **Explicit column selection:**
   ```sql
   -- ✅ Good
   select id, name, email from users
   
   -- ❌ Bad
   select * from users
   ```

3. **Proper materialization:**
   ```sql
   -- Staging: view (fast, no storage)
   -- Intermediate: ephemeral (inline CTE)
   -- Marts: table or incremental
   ```

4. **Add tests:**
   ```yaml
   tests:
     - unique
     - not_null
     - relationships:
         to: ref('dim_users')
         field: user_id
   ```

### ❌ DON'Ts:

1. ❌ Don't use `select *` in production
2. ❌ Don't hardcode dates (use `{{ run_started_at }}`)
3. ❌ Don't skip documentation
4. ❌ Don't ignore failed tests
5. ❌ Don't forget partitioning for large tables

---

## 🔗 Integration dengan Airflow

```python
from airflow.decorators import dag, task
from airflow.operators.bash import BashOperator
from datetime import datetime

@dag(
    dag_id='dbt_pipeline',
    schedule='@daily',
    start_date=datetime(2024, 1, 1)
)
def dbt_transformation():
    
    dbt_run = BashOperator(
        task_id='dbt_run',
        bash_command='cd /dbt && dbt run --profiles-dir .'
    )
    
    dbt_test = BashOperator(
        task_id='dbt_test',
        bash_command='cd /dbt && dbt test --profiles-dir .'
    )
    
    dbt_run >> dbt_test

dbt_transformation()
```

---

## 📊 Commands Reference

```bash
# Run all models
dbt run

# Run specific model
dbt run --select stg_users

# Run models in folder
dbt run --select staging.*

# Run tests
dbt test

# Generate documentation
dbt docs generate
dbt docs serve

# Clean old runs
dbt clean

# Compile (check SQL)
dbt compile

# Debug connection
dbt debug
```

---

## 🎯 When to Use What?

| Materialization | Use Case | Storage | Speed |
|----------------|----------|---------|-------|
| **view** | Staging, rarely queried | None | Slow query |
| **table** | Dimensions, frequently queried | Full | Fast query |
| **incremental** | Large facts, append-only | Partial | Fast updates |
| **ephemeral** | Intermediate, inline CTEs | None | N/A |

---

## 📖 Next Steps

Setelah menguasai dbt:
1. **Production deployment** - CI/CD untuk dbt
2. **Advanced testing** - Custom generic tests
3. **Performance** - Query optimization
4. **Monitoring** - dbt Cloud or custom monitoring

**Transform with confidence! 🎨**
