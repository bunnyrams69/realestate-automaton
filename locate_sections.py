import pymupdf

pdf = pymupdf.open("Professional_Training_I_Real_Estate_AI_Automation_Report.pdf")

# We want the Arabic page number (which is PDF page index - 9, because front matter is 9 pages: pages 1 to 9 are roman i to ix, and page 10 is arabic 1)
# Let's verify by checking the first line of text on each page
arabic_pages = {}
for i in range(9, len(pdf)):
    text = pdf[i].get_text()
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    pg_num = lines[0] # footer/header number
    arabic_pages[i + 1] = pg_num

print("PDF Page to Arabic Page mapping:")
for pdf_pg, ar_pg in arabic_pages.items():
    print(f"  PDF Page {pdf_pg} -> Arabic Page '{ar_pg}'")

print("\nLocating Sections:")
search_items = [
    ("CHAPTER 1", "CHAPTER 1 INTRODUCTION"),
    ("1.1", "1.1 Background"),
    ("1.2", "1.2 Problem Statement"),
    ("1.3", "1.3 Aim of the Project"),
    ("1.4", "1.4 Objectives"),
    ("1.5", "1.5 Scope of the Project"),
    ("1.6", "1.6 Significance and Expected Impact"),
    ("CHAPTER 2", "CHAPTER 2 LITERATURE SURVEY"),
    ("2.1", "2.1 Inferences from Literature Survey"),
    ("2.2", "2.2 Open Problems in Existing Systems"),
    ("CHAPTER 3", "CHAPTER 3 REQUIREMENTS ANALYSIS"),
    ("3.1", "3.1 Feasibility Studies / Risk Analysis"),
    ("3.2", "3.2 Software Requirements Specification Document"),
    ("3.3", "3.3 System Actors and Use Cases"),
    ("CHAPTER 4", "CHAPTER 4 DESCRIPTION OF PROPOSED SYSTEM"),
    ("4.1", "4.1 Selected Methodology or Process Model"),
    ("4.2", "4.2 Architecture / Overall Design of Proposed System"),
    ("4.3", "4.3 Description of Software Implementation and Testing Plan"),
    ("4.4", "4.4 Project Management Plan"),
    ("4.5", "4.5 Financial Report on Estimated Costing"),
    ("4.6", "4.6 Transition / Software to Operations Plan"),
    ("REFERENCES", "REFERENCES"),
    ("Fig 4.1", "Fig 4.1: End-to-End System Architecture"),
    ("Fig 4.2", "Fig 4.2: Asynchronous Real Estate Lead Ingestion"),
    ("Fig 4.3", "Fig 4.3: Multi-Parameter Dynamic Lead Qualification"),
    ("Fig 4.4", "Fig 4.4: Automated Site Visit Scheduling"),
    ("Fig 4.5", "Fig 4.5: Marketing Analytics and Ad Attribution"),
    ("Table 3.1", "Table 3.1: Risk Assessment Matrix"),
    ("Table 3.2", "Table 3.2: Hardware and Software Specifications"),
    ("Table 3.3", "Table 3.3: Functional Requirements"),
    ("Table 3.4", "Table 3.4: Non-Functional Requirements"),
    ("Table 3.5", "Table 3.5: Actor-to-Capability Use Case Matrix"),
    ("Table 4.1", "Table 4.1: Comprehensive System Testing Suite"),
    ("Table 4.2", "Table 4.2: Ten-Phase Engineering Roadmap"),
    ("Table 4.3", "Table 4.3: Financial Costing")
]

for label, title in search_items:
    found_pages = []
    for i, page in enumerate(pdf):
        if label in page.get_text():
            found_pages.append(i + 1)
    print(f"  {title:55s} -> PDF Pages: {found_pages}, Arabic Page: {[arabic_pages.get(p, 'Roman') for p in found_pages]}")
