import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls, qn

doc = docx.Document("Professional_Training_I_Real_Estate_AI_Automation_Report.docx")

def set_font(run, size=11, bold=False):
    run.font.name = "Arial"
    run.font.size = Pt(size)
    run.bold = bold
    rPr = run._r.get_or_add_rPr()
    rFonts = rPr.find(qn('w:rFonts'))
    if rFonts is None:
        rFonts = parse_xml(f'<w:rFonts {nsdecls("w")} w:ascii="Arial" w:hAnsi="Arial" w:cs="Arial"/>')
        rPr.insert(0, rFonts)
    else:
        rFonts.set(qn('w:ascii'), 'Arial')
        rFonts.set(qn('w:hAnsi'), 'Arial')
        rFonts.set(qn('w:cs'), 'Arial')

# Inspect Table 0
t0 = doc.tables[0]
print(f"Table 0 rows: {len(t0.rows)}")
for i, r in enumerate(t0.rows):
    print(i, [c.text.strip() for c in r.cells])

# Inspect Table 1
t1 = doc.tables[1]
print(f"\nTable 1 rows: {len(t1.rows)}")
for i, r in enumerate(t1.rows):
    print(i, [c.text.strip() for c in r.cells])
