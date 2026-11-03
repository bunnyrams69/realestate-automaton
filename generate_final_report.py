import os, sys, shutil
import docx
import fitz
import win32com.client

from report_content_frontmatter import update_frontmatter
from report_content_ch1 import build_chapter_1
from report_content_ch2 import build_chapter_2
from report_content_ch3 import build_chapter_3
from report_content_ch4 import build_chapter_4
from report_content_ch5 import build_chapter_5
from report_content_ch6 import build_chapter_6
from report_content_refs import build_references

SRC_DOC = r"D:\44110350 mohan.docx"
OUT_DOC = os.path.abspath(r"E:\Real Estate-Ai_Automation\Professional_Training_I_Real_Estate_AI_Automation_Report.docx")
OUT_PDF = os.path.abspath(r"E:\Real Estate-Ai_Automation\Professional_Training_I_Real_Estate_AI_Automation_Report.pdf")
FIG_PATH = os.path.abspath(r"E:\Real Estate-Ai_Automation\figures\fig_4_1_system_architecture.png")

def main():
    print("=== STEP 1: Copy base document ===")
    shutil.copyfile(SRC_DOC, OUT_DOC)
    
    print("=== STEP 2: Load document and update front matter ===")
    doc = docx.Document(OUT_DOC)
    update_frontmatter(doc)
    
    print("=== STEP 3: Clear old body content (elements 69 to len-2) ===")
    body = doc._body._element
    initial_len = len(body)
    print(f"Initial elements count: {initial_len}")
    
    # Remove all elements from index len(body)-2 down to 69
    for i in range(len(body) - 2, 68, -1):
        body.remove(body[i])
        
    print(f"Elements count after clearing body: {len(body)}")
    
    print("=== STEP 4: Build new chapters and references ===")
    build_chapter_1(doc)
    build_chapter_2(doc)
    build_chapter_3(doc)
    build_chapter_4(doc, FIG_PATH)
    build_chapter_5(doc)
    build_chapter_6(doc)
    build_references(doc)
    
    print(f"Final body elements count: {len(doc._body._element)}")
    print(f"Saving to {OUT_DOC}...")
    doc.save(OUT_DOC)
    print("Saved DOCX successfully!")
    
    print("=== STEP 5: Export to PDF via Word COM ===")
    word = win32com.client.Dispatch("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    try:
        wdoc = word.Documents.Open(FileName=OUT_DOC, ConfirmConversions=False, ReadOnly=False, AddToRecentFiles=False)
        wdoc.Fields.Update()
        pages = wdoc.ComputeStatistics(2)
        print(f"Word computed total pages: {pages}")
        
        if os.path.exists(OUT_PDF):
            os.remove(OUT_PDF)
            
        wdoc.ExportAsFixedFormat(OUT_PDF, ExportFormat=17) # wdExportFormatPDF = 17
        print(f"Exported PDF to {OUT_PDF}")
        wdoc.Close(False)
    finally:
        word.Quit(0)
        
    print("=== STEP 6: Verify with PyMuPDF ===")
    pdf = fitz.open(OUT_PDF)
    total_pages = len(pdf)
    print(f"Total pages in generated PDF: {total_pages}")
    
    for i, page in enumerate(pdf):
        lines = [l.strip() for l in page.get_text().splitlines() if l.strip()]
        header = ' | '.join(lines[:2]) if lines else '[EMPTY PAGE]'
        footer = lines[-1] if lines else ''
        safe_str = f"Page {i+1:2d} (footer: {footer:>4s}): {header[:80]}".encode('ascii', 'replace').decode('ascii')
        print(safe_str)

if __name__ == "__main__":
    main()
