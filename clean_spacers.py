import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls, qn
import win32com.client
import pymupdf

DOCX_PATH = r"E:\Real Estate-Ai_Automation\Professional_Training_I_Real_Estate_AI_Automation_Report.docx"
PDF_PATH = r"E:\Real Estate-Ai_Automation\Professional_Training_I_Real_Estate_AI_Automation_Report.pdf"

doc = docx.Document(DOCX_PATH)
body = doc._body._element

# Let's inspect paragraphs around TOC, Figures, Tables
# TOC is around P129. Let's see which paragraphs are empty between P130 and P145
print("Scanning empty paragraphs in front matter...")
empty_to_remove = []

# Empty paragraphs between P130 and P145 (after TOC heading before Section 7)
for i in range(130, 145):
    p = doc.paragraphs[i]
    if not p.text.strip() and not p._p.xpath('.//w:sectPr'):
        empty_to_remove.append(p)

# Empty paragraphs between P160 and P193 (after Figures before Section 8)
for i in range(160, 193):
    p = doc.paragraphs[i]
    if not p.text.strip() and not p._p.xpath('.//w:sectPr'):
        empty_to_remove.append(p)

# Empty paragraphs between P195 and P239 (around Table 1 before P240)
for i in range(195, 240):
    p = doc.paragraphs[i]
    if not p.text.strip() and not p._p.xpath('.//w:sectPr'):
        empty_to_remove.append(p)

print(f"Found {len(empty_to_remove)} empty spacer paragraphs to remove.")
for p in empty_to_remove:
    p._p.getparent().remove(p._p)

doc.save(DOCX_PATH)
print("Saved cleaned document. Checking Word page count...")

word = win32com.client.Dispatch("Word.Application")
word.Visible = False
wdoc = word.Documents.Open(os.path.abspath(DOCX_PATH))
wdoc.Fields.Update()
pages = wdoc.ComputeStatistics(2)
words = wdoc.ComputeStatistics(0)
print(f"New Word Page Count: {pages} pages")
wdoc.SaveAs(os.path.abspath(PDF_PATH), 17)
wdoc.Close(False)
word.Quit()

pdf = pymupdf.open(PDF_PATH)
print(f"New PDF Page Count: {len(pdf)} pages")

for i, page in enumerate(pdf):
    lines = [l.strip() for l in page.get_text().splitlines() if l.strip()]
    first_2 = lines[:2] if len(lines) >= 2 else lines
    print(f"Page {i+1:02d}: {first_2}")
