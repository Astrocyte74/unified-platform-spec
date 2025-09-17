# scripts/gpt_task_runner.py
import os, re, subprocess, pathlib, sys
from openai import OpenAI

ROOT = pathlib.Path(".")
TASK_ID = os.environ["TASK_ID"]
WORKING_REPO = os.environ.get("WORKING_REPO", ".")
MODEL = os.environ.get("OPENAI_MODEL", "gpt-5-mini")

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
    print(f"Task {TASK_ID} not found in tasks.md", file=sys.stderr)
    sys.exit(1)
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
    # apply patch relative to working repo dir (e.g., ".", "AInfographics.v2", "Roots_Convert")
    subprocess.run(["git", "apply", "ai.patch", "--directory", WORKING_REPO], check=False)