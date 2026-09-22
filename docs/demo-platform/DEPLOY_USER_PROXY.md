# cut-042 — SPA Deployment on User-Owned Server (Reverse-Proxy Bridge)

> **Date**: 2026-09-22
> **Owner**: cut-042 (底座泛化 + Demo API + UI 骨架)
> **Status**: Contract only — SPA assets are out of cut-042 scope (delivered separately or in cut-045)
> **Divergence from PRD §7**: SPA is hosted on user-owned infrastructure with reverse-proxy
> bridging to the ECE API container. The original PRD §7 rule "single `docker compose up`
> boots everything offline" is replaced by a two-stage deployment: ECE API + DB run in
> docker; SPA ships separately and is reverse-proxied.

## Why this deviation

The procurement-customer interview (interview-001, 2026-09-21) surfaced three constraints
that the original PRD §7 rule did not accommodate:

1. **Hard local-deployment requirement** — many Chinese enterprises forbid outbound traffic
   from the ECE container; the SPA must run on infrastructure the customer already owns
   and trusts (often on the same intranet as the data warehouse).
2. **Reverse-proxy preference** — customer IT prefers single ingress over their existing
   nginx gateway rather than a new `docker compose` runtime in the production zone.
3. **SPA decoupling** — SPA assets and API contract evolve independently; pinning them
   in one image couples release cadence.

This document captures the **contract** between the SPA host and the ECE API: the two
endpoints the SPA must call, the headers it must send, and the reverse-proxy configuration
that bridges them. The SPA itself is delivered separately; cut-042 ships the API contract
that the SPA consumes.

## SPA → ECE API contract

The SPA makes exactly two calls. Both are JSON over HTTPS.

### GET /api/v1/demo/domains

List of registered domain packs (each with its scenario manifest).

Request:
```http
GET /api/v1/demo/domains HTTP/1.1
Host: <gateway-host>
X-User-Id: <caller>
```

Response (200):
```json
{
  "domains": [
    {
      "name": "procurement",
      "label": "采购合规审查",
      "scenarios": ["default"]
    }
  ]
}
```

Forbidden in response body (PRD §5 #2 — internal field hygiene):
`decision_id`, `input_context_ref`, `package_id`, `evidence_id`, `context_request_id`,
any prefix `ctx_` / `dec_` / `ev_`.

### POST /api/v1/demo/scenarios/generate

Run the six-step loop live and return a business-named decision.

Request:
```http
POST /api/v1/demo/scenarios/generate HTTP/1.1
Host: <gateway-host>
Content-Type: application/json
X-User-Id: <caller>

{
  "domain": "procurement",
  "scenario": "default",
  "params": {
    "amount": 1500000,
    "quote_count": 2
  }
}
```

`X-User-Id` is mandatory when the caller is a known user; the API returns
`conclusion: "no_permission"` if the caller is in the scenario's `denied_users` list.

Response (200, allowed user):
```json
{
  "domain": "procurement",
  "scenario": "default",
  "conclusion": "review_required",
  "conclusion_label": "需人工复核",
  "reason": "金额 1,500,000 ≥ 1,000,000 且仅 2 家报价（需 3 家）→ 需人工复核",
  "evidence": [
    {
      "claim": "金额 1,500,000 ≥ 1,000,000",
      "observed": 1500000,
      "threshold": 1000000,
      "source_record_id": "PR-001",
      "source_system": "procurement.legacy",
      "actor": "spike-user-procurement",
      "recorded_at": "2026-09-22T08:30:00+00:00"
    }
  ],
  "state_change": {
    "before": "pending",
    "after": "review_required",
    "key": "review_status"
  },
  "actor": "spike-user-procurement",
  "denied_for": ["spike-user-unrelated"],
  "elapsed_ms": 47.2,
  "generated_at": "2026-09-22T08:30:00.123456+00:00"
}
```

Response (200, denied user):
```json
{
  "domain": "procurement",
  "scenario": "default",
  "conclusion": "no_permission",
  "conclusion_label": "无权查看",
  "reason": "denied",
  "evidence": [],
  "state_change": {
    "before": null,
    "after": "pending",
    "key": "review_status"
  },
  "actor": "spike-user-unrelated",
  "denied_for": ["spike-user-unrelated"],
  "elapsed_ms": 1.7,
  "generated_at": "2026-09-22T08:30:00.456789+00:00"
}
```

## Reverse-proxy configuration (nginx example)

The user's gateway terminates HTTPS, then reverse-proxies `/api/` to the ECE API
container. Sample nginx `server { }` block:

```nginx
server {
    listen 443 ssl;
    server_name ece-gateway.<customer-domain>;

    ssl_certificate     /etc/nginx/certs/<customer>.crt;
    ssl_certificate_key /etc/nginx/certs/<customer>.key;

    # SPA static assets served directly from nginx.
    root /var/www/ece-spa;
    index index.html;
    location / {
        try_files $uri /index.html;  # SPA history-mode fallback
    }

    # ECE API reverse-proxy.
    location /api/ {
        proxy_pass         http://<ece-api-host>:8765;
        proxy_http_version 1.1;
        proxy_set_header   Host              $host;
        proxy_set_header   X-Real-IP         $remote_addr;
        proxy_set_header   X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header   X-Forwarded-Proto $scheme;
        # X-User-Id is forwarded by the SPA unchanged.
        proxy_pass_request_headers on;
        # Long timeout: evidence assembly + persistence can take seconds.
        proxy_read_timeout 30s;
    }
}
```

The ECE API container must be reachable from the gateway host on port `8765`. If the
gateway and ECE API are on different networks, configure a private link (Tailscale,
VPC peering, wireguard, etc.) — `cut-042` does not specify the network topology, only
the contract.

## CORS preflight

If the SPA is served from a different origin than the API gateway (e.g. SPA on
`https://demo.<customer>` and API on `https://api.<customer>`), the API must answer CORS
preflight. The ECE API does NOT set CORS headers by default; the gateway must add them
or the API must be configured with `ECE_CORS_ALLOWED_ORIGINS=<comma-separated origins>`
once that env var lands (it does not exist in cut-042 — out of scope).

Until that env var exists, the deployment requirement is:

> **The SPA MUST be served from the same origin as the `/api/` prefix.** Single-origin
> deployment avoids CORS preflight entirely and matches the customer's existing nginx
> gateway pattern.

## Why not `docker compose up` for the whole stack

PRD §7 originally required "single `docker compose up` boots SPA + API + DB offline".
cut-042 deviates because:

- Customer IT policies forbid new `docker compose` runtimes in production zones.
- Single-origin deployment (nginx gateway hosts SPA + `/api/` proxy) is the customer's
  standard pattern; introducing a separate SPA container creates two ingresses.
- The SPA and the API evolve on different cadences — pinning them in one image couples
  release timing unnecessarily.

This deviation is recorded in the PRD §9 DoD rewrite (see `DEMO_PLATFORM_PRD.md`).

## Acceptance for cut-042

- ✅ The `/api/v1/demo/*` endpoints exist and conform to the contract above.
- ✅ The contract is enforceable by `tests/integration/test_demo_api_contract.py`
  (6 tests, all green) — no internal field leaks, byte-equal determinism, denied-user
  zero side effect.
- ✅ The reverse-proxy configuration is documented; the SPA host is the customer's
  responsibility.
- ⏳ The SPA assets themselves are out of cut-042 scope (delivered separately or in
  cut-045).