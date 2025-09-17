#!/usr/bin/env python3
"""
Minimal Home Inspection script for CI:
- Creates the minimal schema (studies, artifacts, artifact_heads, study_embeddings)
- Inserts a small set of sample rows
- Runs integrity SQL checks from the plan:
  * No orphan artifacts (artifacts.study_id must reference studies)
  * Heads point to valid artifacts
  * Embedding coverage percent computed
  * Simple latency probe (a basic query must complete under threshold)

On failure, exits with non-zero status.
Writes a JSON report to the provided --report path.
"""
import argparse
import json
import os
import sys
import time
from contextlib import closing

import psycopg2

DEFAULT_DB_URL = "postgresql://ai_user:postgres@localhost:5432/ai_infographic"

def run_sql(conn, sql, params=None):
    with conn.cursor() as cur:
        cur.execute(sql, params or ())
        try:
            return cur.fetchall()
        except psycopg2.ProgrammingError:
            return None

def setup_schema(conn):
    sql = """
    CREATE EXTENSION IF NOT EXISTS pgcrypto;
    CREATE TABLE IF NOT EXISTS studies (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        pmid TEXT UNIQUE,
        title TEXT NOT NULL,
        abstract TEXT,
        journal TEXT,
        year INT,
        metadata JSONB,
        created_at TIMESTAMPTZ DEFAULT now()
    );

    CREATE TABLE IF NOT EXISTS artifacts (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        study_id UUID NOT NULL REFERENCES studies(id),
        artifact_type TEXT NOT NULL,
        workspace TEXT NOT NULL CHECK (workspace IN ('roots', 'prod')),
        content JSONB NOT NULL,
        model_id TEXT,
        created_by TEXT NOT NULL,
        status TEXT DEFAULT 'draft' CHECK (status IN ('draft','proposed','approved','archived')),
        supersedes_id UUID REFERENCES artifacts(id),
        created_at TIMESTAMPTZ DEFAULT now()
    );

    CREATE TABLE IF NOT EXISTS artifact_heads (
        study_id UUID NOT NULL REFERENCES studies(id),
        artifact_type TEXT NOT NULL,
        workspace TEXT NOT NULL CHECK (workspace IN ('roots', 'prod')),
        scope TEXT NOT NULL CHECK (scope IN ('global', 'org', 'user')),
        scope_id TEXT,
        artifact_id UUID NOT NULL REFERENCES artifacts(id),
        updated_by TEXT NOT NULL,
        updated_at TIMESTAMPTZ DEFAULT now(),
        UNIQUE(study_id, artifact_type, workspace, scope, scope_id)
    );

    CREATE EXTENSION IF NOT EXISTS vector;
    CREATE TABLE IF NOT EXISTS study_embeddings (
        study_id UUID PRIMARY KEY REFERENCES studies(id) ON DELETE CASCADE,
        model TEXT NOT NULL DEFAULT 'text-embedding-3-large',
        embedding vector(1),
        abstract_sha256 TEXT,
        created_at TIMESTAMPTZ DEFAULT now()
    );
    """
    run_sql(conn, sql)
    conn.commit()

def insert_sample_data(conn):
    # Insert one study, one artifact, one head, one embedding
    with conn.cursor() as cur:
        cur.execute("INSERT INTO studies (pmid, title, abstract, journal, year) VALUES (%s,%s,%s,%s,%s) RETURNING id",
                    ('0000000', 'CI sample study', 'Sample abstract', 'CI Journal', 2025))
        study_id = cur.fetchone()[0]

        cur.execute(
            "INSERT INTO artifacts (study_id, artifact_type, workspace, content, created_by, status) VALUES (%s,%s,%s,%s,%s,%s) RETURNING id",
            (study_id, 'clinical', 'roots', json.dumps({'summary': 'initial'}), 'ci_user', 'approved')
        )
        artifact_id = cur.fetchone()[0]

        cur.execute(
            "INSERT INTO artifact_heads (study_id, artifact_type, workspace, scope, scope_id, artifact_id, updated_by) VALUES (%s,%s,%s,%s,%s,%s,%s)",
            (study_id, 'clinical', 'roots', 'global', None, artifact_id, 'ci_user')
        )

        # For embedding column we created vector(1) to keep it simple in CI
        cur.execute(
            "INSERT INTO study_embeddings (study_id, model, embedding, abstract_sha256) VALUES (%s,%s,%s,%s)",
            (study_id, 'text-embedding-3-large', '[0.1]' , 'dummysha')
        )
    conn.commit()

def run_integrity_checks(conn, thresholds=None):
    thresholds = thresholds or {}
    report = {'checks': [], 'ok': True}

    # 1) No orphan artifacts
    sql_orphan = """
    SELECT COUNT(*) FROM artifacts a
    LEFT JOIN studies s ON s.id = a.study_id
    WHERE s.id IS NULL;
    """
    orphan_count = run_sql(conn, sql_orphan)[0][0]
    ok = (orphan_count == 0)
    report['checks'].append({
        'name': 'no_orphan_artifacts',
        'ok': ok,
        'value': orphan_count,
        'expect': '0'
    })
    report['ok'] = report['ok'] and ok

    # 2) Heads point to valid artifacts
    sql_invalid_heads = """
    SELECT COUNT(*) FROM artifact_heads h
    LEFT JOIN artifacts a ON a.id = h.artifact_id
    WHERE a.id IS NULL;
    """
    invalid_heads = run_sql(conn, sql_invalid_heads)[0][0]
    ok = (invalid_heads == 0)
    report['checks'].append({
        'name': 'heads_point_to_valid_artifacts',
        'ok': ok,
        'value': invalid_heads,
        'expect': '0'
    })
    report['ok'] = report['ok'] and ok

    # 3) Embedding coverage percent: >= minimal threshold (default 0.1)
    sql_coverage = """
    SELECT COUNT(*) FILTER (WHERE embedding IS NOT NULL) * 100.0 / NULLIF((SELECT COUNT(*) FROM studies),0) as coverage_percent
    FROM study_embeddings;
    """
    res = run_sql(conn, sql_coverage)
    coverage = float(res[0][0]) if res and res[0][0] is not None else 0.0
    min_coverage = float(thresholds.get('min_embedding_coverage', 0.01))
    ok = (coverage >= min_coverage)
    report['checks'].append({
        'name': 'embedding_coverage_percent',
        'ok': ok,
        'value': coverage,
        'expect': f'>={min_coverage}'
    })
    report['ok'] = report['ok'] and ok

    # 4) Latency probe: basic query must return under threshold_ms (default 500)
    latency_threshold_ms = int(thresholds.get('latency_threshold_ms', 500))
    start = time.time()
    run_sql(conn, "SELECT s.id, a.id FROM studies s JOIN artifacts a ON a.study_id = s.id LIMIT 1;")
    elapsed_ms = (time.time() - start) * 1000.0
    ok = (elapsed_ms <= latency_threshold_ms)
    report['checks'].append({
        'name': 'latency_probe_join',
        'ok': ok,
        'value_ms': elapsed_ms,
        'expect_ms': f'<={latency_threshold_ms}'
    })
    report['ok'] = report['ok'] and ok

    return report

def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('--db-url', default=os.environ.get('DATABASE_URL', DEFAULT_DB_URL))
    parser.add_argument('--report', default='ci/inspection_report.json')
    parser.add_argument('--min-embedding-coverage', type=float, default=0.01)
    parser.add_argument('--latency-threshold-ms', type=int, default=500)
    args = parser.parse_args(argv)

    report = {'ok': False, 'errors': [], 'checks': []}

    try:
        conn = psycopg2.connect(args.db_url)
    except Exception as e:
        print("ERROR connecting to DB:", e, file=sys.stderr)
        report['errors'].append(f"db_connect_error: {e}")
        with open(args.report, 'w') as f:
            json.dump(report, f, indent=2)
        sys.exit(2)

    try:
        with closing(conn):
            setup_schema(conn)
            insert_sample_data(conn)
            checks = run_integrity_checks(conn, thresholds={
                'min_embedding_coverage': args.min_embedding_coverage,
                'latency_threshold_ms': args.latency_threshold_ms
            })
            report['checks'] = checks['checks']
            report['ok'] = checks['ok']
    except Exception as e:
        report['errors'].append(str(e))
        report['ok'] = False
    finally:
        try:
            conn.close()
        except Exception:
            pass

    # Write report
    os.makedirs(os.path.dirname(args.report), exist_ok=True)
    with open(args.report, 'w') as f:
        json.dump(report, f, indent=2)

    if not report['ok']:
        print("Home inspection FAILED", file=sys.stderr)
        print(json.dumps(report, indent=2), file=sys.stderr)
        sys.exit(1)

    print("Home inspection OK")
    print(json.dumps(report, indent=2))
    sys.exit(0)

if __name__ == '__main__':
    main(sys.argv[1:])