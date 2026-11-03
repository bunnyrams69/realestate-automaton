import fitz

doc = fitz.open("template_preview.pdf")

with open("template_pdf_pages.txt", "w", encoding="utf-8") as f:
    for i, page in enumerate(doc):
        f.write(f"\n{'='*30} PAGE {i+1} {'='*30}\n")
        f.write(page.get_text())

print("Full text dumped to template_pdf_pages.txt")
