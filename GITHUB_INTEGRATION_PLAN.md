
# GitHub Integration Plan for Unified Platform

## ✅ Prerequisites
- **Repo permissions**: Actions can write contents and open PRs (Settings → Actions → Workflow permissions → Read and write).
- **Secrets**: `OPENAI_API_KEY` (and `ANTHROPIC_API_KEY` if using Claude), plus any app-specific env (never hardcode DB creds).
- **Branch protection**: Require status checks to pass before merging (tests + Home Inspection + quality gates).
- **Project enablement**: A GitHub Project (Beta) created for the board; milestones for Phases 0–4.

## 🎯 **Integration Overview**

Transform spec-kit tasks into fully tracked GitHub workflow with automated quality gates and visual progress monitoring.

## 🏗️ **GitHub Structure Design**

### **1. Issues Mapping**
Each task in `tasks.md` becomes a GitHub Issue:

```
Title: (T-001) Create unified schema in AInfographics.v2
Labels: phase-1, database, ainfographics, critical
Milestone: Phase 1: Database Foundation
Body:
- Implementation: Execute complete PostgreSQL schema with workspace isolation, RLS policies
- Location: /Users/markdarby/projects/AInfographics.v2/database/
- Testing: Verify all tables created, RLS policies active, foreign key constraints enforced
- Home Inspection: Run inspection, ensure database connectivity checks pass
- Acceptance: All tables, indexes, RLS policies, triggers created successfully

Checklist:
- [ ] Implementation complete
- [ ] Tests passing
- [ ] Home inspection >90%
- [ ] Git commit with T-001 reference
```

### **2. Milestone Structure**
```
Phase 0: Environment Preparation (Week 0.5)
├── T-000a: Create Roots_Convert Dockerfile
├── T-000b: Integrate into docker-compose
├── T-000c: Database connectivity smoke test
├── T-000d: Verify JSON functionality in Docker
├── T-000e: Initialize GitHub for Roots_Convert
└── T-000f: Add CI pipeline

Phase 1: Database Foundation (Weeks 1-2)
├── T-001: Create unified schema
├── T-002: Backup existing database
├── T-003: Install pgVector
├── T-004: Extract 717 studies from JSON
├── T-005: Create immutable artifacts
├── T-006: Set initial primary versions
└── T-007: Generate study embeddings

Phase 2: Smart Features (Weeks 3-4)
Phase 3: Roots_Convert Migration (Weeks 5-6)
Phase 4: Integration & Polish (Weeks 7-8)
```

### **3. Project Board Layout**
```
┌─────────────┬─────────────┬─────────────┬─────────────┬─────────────┐
│   Backlog   │ In Progress │   Review    │   Testing   │    Done     │
├─────────────┼─────────────┼─────────────┼─────────────┼─────────────┤
│ T-001       │ T-000a      │ T-000b      │ T-000c      │ T-000d      │
│ T-002       │             │             │             │             │
│ T-003       │             │             │             │             │
│ ...         │             │             │             │             │
└─────────────┴─────────────┴─────────────┴─────────────┴─────────────┘
```

### **4. Label System**
```yaml
# Phase Labels
phase-0: Environment Preparation
phase-1: Database Foundation
phase-2: Smart Features
phase-3: Roots_Convert Migration
phase-4: Integration & Polish

# Project Labels
ainfographics: AInfographics.v2 work
roots-convert: Roots_Convert work
cross-project: Affects both projects

# Priority Labels
critical: Blocking other tasks
high: Important for phase completion
medium: Standard priority
low: Nice to have

# Type Labels
database: Database/schema work
frontend: UI/React work
backend: API/Python work
docker: Containerization
testing: Test implementation
documentation: Docs/specs
```

## 🤖 **Multi-AI GitHub Action Workflows**

### **Dual AI Strategy**
Deploy both Claude Code and OpenAI GPT workflows for maximum flexibility:

#### **Claude Code Workflow** (Primary)
- Best for: Architecture decisions, complex reasoning, detailed analysis
- Trigger: Manual dispatch or label `claude-run`
- Use cases: Database schema, system design, integration planning

#### **OpenAI GPT Workflow** (Secondary)
- Best for: Code generation, rapid prototyping, specific implementations
- Trigger: Manual dispatch or label `gpt-run`
- Use cases: Frontend components, API endpoints, utility functions

### **AI Model Selection Guide**
```yaml
# Task Type → Recommended AI
Database Schema: Claude (architectural reasoning)
Frontend Components: GPT-4 (rapid code generation)
Integration Logic: Claude (complex system understanding)
Bug Fixes: GPT-4o (speed + efficiency)
Documentation: Claude (comprehensive analysis)
Unit Tests: GPT-4 (pattern-based generation)
```

## 🤖 **Automated GitHub Action Workflows**

### **1. Issue Generation from Spec-Kit**
```yaml
# .github/workflows/sync-spec-to-issues.yml
name: Sync Spec-Kit to GitHub Issues

on:
  push:
    paths:
      - 'tasks.md'
  workflow_dispatch:

jobs:
  sync-tasks:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Parse tasks.md and create/update issues
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');

            const md = fs.readFileSync('tasks.md', 'utf8');
            const taskRegex = /^- \[ \] \((T-\d{3}[a-z]?)\) \*\*(.+?)\*\*/gm;

            // Map Phase headers to milestones
            const lines = md.split('\n');
            let currentMilestone = null;
            const tasks = [];
            for (let i = 0; i < lines.length; i++) {
              const line = lines[i];

              const phaseMatch = line.match(/^##\s+(Phase\s+\d+):\s+(.+?)\s*(?:-|—)/);
              if (phaseMatch) {
                currentMilestone = `${phaseMatch[1]}: ${phaseMatch[2].trim()}`;
                continue;
              }

              const m = /^- \[ \] \((T-\d{3}[a-z]?)\) \*\*(.+?)\*\*/.exec(line);
              if (m) {
                const id = m[1];
                const title = `(${id}) ${m[2]}`;
                // Collect body from indented sub-bullets until next top-level task
                let j = i + 1, bodyLines = [];
                while (j < lines.length && !lines[j].match(/^- \[ \] \(\T-\d{3}[a-z]?\)/)) {
                  bodyLines.push(lines[j]); j++;
                }
                const body = bodyLines.join('\n');
                tasks.push({ id, title, body, milestone: currentMilestone });
              }
            }

            // Ensure milestones exist and upsert issues idempotently by title
            async function ensureMilestone(title) {
              const { data: milestones } = await github.rest.issues.listMilestones({
                owner: context.repo.owner, repo: context.repo.repo, state: 'open'
              });
              let m = milestones.find(x => x.title === title);
              if (!m) {
                const created = await github.rest.issues.createMilestone({
                  owner: context.repo.owner, repo: context.repo.repo, title
                });
                m = created.data;
              }
              return m.number;
            }

            for (const t of tasks) {
              const labels = [];
              if (t.milestone?.match(/^Phase 0/)) labels.push('phase-0');
              if (t.milestone?.match(/^Phase 1/)) labels.push('phase-1');
              if (t.milestone?.match(/^Phase 2/)) labels.push('phase-2');
              if (t.milestone?.match(/^Phase 3/)) labels.push('phase-3');
              if (t.milestone?.match(/^Phase 4/)) labels.push('phase-4');

              // Check if issue already exists by exact title
              const { data: existing } = await github.rest.search.issuesAndPullRequests({
                q: `repo:${context.repo.owner}/${context.repo.repo} in:title "${t.title}"`
              });
              let issueNumber = existing.items?.find(i => i.title === t.title)?.number;

              const milestoneNumber = t.milestone ? await ensureMilestone(t.milestone) : undefined;

              if (!issueNumber) {
                const created = await github.rest.issues.create({
                  owner: context.repo.owner, repo: context.repo.repo,
                  title: t.title,
                  body: `${t.body}\n\n_Checklist:_\n- [ ] Implementation complete\n- [ ] Tests passing\n- [ ] Home inspection >90%\n- [ ] Git commit with ${t.id} reference`,
                  labels, milestone: milestoneNumber
                });
                issueNumber = created.data.number;
              } else {
                await github.rest.issues.update({
                  owner: context.repo.owner, repo: context.repo.repo,
                  issue_number: issueNumber,
                  body: `${t.body}\n\n_Checklist:_\n- [ ] Implementation complete\n- [ ] Tests passing\n- [ ] Home inspection >90%\n- [ ] Git commit with ${t.id} reference`,
                  labels, milestone: milestoneNumber
                });
              }
            }
```

### **2. OpenAI GPT Task Runner**
```yaml
# .github/workflows/gpt-task-runner.yml
name: GPT Task Runner

on:
  workflow_dispatch:
    inputs:
      task_id:
        description: "Task ID (e.g., T-001)"
        required: true
      working_repo:
        description: "Target repo path (e.g., AInfographics.v2 or Roots_Convert)"
        required: true
        default: "AInfographics.v2"
      model:
        description: "OpenAI model (e.g., gpt-4.1, gpt-4o, gpt-4o-mini)"
        required: false
        default: "gpt-4.1"

jobs:
  run-task:
    runs-on: ubuntu-latest
    permissions:
      contents: write
      pull-requests: write
    steps:
      - name: Checkout repo
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install deps
        run: |
          python -m pip install --upgrade pip
          pip install openai regex

      - name: Run GPT task
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          TASK_ID: ${{ github.event.inputs.task_id }}
          WORKING_REPO: ${{ github.event.inputs.working_repo }}
          OPENAI_MODEL: ${{ github.event.inputs.model }}
        run: |
          python scripts/gpt_task_runner.py

      - name: Quick inspection hook (optional)
        if: success()
        run: |
          if [ "${{ github.event.inputs.working_repo }}" = "AInfographics.v2" ]; then
            cd AInfographics.v2 && npm ci && node scripts/inspect-for-humans.js || true
          fi

      - name: Install GitHub CLI
        uses: cli/cli-action@v2

      - name: Create PR
        if: success()
        env:
          GH_TOKEN: ${{ github.token }}
        run: |
          BRANCH="feat/${{ github.event.inputs.task_id }}-gpt"
          git config user.name "ai-runner"
          git config user.email "ai-runner@users.noreply.github.com"
          git checkout -b "$BRANCH" || true
          git add -A
          git commit -m "${{ github.event.inputs.task_id }}: GPT patch" || echo "Nothing to commit"
          git push -u origin "$BRANCH" || true
          gh pr create --title "${{ github.event.inputs.task_id }}: GPT implementation" \
            --body "Automated patch by GPT Task Runner.\nTask: ${{ github.event.inputs.task_id }}" \
            --base main || true
```

### **3. GPT Task Runner Script**
```python
# scripts/gpt_task_runner.py
import os, re, subprocess, pathlib
from openai import OpenAI

ROOT = pathlib.Path(".")
TASK_ID = os.environ["TASK_ID"]
WORKING_REPO = os.environ["WORKING_REPO"]
MODEL = os.environ.get("OPENAI_MODEL", "gpt-4.1")

def read(p):
    return pathlib.Path(p).read_text(encoding="utf-8")

# Load Spec-Kit docs
spec = read("spec.md")
plan = read("plan.md")
constitution = read("CONSTITUTION.md")
glossary = read("GLOSSARY.md")
tasks = read("tasks.md")

# Extract the task block by T-ID
m = re.search(rf"- \[ \] \({re.escape(TASK_ID)}\).*?(?=\n- \[ \] \(|\Z)", tasks, re.S)
if not m:
    raise SystemExit(f"Task {TASK_ID} not found in tasks.md")
task_block = m.group(0)

system_prompt = """You are a senior engineer working from a Spec-Kit repo.
Follow the Constitution (non-negotiables). Use the plan for HOW and the spec for WHAT/WHY.
Produce minimal, targeted changes to implement EXACTLY the requested task.
Return a unified diff patch (git apply format) for existing files and/or explicit new files with full paths.
Include tests when appropriate. Do not modify the Constitution unless explicitly asked.
"""

user_prompt = f"""
CONSTITUTION.md:
{constitution}

spec.md:
{spec}

plan.md:
{plan}

GLOSSARY.md:
{glossary}

tasks.md (excerpt for {TASK_ID}):
{task_block}

Working directory for code changes: {WORKING_REPO}

Goal: Implement ONLY {TASK_ID}.
Output strictly in this order:
1) Short implementation plan (3–6 bullets).
2) Unified diff patch starting with 'diff --git' OR clearly marked 'NEW FILE:' sections with full content.
3) Short test/inspection plan (commands).
"""

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

resp = client.chat.completions.create(
    model=MODEL,
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ],
    temperature=0.2
)

content = resp.choices[0].message.content or ""
print(content)

# Try to auto-apply a unified diff if present
patch_start = content.find("diff --git")
if patch_start != -1:
    patch = content[patch_start:]
    (ROOT / "ai.patch").write_text(patch, encoding="utf-8")
    # apply patch relative to working repo dir
    subprocess.run(["git", "apply", "ai.patch", "--directory", WORKING_REPO], check=False)
else:
    # Optionally parse "NEW FILE:" sections and write them out
    pass
```

### **4. Quality Gate Enforcement**
```yaml
# .github/workflows/quality-gates.yml
name: Quality Gates

on:
  pull_request:
    types: [opened, synchronize]

jobs:
  test-phase:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run tests
        run: |
          # Run unit tests, integration tests
          # Set exit code based on results

  home-inspection:
    runs-on: ubuntu-latest
    needs: test-phase
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - name: Install deps & run inspection
        run: |
          cd AInfographics.v2
          npm ci
          npm run inspect:json
      - name: Check inspection score
        run: |
          SCORE=$(jq '.overallHealth.percentage' AInfographics.v2/reports/home-inspection.json)
          echo "Score: $SCORE"
          awk 'BEGIN { if ('$SCORE' < 90) exit 1 }'
      - name: Upload inspection report
        uses: actions/upload-artifact@v4
        with:
          name: home-inspection-report
          path: AInfographics.v2/reports/

  enforce-commit-format:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Validate commit messages
        run: |
          # Check that commits reference T-XXX task IDs
          git log --format="%s" ${{ github.event.before }}..${{ github.sha }} | \
          grep -E "^T-[0-9]{3}[a-z]?:" || {
            echo "❌ Commits must start with T-XXX: format"
            exit 1
          }
```

### **3. Progress Tracking Automation**
```yaml
# .github/workflows/progress-tracking.yml
name: Progress Tracking

on:
  issues:
    types: [closed]
  pull_request:
    types: [merged]

jobs:
  update-progress:
    runs-on: ubuntu-latest
    steps:
      - name: Update milestone progress
        uses: actions/github-script@v7
        with:
          script: |
            // Calculate milestone completion percentages
            // Update README.md with progress badges
            // Post to Slack/Discord if configured

      - name: Check phase completion
        uses: actions/github-script@v7
        with:
          script: |
            // If all issues in milestone closed, create release
            // Tag version, generate changelog
            // Notify team of phase completion
```
> Note: The progress tracking script is illustrative. You will need to adapt it to your milestone naming, desired README badge targets, and any external notifications (Slack/Discord).

## 📊 **Visual Progress Tracking**

### **1. README.md Progress Badges**
```markdown
# Unified Platform Development Progress

## 🎯 Phase Progress
![Phase 0](https://img.shields.io/badge/Phase%200-100%25-success)
![Phase 1](https://img.shields.io/badge/Phase%201-60%25-yellow)
![Phase 2](https://img.shields.io/badge/Phase%202-0%25-lightgrey)
![Phase 3](https://img.shields.io/badge/Phase%203-0%25-lightgrey)
![Phase 4](https://img.shields.io/badge/Phase%204-0%25-lightgrey)

## 📈 Overall Progress
![Overall](https://img.shields.io/badge/Overall%20Progress-32%25-orange)

## 🏠 Quality Metrics
![Home Inspection](https://img.shields.io/badge/Home%20Inspection-91.8%25-brightgreen)
![Tests](https://img.shields.io/badge/Tests-Passing-brightgreen)
```

### **2. GitHub Project Dashboard**
- **Kanban view**: Visual task flow across columns
- **Burn-down charts**: Track velocity and completion trends
- **Filter views**: By phase, project, priority, assignee
- **Milestone tracking**: Automatic percentage completion

### **3. Release Management**
```yaml
# Auto-create releases when phases complete
v0.1.0: Phase 0 - Environment Preparation Complete
v0.2.0: Phase 1 - Database Foundation Complete
v0.3.0: Phase 2 - Smart Features Complete
v0.4.0: Phase 3 - Roots_Convert Migration Complete
v1.0.0: Phase 4 - Unified Platform Complete
```

## 🔗 **Integration Benefits**

### **Development Workflow**
1. **Start Task**: Move issue from Backlog → In Progress
2. **Create Branch**: `feature/T-001-unified-schema`
3. **Develop**: Implement with continuous testing
4. **Quality Gates**: PR checks run automatically
5. **Review**: Code review + home inspection results
6. **Merge**: Issue auto-closes, moves to Done
7. **Progress**: Milestone percentage updates automatically

### **Stakeholder Visibility**
- **Real-time progress**: Project board shows current status
- **Quality trends**: Home inspection scores over time
- **Velocity tracking**: Tasks completed per week
- **Risk identification**: Blocked or overdue tasks highlighted

### **AI Assistant Continuity**
- **Context preservation**: Every task has persistent GitHub issue
- **Progress awareness**: AI can query GitHub API for current status
- **Quality enforcement**: CI prevents regressions
- **Traceability**: Complete audit trail from spec → implementation

## 📱 **Mobile Development Control**

### **iPhone GitHub App Workflow**
Transform your phone into a development control center:

```
iPhone GitHub App Workflow:
1. Actions → GPT Task Runner → Run workflow
2. Select: task_id (T-001), working_repo (AInfographics.v2), model (gpt-4)
3. Watch real-time logs in Actions tab
4. Review generated PR from mobile
5. Check quality gates: tests ✅, home inspection 92% ✅
6. Merge PR directly from phone
7. Monitor milestone progress update automatically
- Both **GPT Task Runner** and **Claude Task Runner** workflows are available in the Actions tab and can be run from mobile.
```

### **Advanced Multi-AI Strategies**

#### **A/B Testing AI Approaches**
```yaml
# .github/workflows/ai-comparison.yml
name: AI Comparison Test

on:
  workflow_dispatch:
    inputs:
      task_id:
        description: "Task to test with multiple AIs"
        required: true

jobs:
  claude-approach:
    runs-on: ubuntu-latest
    steps:
      # Run same task with Claude Code

  gpt-approach:
    runs-on: ubuntu-latest
    steps:
      # Run same task with OpenAI GPT

  compare-results:
    needs: [claude-approach, gpt-approach]
    runs-on: ubuntu-latest
    steps:
      # Compare home inspection scores, test coverage, performance
      # Create comparison report with recommendations
```

#### **Label-Triggered Automation**
```yaml
# .github/workflows/label-triggers.yml
name: Label-Triggered AI

on:
  issues:
    types: [labeled]

jobs:
  auto-run:
    if: contains(github.event.label.name, 'ai-run')
    runs-on: ubuntu-latest
    steps:
      # Extract T-ID from issue title
      # Choose AI based on task type
      # Auto-execute with appropriate model
```

#### **AI Model Selection Matrix**
```yaml
# Automatic AI selection based on task patterns
Task Patterns:
  "database|schema|migration": claude-4  # Architecture
  "frontend|component|ui": gpt-4         # Code generation
  "integration|workflow": claude-4        # Complex logic
  "test|unit|spec": gpt-4o               # Pattern-based
  "documentation|readme": claude-4       # Analysis
  "bugfix|hotfix": gpt-4o-mini          # Speed + efficiency
```

### **Repository Secrets Setup**
```
GitHub Repo → Settings → Secrets and variables → Actions:

Required Secrets:
- OPENAI_API_KEY: Your OpenAI API key
- DATABASE_URL: Connection string (for integration tests)
- ANTHROPIC_API_KEY: For Claude Code workflows (if added)

Optional Secrets:
- SLACK_WEBHOOK: Progress notifications
- DISCORD_WEBHOOK: Team updates
```

## 🚀 **Implementation Steps**

1. **Setup GitHub Structure** (30 minutes)
   - Create milestones for each phase
   - Set up project board with columns
   - Configure label system

2. **Generate Initial Issues** (15 minutes)
   - Parse current tasks.md
   - Create issues for all T-XXX tasks
   - Assign to appropriate milestones

3. **Configure CI/CD** (45 minutes)
   - Set up quality gate workflows
   - Configure home inspection automation
   - Add progress tracking automation

4. **Test Integration** (30 minutes)
   - Create test PR with T-XXX commit
   - Verify quality gates run
   - Check progress updates work

**Total Setup Time: ~2 hours for complete automation**

---

*This GitHub integration transforms the spec-kit from static documentation into a living, tracked, and enforced development pipeline.*

## 🔐 Security & Compliance Notes
- Never print API keys or secrets in workflow logs (`echo $SECRET` is forbidden).
- Prefer repository **Environments** with required reviewers for sensitive secrets.
- Restrict AI runners to read-only on branches except the dedicated `feat/T-xxx-ai` branches they create.
- Gate merges with branch protection: require passing checks (tests + inspection + lint).
- Log AI-generated diffs to PR comments; always require human review before merge.
