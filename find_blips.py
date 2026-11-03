import docx

doc = docx.Document(r"D:\Professional Training I template-1 (1).docx")

for i, p in enumerate(doc.paragraphs):
    if "a:blip" in p._p.xml or "w:drawing" in p._p.xml:
        # check specifically for blip
        if "a:blip" in p._p.xml:
            print(f"P{i:03d} has image blip! Text: {repr(p.text)}")

for t_idx, t in enumerate(doc.tables):
    for r_idx, r in enumerate(t.rows):
        for c_idx, c in enumerate(r.cells):
            if "a:blip" in c._tc.xml:
                print(f"Table {t_idx} R{r_idx} C{c_idx} has image blip! Text: {repr(c.text)}")
