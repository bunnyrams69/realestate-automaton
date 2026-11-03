import pymupdf

pdf = pymupdf.open("template_preview.pdf")

with open("orig_template_blocks.txt", "w", encoding="utf-8") as f:
    for i in range(len(pdf)):
        f.write(f"\n{'='*25} PAGE {i+1} {'='*25}\n")
        page = pdf[i]
        for b in page.get_text("blocks"):
            text = b[4].strip().replace("\n", " ")
            if text:
                f.write(f"bbox: ({b[0]:.1f}, {b[1]:.1f}, {b[2]:.1f}, {b[3]:.1f}) | {text[:80]}\n")

print("Done writing orig_template_blocks.txt")
