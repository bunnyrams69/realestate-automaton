import docx
import os

doc_path = r"D:\Professional Training I template-1 (1).docx"
doc = docx.Document(doc_path)

output_file = "template_analysis.txt"

with open(output_file, "w", encoding="utf-8") as f:
    f.write(f"TOTAL PARAGRAPHS: {len(doc.paragraphs)}\n")
    f.write(f"TOTAL TABLES: {len(doc.tables)}\n")
    f.write(f"TOTAL SECTIONS: {len(doc.sections)}\n\n")

    f.write("=== SECTIONS ===\n")
    for s_idx, sec in enumerate(doc.sections):
        f.write(f"Section {s_idx}: start_type={sec.start_type}, orientation={sec.orientation}, page_w={sec.page_width}, page_h={sec.page_height}, top_m={sec.top_margin}, bot_m={sec.bottom_margin}, left_m={sec.left_margin}, right_m={sec.right_margin}\n")
        f.write(f"  header paragraphs: {len(sec.header.paragraphs)}, footer paragraphs: {len(sec.footer.paragraphs)}\n")
        for hp in sec.header.paragraphs:
            if hp.text.strip():
                f.write(f"    header: {hp.text.strip()}\n")
        for fp in sec.footer.paragraphs:
            if fp.text.strip():
                f.write(f"    footer: {fp.text.strip()}\n")

    f.write("\n=== PARAGRAPHS ===\n")
    for i, p in enumerate(doc.paragraphs):
        text = p.text.strip()
        align = p.alignment
        runs_count = len(p.runs)
        f.write(f"P{i:03d} | Style: {p.style.name:20} | Align: {str(align):10} | Runs: {runs_count:2d} | Text: {p.text}\n")

    f.write("\n=== TABLES ===\n")
    for t_idx, table in enumerate(doc.tables):
        f.write(f"\nTable {t_idx} ({len(table.rows)} rows x {len(table.columns)} cols):\n")
        for r_idx, row in enumerate(table.rows):
            row_text = [cell.text.replace("\n", " ").strip() for cell in row.cells]
            f.write(f"  Row {r_idx:02d}: {' | '.join(row_text)}\n")

print(f"Analysis saved to {output_file}")
