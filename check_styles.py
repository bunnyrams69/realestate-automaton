import docx

doc = docx.Document(r"D:\Professional Training I template-1 (1).docx")

print("Checking styles...")
for s in doc.styles:
    if s.type == docx.enum.style.WD_STYLE_TYPE.PARAGRAPH:
        if any(h in s.name.lower() for h in ['head', 'normal', 'body', 'title', 'list', 'table']):
            font = s.font
            print(f"Style: {s.name:25} | Font: {font.name} | Size: {font.size.pt if font.size else 'None'} | Bold: {font.bold}")

print("\nChecking margins of sections...")
for i, sec in enumerate(doc.sections):
    print(f"Sec {i}: top={sec.top_margin.inches:.2f}in, bot={sec.bottom_margin.inches:.2f}in, left={sec.left_margin.inches:.2f}in, right={sec.right_margin.inches:.2f}in, w={sec.page_width.inches:.2f}in, h={sec.page_height.inches:.2f}in")
