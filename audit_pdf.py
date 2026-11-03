import os
import pymupdf

pdf = pymupdf.open("Professional_Training_I_Real_Estate_AI_Automation_Report.pdf")
with open("pdf_layout_audit.txt", "w", encoding="utf-8") as out:
    out.write(f"Total Pages: {len(pdf)}\n\n")
    for i, page in enumerate(pdf):
        text = page.get_text()
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        out.write(f"==================== PAGE {i+1} ====================\n")
        out.write(f"Line count: {len(lines)}\n")
        if lines:
            out.write(f"First 5 lines: {lines[:5]}\n")
            out.write(f"Last 5 lines: {lines[-5:]}\n")
        out.write("\n")

print("Audit written to pdf_layout_audit.txt")
