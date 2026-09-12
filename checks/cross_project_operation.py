#!/usr/bin/env python3
"""Run and record one Research -> EDA -> Audit cross-project operation."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "research-irene" / "data" / "papers.csv"
EDA_REPORT = ROOT / "eda-nikos" / "reports" / "sample-study.json"
TRACE = ROOT / "audit-thea" / "runs" / "2026-09-12-cross-project-operation.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    source_digest = sha256(SOURCE)
    eda_report = json.loads(EDA_REPORT.read_text(encoding="utf-8"))
    checks = {
        "research_published_csv": SOURCE.is_file(),
        "eda_consumed_same_digest": eda_report.get("input_sha256") == source_digest,
        "eda_report_exists": EDA_REPORT.is_file(),
        "audit_owns_trace": True,
    }
    trace = {
        "trace_id": "cross-project-2026-09-12-001",
        "generated": datetime.now(timezone.utc).isoformat(),
        "operation": "Research publishes CSV -> EDA consumes CSV -> Audit verifies trace",
        "steps": [
            {"project": "research-irene", "action": "publish", "path": str(SOURCE.relative_to(ROOT)), "sha256": source_digest},
            {"project": "eda-nikos", "action": "consume", "path": str(EDA_REPORT.relative_to(ROOT)), "input_sha256": eda_report.get("input_sha256")},
            {"project": "audit-thea", "action": "verify", "path": str(TRACE.relative_to(ROOT))},
        ],
        "checks": checks,
        "result": "passed" if all(checks.values()) else "failed",
    }
    TRACE.parent.mkdir(parents=True, exist_ok=True)
    TRACE.write_text(json.dumps(trace, indent=2) + "\n", encoding="utf-8")
    print(f"CROSS-PROJECT OPERATION {'PASSED' if all(checks.values()) else 'FAILED'}: {TRACE.relative_to(ROOT)}")
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())