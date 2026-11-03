import win32com.client
import os

word = win32com.client.Dispatch("Word.Application")
word.Visible = False

doc_path = os.path.abspath(r"D:\Professional Training I template-1 (1).docx")
pdf_path = os.path.abspath(r"template_preview.pdf")

doc = word.Documents.Open(doc_path)
try:
    doc.SaveAs(pdf_path, 17) # 17 = wdFormatPDF
    print(f"Successfully converted template to PDF: {pdf_path}")
finally:
    doc.Close(False)
    word.Quit()
