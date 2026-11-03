import matplotlib.pyplot as plt
import matplotlib.patches as patches

plt.rcParams['font.sans-serif'] = 'Arial'
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['figure.dpi'] = 300

def create_visit_booking_workflow():
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    ax.text(50, 95, "SITE VISIT BOOKING & CALENDAR SYNCHRONIZATION WORKFLOW", 
            ha='center', va='center', fontsize=11.5, fontweight='bold', color='#1A365D')

    boxes = [
        ("1. VISIT REQUEST", "Customer indicates interest in visiting property\nvia WhatsApp message", 12, 68, 22, 16, '#EBF8FF', '#3182CE'),
        ("2. AVAILABILITY CHECK", "System queries Google Calendar API\n& agent schedule for free 45-min slots", 39, 68, 22, 16, '#FEFCBF', '#D69E2E'),
        ("3. SLOT CONFIRMATION", "Customer selects slot from options;\nexplicit consent obtained", 66, 68, 22, 16, '#E6FFFA', '#319795'),
        
        ("6. VISIT EXECUTION & NOTES", "Visit conducted; sales agent records\nwalkthrough notes and outcome", 66, 24, 22, 16, '#FAF5FF', '#805AD5'),
        ("5. REMINDER DISPATCH", "Automated WhatsApp reminder sent\n24 hours and 2 hours prior to visit", 39, 24, 22, 16, '#FFFAF0', '#DD6B20'),
        ("4. CALENDAR SYNC & DB WRITE", "Google Calendar event created;\nRecord saved to `site_visits` table", 12, 24, 22, 16, '#F0FFF4', '#38A169')
    ]

    for title, desc, x, y, w, h, bg, border in boxes:
        rect = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=1,rounding_size=2",
                                      facecolor=bg, edgecolor=border, linewidth=1.5)
        ax.add_patch(rect)
        ax.text(x + w/2, y + h*0.68, title, ha='center', va='center', fontsize=8, fontweight='bold', color='#2D3748')
        ax.text(x + w/2, y + h*0.32, desc, ha='center', va='center', fontsize=7, color='#4A5568')

    # Top Row Arrows: 1 -> 2 -> 3
    ax.annotate('', xy=(38, 76), xytext=(35, 76), arrowprops=dict(facecolor='#4A5568', edgecolor='#4A5568', width=1.2, headwidth=5))
    ax.annotate('', xy=(65, 76), xytext=(62, 76), arrowprops=dict(facecolor='#4A5568', edgecolor='#4A5568', width=1.2, headwidth=5))

    # Down from 3 to 4
    ax.annotate('', xy=(23, 41), xytext=(77, 67),
                arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=-0.2", color='#38A169', lw=1.5))
    ax.text(50, 52, "Booking Confirmed by User", fontsize=7.5, color='#38A169', ha='center')

    # Bottom Row Arrows: 4 -> 5 -> 6
    ax.annotate('', xy=(38, 32), xytext=(35, 32), arrowprops=dict(facecolor='#4A5568', edgecolor='#4A5568', width=1.2, headwidth=5))
    ax.annotate('', xy=(65, 32), xytext=(62, 32), arrowprops=dict(facecolor='#4A5568', edgecolor='#4A5568', width=1.2, headwidth=5))

    # Bottom Safeguard Note
    rect_safeguard = patches.FancyBboxPatch((12, 5), 76, 12, boxstyle="round,pad=1,rounding_size=2",
                                          facecolor='#FFF5F5', edgecolor='#E53E3E', linewidth=1.2)
    ax.add_patch(rect_safeguard)
    ax.text(50, 12.5, "INTEGRITY GUARANTEE: NEVER CONFIRM BEFORE AUTHORITATIVE WRITE", ha='center', va='center', fontsize=8, fontweight='bold', color='#9B2C2C')
    ax.text(50, 8, "The AI agent is architecturally blocked from claiming a booking has succeeded until the database write\nand Google Calendar API response return HTTP 200/201. Private calendar details of other leads are strictly isolated.",
            ha='center', va='center', fontsize=7, color='#4A5568')

    plt.tight_layout()
    fig.savefig("figures/fig_4_4_site_visit_booking.png", dpi=300, bbox_inches='tight')
    plt.close()
    print("Saved fig_4_4_site_visit_booking.png")

def create_marketing_analytics_workflow():
    fig, ax = plt.subplots(figsize=(9, 5.5))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    ax.text(50, 94, "CUSTOMER CONVERSATION INTELLIGENCE & ADVERTISING INSIGHTS", 
            ha='center', va='center', fontsize=11.5, fontweight='bold', color='#1A365D')

    # Input: Collected Interactions
    rect_in = patches.FancyBboxPatch((8, 62), 24, 22, boxstyle="round,pad=1,rounding_size=2",
                                     facecolor='#EBF8FF', edgecolor='#3182CE', linewidth=1.5)
    ax.add_patch(rect_in)
    ax.text(20, 77, "INBOUND CHAT DATA", ha='center', va='center', fontsize=8.5, fontweight='bold', color='#2B6CB0')
    ax.text(20, 69, "Anonymized conversation\ntranscripts, questions,\nobjections, and amenity\npreference inquiries",
            ha='center', va='center', fontsize=7.2, color='#4A5568')

    # Middle: Analytics Engine
    rect_mid = patches.FancyBboxPatch((38, 62), 24, 22, boxstyle="round,pad=1,rounding_size=2",
                                      facecolor='#FAF5FF', edgecolor='#805AD5', linewidth=1.5)
    ax.add_patch(rect_mid)
    ax.text(50, 77, "INSIGHTS ENGINE", ha='center', va='center', fontsize=8.5, fontweight='bold', color='#6B46C1')
    ax.text(50, 69, "Clustering algorithms\ndetect frequent objections,\nunanswered questions,\nand demand trends",
            ha='center', va='center', fontsize=7.2, color='#4A5568')

    # Meta Ads Ingestion
    rect_meta = patches.FancyBboxPatch((38, 22), 24, 22, boxstyle="round,pad=1,rounding_size=2",
                                       facecolor='#FEFCBF', edgecolor='#D69E2E', linewidth=1.5)
    ax.add_patch(rect_meta)
    ax.text(50, 37, "META MARKETING API", ha='center', va='center', fontsize=8.5, fontweight='bold', color='#744210')
    ax.text(50, 29, "Read-only ingestion of\ncampaign spend, clicks,\nimpressions, and ad set\nattribution metadata",
            ha='center', va='center', fontsize=7.2, color='#4A5568')

    # Output: Marketing Intelligence
    rect_out = patches.FancyBboxPatch((68, 42), 24, 30, boxstyle="round,pad=1,rounding_size=2",
                                      facecolor='#F0FFF4', edgecolor='#38A169', linewidth=1.5)
    ax.add_patch(rect_out)
    ax.text(80, 64, "MARKETING ADVISORY", ha='center', va='center', fontsize=8.5, fontweight='bold', color='#22543D')
    ax.text(80, 52, "Actionable recommendations:\n- Clarify price in ad copy\n- Highlight covered parking\n- Adjust target audience\n- Refine landing page copy\n(Evidence-based advice)",
            ha='center', va='center', fontsize=7.2, color='#4A5568')

    # Arrows
    ax.annotate('', xy=(37, 73), xytext=(33, 73), arrowprops=dict(facecolor='#4A5568', edgecolor='#4A5568', width=1.2, headwidth=5))
    ax.annotate('', xy=(67, 65), xytext=(63, 70), arrowprops=dict(facecolor='#6B46C1', edgecolor='#6B46C1', width=1.2, headwidth=5))
    ax.annotate('', xy=(67, 50), xytext=(63, 35), arrowprops=dict(facecolor='#D69E2E', edgecolor='#D69E2E', width=1.2, headwidth=5))

    # Bottom Privacy Banner
    rect_priv = patches.FancyBboxPatch((8, 5), 84, 10, boxstyle="round,pad=1,rounding_size=2",
                                       facecolor='#EDF2F7', edgecolor='#718096', linewidth=1.2)
    ax.add_patch(rect_priv)
    ax.text(50, 11, "PRIVACY & ATTRIBUTION INTEGRITY POLICY", ha='center', va='center', fontsize=8, fontweight='bold', color='#2D3748')
    ax.text(50, 7.5, "Personal PII is strictly stripped prior to clustering. Ad insights are strictly advisory; automated budget modifications are barred.",
            ha='center', va='center', fontsize=7, color='#4A5568')

    plt.tight_layout()
    fig.savefig("figures/fig_4_5_marketing_analytics.png", dpi=300, bbox_inches='tight')
    plt.close()
    print("Saved fig_4_5_marketing_analytics.png")

create_visit_booking_workflow()
create_marketing_analytics_workflow()
