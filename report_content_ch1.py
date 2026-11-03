from report_builder_utils import add_chapter_heading, add_h1, add_p, add_bullet

def build_chapter_1(doc):
    # Chapter 1 starts on Page 1 of Section 4 (no page break needed as it is section start)
    add_chapter_heading(doc, 1, "INTRODUCTION", page_break=False)
    
    # 1.1 Background and Motivation
    add_h1(doc, "1.1", "Background and Motivation")
    add_p(doc, 
        "The contemporary real estate sector is undergoing a profound digital transformation catalyzed by ubiquitous smartphone "
        "connectivity, shifting homebuyer search behavior, and modern performance marketing ecosystems. Prospective property "
        "buyers rarely begin their purchasing journey through physical brokerage visits. Instead, customer discovery is predominantly "
        "driven across high-traffic digital advertising channels, particularly Meta platforms encompassing Facebook and Instagram. "
        "Real estate developers and brokerage firms invest substantial capital into targeted ad campaigns featuring high-resolution "
        "architectural renderings, interactive walkthroughs, and promotional pricing. Prospective buyers are prompted to initiate "
        "direct inquiries by clicking 'Send Message' buttons that route traffic directly into WhatsApp—the world's most pervasive messaging application."
    )
    add_p(doc,
        "WhatsApp provides a frictionless, instantaneous communication channel characterized by open rates exceeding 90%. However, "
        "while digital advertising generates high volumes of prospective inquiries, conventional real estate sales operations suffer from "
        "severe structural bottlenecks at the point of customer engagement. Inquiries are traditionally routed to manual human sales teams "
        "or call center agents who cannot maintain round-the-clock responsiveness. Representatives are frequently occupied conducting physical "
        "site tours, attending client meetings, or navigating peak inquiry surges during evenings and weekends—precisely when prospective "
        "homebuyers conduct personal property research."
    )
    add_p(doc,
        "Empirical investigations in commercial sales conversion velocity demonstrate that initial lead response latency directly dictates "
        "deal closure probability. When an interested buyer inquires about a property, they expect instantaneous details regarding unit "
        "configurations, micro-market location, and pricing. If an organization introduces a response lag exceeding 30 to 60 minutes, the buyer's "
        "engagement rapidly decays, prompting them to contact competing developers. Statistical studies indicate that inquiries engaged within "
        "5 minutes demonstrate a 21-fold higher likelihood of entering formal sales qualification compared to inquiries answered after 30 minutes. "
        "Furthermore, sales representatives suffer from cognitive fatigue, inconsistently qualifying buyer criteria and failing to maintain "
        "diligent follow-up cadences."
    )
    add_p(doc,
        "To systematically eliminate these operational inefficiencies, this project develops the Real Estate AI Sales and Marketing Automation "
        "Agent. By architecting an enterprise-grade autonomous system integrating FastAPI, Anthropic Claude foundation models, the official "
        "WhatsApp Business Platform Cloud API, Supabase PostgreSQL, and Google Calendar, the platform autonomously engages prospective buyers, "
        "qualifies purchasing intent, recommends matching properties, schedules physical site visits, and surfaces actionable marketing analytics."
    )

    # 1.2 Problem Statement
    add_h1(doc, "1.2", "Problem Statement")
    add_p(doc,
        "The fundamental problem addressed in this work is the structural disconnect between high-velocity digital advertising and archaic, "
        "manual sales lead management workflows in the real estate sector. This manifests across four critical operational failure modes:"
    )
    add_bullet(doc,
        "Severe Response Latency and Lead Decay: Human response times routinely range from 30 minutes to over 4 hours during business days, "
        "escalating to complete unavailability during nighttime hours. During this latency window, prospective buyers disengage, seek alternatives, "
        "or conclude that the developer lacks professional customer support.",
        bold_prefix="1. "
    )
    add_bullet(doc,
        "Unstructured Buyer Data and Inconsistent Qualification: Prospective buyers communicate through ambiguous natural language across "
        "WhatsApp. Human agents rarely apply standardized qualification scoring, resulting in misallocated sales effort where low-intent casual "
        "browsers receive the same attention as ready-to-transact buyers.",
        bold_prefix="2. "
    )
    add_bullet(doc,
        "Manual Inventory Matching and Scheduling Friction: Sales agents must manually cross-reference buyer criteria against fragmented "
        "spreadsheets and PDF brochures. Coordinating site visits requires multiple back-and-forth messages, creating friction that leads to drop-offs.",
        bold_prefix="3. "
    )
    add_bullet(doc,
        "Disconnected Marketing Intelligence: Marketing teams managing Meta ad campaigns lack qualitative visibility into why inquiries reject "
        "properties during frontline sales conversations, leading to wasteful advertising spend on unviable target audiences.",
        bold_prefix="4. "
    )

    # 1.3 Project Objectives
    add_h1(doc, "1.3", "Project Objectives")
    add_p(doc,
        "The primary technical objectives of this project encompass the design, implementation, and empirical verification of an autonomous "
        "conversational real estate sales platform:"
    )
    add_bullet(doc,
        "Real-Time Conversational Ingestion: Establish a secure webhook ingestion pipeline built upon FastAPI and the official WhatsApp Business "
        "Cloud API to receive and process customer inquiries with sub-second acknowledgment.",
        bold_prefix="1. "
    )
    add_bullet(doc,
        "Context-Aware Semantic Dialogue Engine: Develop an intelligent conversational pipeline utilizing Claude Foundation Models with strict "
        "domain system prompts to conduct warm, natural sales conversations and extract structured buyer schemas.",
        bold_prefix="2. "
    )
    add_bullet(doc,
        "Multi-Criteria Algorithmic Lead Scoring: Engineer a deterministic qualification state machine that evaluates extracted criteria to "
        "categorize prospects into objective Hot, Warm, and Cold sales tiers.",
        bold_prefix="3. "
    )
    add_bullet(doc,
        "Dynamic Real-Time Inventory Recommendation: Implement a database-driven property matching service that filters active listings and "
        "generates visual property cards with floorplans directly inside WhatsApp.",
        bold_prefix="4. "
    )
    add_bullet(doc,
        "Automated Calendar Coordination: Integrate the Google Calendar API to query sales agent availability, propose open time slots, and "
        "autonomously confirm physical site visits.",
        bold_prefix="5. "
    )
    add_bullet(doc,
        "Executive Marketing Analytics Dashboard: Construct an administrative portal with Next.js and Supabase PostgreSQL to correlate lead "
        "conversion data and customer objections with specific Meta ad campaigns.",
        bold_prefix="6. "
    )

    # 1.4 Scope of the Project
    add_h1(doc, "1.4", "Scope of the Project")
    add_p(doc,
        "The functional scope of the platform spans the complete lead engagement lifecycle, operating within well-defined technical boundaries:"
    )
    add_bullet(doc,
        "Target Real Estate Verticals: Optimized for residential property developments, including apartments, gated villas, and plotted layouts.",
        bold_prefix="• "
    )
    add_bullet(doc,
        "Supported Interaction Medium: Primary customer interaction occurs via WhatsApp text and multimedia messaging, supported by a Next.js "
        "administrative dashboard for real estate personnel.",
        bold_prefix="• "
    )
    add_bullet(doc,
        "Explicit Out-of-Scope Boundaries: The system does not process financial escrow payments, execute legal deed transfers, or conduct automated "
        "title registrations; all binding legal closures remain with human representatives.",
        bold_prefix="• "
    )
    add_bullet(doc,
        "Infrastructure Architecture: Engineered with cloud-native serverless principles (Render, Supabase, Vercel) ensuring zero local disk bloat "
        "and ultra-low operational overheads.",
        bold_prefix="• "
    )

    print("Calibrated Chapter 1 built successfully!")
