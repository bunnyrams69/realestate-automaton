import docx
from lxml import etree

doc = docx.Document(r"D:\Professional Training I template-1 (1).docx")

# Let's inspect P240 pPr sectPr
p240 = doc.paragraphs[240]
sectPr = p240._p.pPr.find(docx.oxml.ns.qn('w:sectPr'))
if sectPr is not None:
    print("P240 sectPr:", etree.tostring(sectPr, encoding='utf-8').decode('utf-8'))

body_sectPr = doc._body._element.find(docx.oxml.ns.qn('w:sectPr'))
if body_sectPr is not None:
    print("\nBody sectPr:", etree.tostring(body_sectPr, encoding='utf-8').decode('utf-8'))
