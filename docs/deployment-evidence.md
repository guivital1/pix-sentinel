# Deployment evidence

## Controlled run — 23 August 2026

The event-driven pipeline was deployed in `us-east-2` with the automatic schedule disabled. One manual producer invocation generated 25 entirely synthetic transactions.

| Check | Observed result |
| --- | --- |
| CloudFormation stack | `CREATE_COMPLETE` |
| Automatic simulation | `false` |
| Producer invocation | 25 published, 0 failed |
| SQS after consumption | 0 visible, 0 in flight |
| Lambda consumer | 5 successful micro-batches |
| S3 curated objects | 5 JSONL objects, hourly partitioned |
| Records persisted | 25 |
| Lambda error metric | 0 |
| Dead-letter messages | 0 |

## Athena validation

Summary query execution: `4107ace2-14be-4769-beec-624b7d210441`

| Transactions | Simulated volume | Alerts | Average risk |
| ---: | ---: | ---: | ---: |
| 25 | BRL 46,470.44 | 4 | 17.64 |

City query execution: `319034e8-befd-4b37-b9a6-b64694847d6e`

| City | Transactions | Alerts |
| --- | ---: | ---: |
| Belo Horizonte | 5 | 2 |
| Rio de Janeiro | 5 | 1 |
| Recife | 2 | 1 |
| Curitiba | 9 | 0 |
| São Paulo | 4 | 0 |

## Sample explainability record

```json
{
  "city": "Curitiba",
  "amount_brl": 5389.11,
  "transactions_last_hour": 7,
  "risk_score": 42,
  "risk_level": "medium",
  "reasons": ["high_amount", "high_velocity"]
}
```

The evidence contains no real customer or banking information. After validation, the Athena table and database, S3 objects, queues, Lambda functions, alarms, and CloudFormation stack were removed. The public dashboard remains a deterministic local-data demonstration.
