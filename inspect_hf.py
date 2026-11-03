import docx

doc = docx.Document(r"D:\Professional Training I template-1 (1).docx")

print(f"Total sections: {len(doc.sections)}")
for s_idx, sec in enumerate(doc.sections):
    print(f"\n--- Section {s_idx} ---")
    print(f"Start type: {sec.start_type}")
    print(f"Different first page: {sec.different_first_page_header_footer}")
    print(f"Header: {[p.text for p in sec.header.paragraphs if p.text.strip()]}")
    print(f"Footer: {[p.text for p in sec.footer.paragraphs if p.text.strip()]}")
    
    # check footer xml for page number fields
    for fp in sec.footer.paragraphs:
        if "w:fldSimple" in fp._p.xml or "w:instrText" in fp._p.xml:
            print(f"  Footer contains page field! XML snippet: {fp._p.xml[:300]}")
