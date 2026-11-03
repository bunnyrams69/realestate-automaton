import docx

doc = docx.Document(r"D:\Professional Training I template-1 (1).docx")

for s_idx, sec in enumerate(doc.sections):
    f_xml = sec.footer.paragraphs[0]._p.xml
    print(f"Sec {s_idx} Footer XML (len {len(f_xml)}): {f_xml}")
