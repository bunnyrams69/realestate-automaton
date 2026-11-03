import docx

doc = docx.Document(r"D:\Professional Training I template-1 (1).docx")

for idx in [8, 9, 10]:
    sec = doc.sections[idx]
    print(f"\n--- Section {idx} ---")
    print(f"Start type: {sec.start_type}")
    print(f"Page width: {sec.page_width}, height: {sec.page_height}")
    print(f"Margins: top={sec.top_margin}, bot={sec.bottom_margin}, left={sec.left_margin}, right={sec.right_margin}")
    print(f"Header: {[p.text for p in sec.header.paragraphs]}")
    print(f"Footer: {[p.text for p in sec.footer.paragraphs]}")
    f_p = sec.footer.paragraphs[0]
    print(f"Footer XML: {f_p._p.xml[:400]}")
