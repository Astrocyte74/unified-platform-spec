# Unified Research Platform Glossary

## Core Concepts

### Workspace
Logical partition within the unified PostgreSQL database that isolates data by environment:
- **`workspace='roots'`**: Research environment for bulk operations and model testing
- **`workspace='prod'`**: Production environment for user-facing, curated content

### Artifact
Immutable content record storing a single version of study-related content:
- **Artifact Types**: clinical, patient, commentary, poetry, infographic
- **Immutability**: Once created, artifacts are never modified - new versions are created
- **Lineage**: Connected via `supersedes_id` to track version history

### Head Pointer
Reference indicating which artifact version is currently "primary" for a given context:
- **Scope Hierarchy**: user → org → global (cascading lookup for primary version)
- **O(1) Operations**: Changing primary versions requires only pointer updates
- **Workspace Isolation**: Each workspace maintains separate head pointers

### Semantic Search
Intelligence layer using vector embeddings to understand content meaning:
- **Embeddings**: Default: 3072-d vectors from OpenAI text-embedding-3-large (preferred for higher semantic fidelity; cost difference minimal, pluggable if schema-compatible)
- **Similarity**: Cosine distance calculations for content relationships
- **Hybrid Queries**: Combine traditional text search with semantic understanding

### Auto-Tagging
Automated categorization system using canonical facets:
- **Facets**: agent, population, outcome, design, duration
- **Confidence Scoring**: Machine learning confidence levels for tag assignments
- **Exemplar-Based**: Classification via similarity to reference studies
- **Extensible Schema**: Facet definitions must support future categories without re-migration

## Project Components

### Roots_Convert
Research interface project transitioning to PostgreSQL workspace='roots':
- **Current State**: 717 studies in JSON format with multiple summary versions
- **Target State**: Research interface to shared database for bulk operations
- **Primary Functions**: Model testing, bulk generation, primary version designation

### AInfographics.v2
Production platform project enhanced with intelligent features:
- **Current State**: PostgreSQL database with user management and 9 test studies
- **Target State**: Full-featured platform with semantic search and collaboration
- **Primary Functions**: User interface, semantic search, collaborative editing

### Commentary System
Enhanced content layer with human insights:
- **GPT-5 Extraction**: AI-derived human insights from existing summaries
- **Threaded Discussions**: Multi-user collaborative improvement workflows
- **Quality Assessment**: Confidence levels and manual review capabilities

## Technical Terms

### pgVector
PostgreSQL extension enabling vector operations:
- **HNSW Indexes**: Hierarchical Navigable Small World graphs for fast similarity search
- **Vector Types**: Native PostgreSQL support for high-dimensional vectors
- **Cosine Distance**: Primary similarity metric for content relationships

### Row-Level Security (RLS)
PostgreSQL feature enforcing data access policies:
- **Workspace Isolation**: Users only see data from appropriate workspace
- **Policy-Based**: Declarative rules controlling data visibility
- **Application-Transparent**: Security enforced at database level
- **Ownership Policies**: Users may only update/delete artifacts they created; SELECT remains open

### Dockerization
Containerization strategy to ensure environment parity:
- **Universal Requirement**: All environments (dev, staging, prod) must run in Docker
- **Environment Parity**: Identical Python, psycopg, and networking across services
- **Roots_Convert**: Must be containerized before PostgreSQL migration
- **Benefits**: Eliminates "works on my laptop" issues, ensures repeatability, validates RLS isolation early

### Immutable Architecture
Design pattern where data is never modified in place:
- **Append-Only**: New versions created rather than updates
- **Complete History**: Full audit trail of all changes
- **Concurrent Safety**: Multiple users can work without conflicts

### Home Inspection
Automated health check system for codebases:
- **Execution**: Run via 🏠 Run Home Inspection.command
- **Coverage**: Validates structure, state management, logging, security, and more
- **Reports**: Generates human-readable and JSON/HTML dashboards
- **Threshold**: Must achieve >90% score before completing tasks
- **Extension**: Roots_Convert will adopt a similar inspection script

### Faceted Search
Multi-dimensional filtering system:
- **Auto-Populated**: Filter options generated from existing data
- **Real-Time Updates**: Filter counts update as selections change
- **Canonical Facets**: Standardized categories for consistent classification

### CI/CD Pipeline
Automated workflow for quality enforcement:
- **Scope**: Builds containers, runs unit/integration tests, executes Home Inspection
- **Integration**: GitHub Actions pipeline for both AInfographics.v2 and Roots_Convert
- **Quality Gates**: Fail on integrity errors, latency regressions, or inspection score <90%
- **Artifacts**: Upload inspection reports for team visibility

## User Roles

### Editor
Basic user role with personal customization abilities:
- **Scope**: Can set user-level primary versions
- **Permissions**: Create and edit own content
- **Workspace Access**: Typically limited to prod workspace

### Curator
Organizational content manager:
- **Scope**: Can set org-level primary versions affecting team members
- **Permissions**: Moderate discussions, promote quality content
- **Workflow**: Review and approve user-generated improvements

### Admin
System administrator with full platform access:
- **Scope**: Can set global primary versions affecting all users
- **Permissions**: Full database access, promotion workflows
- **Responsibilities**: System maintenance, user management, data integrity

### Researcher
Specialized role for research team members:
- **Scope**: Access to roots workspace for experimental work
- **Functions**: Bulk operations, model testing, primary designation
- **Workflow**: Develop content in research environment before production

## Data Flow Concepts

### Promotion Workflow
Process of moving content from research to production:
- **Source**: Artifacts in workspace='roots'
- **Target**: Head pointers in workspace='prod'
- **Mechanism**: O(1) pointer updates with audit trail
- **Approval**: Only artifacts with status='approved' eligible
- **Rollback Support**: Every promotion must be reversible via audit trail and backups

### Embedding Pipeline
Automated process for generating semantic representations:
- **Trigger**: New study or abstract content
- **Processing**: OpenAI API calls with rate limiting
- **Storage**: Vector embeddings with SHA256 checksums, resilient to transient API failures (retry logic)
- **Indexing**: HNSW indexes for fast similarity queries

### Topic Discovery
Automated identification of research themes:
- **Clustering**: HDBSCAN algorithm on study embeddings
- **Labeling**: LLM-generated descriptive labels for clusters
- **Membership**: Studies associated with topics via strength scores
- **Evolution**: Periodic re-clustering to capture emerging themes
- **Transparency**: Cluster membership and labels must be explainable to users

## Quality Metrics

### Confidence Scoring
Numerical assessment of automated processes:
- **Range**: 0.0 to 1.0 with higher values indicating greater certainty
- **Auto-Tagging**: Machine learning confidence in facet assignments
- **Threshold**: Typically 0.6+ for user-visible recommendations
- **Validation**: LLM confirmation of high-confidence assignments
- **Continuous Monitoring**: Confidence distributions tracked over time to detect drift

### Similarity Scoring
Quantitative measure of content relationships:
- **Calculation**: 1 - cosine_distance for intuitive interpretation
- **Range**: 0.0 (dissimilar) to 1.0 (identical)
- **Use Cases**: Related studies, duplicate detection, clustering
- **Precision**: Typically >90% accuracy for top-5 recommendations
- **Threshold Tuning**: Adjustable per use-case to balance recall vs precision

---

*This glossary ensures consistent terminology across all project documentation and implementation.*
