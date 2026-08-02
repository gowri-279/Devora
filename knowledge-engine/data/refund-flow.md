# Refund Flow

A refund is allowed only when:

- payment status is CAPTURED
- refund window is not expired
- no refund is already in progress

Refunds are processed asynchronously.

An idempotency key is required for every refund request to prevent duplicate refunds.