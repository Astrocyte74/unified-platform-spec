# Unified Research Platform Implementation Plan

## Technical Architecture Overview

### Database Foundation (PostgreSQL + pgVector)
```sql
-- Core schema implementing workspace isolation with immutable versioning
CREATE TABLE studies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pmid TEXT UNIQUE,
    title TEXT NOT NULL,
    abstract TEXT,
    journal TEXT,
    year INT,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE artifacts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    study_id UUID NOT NULL REFERENCES studies(id),
    artifact_type TEXT NOT NULL,               -- 'clinical', 'patient', 'commentary'
    workspace TEXT NOT NULL CHECK (workspace IN ('roots', 'prod')),
    content JSONB NOT NULL,
    model_id TEXT,
    created_by TEXT NOT NULL,
    status TEXT DEFAULT 'draft' CHECK (status IN ('draft','proposed','approved','archived')),
    supersedes_id UUID REFERENCES artifacts(id),
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE artifact_heads (
    study_id UUID NOT NULL REFERENCES studies(id),
    artifact_type TEXT NOT NULL,
    workspace TEXT NOT NULL CHECK (workspace IN ('roots', 'prod')),
    scope TEXT NOT NULL CHECK (scope IN ('global', 'org', 'user')),
    scope_id TEXT,                             -- NULL for global scope
    artifact_id UUID NOT NULL REFERENCES artifacts(id),
    updated_by TEXT NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE(study_id, artifact_type, workspace, scope, scope_id)
);

CREATE TABLE study_embeddings (
    study_id UUID PRIMARY KEY REFERENCES studies(id) ON DELETE CASCADE,
    model TEXT NOT NULL DEFAULT 'text-embedding-3-large',
    embedding vector(3072),
    abstract_sha256 TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);
```

### Semantic Intelligence Stack
```python
# Auto-tagging pipeline with canonical facets
class AutoTagger:
    CANONICAL_FACETS = {
        'agent': ['testosterone', 'metformin', 'minoxidil'],
        'population': ['postmenopausal women', 'adolescents', 'men'],
        'outcome': ['cardiovascular', 'metabolic', 'cognition'],
        'design': ['RCT', 'observational', 'meta-analysis'],
        'duration': ['acute', '3-6 months', '12 months', 'multi-year']
    }
    # NOTE: This hardcoded list is illustrative; in production facets should be data-driven via facet_definitions/facet_values tables

    def tag_study_via_embeddings(self, study_id: UUID) -> List[FacetAssignment]:
        # 1. Get study embedding
        # 2. Compare to exemplar centroids per facet
        # 3. LLM validation for high-confidence matches
        # 4. Store with confidence scores
```

### User Role & Permission Model
```sql
CREATE TABLE orgs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,              -- 'editor', 'curator', 'admin', 'researcher'
    scopes TEXT[] NOT NULL,                 -- ['user'], ['user','org'], ['user','org','global']
    workspace_access TEXT[] DEFAULT ARRAY['prod']  -- ['prod'], ['prod','roots']
);

-- Row-Level Security policies enforce workspace isolation
ALTER TABLE artifacts ENABLE ROW LEVEL SECURITY;
CREATE POLICY p_artifacts_workspace ON artifacts
  USING (workspace = current_setting('app.workspace', true));

-- Ownership policy: users can only modify artifacts they created
CREATE POLICY p_artifacts_owner_update ON artifacts
  FOR UPDATE TO editor
  USING (created_by = current_user);

-- Approval gate: only curators/admins may set status='approved'
CREATE POLICY p_artifacts_approval ON artifacts
  FOR UPDATE TO curator, admin
  USING (status <> 'approved' OR current_user IN (SELECT user_id FROM role_assignments WHERE role IN ('curator','admin')));
```

## Implementation Strategy

### Phase 0: Environment Preparation - Week 0.5

#### **CRITICAL: Dockerize Roots_Convert First**
**Why This Matters**: Environment parity prevents "works on my laptop" issues during PostgreSQL migration

```dockerfile
# Roots_Convert/Dockerfile
FROM python:3.11-slim

# System deps for psycopg / libpq
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev ca-certificates && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# Ensure psycopg[binary]>=3.1 for PostgreSQL compatibility

COPY . .

# RLS workspace setting for database isolation
ENV APP_WORKSPACE=roots
CMD ["python", "main.py"]
```

```yaml
# docker-compose.yml integration
services:
  postgres:
    image: pgvector/pgvector:pg16
    # ... existing ai-infographic-postgres-test config

  roots_convert:
    build: ./Roots_Convert
    depends_on: [postgres]
    environment:
      # RLS workspace setting via connection string
      DATABASE_URL: postgres://ai_user:${POSTGRES_PASSWORD}@postgres:5432/ai_infographic?options=-c%20app.workspace%3Droots
      APP_WORKSPACE: roots
    volumes:
      - ./Roots_Convert:/app  # Development mount
    profiles: ["dev"]
```

**Benefits**:
- ✅ **Same environment** as production (Python, psycopg, network)
- ✅ **Early issue detection** for SSL/driver compatibility
- ✅ **Workspace isolation** via RLS from day one
- ✅ **Repeatable operations** for bulk processing and migration

### Phase 1: Database Foundation (AInfographics.v2) - Weeks 1-2

#### 1.1 Schema Migration & Backup
**Location**: `/Users/markdarby/projects/AInfographics.v2/database/`

```bash
# Create comprehensive backup
docker exec ai-infographic-postgres-test pg_dump -U ai_user -d ai_infographic > \
  pre_migration_backup_$(date +%Y%m%d_%H%M%S).sql

# Apply complete unified schema with OpenAI refinements
psql -U ai_user -d ai_infographic < unified_platform_schema.sql
```

#### 1.2 Data Migration from Roots_Convert
**Source**: `/Users/markdarby/projects/Roots_Convert/data/pubmed_studies.backup_1753151645.json`

```python
class DataMigrator:
    def migrate_717_studies(self):
        # Extract JSON → studies table with UUID mapping
        # Convert summary versions → immutable artifacts
        # Set initial head pointers for primary versions
        # Preserve 95 commentary-enhanced studies
```

#### 1.3 pgVector Integration
```sql
-- Install pgVector v0.6.2+ with optimized indexes
CREATE INDEX ON study_embeddings USING hnsw (embedding vector_cosine_ops);

-- Generate embeddings for all 717 studies
-- SHA256 checksums prevent unnecessary regeneration
```

### Phase 2: Intelligent Features (AInfographics.v2) - Weeks 3-4

#### 2.1 Semantic Search Implementation
**Location**: `/Users/markdarby/projects/AInfographics.v2/backend/api/`

```python
# Hybrid search combining text + embeddings
def hybrid_search(query_text: str, query_embedding: List[float]) -> List[StudyResult]:
    # BM25 full-text search (30% weight)
    # Vector similarity search (70% weight)
    # Combined scoring with relevance ranking
```

#### 2.2 Auto-Tagging Pipeline
```python
# Embedding-based facet assignment
class FacetTagger:
    def process_study(self, study_id: UUID):
        # Compare study embedding to exemplar centroids
        # LLM validation for confidence >0.6 assignments
        # Store in study_facets with metadata
```

#### 2.3 Frontend Enhancement
**Location**: `/Users/markdarby/projects/AInfographics.v2/frontend/src/components/`

- Enhanced search interface with semantic capabilities
- Faceted filtering with real-time count updates
- Related studies panels using vector similarity
- Version comparison and collaborative editing

### Phase 3: Roots_Convert Migration - Weeks 5-6

#### 3.1 Backend PostgreSQL Integration
**Location**: `/Users/markdarby/projects/Roots_Convert/pubmed_summarizer/data/`

```python
# Replace JSON operations with database queries
class StudyManager:
    def __init__(self):
        self.workspace = 'roots'  # All operations in research workspace

    def get_study_summary(self, study_id: str) -> Dict:
        # Query artifacts with head pointer resolution
        # Maintain existing API compatibility

    def bulk_generate_summaries(self, study_ids: List[str]):
        # Create new artifacts with proper lineage
        # Optimized batch operations on database
```

#### 3.2 Research Workflow Enhancement
- Primary version designation interface for promotion
- Bulk summary generation optimized for database
- Model testing and comparison tools with analytics
- Migration verification and performance validation

### Phase 4: Integration & Polish - Weeks 7-8

#### 4.1 Promotion Workflows
```python
# O(1) promotion engine
class PromotionEngine:
    def promote_to_production(self, artifact_id: UUID, scope: str = 'global'):
        # Update artifact_heads pointer (no data copying)
        # Audit trail automatically captured via triggers
        # Instant rollback capability
```

#### 4.2 Collaborative Features
- Threaded commentary system with real-time updates
- User role enforcement with database RLS
- Version comparison interface with diff highlighting
- Performance optimization and monitoring

## Technology Stack Details

### Backend Components
- **PostgreSQL 16+** with pgVector extension
- **Python/Flask** with SQLAlchemy ORM
- **OpenAI text-embedding-3-large** (3072-d) as default; pluggable if schema-compatible
- **Redis** for caching and session management

### Frontend Components
- **React 18** with TypeScript
- **TanStack Query** for server state management
- **Tailwind CSS** for styling consistency
- **WebSocket** for real-time collaboration

### Infrastructure
- **Docker Compose** for local development
- **GitHub Actions** for CI/CD
- **PostgreSQL backups** automated daily
- **Environment-specific configurations**

## Performance & Monitoring

### Database Optimization
```sql
-- High-leverage partial indexes
CREATE INDEX idx_artifacts_prod_approved
ON artifacts(study_id, artifact_type, created_at DESC)
WHERE workspace='prod' AND status='approved';

-- Materialized view for fast catalog queries
CREATE MATERIALIZED VIEW mv_study_catalog AS
SELECT s.id, s.title, h.artifact_type, a.content
FROM studies s
JOIN artifact_heads h ON h.study_id = s.id AND h.workspace = 'prod'
JOIN artifacts a ON a.id = h.artifact_id;
```

### Monitoring & Alerting
- Query performance tracking (<500ms target)
- Vector search latency monitoring (<200ms target)
- Embedding generation pipeline health
- User activity and engagement metrics
- CI/CD must run integrity SQL checks (no orphan artifacts, valid heads), embedding coverage %, and latency benchmarks; pipeline fails if targets not met.

## Data Migration Verification

### Integrity Checks
```sql
-- Verify complete migration
SELECT COUNT(*) as migrated_studies FROM studies;  -- Expected: 717

-- Verify artifact creation
SELECT artifact_type, workspace, COUNT(*)
FROM artifacts GROUP BY artifact_type, workspace;

-- Verify embedding coverage
SELECT COUNT(*) * 100.0 / (SELECT COUNT(*) FROM studies) as coverage_percent
FROM study_embeddings;

-- Verify head pointer consistency
SELECT workspace, scope, COUNT(*)
FROM artifact_heads GROUP BY workspace, scope;

-- Verify no orphan artifacts
SELECT COUNT(*) FROM artifacts a
LEFT JOIN studies s ON s.id = a.study_id
WHERE s.id IS NULL;

-- Verify heads point to valid artifacts
SELECT COUNT(*) FROM artifact_heads h
LEFT JOIN artifacts a ON a.id = h.artifact_id
WHERE a.id IS NULL;
```

### Quality Validation
- Semantic search relevance testing with known queries
- Auto-tagging accuracy vs manual classification
- Performance benchmarks under load
- User acceptance testing of key workflows

## Risk Mitigation

### Rollback Procedures
- **Daily automated backups** are required (cron/scheduler). Post-restore, run integrity checks before app reconnect.
```bash
# Emergency rollback to pre-migration state
docker exec ai-infographic-postgres-test psql -U ai_user -d ai_infographic < \
  pre_migration_backup_YYYYMMDD_HHMMSS.sql

# Selective workspace rollback
DELETE FROM artifact_heads WHERE workspace='roots';
DELETE FROM artifacts WHERE workspace='roots';
```

### Monitoring & Alerts
- Database performance degradation detection
- Failed embedding generation alerts
- RLS policy enforcement verification
- User workflow disruption monitoring
- CI/CD must run integrity SQL checks (no orphan artifacts, valid heads), embedding coverage %, and latency benchmarks; pipeline fails if targets not met.

## Success Validation

### Technical Metrics
- ✅ All 717 studies migrated without data loss
- ✅ Semantic search returns relevant results (>90% precision)
- ✅ Sub-second query performance maintained
- ✅ Auto-tagging accuracy ≥85% vs manual classification

### User Experience Metrics
- ✅ Researchers can perform bulk operations in Roots_Convert
- ✅ Production users see enhanced search in AInfographics.v2
- ✅ Promotion workflow enables research → production flow
- ✅ Collaborative editing supports multi-user workflows

### Platform Integration
- ✅ Single database serves both applications
- ✅ Workspace isolation prevents cross-contamination
- ✅ Audit trails track all changes and promotions
- ✅ Backup and rollback procedures validated

---

*This implementation plan provides the detailed technical roadmap for executing the unified platform vision across both project codebases.*
