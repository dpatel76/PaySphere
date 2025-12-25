# Workstream 3: Cloud Adoption Strategy - Detailed Approach
## Bank of America - Global Payments Services

**Document Version:** 1.0
**Last Updated:** 2025-12-18
**Workstream Lead:** US Resource (Data Architect)
**Support:** UK Resource (Data Architect)
**Duration:** Months 2-3 (8 weeks)
**Total Effort:** 120 person-days

---

## Table of Contents

1. [Workstream Overview](#overview)
2. [Phase 1: Cloud Readiness Assessment (Weeks 1-2)](#phase1)
3. [Phase 2: Cloud Use Case Prioritization (Weeks 3-4)](#phase2)
4. [Phase 3: Cloud Platform Recommendation (Weeks 5-6)](#phase3)
5. [Phase 4: Cloud Architecture Patterns (Weeks 7-8)](#phase4)
6. [Dependencies & Sequencing](#dependencies)
7. [Risks & Mitigation](#risks)
8. [Quality Gates](#quality-gates)

---

## 1. Workstream Overview {#overview}

### Objective
Define a pragmatic cloud adoption strategy for GPS payments data workloads, focusing on compute-only patterns approved by BofA governance, and identifying high-value use cases that benefit from cloud elasticity, burst capacity, and specialized services (ML training, analytics).

### Scope
- **Approved Pattern:** Compute-only cloud usage (data persistence in cloud requires additional governance approval)
- **Cloud Platforms:** AWS and Azure (BofA-approved)
- **Use Case Categories:** ML model training, batch regulatory reporting, historical analytics, data quality processing, dev/test environments
- **Out of Scope:** Long-term data persistence in cloud (unless governance approval obtained)

### Key Deliverables
| Deliverable | Due Week | Owner |
|-------------|----------|-------|
| Cloud Readiness Assessment | Week 2 | US Lead |
| Cloud Use Case Prioritization Matrix | Week 4 | US Lead |
| Cloud Platform Recommendation (AWS vs Azure) | Week 6 | US Lead |
| Cloud Architecture Patterns (3 patterns) | Week 8 | US Lead |

### Success Criteria
- ✅ 20+ use cases evaluated for cloud candidacy
- ✅ Platform recommendation (AWS or Azure) with justification
- ✅ 3 reference architecture patterns documented
- ✅ InfoSec approval for compute-only pattern
- ✅ Cost model showing positive ROI for prioritized use cases

### Strategic Context
**BofA Constraint:** Compute-only cloud usage is approved. Data persistence in cloud requires additional governance approval due to:
- Data residency compliance (60+ countries with varying regulations)
- Data sovereignty concerns (regulatory data must remain on-premises)
- Security and access control complexity
- Existing Oracle Exadata investment

**Cloud Value Proposition:**
- **Elasticity:** Scale compute up/down based on demand (avoid over-provisioning on-prem)
- **Burst Capacity:** Handle peak workloads (month-end reporting, model training)
- **Specialized Services:** GPU clusters for ML, managed services for analytics
- **Cost Optimization:** Pay-per-use vs. fixed on-prem capacity
- **Innovation Velocity:** Faster provisioning for dev/test, experimentation

---

## 2. Phase 1: Cloud Readiness Assessment (Weeks 1-2) {#phase1}

**Total Effort:** 30 person-days (15 US Lead + 15 UK Support)

### Activity 1.1: Assessment Framework Development (Week 1) {#activity-1-1}

#### Task 1.1.1: Define Cloud Candidacy Assessment Criteria
**Effort:** 3 days (US Lead: 2 days, UK Support: 1 day)
**Dependencies:** None
**Deliverable:** Cloud candidacy assessment framework

**Detailed Steps:**
1. **Define 6 Assessment Criteria:**

**Criterion 1: Compute Intensity (Weight: 20%)**
- Definition: CPU/memory intensity of workload
- Scoring:
  - 5 = Highly compute-intensive (ML training, complex analytics)
  - 4 = Moderately compute-intensive (large-scale batch processing)
  - 3 = Average compute requirements
  - 2 = Low compute (simple queries, small batch jobs)
  - 1 = Minimal compute (metadata operations)
- Rationale: Cloud provides most value for compute-heavy workloads

**Criterion 2: Burst Capacity Needs (Weight: 15%)**
- Definition: Variability between peak and average workload
- Scoring:
  - 5 = >5x burst (month-end spikes, ad-hoc model training)
  - 4 = 3-5x burst
  - 3 = 2-3x burst
  - 2 = <2x burst
  - 1 = Flat workload (no bursting)
- Rationale: Cloud elasticity avoids over-provisioning for peaks

**Criterion 3: Data Sensitivity (Weight: 20%)**
- Definition: Sensitivity classification of data processed
- Scoring (INVERSE - lower sensitivity = higher score):
  - 5 = Public or anonymized data
  - 4 = Internal use, non-PII
  - 3 = Confidential, aggregated data
  - 2 = PII, payment data (masked/tokenized acceptable)
  - 1 = Highly sensitive, untokenized payment data
- Rationale: Lower sensitivity = easier cloud adoption (less governance friction)

**Criterion 4: Latency Tolerance (Weight: 15%)**
- Definition: Acceptable processing latency
- Scoring:
  - 5 = Hours to days acceptable (batch analytics, model training)
  - 4 = Minutes acceptable (near-real-time batch)
  - 3 = Seconds acceptable (low-latency batch)
  - 2 = Sub-second required (real-time queries)
  - 1 = Millisecond required (fraud screening)
- Rationale: Higher latency tolerance = better cloud fit (data transfer overhead)

**Criterion 5: Integration Complexity (Weight: 15%)**
- Definition: Number and complexity of on-prem integrations
- Scoring (INVERSE):
  - 5 = Minimal integration (self-contained workload)
  - 4 = Few integrations (1-2 data sources)
  - 3 = Moderate integration (3-5 data sources)
  - 2 = High integration (6+ data sources, complex orchestration)
  - 1 = Very high integration (real-time sync, tight coupling)
- Rationale: Fewer integrations = simpler cloud adoption

**Criterion 6: Cost Benefit (Weight: 15%)**
- Definition: Projected cloud cost vs. on-prem cost
- Scoring:
  - 5 = >50% cost reduction
  - 4 = 30-50% cost reduction
  - 3 = 10-30% cost reduction
  - 2 = Break-even to 10% reduction
  - 1 = Cost increase vs. on-prem
- Rationale: Positive ROI required for business case

2. **Define Assessment Methodology:**
- Workload profiling (CPU, memory, I/O, duration)
- Data sensitivity classification review
- SLA requirements analysis
- Dependency mapping
- TCO comparison (on-prem vs. cloud)

3. **Create Assessment Scorecard Template:**
- 6 criteria with weights
- Scoring rubric (1-5 scale)
- Weighted score calculation
- Cloud candidacy recommendation (High/Medium/Low)

**Outputs:**
- `cloud_candidacy_assessment_framework.docx` - Complete assessment methodology (20 pages)
- `cloud_candidacy_scorecard_template.xlsx` - Assessment template

**Quality Check:**
- All 6 criteria clearly defined with scoring rubrics?
- Weights sum to 100%?

---

### Activity 1.2: Current State Workload Profiling (Week 2) {#activity-1-2}

#### Task 1.2.1: Identify Payment Data Workloads
**Effort:** 2 days (US Lead: 1 day, UK Support: 1 day)
**Dependencies:** Task 1.1.1, WS1 Activity 1.2 (Use Case Catalog)
**Deliverable:** Workload inventory

**Detailed Steps:**
1. **Catalog existing payment data workloads from WS1 use case catalog:**
   - Regulatory reporting batch jobs (50+ reports)
   - Fraud detection model training (ML workloads)
   - Historical analytics queries (ad-hoc and scheduled)
   - Data quality batch processing (validation, cleansing)
   - End-of-day reconciliation processing
   - Payment flow analytics (BI dashboards)
   - Stress testing and scenario analysis
   - Development and testing environments

2. **For each workload, gather metrics:**
   - Compute resources (CPU cores, memory GB)
   - Processing duration (minutes, hours, days)
   - Frequency (hourly, daily, weekly, monthly, ad-hoc)
   - Peak vs. average resource utilization
   - Data volume processed (GB, TB)
   - Current platform (Oracle Exadata, dedicated servers, etc.)

**Outputs:**
- `cloud_workload_inventory.xlsx` - 30+ workloads profiled

---

#### Task 1.2.2: Workload Profiling & Characterization
**Effort:** 5 days (US Lead: 3 days, UK Support: 2 days)
**Dependencies:** Task 1.2.1
**Deliverable:** Workload profiles with cloud candidacy

**Detailed Steps:**
1. **Profile each workload in detail:**

**Example: ML Model Training for Fraud Detection**
- **Compute Intensity:** Very high (distributed training, 100+ CPU cores, 500GB memory, GPU beneficial)
- **Burst Capacity:** High (ad-hoc training runs, 10x burst when training new model)
- **Data Sensitivity:** Medium (historical payment data, can be anonymized/tokenized)
- **Latency Tolerance:** High (training can take hours, not time-critical)
- **Integration Complexity:** Low (reads from data lake, writes model artifacts)
- **Cost Benefit:** High (GPU instances on-demand vs. permanent GPU infrastructure)

**Example: FinCEN CTR Batch Generation**
- **Compute Intensity:** Moderate (aggregation of 150K transactions/day)
- **Burst Capacity:** Medium (month-end spikes)
- **Data Sensitivity:** High (contains PII, payment data - but output report can be generated in cloud if input data masked)
- **Latency Tolerance:** High (daily batch, 8-hour window)
- **Integration Complexity:** Medium (reads from on-prem data lake, writes report files)
- **Cost Benefit:** Medium (batch compute more cost-effective in cloud)

2. **Apply assessment framework:**
- Score each workload on 6 criteria (1-5 scale)
- Calculate weighted score
- Categorize as High/Medium/Low cloud candidacy

**Outputs:**
- `cloud_workload_profiles.xlsx` - Detailed profiles for 30+ workloads
- `cloud_candidacy_scores.xlsx` - Assessment scores and rankings

---

#### Task 1.2.3: Current State Cost Analysis
**Effort:** 3 days (US Lead: 2 days, UK Support: 1 day)
**Dependencies:** Task 1.2.2
**Deliverable:** Current state cost baseline

**Detailed Steps:**
1. **Calculate current on-prem costs for each workload:**
   - **Infrastructure Cost:** Allocated cost of Oracle Exadata, servers (amortized capex)
   - **Compute Cost:** CPU/memory utilization cost
   - **Storage Cost:** Data storage cost (though cloud is compute-only, need to account for data transfer)
   - **Operational Cost:** DBA, infrastructure support, maintenance
   - **Licensing Cost:** Software licenses (Oracle, etc.)

2. **Normalize to monthly cost per workload**

**Outputs:**
- `cloud_current_state_cost_baseline.xlsx` - On-prem cost per workload

---

#### Task 1.2.4: Consolidate Readiness Assessment
**Effort:** 2 days (US Lead: 2 days)
**Dependencies:** Tasks 1.2.1-1.2.3
**Deliverable:** Cloud readiness assessment report

**Detailed Steps:**
1. Consolidate findings:
   - Workload inventory (30+ workloads)
   - Cloud candidacy scores (ranked by weighted score)
   - Current state costs
   - Top 10 cloud candidates (highest scores)

2. Identify readiness gaps:
   - Security and compliance requirements not yet met
   - Data masking/tokenization capabilities needed
   - Network connectivity requirements (VPN, Direct Connect/ExpressRoute)
   - Skills gaps (cloud platform expertise)

3. Create executive summary

**Outputs:**
- `DELIVERABLE_cloud_readiness_assessment.docx` - Complete assessment (40 pages)
- `cloud_readiness_executive_summary.pptx` - Executive summary

**Quality Gate:** Review with Steering Committee - proceed to use case prioritization?

---

## 3. Phase 2: Cloud Use Case Prioritization (Weeks 3-4) {#phase2}

**Total Effort:** 30 person-days (15 US Lead + 15 UK Support)

### Activity 2.1: High-Potential Use Case Deep Dive (Week 3) {#activity-2-1}

#### Task 2.1.1: ML Model Training Use Case
**Effort:** 3 days (US Lead: 2 days, UK Support: 1 day)
**Dependencies:** Phase 1 complete
**Deliverable:** ML training use case specification

**Detailed Steps:**
1. **Define ML Training Use Case:**
   - **Objective:** Train fraud detection models on historical payment data
   - **Frequency:** Weekly retraining + ad-hoc training for model experiments
   - **Data Volume:** 1TB historical payment data (3 years), anonymized/tokenized
   - **Compute Requirements:** 50-100 CPU cores, 500GB RAM, 4-8 GPUs (for deep learning)
   - **Duration:** 4-8 hours per training run
   - **Current Challenge:** On-prem GPU capacity limited, long queues for GPU access

2. **Data Sampling/Anonymization Approach:**
   - Extract payment data from on-prem lakehouse
   - Apply tokenization (replace account numbers, party names with tokens)
   - Apply k-anonymity for aggregated features
   - Transfer anonymized data to cloud (encrypted, secure transfer)

3. **Cloud Training Pipeline:**
   - **Step 1:** Data extraction and anonymization (on-prem)
   - **Step 2:** Secure data transfer to cloud (AWS S3/Azure Blob, encrypted)
   - **Step 3:** Distributed training in cloud (SageMaker/Azure ML, GPU instances)
   - **Step 4:** Model artifact export (model file, metadata)
   - **Step 5:** Secure transfer back to on-prem (model deployment to production)
   - **Step 6:** Cloud data deletion (ephemeral, deleted after training)

4. **Security Controls:**
   - Data encryption at rest (S3 SSE-KMS, Azure Storage encryption)
   - Data encryption in transit (TLS 1.3)
   - Network isolation (VPC/VNet, private subnets)
   - Access control (IAM roles, least privilege)
   - Audit logging (CloudTrail, Azure Monitor)
   - Data deletion policy (auto-delete after 7 days)

5. **Cost Comparison:**
   - **On-Prem:** $50K/month GPU infrastructure (amortized), low utilization (30%)
   - **Cloud:** $15K/month on-demand GPU instances (pay per use, 100% utilization during training)
   - **Savings:** 70% cost reduction

**Outputs:**
- `cloud_use_case_ml_training.docx` - Detailed use case (15 pages)
- `cloud_ml_training_architecture.vsdx` - Architecture diagram

---

#### Task 2.1.2: Batch Regulatory Reporting Use Case
**Effort:** 3 days (US Lead: 2 days, UK Support: 1 day)
**Dependencies:** Phase 1 complete
**Deliverable:** Batch reporting use case specification

**Detailed Steps:**
1. **Define Batch Regulatory Reporting Use Case:**
   - **Objective:** Generate regulatory reports (CTR, SAR, IFTI, PSD2, etc.) in batch
   - **Frequency:** Daily, weekly, monthly (depending on report)
   - **Data Volume:** 10M-50M transactions per report
   - **Compute Requirements:** High (complex aggregations, transformations)
   - **Duration:** 2-6 hours per report batch
   - **Current Challenge:** Peak month-end loads cause on-prem resource contention

2. **Cloud Batch Processing Pattern:**
   - **Step 1:** Extract transaction data from on-prem lakehouse (masked if needed)
   - **Step 2:** Transfer to cloud (S3/Blob)
   - **Step 3:** Batch processing in cloud (AWS EMR/Databricks on AWS, Azure Databricks)
   - **Step 4:** Generate report files (XML, CSV, JSON)
   - **Step 5:** Transfer reports back to on-prem for submission to regulators
   - **Step 6:** Cloud data deletion

3. **Cost Comparison:**
   - **On-Prem:** Fixed capacity for peak load (over-provisioned 70% of time)
   - **Cloud:** Burst capacity for month-end, scale down rest of month
   - **Savings:** 40% cost reduction

**Outputs:**
- `cloud_use_case_batch_reporting.docx`

---

#### Task 2.1.3: Historical Analytics Use Case
**Effort:** 2 days (US Lead: 1 day, UK Support: 1 day)
**Dependencies:** Phase 1 complete
**Deliverable:** Analytics use case specification

**Detailed Steps:**
1. **Define Historical Analytics Use Case:**
   - **Objective:** Ad-hoc analytics on 5+ years of payment history (large-scale queries)
   - **Frequency:** Ad-hoc (analyst-driven)
   - **Data Volume:** 5-10TB historical data
   - **Compute Requirements:** Variable (small queries to very large)
   - **Current Challenge:** Historical data on slow-tier storage, large queries timeout

2. **Cloud Analytics Pattern:**
   - Historical data replicated to cloud (one-time, archival tier)
   - Ad-hoc queries run on cloud compute (AWS Athena/Redshift Spectrum, Azure Synapse Serverless)
   - Results returned to analysts (BI tools, notebooks)

**Outputs:**
- `cloud_use_case_historical_analytics.docx`

---

#### Task 2.1.4: Data Quality Batch Processing Use Case
**Effort:** 2 days (US Lead: 1 day, UK Support: 1 day)
**Dependencies:** Phase 1 complete
**Deliverable:** Data quality use case specification

**Detailed Steps:**
1. **Define Data Quality Processing Use Case:**
   - **Objective:** Run data quality validation, profiling, cleansing at scale
   - **Frequency:** Daily batch
   - **Data Volume:** Full payment dataset (100M+ records)
   - **Compute Requirements:** High (quality rules execution)

2. **Cloud Quality Processing Pattern:**
   - Extract payment data (sample or full)
   - Run quality rules in cloud (parallel processing)
   - Return quality reports and flagged records

**Outputs:**
- `cloud_use_case_data_quality.docx`

---

#### Task 2.1.5: Dev/Test Environments Use Case
**Effort:** 2 days (US Lead: 1 day, UK Support: 1 day)
**Dependencies:** Phase 1 complete
**Deliverable:** Dev/test use case specification

**Detailed Steps:**
1. **Define Dev/Test Environments Use Case:**
   - **Objective:** Provision dev/test environments on-demand for development, testing, POCs
   - **Frequency:** Ad-hoc
   - **Data Volume:** Subset of production data (10-20%)
   - **Compute Requirements:** Variable
   - **Current Challenge:** Long lead time for on-prem environment provisioning (weeks)

2. **Cloud Dev/Test Pattern:**
   - Provision cloud environments in minutes (IaC - Terraform, CloudFormation)
   - Data subsetting and masking (production-like but smaller, anonymized)
   - Cost management (auto-shutdown when not in use)

**Outputs:**
- `cloud_use_case_devtest.docx`

---

### Activity 2.2: Use Case Prioritization & Business Case (Week 4) {#activity-2-2}

#### Task 2.2.1: Cost-Benefit Analysis per Use Case
**Effort:** 5 days (US Lead: 3 days, UK Support: 2 days)
**Dependencies:** Activity 2.1 complete
**Deliverable:** Cost-benefit analysis

**Detailed Steps:**
1. **For each use case, develop detailed cost model:**

**Cloud Cost Components:**
- Compute cost (EC2/VMs, EMR/Databricks, SageMaker/Azure ML)
- Storage cost (S3/Blob for ephemeral data)
- Data transfer cost (on-prem ↔ cloud)
- Network cost (VPN, Direct Connect/ExpressRoute)
- Management overhead (cloud admin, monitoring)

**On-Prem Cost Components (baseline):**
- Infrastructure cost (allocated)
- Operational cost
- Licensing cost

**Benefits (quantified):**
- Cost savings (cloud vs. on-prem)
- Time savings (faster provisioning, faster processing)
- Innovation velocity (faster experimentation, model iteration)
- Risk reduction (disaster recovery, burst capacity)

**Benefits (qualitative):**
- Business agility
- Access to latest technology (GPUs, managed services)

2. **Calculate 3-year NPV (Net Present Value) for each use case**

**Outputs:**
- `cloud_use_case_cost_benefit_analysis.xlsx` - 5 use cases with NPV, ROI, payback period

---

#### Task 2.2.2: Risk Assessment per Use Case
**Effort:** 3 days (US Lead: 2 days, UK Support: 1 day)
**Dependencies:** Task 2.2.1
**Deliverable:** Risk assessment

**Detailed Steps:**
1. **For each use case, identify risks:**

**Technical Risks:**
- Data transfer latency (on-prem ↔ cloud)
- Network connectivity failures
- Cloud service outages
- Performance variability (noisy neighbor problem)

**Security Risks:**
- Data breach in cloud
- Unauthorized access
- Data leakage during transfer
- Compliance violations (data residency)

**Operational Risks:**
- Vendor lock-in
- Skills gaps (cloud expertise)
- Complex cost management (cloud billing complexity)

2. **For each risk, define mitigation:**
- Encryption, access controls, audit logging
- Multi-region cloud deployment (disaster recovery)
- Cloud cost monitoring and alerts
- Training and upskilling

**Outputs:**
- `cloud_use_case_risk_assessment.xlsx`

---

#### Task 2.2.3: Use Case Prioritization Matrix
**Effort:** 2 days (US Lead: 2 days)
**Dependencies:** Tasks 2.2.1, 2.2.2
**Deliverable:** Prioritized use case list

**Detailed Steps:**
1. **Rank use cases by:**
   - ROI (highest to lowest)
   - Business impact (strategic importance)
   - Technical feasibility (ease of implementation)
   - Risk (lower risk = higher priority)

2. **Create prioritization matrix (2x2):**
   - X-axis: Business Value (ROI, impact)
   - Y-axis: Feasibility (technical ease, low risk)
   - Quadrants: Quick Wins, Strategic Initiatives, Fill-Ins, Hard Slogs

3. **Recommend top 3 use cases for initial cloud adoption:**
   - Priority 1: ML Model Training (highest ROI, high feasibility)
   - Priority 2: Batch Regulatory Reporting (high business impact)
   - Priority 3: Dev/Test Environments (quick wins, low risk)

**Outputs:**
- `DELIVERABLE_cloud_use_case_prioritization.xlsx` - Prioritized list with recommendations
- `cloud_use_case_prioritization_matrix.pptx` - Visualization

**Quality Gate:** Steering Committee approval for prioritized use cases

---

## 4. Phase 3: Cloud Platform Recommendation (Weeks 5-6) {#phase3}

**Total Effort:** 30 person-days (15 US Lead + 15 UK Support)

### Activity 3.1: AWS Evaluation (Week 5) {#activity-3-1}

#### Task 3.1.1: AWS Services Evaluation
**Effort:** 5 days (US Lead: 3 days, UK Support: 2 days)
**Dependencies:** Phase 2 complete
**Deliverable:** AWS assessment

**Detailed Steps:**
1. **Evaluate relevant AWS services for GPS workloads:**

**Compute:**
- **EC2:** General-purpose compute (batch processing, analytics)
- **EMR:** Managed Hadoop/Spark (batch processing, Databricks alternative)
- **Lambda:** Serverless compute (event-driven, lightweight)
- **SageMaker:** Managed ML platform (model training, deployment)
- **Batch:** Managed batch processing (job scheduling, auto-scaling)

**Storage (ephemeral for compute-only pattern):**
- **S3:** Object storage (input data, model artifacts, temporary storage)
- **EBS:** Block storage (EC2 attached storage)

**Networking:**
- **VPC:** Virtual private cloud (network isolation)
- **Direct Connect:** Dedicated network connection (on-prem ↔ AWS, low latency, high bandwidth)
- **VPN:** Encrypted tunnel (backup connectivity)

**Security:**
- **IAM:** Identity and access management
- **KMS:** Key management service (encryption keys)
- **CloudTrail:** Audit logging
- **GuardDuty:** Threat detection

**Data Transfer:**
- **DataSync:** Automated data transfer (on-prem ↔ S3)
- **Snowball:** Physical data transfer (large datasets, one-time)

2. **Evaluate against GPS requirements:**
   - Compute intensity (ML training) → SageMaker, EC2 GPU instances
   - Batch processing → EMR, Batch
   - Dev/test → EC2, auto-scaling groups

3. **BofA existing AWS footprint:**
   - Document existing BofA AWS accounts, regions
   - Leverage existing enterprise agreements (EA pricing)
   - Leverage existing Direct Connect circuits

4. **Financial services-specific features:**
   - FedRAMP compliance
   - FINRA compliance (for financial data)
   - SOC 1/2/3, PCI-DSS certifications

5. **Data residency options:**
   - AWS regions: US-East (N. Virginia), US-West (Oregon, N. California), EU (Frankfurt, Ireland), APAC (Singapore, Tokyo), etc.
   - Ability to restrict data to specific regions (compliance)

6. **Cost modeling:**
   - On-demand pricing (flexibility)
   - Reserved Instances (cost savings for predictable workloads)
   - Spot Instances (up to 90% savings for fault-tolerant workloads)
   - Savings Plans

**Outputs:**
- `cloud_aws_services_evaluation.xlsx` - Service-by-service assessment
- `cloud_aws_cost_model.xlsx` - Pricing model for 5 use cases

---

### Activity 3.2: Azure Evaluation (Week 5) {#activity-3-2}

#### Task 3.2.1: Azure Services Evaluation
**Effort:** 5 days (US Lead: 3 days, UK Support: 2 days)
**Dependencies:** Phase 2 complete
**Deliverable:** Azure assessment

**Detailed Steps:**
1. **Evaluate relevant Azure services:**

**Compute:**
- **Virtual Machines:** General-purpose compute
- **Synapse Analytics:** Data warehouse + Spark (batch analytics)
- **Databricks on Azure:** Managed Spark (lakehouse analytics)
- **Azure ML:** Managed ML platform
- **Batch:** Managed batch processing
- **Functions:** Serverless compute

**Storage:**
- **Azure Blob Storage:** Object storage (equivalent to S3)
- **Data Lake Storage Gen2:** Optimized for analytics (hierarchical namespace)

**Networking:**
- **Virtual Network (VNet):** Network isolation
- **ExpressRoute:** Dedicated connection (equivalent to Direct Connect)
- **VPN Gateway:** Site-to-site VPN

**Security:**
- **Azure AD:** Identity management
- **Key Vault:** Encryption key management
- **Azure Monitor:** Logging and monitoring
- **Security Center:** Threat detection

**Data Transfer:**
- **Data Factory:** Data integration and transfer
- **Data Box:** Physical data transfer

2. **Evaluate against GPS requirements** (same approach as AWS)

3. **BofA existing Azure footprint:**
   - Existing Azure subscriptions, enterprise agreements
   - Existing ExpressRoute circuits

4. **Financial services features:**
   - Azure compliance certifications (SOC, PCI-DSS, etc.)
   - Financial services-specific solutions

5. **Data residency:** Azure regions (US, EU, Asia)

6. **Cost modeling:**
   - Pay-as-you-go, Reserved VM Instances, Spot VMs

**Outputs:**
- `cloud_azure_services_evaluation.xlsx`
- `cloud_azure_cost_model.xlsx`

---

### Activity 3.3: Platform Comparison & Recommendation (Week 6) {#activity-3-3}

#### Task 3.3.1: AWS vs Azure Comparison
**Effort:** 3 days (US Lead: 2 days, UK Support: 1 day)
**Dependencies:** Activities 3.1, 3.2 complete
**Deliverable:** Platform comparison

**Detailed Steps:**
1. **Compare AWS and Azure across dimensions:**

| Dimension | AWS | Azure | Winner |
|-----------|-----|-------|--------|
| **Service Breadth** | Widest range (200+ services) | Comprehensive (150+ services) | AWS (slight edge) |
| **ML Services** | SageMaker (mature, feature-rich) | Azure ML (good, improving) | AWS |
| **Big Data/Analytics** | EMR (mature), Athena, Redshift | Synapse, Databricks on Azure | Tie |
| **Databricks Support** | Yes (via AWS Marketplace) | Native partnership | Azure |
| **Pricing** | Competitive, complex | Competitive, simpler | Tie |
| **BofA Footprint** | Existing EA, Direct Connect | Existing EA, ExpressRoute | Tie |
| **Enterprise Support** | Excellent (TAM, support plans) | Excellent (CSA, support plans) | Tie |
| **Compliance** | All required certs | All required certs | Tie |
| **Data Transfer Cost** | $0.09/GB egress | $0.087/GB egress | Azure (slight edge) |

2. **Workload-specific fit:**
   - ML training: AWS SageMaker vs Azure ML → AWS edge
   - Batch processing: AWS EMR vs Azure Synapse/Databricks → Depends on Databricks preference (if WS1 recommends Databricks, Azure has native integration)
   - Dev/test: Both equivalent

3. **Strategic considerations:**
   - Multi-cloud strategy (diversification vs. consolidation)
   - BofA enterprise direction (is there a preferred cloud?)
   - Existing teams' skills (AWS or Azure expertise)

**Outputs:**
- `cloud_aws_vs_azure_comparison.xlsx` - Detailed comparison matrix

---

#### Task 3.3.2: Platform Recommendation
**Effort:** 2 days (US Lead: 2 days)
**Dependencies:** Task 3.3.1
**Deliverable:** Cloud platform recommendation

**Detailed Steps:**
1. **Develop recommendation:**
   - Recommendation: AWS or Azure (or multi-cloud with primary)
   - Rationale: Based on comparison, workload fit, BofA strategy
   - Alternative option: If recommendation not approved

2. **Prepare executive presentation:**
   - Executive summary (recommendation, rationale)
   - Detailed comparison
   - Cost projections
   - Risk assessment

**Outputs:**
- `DELIVERABLE_cloud_platform_recommendation.docx` - Recommendation with detailed justification (30 pages)
- `cloud_platform_recommendation_executive.pptx` - Executive presentation

**Quality Gate:** Steering Committee approval for platform selection

---

## 5. Phase 4: Cloud Architecture Patterns (Weeks 7-8) {#phase4}

**Total Effort:** 30 person-days (15 US Lead + 15 UK Support)

### Activity 4.1: Reference Architecture Patterns (Weeks 7-8) {#activity-4-1}

#### Task 4.1.1: Pattern 1 - Burst Analytics Processing
**Effort:** 5 days (US Lead: 3 days, UK Support: 2 days)
**Dependencies:** Phase 3 platform selection
**Deliverable:** Burst analytics pattern

**Detailed Steps:**
1. **Define Pattern:**
   - **Use Case:** Batch regulatory reporting with month-end spikes
   - **Objective:** Handle burst workloads without over-provisioning on-prem

2. **Architecture Components:**

```
On-Premises (BofA Data Center)
├── Data Lake (Databricks on-prem or Oracle Exadata)
│   └── Payment data (Bronze, Silver layers)
├── Orchestration (Airflow, Control-M)
├── Network (Direct Connect/ExpressRoute, VPN)
└── Results Storage

          ↕ Secure data transfer (encrypted)

Cloud (AWS/Azure)
├── Landing Zone (S3/Blob)
│   └── Extracted payment data (masked/tokenized)
├── Compute Cluster (EMR/Synapse, auto-scaling)
│   └── Batch processing (aggregations, transformations)
├── Output Storage (S3/Blob)
│   └── Generated reports (XML, CSV)
└── Ephemeral (auto-delete after 7 days)

          ↕ Secure results transfer

On-Premises (BofA Data Center)
└── Report Submission (to regulators)
```

3. **Data Flow:**
   - **Step 1 (On-Prem):** Extract payment data from lakehouse (filter for report period, mask PII if needed)
   - **Step 2 (Transfer):** Secure transfer to cloud (DataSync/Data Factory, encrypted in transit)
   - **Step 3 (Cloud):** Land in S3/Blob, trigger batch processing
   - **Step 4 (Cloud):** Auto-scaling compute cluster processes data (aggregations, validations, report generation)
   - **Step 5 (Cloud):** Write report files to output storage
   - **Step 6 (Transfer):** Transfer reports back to on-prem (encrypted)
   - **Step 7 (On-Prem):** Ingest reports, submit to regulators
   - **Step 8 (Cloud):** Auto-delete cloud data (retention policy: 7 days)

4. **Security Controls:**
   - **Data Encryption:** At rest (S3 SSE-KMS/Blob encryption with customer-managed keys), in transit (TLS 1.3)
   - **Network Isolation:** VPC/VNet private subnets, no internet access
   - **Access Control:** IAM roles/Azure RBAC, least privilege, no long-term credentials
   - **Audit Logging:** CloudTrail/Azure Monitor, all API calls logged
   - **Data Deletion:** Automated deletion policy (Lambda/Function triggered after 7 days)
   - **DLP (Data Loss Prevention):** Monitor for PII leakage (Macie/Purview)

5. **Network Architecture:**
   - **Primary:** Direct Connect/ExpressRoute (dedicated 10Gbps circuit)
   - **Backup:** Site-to-site VPN (encrypted tunnel)
   - **Routing:** BGP routing, failover to VPN if Direct Connect fails

6. **Cost Optimization:**
   - **Compute:** Spot instances for batch (up to 90% savings), auto-shutdown after job completion
   - **Storage:** S3 Intelligent-Tiering (auto-move to cheaper tiers), Blob cool/archive
   - **Data Transfer:** Minimize transfers (compression, delta sync only changed data)
   - **Reserved Capacity:** For predictable base load (reserved instances, savings plans)

7. **Orchestration:**
   - On-prem orchestrator (Airflow, Control-M) triggers cloud job
   - Cloud job publishes completion event (EventBridge/Event Grid)
   - On-prem orchestrator listens for completion, triggers downstream steps

**Outputs:**
- `cloud_pattern_burst_analytics.docx` - Complete pattern specification (20 pages)
- `cloud_pattern_burst_analytics_architecture.vsdx` - Architecture diagram
- `cloud_pattern_burst_analytics_cost_model.xlsx` - Cost estimation

---

#### Task 4.1.2: Pattern 2 - ML Training Pipeline
**Effort:** 5 days (US Lead: 3 days, UK Support: 2 days)
**Dependencies:** Phase 3 platform selection
**Deliverable:** ML training pattern

**Detailed Steps:**
1. **Define Pattern:**
   - **Use Case:** Fraud detection model training on historical payment data
   - **Objective:** Leverage cloud GPUs for faster, cheaper model training

2. **Architecture Components:**

```
On-Premises
├── Data Lake (historical payment data, 3 years)
├── Feature Engineering (PySpark jobs, create training dataset)
├── Anonymization/Tokenization (mask PII)
├── Model Registry (MLflow on-prem)
└── Model Deployment (production scoring)

          ↕ Secure transfer

Cloud
├── Training Data Storage (S3/Blob)
├── ML Training Service (SageMaker/Azure ML)
│   ├── GPU Instances (P3, NC-series)
│   ├── Distributed Training (Horovod, PyTorch DDP)
│   └── Experiment Tracking (SageMaker Experiments/Azure ML Runs)
├── Model Artifacts (S3/Blob)
└── Ephemeral (delete after training)

          ↕ Transfer model artifacts

On-Premises
└── Model Registry + Deployment
```

3. **Data Flow:**
   - **Step 1:** Feature engineering on-prem (create training dataset from 3 years of payments)
   - **Step 2:** Anonymization (tokenize account numbers, names; k-anonymity for aggregates)
   - **Step 3:** Transfer to cloud (100GB-1TB training data)
   - **Step 4:** Cloud training (SageMaker/Azure ML, GPU instances, distributed training)
   - **Step 5:** Export model artifacts (model file, scaler, preprocessor)
   - **Step 6:** Transfer artifacts back to on-prem
   - **Step 7:** Register model in on-prem MLflow registry
   - **Step 8:** Deploy model to production (on-prem scoring)
   - **Step 9:** Delete cloud data and models

4. **Security Controls:** (similar to Pattern 1, plus model security)

5. **Cost Optimization:**
   - **Spot Instances:** For non-critical training runs (90% savings)
   - **On-Demand GPU:** For time-sensitive training
   - **Auto-Shutdown:** Terminate instances immediately after training

6. **MLOps Integration:**
   - Experiment tracking in cloud (SageMaker/Azure ML)
   - Model versioning (cloud artifact storage)
   - Transfer best model to on-prem registry
   - A/B testing in on-prem production

**Outputs:**
- `cloud_pattern_ml_training.docx`
- `cloud_pattern_ml_training_architecture.vsdx`
- `cloud_pattern_ml_training_cost_model.xlsx`

---

#### Task 4.1.3: Pattern 3 - Dev/Test Environments
**Effort:** 4 days (US Lead: 2 days, UK Support: 2 days)
**Dependencies:** Phase 3 platform selection
**Deliverable:** Dev/test pattern

**Detailed Steps:**
1. **Define Pattern:**
   - **Use Case:** On-demand dev/test environments for development, testing, POCs
   - **Objective:** Fast provisioning (minutes vs. weeks), cost-effective (pay per use)

2. **Architecture:**

```
On-Premises
└── Test Data Subset (10-20% of production, anonymized)

          ↕ One-time transfer

Cloud
├── Dev/Test VPC/VNet (isolated network)
├── Databricks Workspace (dev/test tier)
├── Data Lake (S3/ADLS with test data)
├── Compute Clusters (auto-terminating)
└── IaC (Terraform/CloudFormation)
    └── Provision environment in <1 hour
```

3. **Environment Provisioning:**
   - **IaC Templates:** Terraform or CloudFormation/ARM
   - **Automated Setup:** Run IaC, provision network, Databricks, data lake, load test data
   - **User Access:** Self-service portal (developers request environment, auto-provision)

4. **Cost Management:**
   - **Auto-Shutdown:** Terminate environments after business hours (e.g., 8pm-8am)
   - **Auto-Delete:** Delete environments after inactivity (e.g., 14 days)
   - **Budget Alerts:** Cost alerts per environment (stop if exceeds budget)

5. **Data Management:**
   - **Data Subsetting:** 10-20% of production data (representative sample)
   - **Data Masking:** All PII masked/tokenized
   - **Data Refresh:** Monthly refresh from production

**Outputs:**
- `cloud_pattern_devtest.docx`
- `cloud_pattern_devtest_architecture.vsdx`
- `cloud_pattern_devtest_iac_templates/` - Sample Terraform/CloudFormation

---

### Activity 4.2: Patterns Consolidation & Approval (Week 8) {#activity-4-2}

#### Task 4.2.1: Consolidate Architecture Patterns
**Effort:** 3 days (US Lead: 2 days, UK Support: 1 day)
**Dependencies:** Tasks 4.1.1-4.1.3
**Deliverable:** Complete architecture patterns document

**Detailed Steps:**
1. Consolidate 3 patterns into master document
2. Create pattern selection guide (which pattern for which use case)
3. Document common components (network, security, cost management)

**Outputs:**
- `DELIVERABLE_cloud_architecture_patterns.docx` - 3 patterns (60 pages)

---

#### Task 4.2.2: InfoSec Review & Approval
**Effort:** 3 days (US Lead: 2 days, UK Support: 1 day)
**Dependencies:** Task 4.2.1
**Deliverable:** InfoSec-approved patterns

**Detailed Steps:**
1. Present patterns to InfoSec for security review
2. Address feedback (additional controls, compliance gaps)
3. Obtain InfoSec approval for compute-only pattern

**Quality Gate:** InfoSec approval required to proceed to POC

---

## 6. Dependencies & Sequencing {#dependencies}

### Workstream-Level Dependencies

**External Dependencies:**
- WS1 (Platform Modernization) → Activity 1.2 (use case catalog provides input for cloud workload profiling)
- WS1 (Platform Modernization) → Phase 3 (if Databricks selected, influences AWS vs Azure decision - Azure has native Databricks integration)
- WS4 (POC Planning) → POC 3 validates cloud patterns

**Internal Dependencies:**
```
Phase 1 (Readiness Assessment)
    ↓
Phase 2 (Use Case Prioritization) - requires workload profiles, candidacy scores
    ↓
Phase 3 (Platform Recommendation) - requires prioritized use cases
    ↓
Phase 4 (Architecture Patterns) - requires platform selection
```

### Critical Path

1. Workload Profiling (Week 2) → 10 days
2. Use Case Deep Dive (Week 3) → 12 days
3. Cost-Benefit Analysis (Week 4) → 10 days
4. Platform Evaluation (Week 5) → 10 days (AWS and Azure in parallel)
5. Platform Recommendation (Week 6) → 5 days
6. Architecture Patterns (Weeks 7-8) → 14 days (3 patterns partially in parallel)

**Total Critical Path:** ~61 days (~12 weeks with parallelization) - fits within 8-week timeline

---

## 7. Risks & Mitigation {#risks}

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **InfoSec rejects compute-only pattern** | Low | Critical | Early InfoSec engagement (Week 1), pre-socialize patterns, address concerns proactively |
| **Cloud cost higher than expected** | Medium | High | Detailed cost modeling, pilot with cost monitoring, reserved instances for predictable workloads |
| **Data transfer latency unacceptable** | Medium | Medium | Use Direct Connect/ExpressRoute (high bandwidth, low latency), compression, incremental transfers |
| **Platform recommendation delayed** | Medium | Medium | Parallel AWS and Azure evaluation, decision criteria pre-defined |
| **Skills gap in cloud platform** | High | Medium | Training plan (AWS/Azure certifications), vendor professional services for initial setup |
| **Vendor lock-in concerns** | Medium | Medium | Multi-cloud patterns (portable architectures), containerization (Kubernetes) |
| **Compliance violations** | Low | Critical | Legal/Compliance review, data masking/anonymization, audit all data transfers |

---

## 8. Quality Gates {#quality-gates}

### Quality Gate 1: End of Week 2 (Readiness Assessment Complete)

**Criteria:**
- ✅ 30+ workloads profiled and scored
- ✅ Cloud candidacy assessment complete
- ✅ Current state cost baseline established
- ✅ Top 10 cloud candidates identified

**Decision:** Proceed to use case prioritization?

---

### Quality Gate 2: End of Week 4 (Use Case Prioritization Complete)

**Criteria:**
- ✅ 5 use cases detailed (ML training, batch reporting, analytics, data quality, dev/test)
- ✅ Cost-benefit analysis complete (3-year NPV)
- ✅ Risk assessment complete
- ✅ Top 3 use cases prioritized
- ✅ Steering Committee approval

**Decision:** Proceed to platform recommendation?

---

### Quality Gate 3: End of Week 6 (Platform Recommendation Approved)

**Criteria:**
- ✅ AWS and Azure evaluated
- ✅ Platform comparison complete
- ✅ Platform recommendation (AWS or Azure) with justification
- ✅ Steering Committee approval

**Decision:** Proceed to architecture patterns?

---

### Quality Gate 4: End of Week 8 (Architecture Patterns Approved)

**Criteria:**
- ✅ 3 reference architecture patterns documented
- ✅ Security controls defined
- ✅ Cost models complete
- ✅ InfoSec approval obtained

**Decision:** Proceed to POC Execution (Workstream 4, POC 3)?

---

## Appendix: Deliverables Checklist

| Deliverable | File Name | Due Week | Status |
|-------------|-----------|----------|--------|
| Cloud Readiness Assessment | `DELIVERABLE_cloud_readiness_assessment.docx` | Week 2 | |
| Cloud Use Case Prioritization | `DELIVERABLE_cloud_use_case_prioritization.xlsx` | Week 4 | |
| Cloud Platform Recommendation | `DELIVERABLE_cloud_platform_recommendation.docx` | Week 6 | |
| Cloud Architecture Patterns | `DELIVERABLE_cloud_architecture_patterns.docx` | Week 8 | |

---

**Document Status:** COMPLETE ✅
**Review Date:** 2025-12-18
**Next Review:** At WS3 kickoff
