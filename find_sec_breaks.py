import docx

doc = docx.Document(r"D:\Professional Training I template-1 (1).docx")

# To find where sections split paragraphs, let's look at paragraph elements and sectPr
p_sec = []
current_sec = 0

for i, p in enumerate(doc.paragraphs):
    # check if p has sectPr in its pPr
    pPr = p._p.pPr
    sectPr = pPr.find(docx.oxml.ns.qn('w:sectPr')) if pPr is not None else None
    if sectPr is not None:
        p_sec.append((current_sec, i, p.text[:30]))
        current_sec += 1

print("Section breaks found at paragraphs:")
for s_num, p_idx, text in p_sec:
    print(f"Sec {s_num} ends at P{p_idx:03d}: text={repr(text)}")
print(f"Sec {current_sec} ends at document body end (P{len(doc.paragraphs)-1})")
