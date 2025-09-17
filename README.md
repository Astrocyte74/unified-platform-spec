# Unified Research Platform - Spec-Kit Project

## 🎯 Project Overview

This spec-kit project serves as the **single source of truth** for implementing the unified research platform that transforms Roots_Convert and AInfographics.v2 into a coordinated workspace-isolated system.

## 📁 Project Structure

```
unified-platform-spec/
├── spec.md               # WHAT we're building and WHY
├── plan.md               # HOW to implement technically
├── tasks.md              # Actionable implementation tasks
├── CONSTITUTION.md       # Non-negotiable architectural principles
├── GLOSSARY.md          # Consistent terminology definitions
└── README.md            # This file
```

## 🚀 Getting Started

### For AI Assistants
1. **Read `CONSTITUTION.md` first** - Non-negotiable principles
2. **Review `spec.md`** - Understand the vision and user scenarios
3. **Study `plan.md`** - Technical architecture and implementation strategy
4. **Execute `tasks.md`** - Phase-by-phase implementation with acceptance criteria

### For Human Developers
1. Open this directory in VS Code with Claude Code extension (or any Spec-Kit compatible IDE/agent such as Cursor or JetBrains)
2. Use `/specify`, `/plan`, and `/tasks` commands to iterate on specifications
3. Reference target codebases:
   - `/Users/markdarby/projects/AInfographics.v2/` (70% of work)
   - `/Users/markdarby/projects/Roots_Convert/` (30% of work)

## 🔄 Workflow Commands

```bash
# Update specifications
/specify "Add new capability or modify existing requirements"

# Refine technical implementation
/plan

# Generate updated task breakdown
/tasks
```

## 🎯 Implementation Strategy

### Phase 0: Environment Preparation (Week 0.5)
- **CRITICAL**: Dockerize Roots_Convert for environment parity
- Container integration with shared PostgreSQL
- RLS workspace isolation (`APP_WORKSPACE=roots`)

### Phase 1: Database Foundation (AInfographics.v2, Weeks 1-2)
- Schema creation with workspace isolation
- Data migration from Roots_Convert JSON
- pgVector setup and embedding generation (text-embedding-3-large, 3072-d)

### Phase 2: Smart Features (AInfographics.v2, Weeks 3-4)
- Semantic search implementation
- Auto-tagging pipeline with extensible facet schema
- Enhanced frontend with faceted filtering

### Phase 3: Roots_Convert Migration (Weeks 5-6)
- PostgreSQL backend integration
- Research workflow enhancement
- Primary version designation interface

### Phase 4: Integration & Polish (Weeks 7-8)
- Promotion workflows between workspaces
- Collaborative editing features
- Performance optimization

## 📊 Success Criteria

- ✅ All 717 studies migrated without data loss
- ✅ Semantic search with >90% precision
- ✅ Sub-second query performance maintained
- ✅ Auto-tagging accuracy ≥85%
- ✅ Collaborative editing without conflicts
+ ✅ Continuous integrity and latency checks in CI/CD

## 🔗 Related Documentation

### In Roots_Convert Project
- `PRD_UNIFIED_PLATFORM_FINAL.md` - Complete technical PRD
- `POSTGRESQL_MIGRATION_STRATEGY.md` - Detailed migration procedures
- `CLAUDE.md` - Current system context
- `DEVELOPMENT_LESSONS_LEARNED.md` - Best practices

### Key Principles
- **Single Database**: Workspace isolation, not dual-database sync
- **Immutable Versioning**: All content as artifacts with head pointers
- **O(1) Promotion**: Pointer updates for research → production
- **Semantic Intelligence**: pgVector embeddings for discovery
+ **Resilience**: Automated backups + RLS-enforced isolation

---

*This spec-kit project ensures consistent implementation across both codebases and provides persistent context for AI assistants.*
