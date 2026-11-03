import pymupdf

pdf = pymupdf.open("Professional_Training_I_Real_Estate_AI_Automation_Report.pdf")

for page_num in range(1, 12):
    page = pdf[page_num - 1]
    print(f"\n==================== PAGE {page_num} ====================")
    text = page.get_text()
    for line in text.splitlines():
        if line.strip():
            print("  ", line.strip())
