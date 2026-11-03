import docx

doc = docx.Document(r"D:\Professional Training I template-1 (1).docx")

print(f"Total paragraphs: {len(doc.paragraphs)}")
for i in range(240, 280):
    p = doc.paragraphs[i]
    print(f"P{i:03d} [{p.style.name}]: {repr(p.text[:60])}")
