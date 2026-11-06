from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor


ROOT = Path(r"C:\apps\kato")
OUT = ROOT / "deliverables" / "Briefing_Materiais_Site_Kato_Odontologia.docx"
LOGO = ROOT / "deliverables" / "logo_blue_cumprida.png"

# compact_reference_guide preset + named BlueDigital brand overrides.
FONT = "Calibri"
BRAND = "1739C6"
BRAND_DARK = "102A86"
NAVY = "101828"
TEXT = "344054"
MUTED = "667085"
LIGHT = "EFF3FF"
LIGHTER = "F8FAFC"
LINE = "D8E0F0"
TEAL = "0E7C86"
TEAL_LIGHT = "EAF7F7"
AMBER = "A15C00"
AMBER_LIGHT = "FFF4E5"
WHITE = "FFFFFF"

PAGE_WIDTH_DXA = 9360
TABLE_INDENT_DXA = 120
CELL_MARGINS = {"top": 100, "bottom": 100, "start": 140, "end": 140}


def rgb(hex_color: str) -> RGBColor:
    return RGBColor.from_string(hex_color)


def set_cell_shading(cell, fill: str):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = tc_pr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd")
        tc_pr.append(shd)
    shd.set(qn("w:fill"), fill)
    shd.set(qn("w:val"), "clear")


def set_cell_margins(cell, **kwargs):
    tc = cell._tc
    tc_pr = tc.get_or_add_tcPr()
    tc_mar = tc_pr.first_child_found_in("w:tcMar")
    if tc_mar is None:
        tc_mar = OxmlElement("w:tcMar")
        tc_pr.append(tc_mar)
    for margin in ["top", "start", "bottom", "end"]:
        if margin in kwargs:
            node = tc_mar.find(qn(f"w:{margin}"))
            if node is None:
                node = OxmlElement(f"w:{margin}")
                tc_mar.append(node)
            node.set(qn("w:w"), str(kwargs.get(margin)))
            node.set(qn("w:type"), "dxa")


def set_cell_border(cell, **edges):
    tc_pr = cell._tc.get_or_add_tcPr()
    tc_borders = tc_pr.first_child_found_in("w:tcBorders")
    if tc_borders is None:
        tc_borders = OxmlElement("w:tcBorders")
        tc_pr.append(tc_borders)
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        if edge not in edges:
            continue
        edge_data = edges[edge]
        tag = qn(f"w:{edge}")
        element = tc_borders.find(tag)
        if element is None:
            element = OxmlElement(f"w:{edge}")
            tc_borders.append(element)
        for key in ["val", "sz", "space", "color"]:
            if key in edge_data:
                element.set(qn(f"w:{key}"), str(edge_data[key]))


def set_repeat_table_header(row):
    tr_pr = row._tr.get_or_add_trPr()
    tbl_header = OxmlElement("w:tblHeader")
    tbl_header.set(qn("w:val"), "true")
    tr_pr.append(tbl_header)


def set_table_geometry(table, widths_dxa, indent_dxa=TABLE_INDENT_DXA):
    table.alignment = WD_TABLE_ALIGNMENT.LEFT
    table.autofit = False
    tbl_pr = table._tbl.tblPr

    tbl_w = tbl_pr.find(qn("w:tblW"))
    if tbl_w is None:
        tbl_w = OxmlElement("w:tblW")
        tbl_pr.append(tbl_w)
    tbl_w.set(qn("w:w"), str(sum(widths_dxa)))
    tbl_w.set(qn("w:type"), "dxa")

    tbl_ind = tbl_pr.find(qn("w:tblInd"))
    if tbl_ind is None:
        tbl_ind = OxmlElement("w:tblInd")
        tbl_pr.append(tbl_ind)
    tbl_ind.set(qn("w:w"), str(indent_dxa))
    tbl_ind.set(qn("w:type"), "dxa")

    tbl_layout = tbl_pr.find(qn("w:tblLayout"))
    if tbl_layout is None:
        tbl_layout = OxmlElement("w:tblLayout")
        tbl_pr.append(tbl_layout)
    tbl_layout.set(qn("w:type"), "fixed")

    old_grid = table._tbl.tblGrid
    for child in list(old_grid):
        old_grid.remove(child)
    for width in widths_dxa:
        grid_col = OxmlElement("w:gridCol")
        grid_col.set(qn("w:w"), str(width))
        old_grid.append(grid_col)

    for row in table.rows:
        for idx, cell in enumerate(row.cells):
            width = widths_dxa[min(idx, len(widths_dxa) - 1)]
            tc_pr = cell._tc.get_or_add_tcPr()
            tc_w = tc_pr.find(qn("w:tcW"))
            if tc_w is None:
                tc_w = OxmlElement("w:tcW")
                tc_pr.append(tc_w)
            tc_w.set(qn("w:w"), str(width))
            tc_w.set(qn("w:type"), "dxa")
            set_cell_margins(cell, **CELL_MARGINS)
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER


def font_run(run, size=None, color=TEXT, bold=None, italic=None, name=FONT):
    run.font.name = name
    run._element.get_or_add_rPr().rFonts.set(qn("w:ascii"), name)
    run._element.get_or_add_rPr().rFonts.set(qn("w:hAnsi"), name)
    run._element.get_or_add_rPr().rFonts.set(qn("w:eastAsia"), name)
    if size is not None:
        run.font.size = Pt(size)
    if color:
        run.font.color.rgb = rgb(color)
    if bold is not None:
        run.bold = bold
    if italic is not None:
        run.italic = italic


def paragraph_border_bottom(paragraph, color=BRAND, size=14, space=6):
    p_pr = paragraph._p.get_or_add_pPr()
    p_bdr = p_pr.find(qn("w:pBdr"))
    if p_bdr is None:
        p_bdr = OxmlElement("w:pBdr")
        p_pr.append(p_bdr)
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), str(size))
    bottom.set(qn("w:space"), str(space))
    bottom.set(qn("w:color"), color)
    p_bdr.append(bottom)


def set_keep_with_next(paragraph, keep=True):
    p_pr = paragraph._p.get_or_add_pPr()
    tag = p_pr.find(qn("w:keepNext"))
    if keep and tag is None:
        tag = OxmlElement("w:keepNext")
        p_pr.append(tag)
    elif not keep and tag is not None:
        p_pr.remove(tag)


def set_keep_together(paragraph, keep=True):
    p_pr = paragraph._p.get_or_add_pPr()
    tag = p_pr.find(qn("w:keepLines"))
    if keep and tag is None:
        tag = OxmlElement("w:keepLines")
        p_pr.append(tag)


def add_page_field(paragraph):
    run = paragraph.add_run()
    begin = OxmlElement("w:fldChar")
    begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = " PAGE "
    separate = OxmlElement("w:fldChar")
    separate.set(qn("w:fldCharType"), "separate")
    text = OxmlElement("w:t")
    text.text = "1"
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    run._r.extend([begin, instr, separate, text, end])
    font_run(run, size=8.5, color=MUTED)


def add_image_alt(inline_shape, title, description):
    doc_pr = inline_shape._inline.docPr
    doc_pr.set("title", title)
    doc_pr.set("descr", description)


def add_custom_numbering(doc):
    numbering = doc.part.numbering_part.element
    existing_abs = [int(x.get(qn("w:abstractNumId"))) for x in numbering.findall(qn("w:abstractNum"))]
    existing_num = [int(x.get(qn("w:numId"))) for x in numbering.findall(qn("w:num"))]
    abstract_base = max(existing_abs or [0]) + 1
    num_base = max(existing_num or [0]) + 1

    def make(abstract_id, num_id, fmt, text):
        abstract = OxmlElement("w:abstractNum")
        abstract.set(qn("w:abstractNumId"), str(abstract_id))
        multi = OxmlElement("w:multiLevelType")
        multi.set(qn("w:val"), "singleLevel")
        abstract.append(multi)
        lvl = OxmlElement("w:lvl")
        lvl.set(qn("w:ilvl"), "0")
        start = OxmlElement("w:start")
        start.set(qn("w:val"), "1")
        num_fmt = OxmlElement("w:numFmt")
        num_fmt.set(qn("w:val"), fmt)
        lvl_text = OxmlElement("w:lvlText")
        lvl_text.set(qn("w:val"), text)
        jc = OxmlElement("w:lvlJc")
        jc.set(qn("w:val"), "left")
        p_pr = OxmlElement("w:pPr")
        tabs = OxmlElement("w:tabs")
        tab = OxmlElement("w:tab")
        tab.set(qn("w:val"), "num")
        tab.set(qn("w:pos"), "540")
        tabs.append(tab)
        ind = OxmlElement("w:ind")
        ind.set(qn("w:left"), "540")
        ind.set(qn("w:hanging"), "270")
        spacing = OxmlElement("w:spacing")
        spacing.set(qn("w:after"), "80")
        spacing.set(qn("w:line"), "300")
        spacing.set(qn("w:lineRule"), "auto")
        p_pr.extend([tabs, ind, spacing])
        r_pr = OxmlElement("w:rPr")
        r_fonts = OxmlElement("w:rFonts")
        r_fonts.set(qn("w:ascii"), FONT)
        r_fonts.set(qn("w:hAnsi"), FONT)
        r_pr.append(r_fonts)
        lvl.extend([start, num_fmt, lvl_text, jc, p_pr, r_pr])
        abstract.append(lvl)

        num = OxmlElement("w:num")
        num.set(qn("w:numId"), str(num_id))
        ref = OxmlElement("w:abstractNumId")
        ref.set(qn("w:val"), str(abstract_id))
        num.append(ref)
        return abstract, num

    bullet_abs, bullet_num = make(abstract_base, num_base, "bullet", "•")
    decimal_abs, decimal_num = make(abstract_base + 1, num_base + 1, "decimal", "%1.")

    # OOXML requires all abstractNum definitions before the concrete num nodes.
    # Keeping that order prevents Word from repairing the package and mapping
    # the bullet list to the decimal definition.
    first_num_idx = next(
        (i for i, child in enumerate(numbering) if child.tag == qn("w:num")),
        len(numbering),
    )
    numbering.insert(first_num_idx, bullet_abs)
    numbering.insert(first_num_idx + 1, decimal_abs)
    numbering.append(bullet_num)
    numbering.append(decimal_num)
    return num_base, num_base + 1


def apply_num(paragraph, num_id):
    p_pr = paragraph._p.get_or_add_pPr()
    num_pr = p_pr.find(qn("w:numPr"))
    if num_pr is None:
        num_pr = OxmlElement("w:numPr")
        p_pr.append(num_pr)
    ilvl = OxmlElement("w:ilvl")
    ilvl.set(qn("w:val"), "0")
    num = OxmlElement("w:numId")
    num.set(qn("w:val"), str(num_id))
    num_pr.extend([ilvl, num])


def add_para(doc, text="", size=11, color=TEXT, bold=False, italic=False,
             before=0, after=6, line=1.25, align=WD_ALIGN_PARAGRAPH.LEFT,
             keep=False):
    p = doc.add_paragraph()
    p.alignment = align
    p.paragraph_format.space_before = Pt(before)
    p.paragraph_format.space_after = Pt(after)
    p.paragraph_format.line_spacing = line
    if text:
        r = p.add_run(text)
        font_run(r, size=size, color=color, bold=bold, italic=italic)
    if keep:
        set_keep_together(p)
    return p


def add_bullet(doc, text, bullet_num_id, bold_lead=None):
    p = doc.add_paragraph()
    apply_num(p, bullet_num_id)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = 1.25
    if bold_lead and text.startswith(bold_lead):
        lead = p.add_run(bold_lead)
        font_run(lead, size=11, color=NAVY, bold=True)
        rest = p.add_run(text[len(bold_lead):])
        font_run(rest, size=11, color=TEXT)
    else:
        run = p.add_run(text)
        font_run(run, size=11, color=TEXT)
    return p


def add_numbered(doc, title, text, number_num_id):
    p = doc.add_paragraph()
    apply_num(p, number_num_id)
    p.paragraph_format.space_after = Pt(5)
    p.paragraph_format.line_spacing = 1.25
    r = p.add_run(title + " ")
    font_run(r, size=11, color=NAVY, bold=True)
    r = p.add_run(text)
    font_run(r, size=11, color=TEXT)
    return p


def start_new_page(doc):
    """Start the next block on a new page without creating an empty page.

    A page-break run can be pushed to the next page when the preceding page is
    full, producing a second blank page. Page-break-before keeps the marker
    paragraph itself on the new page and avoids that Word pagination quirk.
    """
    p = doc.add_paragraph()
    p.paragraph_format.page_break_before = True
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = Pt(1)
    r = p.add_run(" ")
    font_run(r, size=1, color=WHITE)
    return p


def add_heading(doc, text, level=1, page_break_before=False):
    p = doc.add_paragraph(style=f"Heading {level}")
    p.paragraph_format.page_break_before = page_break_before
    r = p.add_run(text)
    font_run(r, size={1: 16, 2: 13, 3: 12}[level],
             color={1: BRAND, 2: BRAND, 3: BRAND_DARK}[level], bold=True)
    set_keep_with_next(p)
    return p


def add_kicker(doc, text, after=4):
    p = add_para(doc, text.upper(), size=9.5, color=BRAND, bold=True,
                 after=after, line=1.0, keep=True)
    return p


def add_callout(doc, label, body, fill=LIGHT, accent=BRAND, after=10):
    table = doc.add_table(rows=1, cols=1)
    set_table_geometry(table, [PAGE_WIDTH_DXA])
    cell = table.cell(0, 0)
    set_cell_shading(cell, fill)
    set_cell_border(cell,
                    top={"val": "nil"}, right={"val": "nil"},
                    bottom={"val": "nil"},
                    left={"val": "single", "sz": "22", "color": accent, "space": "0"})
    p = cell.paragraphs[0]
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.15
    r = p.add_run(label.upper())
    font_run(r, size=9, color=accent, bold=True)
    p2 = cell.add_paragraph()
    p2.paragraph_format.space_after = Pt(0)
    p2.paragraph_format.line_spacing = 1.25
    r = p2.add_run(body)
    font_run(r, size=10.8, color=TEXT)
    spacer = doc.add_paragraph()
    spacer.paragraph_format.space_after = Pt(after)
    return table


def add_status_table(doc, rows):
    table = doc.add_table(rows=1, cols=3)
    set_table_geometry(table, [1500, 3000, 4860])
    set_repeat_table_header(table.rows[0])
    headers = ["SITUAÇÃO", "ITEM", "PRÓXIMO PASSO"]
    for i, text in enumerate(headers):
        cell = table.rows[0].cells[i]
        set_cell_shading(cell, BRAND)
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(text)
        font_run(r, size=9, color=WHITE, bold=True)
    for status, item, next_step, palette in rows:
        cells = table.add_row().cells
        for c in cells:
            set_cell_shading(c, WHITE)
        status_fill, status_color = palette
        set_cell_shading(cells[0], status_fill)
        p = cells[0].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(status)
        font_run(r, size=9, color=status_color, bold=True)
        for idx, text in [(1, item), (2, next_step)]:
            p = cells[idx].paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.15
            r = p.add_run(text)
            font_run(r, size=9.8, color=NAVY if idx == 1 else TEXT,
                     bold=(idx == 1))
        for c in cells:
            set_cell_border(c,
                            top={"val": "single", "sz": "4", "color": LINE},
                            bottom={"val": "single", "sz": "4", "color": LINE},
                            left={"val": "single", "sz": "4", "color": LINE},
                            right={"val": "single", "sz": "4", "color": LINE})
    table.rows[0].cells[0].vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
    spacer = doc.add_paragraph()
    spacer.paragraph_format.space_after = Pt(6)
    return table


def add_two_col_info(doc, left_title, left_lines, right_title, right_lines):
    table = doc.add_table(rows=1, cols=2)
    set_table_geometry(table, [4680, 4680])
    for i, (title, lines) in enumerate([(left_title, left_lines), (right_title, right_lines)]):
        cell = table.cell(0, i)
        set_cell_shading(cell, LIGHTER)
        set_cell_border(cell,
                        top={"val": "single", "sz": "6", "color": LINE},
                        bottom={"val": "single", "sz": "6", "color": LINE},
                        left={"val": "single", "sz": "6", "color": LINE},
                        right={"val": "single", "sz": "6", "color": LINE})
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(5)
        r = p.add_run(title)
        font_run(r, size=11, color=BRAND_DARK, bold=True)
        for line in lines:
            p = cell.add_paragraph()
            p.paragraph_format.left_indent = Inches(0.02)
            p.paragraph_format.space_after = Pt(4)
            p.paragraph_format.line_spacing = 1.15
            r = p.add_run("• ")
            font_run(r, size=10, color=BRAND, bold=True)
            r = p.add_run(line)
            font_run(r, size=10, color=TEXT)
    spacer = doc.add_paragraph()
    spacer.paragraph_format.space_after = Pt(8)
    return table


def add_section_marker(doc, number, title, subtitle):
    table = doc.add_table(rows=1, cols=2)
    set_table_geometry(table, [1050, 8310])
    num_cell, text_cell = table.rows[0].cells
    set_cell_shading(num_cell, BRAND)
    set_cell_shading(text_cell, LIGHT)
    for cell in (num_cell, text_cell):
        set_cell_border(cell,
                        top={"val": "nil"}, bottom={"val": "nil"},
                        left={"val": "nil"}, right={"val": "nil"})
    p = num_cell.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(0)
    r = p.add_run(number)
    font_run(r, size=18, color=WHITE, bold=True)
    p = text_cell.paragraphs[0]
    p.paragraph_format.space_after = Pt(1)
    r = p.add_run(title)
    font_run(r, size=13, color=NAVY, bold=True)
    p2 = text_cell.add_paragraph()
    p2.paragraph_format.space_after = Pt(0)
    r = p2.add_run(subtitle)
    font_run(r, size=9.5, color=MUTED)
    spacer = doc.add_paragraph()
    spacer.paragraph_format.space_after = Pt(6)


def configure_styles(doc):
    normal = doc.styles["Normal"]
    normal.font.name = FONT
    normal._element.rPr.rFonts.set(qn("w:ascii"), FONT)
    normal._element.rPr.rFonts.set(qn("w:hAnsi"), FONT)
    normal.font.size = Pt(11)
    normal.font.color.rgb = rgb(TEXT)
    normal.paragraph_format.space_before = Pt(0)
    normal.paragraph_format.space_after = Pt(6)
    normal.paragraph_format.line_spacing = 1.25

    title = doc.styles["Title"]
    title.font.name = FONT
    title._element.rPr.rFonts.set(qn("w:ascii"), FONT)
    title._element.rPr.rFonts.set(qn("w:hAnsi"), FONT)
    title.font.size = Pt(30)
    title.font.bold = True
    title.font.color.rgb = rgb(NAVY)
    title.paragraph_format.space_before = Pt(0)
    title.paragraph_format.space_after = Pt(8)

    subtitle = doc.styles["Subtitle"]
    subtitle.font.name = FONT
    subtitle._element.rPr.rFonts.set(qn("w:ascii"), FONT)
    subtitle._element.rPr.rFonts.set(qn("w:hAnsi"), FONT)
    subtitle.font.size = Pt(13.2)
    subtitle.font.color.rgb = rgb(MUTED)
    subtitle.paragraph_format.space_after = Pt(18)

    specs = {
        "Heading 1": (16, BRAND, 18, 10),
        "Heading 2": (13, BRAND, 14, 7),
        "Heading 3": (12, BRAND_DARK, 10, 5),
    }
    for name, (size, color, before, after) in specs.items():
        style = doc.styles[name]
        style.font.name = FONT
        style._element.rPr.rFonts.set(qn("w:ascii"), FONT)
        style._element.rPr.rFonts.set(qn("w:hAnsi"), FONT)
        style.font.size = Pt(size)
        style.font.bold = True
        style.font.color.rgb = rgb(color)
        style.paragraph_format.space_before = Pt(before)
        style.paragraph_format.space_after = Pt(after)
        style.paragraph_format.keep_with_next = True
        style.paragraph_format.keep_together = True


def configure_page(doc):
    for section in doc.sections:
        section.page_width = Inches(8.5)
        section.page_height = Inches(11)
        section.top_margin = Inches(1)
        section.right_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.header_distance = Inches(0.492)
        section.footer_distance = Inches(0.492)


def add_header_footer(section, first_page=False):
    header = section.header
    p = header.paragraphs[0]
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.tab_stops.add_tab_stop(Inches(6.5))
    if first_page:
        p.text = ""
    else:
        r = p.add_run("KATO ODONTOLOGIA  |  KIT DE ALINHAMENTO")
        font_run(r, size=8.2, color=MUTED, bold=True)
        r = p.add_run("\tBLUE DIGITAL HUB")
        font_run(r, size=8.2, color=BRAND, bold=True)
        paragraph_border_bottom(p, color=LINE, size=4, space=3)

    footer = section.footer
    p = footer.paragraphs[0]
    p.paragraph_format.tab_stops.add_tab_stop(Inches(6.5))
    p.paragraph_format.space_before = Pt(3)
    r = p.add_run("BlueDigital Hub  |  Documento de alinhamento")
    font_run(r, size=8.2, color=MUTED)
    r = p.add_run("\tPágina ")
    font_run(r, size=8.2, color=MUTED)
    add_page_field(p)


def set_document_properties(doc):
    props = doc.core_properties
    props.title = "Briefing de materiais - Site Kato Odontologia"
    props.subject = "Materiais disponíveis, pendências e próximos passos para o novo site"
    props.author = "BlueDigital Hub"
    props.keywords = "Kato Odontologia, site, briefing, materiais, BlueDigital Hub"
    props.comments = "Documento preparado para alinhamento com o cliente."


def build_document():
    doc = Document()
    set_document_properties(doc)
    configure_styles(doc)
    configure_page(doc)
    bullet_id, number_id = add_custom_numbering(doc)
    section = doc.sections[0]
    section.different_first_page_header_footer = True
    add_header_footer(section, first_page=False)
    # The first-page header stays blank through different_first_page_header_footer.
    first_header = section.first_page_header
    first_header.paragraphs[0].text = ""
    first_footer = section.first_page_footer
    fp = first_footer.paragraphs[0]
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = fp.add_run("BlueDigital Hub  |  Estratégia, design e tecnologia com propósito")
    font_run(r, size=8.5, color=MUTED)

    # PAGE 1 - customer_pack opening.
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(24)
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    shape = p.add_run().add_picture(str(LOGO), width=Inches(3.85))
    add_image_alt(shape, "BlueDigital Hub", "Logotipo da BlueDigital Hub")

    add_kicker(doc, "Kit de alinhamento do projeto", after=4)
    p = doc.add_paragraph(style="Title")
    p.paragraph_format.space_after = Pt(7)
    r = p.add_run("Novo site\nKato Odontologia")
    font_run(r, size=30, color=NAVY, bold=True)
    p = doc.add_paragraph(style="Subtitle")
    r = p.add_run("O que já temos e o que precisamos reunir para criar uma presença digital completa, humana e confiável.")
    font_run(r, size=13.2, color=MUTED)

    meta = doc.add_table(rows=2, cols=2)
    set_table_geometry(meta, [4680, 4680], indent_dxa=0)
    meta_data = [
        ("PREPARADO PARA", "Kato Odontologia"),
        ("PREPARADO POR", "BlueDigital Hub"),
        ("ETAPA", "Alinhamento de conteúdo e materiais"),
        ("VERSÃO", "1.0 - 10 de agosto de 2026"),
    ]
    for idx, (label, value) in enumerate(meta_data):
        row, col = divmod(idx, 2)
        cell = meta.cell(row, col)
        set_cell_shading(cell, LIGHTER)
        set_cell_border(cell,
                        top={"val": "single", "sz": "5", "color": LINE},
                        bottom={"val": "single", "sz": "5", "color": LINE},
                        left={"val": "single", "sz": "5", "color": LINE},
                        right={"val": "single", "sz": "5", "color": LINE})
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(2)
        r = p.add_run(label)
        font_run(r, size=8.5, color=BRAND, bold=True)
        p2 = cell.add_paragraph()
        p2.paragraph_format.space_after = Pt(0)
        r = p2.add_run(value)
        font_run(r, size=10.5, color=NAVY, bold=True)

    add_para(doc, "", after=7)
    add_callout(
        doc,
        "Uma construção em conjunto",
        "Este documento não é uma lista burocrática. É um guia para que a equipe da Kato e a BlueDigital Hub trabalhem com clareza, aproveitando tudo o que já existe e identificando apenas o que ainda precisa ser confirmado ou produzido.",
        fill=LIGHT,
        accent=BRAND,
        after=7,
    )
    add_para(
        doc,
        "A direção criativa já está bem encaminhada. A próxima etapa é transformar o material provisório em uma apresentação fiel à clínica, às pessoas que fazem parte dela e à experiência real dos pacientes.",
        size=10.8,
        color=TEXT,
        after=0,
        line=1.25,
    )

    start_new_page(doc)

    # PAGE 2 - current state.
    add_section_marker(doc, "01", "O ponto de partida", "Uma base sólida já está pronta para evoluir com o material oficial da clínica.")
    add_heading(doc, "O que já temos em mãos", level=1)
    add_para(
        doc,
        "O novo site já possui uma estrutura clara, responsiva e orientada para gerar confiança. O conteúdo inicial foi organizado para contar a história da Kato, apresentar a equipe e facilitar o contato com cada unidade.",
        after=9,
    )
    add_two_col_info(
        doc,
        "História e posicionamento",
        [
            "Atuação em Guarulhos desde 1995.",
            "Narrativa central baseada em continuidade, confiança e cuidado entre gerações.",
            "Linha do tempo inicial com marcos de 1995, 2000, 2019, 2020 e 2021.",
        ],
        "Estrutura do site",
        [
            "Página principal adaptada para computador e celular.",
            "Seções de história, especialidades, equipe, avaliações e unidades.",
            "Chamadas diretas para agendamento pelo WhatsApp.",
        ],
    )
    add_two_col_info(
        doc,
        "Conteúdo já levantado",
        [
            "Duas unidades com endereço, telefone, WhatsApp e mapa.",
            "Seis áreas de atendimento já descritas.",
            "Quatro profissionais com fotografias disponíveis.",
            "Dois depoimentos inseridos como prova social inicial.",
        ],
        "Base digital",
        [
            "Título e descrição preparados para mecanismos de busca.",
            "Informações estruturadas de clínica, serviços e localizações.",
            "Imagens da equipe otimizadas para carregamento rápido.",
            "Instagram e Facebook já identificados.",
        ],
    )

    add_callout(
        doc,
        "Em resumo",
        "A estrutura e a direção visual já existem. Para publicar, precisamos receber o logotipo e as fotografias oficiais, além de confirmar contatos, horários, dados profissionais, registros, depoimentos e afirmações institucionais.",
        fill=AMBER_LIGHT,
        accent=AMBER,
        after=0,
    )

    start_new_page(doc)

    # PAGE 3 - essential content.
    add_section_marker(doc, "02", "Informações essenciais", "O que precisa estar confirmado para o site representar a clínica com precisão.")
    add_callout(
        doc,
        "Prioridade para publicação",
        "Antes da publicação, a clínica precisa aprovar por escrito os dados institucionais, profissionais e de contato.",
        fill=AMBER_LIGHT,
        accent=AMBER,
        after=8,
    )

    add_two_col_info(
        doc,
        "Dados institucionais e profissionais",
        [
            "Razão social, nome fantasia, CNPJ e CRO da pessoa jurídica, quando aplicável.",
            "Nome completo e CRO do responsável técnico.",
            "Nome, função, especialidade registrada e CRO de cada profissional.",
            "Unidade e dias de atendimento, se a clínica quiser divulgar.",
            "Ano de início e fatos apresentados na linha do tempo.",
        ],
        "Contatos e funcionamento",
        [
            "Telefones e WhatsApps das duas unidades.",
            "E-mail institucional para atendimento.",
            "Horários, sábados, feriados e diferenças entre unidades.",
            "Links do Google Maps e do Google Business.",
            "Estacionamento, acessibilidade e pontos de referência.",
        ],
    )

    add_heading(doc, "Serviços, equipe e linguagem", level=2)
    service_items = [
        "Revisar as seis áreas de atendimento e confirmar eventuais diferenças entre as unidades.",
        "Validar frases institucionais como 'não há rodízio de profissionais' e 'quem começa o tratamento é quem termina'.",
        "Indicar se existe algum serviço prioritário, público principal ou diferencial que ainda não esteja representado.",
        "Revisar todo o conteúdo final com o responsável técnico antes da publicação.",
    ]
    for item in service_items:
        add_bullet(doc, item, bullet_id)

    add_callout(
        doc,
        "Cuidado com informações clínicas",
        "A BlueDigital Hub organiza e apresenta o conteúdo, mas a validação técnica, ética e regulatória das informações odontológicas deve ser feita pela própria clínica e pelo responsável técnico.",
        fill=LIGHTER,
        accent=BRAND_DARK,
        after=0,
    )

    start_new_page(doc)

    # PAGE 4 - visual assets.
    add_section_marker(doc, "03", "Identidade e imagens", "O material visual será responsável por transformar a boa estrutura em uma experiência autêntica.")
    add_heading(doc, "Materiais de marca", level=1)
    add_para(
        doc,
        "O site já possui uma direção visual inspirada na identidade atual da Kato. Para finalizar com fidelidade, precisamos substituir os elementos provisórios pelos arquivos oficiais.",
        after=8,
    )
    brand_items = [
        "Logotipo oficial em SVG, PDF, AI ou EPS e uma versão PNG transparente.",
        "Variações para fundo claro, fundo escuro, formato horizontal e símbolo isolado, se existirem.",
        "Manual de marca, paleta, tipografias, ícones ou grafismos disponíveis.",
        "Materiais impressos que ajudem a preservar a identidade visual da clínica.",
    ]
    for item in brand_items:
        add_bullet(doc, item, bullet_id)

    add_heading(doc, "Fotografias que farão diferença", level=2)
    add_two_col_info(
        doc,
        "Essenciais",
        [
            "Uma foto principal forte da clínica ou da equipe, com espaço para composição do título.",
            "Fachada e recepção de cada unidade.",
            "Consultórios, salas de atendimento e detalhes do ambiente.",
            "Retratos atualizados de todos os profissionais que serão apresentados.",
        ],
        "Muito bem-vindas",
        [
            "Equipe reunida e momentos espontâneos de trabalho.",
            "Sinalização, acessibilidade e detalhes que transmitam cuidado.",
            "Ambientes de espera, atendimento infantil e tecnologia, quando relevantes.",
            "Imagens externas que ajudem o paciente a reconhecer cada unidade.",
        ],
    )

    add_heading(doc, "Orientação simples para o envio", level=2)
    photo_items = [
        "Enviar os arquivos originais, sem compressão do WhatsApp.",
        "Para a imagem principal, priorizar 2400 pixels ou mais no lado maior.",
        "Para retratos, usar enquadramento vertical, boa iluminação e fundo limpo.",
        "Organizar em pastas por unidade, equipe e marca, com nomes de arquivo claros.",
        "Conteúdo com pacientes ou procedimentos exige autorização documentada e validação da clínica.",
    ]
    for item in photo_items:
        add_bullet(doc, item, bullet_id)

    add_callout(
        doc,
        "Nossa recomendação",
        "Fotos reais ajudam o paciente a reconhecer o espaço, a equipe e o cuidado.",
        fill=TEAL_LIGHT,
        accent=TEAL,
        after=0,
    )

    # The previous page is intentionally full; the following section marker
    # flows naturally to the next page without leaving an empty marker page.
    # PAGE 5 - proof, access and extras.
    add_section_marker(doc, "04", "Confiança e presença digital", "Pequenos detalhes que tornam o site mais útil para o paciente e mais forte para a clínica.")
    add_heading(doc, "O que precisamos alinhar", level=1)
    add_two_col_info(
        doc,
        "Depoimentos e prova social",
        [
            "Origem dos depoimentos de Leandro Correa e Juliana Oliveira.",
            "Autorização para republicação no site com nome.",
            "Links oficiais das avaliações no Google.",
            "Outros depoimentos que a clínica queira incluir.",
            "Preservação do sentido original de cada relato.",
        ],
        "Domínio, acessos e canais",
        [
            "Responsável e registrador do domínio katoodontologia.com.br.",
            "Hospedagem atual e e-mails ligados ao domínio.",
            "Acessos por convite ou usuário colaborador.",
            "Perfis oficiais de Instagram, Facebook e Google Business.",
            "Contato responsável pelas aprovações do projeto.",
            "Senhas compartilhadas somente por um meio seguro.",
        ],
    )

    add_heading(doc, "Conteúdos opcionais que podem enriquecer o site", level=2)
    optional_items = [
        "Perguntas frequentes sobre primeira consulta, duração do atendimento, retorno e orientações gerais.",
        "Informações sobre convênios, formas de pagamento ou facilidades, caso a clínica queira divulgar e aprove o conteúdo.",
        "Orientações para pacientes infantis, pessoas ansiosas ou pacientes com necessidades específicas.",
        "Diferenciais de estrutura, tecnologia, treinamento da equipe e acessibilidade.",
        "Política de privacidade e canais para solicitações relacionadas a dados pessoais, quando aplicável.",
    ]
    for item in optional_items:
        add_bullet(doc, item, bullet_id)

    add_callout(
        doc,
        "Envio organizado economiza tempo",
        "O ideal é reunir tudo em uma única pasta compartilhada, com subpastas por categoria. Também ajuda muito receber as confirmações de conteúdo em um único documento ou e-mail, evitando versões diferentes da mesma informação.",
        fill=LIGHT,
        accent=BRAND,
        after=0,
    )

    start_new_page(doc)

    # PAGE 6 - workflow and final checklist.
    add_section_marker(doc, "05", "Próximos passos", "Um fluxo simples para concluir o projeto com segurança e sem retrabalho.")
    steps = [
        ("Recebimento dos materiais.", "A clínica compartilha marca, fotografias e confirmações essenciais."),
        ("Conferência e organização.", "Revisamos o material e sinalizamos somente o que ainda estiver faltando."),
        ("Finalização do conteúdo.", "Consolidamos textos, profissionais, contatos e unidades para aprovação."),
        ("Aplicação visual.", "Aplicamos logotipo, fotografias e detalhes oficiais da clínica."),
        ("Revisão completa.", "Testamos computador e celular, links, velocidade, acessibilidade e busca."),
        ("Aprovação e publicação.", "A clínica valida por escrito e o site é preparado para entrar no ar."),
    ]
    for title, body in steps:
        add_numbered(doc, title, body, number_id)

    add_heading(doc, "Checklist de liberação", level=2)
    final_checks = [
        "Dados institucionais e registros profissionais aprovados.",
        "Telefones, WhatsApps, e-mail, endereços e horários conferidos.",
        "Especialidades, equipe e afirmações institucionais validadas.",
        "Logotipo e fotografias oficiais aplicados.",
        "Depoimentos e imagens autorizados para uso.",
        "Domínio e acessos necessários disponibilizados com segurança.",
        "Versão final aprovada pelo contato responsável e pelo responsável técnico.",
    ]
    for item in final_checks:
        add_bullet(doc, item, bullet_id)

    add_callout(
        doc,
        "O objetivo final",
        "Queremos que o novo site tenha a mesma sensação de confiança que a Kato construiu ao longo de mais de 30 anos: próximo, profissional e verdadeiro. Com os materiais acima, conseguiremos transformar essa história em uma presença digital à altura da clínica.",
        fill=LIGHT,
        accent=BRAND,
        after=8,
    )

    # Global structural cleanup.
    for p in doc.paragraphs:
        if p.style and p.style.name.startswith("Heading"):
            set_keep_with_next(p)
        set_keep_together(p)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc.save(OUT)
    print(OUT)


if __name__ == "__main__":
    build_document()
