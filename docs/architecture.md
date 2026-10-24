# System Architecture & Technical Specifications

**Project:** Real Estate AI Sales & Marketing Automation Platform  
**Document Version:** 1.0.0 (Phase 1 Baseline)  
**Primary Engine:** Python 3.12 / FastAPI / Claude API / Supabase PostgreSQL  

---

## 1. High-Level System Architecture

The platform is designed as an event-driven, modular monolith that bridges real-time messaging channels (WhatsApp Business Platform) with intelligent conversation management, lead qualification engines, CRM persistence, and scheduling coordination.

```
                   ┌─────────────────────────────────────────┐
                   │    Customer (WhatsApp / Meta Ads)       │
                   └───────────────────┬─────────────────────┘
                                       │ HTTPS Webhook (Events)
                                       ▼
                   ┌─────────────────────────────────────────┐
                   │   Cloudflare Tunnel / Edge Gateway      │
                   └───────────────────┬─────────────────────┘
                                       │ Verified POST /api/v1/webhooks/whatsapp
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│ FastAPI Application Core (Modular Monolith)                                     │
│                                                                                 │
│  ┌───────────────────────┐   ┌────────────────────────┐   ┌──────────────────┐ │
│  │ Webhook Ingestion     │──▶│ Event Deduplication    │──▶│ State Machine    │ │
│  │ & Signature Validator │   │ & Event Store          │   │ & Context Store  │ │
│  └───────────────────────┘   └────────────────────────┘   └────────┬─────────┘ │
│                                                                    │            │
│  ┌─────────────────────────────────────────────────────────────────┴─────────┐ │
│  │ AI Reasoning & Orchestration Layer (Claude API)                          │ │
│  │ - Intent Detection                                                        │ │
│  │ - Lead Qualification (Hot / Warm / Cold Scoring)                         │ │
│  │ - Property Matching Engine (Authoritative DB Search)                     │ │
│  │ - Controlled Tool Calling & Schema Validation                             │ │
│  └─────────────────────────────────┬─────────────────────────────────────────┘ │
│                                    │ Safe Tool Invocation                      │
│                                    ▼                                           │
│  ┌───────────────────────────────────────────────────────────────────────────┐ │
│  │ Domain Services & Repositories                                            │ │
│  │ - Lead Service     - Property Service    - Visit Coordinator             │ │
│  │ - Follow-Up Worker - Messaging Service   - Marketing Analytics           │ │
│  └─────────────────────────────────┬─────────────────────────────────────────┘ │
└────────────────────────────────────┼────────────────────────────────────────────┘
                                     │
           ┌─────────────────────────┴──────────────────────────┐
           ▼                                                    ▼
┌──────────────────────────────┐                      ┌──────────────────────────┐
│ Hosted Persistence           │                      │ External APIs & Workers  │
│ - Supabase / PostgreSQL      │                      │ - WhatsApp Cloud API     │
│ - Normalized Relational Data │                      │ - Google Calendar API    │
│ - Audit & Event Logs         │                      │ - Meta Marketing API     │
└──────────────────────────────┘                      └──────────────────────────┘
```

---

## 2. Layered Responsibilities & Module Seams

Following the principles of [`codebase-design`](file:///C:/Users/WELCOME/.gemini/config/skills/codebase-design/SKILL.md), each layer presents a deep, concise public interface with comprehensive internal implementation:

### 2.1 Communication & Webhook Ingestion Layer (`app.integrations.whatsapp`)
- **Seam:** `WhatsAppClient` and `WebhookVerifier`.
- **Responsibilities:**
  - Verifies HMAC-SHA256 signatures in `X-Hub-Signature-256` using the Meta App Secret.
  - Implements the `GET /webhook` verification handshake (`hub.challenge`).
  - Extracts customer phone number, name, message body, interactive replies, and media IDs.
  - Returns `HTTP 200 OK` promptly (<3 seconds) to satisfy Meta's webhook timeout SLA.
  - Hands message processing off to asynchronous workers or background execution.

### 2.2 Event Deduplication & Idempotency Layer (`app.core` & `app.db`)
- **Seam:** `IdempotencyService`.
- **Responsibilities:**
  - Meta may retry webhook events if acknowledgements are delayed.
  - Persists incoming `external_message_id` with unique constraints in `webhook_events`.
  - Discards duplicates gracefully without re-executing AI responses or booking logic.

### 2.3 Conversation State Machine & Orchestrator (`app.agents`)
- **Seam:** `ConversationOrchestrator.process_message(lead_id, message)`.
- **Responsibilities:**
  - Maintains conversation history and active state (`NEW_ENQUIRY`, `REQUIREMENTS_COLLECTION`, `QUALIFICATION`, `VISIT_INTEREST`, etc.).
  - Assembles minimal necessary context (previous preferences, qualification status, assigned agent) without polluting tokens.
  - Enforces prompt-injection defenses: customer inputs are treated as untrusted strings and never concatenated directly into instructions.

### 2.4 AI Reasoning Layer (`app.integrations.claude`)
- **Seam:** `ClaudeClient.generate_decision(context, available_tools)`.
- **Responsibilities:**
  - Uses the Anthropic Python SDK (`anthropic`) with structured tool use.
  - Exposes deterministic, tightly scoped tools (`search_properties`, `record_lead_preferences`, `check_visit_availability`, `request_human_handoff`).
  - Validates all model tool outputs through Pydantic schemas before executing application actions.

### 2.5 Domain Repositories & Data Layer (`app.repositories`)
- **Seam:** `LeadRepository`, `PropertyRepository`, `VisitRepository`, `MessageRepository`.
- **Responsibilities:**
  - Isolates SQLAlchemy ORM and PostgreSQL operations behind clean domain interfaces.
  - Manages database transactions, rollbacks, and foreign key constraints.

### 2.6 Application-Owned Automation Layer (`app.jobs`)
- **Seam:** `FollowUpScheduler` and `NurturingWorker`.
- **Responsibilities:**
  - Implemented purely in Python code (no n8n, no external workflow engine).
  - Uses database-persisted task records with execution timestamps and retry counts.
  - Scans for due follow-up tasks, verifies customer status, and cancels tasks if the customer has already replied, opted out, or been handed off to a human.

### 2.7 Frontend Layer (`frontend/` - Next.js)
- **Seam:** Secure REST API (`/api/v1/leads`, `/api/v1/conversations`, `/api/v1/analytics`).
- **Responsibilities:**
  - Next.js administrative dashboard deployed on Vercel.
  - Real-time pipeline view (Hot, Warm, Cold leads).
  - Conversation inspection, human takeover trigger, and marketing insights display.

---

## 3. Data Flows & Key Lifecycles

### 3.1 WhatsApp Inbound Enquiry to AI Response
1. Customer sends message on WhatsApp: `"Looking for a 3BHK villa near Whitefield under 1.5 Cr."`
2. Meta sends webhook payload to `POST /api/v1/webhooks/whatsapp`.
3. Application validates HMAC signature:
   - If invalid: rejects with 403 Forbidden.
   - If valid: checks `webhook_events` for duplicate `message_id`.
4. If new: stores event, retrieves or creates `Lead` by phone number, creates `Conversation` entry, and appends `Message`.
5. Orchestrator loads context and invokes Claude with `search_properties` and `update_lead_preferences` tools.
6. Claude issues tool call: `search_properties(bedrooms=3, property_type="VILLA", max_price=15000000)`.
7. Application executes database query against verified properties; returns 2 matching villas.
8. Claude crafts concise, helpful WhatsApp response with property names, price range, and asking if they want to view photos or schedule a visit.
9. Outbound message sent via Meta WhatsApp Cloud API endpoint; status updated to `SENT`.

### 3.2 Lead Qualification & Scoring Lifecycle
- Rules-based scoring weighted by explicit signals:
  - Budget defined & matches inventory: +30 points.
  - Purchase timeline < 3 months: +25 points.
  - Requested site visit: +25 points.
  - Specific location identified: +10 points.
  - Financing pre-approved / ready: +10 points.
- Scoring Tiers:
  - **HOT (>= 75):** Immediate human notification, priority site visit prompt.
  - **WARM (45 - 74):** Automated follow-ups scheduled for 24-48 hours.
  - **COLD (< 45):** Gentle nurturing, periodic educational updates, immediate opt-out compliance.

---

## 4. Architectural Boundaries & Non-Negotiable Rules
1. **Deterministic Execution:** The AI model *proposes* actions via structured tool calling; deterministic application code *validates* and *executes* them.
2. **Authoritative Property Source:** Never allow the LLM to invent property specs, pricing, or availability. All listings must come from the database.
3. **No External Workflow Platforms:** Automation is owned by the codebase (`app.jobs`), preventing external vendor lock-in or unversioned n8n pipelines.
4. **Zero-Secret Commits:** Configuration is driven entirely through environment variables with safe defaults.
