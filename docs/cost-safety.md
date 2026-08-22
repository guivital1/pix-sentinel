# Cost safety

PIX Sentinel is intentionally a short-lived demonstration environment.

## Guardrails

- `EnableSimulation=false` is the deployment default.
- Kinesis uses one provisioned shard and 24-hour retention.
- The producer emits only 25 records every five minutes when explicitly enabled.
- S3 simulation objects expire after 30 days.
- Lambda uses ARM, 256 MB of memory, and a 30-second timeout.
- The consumer retries a failing batch at most twice.
- An optional tagged AWS Budget sends an alert after USD 2 against a USD 5 monthly project budget.
- The public dashboard runs on GitHub Pages, not an always-on AWS service.

## Session checklist

Before a demo:

1. Confirm the account-level AWS Budget is active.
2. Deploy with the schedule disabled.
3. Enable the simulation only for the evidence window.
4. Disable it again and confirm the EventBridge schedule state.
5. Delete the stack after capturing the Kinesis, Lambda, S3, Athena, and CloudWatch evidence.

Credits reduce the bill but do not stop resources automatically. Always verify the Billing and Cost Management dashboard after teardown.

