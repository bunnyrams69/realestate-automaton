import win32com.client
import os
import fitz

word = win32com.client.Dispatch("Word.Application")
word.Visible = False
word.DisplayAlerts = 0

doc_path = os.path.abspath(r"temp.docx")
pdf_path = os.path.abspath(r"temp.pdf")
if os.path.exists(pdf_path):
    os.remove(pdf_path)

doc = word.Documents.Open(FileName=doc_path, ConfirmConversions=False, ReadOnly=True, AddToRecentFiles=False)
doc.ExportAsFixedFormat(pdf_path, ExportFormat=17) # wdExportFormatPDF = 17
doc.Close(False)
word.Quit(0)

pdf = fitz.open(pdf_path)
print("Actual PDF page count:", len(pdf))
for i in range(min(5, len(pdf))):
    print(f"Page {i+1} first line:", repr(pdf[i].get_text().splitlines()[:2]))
