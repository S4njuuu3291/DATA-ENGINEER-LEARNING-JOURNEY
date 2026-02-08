# 🚀 DATA ENGINEER - Learning Hub

**Comprehensive learning materials** untuk Data Engineering - dari fundamental sampai production-ready patterns.

> 📌 **Philosophy**: Learn by doing. Setiap folder berisi theory + hands-on examples + best practices.

---

## 🎯 Quick Navigation

| 🔴 CRITICAL (Start Here) | 🟡 IMPORTANT | 🟢 ADVANCED |
|-------------------------|--------------|-------------|
| [Workflow Orchestration](#-workflow-orchestration-apache-airflow) | [Cloud Services](#%EF%B8%8F-cloud-data-services) | [Performance Optimization](#-performance--optimization) |
| [Testing Framework](#-data-testing-framework) | [dbt Transformation](#-dbt-transformation) | [Security & Compliance](#-security--compliance) |
| [Python Patterns](#-python-engineering-patterns) | [API Integration](#-api-integration-patterns) | |
| [Pipeline Architecture](#%EF%B8%8F-data-pipeline-architecture) | [DevOps & Infra](#-devops--infrastructure) | |
| [Data Serialization](#-data-serialization-contracts) | | |

---

## 📚 Learning Path (Recommended Order)

### 🔴 Phase 1: FOUNDATIONS (Week 1-2)

#### 1. Python Engineering Patterns
📁 **Folder**: `Python_Engineering_Patterns/`

**Master:**
- ✅ Type hints & Pydantic models
- ✅ Error handling & retry mechanisms  
- ✅ HTTP clients (httpx, requests)
- ✅ Configuration management

**Why Critical:**
> Quality Python code = reliable pipelines. Type safety catches bugs early.

**Start with:**
- [Type Safety & Pydantic](Python_Engineering_Patterns/1-type-safety/)
- [Error Handling](Python_Engineering_Patterns/2-error-handling/)

---

#### 2. Data Testing Framework
📁 **Folder**: `Data_Testing_Framework/`

**Master:**
- ✅ Pytest fundamentals
- ✅ Mocking external services
- ✅ Data validation (Pydantic, Pandera)
- ✅ E2E pipeline testing

**Why Critical:**
> Testing = confidence. Deploy without fear of breaking production.

**Learning Path:**
1. [Basic Testing](Data_Testing_Framework/1-basic-testing/)
2. [Pytest Fundamentals](Data_Testing_Framework/2-pytest-fundamentals/)
3. [Data Validation](Data_Testing_Framework/3-data-validation/)
4. [Quality Checks](Data_Testing_Framework/4-quality-checks/)
5. [Testing Pipelines](Data_Testing_Framework/5-testing-pipelines/)

---

### 🟡 Phase 2: ORCHESTRATION & CLOUD (Week 3-4)

#### 3. Workflow Orchestration (Apache Airflow)
📁 **Folder**: `tools/phase3-airflow/`

**Master:**
- ✅ DAG fundamentals & dependencies
- ✅ TaskFlow API (modern approach)
- ✅ XCom communication
- ✅ Scheduling & retry mechanisms
- ✅ Environment management dalam containers

**Why Important:**
> Airflow = production pipeline orchestration. Schedule, monitor, retry automatically.

**Learning Path:**
1. [DAG Fundamentals](tools/phase3-airflow/1-dag-fundamentals/)
2. [TaskFlow API](tools/phase3-airflow/2-taskflow-api/) ⭐ Modern!
3. [XCom Patterns](tools/phase3-airflow/3-xcom-patterns/)
4. [Scheduling & Retry](tools/phase3-airflow/4-scheduling-retry/)
5. [Environment Config](tools/phase3-airflow/5-environment-config/)

---

#### 4. Cloud Data Services
📁 **Folder**: `Cloud_Data_Services/`

**Master:**
- ✅ Cloud Storage (GCS) operations
- ✅ BigQuery data warehouse
- ✅ Secret Manager
- ✅ GCS → BigQuery pipelines

**Why Important:**
> Modern data engineering = cloud-native. Storage + warehouse + security.

**Topics:**
- [Object Storage (GCS)](Cloud_Data_Services/1-object-storage/)
- [Data Warehouse (BigQuery)](Cloud_Data_Services/2-data-warehouse/)
- [Secrets Management](Cloud_Data_Services/3-secrets-management/)
- [Integration Patterns](Cloud_Data_Services/4-integration-patterns/)

---

#### 5. dbt Transformation
📁 **Folder**: `tools/phase5-dbt/`

**Master:**
- ✅ Layered architecture (staging → mart)
- ✅ Dimensional modeling (fact & dimension)
- ✅ Incremental models
- ✅ Data quality tests
- ✅ Type casting & NULL handling

**Why Important:**
> dbt = SQL-first transformations. Version-controlled, tested, documented.

**Topics:**
- [Project Structure](tools/phase5-dbt/1-project-structure/)
- [Data Modeling](tools/phase5-dbt/2-data-modeling/)
- [Data Quality](tools/phase5-dbt/3-data-quality/)

---

### 🔵 Phase 3: INTEGRATION & ARCHITECTURE (Week 5-6)

#### 6. Data Pipeline Architecture
📁 **Folder**: `Data_Pipeline_Architecture/`

**Master:**
- ✅ ETL vs ELT patterns
- ✅ Dimensional modeling (fact & dimension tables)
- ✅ Data quality (validation, deduplication)
- ✅ File formats (JSON, Parquet, CSV)
- ✅ Idempotency & partitioning

**Why Important:**
> Architecture decisions = long-term success. Choose right patterns from the start.

**Topics:**
- [ETL/ELT Patterns](Data_Pipeline_Architecture/1-etl-elt-patterns/)
- [Data Modeling](Data_Pipeline_Architecture/2-data-modeling/)
- [Data Quality](Data_Pipeline_Architecture/3-data-quality/)
- [File Formats](Data_Pipeline_Architecture/4-file-formats/)

---

#### 7. API Integration Patterns
📁 **Folder**: `API_Integration_Patterns/`

**Master:**
- ✅ REST API concepts
- ✅ Authentication (API keys, OAuth, Bearer tokens)
- ✅ Pagination patterns (offset, cursor, page-based)
- ✅ Rate limiting & exponential backoff
- ✅ Error handling & timeouts

**Why Important:**
> Modern pipelines = API integrations. Extract from 3rd-party services reliably.

---

#### 8. DevOps & Infrastructure
📁 **Folder**: `DevOps_Infrastructure/`

**Master:**
- ✅ Docker containerization
- ✅ docker-compose multi-container setup
- ✅ Git workflow & version control
- ✅ Infrastructure as Code
- ✅ CI/CD patterns

**Why Important:**
> DevOps = reproducible deployments. Same code runs everywhere (dev → prod).

---

### 🟢 Phase 4: ADVANCED TOPICS (Week 7+)

#### 9. Data Serialization Contracts
📁 **Folder**: `Data_Serialization_Contracts/`

**Topics:**
- Avro serialization for Kafka & Airflow
- Schema evolution
- In-memory serialization
- Schema registry patterns

---

#### 10. Real-Time Processing
📁 **Folder**: `tools/phase6-kafka/`, `tools/phase7-spark/`

**Topics:**
- Kafka streaming
- Spark batch/streaming processing

---

## 🎓 Learning Strategies

### For Beginners:
1. **Start with Python Patterns** - Build solid foundation
2. **Practice Testing** - Test-driven development mindset
3. **Learn Airflow Basics** - Understand DAGs & scheduling
4. **Simple Cloud Pipeline** - GCS → BigQuery
5. **dbt Transformations** - SQL-based modeling

**Goal:** Build basic ETL pipeline with testing & orchestration.

---

### For Intermediate:
1. **Advanced Airflow** - TaskFlow API, dynamic DAGs
2. **Cloud Integration** - Multi-service pipelines
3. **API Integrations** - Robust HTTP clients
4. **Data Quality** - Comprehensive validation
5. **DevOps Practices** - Docker, CI/CD

**Goal:** Production-ready pipelines dengan proper error handling.

---

### For Advanced:
1. **Architecture Patterns** - Design scalable systems
2. **Performance Tuning** - Optimize queries & pipelines
3. **Security** - Credential management, RBAC
4. **Real-time Streaming** - Kafka, Spark Streaming
5. **Data Governance** - Lineage, cataloging

**Goal:** Architect & lead data platform initiatives.

---

## 📊 Tech Stack Covered

### Core Tools:
- **Orchestration**: Apache Airflow (TaskFlow API)
- **Transformation**: dbt (data build tool)
- **Cloud**: Google Cloud Platform (GCS, BigQuery, Secret Manager)
- **Testing**: pytest, pytest-httpx, Pydantic, Pandera
- **Serialization**: Apache Avro

### Programming:
- **Language**: Python 3.11+
- **Type Safety**: Pydantic, dataclasses, type hints
- **HTTP**: httpx, requests
- **Async**: asyncio, aiohttp
- **Config**: pydantic-settings, YAML

### Infrastructure:
- **Containers**: Docker, docker-compose
- **Version Control**: Git (conventional commits)
- **CI/CD**: GitHub Actions
- **IaC**: Declarative config files

---

## 🎯 Priority Matrix

### 🔴 CRITICAL (Learn First):
- ✅ Python type safety & validation
- ✅ Pytest testing framework
- ✅ Airflow DAG fundamentals
- ✅ Cloud Storage & BigQuery basics
- ✅ dbt transformations
- ✅ Docker basics
- ✅ Git version control

### 🟡 IMPORTANT (Production Skills):
- ✅ Advanced Airflow patterns
- ✅ E2E testing strategies
- ✅ API integration patterns
- ✅ Error handling & retry
- ✅ Configuration management
- ✅ CI/CD pipelines

### 🟢 ADVANCED (Enhancement):
- ✅ Performance optimization
- ✅ Security & compliance
- ✅ Real-time streaming
- ✅ Advanced data modeling (SCD)
- ✅ Infrastructure as Code

---

## 🗂️ Complete Project Structure

```
DATA-ENGINEER/
├── README.md (this file)
├── 1-terminologi.txt
├── pyproject.toml
│
├── Python_Engineering_Patterns/       🔴 CRITICAL
│   ├── 1-type-safety/
│   ├── 2-error-handling/
│   ├── 3-http-clients/
│   ├── 4-configuration/
│   └── 5-async-patterns/
│
├── Data_Testing_Framework/            🔴 CRITICAL
│   ├── 1-basic-testing/
│   ├── 2-pytest-fundamentals/
│   ├── 3-data-validation/
│   ├── 4-quality-checks/
│   └── 5-testing-pipelines/
│
├── Data_Serialization_Contracts/
│   └── 1-teori-dasar/
│
├── Data_Pipeline_Architecture/        🟡 IMPORTANT
│   ├── 1-etl-elt-patterns/
│   ├── 2-data-modeling/
│   ├── 3-data-quality/
│   ├── 4-file-formats/
│   └── 5-orchestration-patterns/
│
├── Cloud_Data_Services/               🟡 IMPORTANT
│   ├── 1-object-storage/
│   ├── 2-data-warehouse/
│   ├── 3-secrets-management/
│   ├── 4-integration-patterns/
│   └── 5-testing-cloud/
│
├── API_Integration_Patterns/          🟡 IMPORTANT
│   ├── 1-rest-api-basics/
│   ├── 2-authentication/
│   ├── 3-pagination/
│   ├── 4-rate-limiting/
│   └── 5-error-handling/
│
├── DevOps_Infrastructure/             🟡 IMPORTANT
│   ├── 1-docker/
│   ├── 2-docker-compose/
│   ├── 3-git-workflow/
│   ├── 4-infrastructure-as-code/
│   └── 5-cicd/
│
├── tools/
│   ├── phase3-airflow/               🔴 CRITICAL
│   │   ├── 1-dag-fundamentals/
│   │   ├── 2-taskflow-api/
│   │   ├── 3-xcom-patterns/
│   │   ├── 4-scheduling-retry/
│   │   ├── 5-environment-config/
│   │   ├── 6-import-resolution/
│   │   ├── 7-operators-comparison/
│   │   ├── 8-task-execution-patterns/
│   │   └── 9-docker-compose-setup/
│   │
│   ├── phase4-cloud/
│   ├── phase5-dbt/                   🟡 IMPORTANT
│   │   ├── 1-project-structure/
│   │   ├── 2-data-modeling/
│   │   ├── 3-data-quality/
│   │   ├── 4-advanced-patterns/
│   │   └── 5-testing-docs/
│   ├── phase6-kafka/
│   └── phase7-spark/
│
└── project/
    ├── project_1-etl_script/
    ├── project_2-gold-silver-price/
    ├── project_3-metal-price-etl-airflow-gcp/
    ├── project_4-global-commodity/
    └── project_05-realtime-crypto-price-dashboard/
```

---

## 🚀 Quick Start

### 1. Clone & Setup
```bash
cd DATA-ENGINEER

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Start Learning
```bash
# Begin with Python patterns
cd Python_Engineering_Patterns/1-type-safety/
cat README.md

# Run examples
python 2-pydantic-models.py

# Run tests
pytest 2-pydantic-models.py -v
```

### 3. Practice Testing
```bash
cd ../../Data_Testing_Framework/2-pytest-fundamentals/
pytest -v
```

### 4. Try Airflow
```bash
cd ../../tools/phase3-airflow/
docker-compose up
# Access: http://localhost:8080
```

---

## 📖 Learning Resources

### Official Docs:
- [Apache Airflow](https://airflow.apache.org/docs/)
- [dbt Documentation](https://docs.getdbt.com/)
- [Pydantic](https://docs.pydantic.dev/)
- [pytest](https://docs.pytest.org/)
- [Google Cloud](https://cloud.google.com/docs)

### Books:
- "Fundamentals of Data Engineering" - Joe Reis & Matt Housley
- "Designing Data-Intensive Applications" - Martin Kleppmann
- "The Data Warehouse Toolkit" - Ralph Kimball

---

## 🎯 Success Metrics

### After Phase 1 (Foundations):
- [ ] Can write type-safe Python code dengan Pydantic
- [ ] Can test data pipelines dengan pytest
- [ ] Understand testing pyramid (unit → integration → E2E)

### After Phase 2 (Orchestration):
- [ ] Can create Airflow DAGs dengan TaskFlow API
- [ ] Can upload/download dari GCS
- [ ] Can load data ke BigQuery
- [ ] Can write dbt models dengan tests

### After Phase 3 (Integration):
- [ ] Can design ETL/ELT pipelines
- [ ] Can integrate dengan REST APIs
- [ ] Can containerize applications dengan Docker
- [ ] Can implement CI/CD pipelines

### After Phase 4 (Advanced):
- [ ] Can architect scalable data platforms
- [ ] Can optimize query performance
- [ ] Can implement security best practices
- [ ] Can mentor junior engineers

---

## 🤝 Contributing

Found errors or have improvements?
1. Create an issue
2. Submit a PR dengan clear description
3. Follow conventional commits

---

## 📝 Notes

> 💡 **Tip**: Jangan belajar semua sekaligus! Focus on one topic, practice, then move to next.

> ⚠️ **Warning**: Examples use GCP, but concepts apply to AWS/Azure. Adjust accordingly.

> ✅ **Best Practice**: Always test code locally before deploying to cloud.

---

## 🎓 Final Words

**Data Engineering is a journey, not a destination.**

Focus on:
1. **Fundamentals** - Strong Python & testing
2. **Incremental Learning** - One topic at a time
3. **Hands-on Practice** - Build real projects
4. **Best Practices** - Quality over speed
5. **Continuous Learning** - Tech evolves fast

**Happy Learning! 🚀**

---

**Last Updated**: January 2026
**Maintained by**: Your Data Engineering Team
