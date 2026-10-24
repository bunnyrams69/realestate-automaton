# Security, Privacy & Reliability Architecture

**Compliance Target:** Industry Standard Webhook Security, OWASP Top 10 API Security, Data Privacy Principles  

---

## 1. Webhook Signature Verification

Meta WhatsApp Cloud API sends an HMAC-SHA256 signature header with every incoming payload:
`X-Hub-Signature-256: sha256=<hex_digest>`

### Verification Implementation Policy
1. The raw HTTP request body bytes are captured **before** JSON parsing.
2. The expected HMAC is computed using `hmac.new(key=WHATSAPP_APP_SECRET.encode(), msg=raw_body, digestmod=hashlib.sha256)`.
3. Signatures are compared using constant-time comparison (`hmac.compare_digest`) to prevent timing side-channel attacks.
4. If the signature is missing or does not match, the endpoint immediately returns `403 Forbidden` and logs a security warning.

---

## 2. Secrets Management & Environment Hygiene

- **Strict Environment Separation:** All credentials (`ANTHROPIC_API_KEY`, `WHATSAPP_API_TOKEN`, `DATABASE_URL`, `SECRET_KEY`) reside exclusively in `.env` files or cloud platform environment secret stores (Render/Vercel).
- **Git Protection:** `.gitignore` explicitly excludes `.env`, `*.key`, `*.pem`, and credentials folders.
- **Automated Secret Redaction:** As implemented in `app.core.logging`, a custom `RedactingFormatter` sanitizes all Anthropic API keys (`sk-ant-*`), Meta tokens (`EAAB*`), Bearer headers, and password parameters before they can be written to standard out or disk logs.
- **Zero-Secret Reporting Rule:** In compliance with project guidelines, no phase reports, test outputs, or terminal messages will ever display live credentials or decrypted tokens.

---

## 3. Data Privacy & Customer Data Protection

- **Data Minimization:** Only information necessary for property discovery and sales qualification is collected (budget, property preferences, contact number). No unnecessary personal attributes are requested or stored.
- **Consent & Opt-Outs:**
  - If a customer messages `"STOP"`, `"UNSUBSCRIBE"`, or indicates they do not want to be contacted, the system sets `consent_status = 'OPTED_OUT'` and sets `state = 'OPTED_OUT'`.
  - All automated nurturing and follow-up workers strictly check `consent_status == 'OPTED_IN'` before triggering any outbound communication.
- **PII Access Control:** Administrative dashboard endpoints require authenticated JWT tokens with role-based access control (`admin`, `manager`, `agent`). Agents can only view leads assigned to their purview.

---

## 4. Reliability & Idempotency Controls

- **Webhook Deduplication:** Meta guarantees at-least-once delivery; network retries can send duplicate webhooks. Each incoming message has an authoritative `wamid` (WhatsApp Message ID). The application records this in `webhook_events(event_id)` with a database unique constraint. If a duplicate arrives, the webhook handler returns `200 OK` immediately without re-triggering AI reasoning or follow-up scheduling.
- **Fail-Safe AI Degradation:** If the Claude API encounters temporary downtime or rate-limiting (HTTP 429/500):
  - The message is placed in a pending retry queue.
  - An emergency fallback message is returned if appropriate: *"We are experiencing high enquiry volumes. An agent will connect with you shortly."*
  - The system will never crash or corrupt conversation state.
