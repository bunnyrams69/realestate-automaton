import pymupdf

pdf = pymupdf.open("Professional_Training_I_Real_Estate_AI_Automation_Report.pdf")

with open("all_pages_text_utf8.txt", "w", encoding="utf-8") as f:
    for page_num in range(1, len(pdf) + 1):
        page = pdf[page_num - 1]
        f.write(f"\n{'='*30} PAGE {page_num:02d} {'='*30}\n")
        text = page.get_text()
        for line in text.splitlines():
            if line.strip():
                f.write(f"  {line.strip()}\n")

print("Done writing all_pages_text_utf8.txt")
