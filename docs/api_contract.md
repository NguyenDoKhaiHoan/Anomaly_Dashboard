# API chính

## Auth
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `GET /api/v1/auth/me`

## Streams
- `GET /api/v1/streams/sessions`
- `POST /api/v1/streams/sessions`
- `POST /api/v1/streams/sessions/{id}/start`
- `POST /api/v1/streams/sessions/{id}/stop`
- `GET /api/v1/streams/sessions/{id}/runtime`
- `GET /api/v1/streams/sessions/{id}/events?token=...`
- `WS  /api/v1/streams/ws/{id}`

## History
- `GET /api/v1/history/events`

## Alerts
- `GET /api/v1/alerts/rules`
- `POST /api/v1/alerts/rules`
- `GET /api/v1/alerts/notifications`

## Admin
- `GET /api/v1/admin/users`
- `PATCH /api/v1/admin/users/{id}`
- `GET /api/v1/admin/overview`

## Catalog
- `GET /api/v1/models`
- `GET /api/v1/datasets`
- `GET /api/v1/health`
