import docx

doc = docx.Document(r"D:\Professional Training I template-1 (1).docx")

for i, t in enumerate(doc.tables):
    print(f"\n--- TABLE {i} ---")
    for r_i, r in enumerate(t.rows):
        print(f"Row {r_i}: {[c.text.strip() for c in r.cells]}")
