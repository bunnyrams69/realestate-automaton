# Project Roadmap & MVP Phase Boundaries

---

## 1. Ten-Phase Delivery Roadmap

| Phase | Title | Scope Summary | Target State |
|:---:|---|---|:---:|
| **Phase 1** | **Discovery & Foundation** | Repo setup, skills selection, architecture, data schemas, security rules, test harness. | **COMPLETE** |
| **Phase 2** | **Database & Lead Management** | SQLAlchemy models, Alembic migrations, CRUD repositories, lead management REST APIs. | Pending Review |
| **Phase 3** | **WhatsApp Integration** | Webhook verification, HMAC validation, event deduplication, inbound/outbound client. | Scheduled |
| **Phase 4** | **AI Agent & Lead Qualification** | Claude API integration, state machine, lead qualification (Hot/Warm/Cold), property search tool. | Scheduled |
| **Phase 5** | **Follow-ups & Nurturing** | Application-owned scheduler, re-engagement rules, duplicate suppression, opt-out logic. | Scheduled |
| **Phase 6** | **Site Visit Booking** | Google Calendar integration, slot availability checking, booking persistence, reminders. | Scheduled |
| **Phase 7** | **Property Gallery & Media** | WhatsApp image payloads, brochure sending, optional speech-to-text integration. | Scheduled |
| **Phase 8** | **Marketing Intelligence & Meta** | Enquiry trend clustering, recurring objection analysis, read-only Meta Marketing insights. | Scheduled |
| **Phase 9** | **Admin Dashboard & Analytics** | Next.js frontend, pipeline review, lead filtering, conversation inspector, human takeover. | Scheduled |
| **Phase 10** | **E2E Testing & Deployment** | End-to-end integration tests, Render/Vercel configuration, production runbooks. | Scheduled |

---

## 2. One-Day MVP Scope Boundaries

To ensure reliable, testable execution within the initial release, priorities are strictly disciplined:

### In Scope (MVP Core):
- Complete WhatsApp customer enquiry reception and signature verification.
- Autonomous conversation handling via Claude API with structured property matching.
- Deterministic lead qualification into HOT, WARM, and COLD with explainable reasoning.
- Real property database records (no hallucinated properties or prices).
- Application-owned scheduled follow-up triggers and automatic cancellation on reply.
- Site visit request coordination and persistence.
- Basic operational health and lead retrieval APIs.

### Excluded / Deferred from Initial One-Day MVP:
- Local Docker Desktop containers (hosted cloud services used instead).
- External workflow platforms (n8n, Zapier) — all logic strictly code-based.
- Voice-note audio synthesis (ElevenLabs) and speech-to-text models.
- Automated advertising campaign budget adjustment or automated ad publishing.
- Multi-tenant enterprise billing or multi-agency isolation.
