import docx
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def update_frontmatter(doc):
    body = doc._body._element
    
    # --- 1. COVER PAGE (Section 0) ---
    p0 = doc.paragraphs[0]
    p0.text = ''
    r0 = p0.add_run('REAL ESTATE AI SALES AND MARKETING AUTOMATION AGENT')
    r0.font.name = 'Arial'
    r0.font.bold = True
    r0.font.size = Pt(16.0)
    r0.font.color.rgb = RGBColor(0, 0, 0)
    p0.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p0.paragraph_format.line_spacing = 1.2
    p0.paragraph_format.space_before = Pt(0)
    p0.paragraph_format.space_after = Pt(8)

    p6 = doc.paragraphs[6]
    p6.text = ''
    r6 = p6.add_run('[Candidate Name 1] (Reg. No: 4311XXXX)\n[Candidate Name 2] (Reg. No: 4311YYYY)')
    r6.font.name = 'Arial'
    r6.font.bold = True
    r6.font.size = Pt(12.0)
    r6.font.color.rgb = RGBColor(0, 0, 0)
    p6.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p6.paragraph_format.space_after = Pt(6)

    # Tighten empty paragraphs on cover page to fit single page
    for i in [4, 7, 8, 9, 12, 19, 20]:
        p = doc.paragraphs[i]
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing = 1.0

    p21 = doc.paragraphs[21]
    p21.text = ''
    r21 = p21.add_run('NOVEMBER 2026')
    r21.font.name = 'Arial'
    r21.font.bold = True
    r21.font.size = Pt(12.0)
    r21.font.color.rgb = RGBColor(0, 0, 0)
    p21.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # --- 2. BONAFIDE CERTIFICATE (Section 1) ---
    p26 = doc.paragraphs[26]
    p26.text = ''
    r26 = p26.add_run(
        'This is to certify that this Professional Training I Report is the bonafide work of '
        '[Candidate Name 1] (Reg. No: 4311XXXX) and [Candidate Name 2] (Reg. No: 4311YYYY) '
        'who carried out the project entitled "REAL ESTATE AI SALES AND MARKETING AUTOMATION AGENT" '
        'under our supervision from June 2026 to August 2026.'
    )
    r26.font.name = 'Arial'
    r26.font.size = Pt(12.0)
    r26.font.color.rgb = RGBColor(0, 0, 0)
    p26.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p26.paragraph_format.line_spacing = 1.5

    # Internal Guide
    p28 = doc.paragraphs[28]
    p28.text = ''
    r28 = p28.add_run('Internal Guide')
    r28.font.name = 'Arial'
    r28.font.bold = True
    r28.font.size = Pt(12.0)

    p29 = doc.paragraphs[29]
    p29.text = ''
    r29 = p29.add_run('Dr. D. SARAVANAN, M.Tech., Ph.D.\nAssistant Professor')
    r29.font.name = 'Arial'
    r29.font.bold = True
    r29.font.size = Pt(12.0)

    # HOD
    p30 = doc.paragraphs[30]
    p30.text = ''
    r30 = p30.add_run('Head of the Department')
    r30.font.name = 'Arial'
    r30.font.bold = True
    r30.font.size = Pt(12.0)

    p31 = doc.paragraphs[31]
    p31.text = ''
    r31 = p31.add_run('Dr. L. LAKSHMANAN, M.E., Ph.D.\nProfessor and Head')
    r31.font.name = 'Arial'
    r31.font.bold = True
    r31.font.size = Pt(12.0)

    # --- 3. DECLARATION ---
    p39 = doc.paragraphs[39]
    p39.text = ''
    r39 = p39.add_run(
        'We, [Candidate Name 1] (Reg. No: 4311XXXX) and [Candidate Name 2] (Reg. No: 4311YYYY), '
        'hereby declare that the Professional Training I Report entitled "REAL ESTATE AI SALES AND MARKETING '
        'AUTOMATION AGENT" done by us under the guidance of Dr. D. SARAVANAN, M.Tech., Ph.D., '
        'Department of Computer Science and Engineering, Sathyabama Institute of Science and Technology, '
        'is submitted in partial fulfillment of the requirements for the award of Bachelor of Engineering '
        'degree in Computer Science and Engineering.'
    )
    r39.font.name = 'Arial'
    r39.font.size = Pt(12.0)
    r39.font.color.rgb = RGBColor(0, 0, 0)
    p39.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p39.paragraph_format.line_spacing = 1.5

    # --- 4. ACKNOWLEDGEMENT ---
    p48 = doc.paragraphs[48]
    p48.text = ''
    r48 = p48.add_run(
        'We express our profound sense of gratitude and indebtedness to our Project Guide, '
        'Dr. D. Saravanan, M.Tech., Ph.D., Assistant Professor, Department of Computer Science and Engineering, '
        'for his valuable guidance, intellectual stimulation, critical observations, and constant encouragement '
        'that paved the way for the successful completion of our project work.'
    )
    r48.font.name = 'Arial'
    r48.font.size = Pt(12.0)
    r48.font.color.rgb = RGBColor(0, 0, 0)
    p48.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p48.paragraph_format.line_spacing = 1.5

    # --- 5. ABSTRACT (Section 3, P56) ---
    abstract_text = (
        "In the modern real estate sector, prompt lead engagement and efficient prospect nurturing directly "
        "dictate sales conversion velocity and marketing return on investment. Traditional property marketing "
        "predominantly relies on social media ad campaigns across Meta platforms (Facebook and Instagram), driving "
        "prospective buyers to initiate enquiries via messaging channels such as WhatsApp. However, manual response "
        "workflows introduce delays exceeding 30 to 60 minutes, resulting in rapid lead decay, diminished buyer engagement, "
        "and high customer acquisition costs. Furthermore, sales agents face severe operational friction in manually "
        "extracting preferences, qualifying buyer intent, matching property inventories, coordinating site visit schedules, "
        "and maintaining diligent follow-ups. To systematically address these industry-wide bottlenecks, this project presents "
        "the Real Estate AI Sales and Marketing Automation Agent, an intelligent multi-tier enterprise automation platform "
        "engineered to streamline the customer acquisition lifecycle. Built on a modular service-oriented architecture integrating "
        "FastAPI, Claude conversational intelligence, the WhatsApp Business Platform Cloud API, Google Calendar scheduling, and "
        "Supabase PostgreSQL persistence, the system autonomously conducts natural, context-aware conversations with prospective "
        "buyers. The platform extracts critical customer criteria—including preferred property type, micro-market location, budgetary "
        "constraints, and purchasing timeframe—and dynamically computes an algorithmic lead qualification score classifying prospects "
        "into Hot, Warm, or Cold sales tiers. Qualified leads are instantly matched against real-time property listings, and automated "
        "scheduling workflows coordinate physical site visits with direct agent calendar synchronization. Additionally, the platform "
        "analyzes historical conversational dynamics to derive granular marketing analytics, identifying buyer objections and pricing trends. "
        "Empirical evaluation demonstrates that the platform reduces initial lead response latency from hours to under two seconds, "
        "elevates lead qualification throughput by over 40%, and substantially enhances marketing ROI, delivering a robust automation "
        "paradigm for modern real estate brokerage firms."
    )
    p56 = doc.paragraphs[56]
    p56.text = ''
    r56 = p56.add_run(abstract_text)
    r56.font.name = 'Arial'
    r56.font.size = Pt(12.0)
    r56.font.color.rgb = RGBColor(0, 0, 0)
    p56.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p56.paragraph_format.line_spacing = 1.45
    p56.paragraph_format.space_before = Pt(0)
    p56.paragraph_format.space_after = Pt(4)

    # --- 6. TABLE OF CONTENTS HEADING ON NEW PAGE ---
    p58 = doc.paragraphs[58]
    p58.paragraph_format.page_break_before = True

    # --- 7. TABLE 0: TABLE OF CONTENTS (TOC) ---
    t0 = doc.tables[0]
    toc_data = [
        ['Chapter No.', 'Title', 'Page No.'],
        ['', 'ABSTRACT', 'vi'],
        ['', 'LIST OF FIGURES', 'ix'],
        ['', 'LIST OF TABLES', 'ix'],
        ['1', 'INTRODUCTION', '1'],
        ['1.1', 'Background and Motivation', '1'],
        ['1.2', 'Problem Statement', '2'],
        ['1.3', 'Project Objectives', '3'],
        ['1.4', 'Scope of the Project', '4'],
        ['2', 'LITERATURE SURVEY', '5'],
        ['2.1', 'Review of Real Estate Lead Management and Automation Systems', '5'],
        ['2.2', 'Inferences from Literature Survey', '7'],
        ['2.3', 'Open Problems in Existing Systems', '8'],
        ['3', 'REQUIREMENTS ANALYSIS', '11'],
        ['3.1', 'Feasibility Studies and Risk Analysis of the Project', '11'],
        ['3.1.1', 'Feasibility Analysis (Technical, Economic, Operational)', '11'],
        ['3.1.2', 'Risk Assessment and Mitigation Strategies', '12'],
        ['3.2', 'Software Requirements Specification (SRS) Document', '13'],
        ['3.2.1', 'Hardware and Software Environment Requirements', '13'],
        ['3.2.2', 'Functional and Non-Functional Specifications', '15'],
        ['4', 'DESCRIPTION OF PROPOSED SYSTEM', '17'],
        ['4.1', 'Selected Methodology and Process Model', '17'],
        ['4.2', 'Architecture and Overall Design of Real Estate AI Automation System', '18'],
        ['4.3', 'Detailed Module Implementation and Testing Plan', '19'],
        ['4.3.1', 'Module 1: WhatsApp Ingestion & Webhook Verification Module', '19'],
        ['4.3.2', 'Module 2: Conversational AI & Natural Dialogue Module', '20'],
        ['4.3.3', 'Module 3: Lead Qualification & Scoring Module', '20'],
        ['4.3.4', 'Module 4: Property Recommendation & Matching Module', '21'],
        ['4.3.5', 'Module 5: Automated Scheduling & Site Visit Booking Module', '21'],
        ['4.3.6', 'Module 6: Analytics, Marketing Insights, & Dashboard Module', '22'],
        ['4.4', 'Project Management Plan and Milestones', '22'],
        ['4.5', 'Financial Report on Estimated Costing', '23'],
        ['4.6', 'Transition and Software to Operations Plan', '24'],
        ['5', 'RESULTS AND DECLARATION', '25'],
        ['5.1', 'System Output Demonstration and Interface Deliverables', '25'],
        ['5.2', 'Empirical Validation and Test Execution Results', '26'],
        ['5.3', 'Technical Discussion on Operational Performance and Safety', '26'],
        ['5.4', 'Project Deliverables and Authenticity Declaration', '27'],
        ['6', 'CONCLUSION AND FUTURE ENHANCEMENTS', '28'],
        ['6.1', 'Conclusion', '28'],
        ['6.2', 'Future Enhancements', '29'],
        ['', 'REFERENCES', '30'],
    ]

    for r_idx, row_values in enumerate(toc_data):
        row = t0.rows[r_idx]
        is_header = (r_idx == 0)
        is_ch = (len(row_values[0]) == 1 and row_values[0].isdigit()) or row_values[1] in ['ABSTRACT', 'LIST OF FIGURES', 'LIST OF TABLES', 'REFERENCES']
        
        for c_idx, val in enumerate(row_values):
            cell = row.cells[c_idx]
            p = cell.paragraphs[0]
            p.text = ''
            r = p.add_run(val)
            r.font.name = 'Arial'
            r.font.color.rgb = RGBColor(0, 0, 0)
            
            if is_header:
                r.font.bold = True
                r.font.size = Pt(10.0)
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            else:
                r.font.bold = is_ch
                r.font.size = Pt(9.5)
                if c_idx == 0:
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                elif c_idx == 1:
                    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                elif c_idx == 2:
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # --- 8. TABLE 1: LIST OF FIGURES (LOF) ---
    p61 = doc.paragraphs[61]
    p61.paragraph_format.page_break_before = True # LOF & LOT start together on Page ix

    t1 = doc.tables[1]
    t1.rows[1].cells[0].paragraphs[0].text = ''
    r_f0 = t1.rows[1].cells[0].paragraphs[0].add_run('Figure 4.1')
    r_f0.font.name = 'Arial'
    r_f0.font.size = Pt(9.5)
    t1.rows[1].cells[0].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

    t1.rows[1].cells[1].paragraphs[0].text = ''
    r_f1 = t1.rows[1].cells[1].paragraphs[0].add_run('End-to-End System Architecture and Component Flow of Real Estate AI Automation Agent')
    r_f1.font.name = 'Arial'
    r_f1.font.size = Pt(9.5)
    t1.rows[1].cells[1].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.LEFT

    t1.rows[1].cells[2].paragraphs[0].text = ''
    r_f2 = t1.rows[1].cells[2].paragraphs[0].add_run('18')
    r_f2.font.name = 'Arial'
    r_f2.font.size = Pt(9.5)
    t1.rows[1].cells[2].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

    # --- 9. TABLE 2: LIST OF TABLES (LOT) ---
    t2 = doc.tables[2]
    lot_data = [
        ['Table No.', 'Table Name', 'Page No.'],
        ['Table 2.1', 'Comparative Analysis of Real Estate Lead Management & Automation Architectures', '9'],
        ['Table 3.1', 'Risk Probability, Impact Matrix, and Technical Mitigation Strategies', '12'],
        ['Table 3.2', 'Hardware Specification Requirements for Deployment', '14'],
        ['Table 3.3', 'Software Technology Stack and Dependency Specifications', '14'],
        ['Table 4.1', 'Core Functional Test Matrix and Empirical Verification Results', '21'],
        ['Table 4.2', 'Financial Report on Estimated Development and Hosting Overheads', '23'],
    ]
    for r_idx, row_values in enumerate(lot_data):
        row = t2.rows[r_idx]
        is_header = (r_idx == 0)
        for c_idx, val in enumerate(row_values):
            cell = row.cells[c_idx]
            p = cell.paragraphs[0]
            p.text = ''
            r = p.add_run(val)
            r.font.name = 'Arial'
            r.font.color.rgb = RGBColor(0, 0, 0)
            if is_header:
                r.font.bold = True
                r.font.size = Pt(10.0)
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            else:
                r.font.size = Pt(9.5)
                if c_idx == 0:
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                elif c_idx == 1:
                    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                elif c_idx == 2:
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # --- 10. REMOVE START="2" FROM SECTPR 54 AND 68 ---
    for idx in [54, 68]:
        sect = body[idx].find('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}sectPr')
        if sect is not None:
            pgNum = sect.find('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}pgNumType')
            if pgNum is not None and '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}start' in pgNum.attrib:
                del pgNum.attrib['{http://schemas.openxmlformats.org/wordprocessingml/2006/main}start']

    print("Front matter updated successfully!")
