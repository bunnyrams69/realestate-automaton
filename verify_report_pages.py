import os
import win32com.client
import pymupdf

DOCX_PATH = r"E:\Real Estate-Ai_Automation\Professional_Training_I_Real_Estate_AI_Automation_Report.docx"
PDF_PATH = r"E:\Real Estate-Ai_Automation\Professional_Training_I_Real_Estate_AI_Automation_Report.pdf"

print("Opening Word Application via COM...")
word = win32com.client.Dispatch("Word.Application")
word.Visible = False

try:
    doc = word.Documents.Open(os.path.abspath(DOCX_PATH))
    doc.Fields.Update()
    
    # Compute Statistics
    page_count = doc.ComputeStatistics(2) # 2 = wdStatisticPages
    word_count = doc.ComputeStatistics(0) # 0 = wdStatisticWords
    print(f"Word Document Statistics:")
    print(f"  Exact Page Count: {page_count} pages")
    print(f"  Word Count: {word_count} words")
    
    # Save as PDF
    print(f"Exporting to PDF: {PDF_PATH}...")
    doc.SaveAs(os.path.abspath(PDF_PATH), 17) # 17 = wdFormatPDF
    doc.Close(False)
finally:
    word.Quit()

print("Inspecting PDF layout via PyMuPDF...")
pdf = pymupdf.open(PDF_PATH)
print(f"Total PDF Pages: {len(pdf)}")

print("\n--- Page by Page Overview ---")
for i, page in enumerate(pdf):
    text = page.get_text()
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    first_3 = lines[:3] if len(lines) >= 3 else lines
    last_2 = lines[-2:] if len(lines) >= 2 else lines
    print(f"Page {i+1:02d}: Starts with {first_3} | Ends with {last_2}")

print("\nFinding Chapter & Section start pages:")
for i, page in enumerate(pdf):
    text = page.get_text()
    for marker in ["CHAPTER 1", "CHAPTER 2", "CHAPTER 3", "CHAPTER 4", "REFERENCES", "4.1", "4.2", "4.3", "4.4", "4.5", "4.6", "3.1", "3.2", "3.3"]:
        if marker in text:
            print(f"  {marker} detected on Page {i+1}")
