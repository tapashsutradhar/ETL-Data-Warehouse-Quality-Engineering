from __future__ import annotations

import json
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from uuid import uuid4

import duckdb
import pandas as pd

REQUIRED = ["order_id", "customer_id", "order_date", "status", "quantity", "unit_price"]
STATUSES = {"pending", "paid", "shipped", "cancelled"}


def read_source(path: str | Path) -> pd.DataFrame:
    frame = pd.read_csv(path, dtype="string", keep_default_na=False)
    missing = sorted(set(REQUIRED) - set(frame.columns))
    if missing:
        raise ValueError(f"CSV is missing required columns: {', '.join(missing)}")
    for column in frame.columns:
        frame[column] = frame[column].str.strip()
    for optional in ("customer_name", "email"):
        if optional not in frame:
            frame[optional] = ""
    return frame


def validate_source(frame: pd.DataFrame) -> list[str]:
    errors: list[str] = []
    for column in REQUIRED:
        bad = frame[column].eq("")
        if bad.any():
            errors.append(f"{column}: {int(bad.sum())} blank value(s)")
    duplicates = frame.loc[frame.order_id.duplicated(keep=False), "order_id"].unique().tolist()
    if duplicates:
        errors.append(f"duplicate order_id values: {duplicates}")
    dates = pd.to_datetime(frame.order_date, format="%Y-%m-%d", errors="coerce")
    if dates.isna().any():
        errors.append(f"order_date: {int(dates.isna().sum())} invalid YYYY-MM-DD value(s)")
    statuses = frame.status.str.lower()
    invalid_status = sorted(set(statuses) - STATUSES)
    if invalid_status:
        errors.append(f"unsupported status values: {invalid_status}")
    quantity = pd.to_numeric(frame.quantity, errors="coerce")
    price = pd.to_numeric(frame.unit_price, errors="coerce")
    if quantity.isna().any() or (quantity.dropna() % 1 != 0).any() or (quantity.dropna() <= 0).any():
        errors.append("quantity must be a positive whole number")
    if price.isna().any() or (price.dropna() < 0).any():
        errors.append("unit_price must be a non-negative number")
    return errors


def run_pipeline(source: str | Path, db_path: str | Path) -> dict:
    batch_id = str(uuid4())
    started = datetime.now(timezone.utc).isoformat()
    checks: list[dict[str, str]] = []
    inserted = 0
    rows = 0
    con = duckdb.connect(str(db_path))
    try:
        con.execute((Path(__file__).resolve().parents[2] / "sql" / "schema.sql").read_text(encoding="utf-8"))
        frame = read_source(source)
        rows = len(frame)
        errors = validate_source(frame)
        checks.append({"name": "source_contract", "status": "failed" if errors else "passed",
                       "detail": "; ".join(errors) if errors else "Required fields, types, keys and domains are valid"})
        con.execute("INSERT INTO batch_audit(batch_id, started_at, source_rows, status) VALUES (?, ?, ?, 'running')", [batch_id, started, rows])
        if errors:
            raise ValueError("source contract failed")

        frame["status"] = frame.status.str.lower()
        frame["order_date"] = pd.to_datetime(frame.order_date, format="%Y-%m-%d").dt.date
        frame["quantity"] = pd.to_numeric(frame.quantity).astype("int64")
        frame["unit_price"] = pd.to_numeric(frame.unit_price).round(2)
        con.register("incoming", frame)
        con.execute("BEGIN TRANSACTION")
        con.execute("INSERT INTO raw_orders SELECT ?, order_id, customer_id, customer_name, email, order_date, status, quantity, unit_price FROM incoming", [batch_id])
        before = con.execute("SELECT count(*) FROM fact_orders").fetchone()[0]
        con.execute("""INSERT INTO dim_customers
            SELECT customer_id, max(customer_name), max(lower(email)) FROM incoming
            GROUP BY customer_id ON CONFLICT(customer_id) DO UPDATE SET
            customer_name=excluded.customer_name, email=excluded.email""")
        con.execute("""INSERT INTO fact_orders
            SELECT order_id, customer_id, order_date, status, quantity, unit_price,
                   round(quantity * unit_price, 2) FROM incoming
            ON CONFLICT(order_id) DO NOTHING""")
        inserted = con.execute("SELECT count(*) FROM fact_orders").fetchone()[0] - before
        source_ids = set(frame.order_id.tolist())
        target_rows = con.execute("SELECT order_id, order_amount FROM fact_orders WHERE order_id IN (SELECT order_id FROM incoming)").fetchall()
        target_ids = {r[0] for r in target_rows}
        src_total = sum((Decimal(str(q)) * Decimal(str(p)) for q, p in zip(frame.quantity, frame.unit_price)), Decimal("0.00")).quantize(Decimal("0.01"))
        tgt_total = sum((Decimal(str(r[1])).quantize(Decimal("0.01")) for r in target_rows), Decimal("0.00"))
        integrity = con.execute("SELECT count(*) FROM fact_orders f LEFT JOIN dim_customers c USING(customer_id) WHERE c.customer_id IS NULL").fetchone()[0]
        rules = [
            ("source_target_count", len(target_ids) == rows, f"source={rows}, target keys={len(target_ids)}"),
            ("source_target_keys", target_ids == source_ids, f"missing={sorted(source_ids-target_ids)}, extra={sorted(target_ids-source_ids)}"),
            ("amount_reconciliation", src_total == tgt_total, f"source={src_total:.2f}, target={tgt_total:.2f}"),
            ("referential_integrity", integrity == 0, f"orphan facts={integrity}"),
        ]
        checks.extend({"name": n, "status": "passed" if ok else "failed", "detail": d} for n, ok, d in rules)
        if any(c["status"] == "failed" for c in checks):
            raise ValueError("warehouse quality or reconciliation check failed")
        con.execute("UPDATE batch_audit SET inserted_rows=?, status='passed', finished_at=? WHERE batch_id=?", [inserted, datetime.now(timezone.utc).isoformat(), batch_id])
        con.execute("COMMIT")
        status = "passed"
    except Exception as exc:
        try:
            con.execute("ROLLBACK")
        except duckdb.Error:
            pass
        state = con.execute("SELECT count(*) FROM batch_audit WHERE batch_id=?", [batch_id]).fetchone()[0]
        if state:
            con.execute("UPDATE batch_audit SET status='failed', error_message=?, finished_at=? WHERE batch_id=?", [str(exc), datetime.now(timezone.utc).isoformat(), batch_id])
        elif not checks:
            checks.append({"name": "pipeline_execution", "status": "failed", "detail": str(exc)})
        status = "failed"
        if not any(c["status"] == "failed" for c in checks):
            checks.append({"name": "pipeline_execution", "status": "failed", "detail": str(exc)})
    finally:
        con.close()
    return {"batch_id": batch_id, "status": status, "source_rows": rows,
            "inserted_rows": inserted if status == "passed" else 0, "checks": checks,
            "started_at": started, "finished_at": datetime.now(timezone.utc).isoformat()}


def write_reports(result: dict, report_dir: str | Path) -> None:
    folder = Path(report_dir)
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "latest.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    lines = ["# DataTrust quality run", "", f"- Status: **{result['status'].upper()}**", f"- Batch: `{result['batch_id']}`",
             f"- Source rows: {result['source_rows']}", f"- Newly inserted rows: {result['inserted_rows']}", "", "| Check | Status | Detail |", "|---|---|---|"]
    lines += [f"| {c['name']} | {c['status']} | {c['detail'].replace('|', '\\|')} |" for c in result["checks"]]
    (folder / "latest.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
