# Data quality and reconciliation rules

| Area | Rule | Action |
|---|---|---|
| Schema | Required order/customer/date/status/quantity/price columns exist | Fail source contract |
| Completeness | Required values are nonblank | Fail source contract |
| Uniqueness | `order_id` is unique within the incoming batch and target | Fail batch / dbt unique test |
| Validity | Date is `YYYY-MM-DD`; status belongs to pending/paid/shipped/cancelled | Fail source contract |
| Accuracy | Quantity is a positive integer; unit price is non-negative; amount equals quantity × price to cents | Fail source contract or reconciliation |
| Referential integrity | Every fact customer exists in the customer dimension | Fail reconciliation / dbt relationship test |
| Reconciliation | Incoming count and key set match target batch; amounts agree | Roll back batch |
| Recovery | A rejected batch leaves no partial raw/dimension/fact writes and no duplicate on retry | Pytest regression |

All bundled rows are synthetic. These rules demonstrate an approachable foundation, not a complete enterprise data-quality policy.
