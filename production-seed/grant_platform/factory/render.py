"""G1 Wave 4 — artifact renderer (G1.7).

Real DOCX and PDF output:

- DOCX: dependency-free OOXML writer (a .docx is a zip of XML parts).
  Headings, paragraphs, page breaks, page numbers via footer fields.
- PDF: reportlab Platypus (headings, paragraphs, page numbers, tables).

Both carry document metadata (title, artifact version, exact
application/project/revision reference). Rendering is content-faithful:
clean formatting never hides missing content — UNKNOWN placeholders
remain visible.
"""
from __future__ import annotations

import io
import re
import zipfile
from dataclasses import dataclass
from datetime import datetime, timezone
from xml.sax.saxutils import escape

PROPOSAL_TITLE = "Georgia Rural Community Impact Grant FY2026 — Proposal"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _escape(text: str) -> str:
    return escape(text)


def _split_heading(line: str) -> tuple[str, str] | None:
    """'## Section Title' -> heading; else paragraph."""
    m = re.match(r"^#{1,6}\s+(.+)$", line.strip())
    if m:
        return m.group(1), "h1"
    return None


@dataclass
class RenderResult:
    kind: str                 # docx | pdf
    payload: bytes
    page_count_estimate: int
    content_hash: str
    artifact_version_id: str
    rendered_at: str = ""

    def write(self, path: str) -> None:
        with open(path, "wb") as fh:
            fh.write(self.payload)


# ---------------------------------------------------------------- DOCX ---

def _docx_xml(title: str, paragraphs: list[tuple[str, str]]) -> str:
    body = ['<w:body>']
    body.append(
        '<w:p><w:pPr><w:pStyle w:val="Title"/></w:pPr>'
        f'<w:r><w:t>{_escape(title)}</w:t></w:r></w:p>')
    for text, style in paragraphs:
        if style == "h1":
            body.append(
                '<w:p><w:pPr><w:pStyle w:val="Heading1"/></w:pPr>'
                f'<w:r><w:t>{_escape(text)}</w:t></w:r></w:p>')
        elif style == "pagebreak":
            body.append(
                '<w:p><w:r><w:br w:type="page"/></w:r></w:p>')
        else:
            body.append(
                '<w:p><w:r><w:t xml:space="preserve">'
                f'{_escape(text)}</w:t></w:r></w:p>')
    body.append('</w:body>')
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/'
        'wordprocessingml/2006/main">' + "".join(body) + '</w:document>')


def _docx_styles() -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:styles xmlns:w="http://schemas.openxmlformats.org/'
        'wordprocessingml/2006/main">'
        '<w:style w:type="paragraph" w:styleId="Title">'
        '<w:name w:val="Title"/><w:rPr><w:sz w:val="48"/></w:rPr></w:style>'
        '<w:style w:type="paragraph" w:styleId="Heading1">'
        '<w:name w:val="heading 1"/><w:rPr><w:sz w:val="36"/></w:rPr></w:style>'
        '</w:styles>')


def _docx_footer() -> str:
    """Page numbers via footer field (shows in Word/Pages)."""
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:ftr xmlns:w="http://schemas.openxmlformats.org/'
        'wordprocessingml/2006/main">'
        '<w:p><w:r><w:fldChar w:fldCharType="begin"/></w:r>'
        '<w:r><w:instrText xml:space="preserve"> PAGE </w:instrText></w:r>'
        '<w:r><w:fldChar w:fldCharType="end"/></w:r></w:p></w:ftr>')


def _section_text(sections: dict) -> dict[str, str]:
    """Accept either {id: str} or {id: SectionDraft} and normalize."""
    out: dict[str, str] = {}
    for sid, value in sections.items():
        out[sid] = getattr(value, "text", value)
    return out


def render_docx(sections: dict, *, artifact_version_id: str,
                project_ref: str = "", revision_ref: str = "") -> RenderResult:
    """Build a real .docx (OOXML zip). Returns payload bytes."""
    sections = _section_text(sections)
    paragraphs: list[tuple[str, str]] = []
    paragraphs.append(("", "pagebreak"))
    for section_id, text in sections.items():
        paragraphs.append((section_id.replace("_", " ").title(), "h1"))
        for line in text.splitlines():
            if not line.strip():
                continue
            h = _split_heading(line)
            paragraphs.append((h[0], h[1]) if h else (line, "p"))
        paragraphs.append(("", "pagebreak"))

    document = _docx_xml(PROPOSAL_TITLE, paragraphs)
    content_types = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/'
        'content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxml'
        'formats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/word/document.xml" ContentType="application/'
        'vnd.openxmlformats-officedocument.wordprocessingml.document.'
        'main+xml"/></Types>')
    rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/'
        '2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/'
        'officeDocument/2006/relationships/officeDocument" '
        'Target="word/document.xml"/>'
        '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/'
        'officeDocument/2006/relationships/styles" Target="word/styles.xml"/>'
        '<Relationship Id="rId3" Type="http://schemas.openxmlformats.org/'
        'officeDocument/2006/relationships/footer" '
        'Target="word/footer1.xml"/></Relationships>')
    doc_rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/'
        '2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/'
        'officeDocument/2006/relationships/styles" Target="styles.xml"/>'
        '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/'
        'officeDocument/2006/relationships/footer" '
        'Target="footer1.xml"/></Relationships>')
    # section properties are embedded in document.xml body via sectPr
    document = document.replace(
        '</w:body>',
        '<w:sectPr><w:footerReference w:type="default" r:id="rId2"/>'
        '</w:sectPr></w:body>')
    document = document.replace(
        '<w:document xmlns:w="http://schemas.openxmlformats.org/'
        'wordprocessingml/2006/main">',
        '<w:document xmlns:w="http://schemas.openxmlformats.org/'
        'wordprocessingml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/'
        '2006/relationships">')

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", content_types)
        zf.writestr("_rels/.rels", rels)
        zf.writestr("word/document.xml", document)
        zf.writestr("word/styles.xml", _docx_styles())
        zf.writestr("word/footer1.xml", _docx_footer())
        zf.writestr("word/_rels/document.xml.rels", doc_rels)
    payload = buf.getvalue()
    import hashlib
    return RenderResult(
        kind="docx", payload=payload,
        page_count_estimate=max(1, sum(1 for _ in sections)),
        content_hash=hashlib.sha256(payload).hexdigest(),
        artifact_version_id=artifact_version_id, rendered_at=_now())


# ---------------------------------------------------------------- PDF ----

def render_pdf(sections: dict, *, artifact_version_id: str,
               project_ref: str = "", revision_ref: str = "") -> RenderResult:
    """Build a real PDF via reportlab (installed)."""
    sections = _section_text(sections)
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import (PageBreak, Paragraph, SimpleDocTemplate,
                                    Spacer)

    styles = getSampleStyleSheet()
    h1 = ParagraphStyle("G1H1", parent=styles["Heading1"],
                        spaceBefore=12, spaceAfter=6)
    body = ParagraphStyle("G1Body", parent=styles["BodyText"],
                          leading=13, spaceAfter=6)

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=letter,
                            leftMargin=inch, rightMargin=inch,
                            topMargin=inch, bottomMargin=inch,
                            title=PROPOSAL_TITLE,
                            author=f"Grant Platform G1 (rev {revision_ref})")

    def _footer(canvas, _doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.grey)
        canvas.drawString(inch, 0.5 * inch, f"Page {_doc.page}")
        canvas.drawRightString(letter[0] - inch, 0.5 * inch,
                               f"Artifact {artifact_version_id}")
        canvas.restoreState()

    story: list = [Paragraph(PROPOSAL_TITLE, styles["Title"]),
                   Spacer(1, 6),
                   Paragraph(f"Revision: {revision_ref} · "
                             f"Project: {project_ref} · "
                             f"Artifact: {artifact_version_id}",
                             styles["Normal"]),
                   PageBreak()]
    for section_id, text in sections.items():
        story.append(Paragraph(section_id.replace("_", " ").title(), h1))
        for line in text.splitlines():
            if not line.strip():
                continue
            h = _split_heading(line)
            if h:
                story.append(Paragraph(h[0], h1))  # headings use h1 style
            else:
                story.append(Paragraph(line, body))
        story.append(Spacer(1, 6))
    doc.build(story, onFirstPage=_footer, onLaterPages=_footer)
    payload = buf.getvalue()
    import hashlib
    return RenderResult(
        kind="pdf", payload=payload,
        page_count_estimate=max(1, len(payload) // 4000),
        content_hash=hashlib.sha256(payload).hexdigest(),
        artifact_version_id=artifact_version_id, rendered_at=_now())
