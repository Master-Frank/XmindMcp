#!/usr/bin/env python3
"""Run the assertion-based test suite; pytest's exit code is authoritative."""

import argparse
import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class ResultReport:
    def __init__(self):
        self.results = []

    def pytest_runtest_logreport(self, report):
        if report.when == "call" or (report.when == "setup" and report.outcome != "passed") or (
            report.when == "teardown" and report.failed
        ):
            self.results.append({"test": report.nodeid, "phase": report.when,
                                 "status": report.outcome, "duration": report.duration})


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--english", action="store_true", help="Compatibility option; pytest controls output")
    parser.add_argument("--save-report", action="store_true", help="Save a JSON test report")
    parser.add_argument("--report-file", help="JSON report path")
    args, pytest_args = parser.parse_known_args(argv)
    # Explicit suite paths allow focused runs; otherwise discover the project's tests.
    if not any(not arg.startswith("-") for arg in pytest_args):
        pytest_args.insert(0, str(ROOT / "tests"))
    report = ResultReport()
    exit_code = int(pytest.main(pytest_args, plugins=[report]))
    if args.save_report or args.report_file:
        destination = Path(args.report_file) if args.report_file else ROOT / "tests/test_reports/test_report.json"
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps({
            "exit_code": exit_code, "results": report.results,
            "summary": {status: sum(item["status"] == status for item in report.results)
                        for status in ("passed", "failed", "skipped")},
        }, ensure_ascii=False, indent=2), encoding="utf-8")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
