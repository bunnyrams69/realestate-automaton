import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

DOCX_PATH = r"E:\Real Estate-Ai_Automation\Professional_Training_I_Real_Estate_AI_Automation_Report.docx"

def set_font(run, size=11, bold=False, color_rgb=(0,0,0)):
    run.font.name = "Arial"
    run.font.size = Pt(size)
    run.bold = bold
    if color_rgb:
        run.font.color.rgb = RGBColor(*color_rgb)
    rPr = run._r.get_or_add_rPr()
    rFonts = rPr.find(qn('w:rFonts'))
    if rFonts is None:
        rFonts = parse_xml(f'<w:rFonts {nsdecls("w")} w:ascii="Arial" w:hAnsi="Arial" w:cs="Arial"/>')
        rPr.insert(0, rFonts)
    else:
        rFonts.set(qn('w:ascii'), 'Arial')
        rFonts.set(qn('w:hAnsi'), 'Arial')
        rFonts.set(qn('w:cs'), 'Arial')

def update_front_matter_tables_and_figures(doc):
    print("Updating Table of Contents (Table 0)...")
    t0 = doc.tables[0]
    
    # Row 1: ABSTRACT
    t0.rows[1].cells[1].text = "ABSTRACT"
    t0.rows[1].cells[4].text = "vi"
    set_font(t0.rows[1].cells[1].paragraphs[0].runs[0], size=11, bold=True)
    set_font(t0.rows[1].cells[4].paragraphs[0].runs[0], size=11, bold=True)
    t0.rows[1].cells[4].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Row 2: LIST OF FIGURES & TABLES
    t0.rows[2].cells[1].text = "LIST OF FIGURES\nLIST OF TABLES"
    t0.rows[2].cells[4].text = "viii\nix"
    for r in t0.rows[2].cells[1].paragraphs[0].runs:
        set_font(r, size=11, bold=True)
    for r in t0.rows[2].cells[4].paragraphs[0].runs:
        set_font(r, size=11, bold=True)
    t0.rows[2].cells[4].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Row 3: 1 INTRODUCTION
    t0.rows[3].cells[0].text = "1"
    t0.rows[3].cells[1].text = "INTRODUCTION"
    t0.rows[3].cells[4].text = "1"
    set_font(t0.rows[3].cells[0].paragraphs[0].runs[0], size=11, bold=True)
    set_font(t0.rows[3].cells[1].paragraphs[0].runs[0], size=11, bold=True)
    set_font(t0.rows[3].cells[4].paragraphs[0].runs[0], size=11, bold=True)
    t0.rows[3].cells[0].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    t0.rows[3].cells[4].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Row 4: 2 LITERATURE SURVEY
    t0.rows[4].cells[0].text = "2"
    t0.rows[4].cells[1].text = "LITERATURE SURVEY"
    t0.rows[4].cells[4].text = "4"
    set_font(t0.rows[4].cells[0].paragraphs[0].runs[0], size=11, bold=True)
    set_font(t0.rows[4].cells[1].paragraphs[0].runs[0], size=11, bold=True)
    set_font(t0.rows[4].cells[4].paragraphs[0].runs[0], size=11, bold=True)
    t0.rows[4].cells[0].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    t0.rows[4].cells[4].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Row 5: 2.1 Inferences
    t0.rows[5].cells[1].text = "2.1"
    t0.rows[5].cells[2].text = "Inferences from Literature Survey"
    t0.rows[5].cells[4].text = "6"
    set_font(t0.rows[5].cells[1].paragraphs[0].runs[0], size=10.5, bold=False)
    set_font(t0.rows[5].cells[2].paragraphs[0].runs[0], size=10.5, bold=False)
    set_font(t0.rows[5].cells[4].paragraphs[0].runs[0], size=10.5, bold=False)
    t0.rows[5].cells[1].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    t0.rows[5].cells[4].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Row 6: 2.2 Open Problems
    t0.rows[6].cells[1].text = "2.2"
    t0.rows[6].cells[2].text = "Open Problems in Existing Systems"
    t0.rows[6].cells[4].text = "6"
    set_font(t0.rows[6].cells[1].paragraphs[0].runs[0], size=10.5, bold=False)
    set_font(t0.rows[6].cells[2].paragraphs[0].runs[0], size=10.5, bold=False)
    set_font(t0.rows[6].cells[4].paragraphs[0].runs[0], size=10.5, bold=False)
    t0.rows[6].cells[1].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    t0.rows[6].cells[4].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Row 7: 3 REQUIREMENTS ANALYSIS
    t0.rows[7].cells[0].text = "3"
    t0.rows[7].cells[1].text = "REQUIREMENTS ANALYSIS"
    t0.rows[7].cells[4].text = "7"
    set_font(t0.rows[7].cells[0].paragraphs[0].runs[0], size=11, bold=True)
    set_font(t0.rows[7].cells[1].paragraphs[0].runs[0], size=11, bold=True)
    set_font(t0.rows[7].cells[4].paragraphs[0].runs[0], size=11, bold=True)
    t0.rows[7].cells[0].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    t0.rows[7].cells[4].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Row 8: 3.1 Feasibility Studies
    t0.rows[8].cells[1].text = "3.1"
    t0.rows[8].cells[2].text = "Feasibility Studies / Risk Analysis of the Project"
    t0.rows[8].cells[4].text = "7"
    set_font(t0.rows[8].cells[1].paragraphs[0].runs[0], size=10.5, bold=False)
    set_font(t0.rows[8].cells[2].paragraphs[0].runs[0], size=10.5, bold=False)
    set_font(t0.rows[8].cells[4].paragraphs[0].runs[0], size=10.5, bold=False)
    t0.rows[8].cells[1].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    t0.rows[8].cells[4].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Row 9: 3.2 & 3.3
    t0.rows[9].cells[1].text = "3.2\n3.3"
    t0.rows[9].cells[2].text = "Software Requirements Specification Document\nSystem Actors and Use Cases"
    t0.rows[9].cells[4].text = "8\n8"
    for r in t0.rows[9].cells[1].paragraphs[0].runs:
        set_font(r, size=10.5, bold=False)
    for r in t0.rows[9].cells[2].paragraphs[0].runs:
        set_font(r, size=10.5, bold=False)
    for r in t0.rows[9].cells[4].paragraphs[0].runs:
        set_font(r, size=10.5, bold=False)
    t0.rows[9].cells[1].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    t0.rows[9].cells[4].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Row 10: 4 DESCRIPTION OF PROPOSED SYSTEM
    t0.rows[10].cells[0].text = "4"
    t0.rows[10].cells[1].text = "DESCRIPTION OF PROPOSED SYSTEM"
    t0.rows[10].cells[4].text = "10"
    set_font(t0.rows[10].cells[0].paragraphs[0].runs[0], size=11, bold=True)
    set_font(t0.rows[10].cells[1].paragraphs[0].runs[0], size=11, bold=True)
    set_font(t0.rows[10].cells[4].paragraphs[0].runs[0], size=11, bold=True)
    t0.rows[10].cells[0].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    t0.rows[10].cells[4].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Row 11: 4.1 Methodology
    t0.rows[11].cells[1].text = "4.1"
    t0.rows[11].cells[2].text = "Selected Methodology or Process Model"
    t0.rows[11].cells[4].text = "10"
    set_font(t0.rows[11].cells[1].paragraphs[0].runs[0], size=10.5, bold=False)
    set_font(t0.rows[11].cells[2].paragraphs[0].runs[0], size=10.5, bold=False)
    set_font(t0.rows[11].cells[4].paragraphs[0].runs[0], size=10.5, bold=False)
    t0.rows[11].cells[1].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    t0.rows[11].cells[4].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Row 12: 4.2 Architecture
    t0.rows[12].cells[1].text = "4.2"
    t0.rows[12].cells[2].text = "Architecture / Overall Design of Proposed System"
    t0.rows[12].cells[4].text = "11"
    set_font(t0.rows[12].cells[1].paragraphs[0].runs[0], size=10.5, bold=False)
    set_font(t0.rows[12].cells[2].paragraphs[0].runs[0], size=10.5, bold=False)
    set_font(t0.rows[12].cells[4].paragraphs[0].runs[0], size=10.5, bold=False)
    t0.rows[12].cells[1].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    t0.rows[12].cells[4].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Row 13: 4.3 Implementation & Testing Plan
    t0.rows[13].cells[1].text = "4.3"
    t0.rows[13].cells[2].text = "Description of Software Implementation and Testing Plan"
    t0.rows[13].cells[4].text = "13"
    set_font(t0.rows[13].cells[1].paragraphs[0].runs[0], size=10.5, bold=False)
    set_font(t0.rows[13].cells[2].paragraphs[0].runs[0], size=10.5, bold=False)
    set_font(t0.rows[13].cells[4].paragraphs[0].runs[0], size=10.5, bold=False)
    t0.rows[13].cells[1].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    t0.rows[13].cells[4].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Row 14: 4.4, 4.5, 4.6
    t0.rows[14].cells[1].text = "4.4\n4.5\n4.6"
    t0.rows[14].cells[2].text = "Project Management Plan\nFinancial Report on Estimated Costing\nTransition / Software to Operations Plan"
    t0.rows[14].cells[4].text = "17\n18\n18"
    for r in t0.rows[14].cells[1].paragraphs[0].runs:
        set_font(r, size=10.5, bold=False)
    for r in t0.rows[14].cells[2].paragraphs[0].runs:
        set_font(r, size=10.5, bold=False)
    for r in t0.rows[14].cells[4].paragraphs[0].runs:
        set_font(r, size=10.5, bold=False)
    t0.rows[14].cells[1].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    t0.rows[14].cells[4].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Row 15: REFERENCES
    t0.rows[15].cells[1].text = "REFERENCES"
    t0.rows[15].cells[4].text = "19"
    set_font(t0.rows[15].cells[1].paragraphs[0].runs[0], size=11, bold=True)
    set_font(t0.rows[15].cells[4].paragraphs[0].runs[0], size=11, bold=True)
    t0.rows[15].cells[4].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

    print("Updating List of Figures...")
    # List of figures in paragraphs 155 to 159
    fig_items = [
        ("4.1", "End-to-End System Architecture of Real Estate AI Automation Platform", "11"),
        ("4.2", "Asynchronous Real Estate Lead Ingestion and Automation Lifecycle Workflow", "12"),
        ("4.3", "Multi-Parameter Dynamic Lead Qualification and Scoring Framework", "14"),
        ("4.4", "Automated Site Visit Scheduling and Calendar Sync State Machine", "15"),
        ("4.5", "Marketing Analytics, Ad Attribution, and Performance Optimization Architecture", "16")
    ]
    for idx, (f_num, f_title, f_page) in enumerate(fig_items):
        p_idx = 155 + idx
        p = doc.paragraphs[p_idx]
        p.text = f"{f_num}\t{f_title}\t{f_page}"
        for r in p.runs:
            set_font(r, size=11, bold=False)

    print("Updating List of Tables (Table 1)...")
    t1 = doc.tables[1]
    tables_data = [
        ("3.1", "Comprehensive Project Risk Assessment and Mitigation Matrix", "8"),
        ("3.2", "Minimum and Recommended Hardware and Software Specifications", "8"),
        ("3.3", "System Functional Requirements Specification (FR-01 to FR-12)", "8"),
        ("3.4", "System Non-Functional Requirements Specification (NFR-01 to NFR-08)", "9"),
        ("3.5", "Actor-to-Capability Interaction Use Case Matrix", "10"),
        ("4.1", "Comprehensive System Testing Suite, Scenarios, and Verification Gates", "17"),
        ("4.2", "Ten-Phase Engineering Roadmap, Deliverables, and Verification Milestones", "17"),
        ("4.3", "Financial Costing, Cloud Infrastructure, and Third-Party API Operating Budget", "18")
    ]
    
    # Overwrite rows 1, 2, 3
    for i in range(1, 4):
        num, name, page = tables_data[i-1]
        t1.rows[i].cells[0].text = num
        t1.rows[i].cells[1].text = name
        t1.rows[i].cells[2].text = page
        for c in t1.rows[i].cells:
            for r in c.paragraphs[0].runs:
                set_font(r, size=10.5, bold=False)
            c.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER if c != t1.rows[i].cells[1] else WD_ALIGN_PARAGRAPH.LEFT
            
    # Append rows 4 to 8
    for i in range(4, len(tables_data) + 1):
        num, name, page = tables_data[i-1]
        row = t1.add_row()
        row.cells[0].text = num
        row.cells[1].text = name
        row.cells[2].text = page
        for c in row.cells:
            for r in c.paragraphs[0].runs:
                set_font(r, size=10.5, bold=False)
            c.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER if c != row.cells[1] else WD_ALIGN_PARAGRAPH.LEFT
            
    print(f"Saving fully updated document to {DOCX_PATH}...")
    doc.save(DOCX_PATH)
    print("Document saved successfully!")

if __name__ == "__main__":
    doc = docx.Document(DOCX_PATH)
    update_front_matter_tables_and_figures(doc)
