import fitz

doc = fitz.open("template_preview.pdf")

for i in range(12):
    page = doc[i]
    blocks = page.get_text("blocks")
    print(f"--- Page {i+1} blocks ---")
    for b in blocks[:3]:
        print(f"  bbox={b[:4]}: {repr(b[4].strip())}")
