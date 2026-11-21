# Agent-Friendly CLI & Feature Map Guide

## 1. CLI Contract Template

Keep the CLI thin to invoke and rich in feedback:

```text
<cli> --help                       # lists subcommand groups with 1-line descriptions
<cli> <group> --help               # lists actions + copy-pasteable examples
<cli> <group> <action> --json      # deterministic JSON on stdout; human logs on stderr
<cli> <group> <mutate> --dry-run   # shows planned effect without mutating state
```

### Standard JSON Envelope

```json
{
  "ok": true,
  "command": "flow repro-checkout",
  "duration_ms": 842,
  "artifacts": ["artifacts/checkout-desktop.png"],
  "data": { "order_id": "ord_123", "status": "paid" }
}
```

On failure (`exit != 0`):

```json
{
  "ok": false,
  "error": "AUTH_SESSION_MISSING",
  "message": "No active local test session found at .tmp/session.json",
  "next_action": "Run `scripts/verify auth login --fixture admin` then retry."
}
```

## 2. Feature Map Template

Store as `docs/feature-map.md` (or `references/features/README.md` + per-area files for large apps):

```markdown
# Feature Map

| Feature | User / Caller Entry | Key Owning Files | Verify Command | Expected Proof |
|---|---|---|---|---|
| Checkout flow | `POST /api/orders` / `/checkout` | `src/checkout/`, `src/payments/` | `scripts/verify flow checkout --json` | `ok: true`, order persisted, receipt screenshot |
| Webhook retry | `worker/webhooks.py` | `src/webhooks/retry.py` | `scripts/verify webhook replay --dry-run` | backoff schedule JSON matches contract |
```

## 3. Maintenance Hygiene

- Keep the Feature Map grounded in **real, runnable commands**—never list imaginary flags or stale routes.
- When a feature or route changes, update its Feature Map row in the same PR (or run a scheduled refresh pass that checks every entry against the codebase).
- Prefer existing project tooling (e.g., Playwright/CDP for web, simulator CLI for mobile, pytest/curl for services) wrapped cleanly rather than building a parallel test framework.
