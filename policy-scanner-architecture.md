# Policy Document Management System - Architecture Design Document
## GovChat-NL Integration

**Version**: 1.0
**Date**: October 2025
**Author**: Software Architect
**Status**: READY FOR REVIEW

---

## [Status Update]
```
Know:
- Existing GovChat-NL architecture (SvelteKit + FastAPI/OpenWebUI fork)
- 24 detailed user stories with acceptance criteria
- Current tech stack (PostgreSQL, LiteLLM, OAuth2, Docker/K8s)
- Scale requirements (1000+ users, 100K+ documents)
- Budget constraints (<€5K/month)
- Timeline (6 months, 6 developers)

Don't Know:
- Exact scraping target websites beyond Gemeentebladen
- Specific document formats distribution (% PDF vs HTML vs DOCX)
- Current PostgreSQL schema details
- Existing API rate limits from government sources
- Detailed RBAC implementation in current system

Need:
- Approval on technology selections
- Access to target website APIs/documentation
- Decision on build vs buy for vector DB
- Confirmation on n8n integration approach

Plan 24h:
- Finalize technology stack selection
- Begin database schema design
- Start API contract definitions
- Initiate scraper plugin architecture

Blockers:
- None currently (architectural design phase)
```

---

## [Task Brief]
```
Objective: Design scalable Policy Document Management System for GovChat-NL
Scope In: Scanning, indexing, search, AI categorization, user interface
Scope Out: Modifying core GovChat-NL chat functionality, rewriting existing auth
Constraints: 6 months, 6 developers, €5K/month, must integrate with existing stack
Acceptance Criteria:
- Handle 1000+ concurrent users
- Index 100K+ documents
- Sub-second search response
- 99.9% uptime
- GDPR compliant
Artifacts Needed: Target website documentation, current DB schema
Risks:
- Government website changes/blocking
- LLM API costs exceeding budget
- Complex integration with existing system
```

---

## Executive Summary

This document presents the architecture for integrating a Policy Document Management System (Policy Scanner) into the existing GovChat-NL platform. The design follows a **hybrid approach** combining microservices for new capabilities with deep integration into the existing OpenWebUI infrastructure.

### Key Architectural Decisions

1. **Integration Strategy**: Hybrid - new microservices for scanning/indexing, integrated UI within existing SvelteKit frontend
2. **Message Broker**: RabbitMQ (simpler than Kafka, sufficient for our scale)
3. **Search Engine**: Meilisearch (better cost/performance than Elasticsearch for our scale)
4. **Vector Database**: Qdrant (self-hosted, open-source, cost-effective)
5. **Workflow Engine**: n8n (already mentioned in README, visual workflow design)

---

## 1. High-Level Architecture

### 1.1 Integration Approach

Given the existing GovChat-NL architecture and constraints, I recommend a **Hybrid Integration Strategy**:

```
┌─────────────────────────────────────────────────────────────┐
│                   GovChat-NL Platform                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────────────────────────────────┐          │
│  │        Existing Components                   │          │
│  │  - SvelteKit Frontend                       │          │
│  │  - FastAPI Backend (OpenWebUI)              │          │
│  │  - PostgreSQL Database                      │          │
│  │  - LiteLLM Router                          │          │
│  │  - OAuth2/Entra ID                         │          │
│  └──────────────┬───────────────────────────────┘          │
│                 │                                           │
│  ┌──────────────▼───────────────────────────────┐          │
│  │      Policy Scanner Integration Layer        │          │
│  │  - API Extensions in FastAPI                │          │
│  │  - New UI Routes in SvelteKit              │          │
│  │  - Shared Database Tables                  │          │
│  └──────────────┬───────────────────────────────┘          │
│                 │                                           │
└─────────────────┼───────────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────────┐
│            Policy Scanner Microservices                     │
├──────────────┬──────────────┬───────────────┬──────────────┤
│   Scanner    │   Search     │   Workflow    │   Vector     │
│   Service    │   Service    │   Engine      │   Service    │
│  (Python)    │ (Meilisearch)│    (n8n)      │  (Qdrant)    │
└──────┬───────┴──────┬───────┴───────┬───────┴──────┬───────┘
       │              │               │              │
┌──────▼──────────────▼───────────────▼──────────────▼────────┐
│                    Infrastructure Layer                      │
│   PostgreSQL | RabbitMQ | MinIO | Redis | Monitoring        │
└───────────────────────────────────────────────────────────────┘
```

### 1.2 ADR-001: Integration Strategy

**Context**: Need to add Policy Scanner to existing GovChat-NL without disrupting current functionality.

**Options Evaluated**:

| Option | Description | Pros | Cons |
|--------|------------|------|------|
| **1. Fully Integrated** | Build everything within OpenWebUI | - Single deployment<br>- Shared auth/DB | - Risk to existing system<br>- Harder to scale independently |
| **2. Fully Separate** | Completely independent application | - No risk to existing<br>- Independent scaling | - Duplicate auth/UI<br>- Poor UX |
| **3. Hybrid** ✅ | UI integrated, services separate | - Seamless UX<br>- Independent scaling<br>- Gradual migration | - Some complexity<br>- Multiple deployments |

**Decision**: Hybrid approach - integrate UI and auth, separate compute-intensive services.

**Consequences**:
- ✅ Minimal risk to existing system
- ✅ Can scale scanning independently
- ⚠️ Need to maintain API contracts
- ⚠️ Slightly more complex deployment

**Testing Strategy**: Integration tests between services, contract testing
**Rollback Plan**: Feature flag to disable Policy Scanner UI

---

## 2. Technology Stack Selection

### 2.1 Technology Decision Matrix

| Component | Selected | Alternatives Considered | Rationale |
|-----------|----------|------------------------|-----------|
| **Message Broker** | RabbitMQ | Kafka, Redis Streams | Simpler ops, sufficient throughput, good Python support |
| **Search Engine** | Meilisearch | Elasticsearch, OpenSearch | 10x less resource usage, built-in typo tolerance, instant search |
| **Vector DB** | Qdrant | Pinecone, Weaviate | Self-hosted, good performance, active development |
| **Workflow Engine** | n8n | Airflow, Temporal | Visual workflows, already in README, easy for non-devs |
| **Object Storage** | MinIO | S3, Azure Blob | Self-hosted option, S3-compatible API |
| **Scraper Framework** | Scrapy | BeautifulSoup, Playwright | Battle-tested, async, built-in retries |
| **PDF Processing** | PyPDF2 + Tesseract | PDFMiner, Apache Tika | Good balance of speed and accuracy |

### 2.2 Cost Analysis

**Monthly Infrastructure Costs (Self-Hosted on Hetzner)**:
```
Kubernetes Cluster (3 nodes)     : €150
Database Server (dedicated)      : €100
Storage (10TB)                  : €50
Backup Storage                  : €30
Load Balancer                   : €20
------------------------
Subtotal Infrastructure         : €350

LLM API Costs (estimated):
- Categorization (100K docs)    : €500
- Embeddings (100K docs)        : €200
- Semantic search (10K queries) : €300
------------------------
Subtotal AI/ML                  : €1,000

Total Monthly                   : €1,350 (well under €5K budget)
```

---

## 3. Database Schema Design

### 3.1 Integration with Existing Schema

The Policy Scanner will extend the existing PostgreSQL database with new tables in a separate schema:

```sql
-- Create separate schema for policy scanner
CREATE SCHEMA IF NOT EXISTS policy_scanner;

-- Grant permissions to existing application user
GRANT ALL ON SCHEMA policy_scanner TO govchat_user;
```

### 3.2 Core Tables

```sql
-- Policy Sources Configuration
CREATE TABLE policy_scanner.sources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    source_type VARCHAR(50) NOT NULL CHECK (source_type IN ('gemeenteblad', 'dso', 'custom')),
    base_url TEXT NOT NULL,
    selector_config JSONB NOT NULL, -- CSS selectors, pagination rules
    auth_config JSONB, -- API keys, headers if needed
    rate_limit INTEGER DEFAULT 10, -- requests per second
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES auth.user(id),
    UNIQUE(name)
);

CREATE INDEX idx_sources_active ON policy_scanner.sources(is_active);
CREATE INDEX idx_sources_type ON policy_scanner.sources(source_type);

-- Documents Master Table
CREATE TABLE policy_scanner.documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id UUID REFERENCES policy_scanner.sources(id) ON DELETE CASCADE,
    external_id VARCHAR(500), -- ID from source system
    title TEXT NOT NULL,
    description TEXT,
    content_hash VARCHAR(64) NOT NULL, -- SHA-256 for deduplication
    document_url TEXT NOT NULL,
    document_type VARCHAR(20) CHECK (document_type IN ('pdf', 'html', 'docx', 'xlsx')),
    municipality VARCHAR(255),
    publication_date DATE,
    effective_date DATE,
    file_size BIGINT,
    page_count INTEGER,
    language VARCHAR(10) DEFAULT 'nl',
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'indexed', 'failed', 'archived')),
    metadata JSONB, -- Flexible additional metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    indexed_at TIMESTAMPTZ,
    UNIQUE(source_id, external_id),
    UNIQUE(content_hash)
);

CREATE INDEX idx_documents_source ON policy_scanner.documents(source_id);
CREATE INDEX idx_documents_status ON policy_scanner.documents(status);
CREATE INDEX idx_documents_municipality ON policy_scanner.documents(municipality);
CREATE INDEX idx_documents_pub_date ON policy_scanner.documents(publication_date DESC);
CREATE INDEX idx_documents_hash ON policy_scanner.documents(content_hash);

-- Document Storage Locations
CREATE TABLE policy_scanner.document_files (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID REFERENCES policy_scanner.documents(id) ON DELETE CASCADE,
    file_type VARCHAR(20) NOT NULL, -- 'original', 'processed', 'text', 'preview'
    storage_path TEXT NOT NULL,
    storage_backend VARCHAR(20) DEFAULT 'minio', -- 'minio', 's3', 'local'
    file_size BIGINT,
    mime_type VARCHAR(100),
    checksum VARCHAR(64),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_document_files_document ON policy_scanner.document_files(document_id);

-- Categories Hierarchy
CREATE TABLE policy_scanner.categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    parent_id UUID REFERENCES policy_scanner.categories(id),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) NOT NULL,
    description TEXT,
    icon VARCHAR(50),
    color VARCHAR(7), -- hex color
    path LTREE, -- For efficient hierarchy queries
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(slug),
    UNIQUE(parent_id, name)
);

CREATE INDEX idx_categories_path ON policy_scanner.categories USING GIST(path);
CREATE INDEX idx_categories_parent ON policy_scanner.categories(parent_id);

-- Document Categorization
CREATE TABLE policy_scanner.document_categories (
    document_id UUID REFERENCES policy_scanner.documents(id) ON DELETE CASCADE,
    category_id UUID REFERENCES policy_scanner.categories(id) ON DELETE CASCADE,
    confidence_score DECIMAL(3,2) CHECK (confidence_score BETWEEN 0 AND 1),
    assigned_by VARCHAR(20) CHECK (assigned_by IN ('auto', 'rule', 'manual')),
    assigned_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (document_id, category_id)
);

CREATE INDEX idx_doc_cats_category ON policy_scanner.document_categories(category_id);

-- Scan Jobs Tracking
CREATE TABLE policy_scanner.scan_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id UUID REFERENCES policy_scanner.sources(id),
    job_type VARCHAR(20) CHECK (job_type IN ('full', 'incremental', 'manual')),
    status VARCHAR(20) DEFAULT 'pending',
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    documents_found INTEGER DEFAULT 0,
    documents_new INTEGER DEFAULT 0,
    documents_updated INTEGER DEFAULT 0,
    documents_failed INTEGER DEFAULT 0,
    error_details JSONB,
    triggered_by UUID REFERENCES auth.user(id),
    job_config JSONB, -- Scan-specific configuration
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_scan_jobs_source ON policy_scanner.scan_jobs(source_id);
CREATE INDEX idx_scan_jobs_status ON policy_scanner.scan_jobs(status);
CREATE INDEX idx_scan_jobs_created ON policy_scanner.scan_jobs(created_at DESC);

-- Search History (for analytics and suggestions)
CREATE TABLE policy_scanner.search_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.user(id),
    query_text TEXT,
    filters JSONB,
    result_count INTEGER,
    clicked_results UUID[], -- Array of document IDs
    search_type VARCHAR(20) DEFAULT 'keyword', -- 'keyword', 'semantic', 'hybrid'
    response_time_ms INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_search_history_user ON policy_scanner.search_history(user_id, created_at DESC);
CREATE INDEX idx_search_history_query ON policy_scanner.search_history USING GIN(to_tsvector('dutch', query_text));

-- Saved Searches
CREATE TABLE policy_scanner.saved_searches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.user(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    query_text TEXT,
    filters JSONB,
    notification_enabled BOOLEAN DEFAULT false,
    notification_frequency VARCHAR(20) CHECK (notification_frequency IN ('immediate', 'daily', 'weekly')),
    last_notified_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_saved_searches_user ON policy_scanner.saved_searches(user_id);

-- Categorization Rules
CREATE TABLE policy_scanner.categorization_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    rule_type VARCHAR(20) CHECK (rule_type IN ('keyword', 'regex', 'llm')),
    conditions JSONB NOT NULL, -- Rule definition
    actions JSONB NOT NULL, -- What to do when matched
    priority INTEGER DEFAULT 100,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES auth.user(id)
);

CREATE INDEX idx_cat_rules_active ON policy_scanner.categorization_rules(is_active, priority DESC);
```

### 3.3 Migration Strategy

```sql
-- Migration 001: Create Policy Scanner Schema
BEGIN;
-- Create schema and tables as above
-- Add foreign key to link with existing users
ALTER TABLE policy_scanner.sources
    ADD CONSTRAINT fk_sources_user
    FOREIGN KEY (created_by)
    REFERENCES auth.user(id);
COMMIT;

-- Migration 002: Add Integration Points
BEGIN;
-- Add policy scanner permissions to existing roles
INSERT INTO auth.permissions (name, resource, action) VALUES
    ('policy.search', 'policy_documents', 'read'),
    ('policy.admin', 'policy_sources', 'write'),
    ('policy.categorize', 'policy_categories', 'write');

-- Link permissions to existing roles
INSERT INTO auth.role_permissions (role_id, permission_id)
SELECT r.id, p.id
FROM auth.roles r, auth.permissions p
WHERE r.name = 'admin' AND p.name LIKE 'policy.%';
COMMIT;
```

---

## 4. API Design

### 4.1 RESTful API Contracts

All APIs follow OpenAPI 3.0 specification and integrate with existing FastAPI backend:

#### Search API
```yaml
/api/v1/policy/search:
  post:
    summary: Search policy documents
    requestBody:
      content:
        application/json:
          schema:
            type: object
            properties:
              query:
                type: string
                description: Search query text
              filters:
                type: object
                properties:
                  sources:
                    type: array
                    items:
                      type: string
                  municipalities:
                    type: array
                    items:
                      type: string
                  date_from:
                    type: string
                    format: date
                  date_to:
                    type: string
                    format: date
                  categories:
                    type: array
                    items:
                      type: string
              page:
                type: integer
                default: 1
              limit:
                type: integer
                default: 20
                maximum: 100
              sort:
                type: string
                enum: [relevance, date_desc, date_asc, title]
                default: relevance
    responses:
      200:
        description: Search results
        content:
          application/json:
            schema:
              type: object
              properties:
                results:
                  type: array
                  items:
                    $ref: '#/components/schemas/DocumentSummary'
                total:
                  type: integer
                facets:
                  type: object
                  properties:
                    sources:
                      type: object
                    municipalities:
                      type: object
                    categories:
                      type: object
                page:
                  type: integer
                took_ms:
                  type: integer
```

#### Document Management API
```yaml
/api/v1/policy/documents/{id}:
  get:
    summary: Get document details
    parameters:
      - name: id
        in: path
        required: true
        schema:
          type: string
          format: uuid
    responses:
      200:
        description: Document details
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/Document'

/api/v1/policy/documents/{id}/download:
  get:
    summary: Download document file
    parameters:
      - name: id
        in: path
        required: true
        schema:
          type: string
      - name: format
        in: query
        schema:
          type: string
          enum: [original, pdf, text]
          default: original
    responses:
      200:
        description: Document file
        content:
          application/pdf: {}
          application/octet-stream: {}
      302:
        description: Redirect to signed URL
```

#### Scanner Management API
```yaml
/api/v1/policy/sources:
  get:
    summary: List policy sources
    security:
      - bearerAuth: []
    responses:
      200:
        description: List of sources
        content:
          application/json:
            schema:
              type: array
              items:
                $ref: '#/components/schemas/PolicySource'

  post:
    summary: Create new policy source
    security:
      - bearerAuth: []
    requestBody:
      required: true
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/PolicySourceCreate'

/api/v1/policy/sources/{id}/scan:
  post:
    summary: Trigger manual scan
    parameters:
      - name: id
        in: path
        required: true
        schema:
          type: string
    requestBody:
      content:
        application/json:
          schema:
            type: object
            properties:
              scan_type:
                type: string
                enum: [full, incremental]
                default: incremental
    responses:
      202:
        description: Scan job created
        content:
          application/json:
            schema:
              type: object
              properties:
                job_id:
                  type: string
                status:
                  type: string
                message:
                  type: string
```

### 4.2 Rate Limiting Strategy

```python
from fastapi import HTTPException
from fastapi_limiter.depends import RateLimiter

@app.post("/api/v1/policy/search", dependencies=[Depends(RateLimiter(times=30, seconds=60))])
async def search_documents():
    # Standard users: 30 requests per minute
    pass

@app.post("/api/v1/policy/semantic-search", dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def semantic_search():
    # Expensive AI operations: 10 requests per minute
    pass

@app.post("/api/v1/policy/sources", dependencies=[Depends(RateLimiter(times=5, seconds=60))])
async def create_source():
    # Admin operations: 5 requests per minute
    pass
```

---

## 5. Scraper Architecture

### 5.1 Plugin-Based Scraper System

```python
# Base Scraper Interface
from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from pydantic import BaseModel

class DocumentMetadata(BaseModel):
    title: str
    url: str
    external_id: str
    publication_date: Optional[date]
    municipality: Optional[str]
    document_type: str
    metadata: Dict

class ScraperPlugin(ABC):
    """Base class for all scraper plugins"""

    def __init__(self, config: Dict):
        self.config = config
        self.rate_limiter = RateLimiter(config.get('rate_limit', 10))

    @abstractmethod
    async def discover_documents(self,
                                 start_date: Optional[date] = None,
                                 end_date: Optional[date] = None) -> List[DocumentMetadata]:
        """Discover available documents"""
        pass

    @abstractmethod
    async def download_document(self, doc_metadata: DocumentMetadata) -> bytes:
        """Download document content"""
        pass

    @abstractmethod
    def validate_config(self) -> bool:
        """Validate plugin configuration"""
        pass

# Gemeenteblad Scraper Plugin
class GemeentebladScraper(ScraperPlugin):
    """Scraper for Gemeentebladen.nl"""

    async def discover_documents(self, start_date=None, end_date=None):
        async with aiohttp.ClientSession() as session:
            # Custom headers to avoid bot detection
            headers = {
                'User-Agent': 'Mozilla/5.0 (GovChat-NL Policy Scanner)',
                'Accept': 'text/html,application/xhtml+xml',
                'Accept-Language': 'nl-NL,nl;q=0.9'
            }

            documents = []
            page = 1
            while True:
                await self.rate_limiter.acquire()

                url = f"{self.config['base_url']}/search"
                params = {
                    'page': page,
                    'municipality': self.config.get('municipality'),
                    'from_date': start_date.isoformat() if start_date else None,
                    'to_date': end_date.isoformat() if end_date else None
                }

                async with session.get(url, headers=headers, params=params) as response:
                    if response.status == 429:  # Rate limited
                        await asyncio.sleep(60)
                        continue

                    html = await response.text()
                    docs = self._parse_search_results(html)

                    if not docs:
                        break

                    documents.extend(docs)
                    page += 1

                    # Respect robots.txt crawl-delay
                    await asyncio.sleep(self.config.get('crawl_delay', 1))

            return documents

    def _parse_search_results(self, html: str) -> List[DocumentMetadata]:
        soup = BeautifulSoup(html, 'html.parser')
        documents = []

        for item in soup.select(self.config['selectors']['item']):
            title_elem = item.select_one(self.config['selectors']['title'])
            url_elem = item.select_one(self.config['selectors']['url'])
            date_elem = item.select_one(self.config['selectors']['date'])

            if title_elem and url_elem:
                documents.append(DocumentMetadata(
                    title=title_elem.text.strip(),
                    url=urljoin(self.config['base_url'], url_elem['href']),
                    external_id=self._extract_id(url_elem['href']),
                    publication_date=self._parse_date(date_elem.text if date_elem else None),
                    municipality=self.config.get('municipality'),
                    document_type='pdf'  # Most Gemeenteblad docs are PDFs
                ))

        return documents
```

### 5.2 Anti-Bot Handling

```python
class RobustScraper:
    """Enhanced scraper with anti-bot countermeasures"""

    def __init__(self):
        self.session = None
        self.retry_strategy = ExponentialBackoff()

    async def scrape_with_retry(self, url: str, max_retries: int = 3):
        for attempt in range(max_retries):
            try:
                response = await self._fetch(url)

                # Check for bot detection
                if self._is_blocked(response):
                    await self._handle_blocking(attempt)
                    continue

                return response

            except aiohttp.ClientError as e:
                if attempt == max_retries - 1:
                    raise
                await self.retry_strategy.wait(attempt)

    def _is_blocked(self, response):
        """Detect common bot blocking patterns"""
        if response.status == 403:
            return True
        if response.status == 429:  # Rate limited
            return True
        if 'captcha' in response.url.path.lower():
            return True
        return False

    async def _handle_blocking(self, attempt: int):
        """Handle bot detection"""
        if attempt == 0:
            # Rotate user agent
            self.session.headers['User-Agent'] = self._get_random_user_agent()
        elif attempt == 1:
            # Add more human-like headers
            self.session.headers.update({
                'Accept-Language': 'nl-NL,nl;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache'
            })
        else:
            # Exponential backoff
            wait_time = 2 ** attempt * 60
            logger.warning(f"Blocked, waiting {wait_time}s before retry")
            await asyncio.sleep(wait_time)
```

---

## 6. Infrastructure Architecture

### 6.1 Kubernetes Deployment Topology

```yaml
# Namespace Structure
apiVersion: v1
kind: Namespace
metadata:
  name: policy-scanner
---
# Scanner Deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: scanner-service
  namespace: policy-scanner
spec:
  replicas: 2  # Start with 2, scale based on load
  selector:
    matchLabels:
      app: scanner-service
  template:
    metadata:
      labels:
        app: scanner-service
    spec:
      containers:
      - name: scanner
        image: govchat-nl/scanner-service:1.0.0
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: url
        - name: RABBITMQ_URL
          value: amqp://rabbitmq:5672
        - name: MINIO_ENDPOINT
          value: minio:9000
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
---
# Meilisearch StatefulSet
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: meilisearch
  namespace: policy-scanner
spec:
  serviceName: meilisearch
  replicas: 1  # Meilisearch doesn't support clustering in free version
  selector:
    matchLabels:
      app: meilisearch
  template:
    metadata:
      labels:
        app: meilisearch
    spec:
      containers:
      - name: meilisearch
        image: getmeili/meilisearch:v1.5
        env:
        - name: MEILI_MASTER_KEY
          valueFrom:
            secretKeyRef:
              name: meilisearch-secret
              key: master-key
        - name: MEILI_ENV
          value: production
        volumeMounts:
        - name: data
          mountPath: /meili_data
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
  volumeClaimTemplates:
  - metadata:
      name: data
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 50Gi
---
# Qdrant Vector DB Deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: qdrant
  namespace: policy-scanner
spec:
  replicas: 1
  selector:
    matchLabels:
      app: qdrant
  template:
    metadata:
      labels:
        app: qdrant
    spec:
      containers:
      - name: qdrant
        image: qdrant/qdrant:v1.7.4
        ports:
        - containerPort: 6333
        volumeMounts:
        - name: qdrant-storage
          mountPath: /qdrant/storage
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
      volumes:
      - name: qdrant-storage
        persistentVolumeClaim:
          claimName: qdrant-pvc
---
# RabbitMQ Deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: rabbitmq
  namespace: policy-scanner
spec:
  replicas: 1
  selector:
    matchLabels:
      app: rabbitmq
  template:
    metadata:
      labels:
        app: rabbitmq
    spec:
      containers:
      - name: rabbitmq
        image: rabbitmq:3.12-management
        ports:
        - containerPort: 5672
        - containerPort: 15672
        env:
        - name: RABBITMQ_DEFAULT_USER
          value: admin
        - name: RABBITMQ_DEFAULT_PASS
          valueFrom:
            secretKeyRef:
              name: rabbitmq-secret
              key: password
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
```

### 6.2 Service Mesh Configuration (Optional)

For advanced traffic management and observability:

```yaml
# Istio VirtualService for canary deployments
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: policy-scanner-vs
  namespace: policy-scanner
spec:
  hosts:
  - policy-scanner
  http:
  - match:
    - headers:
        canary:
          exact: "true"
    route:
    - destination:
        host: scanner-service
        subset: v2
      weight: 100
  - route:
    - destination:
        host: scanner-service
        subset: v1
      weight: 90
    - destination:
        host: scanner-service
        subset: v2
      weight: 10  # 10% canary traffic
```

### 6.3 Monitoring and Observability

```yaml
# Prometheus ServiceMonitor
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: policy-scanner-metrics
  namespace: policy-scanner
spec:
  selector:
    matchLabels:
      app: scanner-service
  endpoints:
  - port: metrics
    interval: 30s
    path: /metrics
---
# Key Metrics to Monitor
metrics:
  - scanner_documents_processed_total
  - scanner_errors_total{type="parse|download|timeout"}
  - search_requests_duration_seconds
  - search_requests_total{status="success|error"}
  - categorization_accuracy_percent
  - storage_usage_bytes{type="documents|embeddings"}
  - rabbitmq_queue_depth{queue="scan|categorize|embed"}
```

---

## 7. AI/ML Pipeline

### 7.1 Document Processing Pipeline

```python
class DocumentProcessor:
    """Orchestrates the document processing pipeline"""

    def __init__(self):
        self.text_extractor = TextExtractor()
        self.embedder = DocumentEmbedder()
        self.categorizer = DocumentCategorizer()
        self.indexer = SearchIndexer()

    async def process_document(self, doc_id: str):
        """Main processing pipeline"""
        try:
            # 1. Extract text from document
            doc = await self.get_document(doc_id)
            text = await self.text_extractor.extract(doc.file_path)

            # 2. Clean and normalize text
            cleaned_text = self.clean_text(text)

            # 3. Generate embeddings (chunked for long documents)
            chunks = self.chunk_document(cleaned_text, max_tokens=512)
            embeddings = await self.embedder.embed_chunks(chunks)

            # 4. Categorize document
            categories = await self.categorizer.categorize(cleaned_text)

            # 5. Index in Meilisearch
            await self.indexer.index_document({
                'id': doc_id,
                'title': doc.title,
                'content': cleaned_text,
                'categories': categories,
                'municipality': doc.municipality,
                'date': doc.publication_date
            })

            # 6. Store embeddings in Qdrant
            await self.store_embeddings(doc_id, embeddings)

            # 7. Update document status
            await self.update_status(doc_id, 'indexed')

        except Exception as e:
            logger.error(f"Processing failed for {doc_id}: {e}")
            await self.update_status(doc_id, 'failed', error=str(e))
```

### 7.2 Semantic Search Implementation

```python
class SemanticSearchService:
    """Hybrid search combining keyword and vector search"""

    def __init__(self):
        self.meilisearch = MeiliSearchClient()
        self.qdrant = QdrantClient()
        self.embedder = QueryEmbedder()

    async def search(self, query: str, filters: dict = None, limit: int = 20):
        """Perform hybrid search"""

        # 1. Parallel execution of both search types
        keyword_task = self.keyword_search(query, filters, limit * 2)
        semantic_task = self.semantic_search(query, filters, limit * 2)

        keyword_results, semantic_results = await asyncio.gather(
            keyword_task, semantic_task
        )

        # 2. Merge results using Reciprocal Rank Fusion
        merged = self.reciprocal_rank_fusion(
            keyword_results,
            semantic_results,
            k=60,  # RRF parameter
            keyword_weight=0.3,
            semantic_weight=0.7
        )

        # 3. Re-rank top results using cross-encoder
        if len(merged) > 0:
            reranked = await self.rerank_results(query, merged[:limit*2])
            return reranked[:limit]

        return merged[:limit]

    async def semantic_search(self, query: str, filters: dict, limit: int):
        """Vector similarity search"""
        # Generate query embedding
        query_embedding = await self.embedder.embed_query(query)

        # Search in Qdrant with metadata filtering
        search_params = {
            'vector': query_embedding,
            'limit': limit,
            'with_payload': True
        }

        if filters:
            search_params['filter'] = self.build_qdrant_filter(filters)

        results = await self.qdrant.search(**search_params)
        return results
```

### 7.3 Categorization Strategy

```python
class HierarchicalCategorizer:
    """Multi-level categorization with confidence scoring"""

    def __init__(self):
        self.rule_engine = RuleBasedCategorizer()
        self.ml_model = load_model('bert-policy-classifier')
        self.llm_client = LiteLLMClient()

    async def categorize(self, document_text: str) -> List[Category]:
        """Three-tier categorization approach"""

        categories = []

        # 1. Fast rule-based categorization
        rule_categories = self.rule_engine.categorize(document_text)
        if rule_categories and max(c.confidence for c in rule_categories) > 0.9:
            return rule_categories

        # 2. ML model for standard categories
        ml_predictions = await self.ml_model.predict(document_text)
        for pred in ml_predictions:
            if pred.confidence > 0.7:
                categories.append(Category(
                    id=pred.category_id,
                    confidence=pred.confidence,
                    method='ml_model'
                ))

        # 3. LLM for ambiguous cases
        if not categories or max(c.confidence for c in categories) < 0.7:
            llm_categories = await self.llm_categorize(document_text)
            categories.extend(llm_categories)

        return self.deduplicate_categories(categories)

    async def llm_categorize(self, text: str):
        """Use LLM for complex categorization"""
        prompt = f"""
        Categorize this Dutch policy document into relevant categories.

        Categories:
        {self.get_category_taxonomy()}

        Document excerpt:
        {text[:2000]}

        Return JSON: [{{"category": "name", "confidence": 0.0-1.0, "reasoning": "..."}}]
        """

        response = await self.llm_client.complete(
            model="gpt-4",
            prompt=prompt,
            response_format={"type": "json_object"}
        )

        return self.parse_llm_response(response)
```

---

## 8. Implementation Roadmap

### 8.1 Phase 1: Foundation (Months 1-2)

**Team Allocation**: 4 developers

| Week | Tasks | Deliverables | Risk Mitigation |
|------|-------|--------------|-----------------|
| 1-2 | Infrastructure setup | K8s cluster, CI/CD | Use managed K8s if setup delays |
| 3-4 | Database schema & migrations | PostgreSQL extensions | Test migrations on staging first |
| 5-6 | Basic scanner for Gemeentebladen | Working scraper | Have fallback HTML parser ready |
| 7-8 | Meilisearch integration | Search API | Consider Elasticsearch if issues |

**Success Metrics**:
- Successfully scan 100 documents
- Search response time < 500ms
- 95% uptime

### 8.2 Phase 2: Core Features (Months 3-4)

**Team Allocation**: 6 developers

| Week | Tasks | Deliverables | Risk Mitigation |
|------|-------|--------------|-----------------|
| 9-10 | UI integration in SvelteKit | Search interface | Progressive enhancement approach |
| 11-12 | Document viewer & downloads | PDF viewer | Use iframe fallback for complex PDFs |
| 13-14 | Admin dashboard | Source management | Feature flag for gradual rollout |
| 15-16 | RabbitMQ & async processing | Queue system | Redis as simpler alternative |

**Success Metrics**:
- Handle 10K documents
- 50 concurrent users
- < 2s document load time

### 8.3 Phase 3: AI Features (Months 5-6)

**Team Allocation**: 4 developers + 1 ML engineer

| Week | Tasks | Deliverables | Risk Mitigation |
|------|-------|--------------|-----------------|
| 17-18 | Vector DB & embeddings | Semantic search | Start with pre-trained embeddings |
| 19-20 | Auto-categorization | ML pipeline | Manual rules as fallback |
| 21-22 | Performance optimization | Caching, CDN | Incremental improvements |
| 23-24 | Testing & deployment | Production ready | Staged rollout to subset of users |

**Success Metrics**:
- 100K documents indexed
- Semantic search < 2s
- 80% categorization accuracy

### 8.4 Team Composition

```
Team Structure (6 developers):

Frontend Team (2 devs):
- SvelteKit integration
- UI/UX implementation
- Admin dashboard

Backend Team (3 devs):
- FastAPI extensions
- Scraper development
- Search & categorization

DevOps/Data (1 dev):
- Infrastructure
- Database optimization
- Monitoring
```

### 8.5 Risk Matrix

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Government sites block scraping | Medium | High | Official API partnerships, rotating IPs |
| LLM costs exceed budget | Medium | Medium | Implement usage quotas, caching |
| Performance issues at scale | Low | High | Load testing, horizontal scaling |
| Complex integration with OpenWebUI | Medium | Medium | Modular architecture, feature flags |
| Dutch language NLP challenges | Low | Medium | Use multilingual models, manual rules |

---

## 9. Testing Strategy

### 9.1 Test Pyramid

```
         /\
        /  \     E2E Tests (5%)
       /    \    - User journeys
      /──────\   - Cross-browser
     /        \
    /          \ Integration Tests (20%)
   /            \- API contracts
  /              \- Service communication
 /────────────────\
/                  \ Unit Tests (75%)
└───────────────────┘- Business logic
                     - Scrapers
                     - Parsers
```

### 9.2 Test Implementation

```python
# Unit Test Example
async def test_gemeenteblad_scraper():
    """Test Gemeenteblad scraper with mocked responses"""
    scraper = GemeentebladScraper({
        'base_url': 'https://example.com',
        'municipality': 'Amsterdam'
    })

    with aioresponses() as mocked:
        mocked.get(
            'https://example.com/search?municipality=Amsterdam',
            payload={'documents': [...]}
        )

        results = await scraper.discover_documents()
        assert len(results) == 10
        assert all(d.municipality == 'Amsterdam' for d in results)

# Integration Test Example
@pytest.mark.integration
async def test_search_pipeline():
    """Test full search pipeline"""
    async with TestClient(app) as client:
        # Index test document
        doc_id = await index_test_document()

        # Search for document
        response = await client.post('/api/v1/policy/search', json={
            'query': 'test document',
            'filters': {'municipality': 'Amsterdam'}
        })

        assert response.status_code == 200
        assert response.json()['total'] > 0
        assert doc_id in [r['id'] for r in response.json()['results']]

# Load Test Configuration (Locust)
class PolicySearchUser(HttpUser):
    wait_time = between(1, 3)

    @task(3)
    def search_documents(self):
        self.client.post('/api/v1/policy/search', json={
            'query': random.choice(['beleid', 'vergunning', 'subsidie']),
            'limit': 20
        })

    @task(1)
    def view_document(self):
        doc_id = random.choice(self.document_ids)
        self.client.get(f'/api/v1/policy/documents/{doc_id}')
```

---

## 10. Security Architecture

### 10.1 Security Layers

```
┌─────────────────────────────────────────┐
│          WAF (ModSecurity)              │ Layer 7 Protection
├─────────────────────────────────────────┤
│       Rate Limiting (Redis)             │ API Protection
├─────────────────────────────────────────┤
│     OAuth2/JWT (Existing)               │ Authentication
├─────────────────────────────────────────┤
│        RBAC (Extended)                  │ Authorization
├─────────────────────────────────────────┤
│    Input Validation (Pydantic)          │ Data Validation
├─────────────────────────────────────────┤
│     Encryption (TLS 1.3)                │ Transport Security
├─────────────────────────────────────────┤
│   Database Encryption (at rest)         │ Storage Security
└─────────────────────────────────────────┘
```

### 10.2 RBAC Extension

```python
# Extend existing GovChat-NL permissions
class PolicyPermissions(Enum):
    SEARCH = "policy:search"  # Basic search
    DOWNLOAD = "policy:download"  # Download documents
    ADMIN = "policy:admin"  # Manage sources
    CATEGORIZE = "policy:categorize"  # Manage categories
    ANALYTICS = "policy:analytics"  # View analytics

# Permission checks
@app.get("/api/v1/policy/sources")
@requires_permission(PolicyPermissions.ADMIN)
async def list_sources(user: User = Depends(get_current_user)):
    # Only admins can manage sources
    return await get_sources(user.organization_id)

@app.post("/api/v1/policy/search")
@requires_permission(PolicyPermissions.SEARCH)
@rate_limit(calls=30, period=timedelta(minutes=1))
async def search(query: SearchQuery, user: User = Depends(get_current_user)):
    # All authenticated users can search
    return await search_documents(query, user)
```

---

## 11. Performance Optimization

### 11.1 Caching Strategy

```python
# Multi-layer caching
class CacheManager:
    def __init__(self):
        self.redis = Redis()
        self.local_cache = TTLCache(maxsize=1000, ttl=300)

    async def get_or_set(self, key: str, factory, ttl: int = 3600):
        # L1: Local memory cache
        if key in self.local_cache:
            return self.local_cache[key]

        # L2: Redis cache
        cached = await self.redis.get(key)
        if cached:
            self.local_cache[key] = cached
            return cached

        # L3: Generate and cache
        result = await factory()
        await self.redis.setex(key, ttl, result)
        self.local_cache[key] = result
        return result

# Usage
@app.get("/api/v1/policy/filters")
async def get_filters():
    return await cache.get_or_set(
        "filters:municipalities",
        lambda: fetch_municipalities_from_db(),
        ttl=3600
    )
```

### 11.2 Database Optimization

```sql
-- Partitioning for large tables
CREATE TABLE policy_scanner.documents_2025 PARTITION OF policy_scanner.documents
    FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');

-- Materialized view for common queries
CREATE MATERIALIZED VIEW policy_scanner.document_stats AS
SELECT
    municipality,
    DATE_TRUNC('month', publication_date) as month,
    COUNT(*) as document_count,
    COUNT(DISTINCT source_id) as source_count
FROM policy_scanner.documents
WHERE status = 'indexed'
GROUP BY municipality, month
WITH DATA;

CREATE UNIQUE INDEX ON policy_scanner.document_stats (municipality, month);
REFRESH MATERIALIZED VIEW CONCURRENTLY policy_scanner.document_stats;

-- Optimal indexes
CREATE INDEX idx_documents_search ON policy_scanner.documents
    USING GIN(to_tsvector('dutch', title || ' ' || description));
```

---

## 12. Cost-Benefit Analysis

### 12.1 Build vs Buy Comparison

| Component | Build Cost | Buy Cost | Decision | Rationale |
|-----------|------------|----------|----------|-----------|
| Search Engine | €10K (2 dev-weeks) | €500/month (Algolia) | **Build** (Meilisearch) | Lower TCO, data sovereignty |
| Vector DB | €15K (3 dev-weeks) | €300/month (Pinecone) | **Build** (Qdrant) | Cost savings, on-premise option |
| Workflow Engine | €20K (4 dev-weeks) | €200/month (Zapier) | **Use n8n** (OSS) | Already in stack, visual workflows |
| PDF Processing | €5K (1 dev-week) | €100/month (API) | **Build** | Simple requirements, privacy |

**Total Savings**: €800/month → €9,600/year

### 12.2 ROI Calculation

```
Investment:
- Development: 6 devs × 6 months × €6K = €216,000
- Infrastructure (Year 1): €1,350 × 12 = €16,200
- Total Year 1: €232,200

Benefits:
- Manual research time saved: 100 users × 2 hrs/week × €50/hr = €520,000/year
- Improved decision making: Estimated €200,000/year value
- Total Annual Benefit: €720,000

ROI = (€720,000 - €232,200) / €232,200 = 210% in Year 1
Break-even: Month 4
```

---

## 13. Conclusion and Next Steps

### 13.1 Key Recommendations

1. **Start with Gemeentebladen scraping** - proven need, clear scope
2. **Use Meilisearch over Elasticsearch** - 10x cost reduction, easier operations
3. **Implement feature flags** - gradual rollout, easy rollback
4. **Invest in monitoring early** - prevent issues before they impact users
5. **Build scraper plugin system** - future-proof for new sources

### 13.2 Critical Success Factors

✅ **Technical**:
- Robust scraping with retry logic
- Fast search (<500ms p95)
- Accurate categorization (>80%)

✅ **Operational**:
- Clear documentation
- Monitoring and alerting
- Regular security updates

✅ **Business**:
- User adoption (>50% of target users)
- Positive feedback (NPS >7)
- Cost within budget (<€5K/month)

### 13.3 Immediate Actions

1. **Week 1**:
   - [ ] Set up development environment
   - [ ] Create project repositories
   - [ ] Initialize database schema
   - [ ] Begin Gemeentebladen scraper

2. **Week 2**:
   - [ ] Deploy Meilisearch
   - [ ] Implement basic search API
   - [ ] Create initial UI mockups
   - [ ] Set up CI/CD pipeline

3. **Week 3**:
   - [ ] Complete scraper MVP
   - [ ] Integrate with existing auth
   - [ ] Begin frontend integration
   - [ ] Load testing setup

### 13.4 Decision Points

**Month 1 Review**:
- Scraping success rate
- Performance benchmarks
- Adjust team allocation if needed

**Month 3 Review**:
- User feedback from beta
- Decide on AI feature priorities
- Evaluate infrastructure costs

**Month 5 Review**:
- Full feature assessment
- Performance optimization needs
- Plan for post-launch support

---

## Appendix A: API Examples

```python
# Complete FastAPI integration example
from fastapi import FastAPI, Depends, HTTPException
from typing import List, Optional
import asyncio

app = FastAPI(title="Policy Scanner API")

@app.post("/api/v1/policy/search")
async def search_documents(
    query: str,
    filters: Optional[SearchFilters] = None,
    page: int = 1,
    limit: int = 20,
    sort: str = "relevance",
    current_user: User = Depends(get_current_user)
) -> SearchResponse:
    """
    Search policy documents with filters
    """
    # Record search for analytics
    await record_search(current_user.id, query, filters)

    # Perform hybrid search
    results = await hybrid_search_service.search(
        query=query,
        filters=filters.dict() if filters else {},
        offset=(page - 1) * limit,
        limit=limit,
        sort=sort
    )

    # Format response
    return SearchResponse(
        results=results.documents,
        total=results.total,
        facets=results.facets,
        page=page,
        took_ms=results.took_ms
    )

@app.get("/api/v1/policy/documents/{doc_id}")
async def get_document(
    doc_id: UUID,
    current_user: User = Depends(get_current_user)
) -> DocumentResponse:
    """
    Get document details with related documents
    """
    # Get document
    doc = await document_service.get_document(doc_id)
    if not doc:
        raise HTTPException(404, "Document not found")

    # Record access
    await record_access(current_user.id, doc_id, "view")

    # Get related documents
    related = await get_similar_documents(doc_id, limit=5)

    return DocumentResponse(
        document=doc,
        related=related,
        download_url=generate_download_url(doc_id, current_user.id)
    )
```

---

## Appendix B: Database Migration Scripts

```sql
-- Migration 001: Initial schema
BEGIN;
CREATE SCHEMA IF NOT EXISTS policy_scanner;
-- Add all tables from section 3.2
COMMIT;

-- Migration 002: Add full-text search
BEGIN;
-- Add Dutch text search configuration
CREATE TEXT SEARCH CONFIGURATION dutch_search (COPY = dutch);
-- Add indexes
CREATE INDEX idx_documents_fulltext
    ON policy_scanner.documents
    USING GIN (
        to_tsvector('dutch_search',
        coalesce(title, '') || ' ' ||
        coalesce(description, ''))
    );
COMMIT;

-- Migration 003: Add partitioning
BEGIN;
-- Convert to partitioned table
ALTER TABLE policy_scanner.documents
    PARTITION BY RANGE (publication_date);
-- Create partitions
CREATE TABLE policy_scanner.documents_2024
    PARTITION OF policy_scanner.documents
    FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');
COMMIT;
```

---

## Appendix C: Monitoring Dashboards

```yaml
# Grafana Dashboard Configuration
{
  "dashboard": {
    "title": "Policy Scanner Metrics",
    "panels": [
      {
        "title": "Search Request Rate",
        "targets": [{
          "expr": "rate(search_requests_total[5m])"
        }]
      },
      {
        "title": "Document Processing Queue",
        "targets": [{
          "expr": "rabbitmq_queue_messages{queue='document_processing'}"
        }]
      },
      {
        "title": "Scraper Success Rate",
        "targets": [{
          "expr": "rate(scraper_documents_success[1h]) / rate(scraper_documents_total[1h])"
        }]
      },
      {
        "title": "API Response Times (p95)",
        "targets": [{
          "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))"
        }]
      }
    ]
  }
}
```

---

**Document Status**: READY FOR REVIEW
**Next Review**: Architecture Review Meeting
**Questions**: Contact Software Architect
