import docx
import pymupdf

doc_orig = docx.Document(r"D:\Professional Training I template-1 (1).docx")
doc_our = docx.Document(r"E:\Real Estate-Ai_Automation\Professional_Training_I_Real_Estate_AI_Automation_Report.docx")

print("--- Original Sections ---")
for i, s in enumerate(doc_orig.sections):
    print(f"Sec {i}: start_type={s.start_type}, top={s.top_margin.pt}, bottom={s.bottom_margin.pt}, left={s.left_margin.pt}, right={s.right_margin.pt}")

print("\n--- Our Sections ---")
for i, s in enumerate(doc_our.sections):
    print(f"Sec {i}: start_type={s.start_type}, top={s.top_margin.pt}, bottom={s.bottom_margin.pt}, left={s.left_margin.pt}, right={s.right_margin.pt}")
