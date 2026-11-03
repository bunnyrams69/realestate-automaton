import docx

doc = docx.Document(r"D:\Professional Training I template-1 (1).docx")

for i, p in enumerate(doc.paragraphs):
    if "drawing" in p._p.xml:
        print(f"P{i:03d} contains a drawing/image! Text: {p.text[:50]}")
