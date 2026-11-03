import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn
import lxml.etree as etree

TEMPLATE_PATH = r"D:\Professional Training I template-1 (1).docx"
OUTPUT_PATH = r"E:\Real Estate-Ai_Automation\Professional_Training_I_Real_Estate_AI_Automation_Report.docx"
FIG_DIR = r"E:\Real Estate-Ai_Automation\figures"

def set_run_font(run, name="Arial", size_pt=12, bold=False, italic=False, color_rgb=(0,0,0)):
    run.font.name = name
    run.font.size = Pt(size_pt)
    run.bold = bold
    run.italic = italic
    if color_rgb:
        run.font.color.rgb = RGBColor(*color_rgb)
    rPr = run._r.get_or_add_rPr()
    rFonts = rPr.find(qn('w:rFonts'))
    if rFonts is None:
        rFonts = parse_xml(f'<w:rFonts {nsdecls("w")} w:ascii="{name}" w:hAnsi="{name}" w:cs="{name}"/>')
        rPr.insert(0, rFonts)
    else:
        rFonts.set(qn('w:ascii'), name)
        rFonts.set(qn('w:hAnsi'), name)
        rFonts.set(qn('w:cs'), name)

def add_academic_heading(doc, text, level=1, space_before=12, space_after=6):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.keep_with_next = True
    
    run = p.add_run(text)
    if level == 1:
        set_run_font(run, name="Arial", size_pt=14, bold=True, color_rgb=(0, 32, 96))
    elif level == 2:
        set_run_font(run, name="Arial", size_pt=12.5, bold=True, color_rgb=(15, 60, 130))
    elif level == 3:
        set_run_font(run, name="Arial", size_pt=12, bold=True, italic=True, color_rgb=(30, 30, 30))
    return p

def add_body_paragraph(doc, text, space_after=6, line_spacing=1.15, bold_prefix=None):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = line_spacing
    
    if bold_prefix:
        r_pre = p.add_run(bold_prefix)
        set_run_font(r_pre, name="Arial", size_pt=12, bold=True)
    
    run = p.add_run(text)
    set_run_font(run, name="Arial", size_pt=12, bold=False)
    return p

def add_bullet_point(doc, bold_title, text, space_after=4):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.left_indent = Inches(0.25)
    
    r_bullet = p.add_run("•  ")
    set_run_font(r_bullet, name="Arial", size_pt=12, bold=True, color_rgb=(0, 51, 102))
    
    if bold_title:
        r_title = p.add_run(bold_title + ": ")
        set_run_font(r_title, name="Arial", size_pt=12, bold=True)
        
    run = p.add_run(text)
    set_run_font(run, name="Arial", size_pt=12, bold=False)
    return p

def add_figure_with_caption(doc, image_filename, caption_text, width_inches=5.8):
    image_path = os.path.join(FIG_DIR, image_filename)
    if not os.path.exists(image_path):
        print(f"Warning: image {image_path} not found!")
        return None
        
    p_img = doc.add_paragraph()
    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_img.paragraph_format.space_before = Pt(8)
    p_img.paragraph_format.space_after = Pt(4)
    p_img.paragraph_format.keep_with_next = True
    
    run_img = p_img.add_run()
    run_img.add_picture(image_path, width=Inches(width_inches))
    
    p_cap = doc.add_paragraph()
    p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cap.paragraph_format.space_before = Pt(2)
    p_cap.paragraph_format.space_after = Pt(10)
    p_cap.paragraph_format.keep_with_next = False
    
    # split caption into label and description if has colon
    parts = caption_text.split(":", 1)
    if len(parts) == 2:
        r_lbl = p_cap.add_run(parts[0] + ":")
        set_run_font(r_lbl, name="Arial", size_pt=10.5, bold=True, color_rgb=(0, 32, 96))
        r_desc = p_cap.add_run(parts[1])
        set_run_font(r_desc, name="Arial", size_pt=10.5, italic=True)
    else:
        run = p_cap.add_run(caption_text)
        set_run_font(run, name="Arial", size_pt=10.5, bold=True)
    return p_cap

def set_cell_margins(cell, top=100, bottom=100, left=120, right=120):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def set_cell_shading(cell, fill_hex="F0F4F8"):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_borders(cell, top="single", bottom="single", left="none", right="none", 
                     color="CCCCCC", sz="4"):
    tcPr = cell._tc.get_or_add_tcPr()
    borders_xml = f'<w:tcBorders {nsdecls("w")}>'
    borders_xml += f'<w:top w:val="{top}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
    borders_xml += f'<w:left w:val="{left}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
    borders_xml += f'<w:bottom w:val="{bottom}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
    borders_xml += f'<w:right w:val="{right}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
    borders_xml += '</w:tcBorders>'
    tcPr.append(parse_xml(borders_xml))

def create_styled_table(doc, headers, data, col_widths, caption_text):
    # Caption
    p_cap = doc.add_paragraph()
    p_cap.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_cap.paragraph_format.space_before = Pt(8)
    p_cap.paragraph_format.space_after = Pt(3)
    p_cap.paragraph_format.keep_with_next = True
    
    parts = caption_text.split(":", 1)
    if len(parts) == 2:
        r_lbl = p_cap.add_run(parts[0] + ":")
        set_run_font(r_lbl, name="Arial", size_pt=10.5, bold=True, color_rgb=(0, 32, 96))
        r_desc = p_cap.add_run(parts[1])
        set_run_font(r_desc, name="Arial", size_pt=10.5, bold=True)
    else:
        run = p_cap.add_run(caption_text)
        set_run_font(run, name="Arial", size_pt=10.5, bold=True)
        
    table = doc.add_table(rows=len(data) + 1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    
    # Style header row
    hdr_row = table.rows[0]
    hdr_row._tr.get_or_add_trPr().append(parse_xml(f'<w:tblHeader {nsdecls("w")}/>'))
    
    for i, title in enumerate(headers):
        cell = hdr_row.cells[i]
        cell.width = Inches(col_widths[i])
        set_cell_shading(cell, "003366")
        set_cell_margins(cell, top=100, bottom=100, left=120, right=120)
        set_cell_borders(cell, top="single", bottom="single", left="single", right="single", color="002244", sz="6")
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        run = p.add_run(title)
        set_run_font(run, name="Arial", size_pt=9.5, bold=True, color_rgb=(255, 255, 255))
        
    # Style data rows
    for r_idx, row_data in enumerate(data):
        row = table.rows[r_idx + 1]
        bg_fill = "F7F9FB" if r_idx % 2 == 1 else "FFFFFF"
        for c_idx, cell_value in enumerate(row_data):
            cell = row.cells[c_idx]
            cell.width = Inches(col_widths[c_idx])
            set_cell_shading(cell, bg_fill)
            set_cell_margins(cell, top=80, bottom=80, left=100, right=100)
            set_cell_borders(cell, top="single", bottom="single", left="single", right="single", color="D0D7DE", sz="4")
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if c_idx > 0 and len(cell_value) > 10 else WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.05
            run = p.add_run(cell_value)
            set_run_font(run, name="Arial", size_pt=9.0, bold=(c_idx == 0))
            
    p_spacer = doc.add_paragraph()
    p_spacer.paragraph_format.space_before = Pt(0)
    p_spacer.paragraph_format.space_after = Pt(6)
    return table

print("Base helper functions defined successfully.")
