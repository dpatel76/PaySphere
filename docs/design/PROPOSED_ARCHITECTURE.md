# GPS Payments CDM - Proposed Architecture Design

**Version:** 1.0
**Date:** 2024-12-20
**Status:** PROPOSED - Awaiting Approval

---

## 1. Executive Summary

This document presents the proposed architecture for the Global Payment Services Common Domain Model (GPS CDM) Analytics Platform. The platform is designed to:

- Process **50 million payment messages per day**
- Support **16 payment standards** and **13 regulatory reports**
- Provide **end-to-end data lineage** from source to report
- Enable **self-service data provisioning** for consumers
- Support **fraud detection** via graph analytics

### Key Architecture Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Backend Language | Python 3.11+ | Async performance, data ecosystem |
| API Framework | FastAPI | Async-native, OpenAPI, high throughput |
| Frontend | React 19 + TypeScript | Modern, component-based UI |
| Analytical DB | Databricks | Scalable analytics, Unity Catalog |
| Federated Query | Starburst | Cross-platform query federation |
| Graph DB | Neo4J | Fraud detection, lineage visualization |
| Orchestration | Celery + Temporal | Background jobs + long-running workflows |
| CDM Format | JSON Schema + Python dataclasses | Machine-readable, validatable |

---

## 2. System Context

### 2.1 Context Diagram

```
                            +------------------+
                            |   Regulators     |
                            | (FinCEN, AUSTRAC,|
                            |  OFAC, UK NCA)   |
                            +--------^---------+
                                     |
                                     | Regulatory Reports
                                     |
+------------------+         +-------+--------+         +------------------+
|  Source Systems  |         |                |         |  Data Consumers  |
|                  |         |   GPS CDM      |         |                  |
| - Oracle Exadata +-------->+   Platform     +-------->+ - Analytics      |
| - SWIFT Network  |         |                |         | - Risk           |
| - Message Queues | Ingest  |  50M msgs/day  | Provision| - Compliance    |
| - File Feeds     |         |                |         | - Business Units |
+------------------+         +-------+--------+         +------------------+
                                     |
                                     | Lineage & Metrics
                                     v
                            +------------------+
                            |  Data Governance |
                            | (Unity Catalog,  |
                            |  Collibra)       |
                            +------------------+
```

### 2.2 Key Actors

| Actor | Role | Interactions |
|-------|------|--------------|
| **Data Providers** | Supply source payment data | Ingestion connectors |
| **Data Owners** | Manage CDM entities | Catalog management |
| **Data Consumers** | Request data provisions | Self-service portal |
| **Compliance** | Generate regulatory reports | DSL report definitions |
| **Risk/Fraud** | Detect suspicious patterns | Graph analytics |
| **Platform Admin** | Manage platform operations | Admin dashboards |

---

## 3. Logical Architecture

### 3.1 Layered Architecture

```
+=====================================================================+
|                        PRESENTATION LAYER                            |
|  +---------------+  +---------------+  +---------------+             |
|  | Self-Service  |  | Admin         |  | Lineage       |             |
|  | Portal (React)|  | Dashboard     |  | Explorer      |             |
|  +---------------+  +---------------+  +---------------+             |
+=====================================================================+
                              |
                              v
+=====================================================================+
|                          API LAYER (FastAPI)                         |
|  +-------------+  +-------------+  +-------------+  +-------------+  |
|  | Ingestion   |  | Provisioning|  | Lineage     |  | Regulatory  |  |
|  | API         |  | API         |  | API         |  | API         |  |
|  +-------------+  +-------------+  +-------------+  +-------------+  |
+=====================================================================+
                              |
                              v
+=====================================================================+
|                        SERVICE LAYER (Async)                         |
|  +-------------+  +-------------+  +-------------+  +-------------+  |
|  | Ingestion   |  | CDM         |  | Lineage     |  | Quality     |  |
|  | Service     |  | Transform   |  | Capture     |  | Engine      |  |
|  +-------------+  +-------------+  +-------------+  +-------------+  |
|  +-------------+  +-------------+  +-------------+  +-------------+  |
|  | Provisioning|  | DSL         |  | Graph       |  | Catalog     |  |
|  | Engine      |  | Runtime     |  | Analytics   |  | Sync        |  |
|  +-------------+  +-------------+  +-------------+  +-------------+  |
+=====================================================================+
                              |
                              v
+=====================================================================+
|                     DATA ACCESS LAYER                                |
|  +------------------+  +------------------+  +------------------+    |
|  | Databricks       |  | Starburst        |  | Neo4J            |    |
|  | Repository       |  | Repository       |  | Repository       |    |
|  +------------------+  +------------------+  +------------------+    |
+=====================================================================+
                              |
                              v
+=====================================================================+
|                      PERSISTENCE LAYER                               |
|  +------------------+  +------------------+  +------------------+    |
|  | Databricks       |  | Starburst        |  | Neo4J            |    |
|  | (Analytical)     |  | (Federated)      |  | (Graph)          |    |
|  +------------------+  +------------------+  +------------------+    |
+=====================================================================+
```

### 3.2 Component Descriptions

| Component | Responsibility | Key Interfaces |
|-----------|---------------|----------------|
| **Ingestion Service** | Parse & ingest payment messages | Connectors, Parsers |
| **CDM Transform** | Standardize to CDM, Bronze->Silver->Gold | Transformers, Validators |
| **Lineage Capture** | Track field-level transformations | LineageEventEmitter |
| **Quality Engine** | Validate data against rules | RuleRegistry, Metrics |
| **Provisioning Engine** | Generate data feeds & APIs | QueryGenerator, Writers |
| **DSL Runtime** | Execute regulatory report definitions | Compiler, Executor |
| **Graph Analytics** | Fraud detection, network analysis | Neo4J queries |
| **Catalog Sync** | Sync metadata to Unity/Collibra | CatalogService |

---

## 4. Data Architecture

### 4.1 Medallion Architecture

```
+=====================================================================+
|                         BRONZE ZONE                                  |
|  Raw data landing with minimal transformation                        |
|  - Preserve original message format                                  |
|  - Add ingestion metadata (timestamp, source, batch)                 |
|  - Partition by date and source system                               |
|  - Append-only writes                                                |
+=====================================================================+
                              |
                              | Standardization + Validation
                              v
+=====================================================================+
|                         SILVER ZONE                                  |
|  CDM-conformant, cleansed, validated data                            |
|  - Transform to Payments CDM structure                               |
|  - Apply data quality rules                                          |
|  - Deduplicate records                                               |
|  - Enforce referential integrity                                     |
|  - Full lineage from bronze to CDM fields                            |
|  - Bi-temporal versioning (valid_from, valid_to)                     |
+=====================================================================+
                              |
                              | Aggregation + Enrichment
                              v
+=====================================================================+
|                          GOLD ZONE                                   |
|  Universal Business Entity Views & Data Products                     |
|  - Consumption-pattern driven design                                 |
|  - Pre-built universal entity views (360 views)                      |
|  - Domain-specific data products                                     |
|  - Self-service ready datasets                                       |
+=====================================================================+
```

### 4.2 Gold Zone Architecture - Data Products & Universal Views

The Gold Zone organizes CDM-conformant Silver data into **universal business entity views** and **domain-specific data products** designed around consumption patterns.

#### 4.2.1 Universal Business Entity Views (360 Views)

These provide a consolidated, cross-domain view of core business entities:

| Entity View | Description | Source Domains | Key Use Cases |
|-------------|-------------|----------------|---------------|
| **Party 360** | Complete view of counterparty across all interactions | Party, Payment, Account, Compliance | Customer analytics, relationship management, risk assessment |
| **Payment 360** | Full payment lifecycle with all related entities | Payment, Party, Account, Settlement, Events | Payment tracking, reconciliation, dispute resolution |
| **Account 360** | Account activity, balances, and relationships | Account, Party, Payment, Settlement | Balance management, activity monitoring, fraud detection |
| **Institution 360** | Financial institution performance and relationships | FinancialInstitution, Payment, Settlement | Correspondent banking, routing optimization |
| **Compliance 360** | Unified compliance view across all regulatory domains | RegulatoryReport, ComplianceCase, Party, Payment | Regulatory oversight, audit support, risk scoring |

#### 4.2.2 Domain-Specific Data Products

Packaged datasets designed for specific consumption patterns:

| Data Product | Consumers | Update Frequency | Format | Description |
|--------------|-----------|------------------|--------|-------------|
| **Payment Analytics** | BI/Analytics Teams | Hourly | Delta Lake | Aggregated payment metrics by corridor, type, time |
| **Regulatory Ready** | Compliance | Daily | Parquet | Pre-validated data for CTR, SAR, IFTI, FATCA reports |
| **Fraud Features** | ML Platform | Real-time | Feature Store | Pre-computed fraud detection features for ML models |
| **Correspondent Banking** | Treasury | Daily | Delta Lake | Nostro/vostro activity, correspondent performance |
| **Customer Behavior** | Product Teams | Daily | Delta Lake | Payment patterns, channel usage, product adoption |
| **Settlement Analytics** | Operations | Hourly | Delta Lake | Settlement status, fails, timing metrics |
| **Sanctions Screening** | Compliance | Real-time | API | Pre-enriched party data for screening |
| **Lineage Catalog** | Data Governance | On-demand | Graph/API | Field-level lineage for impact analysis |

#### 4.2.3 Gold Zone Physical Tables

```
+=====================================================================+
|                     GOLD ZONE - DATABRICKS                           |
+=====================================================================+
|                                                                      |
|  UNIVERSAL ENTITY VIEWS (360s)                                       |
|  +------------------+  +------------------+  +------------------+    |
|  | gold.party_360   |  | gold.payment_360 |  | gold.account_360 |   |
|  | - party_id       |  | - payment_id     |  | - account_id     |   |
|  | - all_names      |  | - full_lifecycle |  | - all_owners     |   |
|  | - all_accounts   |  | - all_parties    |  | - all_activity   |   |
|  | - total_volume   |  | - all_events     |  | - balance_history|   |
|  | - risk_score     |  | - lineage_path   |  | - risk_indicators|   |
|  | - compliance_flags| | - dq_score       |  | - linked_parties |   |
|  +------------------+  +------------------+  +------------------+    |
|                                                                      |
|  DOMAIN DATA PRODUCTS                                                |
|  +------------------+  +------------------+  +------------------+    |
|  | gold.payment_    |  | gold.regulatory_ |  | gold.fraud_      |   |
|  |     analytics    |  |     ready        |  |     features     |   |
|  | - corridor_stats |  | - ctr_eligible   |  | - velocity_score |   |
|  | - type_breakdown |  | - sar_candidates |  | - network_score  |   |
|  | - hourly_volume  |  | - ifti_reportable|  | - pattern_flags  |   |
|  | - avg_amount     |  | - fatca_accounts |  | - risk_score     |   |
|  +------------------+  +------------------+  +------------------+    |
|                                                                      |
|  AGGREGATION TABLES                                                  |
|  +------------------+  +------------------+  +------------------+    |
|  | gold.daily_      |  | gold.corridor_   |  | gold.institution_|   |
|  |     summary      |  |     metrics      |  |     performance  |   |
|  | - date           |  | - origin_country |  | - institution_id |   |
|  | - total_count    |  | - dest_country   |  | - success_rate   |   |
|  | - total_amount   |  | - avg_time       |  | - avg_latency    |   |
|  | - by_type        |  | - volume         |  | - volume         |   |
|  +------------------+  +------------------+  +------------------+    |
|                                                                      |
+=====================================================================+
```

#### 4.2.4 Consumption Patterns & Access Methods

| Pattern | Access Method | Latency | Optimization |
|---------|---------------|---------|--------------|
| **Interactive Analytics** | SQL via Starburst/Databricks | Sub-second | Pre-aggregated, materialized views |
| **Dashboard/BI** | Direct connection to Gold tables | < 5 sec | Columnar format, partition pruning |
| **ML Training** | Feature Store API | Batch | Point-in-time correct snapshots |
| **ML Inference** | Feature Store API | Real-time | Redis cache, pre-computed |
| **Regulatory Reports** | DSL Runtime | Batch | Pre-filtered, validated datasets |
| **Data Sharing** | Delta Sharing | On-demand | Pre-packaged data products |
| **API Consumers** | REST/GraphQL | < 100ms | Materialized views, caching |

#### 4.2.5 Gold Zone Refresh Strategy

| Table Type | Refresh Frequency | Method | Dependencies |
|------------|-------------------|--------|--------------|
| **360 Views** | Hourly | Incremental merge | All Silver tables |
| **Regulatory Ready** | Daily | Full rebuild | Silver + Reference data |
| **Fraud Features** | Real-time (streaming) | Micro-batch | Silver payments + Graph |
| **Daily Aggregations** | Daily 02:00 UTC | Full rebuild | Silver payments |
| **Hourly Aggregations** | Every hour | Incremental | Silver payments |

### 4.3 CDM Entity Model (29 Entities)

```
+-------------------+       +-------------------+       +-------------------+
|   Payment Core    |       |      Party        |       |     Account       |
+-------------------+       +-------------------+       +-------------------+
| - Payment         |       | - Party           |       | - Account         |
| - PaymentInstr    |<----->| - PartyIdent      |<----->| - CashAccount     |
| - CreditTransfer  |       | - FinancialInst   |       | - AccountOwner    |
| - DirectDebit     |       | - Person          |       +-------------------+
| - PaymentReturn   |       | - Organisation    |
| - PaymentReversal |       +-------------------+
| - StatusReport    |
+-------------------+
         |
         v
+-------------------+       +-------------------+       +-------------------+
|      Amount       |       |    Settlement     |       |    Reference      |
+-------------------+       +-------------------+       +-------------------+
| - Amount          |       | - Settlement      |       | - PaymentTypeInfo |
| - CurrencyExchange|       | - SettlementInstr |       | - RegReporting    |
| - Charges         |       | - ClearingSystem  |       | - RemittanceInfo  |
+-------------------+       +-------------------+       | - Document        |
                                                        +-------------------+
         |
         v
+-------------------+       +-------------------+
|      Events       |       |     Lineage       |
+-------------------+       +-------------------+
| - PaymentEvent    |       | - LineageMetadata |
| - WorkflowEvent   |       | - AuditTrail      |
+-------------------+       +-------------------+
```

### 4.3 Physical Model Distribution

| Platform | Purpose | Entities Stored |
|----------|---------|-----------------|
| **Databricks** | Analytical queries, ML features | All CDM entities (Delta Lake) |
| **Starburst** | Federated queries across sources | Virtual views, query federation |
| **Neo4J** | Graph relationships, fraud detection | Party-Payment-Account graph, Lineage graph |

---

## 5. Data Flow Architecture

### 5.1 Ingestion Flow

```
+-------------+     +-------------+     +-------------+     +-------------+
|   SOURCE    |     |  CONNECTOR  |     |   PARSER    |     |   BRONZE    |
+-------------+     +-------------+     +-------------+     +-------------+
|             |     |             |     |             |     |             |
| Oracle      +---->+ Oracle      +---->+ ISO 20022   +---->+ Raw JSON    |
| Exadata     |     | Connector   |     | Parser      |     | + Metadata  |
|             |     |             |     |             |     |             |
+-------------+     +-------------+     +-------------+     +-------------+
|             |     |             |     |             |     |
| SWIFT MQ    +---->+ MQ          +---->+ MT103       +---->+ Raw JSON    |
|             |     | Connector   |     | Parser      |     | + Metadata  |
|             |     |             |     |             |     |             |
+-------------+     +-------------+     +-------------+     +-------------+
|             |     |             |     |             |     |
| File Feed   +---->+ File        +---->+ ACH/Fedwire +---->+ Raw JSON    |
| (CSV/XML)   |     | Connector   |     | Parser      |     | + Metadata  |
|             |     |             |     |             |     |             |
+-------------+     +-------------+     +-------------+     +-------------+

Throughput Target: 50M messages/day = ~580 messages/second
```

### 5.2 Transformation Flow

```
+-------------+     +-------------+     +-------------+     +-------------+
|   BRONZE    |     | STANDARDIZE |     |  VALIDATE   |     |   SILVER    |
+-------------+     +-------------+     +-------------+     +-------------+
|             |     |             |     |             |     |             |
| Raw Message +---->+ CDM         +---->+ Quality     +---->+ CDM Entity  |
| + Lineage   |     | Transformer |     | Rules       |     | + Lineage   |
|             |     |             |     |             |     |             |
+-------------+     +------+------+     +------+------+     +-------------+
                           |                   |
                           v                   v
                    +-------------+     +-------------+
                    | Lineage     |     | DQ Metrics  |
                    | Graph       |     | Store       |
                    +-------------+     +-------------+
```

### 5.3 Gold Zone Transformation Flow

```
+-------------+     +-------------+     +-------------+     +-------------+
|   SILVER    |     |   JOIN &    |     |  AGGREGATE  |     |    GOLD     |
|   TABLES    |     |   ENRICH    |     |  & COMPUTE  |     |   TABLES    |
+-------------+     +-------------+     +-------------+     +-------------+
|             |     |             |     |             |     |             |
| CDM Payment +---->+ Cross-Domain+---->+ 360 Views   +---->+ party_360   |
| CDM Party   |     | Joins       |     | Calculations|     | payment_360 |
| CDM Account |     | Reference   |     | Metrics     |     | account_360 |
| CDM Events  |     | Enrichment  |     | Scoring     |     |             |
+-------------+     +------+------+     +------+------+     +-------------+
                           |                   |
                           v                   v
+-------------+     +-------------+     +-------------+     +-------------+
|   SILVER    |     | FILTER &    |     |  FORMAT &   |     |    GOLD     |
|   TABLES    |     | VALIDATE    |     |  PACKAGE    |     | DATA PROD   |
+-------------+     +-------------+     +-------------+     +-------------+
|             |     |             |     |             |     |             |
| CDM Payment +---->+ Eligibility +---->+ Regulatory  +---->+ reg_ready   |
| CDM Party   |     | Rules       |     | Formats     |     | fraud_feats |
| Compliance  |     | Thresholds  |     | ML Features |     | analytics   |
+-------------+     +-------------+     +-------------+     +-------------+
                           |
                           v
                    +-------------+
                    | Lineage     |
                    | (Silver->   |
                    |  Gold Edge) |
                    +-------------+
```

#### Gold Zone Processing Jobs

| Job | Schedule | Source | Target | Processing Type |
|-----|----------|--------|--------|-----------------|
| **build_party_360** | Hourly | silver.party, silver.payment, silver.account | gold.party_360 | Incremental merge |
| **build_payment_360** | Hourly | silver.payment, silver.party, silver.events | gold.payment_360 | Incremental merge |
| **build_regulatory_ready** | Daily 01:00 | silver.*, reference.* | gold.regulatory_ready | Full rebuild |
| **compute_fraud_features** | Streaming | silver.payment + Neo4J | gold.fraud_features | Micro-batch |
| **aggregate_daily_metrics** | Daily 02:00 | silver.payment | gold.daily_summary | Full rebuild |
| **aggregate_corridor_metrics** | Hourly | silver.payment | gold.corridor_metrics | Incremental |

### 5.4 Provisioning Flow

```
+-------------+     +-------------+     +-------------+     +-------------+
|   REQUEST   |     |   QUERY     |     |  TRANSFORM  |     |   OUTPUT    |
+-------------+     +-------------+     +-------------+     +-------------+
|             |     |             |     |             |     |             |
| Provisioning+---->+ Query       +---->+ Field       +---->+ CSV/JSON/   |
| Request     |     | Generator   |     | Selection   |     | Parquet     |
|             |     |             |     |             |     |             |
+-------------+     +-------------+     +-------------+     +-------------+
                           |                                       |
                           v                                       v
                    +-------------+                         +-------------+
                    | Lineage     |                         | Consumer    |
                    | Registration|                         | Notification|
                    +-------------+                         +-------------+
```

---

## 6. Integration Architecture

### 6.1 Source System Connectors

| Connector | Protocol | Features |
|-----------|----------|----------|
| **Oracle Exadata** | JDBC/OCI | Connection pooling, CDC, parallel queries |
| **File** | SFTP/S3/Local | Streaming, checkpointing, schema inference |
| **Message Queue** | Kafka/IBM MQ/RabbitMQ | Consumer groups, offset tracking |
| **API** | REST/GraphQL | OAuth, rate limiting, pagination |

### 6.2 Parser Registry

| Parser | Message Types | Priority |
|--------|---------------|----------|
| **ISO20022Parser** | pain.*, pacs.*, camt.* | High |
| **SwiftMTParser** | MT1xx, MT2xx, MT9xx | High |
| **USPaymentParser** | Fedwire, CHIPS, ACH | High |
| **EUPaymentParser** | SEPA SCT, SEPA Inst | High |
| **CardParser** | ISO 8583, Visa, MC | Medium |
| **RegionalParser** | PIX, UPI, PayNow, PromptPay | Medium |

### 6.3 External Integrations

```
+-------------------+     +-------------------+     +-------------------+
|   Unity Catalog   |     |     Collibra      |     |   Notification    |
+-------------------+     +-------------------+     +-------------------+
|                   |     |                   |     |                   |
| - CDM Schemas     |     | - Data Dictionary |     | - Email (SMTP)    |
| - Access Control  |     | - Business Glossary|    | - Slack           |
| - Lineage         |     | - DQ Scores       |     | - Teams           |
|                   |     |                   |     |                   |
+-------------------+     +-------------------+     +-------------------+
         ^                         ^                         ^
         |                         |                         |
         +-----------+-------------+-----------+-------------+
                     |                         |
              +------+------+           +------+------+
              | Catalog     |           | Notification|
              | Sync Service|           | Service     |
              +-------------+           +-------------+
```

---

## 7. Lineage Architecture

### 7.1 Lineage Data Model

```
+-------------------+         +-------------------+
|   LineageNode     |         |   LineageEdge     |
+-------------------+         +-------------------+
| - node_id (UUID)  |         | - edge_id (UUID)  |
| - node_type       |<--------+ - source_node_id  |
| - system_name     |         | - target_node_id  |
| - entity_name     |         | - transform_type  |
| - field_name      |         | - transform_logic |
| - field_path      |         | - confidence      |
| - data_type       |         | - effective_from  |
+-------------------+         +-------------------+
         ^
         |
+-------------------+
|  LineageConsumer  |
+-------------------+
| - consumer_id     |
| - consumer_type   |
| - consumer_name   |
| - fields_consumed |
| - criticality     |
+-------------------+
```

### 7.2 Lineage Node Types

```
SOURCE_FIELD --> BRONZE_FIELD --> SILVER_FIELD --> GOLD_FIELD
                                        |
                                        +---> REPORT_FIELD
                                        |
                                        +---> FEED_FIELD
                                        |
                                        +---> API_FIELD
```

### 7.3 Lineage Queries

| Query Type | Use Case | Implementation |
|------------|----------|----------------|
| **Forward Lineage** | Impact analysis | Neo4J traversal from source |
| **Backward Lineage** | Root cause analysis | Neo4J traversal to source |
| **Consumer Impact** | Report/feed affected | Graph query to consumers |
| **Blast Radius** | DQ issue scope | Aggregate downstream count |

---

## 8. Regulatory Reporting DSL Architecture

The Regulatory Reporting DSL enables adding new reports entirely through DSL definition - no manual coding required. The DSL compiler generates all implementation code, similar to ISDA DRR's approach.

### 8.1 DSL Design Philosophy

| Principle | Description |
|-----------|-------------|
| **Declarative** | Define WHAT to report, not HOW to generate it |
| **Complete** | DSL covers eligibility, mapping, transformation, validation, and output |
| **Code Generation** | Compiler generates Python/SQL implementation from DSL |
| **Self-Documenting** | DSL serves as living documentation of regulatory requirements |
| **Versionable** | DSL files are version-controlled, enabling audit trail |

### 8.2 DSL Grammar & Structure

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        REPORT DSL STRUCTURE                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  REPORT <report_name>                     ← Report identifier            │
│    METADATA { ... }                       ← Report metadata              │
│    DATA_SOURCES { ... }                   ← CDM entities & joins         │
│    ELIGIBILITY { ... }                    ← Rules for reportable txns    │
│    FIELDS { ... }                         ← Field mappings & transforms  │
│    VALIDATIONS { ... }                    ← Business rule validations    │
│    OUTPUT { ... }                         ← Format & delivery config     │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

#### 8.2.1 Complete DSL Syntax

```dsl
# ============================================================================
# REPORT DEFINITION - Complete Syntax Reference
# ============================================================================

REPORT <ReportName>

  # --------------------------------------------------------------------------
  # METADATA BLOCK - Report identification and scheduling
  # --------------------------------------------------------------------------
  METADATA {
    version:        "<semantic_version>"           # e.g., "2.0.1"
    jurisdiction:   "<country_code>"               # e.g., "US", "AU", "EU"
    regulator:      "<regulator_name>"             # e.g., "FinCEN", "AUSTRAC"
    report_type:    "<type>"                       # CTR | SAR | IFTI | FATCA | CRS | ...
    frequency:      "<schedule>"                   # REALTIME | DAILY | WEEKLY | MONTHLY | ANNUAL
    effective_from: "<date>"                       # When this version becomes active
    effective_to:   "<date>" | NULL                # When this version expires (NULL = current)
    description:    "<text>"                       # Human-readable description
  }

  # --------------------------------------------------------------------------
  # DATA_SOURCES BLOCK - Define source entities and relationships
  # --------------------------------------------------------------------------
  DATA_SOURCES {
    PRIMARY <cdm_entity> AS <alias>

    JOIN <cdm_entity> AS <alias>
      ON <join_condition>
      TYPE [INNER | LEFT | RIGHT]

    LOOKUP <reference_table> AS <alias>
      ON <lookup_condition>
      CACHE [TRUE | FALSE]                         # Cache for performance

    # Subquery support for complex scenarios
    SUBQUERY <alias> {
      SELECT ...
      FROM ...
      WHERE ...
    }
  }

  # --------------------------------------------------------------------------
  # ELIGIBILITY BLOCK - Determine which transactions are reportable
  # --------------------------------------------------------------------------
  ELIGIBILITY {
    # Simple threshold rules
    RULE threshold_check {
      condition: <expression>                      # Boolean expression
      description: "<text>"
    }

    # Aggregation-based rules (e.g., structuring detection)
    RULE aggregate_check {
      aggregate: <SUM | COUNT | AVG | MAX | MIN>
      over: <field>
      partition_by: [<field>, ...]
      window: <time_window>                        # e.g., "24H", "7D", "30D"
      condition: <expression>
    }

    # Combine rules with logic
    COMBINE [ALL | ANY] OF [<rule_name>, ...]      # ALL = AND, ANY = OR

    # Exclusion rules (transactions to skip)
    EXCLUDE WHEN <expression>
  }

  # --------------------------------------------------------------------------
  # FIELDS BLOCK - Define output field mappings and transformations
  # --------------------------------------------------------------------------
  FIELDS {
    FIELD <output_field_name> {
      source:       <cdm_path>                     # e.g., payment.debtor.name
      type:         <data_type>                    # STRING | NUMBER | DATE | BOOLEAN | ENUM
      required:     [TRUE | FALSE]
      max_length:   <integer>                      # For STRING types
      format:       "<format_pattern>"             # e.g., "yyyy-MM-dd", "###,###.00"

      # Transformation pipeline (executed in order)
      transform: [
        <TRANSFORM_FUNCTION>,                      # See transform functions below
        ...
      ]

      # Conditional mapping
      when: <condition>
      default: <value>                             # Default if source is null

      # Enumeration mapping
      enum_map: {
        <source_value>: <target_value>,
        ...
        DEFAULT: <fallback_value>
      }

      # Derived/calculated fields
      derive: <expression>                         # SQL-like expression

      # Nested/repeated fields
      repeat_for: <collection_path>
      nested_fields: { ... }
    }
  }

  # --------------------------------------------------------------------------
  # VALIDATIONS BLOCK - Business rule validations
  # --------------------------------------------------------------------------
  VALIDATIONS {
    VALIDATE <validation_name> {
      rule:        <expression>
      severity:    [ERROR | WARNING | INFO]        # ERROR blocks submission
      message:     "<error_message>"
      error_code:  "<code>"
    }

    # Cross-field validations
    VALIDATE <name> {
      rule: <field1> + <field2> == <field3>
      severity: ERROR
      message: "Amounts must balance"
    }

    # Reference data validations
    VALIDATE <name> {
      rule: <field> IN LOOKUP(<reference_table>.<column>)
      severity: ERROR
      message: "Invalid code"
    }
  }

  # --------------------------------------------------------------------------
  # OUTPUT BLOCK - Format and delivery configuration
  # --------------------------------------------------------------------------
  OUTPUT {
    format:         [XML | JSON | CSV | FIXED_WIDTH | ISO20022]
    schema:         "<xsd_or_json_schema_path>"    # For validation
    template:       "<template_path>"              # Optional template file
    encoding:       "<encoding>"                   # e.g., "UTF-8"

    # File naming convention
    filename_pattern: "<pattern>"                  # e.g., "CTR_{date}_{sequence}.xml"

    # Delivery configuration
    delivery: {
      method:       [SFTP | API | S3 | EMAIL]
      destination:  "<endpoint>"
      credentials:  "<secret_reference>"
      retry_policy: { max_attempts: 3, backoff: "exponential" }
    }

    # Batching rules
    batching: {
      max_records:  <integer>
      max_size:     "<size>"                       # e.g., "100MB"
      split_by:     <field>                        # Split into separate files
    }
  }

# ============================================================================
# TRANSFORM FUNCTIONS (Built-in Library)
# ============================================================================
#
# String Functions:
#   UPPER(<field>)                    - Convert to uppercase
#   LOWER(<field>)                    - Convert to lowercase
#   TRIM(<field>)                     - Remove whitespace
#   LEFT(<field>, n)                  - Left n characters
#   RIGHT(<field>, n)                 - Right n characters
#   SUBSTRING(<field>, start, len)    - Extract substring
#   REPLACE(<field>, old, new)        - Replace occurrences
#   CONCAT(<field1>, <field2>, ...)   - Concatenate fields
#   PAD_LEFT(<field>, len, char)      - Left pad with character
#   PAD_RIGHT(<field>, len, char)     - Right pad with character
#   REGEX_EXTRACT(<field>, pattern)   - Extract via regex
#   MASK(<field>, show_last_n)        - Mask sensitive data
#
# Numeric Functions:
#   ROUND(<field>, decimals)          - Round to n decimals
#   FLOOR(<field>)                    - Round down
#   CEIL(<field>)                     - Round up
#   ABS(<field>)                      - Absolute value
#   CURRENCY_CONVERT(<field>, from, to, rate_date)
#
# Date Functions:
#   FORMAT_DATE(<field>, pattern)     - Format date
#   DATE_ADD(<field>, interval)       - Add to date
#   DATE_DIFF(<field1>, <field2>)     - Difference between dates
#   EXTRACT(<part>, <field>)          - Extract year/month/day/etc.
#   TO_UTC(<field>, source_tz)        - Convert to UTC
#
# Conditional Functions:
#   IF(<condition>, then, else)       - Conditional value
#   COALESCE(<field1>, <field2>, ...) - First non-null
#   NULLIF(<field>, value)            - Return null if equals value
#   CASE WHEN ... THEN ... END        - Case expression
#
# Lookup Functions:
#   LOOKUP(<table>, <key>, <return_col>)
#   ENRICH(<external_api>, <key>)
#
# Aggregation Functions (for repeated groups):
#   SUM(<field>)
#   COUNT(<field>)
#   MAX(<field>)
#   MIN(<field>)
#   FIRST(<field>)
#   LAST(<field>)
#   COLLECT(<field>)                  - Collect into array
```

### 8.3 DSL Examples for Key Reports

#### 8.3.1 FinCEN CTR (Currency Transaction Report)

```dsl
REPORT FinCEN_CTR

  METADATA {
    version:        "2.0.0"
    jurisdiction:   "US"
    regulator:      "FinCEN"
    report_type:    "CTR"
    frequency:      "DAILY"
    effective_from: "2024-01-01"
    description:    "Currency Transaction Report for cash transactions >= $10,000"
  }

  DATA_SOURCES {
    PRIMARY gold.payment_360 AS payment

    JOIN silver.party AS debtor
      ON debtor.party_id = payment.debtor_id
      TYPE INNER

    JOIN silver.party AS creditor
      ON creditor.party_id = payment.creditor_id
      TYPE INNER

    JOIN silver.financial_institution AS fi
      ON fi.fi_id = payment.processing_fi_id
      TYPE INNER

    LOOKUP reference.country_codes AS countries
      ON countries.iso_code = debtor.country
      CACHE TRUE
  }

  ELIGIBILITY {
    # Primary threshold rule
    RULE cash_threshold {
      condition: payment.instructed_amount >= 10000
                 AND payment.currency = 'USD'
                 AND payment.payment_method IN ('CASH', 'CURRENCY')
      description: "Cash transaction >= $10,000 USD"
    }

    # Aggregation rule for structuring detection
    RULE aggregate_threshold {
      aggregate: SUM
      over: payment.instructed_amount
      partition_by: [debtor.party_id, payment.processing_date]
      window: "24H"
      condition: SUM >= 10000
      description: "Multiple cash transactions totaling >= $10,000 in 24 hours"
    }

    # Combine rules - report if ANY rule matches
    COMBINE ANY OF [cash_threshold, aggregate_threshold]

    # Exclusions
    EXCLUDE WHEN payment.payment_type = 'INTERNAL_TRANSFER'
    EXCLUDE WHEN debtor.party_type = 'FINANCIAL_INSTITUTION'
  }

  FIELDS {
    # Part I - Filing Institution Information
    FIELD filingInstitution.name {
      source: fi.legal_name
      type: STRING
      required: TRUE
      max_length: 150
      transform: [UPPER, TRIM]
    }

    FIELD filingInstitution.ein {
      source: fi.tax_id
      type: STRING
      required: TRUE
      transform: [REGEX_EXTRACT("\\d{9}")]
    }

    FIELD filingInstitution.address {
      source: fi.address
      type: STRING
      nested_fields: {
        FIELD street { source: fi.address.street_line1 }
        FIELD city { source: fi.address.city }
        FIELD state { source: fi.address.state }
        FIELD zipCode { source: fi.address.postal_code }
      }
    }

    # Part II - Person Involved in Transaction
    FIELD personInvolved {
      repeat_for: [debtor, creditor]
      nested_fields: {
        FIELD fullName {
          derive: CONCAT(person.last_name, ", ", person.first_name)
          transform: [UPPER, LEFT(150)]
        }

        FIELD tinType {
          source: person.tax_id_type
          enum_map: {
            "SSN": "1"
            "EIN": "2"
            "ITIN": "3"
            "FOREIGN": "4"
            DEFAULT: "0"
          }
        }

        FIELD tin {
          source: person.tax_id
          transform: [MASK(4)]  # Show only last 4 digits in logs
        }

        FIELD dateOfBirth {
          source: person.birth_date
          type: DATE
          format: "yyyy-MM-dd"
        }

        FIELD occupation {
          source: person.occupation
          type: STRING
          max_length: 30
          transform: [UPPER, TRIM]
        }
      }
    }

    # Part III - Transaction Information
    FIELD transactionDate {
      source: payment.value_date
      type: DATE
      required: TRUE
      format: "yyyy-MM-dd"
    }

    FIELD transactionAmount {
      source: payment.instructed_amount
      type: NUMBER
      required: TRUE
      transform: [ROUND(2)]
    }

    FIELD cashInAmount {
      derive: IF(payment.direction = 'INBOUND', payment.instructed_amount, 0)
      type: NUMBER
      transform: [ROUND(2)]
    }

    FIELD cashOutAmount {
      derive: IF(payment.direction = 'OUTBOUND', payment.instructed_amount, 0)
      type: NUMBER
      transform: [ROUND(2)]
    }

    FIELD foreignCurrencyAmount {
      source: payment.foreign_currency_amount
      type: NUMBER
      when: payment.involves_foreign_currency = TRUE
      transform: [ROUND(2)]
    }

    FIELD foreignCurrencyCountry {
      source: payment.foreign_currency_country
      type: STRING
      when: payment.involves_foreign_currency = TRUE
      transform: [LOOKUP(countries, iso_code, name)]
    }
  }

  VALIDATIONS {
    VALIDATE amount_positive {
      rule: transactionAmount > 0
      severity: ERROR
      message: "Transaction amount must be positive"
      error_code: "CTR-001"
    }

    VALIDATE tin_format {
      rule: personInvolved.tin MATCHES "^\\d{9}$" OR personInvolved.tinType = "4"
      severity: ERROR
      message: "TIN must be 9 digits for US persons"
      error_code: "CTR-002"
    }

    VALIDATE cash_balance {
      rule: cashInAmount + cashOutAmount = transactionAmount
      severity: ERROR
      message: "Cash in/out must equal total amount"
      error_code: "CTR-003"
    }

    VALIDATE future_date {
      rule: transactionDate <= CURRENT_DATE()
      severity: ERROR
      message: "Transaction date cannot be in the future"
      error_code: "CTR-004"
    }
  }

  OUTPUT {
    format: XML
    schema: "schemas/fincen/ctr_2.0.xsd"
    template: "templates/fincen_ctr.xml.j2"
    encoding: "UTF-8"
    filename_pattern: "CTR_{filing_date}_{batch_id}.xml"

    delivery: {
      method: SFTP
      destination: "${FINCEN_BSA_ENDPOINT}"
      credentials: "vault://fincen/sftp-credentials"
      retry_policy: { max_attempts: 3, backoff: "exponential" }
    }

    batching: {
      max_records: 10000
      max_size: "50MB"
    }
  }
```

#### 8.3.2 AUSTRAC IFTI (International Funds Transfer Instruction)

```dsl
REPORT AUSTRAC_IFTI

  METADATA {
    version:        "1.0.0"
    jurisdiction:   "AU"
    regulator:      "AUSTRAC"
    report_type:    "IFTI"
    frequency:      "REALTIME"
    effective_from: "2024-01-01"
    description:    "International Funds Transfer Instruction for cross-border payments"
  }

  DATA_SOURCES {
    PRIMARY silver.payment AS payment

    JOIN silver.party AS ordering_customer
      ON ordering_customer.party_id = payment.debtor_id
      TYPE INNER

    JOIN silver.party AS beneficiary
      ON beneficiary.party_id = payment.creditor_id
      TYPE INNER

    JOIN silver.financial_institution AS ordering_institution
      ON ordering_institution.fi_id = payment.debtor_agent_id
      TYPE LEFT

    JOIN silver.financial_institution AS beneficiary_institution
      ON beneficiary_institution.fi_id = payment.creditor_agent_id
      TYPE LEFT
  }

  ELIGIBILITY {
    RULE international_transfer {
      condition: payment.is_cross_border = TRUE
                 AND (payment.debtor_country = 'AU' OR payment.creditor_country = 'AU')
      description: "Cross-border transfer involving Australia"
    }

    RULE electronic_funds_transfer {
      condition: payment.payment_method IN ('WIRE', 'SWIFT', 'RTGS', 'SEPA')
      description: "Electronic funds transfer method"
    }

    COMBINE ALL OF [international_transfer, electronic_funds_transfer]

    EXCLUDE WHEN payment.payment_type = 'CARD_TRANSACTION'
  }

  FIELDS {
    # Report Header
    FIELD reportType {
      derive: "IFTI"
      type: STRING
    }

    FIELD submissionDate {
      derive: CURRENT_TIMESTAMP()
      type: DATE
      format: "yyyy-MM-dd'T'HH:mm:ss"
    }

    # Transfer Details
    FIELD transferDirection {
      derive: IF(payment.debtor_country = 'AU', 'OUTGOING', 'INCOMING')
      type: STRING
      enum_map: {
        "OUTGOING": "O"
        "INCOMING": "I"
      }
    }

    FIELD instructionDate {
      source: payment.creation_date_time
      type: DATE
      format: "yyyy-MM-dd"
    }

    FIELD valueDate {
      source: payment.value_date
      type: DATE
      format: "yyyy-MM-dd"
    }

    FIELD transferAmount {
      source: payment.instructed_amount
      type: NUMBER
      transform: [ROUND(2)]
    }

    FIELD transferCurrency {
      source: payment.currency
      type: STRING
      max_length: 3
    }

    FIELD audEquivalent {
      derive: CURRENCY_CONVERT(payment.instructed_amount,
                               payment.currency,
                               'AUD',
                               payment.value_date)
      type: NUMBER
      transform: [ROUND(2)]
    }

    # Ordering Customer
    FIELD orderingCustomer {
      nested_fields: {
        FIELD fullName {
          source: ordering_customer.name
          type: STRING
          max_length: 200
        }

        FIELD customerType {
          source: ordering_customer.party_type
          enum_map: {
            "INDIVIDUAL": "P"
            "ORGANISATION": "C"
            "TRUST": "T"
            DEFAULT: "O"
          }
        }

        FIELD idType {
          source: ordering_customer.primary_id_type
          type: STRING
        }

        FIELD idNumber {
          source: ordering_customer.primary_id_number
          type: STRING
        }

        FIELD country {
          source: ordering_customer.country
          type: STRING
          max_length: 2
        }
      }
    }

    # Beneficiary
    FIELD beneficiary {
      nested_fields: {
        FIELD fullName {
          source: beneficiary.name
          type: STRING
          max_length: 200
        }

        FIELD country {
          source: beneficiary.country
          type: STRING
          max_length: 2
        }
      }
    }
  }

  VALIDATIONS {
    VALIDATE aus_party_required {
      rule: orderingCustomer.country = 'AU' OR beneficiary.country = 'AU'
      severity: ERROR
      message: "At least one party must be Australian"
      error_code: "IFTI-001"
    }

    VALIDATE valid_currency {
      rule: transferCurrency IN LOOKUP(reference.currencies, iso_code)
      severity: ERROR
      message: "Invalid currency code"
      error_code: "IFTI-002"
    }
  }

  OUTPUT {
    format: XML
    schema: "schemas/austrac/ifti_1.0.xsd"
    encoding: "UTF-8"
    filename_pattern: "IFTI_{timestamp}_{entity_id}.xml"

    delivery: {
      method: API
      destination: "${AUSTRAC_REPORTING_API}"
      credentials: "vault://austrac/api-credentials"
    }
  }
```

### 8.4 DSL Compiler Architecture

The DSL Compiler transforms DSL definitions into executable Python code and SQL queries.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           DSL COMPILER PIPELINE                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐             │
│   │   DSL    │    │  LEXER   │    │  PARSER  │    │   AST    │             │
│   │   File   │───>│          │───>│          │───>│          │             │
│   │  (.dsl)  │    │ (Tokens) │    │ (Grammar)│    │  (Tree)  │             │
│   └──────────┘    └──────────┘    └──────────┘    └────┬─────┘             │
│                                                         │                    │
│   ┌─────────────────────────────────────────────────────┘                    │
│   │                                                                          │
│   v                                                                          │
│   ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                  │
│   │  SEMANTIC    │    │    CODE      │    │   GENERATED  │                  │
│   │  ANALYZER    │───>│  GENERATORS  │───>│     CODE     │                  │
│   │              │    │              │    │              │                  │
│   └──────────────┘    └──────────────┘    └──────────────┘                  │
│         │                    │                    │                          │
│         v                    v                    v                          │
│   ┌──────────┐    ┌─────────────────────────────────────┐                   │
│   │ Validate │    │         Generated Artifacts          │                   │
│   │ - Types  │    │  ┌─────────────┐  ┌─────────────┐   │                   │
│   │ - Refs   │    │  │ Python      │  │ SQL         │   │                   │
│   │ - Logic  │    │  │ Module      │  │ Queries     │   │                   │
│   └──────────┘    │  │ (.py)       │  │ (.sql)      │   │                   │
│                   │  └─────────────┘  └─────────────┘   │                   │
│                   │  ┌─────────────┐  ┌─────────────┐   │                   │
│                   │  │ Pydantic    │  │ Lineage     │   │                   │
│                   │  │ Schemas     │  │ Metadata    │   │                   │
│                   │  │ (.py)       │  │ (.json)     │   │                   │
│                   │  └─────────────┘  └─────────────┘   │                   │
│                   └─────────────────────────────────────┘                   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### 8.4.1 Compiler Components

| Component | Input | Output | Description |
|-----------|-------|--------|-------------|
| **Lexer** | DSL text | Token stream | Tokenizes DSL into keywords, identifiers, operators |
| **Parser** | Token stream | AST | Builds Abstract Syntax Tree per grammar rules |
| **Semantic Analyzer** | AST | Validated AST | Type checking, reference validation, logic validation |
| **Eligibility Generator** | AST | Python + SQL | Generates eligibility check code and queries |
| **Field Mapper Generator** | AST | Python + SQL | Generates field mapping and transformation code |
| **Validator Generator** | AST | Python | Generates validation rule implementations |
| **Output Generator** | AST | Python | Generates serialization and delivery code |
| **Lineage Generator** | AST | JSON | Generates lineage metadata for the report |

#### 8.4.2 Generated Code Structure

For each DSL file, the compiler generates:

```
generated/
└── reports/
    └── fincen_ctr/
        ├── __init__.py                    # Module init
        ├── eligibility.py                 # Eligibility check functions
        ├── eligibility.sql                # Eligibility SQL query
        ├── field_mapper.py                # Field mapping & transforms
        ├── validators.py                  # Validation rules
        ├── output_serializer.py           # XML/JSON serialization
        ├── report_executor.py             # Main orchestration
        ├── schemas.py                     # Pydantic models
        ├── lineage_metadata.json          # Field-level lineage
        └── tests/
            ├── test_eligibility.py
            ├── test_field_mapper.py
            └── test_validators.py
```

#### 8.4.3 Generated Eligibility Code Example

```python
# generated/reports/fincen_ctr/eligibility.py
# AUTO-GENERATED FROM DSL - DO NOT EDIT MANUALLY
# Source: dsl/reports/fincen_ctr.dsl
# Generated: 2024-12-20T10:30:00Z

from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime, timedelta
from decimal import Decimal

from gps_cdm.core.eligibility import EligibilityRule, EligibilityResult
from gps_cdm.data.repositories import PaymentRepository, PartyRepository


@dataclass
class CashThresholdRule(EligibilityRule):
    """Cash transaction >= $10,000 USD"""

    rule_id: str = "cash_threshold"
    description: str = "Cash transaction >= $10,000 USD"

    def evaluate(self, payment: Payment) -> EligibilityResult:
        is_eligible = (
            payment.instructed_amount >= Decimal("10000") and
            payment.currency == "USD" and
            payment.payment_method in ("CASH", "CURRENCY")
        )
        return EligibilityResult(
            rule_id=self.rule_id,
            is_eligible=is_eligible,
            reason=self.description if is_eligible else None
        )


@dataclass
class AggregateThresholdRule(EligibilityRule):
    """Multiple cash transactions totaling >= $10,000 in 24 hours"""

    rule_id: str = "aggregate_threshold"
    description: str = "Multiple cash transactions totaling >= $10,000 in 24 hours"

    def __init__(self, payment_repo: PaymentRepository):
        self.payment_repo = payment_repo

    async def evaluate(self, payment: Payment) -> EligibilityResult:
        window_start = payment.processing_date - timedelta(hours=24)

        total_amount = await self.payment_repo.sum_amount(
            party_id=payment.debtor_id,
            start_date=window_start,
            end_date=payment.processing_date,
            payment_methods=["CASH", "CURRENCY"]
        )

        is_eligible = total_amount >= Decimal("10000")
        return EligibilityResult(
            rule_id=self.rule_id,
            is_eligible=is_eligible,
            aggregate_amount=total_amount,
            reason=self.description if is_eligible else None
        )


class FinCENCTREligibilityChecker:
    """Eligibility checker for FinCEN CTR reports."""

    def __init__(self, payment_repo: PaymentRepository):
        self.rules = [
            CashThresholdRule(),
            AggregateThresholdRule(payment_repo)
        ]
        self.combine_mode = "ANY"  # ANY = OR logic
        self.exclusions = [
            lambda p: p.payment_type == "INTERNAL_TRANSFER",
            lambda p: p.debtor_party_type == "FINANCIAL_INSTITUTION"
        ]

    async def check_eligibility(self, payment: Payment) -> EligibilityResult:
        # Check exclusions first
        for exclusion in self.exclusions:
            if exclusion(payment):
                return EligibilityResult(
                    is_eligible=False,
                    reason="Excluded by exclusion rule"
                )

        # Evaluate all rules
        results = []
        for rule in self.rules:
            result = await rule.evaluate(payment)
            results.append(result)

        # Combine results (ANY = at least one must match)
        is_eligible = any(r.is_eligible for r in results)

        return EligibilityResult(
            is_eligible=is_eligible,
            rule_results=results,
            reason="Matched rules: " + ", ".join(
                r.rule_id for r in results if r.is_eligible
            )
        )
```

#### 8.4.4 Generated SQL Query Example

```sql
-- generated/reports/fincen_ctr/eligibility.sql
-- AUTO-GENERATED FROM DSL - DO NOT EDIT MANUALLY
-- Source: dsl/reports/fincen_ctr.dsl
-- Generated: 2024-12-20T10:30:00Z

WITH cash_threshold AS (
    -- Rule: cash_threshold
    -- Description: Cash transaction >= $10,000 USD
    SELECT
        payment_id,
        'cash_threshold' AS matched_rule
    FROM gold.payment_360 payment
    WHERE payment.instructed_amount >= 10000
      AND payment.currency = 'USD'
      AND payment.payment_method IN ('CASH', 'CURRENCY')
      AND payment.payment_type != 'INTERNAL_TRANSFER'
),

aggregate_threshold AS (
    -- Rule: aggregate_threshold
    -- Description: Multiple cash transactions totaling >= $10,000 in 24 hours
    SELECT
        p.payment_id,
        'aggregate_threshold' AS matched_rule
    FROM gold.payment_360 p
    INNER JOIN (
        SELECT
            debtor_id,
            processing_date,
            SUM(instructed_amount) as total_amount
        FROM gold.payment_360
        WHERE payment_method IN ('CASH', 'CURRENCY')
        GROUP BY debtor_id, processing_date
        HAVING SUM(instructed_amount) >= 10000
    ) agg ON p.debtor_id = agg.debtor_id
         AND p.processing_date = agg.processing_date
    WHERE p.payment_type != 'INTERNAL_TRANSFER'
),

eligible_payments AS (
    -- Combine rules with ANY (OR) logic
    SELECT DISTINCT payment_id, matched_rule
    FROM (
        SELECT * FROM cash_threshold
        UNION ALL
        SELECT * FROM aggregate_threshold
    )
)

SELECT
    p.*,
    e.matched_rule
FROM gold.payment_360 p
INNER JOIN eligible_payments e ON p.payment_id = e.payment_id
WHERE p.processing_date = :report_date
  -- Exclusion: Not internal transfers
  AND p.payment_type != 'INTERNAL_TRANSFER'
  -- Exclusion: Debtor is not a financial institution
  AND p.debtor_party_type != 'FINANCIAL_INSTITUTION';
```

### 8.5 Report Execution Runtime

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         REPORT EXECUTION FLOW                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────┐                                                           │
│  │   Schedule   │  (Temporal/Celery triggers report job)                    │
│  │   Trigger    │                                                           │
│  └──────┬───────┘                                                           │
│         │                                                                    │
│         v                                                                    │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                  │
│  │   Load DSL   │    │   Execute    │    │   Fetch      │                  │
│  │   Config     │───>│   Eligibility│───>│   Eligible   │                  │
│  │              │    │   Query      │    │   Records    │                  │
│  └──────────────┘    └──────────────┘    └──────┬───────┘                  │
│                                                  │                          │
│         ┌────────────────────────────────────────┘                          │
│         │                                                                    │
│         v                                                                    │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                  │
│  │   Apply      │    │   Run        │    │   Serialize  │                  │
│  │   Field      │───>│   Validations│───>│   to Output  │                  │
│  │   Mappings   │    │              │    │   Format     │                  │
│  └──────────────┘    └──────┬───────┘    └──────┬───────┘                  │
│                             │                    │                          │
│                    ┌────────┴────────┐           │                          │
│                    │                 │           │                          │
│                    v                 v           v                          │
│             ┌──────────┐      ┌──────────┐ ┌──────────┐                    │
│             │ Errors   │      │ Warnings │ │  Output  │                    │
│             │ (Block)  │      │ (Log)    │ │  File    │                    │
│             └──────────┘      └──────────┘ └────┬─────┘                    │
│                                                  │                          │
│         ┌────────────────────────────────────────┘                          │
│         │                                                                    │
│         v                                                                    │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                  │
│  │   Deliver    │    │   Register   │    │   Log        │                  │
│  │   to         │───>│   Lineage    │───>│   Audit      │                  │
│  │   Regulator  │    │              │    │   Trail      │                  │
│  └──────────────┘    └──────────────┘    └──────────────┘                  │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 8.6 Adding a New Report (Developer Workflow)

To add a new regulatory report, developers only need to:

```
Step 1: Create DSL file
─────────────────────────────────────────
$ mkdir -p dsl/reports/new_report
$ vi dsl/reports/new_report.dsl
# Write the complete DSL definition

Step 2: Validate DSL
─────────────────────────────────────────
$ python -m gps_cdm.dsl.cli validate dsl/reports/new_report.dsl
✓ Syntax valid
✓ All CDM references valid
✓ All transforms supported
✓ Output schema compatible

Step 3: Generate Code
─────────────────────────────────────────
$ python -m gps_cdm.dsl.cli generate dsl/reports/new_report.dsl
Generated: generated/reports/new_report/eligibility.py
Generated: generated/reports/new_report/eligibility.sql
Generated: generated/reports/new_report/field_mapper.py
Generated: generated/reports/new_report/validators.py
Generated: generated/reports/new_report/output_serializer.py
Generated: generated/reports/new_report/report_executor.py
Generated: generated/reports/new_report/schemas.py
Generated: generated/reports/new_report/lineage_metadata.json
Generated: generated/reports/new_report/tests/*

Step 4: Run Tests
─────────────────────────────────────────
$ pytest generated/reports/new_report/tests/
==================== 24 passed in 2.3s ====================

Step 5: Deploy
─────────────────────────────────────────
$ python -m gps_cdm.dsl.cli deploy dsl/reports/new_report.dsl
✓ Report registered in catalog
✓ Schedule configured (DAILY at 02:00 UTC)
✓ Lineage metadata registered
✓ Ready for production
```

### 8.7 DSL Feature Summary

| Feature | Description | Benefit |
|---------|-------------|---------|
| **Declarative Eligibility** | Define which transactions are reportable using rules | No coding for threshold/aggregation logic |
| **Flexible Joins** | Multiple data source joins with subquery support | Complex data assembly without SQL |
| **Transform Library** | 40+ built-in transform functions | Common transformations out-of-the-box |
| **Enum Mapping** | Source-to-target value mapping | Handle regulatory code translations |
| **Nested Fields** | Support for repeated/nested structures | Handle complex report schemas |
| **Cross-Field Validation** | Business rules across fields | Ensure report integrity |
| **Code Generation** | Full Python + SQL generation | Zero manual coding for new reports |
| **Auto-Testing** | Generated test cases | Built-in quality assurance |
| **Lineage Integration** | Auto-registered lineage metadata | Full traceability from CDM to report |

### 8.8 Regulatory Requirement Traceability Framework

The Traceability Framework ensures bidirectional linkage between regulatory requirements and DSL implementations, enabling compliance verification, gap detection, and change impact analysis.

#### 8.8.1 Traceability Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    REGULATORY TRACEABILITY ARCHITECTURE                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                 REGULATORY REQUIREMENT REGISTRY                       │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │   │
│  │  │ FinCEN      │  │ AUSTRAC     │  │ FATCA/CRS   │  │ UK NCA      │  │   │
│  │  │ Requirements│  │ Requirements│  │ Requirements│  │ Requirements│  │   │
│  │  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  │   │
│  │         │                │                │                │         │   │
│  └─────────┼────────────────┼────────────────┼────────────────┼─────────┘   │
│            │                │                │                │             │
│            v                v                v                v             │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                      TRACEABILITY ENGINE                              │   │
│  │                                                                       │   │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐       │   │
│  │  │ Link Manager    │  │ Gap Detector    │  │ Impact Analyzer │       │   │
│  │  │                 │  │                 │  │                 │       │   │
│  │  │ - Create links  │  │ - Find missing  │  │ - Reg changes   │       │   │
│  │  │ - Validate refs │  │ - Coverage %    │  │ - DSL changes   │       │   │
│  │  │ - Update matrix │  │ - Alert gaps    │  │ - Blast radius  │       │   │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘       │   │
│  │                                                                       │   │
│  └───────────────────────────────┬───────────────────────────────────────┘   │
│                                  │                                           │
│                                  v                                           │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                         DSL RULES WITH ANNOTATIONS                    │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │   │
│  │  │ CTR Rules   │  │ IFTI Rules  │  │ SAR Rules   │  │ FATCA Rules │  │   │
│  │  │ @REQ-CTR-*  │  │ @REQ-IFTI-* │  │ @REQ-SAR-*  │  │ @REQ-FATCA-*│  │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘  │   │
│  │                                                                       │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                         TRACEABILITY OUTPUTS                          │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │   │
│  │  │ Traceability│  │ Coverage    │  │ Gap         │  │ Audit       │  │   │
│  │  │ Matrix      │  │ Reports     │  │ Alerts      │  │ Evidence    │  │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘  │   │
│  │                                                                       │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### 8.8.2 Regulatory Requirement Registry

The Registry is the authoritative source for all regulatory requirements. Each requirement is catalogued with structured metadata.

##### Requirement Schema

```yaml
# registry/requirements/fincen/ctr/REQ-CTR-001.yaml
requirement:
  id: "REQ-CTR-001"

  # Classification
  regulator: "FinCEN"
  regulation: "31 CFR 1010.311"
  report_type: "CTR"
  category: "ELIGIBILITY"          # ELIGIBILITY | FIELD | VALIDATION | FORMAT | TIMING
  subcategory: "THRESHOLD"

  # Requirement Details
  title: "Currency Transaction Reporting Threshold"
  description: |
    Each financial institution shall file a report of each deposit, withdrawal,
    exchange of currency or other payment or transfer, by, through, or to such
    financial institution which involves a transaction in currency of more than $10,000.

  # Source References
  source:
    document: "Bank Secrecy Act - 31 CFR 1010.311"
    section: "1010.311(a)"
    url: "https://www.ecfr.gov/current/title-31/subtitle-B/chapter-X/part-1010/subpart-C/section-1010.311"
    effective_date: "2024-01-01"
    last_amended: "2023-06-15"

  # Requirement Attributes
  attributes:
    threshold_amount: 10000
    threshold_currency: "USD"
    transaction_types: ["CASH", "CURRENCY"]
    aggregation_window: "24H"
    aggregation_required: true

  # Criticality
  criticality: "MANDATORY"         # MANDATORY | RECOMMENDED | OPTIONAL
  penalty_risk: "HIGH"             # Regulatory penalty if not implemented

  # Related Requirements
  related_requirements:
    - "REQ-CTR-002"                # Aggregation requirement
    - "REQ-CTR-015"                # Multiple transactions same day

  # Lifecycle
  status: "ACTIVE"                 # DRAFT | ACTIVE | DEPRECATED | SUPERSEDED
  superseded_by: null

  # Implementation Tracking
  implementation:
    expected_dsl_rules: ["cash_threshold", "aggregate_threshold"]
    expected_dsl_fields: []
    expected_validations: []
    notes: "Must implement both single-transaction and aggregation logic"
```

##### Registry Directory Structure

```
registry/
├── requirements/
│   ├── fincen/
│   │   ├── ctr/
│   │   │   ├── REQ-CTR-001.yaml      # $10K threshold
│   │   │   ├── REQ-CTR-002.yaml      # Aggregation rule
│   │   │   ├── REQ-CTR-003.yaml      # Filing institution info
│   │   │   ├── REQ-CTR-004.yaml      # Person identification
│   │   │   ├── ...
│   │   │   └── REQ-CTR-117.yaml
│   │   ├── sar/
│   │   │   ├── REQ-SAR-001.yaml
│   │   │   └── ...
│   │   └── index.yaml                 # Index of all FinCEN requirements
│   │
│   ├── austrac/
│   │   ├── ifti/
│   │   │   ├── REQ-IFTI-001.yaml
│   │   │   └── ...
│   │   ├── ttr/
│   │   ├── smr/
│   │   └── index.yaml
│   │
│   ├── irs/
│   │   ├── fatca/
│   │   └── index.yaml
│   │
│   ├── oecd/
│   │   ├── crs/
│   │   └── index.yaml
│   │
│   └── master_index.yaml              # Global requirement index
│
├── schemas/
│   └── requirement_schema.json        # JSON Schema for validation
│
└── changelog/
    ├── 2024-01-15_ctr_updates.yaml    # Regulatory change log
    └── ...
```

#### 8.8.3 DSL Traceability Annotations

DSL rules include `@TRACES` annotations that link to regulatory requirements.

##### Enhanced DSL Syntax with Traceability

```dsl
REPORT FinCEN_CTR

  METADATA {
    version:        "2.0.0"
    jurisdiction:   "US"
    regulator:      "FinCEN"
    report_type:    "CTR"

    # Traceability Metadata
    traceability: {
      registry_version: "2024.1.0"
      last_compliance_review: "2024-12-01"
      reviewed_by: "compliance_team@example.com"
      next_review_date: "2025-03-01"
    }
  }

  ELIGIBILITY {

    # ─────────────────────────────────────────────────────────────────────
    # RULE: cash_threshold
    # Implements the primary $10,000 cash transaction threshold
    # ─────────────────────────────────────────────────────────────────────
    RULE cash_threshold {
      condition: payment.instructed_amount >= 10000
                 AND payment.currency = 'USD'
                 AND payment.payment_method IN ('CASH', 'CURRENCY')
      description: "Cash transaction >= $10,000 USD"

      # TRACEABILITY ANNOTATIONS
      @TRACES {
        requirements: [
          {
            id: "REQ-CTR-001"
            coverage: "FULL"           # FULL | PARTIAL | EXTENDS
            notes: "Implements primary threshold check"
          }
        ]

        # Link to specific regulatory text
        regulatory_reference: {
          regulation: "31 CFR 1010.311(a)"
          text_excerpt: "...involves a transaction in currency of more than $10,000"
        }

        # Implementation rationale
        rationale: |
          Threshold set at >= 10000 (not > 10000) per FinCEN guidance that
          transactions of exactly $10,000 are reportable.

        # Test case references
        test_cases: ["TC-CTR-001", "TC-CTR-002", "TC-CTR-003"]
      }
    }

    # ─────────────────────────────────────────────────────────────────────
    # RULE: aggregate_threshold
    # Implements aggregation for multiple transactions
    # ─────────────────────────────────────────────────────────────────────
    RULE aggregate_threshold {
      aggregate: SUM
      over: payment.instructed_amount
      partition_by: [debtor.party_id, payment.processing_date]
      window: "24H"
      condition: SUM >= 10000
      description: "Multiple cash transactions totaling >= $10,000 in 24 hours"

      @TRACES {
        requirements: [
          {
            id: "REQ-CTR-001"
            coverage: "PARTIAL"
            notes: "Aggregation component of threshold requirement"
          },
          {
            id: "REQ-CTR-002"
            coverage: "FULL"
            notes: "Primary implementation of aggregation rule"
          }
        ]

        regulatory_reference: {
          regulation: "31 CFR 1010.313"
          text_excerpt: "...multiple currency transactions shall be treated as
                        a single transaction if the financial institution has
                        knowledge that they are by or on behalf of any person
                        and result in either cash in or cash out totaling more
                        than $10,000"
        }

        rationale: |
          24-hour window based on FinCEN guidance. Partition by debtor and
          processing date to catch structuring attempts.

        test_cases: ["TC-CTR-010", "TC-CTR-011", "TC-CTR-012"]
      }
    }

    COMBINE ANY OF [cash_threshold, aggregate_threshold]

    EXCLUDE WHEN payment.payment_type = 'INTERNAL_TRANSFER' {
      @TRACES {
        requirements: [
          {
            id: "REQ-CTR-050"
            coverage: "FULL"
            notes: "Internal transfers exemption"
          }
        ]
      }
    }
  }

  FIELDS {

    FIELD filingInstitution.name {
      source: fi.legal_name
      type: STRING
      required: TRUE
      max_length: 150
      transform: [UPPER, TRIM]

      @TRACES {
        requirements: [
          {
            id: "REQ-CTR-003"
            coverage: "FULL"
            field_reference: "Part I, Item 2"
          }
        ]

        regulatory_reference: {
          form: "FinCEN Form 112"
          field_number: "2"
          field_name: "Name of financial institution"
        }
      }
    }

    FIELD transactionAmount {
      source: payment.instructed_amount
      type: NUMBER
      required: TRUE
      transform: [ROUND(2)]

      @TRACES {
        requirements: [
          {
            id: "REQ-CTR-025"
            coverage: "FULL"
            field_reference: "Part III, Item 20"
          }
        ]

        regulatory_reference: {
          form: "FinCEN Form 112"
          field_number: "20"
          field_name: "Amount of transaction in U.S. dollars"
        }

        # Field-specific validations traced to requirements
        validation_requirements: ["REQ-CTR-026", "REQ-CTR-027"]
      }
    }
  }

  VALIDATIONS {

    VALIDATE amount_positive {
      rule: transactionAmount > 0
      severity: ERROR
      message: "Transaction amount must be positive"
      error_code: "CTR-001"

      @TRACES {
        requirements: [
          {
            id: "REQ-CTR-027"
            coverage: "FULL"
          }
        ]
      }
    }
  }
```

#### 8.8.4 Traceability Link Types

| Link Type | Direction | Description | Example |
|-----------|-----------|-------------|---------|
| **IMPLEMENTS** | Req → DSL | DSL rule fully implements requirement | `REQ-CTR-001` → `cash_threshold` |
| **PARTIALLY_IMPLEMENTS** | Req → DSL | DSL rule partially implements requirement | `REQ-CTR-001` → `aggregate_threshold` |
| **EXTENDS** | Req → DSL | DSL rule extends beyond requirement | Custom risk scoring beyond reg minimum |
| **EXCLUDES** | Req → DSL | DSL rule implements an exclusion | `REQ-CTR-050` → internal transfer exclusion |
| **VALIDATES** | Req → DSL | Validation rule implements requirement | `REQ-CTR-027` → `amount_positive` |
| **MAPS_FIELD** | Req → DSL | Field mapping implements requirement | `REQ-CTR-003` → `filingInstitution.name` |

#### 8.8.5 Traceability Matrix Generation

The system automatically generates a Requirements Traceability Matrix (RTM) from DSL annotations.

##### Generated Traceability Matrix

```
┌─────────────────────────────────────────────────────────────────────────────┐
│              REQUIREMENTS TRACEABILITY MATRIX - FinCEN CTR                   │
│              Generated: 2024-12-20T10:30:00Z                                 │
│              Registry Version: 2024.1.0                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  SUMMARY                                                                     │
│  ├─ Total Requirements: 117                                                  │
│  ├─ Implemented: 115 (98.3%)                                                 │
│  ├─ Partially Implemented: 2 (1.7%)                                          │
│  ├─ Not Implemented: 0 (0.0%)                                                │
│  └─ Coverage Score: 99.1%                                                    │
│                                                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ELIGIBILITY REQUIREMENTS                                                    │
│  ─────────────────────────────────────────────────────────────────────────  │
│  REQ-CTR-001  │ $10K Threshold        │ IMPLEMENTED  │ cash_threshold,       │
│               │                       │              │ aggregate_threshold   │
│  REQ-CTR-002  │ Aggregation Rule      │ IMPLEMENTED  │ aggregate_threshold   │
│  REQ-CTR-050  │ Internal Xfer Exempt  │ IMPLEMENTED  │ EXCLUDE clause        │
│  ...                                                                         │
│                                                                              │
│  FIELD REQUIREMENTS                                                          │
│  ─────────────────────────────────────────────────────────────────────────  │
│  REQ-CTR-003  │ FI Name               │ IMPLEMENTED  │ filingInstitution.name│
│  REQ-CTR-004  │ FI EIN                │ IMPLEMENTED  │ filingInstitution.ein │
│  REQ-CTR-005  │ FI Address            │ IMPLEMENTED  │ filingInstitution.addr│
│  REQ-CTR-025  │ Transaction Amount    │ IMPLEMENTED  │ transactionAmount     │
│  ...                                                                         │
│                                                                              │
│  VALIDATION REQUIREMENTS                                                     │
│  ─────────────────────────────────────────────────────────────────────────  │
│  REQ-CTR-026  │ Amount Format         │ IMPLEMENTED  │ transform: ROUND(2)   │
│  REQ-CTR-027  │ Amount Positive       │ IMPLEMENTED  │ amount_positive       │
│  ...                                                                         │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### 8.8.6 Gap Detection Engine

The Gap Detector identifies requirements without corresponding DSL implementations.

##### Gap Detection Process

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           GAP DETECTION FLOW                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────┐                                                           │
│  │   Load       │  Load all requirements from registry                      │
│  │   Registry   │  (master_index.yaml → individual requirement files)       │
│  └──────┬───────┘                                                           │
│         │                                                                    │
│         v                                                                    │
│  ┌──────────────┐                                                           │
│  │   Parse      │  Extract all @TRACES annotations from DSL files           │
│  │   DSL Files  │  Build requirement_id → DSL_element map                   │
│  └──────┬───────┘                                                           │
│         │                                                                    │
│         v                                                                    │
│  ┌──────────────┐                                                           │
│  │   Compare    │  For each requirement in registry:                        │
│  │   Coverage   │    - Check if requirement_id exists in DSL map            │
│  └──────┬───────┘    - Verify coverage type (FULL/PARTIAL/NONE)             │
│         │                                                                    │
│         v                                                                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                       │
│  │   COVERED    │  │   PARTIAL    │  │   GAP        │                       │
│  │              │  │              │  │              │                       │
│  │ REQ has at   │  │ REQ has only │  │ REQ has no   │                       │
│  │ least one    │  │ PARTIAL      │  │ implementing │                       │
│  │ FULL impl    │  │ implementations│ │ DSL elements │                       │
│  └──────────────┘  └──────────────┘  └──────┬───────┘                       │
│                                              │                               │
│                                              v                               │
│                                     ┌──────────────┐                        │
│                                     │   Generate   │                        │
│                                     │   Gap Alert  │                        │
│                                     └──────────────┘                        │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

##### Gap Alert Schema

```yaml
# Generated: gaps/fincen_ctr_gaps_2024-12-20.yaml
gap_report:
  report_type: "FinCEN_CTR"
  generated_at: "2024-12-20T10:30:00Z"
  registry_version: "2024.1.0"
  dsl_version: "2.0.0"

  summary:
    total_requirements: 117
    fully_covered: 115
    partially_covered: 2
    not_covered: 0
    coverage_percentage: 98.3

  gaps: []  # Empty when fully compliant

  partial_coverage:
    - requirement_id: "REQ-CTR-089"
      title: "Foreign Currency Reporting"
      category: "FIELD"
      criticality: "MANDATORY"

      current_coverage:
        - dsl_element: "foreignCurrencyAmount"
          coverage: "PARTIAL"
          notes: "Amount captured but source country logic incomplete"

      missing_aspects:
        - "Country of origin for currency must be validated against OFAC list"

      recommended_action: |
        Add LOOKUP validation to foreignCurrencyCountry field to check
        against OFAC sanctioned countries list.

      assigned_to: null
      target_date: null

    - requirement_id: "REQ-CTR-092"
      # ... additional partial coverage items

  # Orphaned DSL elements (implemented but no requirement link)
  orphaned_implementations:
    - dsl_element: "custom_risk_score"
      dsl_file: "fincen_ctr.dsl"
      notes: "Custom implementation beyond regulatory requirements"
      action: "DOCUMENT"  # Link to internal requirement or document as enhancement
```

##### Gap Detection CLI Commands

```bash
# Run gap detection for all reports
$ python -m gps_cdm.traceability.cli detect-gaps
Scanning registry: 487 requirements loaded
Scanning DSL files: 13 reports found

Gap Detection Results:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Report          │ Requirements │ Covered │ Partial │ Gaps  │ Coverage
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  FinCEN_CTR      │     117      │   115   │    2    │   0   │   98.3%
  FinCEN_SAR      │     184      │   184   │    0    │   0   │  100.0%
  AUSTRAC_IFTI    │      87      │    85   │    1    │   1   │   97.7%
  AUSTRAC_TTR     │      76      │    76   │    0    │   0   │  100.0%
  FATCA_8966      │      97      │    97   │    0    │   0   │  100.0%
  ...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  TOTAL           │     487      │   483   │    3    │   1   │   99.2%
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠ 1 GAP DETECTED:
  - REQ-IFTI-045: AUSTRAC_IFTI - "Beneficiary Bank Country Validation"
    Criticality: MANDATORY
    Action Required: Implement country validation for beneficiary bank

Details written to: reports/gap_detection_2024-12-20.yaml

# Run gap detection for specific report
$ python -m gps_cdm.traceability.cli detect-gaps --report FinCEN_CTR

# Generate detailed gap report with recommendations
$ python -m gps_cdm.traceability.cli detect-gaps --detailed --output gap_report.pdf
```

#### 8.8.7 Regulatory Change Impact Analysis

When regulations change, the system analyzes impact on existing DSL implementations.

##### Change Impact Workflow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    REGULATORY CHANGE IMPACT ANALYSIS                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  1. REGULATORY CHANGE NOTIFICATION                                           │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │  Change Notice: FinCEN Amendment to 31 CFR 1010.311                   │   │
│  │  Effective Date: 2025-04-01                                           │   │
│  │  Change Type: THRESHOLD_MODIFICATION                                  │   │
│  │  Summary: CTR threshold lowered from $10,000 to $8,000                │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  2. IMPACT ANALYSIS                                                          │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  $ python -m gps_cdm.traceability.cli analyze-impact \                      │
│      --requirement REQ-CTR-001 \                                            │
│      --change-type THRESHOLD_MODIFICATION \                                  │
│      --new-value 8000                                                        │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │  IMPACT ANALYSIS REPORT                                               │   │
│  │  ════════════════════════════════════════════════════════════════════│   │
│  │                                                                       │   │
│  │  Affected Requirement: REQ-CTR-001                                    │   │
│  │  Change: threshold_amount: 10000 → 8000                               │   │
│  │                                                                       │   │
│  │  AFFECTED DSL ELEMENTS:                                               │   │
│  │  ┌────────────────────────────────────────────────────────────────┐  │   │
│  │  │ 1. RULE: cash_threshold                                        │  │   │
│  │  │    File: dsl/reports/fincen_ctr.dsl:42                         │  │   │
│  │  │    Current: payment.instructed_amount >= 10000                 │  │   │
│  │  │    Required: payment.instructed_amount >= 8000                 │  │   │
│  │  │    Action: UPDATE_THRESHOLD                                    │  │   │
│  │  ├────────────────────────────────────────────────────────────────┤  │   │
│  │  │ 2. RULE: aggregate_threshold                                   │  │   │
│  │  │    File: dsl/reports/fincen_ctr.dsl:58                         │  │   │
│  │  │    Current: SUM >= 10000                                       │  │   │
│  │  │    Required: SUM >= 8000                                       │  │   │
│  │  │    Action: UPDATE_THRESHOLD                                    │  │   │
│  │  └────────────────────────────────────────────────────────────────┘  │   │
│  │                                                                       │   │
│  │  DOWNSTREAM IMPACT:                                                   │   │
│  │  ┌────────────────────────────────────────────────────────────────┐  │   │
│  │  │ • Generated Code: eligibility.py, eligibility.sql              │  │   │
│  │  │ • Test Cases: TC-CTR-001, TC-CTR-002, TC-CTR-010, TC-CTR-011   │  │   │
│  │  │ • Documentation: CTR_User_Guide.md                             │  │   │
│  │  │ • Volume Impact: ~15% increase in reportable transactions      │  │   │
│  │  └────────────────────────────────────────────────────────────────┘  │   │
│  │                                                                       │   │
│  │  RECOMMENDED ACTIONS:                                                 │   │
│  │  □ Update REQ-CTR-001 in registry (threshold: 8000)                  │   │
│  │  □ Modify cash_threshold rule in fincen_ctr.dsl                      │   │
│  │  □ Modify aggregate_threshold rule in fincen_ctr.dsl                 │   │
│  │  □ Regenerate code: python -m gps_cdm.dsl.cli generate               │   │
│  │  □ Update test cases with new threshold                              │   │
│  │  □ Schedule deployment before 2025-04-01                             │   │
│  │                                                                       │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  3. GENERATE CHANGE TASKS                                                    │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  $ python -m gps_cdm.traceability.cli generate-change-tasks \               │
│      --impact-report impact_2025-04-01.yaml \                               │
│      --output jira                                                           │
│                                                                              │
│  Created JIRA tickets:                                                       │
│  • GPS-1234: Update CTR threshold to $8,000 (REQ-CTR-001)                   │
│  • GPS-1235: Update aggregation threshold to $8,000 (REQ-CTR-001)           │
│  • GPS-1236: Regenerate CTR report code                                      │
│  • GPS-1237: Update CTR test cases for new threshold                         │
│  • GPS-1238: Deploy CTR changes before 2025-04-01                            │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### 8.8.8 Audit Evidence Generation

Generate compliance evidence packages for regulatory audits.

##### Audit Evidence Package

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        AUDIT EVIDENCE PACKAGE                                │
│                        FinCEN CTR Compliance                                 │
│                        Generated: 2024-12-20                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  1. EXECUTIVE SUMMARY                                                        │
│     • Report Type: Currency Transaction Report (CTR)                         │
│     • Regulator: FinCEN                                                      │
│     • Compliance Status: FULLY COMPLIANT                                     │
│     • Coverage: 117/117 requirements implemented (100%)                      │
│     • Last Review: 2024-12-01                                                │
│                                                                              │
│  2. REQUIREMENTS TRACEABILITY MATRIX                                         │
│     [Full matrix with all 117 requirements and implementations]              │
│                                                                              │
│  3. REQUIREMENT DETAIL SHEETS                                                │
│     For each requirement:                                                    │
│     • Regulatory source citation                                             │
│     • DSL implementation code                                                │
│     • Generated Python/SQL code                                              │
│     • Test cases and results                                                 │
│     • Sample output data                                                     │
│                                                                              │
│  4. CHANGE HISTORY                                                           │
│     • All changes to DSL files with timestamps                               │
│     • Regulatory changes and implementation dates                            │
│     • Approval records                                                       │
│                                                                              │
│  5. TEST EVIDENCE                                                            │
│     • Test case inventory                                                    │
│     • Test execution results                                                 │
│     • Edge case coverage                                                     │
│                                                                              │
│  6. CERTIFICATION                                                            │
│     • Compliance officer sign-off                                            │
│     • Technical review sign-off                                              │
│     • Effective date confirmation                                            │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

##### Audit Evidence CLI

```bash
# Generate full audit package
$ python -m gps_cdm.traceability.cli generate-audit-package \
    --report FinCEN_CTR \
    --format pdf \
    --output audit_evidence_ctr_2024-12.pdf

Generating Audit Evidence Package...
✓ Loading requirements from registry
✓ Parsing DSL traceability annotations
✓ Building traceability matrix
✓ Collecting test evidence
✓ Generating requirement detail sheets
✓ Compiling change history
✓ Creating PDF document

Audit package generated: audit_evidence_ctr_2024-12.pdf (127 pages)

# Generate for all reports
$ python -m gps_cdm.traceability.cli generate-audit-package --all

# Export to specific format for regulator
$ python -m gps_cdm.traceability.cli generate-audit-package \
    --report FinCEN_CTR \
    --format fincen-xml \
    --output ctr_compliance_attestation.xml
```

#### 8.8.9 Traceability Dashboard

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     REGULATORY TRACEABILITY DASHBOARD                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  OVERALL COMPLIANCE STATUS                                                   │
│  ═══════════════════════════════════════════════════════════════════════════│
│                                                                              │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐              │
│  │   REQUIREMENTS  │  │    COVERAGE     │  │     GAPS        │              │
│  │      487        │  │     99.2%       │  │       1         │              │
│  │    Total        │  │   Implemented   │  │    Open         │              │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘              │
│                                                                              │
│  COVERAGE BY REGULATOR                                                       │
│  ═══════════════════════════════════════════════════════════════════════════│
│                                                                              │
│  FinCEN    ████████████████████████████████████████████████░░  98.7%        │
│  AUSTRAC   █████████████████████████████████████████████████░  99.1%        │
│  IRS       ██████████████████████████████████████████████████  100%         │
│  OECD      ██████████████████████████████████████████████████  100%         │
│  UK NCA    █████████████████████████████████████████████████░  99.5%        │
│                                                                              │
│  RECENT REGULATORY CHANGES                                                   │
│  ═══════════════════════════════════════════════════════════════════════════│
│                                                                              │
│  ⚠ 2025-04-01  FinCEN: CTR threshold change ($10K → $8K)    PENDING         │
│  ✓ 2024-12-01  AUSTRAC: IFTI format v2.1 update             IMPLEMENTED     │
│  ✓ 2024-11-15  IRS: FATCA reporting deadline extension      IMPLEMENTED     │
│                                                                              │
│  UPCOMING COMPLIANCE REVIEWS                                                 │
│  ═══════════════════════════════════════════════════════════════════════════│
│                                                                              │
│  📅 2025-01-15  FinCEN CTR Annual Review                                     │
│  📅 2025-02-01  AUSTRAC IFTI Quarterly Review                                │
│  📅 2025-03-01  FATCA Annual Certification                                   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### 8.8.10 Traceability Data Model

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     TRACEABILITY DATA MODEL                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────────┐         ┌──────────────────┐                          │
│  │   Regulator      │         │   Regulation     │                          │
│  ├──────────────────┤         ├──────────────────┤                          │
│  │ regulator_id     │────────<│ regulation_id    │                          │
│  │ name             │         │ regulator_id (FK)│                          │
│  │ jurisdiction     │         │ title            │                          │
│  │ website          │         │ cfr_reference    │                          │
│  └──────────────────┘         │ effective_date   │                          │
│                               └────────┬─────────┘                          │
│                                        │                                     │
│                                        │ 1:N                                 │
│                                        ▼                                     │
│  ┌──────────────────┐         ┌──────────────────┐                          │
│  │   ReportType     │         │   Requirement    │                          │
│  ├──────────────────┤         ├──────────────────┤                          │
│  │ report_type_id   │────────<│ requirement_id   │                          │
│  │ name             │         │ regulation_id(FK)│                          │
│  │ frequency        │         │ report_type (FK) │                          │
│  │ format           │         │ category         │                          │
│  └──────────────────┘         │ title            │                          │
│                               │ description      │                          │
│                               │ criticality      │                          │
│                               │ status           │                          │
│                               └────────┬─────────┘                          │
│                                        │                                     │
│                                        │ M:N                                 │
│                                        ▼                                     │
│                               ┌──────────────────┐                          │
│                               │ TraceabilityLink │                          │
│                               ├──────────────────┤                          │
│                               │ link_id          │                          │
│                               │ requirement_id   │                          │
│                               │ dsl_element_id   │                          │
│                               │ link_type        │                          │
│                               │ coverage         │                          │
│                               │ notes            │                          │
│                               │ created_at       │                          │
│                               │ created_by       │                          │
│                               └────────┬─────────┘                          │
│                                        │                                     │
│                                        │ N:1                                 │
│                                        ▼                                     │
│  ┌──────────────────┐         ┌──────────────────┐                          │
│  │   DSLReport      │         │   DSLElement     │                          │
│  ├──────────────────┤         ├──────────────────┤                          │
│  │ dsl_report_id    │────────<│ element_id       │                          │
│  │ name             │         │ dsl_report_id(FK)│                          │
│  │ version          │         │ element_type     │  (RULE|FIELD|VALIDATION) │
│  │ file_path        │         │ element_name     │                          │
│  │ last_modified    │         │ source_code      │                          │
│  └──────────────────┘         │ line_number      │                          │
│                               └──────────────────┘                          │
│                                                                              │
│  ┌──────────────────┐         ┌──────────────────┐                          │
│  │   GapRecord      │         │   ChangeImpact   │                          │
│  ├──────────────────┤         ├──────────────────┤                          │
│  │ gap_id           │         │ impact_id        │                          │
│  │ requirement_id   │         │ requirement_id   │                          │
│  │ detected_at      │         │ change_type      │                          │
│  │ severity         │         │ old_value        │                          │
│  │ status           │         │ new_value        │                          │
│  │ resolved_at      │         │ affected_elements│                          │
│  │ resolution_notes │         │ analyzed_at      │                          │
│  └──────────────────┘         └──────────────────┘                          │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### 8.8.11 Integration with CI/CD Pipeline

```yaml
# .github/workflows/compliance-check.yml
name: Compliance Traceability Check

on:
  push:
    paths:
      - 'dsl/**'
      - 'registry/**'
  pull_request:
    paths:
      - 'dsl/**'
      - 'registry/**'

jobs:
  traceability-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install -e .[traceability]

      - name: Validate DSL syntax
        run: python -m gps_cdm.dsl.cli validate dsl/reports/*.dsl

      - name: Check traceability annotations
        run: |
          python -m gps_cdm.traceability.cli validate-annotations \
            --dsl-dir dsl/reports \
            --registry-dir registry/requirements

      - name: Run gap detection
        run: |
          python -m gps_cdm.traceability.cli detect-gaps \
            --fail-on-mandatory-gaps \
            --output gap_report.yaml

      - name: Generate traceability matrix
        run: |
          python -m gps_cdm.traceability.cli generate-matrix \
            --output traceability_matrix.html

      - name: Upload artifacts
        uses: actions/upload-artifact@v3
        with:
          name: compliance-reports
          path: |
            gap_report.yaml
            traceability_matrix.html

      - name: Comment on PR with coverage
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v6
        with:
          script: |
            const fs = require('fs');
            const gaps = JSON.parse(fs.readFileSync('gap_report.yaml'));
            const comment = `## Compliance Traceability Report

            | Metric | Value |
            |--------|-------|
            | Total Requirements | ${gaps.summary.total_requirements} |
            | Covered | ${gaps.summary.fully_covered} |
            | Coverage | ${gaps.summary.coverage_percentage}% |
            | Gaps | ${gaps.gaps.length} |
            `;
            github.rest.issues.createComment({
              ...context.repo,
              issue_number: context.issue.number,
              body: comment
            });
```

#### 8.8.12 Traceability Feature Summary

| Feature | Description | Benefit |
|---------|-------------|---------|
| **Requirement Registry** | Structured catalog of all regulatory requirements | Single source of truth for compliance |
| **DSL Annotations** | `@TRACES` blocks linking rules to requirements | Clear implementation evidence |
| **Bidirectional Links** | Requirement → DSL and DSL → Requirement | Full traceability in both directions |
| **Gap Detection** | Automated identification of unimplemented requirements | Proactive compliance monitoring |
| **Coverage Metrics** | Percentage coverage by report, regulator, category | Quantified compliance status |
| **Change Impact Analysis** | Analyze effect of regulatory changes on DSL | Efficient change management |
| **Audit Evidence Generation** | Automated compliance evidence packages | Reduced audit preparation effort |
| **CI/CD Integration** | Automated traceability checks in pipeline | Continuous compliance verification |
| **Dashboard** | Visual compliance status across all reports | Executive visibility |

---

## 9. Fraud Detection Architecture

### 9.1 Neo4J Graph Model

```
(:Party)-[:SENT_PAYMENT]->(:Payment)-[:RECEIVED_BY]->(:Party)
    |                          |
    v                          v
(:Account)                (:FinancialInstitution)
```

### 9.2 Fraud Detection Patterns

| Pattern | Description | Neo4J Query Pattern |
|---------|-------------|---------------------|
| **Ring Detection** | Circular payment flows | MATCH path = (p)-[:SENT*3..10]->(p) |
| **Velocity Analysis** | High-frequency payments | COUNT within time window |
| **Structuring** | Just-under-threshold | Amount BETWEEN 9000 AND 10000 |
| **Layering** | Multi-hop obfuscation | Path length analysis |

### 9.3 Real-Time Scoring

```
+-------------+     +-------------+     +-------------+     +-------------+
|  Payment    |     |   Graph     |     |   ML Model  |     |   Alert     |
+-------------+     +-------------+     +-------------+     +-------------+
|             |     |             |     |             |     |             |
| New Payment +---->+ Extract     +---->+ Score       +---->+ Generate    |
| Ingested    |     | Features    |     | Payment     |     | Alert       |
|             |     |             |     |             |     |             |
+-------------+     +-------------+     +-------------+     +-------------+
```

---

## 10. Deployment Architecture

### 10.1 Container Architecture

```
+=====================================================================+
|                         KUBERNETES CLUSTER                           |
+=====================================================================+
|                                                                      |
|  +------------------+  +------------------+  +------------------+    |
|  | API Gateway      |  | Load Balancer    |  | Ingress          |    |
|  | (Kong/Nginx)     |  |                  |  | Controller       |    |
|  +------------------+  +------------------+  +------------------+    |
|                                                                      |
|  +------------------+  +------------------+  +------------------+    |
|  | Backend Pods     |  | Worker Pods      |  | Frontend Pods    |    |
|  | (FastAPI)        |  | (Celery)         |  | (React/Nginx)    |    |
|  | Replicas: 10     |  | Replicas: 20     |  | Replicas: 3      |    |
|  +------------------+  +------------------+  +------------------+    |
|                                                                      |
|  +------------------+  +------------------+  +------------------+    |
|  | Redis            |  | PostgreSQL       |  | Temporal         |    |
|  | (Cache/Broker)   |  | (Metadata)       |  | (Workflows)      |    |
|  +------------------+  +------------------+  +------------------+    |
|                                                                      |
+=====================================================================+
|                                                                      |
|  +------------------+  +------------------+  +------------------+    |
|  | Databricks       |  | Starburst        |  | Neo4J            |    |
|  | (Managed)        |  | (Managed)        |  | (Managed)        |    |
|  +------------------+  +------------------+  +------------------+    |
|                                                                      |
+=====================================================================+
```

### 10.2 Scaling Strategy

| Component | Scaling Trigger | Target |
|-----------|-----------------|--------|
| API Pods | CPU > 70% | 10-50 replicas |
| Worker Pods | Queue depth > 1000 | 20-100 replicas |
| Databricks | Data volume | Auto-scale clusters |
| Neo4J | Query latency > 100ms | Read replicas |

---

## 11. Security Architecture

### 11.1 Authentication & Authorization

```
+-------------+     +-------------+     +-------------+
|   User      |     |   OAuth/    |     |   RBAC      |
|             |     |   SAML      |     |   Engine    |
+-------------+     +-------------+     +-------------+
|             |     |             |     |             |
| Request     +---->+ Authenticate+---->+ Authorize   |
|             |     | (JWT Token) |     | (Roles/     |
|             |     |             |     |  Permissions)|
+-------------+     +-------------+     +-------------+
```

### 11.2 Data Security

| Layer | Protection | Implementation |
|-------|------------|----------------|
| **Transport** | TLS 1.3 | All API communications |
| **Storage** | AES-256 | Databricks encryption at rest |
| **Field-Level** | Tokenization | PII fields masked |
| **Access** | Row-Level Security | Unity Catalog policies |

---

## 12. Observability Architecture

### 12.1 Monitoring Stack

```
+-------------+     +-------------+     +-------------+
| Prometheus  |     | Grafana     |     | AlertManager|
| (Metrics)   |     | (Dashboards)|     | (Alerts)    |
+-------------+     +-------------+     +-------------+
      ^                   ^                   ^
      |                   |                   |
      +-------------------+-------------------+
                          |
+-------------+     +-------------+     +-------------+
| Application |     | Database    |     | Infrastructure|
| Metrics     |     | Metrics     |     | Metrics       |
+-------------+     +-------------+     +-------------+
```

### 12.2 Key Metrics

| Category | Metrics |
|----------|---------|
| **Ingestion** | Messages/sec, parse errors, latency |
| **Quality** | DQ pass rate, rule violations |
| **Lineage** | Nodes/edges, query latency |
| **Provisioning** | Requests/hour, file sizes |
| **Regulatory** | Reports generated, validation errors |

---

## 13. Implementation Phases

### Phase 1: Foundation & CDM (Weeks 1-4)
- Finalize CDM logical model
- Create all JSON schemas
- Implement Databricks physical model
- Implement Neo4J graph schema
- Setup development environment

### Phase 2: Ingestion Layer (Weeks 5-8)
- Implement connectors (Oracle, File, MQ, API)
- Implement parsers (ISO 20022, SWIFT, US systems)
- Implement Bronze zone processing
- Setup lineage capture at ingestion

### Phase 3: Transformation & Lineage (Weeks 9-12)
- Implement Silver zone transformers
- Implement lineage graph service
- Implement lineage query APIs
- Build lineage visualization UI

### Phase 4: Quality & Provisioning (Weeks 13-16)
- Implement data quality rules engine
- Implement provisioning engine
- Build self-service portal
- Implement approval workflows

### Phase 5: Regulatory Reporting (Weeks 17-20)
- Implement DSL compiler and runtime
- Implement all 13 regulatory reports
- Validate report outputs
- Build report scheduling

### Phase 6: Fraud & Analytics (Weeks 21-24)
- Implement Neo4J fraud patterns
- Build fraud detection dashboard
- Implement catalog sync (Unity, Collibra)
- Performance optimization

---

## 14. Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| 50M/day throughput | High | Horizontal scaling, async processing |
| Lineage complexity | Medium | Incremental lineage capture, caching |
| Regulatory changes | Medium | DSL-based reports, version control |
| Schema evolution | Medium | Bi-temporal versioning, migrations |
| Integration failures | High | Circuit breakers, retries, DLQ |

---

## 15. Decision Log

| Decision | Date | Rationale | Alternatives Considered |
|----------|------|-----------|------------------------|
| Python over Java | 2024-12-20 | Data ecosystem, async support | Java (RegSphere pattern) |
| FastAPI over Flask | 2024-12-20 | Async-native, OpenAPI | Flask, Django |
| Medallion Architecture | 2024-12-20 | Industry standard, clear zones | Lambda architecture |
| Neo4J for lineage | 2024-12-20 | Graph traversal performance | PostgreSQL JSONB |
| DSL for reports | 2024-12-20 | ISDA DRR pattern, maintainability | Hardcoded reports |

---

## 16. Approval

### Checklist

- [ ] Technology stack approved
- [ ] Data architecture approved
- [ ] Integration patterns approved
- [ ] Security approach approved
- [ ] Deployment strategy approved
- [ ] Implementation phases approved

### Sign-off

| Role | Name | Date | Signature |
|------|------|------|-----------|
| Data Architect | | | |
| Solution Architect | | | |
| Security Architect | | | |
| Platform Owner | | | |

---

**Document Version:** 1.0
**Author:** Claude Code
**Date:** 2024-12-20
**Status:** PROPOSED - Awaiting Approval
