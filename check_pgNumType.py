import docx

doc = docx.Document(r"D:\Professional Training I template-1 (1).docx")

for i, p in enumerate(doc.paragraphs):
    pPr = p._p.pPr
    sectPr = pPr.find(docx.oxml.ns.qn('w:sectPr')) if pPr is not None else None
    if sectPr is not None:
        pnt = sectPr.find(docx.oxml.ns.qn('w:pgNumType'))
        if pnt is not None:
            print(f"P{i:03d} pgNumType: {pnt.attrib}")

body_sectPr = doc._body._element.find(docx.oxml.ns.qn('w:sectPr'))
if body_sectPr is not None:
    pnt = body_sectPr.find(docx.oxml.ns.qn('w:pgNumType'))
    if pnt is not None:
        print(f"Body pgNumType: {pnt.attrib}")
