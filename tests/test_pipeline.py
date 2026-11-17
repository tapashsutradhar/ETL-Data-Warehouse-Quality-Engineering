import json
from pathlib import Path

import duckdb
import pytest

from etl_quality.pipeline import read_source, run_pipeline, validate_source, write_reports

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def workspace(tmp_path):
    return tmp_path, ROOT / "data" / "orders.csv"


def test_first_load_reconciles_then_repeat_is_idempotent(workspace):
        work, source = workspace
        db = work / "test.duckdb"
        first = run_pipeline(source, db)
        assert first["status"] == "passed"
        assert first["source_rows"] == 8
        assert first["inserted_rows"] == 8
        second = run_pipeline(source, db)
        assert second["status"] == "passed"
        assert second["inserted_rows"] == 0
        con = duckdb.connect(str(db), read_only=True)
        assert con.execute("SELECT COUNT(*) FROM fact_orders").fetchone()[0] == 8
        assert con.execute("SELECT COUNT(*) FROM dim_customers").fetchone()[0] == 5
        con.close()

def test_invalid_batch_fails_without_partial_write_and_corrected_retry_recovers(workspace):
        work, source = workspace
        db_path = work / "test.duckdb"
        bad = ROOT / "tests" / "fixtures" / "orders_duplicate_and_blank_customer.csv"
        failed = run_pipeline(bad, db_path)
        assert failed["status"] == "failed"
        con = duckdb.connect(str(db_path), read_only=True)
        assert con.execute("SELECT COUNT(*) FROM fact_orders").fetchone()[0] == 0
        assert con.execute("SELECT COUNT(*) FROM dim_customers").fetchone()[0] == 0
        assert con.execute("SELECT status FROM batch_audit").fetchone()[0] == "failed"
        con.close()
        recovered = run_pipeline(source, db_path)
        assert recovered["status"] == "passed"
        assert recovered["inserted_rows"] == 8

def test_negative_fixtures_detect_invalid_status_and_amount(workspace):
        _, source = workspace
        frame = read_source(source)
        frame.loc[0, "status"] = "mystery"
        frame.loc[1, "unit_price"] = "-1"
        errors = " ".join(validate_source(frame))
        assert "unsupported status" in errors
        assert "non-negative" in errors

def test_reports_are_written(workspace):
        work, source = workspace
        result = run_pipeline(source, work / "test.duckdb")
        write_reports(result, work / "reports")
        assert json.loads((work / "reports" / "latest.json").read_text())["status"] == "passed"
        assert "amount_reconciliation" in (work / "reports" / "latest.md").read_text()

