# Unified Research Platform Specification

## What We're Building

Transform two separate research projects into a unified, intelligent platform that enables semantic discovery, collaborative editing, and seamless research-to-production workflows.

### Current State
- **Roots_Convert**: 717 studies in JSON format with multiple summary versions
- **AInfographics.v2**: Production PostgreSQL database with user management
- **Commentary System**: 95 studies enhanced with GPT-5 extracted insights
- **pgVector Ready**: Semantic search tested and proven on 9 studies

### Target Vision
A unified PostgreSQL platform with workspace isolation that serves both research workflows and production users while enabling intelligent discovery through semantic search and auto-categorization.

## Core Capabilities

### 1. Workspace-Isolated Research Platform
**What**: Single database with `workspace='roots'` and `workspace='prod'` partitions
**Why**: Eliminates dual-database synchronization complexity while maintaining clean separation
**For**: Researchers need bulk operations; users need stable, curated content

### 2. Immutable Version Management
**What**: All content stored as immutable artifacts with head pointers for "primary" versions
**Why**: Preserves complete history while enabling O(1) promotion workflows
**For**: Multiple users creating unlimited versions without conflicts

### 3. Intelligent Auto-Categorization
**What**: Embedding-based facet tagging (agent, population, outcome, design, duration)  
**Constraint**: Facet schema must be extensible to accommodate new categories without re-migration
**Why**: Eliminates manual categorization bottlenecks as content scales
**For**: Researchers and users discovering relevant studies without manual curation

### 4. Semantic Discovery System
**What**: pgVector-powered similarity search with hybrid text+embedding queries
**Why**: Surface hidden relationships and enable concept-based discovery
**For**: Users finding related studies beyond keyword matching

### 5. Collaborative Research Workflows
**What**: Multi-user editing with threaded discussions and promotion pipelines
**Why**: Enable community-driven content improvement and quality assurance
**For**: Research teams collaborating on summary enhancement

## User Scenarios

### Research Team Workflow
1. **Bulk Processing**: Upload 100+ new studies via Roots_Convert interface
2. **Model Testing**: Generate summaries with different AI models for comparison
3. **Quality Review**: Designate primary versions based on research criteria
4. **Promotion**: Push approved content to production with O(1) operations

### Production User Experience
1. **Semantic Search**: Enter concepts like "cardiovascular risk" and find relevant studies
2. **Faceted Filtering**: Combine filters like "testosterone + RCT + 12 months"
3. **Discovery**: View related studies panel showing similar research
4. **Collaboration**: Edit summaries and participate in threaded discussions

### Content Curator Workflow
1. **Review Pipeline**: Monitor user-generated improvements to summaries
2. **Quality Assessment**: Use confidence scores and community feedback
3. **Promotion Decisions**: Elevate high-quality user edits to organizational defaults
4. **Topic Discovery**: Identify emerging research themes through clustering

## Technical Requirements

### Database Architecture
- **Single PostgreSQL database** with workspace-based partitioning
- **Immutable artifacts table** storing all content versions
- **Head pointers system** for primary version management
- **pgVector extension** for semantic search capabilities
- **Default embedding model**: text-embedding-3-large (3072-d) for semantic search

### Performance Standards
- Sub-second search response for 10,000+ studies
- Vector similarity queries completing in <200ms
- Batch operations supporting 100+ concurrent studies
- Auto-tagging accuracy ≥85% vs manual classification

### Integration Points
- **AInfographics.v2**: Enhanced with semantic search and collaborative features
- **Roots_Convert**: Migrated from JSON to PostgreSQL workspace='roots'
- **Cross-Workspace**: Promotion workflows and shared embedding indexes

### Data Migration
- All 717 studies preserved with complete metadata
- Multiple summary versions converted to immutable artifacts
- 95 commentary-enhanced studies migrated to threaded discussion format
- Existing user workflows maintained throughout transition

## Success Measures

### User Adoption
- 80% of searches utilize semantic/faceted filtering
- 60% of users create custom summary versions
- 90% user satisfaction with related studies recommendations
- 50% increase in average session engagement time

### Technical Performance
- 100% successful data migration without loss
- 99.9% uptime for production database
- Auto-tagging reduces manual categorization by >80%
- Vector search precision ≥90% for similarity recommendations

### Research Impact
- Community-edited summaries rate 20% higher quality
- Topic clusters cover 90% of research themes automatically
- Production content reflects latest research findings
- Cross-study relationships discovered through semantic analysis

## Constraints and Assumptions

### Technical Constraints
- Must use existing PostgreSQL infrastructure
- Preserve all existing data and functionality
- Maintain API compatibility during migration
- Support multi-user concurrent access

### Business Constraints
- Two-project coordination (70% AInfographics.v2, 30% Roots_Convert)
- 8-week implementation timeline
- Resource allocation based on existing team structure
- Backward compatibility with current user workflows

### Data Constraints
- Public PubMed abstracts only (no patient data)
- Standard web development security practices appropriate
- 717 studies with potential for scaling to thousands
- Multiple summary types: clinical, patient, commentary, infographic

## Quality Attributes

### Reliability
- Daily automated backups with integrity checks on restore (before and after schema changes)
- Complete rollback procedures for failed migrations
- Audit trails for all data modifications
- Row-level security enforcing workspace isolation, user ownership of artifacts, and curator-only approval for production content

### Scalability
- Database design supports 10x current study volume
- Embedding generation optimized for batch processing
- Auto-tagging pipeline handles continuous content addition
- UI responsive with thousands of concurrent users

### Maintainability
- Clear separation between research and production concerns
- Modular architecture supporting independent development
- Comprehensive documentation for all major components
- CI/CD pipelines run automated integrity checks (no orphan artifacts, valid head pointers, embedding coverage) and performance benchmarks
- Spec-driven development ensuring consistent implementation

---

*This specification provides the foundation for technical planning and implementation across both project codebases.*
