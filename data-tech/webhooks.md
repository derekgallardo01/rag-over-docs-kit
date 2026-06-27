# Webhooks (sample technical docs)

## What webhooks do
A webhook delivers an HTTP POST to your endpoint whenever a subscribed event
happens in our system. Webhooks are the preferred alternative to polling for
real-time integrations. You can subscribe to event types like
`item.created`, `item.updated`, `item.deleted`, and `comment.added`.

## Registering an endpoint
Add an endpoint URL from the Developer Console under Settings → Webhooks.
Pick the events you want to receive. The URL must use HTTPS and respond
with a 2xx within 5 seconds. Slow or failing endpoints are retried with
exponential backoff for up to 24 hours; after that the delivery is
permanently dropped and you'll see it in the failed-deliveries list.

## Verifying signatures
Every delivery includes an `X-Signature` header containing an HMAC-SHA256
signature of the request body, keyed with your webhook signing secret. Verify
this signature on every request to confirm it really came from us and wasn't
tampered with in transit. The signing secret is shown once when you create
the endpoint — store it securely.

## Replays
You can replay any past delivery from the Developer Console's failed-
deliveries view — useful for debugging or recovering from a downstream outage.
Replays carry the original event timestamp; design your handler to be
idempotent (use the `event_id` for dedup) so replays don't double-process.

## Common pitfalls
The most common webhook bug is treating the delivery as authoritative without
verifying the signature; the second most common is failing to ack within 5
seconds because the handler synchronously runs heavy work. Always
queue-and-ack: respond 200 immediately, then process asynchronously.
