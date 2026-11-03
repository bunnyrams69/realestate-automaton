import pymupdf

orig_pdf = pymupdf.open("template_preview.pdf")
our_pdf = pymupdf.open("Professional_Training_I_Real_Estate_AI_Automation_Report.pdf")

print(f"Original PDF Pages: {len(orig_pdf)}")
print(f"Our PDF Pages: {len(our_pdf)}")

print("\n--- Comparing Page Headers / Titles ---")
for i in range(min(12, len(orig_pdf), len(our_pdf))):
    p_orig = orig_pdf[i]
    p_our = our_pdf[i]
    lines_orig = [l.strip() for l in p_orig.get_text().splitlines() if l.strip()]
    lines_our = [l.strip() for l in p_our.get_text().splitlines() if l.strip()]
    
    t_orig = lines_orig[1] if len(lines_orig) > 1 else (lines_orig[0] if lines_orig else "")
    t_our = lines_our[1] if len(lines_our) > 1 else (lines_our[0] if lines_our else "")
    
    print(f"Page {i+1:02d}: Orig -> {t_orig[:40]:40s} | Our -> {t_our[:40]}")
