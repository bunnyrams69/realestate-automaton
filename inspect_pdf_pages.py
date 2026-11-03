import fitz

doc = fitz.open("template_preview.pdf")
print("Total PDF pages in template:", len(doc))

for i, page in enumerate(doc):
    text = page.get_text()
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    first_few = " | ".join(lines[:4]) if lines else "[EMPTY PAGE]"
    print(f"Page {i+1:02d} ({len(lines)} lines): {first_few[:120]}")
