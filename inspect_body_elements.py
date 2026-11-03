import docx

doc = docx.Document(r"D:\Professional Training I template-1 (1).docx")

body_elements = []
for child in doc._body._element:
    tag = child.tag.split('}')[-1]
    if tag == 'p':
        p = docx.text.paragraph.Paragraph(child, doc)
        body_elements.append(('p', p.text.strip()[:60]))
    elif tag == 'tbl':
        tbl = docx.table.Table(child, doc)
        body_elements.append(('tbl', f"Table with {len(tbl.rows)} rows x {len(tbl.columns)} cols: first cell={tbl.rows[0].cells[0].text.strip()[:30]}"))

for idx, (el_type, text) in enumerate(body_elements):
    if el_type == 'tbl' or any(keyword in text.upper() for keyword in ['CHAPTER', 'TABLE OF CONTENTS', 'ABSTRACT', 'BONAFIDE', 'DECLARATION', 'CERTIFICATE', 'LIST OF']):
        print(f"Elem {idx:03d} [{el_type}]: {text}")
