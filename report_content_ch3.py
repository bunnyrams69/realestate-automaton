from report_builder_utils import add_chapter_heading, add_h1, add_h2, add_h3, add_p, add_bullet, add_table
from docx.enum.text import WD_ALIGN_PARAGRAPH

def build_chapter_3(doc):
    add_chapter_heading(doc, 3, "REQUIREMENTS ANALYSIS", page_break=True)
    
    # 3.1 Feasibility Studies and Risk Analysis of the Project
    add_h1(doc, "3.1", "Feasibility Studies and Risk Analysis of the Project")
    add_p(doc,
        "Prior to initiating system implementation, rigorous feasibility studies and comprehensive risk analyses were conducted "
        "to validate the technical viability, economic soundness, and operational practicality of the Real Estate AI Sales and "
        "Marketing Automation Agent. Deploying an autonomous AI agent in a high-stakes commercial environment where transactions "
        "involve substantial financial commitments requires an exhaustive evaluation of system dependencies, operational hazards, "
        "and data integrity constraints."
    )
    
    # 3.1.1 Feasibility
    add_h2(doc, "3.1.1", "Feasibility Analysis")
    
    # 3.1.1.1 Technical Feasibility
    add_h3(doc, "3.1.1.1", "Technical Feasibility")
    add_p(doc,
        "Technical feasibility evaluates whether the proposed architecture can be successfully engineered using mature technologies. "
        "The technical stack is anchored upon Python 3.11 and the FastAPI asynchronous framework, which provides native ASGI concurrency "
        "capable of processing thousands of non-blocking I/O requests per second. The conversational intelligence layer leverages the Claude API "
        "(utilizing Claude 3.5 Sonnet for complex contextual qualification and Claude 3.5 Haiku for rapid conversational turns), delivering "
        "exceptional instruction following and structured JSON schema enforcement via Pydantic. Customer communication interfaces directly "
        "with Meta's official WhatsApp Business Platform Cloud API via webhooks. Data persistence is managed by PostgreSQL hosted on Supabase, "
        "offering robust relational consistency and Row-Level Security (RLS). Scheduling synchronizes with the Google Calendar v3 API via "
        "OAuth2 authentication. The technical feasibility of this integrated stack is exceptionally high."
    )

    # 3.1.1.2 Economic Feasibility
    add_h3(doc, "3.1.1.2", "Economic Feasibility")
    add_p(doc,
        "Economic feasibility examines the cost-benefit calculus, capital requirements, and ongoing operational expenditure. Traditional "
        "brokerage models incur heavy personnel costs, with sales teams commanding base salaries from ₹40,000 to ₹1,50,000 per month per "
        "representative, while still failing to provide 24/7 responsiveness. Commercial workflow automation platforms such as n8n Enterprise "
        "impose steep recurring monthly subscription fees. In contrast, the proposed solution implements all workflow automation logic "
        "directly in modular Python code, entirely eliminating third-party automation licensing fees. Infrastructure hosting leverages modern "
        "serverless tiers (Vercel, Render, and Supabase) that provide generous free tiers accommodating development and early-stage commercial "
        "pilots at ₹0.00 infrastructure cost. Production operating overheads are limited strictly to metered API consumption, yielding an "
        "ultra-low operating cost structure."
    )

    # 3.1.1.3 Operational Feasibility
    add_h3(doc, "3.1.1.3", "Operational Feasibility")
    add_p(doc,
        "Operational feasibility assesses organizational adoption and usability. From the customer perspective, operational friction is "
        "completely eliminated: prospective buyers are not required to download new mobile applications, register accounts, or navigate complex "
        "web forms. The entire interaction occurs seamlessly within WhatsApp—an application already present on the user's mobile device. For "
        "real estate sales agents and marketing executives, qualified leads are instantly pushed to CRM tables with clear Hot/Warm/Cold classifications, "
        "while scheduled site visits appear automatically on agents' Google Calendars. The Next.js administrative dashboard provides intuitive visual "
        "controls requiring zero specialized technical training, ensuring seamless organizational adoption."
    )

    # 3.1.2 Risk Assessment and Mitigation Strategies
    add_h2(doc, "3.1.2", "Risk Assessment and Mitigation Strategies")
    add_p(doc,
        "Deploying an automated conversational agent capable of engaging prospective property buyers and scheduling appointments entails "
        "operational risks that must be proactively mitigated. Table 3.1 delineates the identified risk events, their estimated probability "
        "and business impact, and the engineering mitigation strategies implemented in the system architecture."
    )
    
    headers_3_1 = ["Identified Risk Event", "Probability", "Impact", "Technical Mitigation Strategy"]
    rows_3_1 = [
        [
            "WhatsApp API Rate Limiting\n& Account Suspension",
            "Moderate",
            "High",
            "Adhere strictly to official WhatsApp Cloud API guidelines; implement exponential backoff retry queues and maintain verified Meta Business Manager credentials."
        ],
        [
            "Generative Hallucination\non Pricing / Amenities",
            "Moderate",
            "Critical",
            "Enforce strict system prompt boundaries forbidding the LLM from inventing facts; inject vetted PostgreSQL property inventory into prompt context via schema-enforced Pydantic contracts."
        ],
        [
            "Calendar Double-Booking\n& Schedule Collisions",
            "Low",
            "High",
            "Execute atomic time-slot availability checks via Google Calendar API immediately prior to booking confirmation; establish buffer periods between site visits."
        ],
        [
            "Data Privacy & PII\nLeakage (Customer Data)",
            "Low",
            "Critical",
            "Enforce TLS 1.3 encryption in transit; implement PostgreSQL Row-Level Security (RLS); sanitize and redact sensitive PII before storing telemetry logs."
        ],
        [
            "Webhook Network Latency\n& Partitioning Downtime",
            "Low",
            "Moderate",
            "Deploy FastAPI behind high-availability reverse proxies with asynchronous worker queues; return instantaneous HTTP 200 acknowledgments to Meta webhooks."
        ],
        [
            "Prompt Injection &\nAdversarial Attacks",
            "Moderate",
            "Moderate",
            "Implement input sanitization regex filters; enforce separation between untrusted user input and core system instructions; cap maximum token outputs."
        ]
    ]
    add_table(doc, "Table 3.1: Risk Probability, Impact Matrix, and Technical Mitigation Strategies", 
              headers_3_1, rows_3_1, col_widths=[1.5, 0.9, 0.9, 3.2])

    # 3.2 Software Requirements Specification (SRS) Document
    add_h1(doc, "3.2", "Software Requirements Specification (SRS) Document")
    add_p(doc,
        "The Software Requirements Specification (SRS) formalizes the operational environment, technical stack dependencies, and detailed "
        "functional and non-functional specifications governing the platform's behavior."
    )
    
    # 3.2.1 Hardware and Software Environment Requirements
    add_h2(doc, "3.2.1", "Hardware and Software Environment Requirements")
    add_p(doc,
        "The application is engineered with a modern cloud-native, lightweight microservices paradigm, ensuring zero reliance on heavy local "
        "workstation hardware or dedicated GPU server clusters. Table 3.2 specifies the minimum hardware deployment parameters, while Table 3.3 "
        "details the software technology stack and dependencies."
    )
    
    headers_3_2 = ["Component Category", "Minimum Requirement", "Production Recommended"]
    rows_3_2 = [
        ["Client Mobile Device", "Android 8.0+ / iOS 12.0+ with WhatsApp", "Modern smartphone with 4G/5G/Wi-Fi connection"],
        ["Application Backend Host", "1 vCPU, 512 MB RAM (Serverless container)", "2 vCPU, 2 GB RAM (Render / AWS ECS container)"],
        ["Database Server Host", "Shared vCPU, 500 MB RAM (Supabase Free)", "2 vCPU, 4 GB RAM dedicated PostgreSQL instance"],
        ["Admin Dashboard Client", "Modern Web Browser (Chrome 90+, Safari 14+)", "Desktop / Laptop Display 1920x1080 resolution"],
        ["Developer Workstation", "Dual-Core x86_64, 4 GB RAM, 10 GB disk space", "Quad-Core CPU, 16 GB RAM, 256 GB SSD"]
    ]
    add_table(doc, "Table 3.2: Hardware Specification Requirements for Deployment", 
              headers_3_2, rows_3_2, col_widths=[1.5, 2.5, 2.5])

    headers_3_3 = ["Layer / Subsystem", "Technology Selected", "Operational Functionality"]
    rows_3_3 = [
        ["Programming Language", "Python 3.11+", "Core backend business logic, AI orchestration, and API services"],
        ["Backend API Framework", "FastAPI (ASGI / Uvicorn)", "High-performance asynchronous webhook routing and REST endpoints"],
        ["Conversational AI Engine", "Anthropic Claude 3.5 Sonnet / Haiku", "Multi-turn natural language dialogue, semantic parsing, and variable extraction"],
        ["Messaging Infrastructure", "Meta WhatsApp Business Cloud API", "Official enterprise messaging, incoming webhook processing, and message delivery"],
        ["Relational Database", "PostgreSQL 15 (Supabase)", "Persistent storage for properties, leads, conversations, and marketing telemetry"],
        ["Calendar Scheduling", "Google Calendar v3 REST API", "Agent availability lookup, appointment conflict detection, and event generation"],
        ["Admin Web Dashboard", "Next.js 14, React, Tailwind CSS", "Executive analytics portal, pipeline tracking, and property inventory manager"],
        ["Hosting & Deployment", "Render (Backend), Vercel (Frontend)", "Automated CI/CD git-triggered containerized cloud deployment"]
    ]
    add_table(doc, "Table 3.3: Software Technology Stack and Dependency Specifications", 
              headers_3_3, rows_3_3, col_widths=[1.5, 2.2, 2.8])

    # 3.2.2 Functional and Non-Functional Specifications
    add_h2(doc, "3.2.2", "Functional and Non-Functional Specifications")
    add_p(doc,
        "The operational behavior and quality attributes of the system are governed by rigorous functional and non-functional requirements:"
    )
    add_p(doc, "Functional Requirements (FR):", bold=True)
    add_bullet(doc,
        "FR1 (WhatsApp Ingestion & Verification): Authenticated HTTPS webhook endpoint conforming to Meta's verification challenge protocol, "
        "verifying SHA-256 HMAC payload signatures and parsing incoming text, button replies, and media attachments.",
        bold_prefix="1. "
    )
    add_bullet(doc,
        "FR2 (Natural Dialogue & Entity Extraction): Engage prospective buyers in natural, context-aware conversation via the Claude API, "
        "maintaining multi-turn context and extracting structured variables (budget, unit type, locality, timeline) into validated Pydantic models.",
        bold_prefix="2. "
    )
    add_bullet(doc,
        "FR3 (Algorithmic Lead Qualification): Evaluate extracted variables against a deterministic qualification rubric, computing an objective "
        "lead score (0-100) and classifying the prospect into Hot, Warm, or Cold sales pipeline categories.",
        bold_prefix="3. "
    )
    add_bullet(doc,
        "FR4 (Dynamic Property Inventory Matching): Query active PostgreSQL property listings based on qualified buyer preferences, generating "
        "formatted WhatsApp message cards featuring project name, location, pricing, and visual floorplan assets.",
        bold_prefix="4. "
    )
    add_bullet(doc,
        "FR5 (Automated Site Visit Scheduling): Interface with the Google Calendar API to query real-time sales agent availability, propose available "
        "60-minute site visit windows to the user, and confirm bookings upon customer agreement.",
        bold_prefix="5. "
    )
    add_bullet(doc,
        "FR6 (Executive Marketing Analytics Dashboard): Aggregate conversational telemetry, objection reasons, lead quality distributions, and "
        "Meta ad campaign identifiers, rendering interactive visualizations on the Next.js administrative dashboard.",
        bold_prefix="6. "
    )

    add_p(doc, "Non-Functional Requirements (NFR):", bold=True)
    add_bullet(doc,
        "NFR1 (Response Latency): The end-to-end processing pipeline—from receipt of a WhatsApp webhook to the delivery of an AI-generated reply—shall "
        "complete within an average response latency of less than 2.0 seconds.",
        bold_prefix="1. "
    )
    add_bullet(doc,
        "NFR2 (System Scalability & Concurrency): The backend architecture shall utilize non-blocking asynchronous event loops capable of concurrently "
        "processing over 100 simultaneous user dialogue sessions without latency degradation.",
        bold_prefix="2. "
    )
    add_bullet(doc,
        "NFR3 (Information Security & Privacy): All communication channels shall enforce TLS 1.3 encryption. Customer PII and conversation records "
        "shall be persisted within PostgreSQL protected by Row-Level Security and encrypted database storage.",
        bold_prefix="3. "
    )
    add_bullet(doc,
        "NFR4 (Availability & Reliability): The platform shall achieve 99.9% operational uptime, incorporating idempotency checking on all webhook "
        "event handlers to prevent duplicate message processing or redundant calendar bookings.",
        bold_prefix="4. "
    )
    add_bullet(doc,
        "NFR5 (Modularity & Maintainability): The codebase shall follow clean architectural separation between ingestion, intelligence, business logic, "
        "and persistence layers, ensuring high testability and modular extensibility.",
        bold_prefix="5. "
    )

    print("Calibrated Chapter 3 built successfully!")
