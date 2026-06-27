# API Authentication (sample technical docs)

## API keys
Every request to the API must include an API key. Create a key from the
Developer Console under Settings → API Keys. Keys are scoped to a single
workspace and can be marked read-only or read-write at creation time. Keep
keys server-side; never embed them in client-side code or commit them to
version control.

## Authentication header
Pass the API key in the `Authorization` header using the `Bearer` scheme:

```
Authorization: Bearer <your_api_key>
```

The legacy `X-API-Key` header is still accepted but deprecated; new
integrations should use the Bearer scheme.

## Rotating keys
You can rotate a key without downtime: create the new key, deploy it, then
delete the old key from the console. Deleted keys stop working immediately
— there is no grace period.

## Service accounts
For machine-to-machine access (no human user), create a service account
rather than reusing a personal account's key. Service accounts inherit
workspace permissions but have no UI access and can be audited separately.
