<!-- SPEC-KIT STARTER TASKS -->

# Unified Platform Implementation Tasks

*Generated from PRD_UNIFIED_PLATFORM_FINAL.md for spec-kit integration*

## Phase 0: Environment Preparation - Week 0.5

### Dockerize Roots_Convert (CRITICAL)
- [ ] (T-000a) **Create Roots_Convert Dockerfile**
  - **Implementation**: Create Dockerfile with `python:3.11-slim`, psycopg[binary], libpq-dev
  - **Location**: `/Users/markdarby/projects/Roots_Convert/Dockerfile`
  - **Environment**: `APP_WORKSPACE=roots` for RLS integration
  - **Testing**: Container builds, runs existing JSON workflows, connects to test database
  - **Git**: Set up GitHub repository for Roots_Convert, commit "T-000a: Add Docker containerization"
  - **Acceptance**: Container builds successfully and runs current JSON-based functionality

- [ ] (T-000b) **Integrate Roots_Convert into docker-compose**
  - **Location**: `/Users/markdarby/projects/Roots_Convert/docker-compose.yml` or extend AInfographics.v2
  - **Network**: Same network as `ai-infographic-postgres-test`
  - **DATABASE_URL**: `postgres://ai_user:pass@postgres:5432/ai_infographic?options=-c%20app.workspace%3Droots`
  - **Acceptance**: Roots_Convert container connects to shared PostgreSQL with workspace RLS

- [ ] (T-000c) **Create database connectivity smoke test**
  - **Location**: `/Users/markdarby/projects/Roots_Convert/scripts/smoke_db.py`
  - **Tests**: Verify workspace setting, study count, RLS isolation
  - **Command**: `docker compose run --rm roots_convert python -m scripts.smoke_db`
  - **Acceptance**: Confirms `workspace=roots` and database connectivity

- [ ] (T-000d) **Verify JSON functionality in Docker**
  - **Implementation**: Test all existing JSON-based workflows in containerized environment
  - **Testing**: Load studies, run summaries, export functionality, performance comparison
  - **Git**: Commit "T-000d: Verify Docker environment functionality"
  - **Future**: Create Roots_Convert home inspection script (similar to AInfographics.v2)
  - **Acceptance**: All current Roots_Convert features work identically in Docker

- [ ] (T-000e) **Initialize GitHub for Roots_Convert**
  - **Implementation**: Create GitHub repo, add remote, push initial Dockerized project
  - **Security**: Configure repo secrets for DATABASE_URL (no plaintext credentials)
  - **Git**: Commit "T-000e: Initialize Roots_Convert GitHub repository"
  - **Acceptance**: Repo accessible, secrets configured, CI can read envs

- [ ] (T-000f) **Add CI pipeline for tests + inspection**
  - **Location**: `.github/workflows/ci.yml` (Roots_Convert and AInfographics.v2)
  - **Steps**: Build container, run unit/integration tests, run Home Inspection (AInfographics.v2), upload reports artifact
  - **Gate**: Fail on integrity SQL checks and latency benchmarks (as defined in plan/spec)
  - **Acceptance**: CI runs on PRs and main, artifacts uploaded, red/green signal enforced

## Phase 1: Database Foundation (AInfographics.v2) - Weeks 1-2

### Database Schema Creation
- [ ] (T-001) **Create unified schema in AInfographics.v2**
  - **Implementation**: Execute complete PostgreSQL schema with workspace isolation, RLS policies
  - **Location**: `/Users/markdarby/projects/AInfographics.v2/database/`
  - **Testing**: Verify all tables created, RLS policies active, foreign key constraints enforced
  - **Home Inspection**: Run inspection, ensure database connectivity checks pass
  - **Git**: Commit "T-001: Implement unified database schema with workspace isolation"
  - **Acceptance**: All tables, indexes, RLS policies, triggers created successfully
  - **Note**: Remove `jsonb_schema_valid` check from schema; validate JSON in app layer

- [ ] (T-002) **Backup existing database**
  - **Command**: `docker exec ai-infographic-postgres-test pg_dump -U ai_user -d ai_infographic > pre_migration_backup.sql`
  - **Acceptance**: Backup file created and verified

- [ ] (T-003) **Install pgVector with production refinements**
  - **Deliverable**: pgVector v0.6.2+ with HNSW indexes
  - **Acceptance**: Vector similarity queries return results <200ms

### Data Migration from Roots_Convert
- [ ] (T-004) **Extract 717 studies from JSON**
  - **Source**: `/Users/markdarby/projects/Roots_Convert/data/pubmed_studies.backup_1753151645.json`
  - **Target**: `studies` table with UUID mapping
  - **Acceptance**: All 717 studies migrated with data integrity verification

- [ ] (T-005) **Create immutable artifacts for summary versions**
  - **Logic**: Convert multiple summary types to artifacts with workspace='roots'
  - **Types**: clinical, patient, commentary, poetry, infographic
  - **Acceptance**: All existing summary versions preserved as artifacts

- [ ] (T-006) **Set initial primary versions via head pointers**
  - **Logic**: Designate primary versions for each artifact type
  - **Scope**: global scope for initial migration
  - **Acceptance**: All studies have primary versions accessible

### Embedding Generation
- [ ] (T-007) **Generate study embeddings for semantic search**
  - **Model**: text-embedding-3-large (3072 dimensions, preferred for higher semantic fidelity; cost difference minimal)
  - **Source**: Abstract text with SHA256 checksums
  - **Acceptance**: >95% of studies have embeddings, similarity search functional

## Phase 2: Smart Features (AInfographics.v2) - Weeks 3-4

### Auto-Tagging Pipeline
- [ ] (T-008) **Implement canonical facet system**
  - **Location**: `/Users/markdarby/projects/AInfographics.v2/backend/`
  - **Facets**: agent, population, outcome, design, duration
  - **Constraint**: Facet schema must be extensible; values managed in facet_definitions/facet_values tables rather than hardcoded
  - **Acceptance**: Facet values seeded, confidence scoring >80% accuracy

- [ ] (T-009) **Build embedding-based auto-tagger**
  - **Logic**: Cosine similarity to exemplar studies
  - **Validation**: LLM confirmation of facet assignments
  - **Acceptance**: All studies auto-tagged with confidence scores

### Frontend Enhancement
- [ ] (T-010) **Enhanced search interface with semantic capabilities**
  - **Location**: `/Users/markdarby/projects/AInfographics.v2/frontend/`
  - **Features**: Hybrid search (text + embeddings), faceted filtering
  - **Acceptance**: Sub-second search response, relevant results

- [ ] (T-011) **Related studies panels**
  - **Logic**: Vector similarity recommendations
  - **UI**: Display 5-10 most similar studies per study page
  - **Acceptance**: Recommendations are contextually relevant

- [ ] (T-012) **Real-time faceted filtering**
  - **Features**: Auto-populated dropdowns, filter counts
  - **Performance**: Instant updates as users select filters
  - **Acceptance**: Smooth UX with >100 simultaneous filters

## Phase 3: Roots_Convert Migration - Weeks 5-6

### Backend PostgreSQL Integration
- [ ] (T-013) **Replace JSON storage with PostgreSQL queries**
  - **Location**: `/Users/markdarby/projects/Roots_Convert/pubmed_summarizer/data/study_manager.py`
  - **Change**: Switch from file operations to database queries
  - **Workspace**: All operations use workspace='roots'
  - **Acceptance**: Existing functionality preserved, performance equivalent or better

- [ ] (T-014) **Update StudyManager class for database operations**
  - **Methods**: get_study_summary, save_study, bulk operations
  - **Logic**: Query artifacts with head pointer resolution
  - **Acceptance**: All existing API endpoints functional

### Research Workflow Enhancement
- [ ] (T-015) **Primary version designation interface**
  - **Location**: `/Users/markdarby/projects/Roots_Convert/frontend/`
  - **Feature**: UI controls to set artifact_heads for promotion
  - **Acceptance**: Researchers can designate primary versions for promotion

- [ ] (T-016) **Bulk summary generation optimized for database**
  - **Performance**: Batch operations on 100+ studies
  - **Versioning**: Create new artifacts with proper lineage
  - **Acceptance**: Bulk operations complete in reasonable time with full audit trail

## Phase 4: Integration & Polish - Weeks 7-8

### Promotion Workflows
- [ ] (T-017) **Build promotion engine (roots → prod)**
  - **Location**: Both projects (shared service)
  - **Logic**: O(1) head pointer updates with audit trail
  - **Acceptance**: Promotion completes instantly with full rollback capability
  - **Constraint**: Only artifacts with status='approved' may be promoted to global scope

- [ ] (T-018) **User role enforcement with RLS**
  - **Database**: Row-level security policies active
  - **Application**: Role-based access controls enforced
  - **Acceptance**: Users can only access appropriate workspace data
    - **Ownership enforced**: users may only update/delete their own artifacts
    - **Approval gate enforced**: only curators/admins can set status='approved'

### Collaborative Features
- [ ] (T-019) **Threaded commentary system**
  - **Location**: `/Users/markdarby/projects/AInfographics.v2/`
  - **Features**: artifact_comments with threading, real-time updates
  - **Acceptance**: Multiple users can collaborate on summary improvement

- [ ] (T-020) **Version comparison interface**
  - **Features**: Side-by-side artifact comparison, diff highlighting
  - **Logic**: Compare any two artifacts for same study/type
  - **Acceptance**: Users can easily identify changes between versions

## Success Criteria

### Technical Validation
- [ ] (T-021) **All 717 studies accessible in both workspaces**
- [ ] (T-022) **Semantic search returns relevant results**
- [ ] (T-023) **Sub-second query performance maintained**
- [ ] (T-024) **Data integrity preserved throughout migration**
- [ ] (T-025) **RLS and audit triggers validated in Postgres**
- [ ] (T-026) **CI/CD pipelines run integrity checks** (no orphan artifacts, valid head pointers, embedding coverage) and performance benchmarks

### User Experience Validation
- [ ] (T-027) **Researchers can bulk-generate summaries in Roots_Convert**
- [ ] (T-028) **Production users see enhanced search in AInfographics.v2**
- [ ] (T-029) **Promotion workflow enables research → production**
- [ ] (T-030) **Auto-tagging reduces manual categorization by >80%**

### Platform Integration
- [ ] (T-031) **Single database serves both applications**
- [ ] (T-032) **Workspace isolation prevents data cross-contamination**
- [ ] (T-033) **Audit trails track all changes and promotions**
- [ ] (T-034) **Daily automated backups with restore validation validated**

---

*Each task includes specific file locations, acceptance criteria, and references to the source PRD. This enables any AI agent to pick up implementation at any phase with full context.*

## Task Completion Standards

### Required Steps for Each Task
Every task MUST include these completion steps where applicable:

#### 1. **Testing Phase** 🧪
- **Unit tests** for new functions/classes
- **Integration tests** for database operations
- **End-to-end tests** for UI workflows
- **Performance benchmarks** for critical paths

#### 2. **Home Inspection** 🏠 (AInfographics.v2)
- Run `🏠 Run Home Inspection.command` after each significant change
- **Target**: Maintain >90% health score
- **Address**: Critical issues (❌) before task completion
- **Monitor**: Warning trends across development
- **Report**: Include inspection results in task completion notes

#### 3. **Git Workflow** 📝
- **AInfographics.v2**: Already configured with GitHub integration
- **Roots_Convert**: Set up GitHub integration as part of Docker tasks
- **Commit Standards**: Descriptive messages with task ID reference
- **Branch Strategy**: Feature branches for major tasks, direct commits for fixes
- **Required**: Push to GitHub after task completion and successful inspection

### Task Template
```
- [ ] (T-XXX) **Task Name**
  - **Implementation**: [Core work]
  - **Testing**: [Specific tests to run]
  - **Home Inspection**: Run and achieve >90% health score
  - **Git**: Commit with "T-XXX: [description]" and push to GitHub
  - **Acceptance**: [Success criteria]
```

## Notes for Agents

- Use consistent PL/pgSQL quoting (`$$ ... $$`) when generating functions/triggers
- Remove trailing commas in SQL blocks to avoid syntax errors
- Task IDs (T-001, T-002, etc.) may be prefixed to tasks for easier referencing
- **NEVER skip the testing, inspection, or git steps** - they prevent technical debt accumulation
- **Home inspection failures** indicate architectural issues that must be resolved
