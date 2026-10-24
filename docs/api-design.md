# REST API Design Specification

**Base URL:** `/api/v1`  
**Protocol:** HTTPS  
**Data Format:** JSON (`application/json`)  
**Security:** JWT Bearer Authentication for Admin Endpoints; HMAC-SHA256 Webhook Verification for Meta  

---

## 1. Global Standards & Error Handling

All error responses adhere to a consistent JSON structure:

```json
{
  "error": "ValidationError",
  "message": "Invalid budget range specified: budget_min cannot exceed budget_max",
  "details": {
    "field": "budget_min",
    "value": 20000000
  }
}
```

### HTTP Status Code Conventions
- `200 OK`: Request succeeded with payload.
- `201 Created`: Resource successfully created.
- `202 Accepted`: Asynchronous task or webhook queued for processing.
- `400 Bad Request`: Input validation failed or malformed syntax.
- `401 Unauthorized`: Missing or invalid Bearer token.
- `403 Forbidden`: Insufficient permissions or invalid webhook signature.
- `404 Not Found`: Target entity does not exist.
- `409 Conflict`: Duplicate entry or idempotency collision.
- `500 Internal Server Error`: Unhandled server exception.

---

## 2. Core Endpoint Specifications

### 2.1 Health & Observability
- `GET /health`: Liveness probe for host/balancer. Returns `{"status": "healthy"}`.
- `GET /api/v1/system/status`: Detailed dependency readiness check (Database, WhatsApp, Claude, Google Calendar).

### 2.2 WhatsApp Webhooks
- `GET /api/v1/webhooks/whatsapp`:
  - **Query Params:** `hub.mode`, `hub.verify_token`, `hub.challenge`.
  - **Behavior:** Verifies `hub.verify_token` against `WHATSAPP_VERIFY_TOKEN`. Returns integer challenge in plaintext on match; `403 Forbidden` on mismatch.
- `POST /api/v1/webhooks/whatsapp`:
  - **Headers:** `X-Hub-Signature-256: sha256=<hmac>`
  - **Behavior:** Validates HMAC signature against `WHATSAPP_APP_SECRET`. Enqueues event for async processing. Returns `HTTP 200 {"status": "received"}` within 1 second.

### 2.3 Leads Management
- `GET /api/v1/leads`:
  - **Query Params:** `category` (`HOT` | `WARM` | `COLD`), `assigned_agent_id`, `search`, `limit`, `offset`.
  - **Response:** Paginated list of leads with contact details, scores, and qualification reasons.
- `GET /api/v1/leads/{lead_id}`:
  - **Response:** Detailed lead record, including full requirements, property matches, and visit history.
- `PATCH /api/v1/leads/{lead_id}`:
  - **Body:** `{ "lead_category": "HOT", "assigned_agent_id": "<uuid>", "notes": "..." }`
  - **Behavior:** Allows human agent override of AI classification or assignment.

### 2.4 Conversations & Human Handoff
- `GET /api/v1/conversations/{conversation_id}`:
  - **Response:** Conversation metadata and chronological message history.
- `POST /api/v1/conversations/{conversation_id}/human-takeover`:
  - **Body:** `{ "takeover": true, "reason": "High-value enterprise investor" }`
  - **Behavior:** Sets `is_human_takeover = true`, pauses automated AI responses and scheduled follow-ups.

### 2.5 Property Catalog
- `GET /api/v1/properties`:
  - **Query Params:** `property_type`, `location`, `min_price`, `max_price`, `bedrooms`, `status`.
  - **Response:** List of matching property listings.
- `POST /api/v1/properties`:
  - **Body:** Property listing attributes (name, location, price range, bedrooms, amenities, images).
  - **Security:** Restricted to admin/manager role.
- `GET /api/v1/properties/{property_id}`:
  - **Response:** Full property specs, image URLs, and walkthrough notes.

### 2.6 Site Visits & Scheduling
- `GET /api/v1/site-visits`:
  - **Query Params:** `status`, `from_date`, `to_date`, `agent_id`.
  - **Response:** List of booked and requested site visits.
- `POST /api/v1/site-visits`:
  - **Body:** `{ "lead_id": "<uuid>", "property_id": "<uuid>", "scheduled_time": "2026-10-25T14:00:00Z" }`
  - **Behavior:** Validates slot availability, persists visit, syncs with Google Calendar if enabled, and dispatches confirmation.
- `PATCH /api/v1/site-visits/{visit_id}`:
  - **Body:** `{ "status": "COMPLETED", "notes": "Customer loved the master bedroom layout." }`

### 2.7 Follow-Ups & Nurturing
- `GET /api/v1/follow-ups`:
  - **Query Params:** `status` (`PENDING` | `EXECUTED`), `due_before`.
  - **Response:** Tasks in queue with target leads and payloads.

### 2.8 Marketing Analytics & Insights
- `GET /api/v1/analytics/overview`:
  - **Response:** Total leads, conversion funnel (Enquiries -> Hot Leads -> Site Visits -> Closures).
- `GET /api/v1/analytics/insights`:
  - **Response:** Top recurring customer objections, most popular BHK configurations, frequently requested localities, and AI-recommended marketing ad copy improvements.
