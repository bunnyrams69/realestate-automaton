import win32com.client
import os

word = win32com.client.Dispatch("Word.Application")
word.Visible = False

doc_path = os.path.abspath(r"D:\Professional Training I template-1 (1).docx")
doc = word.Documents.Open(doc_path)

try:
    page_count = doc.ComputeStatistics(2) # 2 = wdStatisticPages
    print("Word page count:", page_count)
    
    # Check sections
    print("Section count:", doc.Sections.Count)
    for i in range(1, doc.Sections.Count + 1):
        sec = doc.Sections(i)
        print(f"Section {i}: Start={sec.PageSetup.SectionStart}")
finally:
    doc.Close(False)
    word.Quit()
