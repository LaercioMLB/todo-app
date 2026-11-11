"""Gera escopo.pdf e o fluxo vetorial a partir de docs/escopo.md.

Dependência de geração: reportlab. Execute: python scripts/render-escopo.py
Não inicia serviços nem modifica a aplicação.
"""

from __future__ import annotations

import re
from pathlib import Path
from xml.sax.saxutils import escape

import reportlab
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    Flowable,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs" / "escopo.md"
OUT = ROOT / "escopo.pdf"
WIDTH, HEIGHT = A4
MARGIN = 47
CONTENT = WIDTH - MARGIN * 2
BLUE = colors.HexColor("#174a8b")
INK = colors.HexColor("#243349")
MUTED = colors.HexColor("#5d6f86")
LINE = colors.HexColor("#d9e3ef")
PALE = colors.HexColor("#f1f5fb")
ORANGE = colors.HexColor("#f47b20")
WHITE = colors.white


def register_fonts() -> None:
    bundled = Path(reportlab.__file__).parent / "fonts"
    system = Path("C:/Windows/Fonts")
    fonts = (("DocSans", system / "segoeui.ttf"), ("DocBold", system / "segoeuib.ttf"))
    if not all(path.is_file() for _, path in fonts):
        fonts = (("DocSans", bundled / "Vera.ttf"), ("DocBold", bundled / "VeraBd.ttf"))
    for name, path in fonts:
        pdfmetrics.registerFont(TTFont(name, str(path)))
    pdfmetrics.registerFontFamily(
        "DocSans", normal="DocSans", bold="DocBold", italic="DocSans",
        boldItalic="DocBold",
    )


def inline(text: str) -> str:
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", escape(text))


def theme() -> dict[str, ParagraphStyle]:
    body = ParagraphStyle(
        "Body", fontName="DocSans", fontSize=9.7, leading=14,
        textColor=INK, spaceAfter=8,
    )
    return {
        "body": body,
        "small": ParagraphStyle(
            "Small", parent=body, fontSize=8.9, leading=12.5, spaceAfter=0,
        ),
        "cell": ParagraphStyle(
            "Cell", parent=body, fontSize=8.8, leading=12, spaceAfter=0,
        ),
        "cellhead": ParagraphStyle(
            "CellHead", parent=body, fontName="DocBold", fontSize=8.8,
            leading=12, textColor=WHITE, spaceAfter=0,
        ),
        "title": ParagraphStyle(
            "Title", fontName="DocBold", fontSize=38, leading=43,
            textColor=BLUE, spaceAfter=9,
        ),
        "page": ParagraphStyle(
            "PageTitle", fontName="DocBold", fontSize=22, leading=28,
            textColor=BLUE, spaceAfter=12,
        ),
        "section": ParagraphStyle(
            "Section", fontName="DocBold", fontSize=11.5, leading=16,
            textColor=BLUE, spaceBefore=9, spaceAfter=6, keepWithNext=True,
        ),
        "eyebrow": ParagraphStyle(
            "Eyebrow", fontName="DocBold", fontSize=7.8, leading=11,
            textColor=MUTED, spaceAfter=9,
        ),
        "lead": ParagraphStyle(
            "Lead", parent=body, fontSize=11.5, leading=17,
            textColor=BLUE, spaceAfter=10,
        ),
        "bullet": ParagraphStyle(
            "Bullet", parent=body, leftIndent=10, firstLineIndent=-10,
            spaceAfter=5,
        ),
    }


def fit_label(pdf, text: str, x: float, y: float, width: float,
              size: float = 7.5, font: str = "DocSans") -> None:
    size = min(size, size * width / max(pdfmetrics.stringWidth(text, font, size), 1))
    pdf.setFont(font, size)
    pdf.drawCentredString(x, y, text)


def arrow(pdf, start: float, end: float, y: float, label: str,
          response: bool = False) -> None:
    direction = 1 if end > start else -1
    pdf.setStrokeColor(MUTED if response else BLUE)
    pdf.setFillColor(MUTED if response else BLUE)
    pdf.setLineWidth(1)
    if response:
        pdf.setDash(3, 2)
    pdf.line(start, y, end - direction * 5, y)
    pdf.setDash()
    path = pdf.beginPath()
    path.moveTo(end, y)
    path.lineTo(end - direction * 6, y + 2.8)
    path.lineTo(end - direction * 6, y - 2.8)
    path.close()
    pdf.drawPath(path, fill=1, stroke=0)
    fit_label(pdf, label, (start + end) / 2, y + 5, abs(end - start) - 8)


class Architecture(Flowable):
    def __init__(self):
        super().__init__()
        self.width = CONTENT
        self.height = 145

    def draw(self):
        pdf = self.canv
        pdf.setFillColor(PALE)
        pdf.roundRect(0, 5, self.width, 138, 8, fill=1, stroke=0)
        pdf.setFillColor(BLUE)
        pdf.setFont("DocBold", 8)
        pdf.drawString(14, 123, "ARQUITETURA MÍNIMA / PROVEDOR DE NUVEM LIVRE")
        boxes = [(14, 67, 84, 32), (132, 42, 169, 65), (337, 42, 150, 65)]
        for x, y, width, height in boxes:
            pdf.setFillColor(WHITE)
            pdf.setStrokeColor(LINE)
            pdf.roundRect(x, y, width, height, 5, fill=1, stroke=1)
        pdf.setFillColor(INK)
        pdf.setFont("DocBold", 8.4)
        pdf.drawCentredString(56, 79, "Visitantes")
        pdf.drawString(143, 88, "VM 1 / APLICAÇÃO")
        pdf.drawString(348, 88, "VM 2 / BANCO")
        pdf.setFont("DocSans", 8.2)
        pdf.drawString(143, 70, "Nginx + React")
        pdf.drawString(143, 55, "API Node.js / Express")
        pdf.drawString(348, 70, "MongoDB autenticado")
        pdf.drawString(348, 55, "Volume persistente")
        arrow(pdf, 98, 132, 83, "HTTPS")
        arrow(pdf, 301, 337, 74, "Privada")
        pdf.setFillColor(MUTED)
        pdf.setFont("DocSans", 7.6)
        pdf.drawString(14, 21, "Somente a aplicação recebe tráfego público. A API acessa o banco pela rede privada.")


class ApplicationFlow(Flowable):
    def __init__(self):
        super().__init__()
        self.width = CONTENT
        self.height = 420

    def draw(self):
        pdf = self.canv
        lanes = [60, 185, 310, 435]
        pdf.setFillColor(PALE)
        pdf.roundRect(0, 0, self.width, self.height - 2, 8, fill=1, stroke=0)
        pdf.setStrokeColor(LINE)
        pdf.setLineWidth(0.8)
        pdf.setDash(3, 4)
        for x in lanes:
            pdf.line(x, 368, x, 20)
        pdf.setDash()
        labels = [
            ("Navegador", "React / visitante"),
            ("Nginx", "VM da aplicação"),
            ("API Express", "VM da aplicação"),
            ("MongoDB", "VM exclusiva do banco"),
        ]
        for x, (title, subtitle) in zip(lanes, labels):
            pdf.setFillColor(WHITE)
            pdf.setStrokeColor(LINE)
            pdf.roundRect(x - 55, 373, 110, 35, 5, fill=1, stroke=1)
            pdf.setFillColor(BLUE)
            fit_label(pdf, title, x, 393, 98, 8.6, "DocBold")
            pdf.setFillColor(MUTED)
            fit_label(pdf, subtitle, x, 381, 98, 7.1)

        def stage(y: float, label: str) -> None:
            pdf.setFillColor(PALE)
            pdf.rect(7, y - 4, self.width - 14, 16, fill=1, stroke=0)
            pdf.setFillColor(ORANGE)
            pdf.roundRect(10, y - 1, 3, 9, 1.5, fill=1, stroke=0)
            pdf.setFillColor(BLUE)
            pdf.setFont("DocBold", 8.1)
            pdf.drawString(20, y, label)

        stage(352, "1 · Abertura da aplicação")
        arrow(pdf, lanes[0], lanes[1], 330, "GET /")
        arrow(pdf, lanes[1], lanes[0], 310, "HTML / CSS / JS", response=True)

        operations = [
            (284, "2 · Listar tarefas", "GET /todos", "Consultar tarefas", "Lista de tarefas", "200 / JSON"),
            (218, "3 · Adicionar tarefa", "POST /todos", "Inserir tarefa", "Tarefa salva", "201 / JSON"),
            (152, "4 · Concluir ou reabrir", "PATCH /todos/:id", "Buscar + salvar estado", "Tarefa atualizada", "200 / JSON"),
            (86, "5 · Excluir tarefa", "DELETE /todos/:id", "Excluir tarefa", "Resultado da exclusão", "200 / JSON"),
        ]
        for y, title, request, operation, result, status in operations:
            stage(y, title)
            arrow(pdf, lanes[0], lanes[1], y - 22, request)
            arrow(pdf, lanes[1], lanes[2], y - 22, request)
            arrow(pdf, lanes[2], lanes[3], y - 22, operation)
            arrow(pdf, lanes[3], lanes[2], y - 42, result, response=True)
            arrow(pdf, lanes[2], lanes[1], y - 42, status, response=True)
            arrow(pdf, lanes[1], lanes[0], y - 42, status, response=True)
        pdf.setFillColor(MUTED)
        fit_label(pdf, "Fluxos de sucesso da implantação proposta; os caminhos da API são preservados.",
                  self.width / 2, 12, self.width - 24, 7.1)


def make_table(headers: list[str], rows: list[list[str]], styles: dict) -> Table:
    first = 0.31
    values = [[Paragraph(inline(cell), styles["cellhead"]) for cell in headers]]
    values.extend([Paragraph(inline(cell), styles["cell"]) for cell in row] for row in rows)
    result = Table(values, colWidths=[CONTENT * first, CONTENT * (1 - first)],
                   repeatRows=1, hAlign="LEFT")
    result.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), BLUE),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, PALE]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 9),
        ("RIGHTPADDING", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("LINEBELOW", (0, -1), (-1, -1), 0.5, LINE),
    ]))
    return result


def callout(text: str, styles: dict) -> Table:
    result = Table([[Paragraph(inline(text), styles["small"])]], colWidths=[CONTENT])
    result.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), PALE),
        ("LINEBEFORE", (0, 0), (0, -1), 3, BLUE),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
    ]))
    return result


class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.saved_pages = []

    def showPage(self):
        self.saved_pages.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        total = len(self.saved_pages)
        for state in self.saved_pages:
            self.__dict__.update(state)
            self.setFillColor(MUTED)
            self.setFont("DocSans", 7)
            self.drawRightString(WIDTH - MARGIN, 34, f"{self._pageNumber} / {total}")
            super().showPage()
        super().save()


def frame(pdf, document):
    pdf.saveState()
    pdf.setFillColor(BLUE)
    pdf.roundRect(MARGIN, HEIGHT - 58, 29, 27, 4, fill=1, stroke=0)
    pdf.setFillColor(WHITE)
    pdf.setFont("DocBold", 10)
    pdf.drawCentredString(MARGIN + 14.5, HEIGHT - 48, "TD")
    pdf.setFillColor(BLUE)
    pdf.setFont("DocBold", 10)
    pdf.drawString(MARGIN + 37, HEIGHT - 43, "TODO APP")
    pdf.setFillColor(MUTED)
    pdf.setFont("DocSans", 7)
    pdf.drawString(MARGIN + 37, HEIGHT - 55, "Engenharia de Software · 3º período")
    pdf.setStrokeColor(ORANGE)
    pdf.setLineWidth(1.5)
    pdf.line(WIDTH - MARGIN - 145, HEIGHT - 34, WIDTH - MARGIN, HEIGHT - 34)
    pdf.setFillColor(MUTED)
    pdf.setFont("DocSans", 6.7)
    pdf.drawRightString(WIDTH - MARGIN, HEIGHT - 47, "FEIRA DE PROFISSÕES / NUVEM")
    pdf.setStrokeColor(LINE)
    pdf.setLineWidth(0.5)
    pdf.line(MARGIN, 51, WIDTH - MARGIN, 51)
    pdf.setFillColor(MUTED)
    pdf.setFont("DocSans", 7)
    pdf.drawString(MARGIN, 34, "ToDo App · Escopo · v1.0 · 11/11/2026")
    pdf.restoreState()


def build_story(source: str, styles: dict) -> list:
    chunks = re.split(r"^## (.+)$", source, flags=re.MULTILINE)
    if len(chunks) != 15:
        raise ValueError("Esperadas sete partes de nível 2 no escopo.")
    story = []
    for page_index in range(7):
        title, content = chunks[page_index * 2 + 1:page_index * 2 + 3]
        if page_index:
            story.append(PageBreak())
        story.append(Paragraph(f"ESCOPO DO PROJETO / {page_index + 1:02d}", styles["eyebrow"]))
        story.append(Paragraph("Escopo" if page_index == 0 else escape(title),
                               styles["title" if page_index == 0 else "page"]))
        if page_index == 0:
            story.append(Paragraph("ToDo App · Implantação em nuvem para a Feira de Profissões", styles["lead"]))
        lines = content.strip().splitlines()
        index = 0
        while index < len(lines):
            line = lines[index].strip()
            if not line:
                index += 1
                continue
            if line.startswith("### "):
                story.append(Paragraph(inline(line[4:]), styles["section"]))
                index += 1
            elif line.startswith("```mermaid"):
                end = index + 1
                while end < len(lines) and not lines[end].startswith("```"):
                    end += 1
                if end == len(lines):
                    raise ValueError("Diagrama sem fechamento.")
                kind = lines[index + 1].strip()
                if kind.startswith("flowchart"):
                    story.append(Architecture())
                elif kind == "sequenceDiagram":
                    story.append(ApplicationFlow())
                else:
                    raise ValueError(f"Diagrama não suportado: {kind}")
                story.append(Spacer(1, 9))
                index = end + 1
            elif line.startswith("|"):
                block = []
                while index < len(lines) and lines[index].strip().startswith("|"):
                    block.append([cell.strip() for cell in lines[index].strip().strip("|").split("|")])
                    index += 1
                story.append(make_table(block[0], block[2:], styles))
                story.append(Spacer(1, 9))
            elif line.startswith("> "):
                story.append(callout(line[2:], styles))
                story.append(Spacer(1, 9))
                index += 1
            elif line.startswith("- "):
                story.append(Paragraph("• " + inline(line[2:]), styles["bullet"]))
                index += 1
            else:
                paragraph = [line]
                index += 1
                while index < len(lines) and lines[index].strip():
                    paragraph.append(lines[index].strip())
                    index += 1
                story.append(Paragraph(inline(" ".join(paragraph)), styles["body"]))
        while story and isinstance(story[-1], Spacer):
            story.pop()
    return story


def main() -> None:
    register_fonts()
    styles = theme()
    document = SimpleDocTemplate(
        str(OUT), pagesize=A4, leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=97, bottomMargin=65, title="Escopo — ToDo App",
        author="ToDo App · Engenharia de Software",
        subject="Implantação e operação em nuvem para a Feira de Profissões",
        pageCompression=1,
    )
    document.build(build_story(SOURCE.read_text(encoding="utf-8"), styles),
                   onFirstPage=frame, onLaterPages=frame, canvasmaker=NumberedCanvas)
    asset = ROOT / "docs" / "assets" / "fluxo-aplicacao.pdf"
    asset.parent.mkdir(parents=True, exist_ok=True)
    pdf = canvas.Canvas(str(asset), pagesize=(CONTENT + 48, 488))
    pdf.setTitle("ToDo App — Fluxo da implantação proposta")
    pdf.setAuthor("ToDo App · Engenharia de Software")
    pdf.setFillColor(BLUE)
    pdf.setFont("DocBold", 14)
    pdf.drawString(24, 461, "ToDo App · Fluxo da aplicação na nuvem")
    flow = ApplicationFlow()
    flow.canv = pdf
    pdf.saveState()
    pdf.translate(24, 24)
    flow.draw()
    pdf.restoreState()
    pdf.save()
    print(f"Gerado: {OUT}")
    print(f"Gerado: {asset}")


if __name__ == "__main__":
    main()
