# Quality Assurance & Testing Strategy

**Framework:** Pytest 8+ / Pytest-Asyncio / HTTPX Async Transport  
**Methodology:** Test-Driven Development (TDD) at Public Seams  

---

## 1. Testing Philosophy & Seam Isolation

Following the [`tdd`](file:///C:/Users/WELCOME/.gemini/config/skills/tdd/SKILL.md) and [`codebase-design`](file:///C:/Users/WELCOME/.gemini/config/skills/codebase-design/SKILL.md) disciplines:
1. **Public Seam Testing:** Tests exercise behavior through public module interfaces (e.g., calling `Orchestrator.process()` or hitting `POST /api/v1/webhooks/whatsapp`), not private internal methods.
2. **Vertical Slices:** Features are built incrementally in vertical slices: failing test first (Red) -> minimal working code (Green) -> review and clean.
3. **No Tautological Assertions:** Assertions compare actual system responses against expected domain requirements and golden fixtures, rather than mirroring internal calculations.

---

## 2. Test Architecture & Directory Layout

```
tests/
├── conftest.py              # Shared fixtures (AsyncClient, Mock Settings, In-Memory DB)
├── fixtures/                # Golden JSON payloads (WhatsApp webhooks, Claude tool calls)
├── unit/
│   ├── test_config.py       # Configuration loading, environment parsing, secret scrubbing
│   ├── test_scoring.py      # Lead qualification scoring formulas & edge cases
│   └── test_tools.py        # Pydantic tool schema parsing and validation
└── integration/
    ├── test_health.py       # Liveness, readiness, and integration status endpoints
    ├── test_webhooks.py     # HMAC validation, challenge handshakes, duplicate events
    ├── test_orchestrator.py # Conversation state transitions and tool calling workflows
    └── test_followups.py    # Background scheduler execution and opt-out cancellation
```

---

## 3. Simulated Testing Strategy for External APIs

To avoid dependence on active third-party billing, real customer communication, or unavailable sandbox credentials during early phases:
- **WhatsApp Webhook Simulation:** Golden mock fixtures based on Meta Cloud API specs are delivered to `POST /api/v1/webhooks/whatsapp` via `AsyncClient`.
- **Claude API Mocking:** Mock Anthropic responses returning structured tool use (`tool_use` blocks) to test agent state transitions deterministically.
- **Google Calendar Adapter Fakes:** An in-memory fake calendar adapter satisfies the interface during test runs, validating scheduling logic without hitting external Google APIs.
- **Zero Real-Customer Risk:** Tests run exclusively against isolated test databases and synthetic fixtures.
