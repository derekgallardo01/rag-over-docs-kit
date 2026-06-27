# Rate Limits (sample technical docs)

## Default limits
The API enforces per-key rate limits. The defaults are 60 requests per minute
and 5,000 requests per day for read endpoints, and 30 requests per minute and
2,000 requests per day for write endpoints. Limits are tracked per API key,
not per workspace.

## Headers in the response
Every response includes:

- `X-RateLimit-Limit` — the per-minute quota
- `X-RateLimit-Remaining` — remaining calls in the current window
- `X-RateLimit-Reset` — Unix timestamp when the window resets

When the limit is exceeded, the server returns HTTP `429 Too Many Requests`
with a `Retry-After` header (in seconds). Clients should back off and retry
after that interval; immediate retries will also be rejected.

## Raising your limit
Workspace administrators can request a higher rate limit by emailing
`api-support@example.com` with the use case and expected sustained throughput.
We typically respond within two business days. Limit increases are charged on
the Enterprise tier; the Team plan keeps the default limits.

## Bulk endpoints
For large data extracts, use the bulk endpoints (`/v1/bulk/*`) instead of
hitting the per-record endpoints in a loop. Bulk endpoints are counted as
one request against the rate limit regardless of how many records they return.
