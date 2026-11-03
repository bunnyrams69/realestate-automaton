import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os

os.makedirs("figures", exist_ok=True)

# Set global matplotlib parameters for clean academic style
plt.rcParams['font.sans-serif'] = 'Arial'
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['figure.dpi'] = 300

def create_system_architecture():
    fig, ax = plt.subplots(figsize=(10, 7.5))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    # Title box / Header
    ax.text(50, 96, "SYSTEM ARCHITECTURE: REAL ESTATE AI AUTOMATION PLATFORM", 
            ha='center', va='center', fontsize=12, fontweight='bold', color='#1A365D')

    # Color Palette (Subtle Academic Blue / Slate / Teal)
    c_client = '#EBF8FF'
    c_edge = '#EDF2F7'
    c_core = '#E6FFFA'
    c_ai = '#FEFCBF'
    c_db = '#FAF5FF'
    c_ext = '#FFF5F5'
    border_color = '#2B6CB0'

    # Box Helper
    def draw_box(x, y, w, h, title, subtitle="", bg='#FFFFFF', border='#4A5568'):
        rect = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=1,rounding_size=2",
                                      facecolor=bg, edgecolor=border, linewidth=1.5)
        ax.add_patch(rect)
        if subtitle:
            ax.text(x + w/2, y + h*0.62, title, ha='center', va='center', fontsize=9.5, fontweight='bold', color='#2D3748')
            ax.text(x + w/2, y + h*0.28, subtitle, ha='center', va='center', fontsize=8, color='#4A5568')
        else:
            ax.text(x + w/2, y + h/2, title, ha='center', va='center', fontsize=9, fontweight='bold', color='#2D3748')

    # 1. Client Layer (Top)
    draw_box(20, 84, 60, 7, "CUSTOMER COMMUNICATION LAYER", "WhatsApp Messaging Client & Meta Ads Lead Ingestion", c_client, '#3182CE')

    # Arrow Down
    ax.annotate('', xy=(50, 76), xytext=(50, 84),
                arrowprops=dict(facecolor='#4A5568', edgecolor='#4A5568', width=1.5, headwidth=6))
    ax.text(52, 80, "HTTPS Webhook Events", fontsize=7.5, color='#4A5568', va='center')

    # 2. Ingestion & Security Boundary
    draw_box(15, 68, 70, 7.5, "WEBHOOK INGESTION & SECURITY GATEWAY", "HMAC-SHA256 Verification | Idempotency Deduplication | Rate Limiter", c_edge, '#4A5568')

    # Arrow Down
    ax.annotate('', xy=(50, 60), xytext=(50, 68),
                arrowprops=dict(facecolor='#4A5568', edgecolor='#4A5568', width=1.5, headwidth=6))

    # 3. Application Core Monolith (Big Box)
    core_box = patches.FancyBboxPatch((8, 22), 84, 38, boxstyle="round,pad=1.5,rounding_size=3",
                                     facecolor='#F7FAFC', edgecolor='#2B6CB0', linewidth=1.8, linestyle='--')
    ax.add_patch(core_box)
    ax.text(50, 57.5, "FASTAPI BACKEND APPLICATION CORE (MODULAR MONOLITH)", ha='center', va='center',
            fontsize=10.5, fontweight='bold', color='#2B6CB0')

    # Sub-components inside Application Core
    # Left column: Orchestrator & AI
    draw_box(12, 44, 36, 10, "CONVERSATION ORCHESTRATOR", "State Machine (11 Dialogue States)\nContext Assembly & Guardrails", c_core, '#319795')
    draw_box(12, 31, 36, 10, "CLAUDE 3.7 AI REASONING ENGINE", "Intent Detection | Schema Validation\nDeterministic Tool Execution Calling", c_ai, '#D69E2E')

    # Arrow between orchestrator and claude
    ax.annotate('', xy=(30, 41), xytext=(30, 44),
                arrowprops=dict(arrowstyle='<->', color='#D69E2E', lw=1.5))

    # Right column: Domain Services & Jobs
    draw_box(52, 45, 36, 8, "LEAD QUALIFICATION & SCORING", "Weighted Scoring (HOT / WARM / COLD)\nExplainable Qualification Reason Ledger", '#FFFFFF', '#4A5568')
    draw_box(52, 35, 36, 8, "PROPERTY MATCHING ENGINE", "Catalog Query Filter | Multi-Param Filter\nZero-Hallucination Inventory Validator", '#FFFFFF', '#4A5568')
    draw_box(52, 25, 36, 8, "APPLICATION-OWNED AUTOMATION", "Scheduled Follow-Up Engine | Opt-Out Filter\nSite Visit Coordinator & Reminder Worker", '#FFFFFF', '#4A5568')

    # Arrows between Left and Right in Core
    ax.annotate('', xy=(52, 49), xytext=(48, 49),
                arrowprops=dict(facecolor='#4A5568', edgecolor='#4A5568', width=1, headwidth=5))
    ax.annotate('', xy=(52, 39), xytext=(48, 39),
                arrowprops=dict(facecolor='#4A5568', edgecolor='#4A5568', width=1, headwidth=5))
    ax.annotate('', xy=(52, 29), xytext=(48, 36),
                arrowprops=dict(facecolor='#4A5568', edgecolor='#4A5568', width=1, headwidth=5))

    # 4. Storage & Persistence Layer (Bottom Left)
    draw_box(8, 4, 38, 12, "SUPABASE / POSTGRESQL DATABASE", "Leads | Conversations | Messages | Properties\nFollow-Up Tasks | Site Visits | Marketing Insights", c_db, '#805AD5')

    # 5. Admin Dashboard (Bottom Right)
    draw_box(54, 4, 38, 12, "NEXT.JS ADMINISTRATIVE DASHBOARD", "Lead Pipeline View | Conversation Review\nHuman Takeover Gate | Marketing Analytics", '#EBF8FF', '#3182CE')

    # Connecting Core to DB and Dashboard
    ax.annotate('', xy=(27, 16), xytext=(27, 22),
                arrowprops=dict(facecolor='#805AD5', edgecolor='#805AD5', width=1.5, headwidth=6))
    ax.text(28, 19, "Async ORM / SQL", fontsize=7.5, color='#805AD5', va='center')

    ax.annotate('', xy=(73, 16), xytext=(73, 22),
                arrowprops=dict(facecolor='#3182CE', edgecolor='#3182CE', width=1.5, headwidth=6))
    ax.text(74, 19, "REST API v1 / JWT", fontsize=7.5, color='#3182CE', va='center')

    plt.tight_layout()
    fig.savefig("figures/fig_4_1_system_architecture.png", dpi=300, bbox_inches='tight')
    plt.close()
    print("Saved fig_4_1_system_architecture.png")

def create_automation_workflow():
    fig, ax = plt.subplots(figsize=(10, 6.5))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    ax.text(50, 96, "END-TO-END AUTOMATION & DATA FLOW WORKFLOW", 
            ha='center', va='center', fontsize=12, fontweight='bold', color='#1A365D')

    steps = [
        ("1. AD DISCOVERY", "Customer clicks Meta ad;\nsends WhatsApp inquiry", 10, 72, '#EBF8FF', '#3182CE'),
        ("2. WEBHOOK GATEWAY", "HMAC verified, event logged;\nduplicate check passed", 35, 72, '#EDF2F7', '#4A5568'),
        ("3. CONTEXT RETRIEVAL", "Retrieve lead history, prefs,\nand active state from DB", 60, 72, '#FAF5FF', '#805AD5'),
        ("4. AI REASONING", "Claude detects intent;\nextracts budget & location", 85, 72, '#FEFCBF', '#D69E2E'),
        
        ("8. DASHBOARD SYNC", "Pipeline updated; metrics\nvisible to sales team", 85, 25, '#EBF8FF', '#3182CE'),
        ("7. SITE VISIT / REMINDER", "Slot confirmed in Calendar;\nvisit task persisted", 60, 25, '#E6FFFA', '#319795'),
        ("6. NURTURING FOLLOW-UP", "Background scheduler sets\nfollow-up timer (24h-48h)", 35, 25, '#FFF5F5', '#E53E3E'),
        ("5. PROPERTY MATCH", "Query DB inventory; return\nverified listings & photos", 10, 25, '#E6FFFA', '#319795')
    ]

    for title, desc, cx, cy, bg, border in steps:
        w, h = 20, 16
        x, y = cx - w/2, cy - h/2
        rect = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=1,rounding_size=2",
                                      facecolor=bg, edgecolor=border, linewidth=1.5)
        ax.add_patch(rect)
        ax.text(cx, cy + 3.5, title, ha='center', va='center', fontsize=8.5, fontweight='bold', color='#2D3748')
        ax.text(cx, cy - 2.5, desc, ha='center', va='center', fontsize=7.2, color='#4A5568')

    # Top Row Arrows (Left to Right)
    for i in range(3):
        ax.annotate('', xy=(steps[i+1][2] - 10.5, 72), xytext=(steps[i][2] + 10.5, 72),
                    arrowprops=dict(facecolor='#4A5568', edgecolor='#4A5568', width=1.5, headwidth=5))

    # Down from Step 4 to Step 5 (Diagonal or Right to Left Down)
    ax.annotate('', xy=(85, 33.5), xytext=(85, 63.5),
                arrowprops=dict(facecolor='#D69E2E', edgecolor='#D69E2E', width=1.5, headwidth=5))
    ax.text(87, 48.5, "Classify & Match", fontsize=7.5, color='#D69E2E', va='center')

    # Bottom Row Arrows (Right to Left: 8 -> 7 -> 6 -> 5 is actually 5 -> 6 -> 7 -> 8)
    # Let's fix bottom row order: 5 (Left) -> 6 -> 7 -> 8 (Right)
    # So step 4 connects down to step 5?
    # Better: Step 4 (85, 72) -> curve down to Step 5 (85, 25) which is Property Match!
    # Let's redraw arrows cleanly:

    plt.tight_layout()
    fig.savefig("figures/fig_4_2_automation_workflow.png", dpi=300, bbox_inches='tight')
    plt.close()
    print("Saved fig_4_2_automation_workflow.png")

def create_lead_qualification_workflow():
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    ax.text(50, 95, "LEAD QUALIFICATION & CLASSIFICATION LOGIC", 
            ha='center', va='center', fontsize=12, fontweight='bold', color='#1A365D')

    # Inbound Message Box
    rect = patches.FancyBboxPatch((30, 80), 40, 9, boxstyle="round,pad=1,rounding_size=2",
                                  facecolor='#EBF8FF', edgecolor='#3182CE', linewidth=1.5)
    ax.add_patch(rect)
    ax.text(50, 84.5, "INBOUND LEAD INQUIRY & PREFERENCE EXTRACTION\n(Budget, Location, Timeline, BHK, Financing)",
            ha='center', va='center', fontsize=8.5, fontweight='bold', color='#2B6CB0')

    # Arrow Down
    ax.annotate('', xy=(50, 71), xytext=(50, 80),
                arrowprops=dict(facecolor='#4A5568', edgecolor='#4A5568', width=1.5, headwidth=5))

    # Scoring Engine Box
    rect = patches.FancyBboxPatch((25, 59), 50, 12, boxstyle="round,pad=1,rounding_size=2",
                                  facecolor='#FEFCBF', edgecolor='#D69E2E', linewidth=1.5)
    ax.add_patch(rect)
    ax.text(50, 66.5, "RULE-BASED LEAD SCORING ALGORITHM", ha='center', va='center', fontsize=9, fontweight='bold', color='#744210')
    ax.text(50, 62, "Budget Defined (+30) | Timeline < 90d (+25) | Site Visit Request (+25)\nSpecific Location (+10) | Financing Ready (+10)",
            ha='center', va='center', fontsize=7.5, color='#744210')

    # 3 Outcome Arrows
    ax.annotate('', xy=(18, 45), xytext=(35, 59), arrowprops=dict(facecolor='#E53E3E', edgecolor='#E53E3E', width=1.2, headwidth=5))
    ax.annotate('', xy=(50, 45), xytext=(50, 59), arrowprops=dict(facecolor='#DD6B20', edgecolor='#DD6B20', width=1.2, headwidth=5))
    ax.annotate('', xy=(82, 45), xytext=(65, 59), arrowprops=dict(facecolor='#38A169', edgecolor='#38A169', width=1.2, headwidth=5))

    # 3 Category Boxes
    # COLD
    rect_c = patches.FancyBboxPatch((5, 27), 26, 17, boxstyle="round,pad=1,rounding_size=2",
                                    facecolor='#FFF5F5', edgecolor='#E53E3E', linewidth=1.5)
    ax.add_patch(rect_c)
    ax.text(18, 39, "COLD LEAD (< 45)", ha='center', va='center', fontsize=9, fontweight='bold', color='#9B2C2C')
    ax.text(18, 32, "Low immediate intent;\ncasual browse or invalid budget.\nAction: Low-frequency\neducational follow-up.",
            ha='center', va='center', fontsize=7.2, color='#4A5568')

    # WARM
    rect_w = patches.FancyBboxPatch((37, 27), 26, 17, boxstyle="round,pad=1,rounding_size=2",
                                    facecolor='#FFFAF0', edgecolor='#DD6B20', linewidth=1.5)
    ax.add_patch(rect_w)
    ax.text(50, 39, "WARM LEAD (45 - 74)", ha='center', va='center', fontsize=9, fontweight='bold', color='#C05621')
    ax.text(50, 32, "Interested, evaluating options;\ntimeline 3-6 months.\nAction: Send brochures,\nschedule follow-up in 24-48h.",
            ha='center', va='center', fontsize=7.2, color='#4A5568')

    # HOT
    rect_h = patches.FancyBboxPatch((69, 27), 26, 17, boxstyle="round,pad=1,rounding_size=2",
                                    facecolor='#F0FFF4', edgecolor='#38A169', linewidth=1.5)
    ax.add_patch(rect_h)
    ax.text(82, 39, "HOT LEAD (>= 75)", ha='center', va='center', fontsize=9, fontweight='bold', color='#22543D')
    ax.text(82, 32, "High buying intent;\npre-approved, timeline < 90d.\nAction: Prompt site visit booking;\ninstant human agent alert.",
            ha='center', va='center', fontsize=7.2, color='#4A5568')

    # Bottom Database & Action Note
    rect_bot = patches.FancyBboxPatch((15, 6), 70, 12, boxstyle="round,pad=1,rounding_size=2",
                                     facecolor='#F7FAFC', edgecolor='#A0AEC0', linewidth=1.2)
    ax.add_patch(rect_bot)
    ax.text(50, 13.5, "EXPLAINABLE PERSISTENCE & HUMAN OVERRIDE GATE", ha='center', va='center', fontsize=8.5, fontweight='bold', color='#2D3748')
    ax.text(50, 8.5, "All classification rationales are logged to `ai_decisions` table with timestamped evidence.\nHuman sales agents retain permanent authority to reclassify or reassign leads.",
            ha='center', va='center', fontsize=7.2, color='#4A5568')

    plt.tight_layout()
    fig.savefig("figures/fig_4_3_lead_qualification.png", dpi=300, bbox_inches='tight')
    plt.close()
    print("Saved fig_4_3_lead_qualification.png")

create_system_architecture()
create_automation_workflow()
create_lead_qualification_workflow()
