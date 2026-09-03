"""Refresh local groups structure from live MIA."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.fetcher import GroupStructureFetcher  # noqa: E402
from config.settings import GROUPS_FILE  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Refresh MIA faculties/courses/groups structure")
    parser.add_argument(
        "--output",
        default=str(GROUPS_FILE),
        help="Output JSON path (default: data/mia_structure.json)",
    )
    return parser.parse_args()


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    args = parse_args()
    out_path = Path(args.output).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    fetcher = GroupStructureFetcher()
    try:
        structure = fetcher.save_structure(str(out_path))
    except Exception as exc:
        logging.error("Failed to refresh MIA structure: %s", exc)
        print("\nMIA request status log:")
        for status in fetcher.request_statuses:
            base = f"- {status.method} {status.url} -> {status.status_code}"
            if status.ok:
                print(f"{base} OK")
            else:
                print(f"{base} ERROR: {status.error or 'request failed'}")
        return 1

    print(f"Saved structure to: {out_path}")
    print(f"Faculties: {len(structure)}")
    print(f"Courses: {sum(len(f['courses']) for f in structure)}")
    print(
        "Groups: "
        f"{sum(len(c['groups']) for f in structure for c in f['courses'])}"
    )
    print("\nMIA request status log:")
    for status in fetcher.request_statuses:
        base = f"- {status.method} {status.url} -> {status.status_code}"
        if status.ok:
            print(f"{base} OK")
        else:
            print(f"{base} ERROR: {status.error or 'request failed'}")

    with open(out_path, "r", encoding="utf-8") as fh:
        json.load(fh)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

