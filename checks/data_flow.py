#!/usr/bin/env python3
"""Verify the Research -> EDA handoff and publish an audit record."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "research-irene" / "data" / "papers.csv"
EDA_REPORT = ROOT / "eda-nikos" / "reports" / "sample-study.json"
EDA_FIGURE = ROOT / "eda-nikos" / "figures" / "citations-by-year.svg"
REGISTRY = ROOT / "_registry" / "projects.json"
RUN = ROOT / "audit-thea" / "runs" / "2026-09-12-data-flow.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_initialized(path: Path) -> bool:
    result = subprocess.run(
        ["git", "-C", str(path), "rev-parse", "--is-inside-work-tree"],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode == 0 and result.stdout.strip() == "true"


def main() -> None:
    rows = list(csv.DictReader(SOURCE.open(encoding="utf-8", newline="")))
    eda = json.loads(EDA_REPORT.read_text(encoding="utf-8"))
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    expected_projects = {"research-irene", "eda-nikos", "audit-thea"}
    actual_projects = {project["id"] for project in registry["projects"]}
    source_digest = digest(SOURCE)
    checks = {
        "source_rows_present": len(rows) > 0,
        "source_digest_matches_eda": eda["input_sha256"] == source_digest,
        "eda_report_present": EDA_REPORT.is_file(),
        "eda_figure_present": EDA_FIGURE.is_file(),
        "three_projects_registered": actual_projects == expected_projects,
        "three_git_repositories_initialized": all(
            git_initialized(ROOT / project) for project in expected_projects
        ),
    }
    passed = all(checks.values())
    report = {
        "generated": datetime.now(timezone.utc).isoformat(),
        "checks": checks,
        "source": {"path": str(SOURCE.relative_to(ROOT)), "sha256": source_digest},
        "eda": {"report": str(EDA_REPORT.relative_to(ROOT)), "figure": str(EDA_FIGURE.relative_to(ROOT))},
        "result": "passed" if passed else "failed",
    }
    RUN.parent.mkdir(parents=True, exist_ok=True)
    RUN.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    status_path = ROOT / "docs" / "status.json"
    status = json.loads(status_path.read_text(encoding="utf-8"))
    status["last_byte_audit"] = report["generated"]
    status_path.write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    print(f"AUDIT {'PASSED' if passed else 'FAILED'}: {sum(checks.values())}/{len(checks)} checks")
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()