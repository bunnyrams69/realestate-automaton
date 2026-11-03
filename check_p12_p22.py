import docx

doc = docx.Document(r"D:\Professional Training I template-1 (1).docx")

for p_idx in [12, 22]:
    p = doc.paragraphs[p_idx]
    xml = p._p.xml
    print(f"P{p_idx} XML:")
    print(xml[:500])
