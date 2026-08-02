# API Overview

The Cal.diy API allows clients to access scheduling resources programmatically.

## Authentication

Requests require an API key or token.

## Base URL

```text
https://api.cal.diy/v2
```

## Example Request

```http
GET /bookings
Authorization: Bearer <token>
```

## Example Response

```json
{
  "bookings": []
}
```

Use the API to retrieve bookings, event types, and scheduling information.