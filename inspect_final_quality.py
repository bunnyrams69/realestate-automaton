import docx
import pymupdf
import re

DOCX_PATH = "Professional_Training_I_Real_Estate_AI_Automation_Report.docx"
PDF_PATH = "Professional_Training_I_Real_Estate_AI_Automation_Report.pdf"

print("==================== FINAL QUALITY AUDIT ====================")

# 1. Inspect DOCX structure
doc = docx.Document(DOCX_PATH)
print(f"Total Paragraphs: {len(doc.paragraphs)}")
print(f"Total Tables: {len(doc.tables)}")
print(f"Total Sections: {len(doc.sections)}")

# 2. Check for banned/sample remnants
banned_words = ["Neural Consensus", "NCIO", "Azure ML Studio", "Dalta Tarun", "TARUN", "Maven"]
found_banned = {}
for i, p in enumerate(doc.paragraphs):
    for w in banned_words:
        if w.lower() in p.text.lower():
            found_banned.setdefault(w, []).append(f"P{i}: {p.text[:60]}")

print("\n--- Banned Sample Project Text Check ---")
if found_banned:
    for w, locs in found_banned.items():
        print(f"  WARNING: Found '{w}' at: {locs}")
else:
    print("  PASS: Zero occurrences of sample project keywords found!")

# 3. Check Abstract format
print("\n--- Abstract Compliance Check ---")
# Abstract is P116
abs_p = doc.paragraphs[116]
abs_text = abs_p.text.strip()
word_count = len(abs_text.split())
print(f"  Abstract Word Count: {word_count} words")
print(f"  Abstract starts with: '{abs_text[:60]}...'")
print(f"  Abstract ends with: '...{abs_text[-60:]}'")
print(f"  Abstract has bullets: {'•' in abs_text or '*' in abs_text}")
print(f"  Abstract line breaks: {'\n' in abs_text}")

# 4. Check References compliance
print("\n--- References Compliance Check ---")
ref_paragraphs = []
in_ref = False
for p in doc.paragraphs:
    if p.text.strip() == "REFERENCES":
        in_ref = True
        continue
    if in_ref and p.text.strip():
        ref_paragraphs.append(p.text.strip())

print(f"  Total References Found: {len(ref_paragraphs)}")
url_pattern = re.compile(r'https?://|www\.|\.org/|\.com/|doi\.org')
found_urls = []
first_authors = []
for idx, r in enumerate(ref_paragraphs, 1):
    if url_pattern.search(r):
        found_urls.append((idx, r))
    # extract author
    match = re.match(r'\[\d+\]\s+([A-Za-z]+)', r)
    if match:
        first_authors.append(match.group(1))

if found_urls:
    print(f"  WARNING: Found URLs in references: {found_urls}")
else:
    print("  PASS: Zero website references or URLs found in References section!")

print(f"  First author surnames: {first_authors}")
is_sorted = first_authors == sorted(first_authors)
print(f"  PASS: Alphabetically sorted: {is_sorted}")

# 5. Check PDF Page count and footer numbering
print("\n--- PDF Pages and Numbering Check ---")
pdf = pymupdf.open(PDF_PATH)
print(f"  Total PDF Pages: {len(pdf)} (Target: 25 to 30 pages)")
assert 25 <= len(pdf) <= 30, f"Page count {len(pdf)} out of bounds!"
print(f"  PASS: Page count strictly within [25, 30] boundary!")

for i, page in enumerate(pdf):
    text = page.get_text()
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    num_indicator = lines[0] if lines else "EMPTY"
    print(f"  Page {i+1:02d}: Indicator = '{num_indicator}'")

print("\n==================== AUDIT COMPLETE ====================")
