import argparse

from .pipeline import run_pipeline, write_reports


def main() -> int:
    parser = argparse.ArgumentParser(description="Load and quality-check retail orders")
    parser.add_argument("--source", required=True)
    parser.add_argument("--db", required=True)
    parser.add_argument("--report-dir", default="reports")
    args = parser.parse_args()
    result = run_pipeline(args.source, args.db)
    write_reports(result, args.report_dir)
    print(f"Batch {result['batch_id']}: {result['status']} ({result['inserted_rows']} inserted)")
    for check in result["checks"]:
        print(f"{check['status'].upper():6} {check['name']}: {check['detail']}")
    return 0 if result["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())

