import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn
import win32com.client
import pymupdf

DOCX_PATH = r"E:\Real Estate-Ai_Automation\Professional_Training_I_Real_Estate_AI_Automation_Report.docx"
PDF_PATH = r"E:\Real Estate-Ai_Automation\Professional_Training_I_Real_Estate_AI_Automation_Report.pdf"

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

def get_unique_cells(row):
    unique = []
    for c in row.cells:
        if c._tc not in [u._tc for u in unique]:
            unique.append(c)
    return unique

def fix_all_front_matter():
    # We rebuild from clean template to have clean structure
    import build_perfect_report
    print("Step 1: Running build_perfect_report()...")
    build_perfect_report.build_perfect_report()
    
    print("Step 2: Updating TOC, Figures, and Tables with clean cell mapping...")
    doc = docx.Document(DOCX_PATH)
    
    # 1. Update Table 0 (Table of Contents)
    t0 = doc.tables[0]
    
    # Row 1: ABSTRACT
    u = get_unique_cells(t0.rows[1])
    u[1].text = "ABSTRACT"
    u[2].text = "vi"
    set_font(u[1].paragraphs[0].runs[0], size=11, bold=True)
    set_font(u[2].paragraphs[0].runs[0], size=11, bold=True)
    u[2].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Row 2: LIST OF FIGURES & TABLES
    u = get_unique_cells(t0.rows[2])
    u[1].text = "LIST OF FIGURES\nLIST OF TABLES"
    u[2].text = "viii\nix"
    for r in u[1].paragraphs[0].runs:
        set_font(r, size=11, bold=True)
    for r in u[2].paragraphs[0].runs:
        set_font(r, size=11, bold=True)
    u[2].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Row 3: 1 INTRODUCTION
    u = get_unique_cells(t0.rows[3])
    u[0].text = "1"
    u[1].text = "INTRODUCTION"
    u[2].text = "1"
    set_font(u[0].paragraphs[0].runs[0], size=11, bold=True)
    set_font(u[1].paragraphs[0].runs[0], size=11, bold=True)
    set_font(u[2].paragraphs[0].runs[0], size=11, bold=True)
    u[0].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    u[2].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Row 4: 2 LITERATURE SURVEY
    u = get_unique_cells(t0.rows[4])
    u[0].text = "2"
    u[1].text = "LITERATURE SURVEY"
    u[2].text = "4"
    set_font(u[0].paragraphs[0].runs[0], size=11, bold=True)
    set_font(u[1].paragraphs[0].runs[0], size=11, bold=True)
    set_font(u[2].paragraphs[0].runs[0], size=11, bold=True)
    u[0].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    u[2].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Row 5: 2.1 Inferences
    u = get_unique_cells(t0.rows[5])
    u[1].text = "2.1"
    u[2].text = "Inferences from Literature Survey"
    u[3].text = "6"
    set_font(u[1].paragraphs[0].runs[0], size=10.5, bold=False)
    set_font(u[2].paragraphs[0].runs[0], size=10.5, bold=False)
    set_font(u[3].paragraphs[0].runs[0], size=10.5, bold=False)
    u[1].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    u[3].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Row 6: 2.2 Open Problems
    u = get_unique_cells(t0.rows[6])
    u[1].text = "2.2"
    u[2].text = "Open Problems in Existing Systems"
    u[3].text = "6"
    set_font(u[1].paragraphs[0].runs[0], size=10.5, bold=False)
    set_font(u[2].paragraphs[0].runs[0], size=10.5, bold=False)
    set_font(u[3].paragraphs[0].runs[0], size=10.5, bold=False)
    u[1].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    u[3].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Row 7: 3 REQUIREMENTS ANALYSIS
    u = get_unique_cells(t0.rows[7])
    u[0].text = "3"
    u[1].text = "REQUIREMENTS ANALYSIS"
    u[2].text = "7"
    set_font(u[0].paragraphs[0].runs[0], size=11, bold=True)
    set_font(u[1].paragraphs[0].runs[0], size=11, bold=True)
    set_font(u[2].paragraphs[0].runs[0], size=11, bold=True)
    u[0].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    u[2].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Row 8: 3.1 Feasibility
    u = get_unique_cells(t0.rows[8])
    u[1].text = "3.1"
    u[2].text = "Feasibility Studies / Risk Analysis of the Project"
    u[3].text = "7"
    set_font(u[1].paragraphs[0].runs[0], size=10.5, bold=False)
    set_font(u[2].paragraphs[0].runs[0], size=10.5, bold=False)
    set_font(u[3].paragraphs[0].runs[0], size=10.5, bold=False)
    u[1].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    u[3].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Row 9: 3.2 & 3.3
    u = get_unique_cells(t0.rows[9])
    u[1].text = "3.2\n3.3"
    u[2].text = "Software Requirements Specification Document\nSystem Actors and Use Cases"
    u[3].text = "8\n8"
    for r in u[1].paragraphs[0].runs:
        set_font(r, size=10.5, bold=False)
    for r in u[2].paragraphs[0].runs:
        set_font(r, size=10.5, bold=False)
    for r in u[3].paragraphs[0].runs:
        set_font(r, size=10.5, bold=False)
    u[1].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    u[3].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Row 10: 4 DESCRIPTION OF PROPOSED SYSTEM
    u = get_unique_cells(t0.rows[10])
    u[0].text = "4"
    u[1].text = "DESCRIPTION OF PROPOSED SYSTEM"
    u[2].text = "10"
    set_font(u[0].paragraphs[0].runs[0], size=11, bold=True)
    set_font(u[1].paragraphs[0].runs[0], size=11, bold=True)
    set_font(u[2].paragraphs[0].runs[0], size=11, bold=True)
    u[0].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    u[2].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Row 11: 4.1 Methodology
    u = get_unique_cells(t0.rows[11])
    u[1].text = "4.1"
    u[2].text = "Selected Methodology or Process Model"
    u[3].text = "10"
    set_font(u[1].paragraphs[0].runs[0], size=10.5, bold=False)
    set_font(u[2].paragraphs[0].runs[0], size=10.5, bold=False)
    set_font(u[3].paragraphs[0].runs[0], size=10.5, bold=False)
    u[1].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    u[3].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Row 12: 4.2 Architecture
    u = get_unique_cells(t0.rows[12])
    u[1].text = "4.2"
    u[2].text = "Architecture / Overall Design of Proposed System"
    u[3].text = "11"
    set_font(u[1].paragraphs[0].runs[0], size=10.5, bold=False)
    set_font(u[2].paragraphs[0].runs[0], size=10.5, bold=False)
    set_font(u[3].paragraphs[0].runs[0], size=10.5, bold=False)
    u[1].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    u[3].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Row 13: 4.3 Implementation & Testing Plan
    u = get_unique_cells(t0.rows[13])
    u[1].text = "4.3"
    u[2].text = "Description of Software Implementation and Testing Plan"
    u[3].text = "13"
    set_font(u[1].paragraphs[0].runs[0], size=10.5, bold=False)
    set_font(u[2].paragraphs[0].runs[0], size=10.5, bold=False)
    set_font(u[3].paragraphs[0].runs[0], size=10.5, bold=False)
    u[1].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    u[3].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Row 14: 4.4, 4.5, 4.6
    u = get_unique_cells(t0.rows[14])
    u[1].text = "4.4\n4.5\n4.6"
    u[2].text = "Project Management Plan\nFinancial Report on Estimated Costing\nTransition / Software to Operations Plan"
    u[3].text = "17\n18\n18"
    for r in u[1].paragraphs[0].runs:
        set_font(r, size=10.5, bold=False)
    for r in u[2].paragraphs[0].runs:
        set_font(r, size=10.5, bold=False)
    for r in u[3].paragraphs[0].runs:
        set_font(r, size=10.5, bold=False)
    u[1].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    u[3].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Row 15: REFERENCES
    u = get_unique_cells(t0.rows[15])
    u[1].text = "REFERENCES"
    u[2].text = "19"
    set_font(u[1].paragraphs[0].runs[0], size=11, bold=True)
    set_font(u[2].paragraphs[0].runs[0], size=11, bold=True)
    u[2].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

    # 2. Update List of Figures (remove numPr and set tab stops)
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
        # remove numPr
        numPr = p._p.xpath('.//w:numPr')
        for np in numPr:
            np.getparent().remove(np)
        p.text = f"{f_num}\t{f_title}\t{f_page}"
        for r in p.runs:
            set_font(r, size=11, bold=False)
            
    # 3. Update Table 1 (List of Tables)
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
    for i in range(1, 4):
        num, name, page = tables_data[i-1]
        t1.rows[i].cells[0].text = num
        t1.rows[i].cells[1].text = name
        t1.rows[i].cells[2].text = page
        for c in t1.rows[i].cells:
            for r in c.paragraphs[0].runs:
                set_font(r, size=10.5, bold=False)
            c.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER if c != t1.rows[i].cells[1] else WD_ALIGN_PARAGRAPH.LEFT
            
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

    # 4. Remove empty paragraphs in front matter that cause page spills
    empty_to_remove = []
    # between TOC and List of Figures
    for i in range(130, 146):
        p = doc.paragraphs[i]
        if not p.text.strip() and not p._p.xpath('.//w:sectPr'):
            empty_to_remove.append(p)
            
    # after List of Figures before List of Tables
    for i in range(160, 194):
        p = doc.paragraphs[i]
        if not p.text.strip() and not p._p.xpath('.//w:sectPr'):
            empty_to_remove.append(p)
            
    # after List of Tables before P240
    for i in range(195, 240):
        p = doc.paragraphs[i]
        if not p.text.strip() and not p._p.xpath('.//w:sectPr'):
            empty_to_remove.append(p)
            
    for p in empty_to_remove:
        try:
            p._p.getparent().remove(p._p)
        except Exception:
            pass

    doc.save(DOCX_PATH)
    print("Saved updated document. Measuring Word & PDF statistics...")

    word = win32com.client.Dispatch("Word.Application")
    word.Visible = False
    wdoc = word.Documents.Open(os.path.abspath(DOCX_PATH))
    wdoc.Fields.Update()
    pages = wdoc.ComputeStatistics(2)
    words = wdoc.ComputeStatistics(0)
    print(f"Final Word Page Count: {pages} pages")
    print(f"Final Word Word Count: {words} words")
    wdoc.SaveAs(os.path.abspath(PDF_PATH), 17)
    wdoc.Close(False)
    word.Quit()

    pdf = pymupdf.open(PDF_PATH)
    print(f"Final PDF Page Count: {len(pdf)} pages")
    for i, page in enumerate(pdf):
        lines = [l.strip() for l in page.get_text().splitlines() if l.strip()]
        first_2 = lines[:2] if len(lines) >= 2 else lines
        print(f"Page {i+1:02d}: {first_2}")

if __name__ == "__main__":
    fix_all_front_matter()
