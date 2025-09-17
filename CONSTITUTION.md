# Unified Research Platform Constitution

## Non-Negotiable Architectural Principles

### Single Database Architecture
- **MUST use one PostgreSQL database** with workspace isolation (`roots` vs `prod`)
- **NEVER implement dual-database synchronization** - use workspace partitioning instead
- **MUST enforce workspace isolation** via Row-Level Security (RLS) policies
- **O(1) promotion workflows** via head pointer updates, not data copying

### Immutable Versioning System
- **All content stored as immutable artifacts** - never modify existing records
- **Version lineage preserved** via `supersedes_id` relationships
- **Primary versions designated** via `artifact_heads` table with scope hierarchy
- **Complete audit trail** for all head pointer changes

### Workspace Design Principles
- **`workspace='roots'`**: Research environment for bulk operations and model testing
- **`workspace='prod'`**: Production environment for user-facing content
- **Clear separation**: Each project operates primarily in its designated workspace
- **Controlled promotion**: Only approved artifacts promoted from roots → prod

### Data Integrity Requirements
- **UUID-based relationships** throughout the schema
- **Foreign key constraints** enforced for referential integrity
- **JSON schema validation** in application layer (not database constraints)
- **SHA256 checksums** for embedding change detection
- **Automated backups and rollback capability** required for both workspaces
- **Continuous schema integrity checks** (no orphaned artifacts, invalid head pointers, or missing embeddings) must run in CI

### Performance Standards
- **Sub-second search response** for 10,000+ studies
- **Vector similarity queries <200ms** for semantic search
- **Batch operations optimized** for processing 100+ studies
- **Auto-tagging accuracy ≥85%** vs manual curation

### Security and Access Control
- **Row-Level Security policies** enforce workspace isolation
- **User role hierarchy**: editor → curator → admin with appropriate scopes
- **Audit logging** for all modifications and promotions
- **Standard PostgreSQL hardening** despite non-clinical data classification

### Semantic Intelligence
- **pgVector embeddings required** for all study abstracts
- **Embedding resilience**: generation must fail gracefully with retry logic; missing embeddings must never block artifact creation
- **Auto-tagging via canonical facets**: agent, population, outcome, design, duration
- **Facet schema must remain extensible** to support future categories without re-migration
- **Dynamic topic discovery** through embedding clustering
- **Hybrid search**: Combine full-text + semantic similarity

### Project Coordination
- **AInfographics.v2**: Primary platform development (70% of work)
- **Roots_Convert**: Research interface migration (30% of work)
- **Shared schema**: Both projects use same database with workspace separation
- **Cross-project tasks**: Explicitly reference both codebases in implementation

### Technology Constraints
- **PostgreSQL 16+** with pgVector extension
- **Default: OpenAI text-embedding-3-large** (preferred for semantic search accuracy; may be swapped if schema compatibility maintained)
- **React/TypeScript** for frontend components
- **Python/Flask** for backend services
- **Docker deployment** for ALL environments (development, staging, production)
- **Environment parity**: Roots_Convert MUST be containerized before PostgreSQL migration

## Quality Assurance Standards

### Task Completion Requirements
Every task MUST include:
- **Testing phase** with appropriate unit, integration, and performance tests
- **Home inspection** achieving >90% health score (AInfographics.v2, and Roots_Convert once containerized)
- **Git workflow** with descriptive commits and GitHub push
- **Commit messages MUST reference task IDs (T-XXX) for traceability**
- **Secrets management** enforced via GitHub Actions / Docker environment variables (no plaintext in repos)
- **Documentation** of any architectural decisions or trade-offs

### Quality Gates
- **No task is complete** without passing all three phases: testing, inspection, git
- **Home inspection failures** indicate architectural issues requiring resolution
- **Performance benchmarks** must be met before moving to next phase
- **Git history** must maintain clear task traceability

## Implementation Guardrails

### What MUST Be Preserved
- All 717 existing studies and their metadata
- 95 studies with human commentary
- Multiple summary versions per study
- Existing user workflows and interfaces
- Commentary extraction pipeline results

### What MUST Be Avoided
- Dual database architectures requiring synchronization
- Data loss during migration
- Breaking changes to existing APIs
- Manual categorization workflows
- Vendor lock-in to specific AI models
- Skipping CI/CD pipelines or merging untested code

### Success Criteria (Non-Negotiable)
- **100% data migration** from JSON to PostgreSQL without loss
- **Functional semantic search** with relevant results
- **Working promotion workflow** between workspaces
- **Collaborative editing** without data conflicts
- **Performance maintained** or improved vs JSON storage

---

*This constitution serves as the foundation for all implementation decisions and must be consulted before any architectural changes.*
