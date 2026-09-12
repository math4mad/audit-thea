#!/usr/bin/env python3
"""Smoke-test the ownership and merge rules without requiring a database."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def main() -> None:
    registry = json.loads((ROOT / "_registry" / "projects.json").read_text())
    status = json.loads((ROOT / "docs" / "status.json").read_text())
    presence = {
        path.stem: json.loads(path.read_text())
        for path in (ROOT / "docs" / "presence").glob("*.json")
    }
    project_paths = [
        path
        for project in registry["projects"]
        for path in project["write_paths"]
    ]
    checks = {
        "machine_ids_are_distinct": len(presence) == len({record["machine"] for record in presence.values()}),
        "status_has_every_machine": {row["machine"] for row in status["machines"]} == set(presence),
        "project_write_paths_are_disjoint": len(project_paths) == len(set(project_paths)),
        "writer_docs_do_not_share_ids": len({"_presence/m1pro-32g", "_presence/m1-16g"}) == 2,
    }
    if not all(checks.values()):
        print(json.dumps(checks, indent=2))
        raise SystemExit(1)
    print(f"SYNC SMOKE PASSED: {len(checks)} ownership checks")


if __name__ == "__main__":
    main()