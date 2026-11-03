import docx

doc = docx.Document(r"D:\Professional Training I template-1 (1).docx")

for s_idx, sec in enumerate(doc.sections):
    sectPr = sec._sectPr
    pnt = sectPr.find(docx.oxml.ns.qn('w:pgNumType'))
    if pnt is not None:
        print(f"Sec {s_idx} pgNumType: {pnt.attrib}")
    else:
        print(f"Sec {s_idx} pgNumType: None (continues from previous)")
