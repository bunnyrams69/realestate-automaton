import docx

doc = docx.Document(r"D:\Professional Training I template-1 (1).docx")

for s_idx, sec in enumerate(doc.sections):
    f = sec.footer
    instr = [e.text for e in f._element.iter() if e.tag.endswith('instrText')]
    texts = [e.text for e in f._element.iter() if e.tag.endswith('}t')]
    print(f"Sec {s_idx}: instr={instr}, texts={texts}")
