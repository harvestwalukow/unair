"""Render ARTIKEL_PKM_ESI.md as a polished, self-contained PDF."""

from __future__ import annotations

import html
import re
from pathlib import Path

from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Image,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "ARTIKEL_PKM_ESI.md"
OUTPUT = ROOT / "output" / "pdf" / "ARTIKEL_PKM_ESI.pdf"


def register_fonts() -> None:
    fonts = Path(r"C:\Windows\Fonts")
    pdfmetrics.registerFont(TTFont("TimesNewRoman", fonts / "times.ttf"))
    pdfmetrics.registerFont(TTFont("TimesNewRoman-Bold", fonts / "timesbd.ttf"))
    pdfmetrics.registerFont(TTFont("TimesNewRoman-Italic", fonts / "timesi.ttf"))
    pdfmetrics.registerFont(TTFont("TimesNewRoman-BoldItalic", fonts / "timesbi.ttf"))
    pdfmetrics.registerFontFamily(
        "TimesNewRoman",
        normal="TimesNewRoman",
        bold="TimesNewRoman-Bold",
        italic="TimesNewRoman-Italic",
        boldItalic="TimesNewRoman-BoldItalic",
    )


def inline_markup(text: str) -> str:
    text = text.replace("–", "-").replace("—", "-").replace("‑", "-")
    text = html.escape(text.strip(), quote=False)
    text = re.sub(r"`([^`]+)`", r'<font name="Courier">\1</font>', text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<i>\1</i>", text)
    text = re.sub(r"\$([^$]+)\$", r"<i>\1</i>", text)
    text = re.sub(r"\[([^]]+)\]\((https?://[^)]+)\)", r'<link href="\2" color="#1d4ed8">\1</link>', text)
    return text.replace("  ", " ")


def equation_text(lines: list[str]) -> str:
    raw = " ".join(line.strip() for line in lines)
    known = {
        r"r_t=\frac{P_t-P_{t-1}}{P_{t-1}},": "rₜ = (Pₜ − Pₜ₋₁) / Pₜ₋₁,",
        r"ESI_t=\sum_{j=1}^{12} w_j z_{j,t},": "ESIₜ = Σⱼ₌₁¹² wⱼ zⱼ,ₜ,",
        r"\Delta MAE=\frac{MAE_{naive}-MAE_{model}}{MAE_{naive}}\times100\%.": "ΔMAE = [(MAEₙₐᵢᵥₑ − MAEₘₒdₑₗ) / MAEₙₐᵢᵥₑ] × 100%.",
    }
    return known.get(raw, raw.replace("\\", ""))


def make_styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "TitleAcademic",
            parent=base["Title"],
            fontName="TimesNewRoman-Bold",
            fontSize=12,
            leading=14,
            alignment=TA_CENTER,
            spaceAfter=5,
            textColor=colors.HexColor("#111827"),
        ),
        "authors": ParagraphStyle(
            "Authors",
            fontName="TimesNewRoman",
            fontSize=10,
            leading=10.5,
            alignment=TA_CENTER,
            spaceAfter=1,
        ),
        "h2": ParagraphStyle(
            "H2",
            fontName="TimesNewRoman-Bold",
            fontSize=12,
            leading=13.8,
            alignment=TA_LEFT,
            spaceBefore=7,
            spaceAfter=3,
            keepWithNext=True,
        ),
        "h3": ParagraphStyle(
            "H3",
            fontName="TimesNewRoman-Bold",
            fontSize=12,
            leading=13.8,
            spaceBefore=6,
            spaceAfter=3,
            keepWithNext=True,
        ),
        "body": ParagraphStyle(
            "BodyAcademic",
            fontName="TimesNewRoman",
            fontSize=12,
            leading=13.8,
            alignment=TA_JUSTIFY,
            firstLineIndent=0.75 * cm,
            spaceAfter=4,
            allowWidows=0,
            allowOrphans=0,
        ),
        "abstract": ParagraphStyle(
            "Abstract",
            fontName="TimesNewRoman",
            fontSize=11,
            leading=11,
            alignment=TA_JUSTIFY,
            spaceAfter=3,
        ),
        "caption": ParagraphStyle(
            "Caption",
            fontName="TimesNewRoman-Italic",
            fontSize=11,
            leading=11,
            alignment=TA_CENTER,
            spaceBefore=3,
            spaceAfter=3,
        ),
        "equation": ParagraphStyle(
            "Equation",
            fontName="TimesNewRoman-Italic",
            fontSize=12,
            leading=13.8,
            alignment=TA_CENTER,
            spaceBefore=4,
            spaceAfter=6,
        ),
        "table_title": ParagraphStyle(
            "TableTitle",
            fontName="TimesNewRoman-Bold",
            fontSize=11,
            leading=11,
            spaceBefore=5,
            spaceAfter=4,
        ),
        "table_cell": ParagraphStyle(
            "TableCell",
            fontName="TimesNewRoman",
            fontSize=9.5,
            leading=10.5,
        ),
        "table_header": ParagraphStyle(
            "TableHeader",
            fontName="TimesNewRoman-Bold",
            fontSize=9.5,
            leading=10.5,
            alignment=TA_CENTER,
        ),
        "source": ParagraphStyle(
            "Source",
            fontName="TimesNewRoman-Italic",
            fontSize=11,
            leading=11,
            alignment=TA_CENTER,
            spaceAfter=5,
        ),
        "reference": ParagraphStyle(
            "Reference",
            fontName="TimesNewRoman",
            fontSize=12,
            leading=13.8,
            alignment=TA_JUSTIFY,
            leftIndent=0.75 * cm,
            firstLineIndent=-0.75 * cm,
            spaceAfter=4,
        ),
    }


def page_decor(canvas, doc) -> None:
    canvas.saveState()
    canvas.setFont("TimesNewRoman", 12)
    canvas.setFillColor(colors.black)
    canvas.drawRightString(A4[0] - 3 * cm, A4[1] - 1.8 * cm, str(doc.page))
    canvas.restoreState()


def image_flowable(path: Path, max_width: float, max_height: float) -> Image:
    with PILImage.open(path) as picture:
        width, height = picture.size
    scale = min(max_width / width, max_height / height)
    item = Image(str(path), width=width * scale, height=height * scale)
    item.hAlign = "CENTER"
    return item


def table_flowable(rows: list[list[str]], styles: dict[str, ParagraphStyle], width: float) -> Table:
    parsed = []
    for row_index, row in enumerate(rows):
        style = styles["table_header"] if row_index == 0 else styles["table_cell"]
        parsed.append([Paragraph(inline_markup(cell), style) for cell in row])
    if len(rows[0]) == 2:
        col_widths = [0.72 * width, 0.28 * width]
    elif len(rows[0]) == 5:
        col_widths = [0.34 * width, *([0.165 * width] * 4)]
    else:
        col_widths = [width / len(rows[0])] * len(rows[0])
    table = Table(parsed, colWidths=col_widths, repeatRows=1, hAlign="CENTER")
    table.setStyle(TableStyle([
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#111827")),
        ("LINEABOVE", (0, 0), (-1, 0), 0.7, colors.black),
        ("LINEBELOW", (0, 0), (-1, 0), 0.5, colors.black),
        ("LINEBELOW", (0, -1), (-1, -1), 0.7, colors.black),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    return table


def build_story(text: str, styles: dict[str, ParagraphStyle], content_width: float) -> list:
    lines = text.splitlines()
    story = []
    paragraph: list[str] = []
    in_abstract = False
    in_references = False

    def flush_paragraph() -> None:
        nonlocal paragraph
        if paragraph:
            raw = " ".join(part.strip() for part in paragraph)
            style = styles["abstract"] if in_abstract else styles["body"]
            if in_references:
                style = styles["reference"]
            if raw.startswith("**Kata-kata kunci:") or raw.startswith("**Keywords:"):
                style = styles["abstract"]
            if raw.startswith("*Sumber:"):
                style = styles["source"]
            story.append(Paragraph(inline_markup(raw), style))
            paragraph = []

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            flush_paragraph()
            i += 1
            continue
        if line.startswith("# "):
            flush_paragraph()
            story.append(Paragraph(inline_markup(line[2:]), styles["title"]))
            i += 1
            while i < len(lines) and lines[i].strip() and not lines[i].startswith("## "):
                story.append(Paragraph(inline_markup(lines[i]), styles["authors"]))
                i += 1
            story.append(Spacer(1, 5))
            continue
        if line.startswith("## "):
            flush_paragraph()
            heading = line[3:]
            if heading == "PENDAHULUAN":
                story.append(PageBreak())
            if heading.startswith("LAMPIRAN"):
                story.append(PageBreak())
            in_abstract = heading in {"ABSTRAK", "ABSTRACT"}
            in_references = heading == "DAFTAR PUSTAKA"
            story.append(Paragraph(inline_markup(heading), styles["h2"]))
            i += 1
            continue
        if line.startswith("### "):
            flush_paragraph()
            story.append(Paragraph(inline_markup(line[4:]), styles["h3"]))
            i += 1
            continue
        if line == "$$":
            flush_paragraph()
            equation_lines = []
            i += 1
            while i < len(lines) and lines[i].strip() != "$$":
                equation_lines.append(lines[i])
                i += 1
            story.append(Paragraph(html.escape(equation_text(equation_lines)), styles["equation"]))
            i += 1
            continue
        image_match = re.fullmatch(r"!\[[^]]*\]\(([^)]+)\)", line)
        if image_match:
            flush_paragraph()
            path = ROOT / image_match.group(1)
            if not path.exists():
                raise FileNotFoundError(f"Missing article image: {path}")
            image = image_flowable(path, content_width, 9.5 * cm)
            block = [image]
            if i + 2 < len(lines) and not lines[i + 1].strip() and lines[i + 2].strip().startswith("*"):
                block.append(Paragraph(inline_markup(lines[i + 2].strip()), styles["caption"]))
                i += 3
            else:
                i += 1
            story.append(KeepTogether(block))
            continue
        if line.startswith("**Tabel "):
            flush_paragraph()
            table_title = Paragraph(inline_markup(line), styles["table_title"])
            i += 1
            while i < len(lines) and not lines[i].strip():
                i += 1
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                cells = [cell.strip() for cell in lines[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells):
                    rows.append(cells)
                i += 1
            story.append(KeepTogether([
                table_title,
                table_flowable(rows, styles, content_width),
                Spacer(1, 6),
            ]))
            continue
        if line.startswith("|"):
            flush_paragraph()
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                cells = [cell.strip() for cell in lines[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells):
                    rows.append(cells)
                i += 1
            story.append(table_flowable(rows, styles, content_width))
            story.append(Spacer(1, 6))
            continue
        paragraph.append(line)
        i += 1
    flush_paragraph()
    return story


def main() -> None:
    register_fonts()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    styles = make_styles()
    doc = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=A4,
        rightMargin=3 * cm,
        leftMargin=4 * cm,
        topMargin=3 * cm,
        bottomMargin=3 * cm,
        title="Pemodelan dan Prediksi Indeks Tekanan Ekonomi Masyarakat Indonesia",
        author="Aflah Zain Japamel; Harvest Walukow",
        subject="Artikel PKM Economic Stress Index",
    )
    story = build_story(SOURCE.read_text(encoding="utf-8"), styles, doc.width)
    doc.build(story, onFirstPage=page_decor, onLaterPages=page_decor)
    print(OUTPUT)


if __name__ == "__main__":
    main()
