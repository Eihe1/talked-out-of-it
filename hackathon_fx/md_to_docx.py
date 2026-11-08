"""Convert REPORT_FINAL.md to a .docx close to the Apart template (serif 11 pt, 1.15 spacing, 1-inch margins),
so it can be pasted into the Google Docs template and its page count checked.

  python -X utf8 md_to_docx.py ../REPORT_FINAL.md ../REPORT_FINAL.docx
"""
import re
import sys
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt

FONT = "Cambria"


def add_runs(par, text):
    # **bold**, *italic*, `code`
    for tok in re.split(r"(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`)", text):
        if not tok:
            continue
        if tok.startswith("**"):
            r = par.add_run(tok[2:-2]); r.bold = True
        elif tok.startswith("*"):
            r = par.add_run(tok[1:-1]); r.italic = True
        elif tok.startswith("`"):
            r = par.add_run(tok[1:-1]); r.font.name = "Consolas"
        else:
            r = par.add_run(tok)


def main(src: str, dst: str) -> None:
    base = Path(src).resolve().parent
    lines = Path(src).read_text(encoding="utf-8").splitlines()
    doc = Document()
    for s in doc.sections:
        s.left_margin = s.right_margin = s.top_margin = s.bottom_margin = Inches(1)
    st = doc.styles["Normal"]
    st.font.name = FONT
    st.font.size = Pt(11)
    st.paragraph_format.line_spacing = 1.15
    st.paragraph_format.space_after = Pt(6)
    i, para = 0, []

    def flush():
        if para:
            p = doc.add_paragraph()
            add_runs(p, " ".join(para))
            para.clear()

    while i < len(lines):
        ln = lines[i].rstrip()
        if not ln.strip() or ln.strip() == "---":
            flush(); i += 1; continue
        if ln.startswith("# "):
            flush(); p = doc.add_paragraph(); r = p.add_run(ln[2:]); r.bold = True; r.font.size = Pt(16)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER; i += 1; continue
        if ln.startswith("## ") or ln.startswith("### "):
            flush(); doc.add_heading(ln.lstrip("#").strip(), level=1 if ln.startswith("## ") else 2); i += 1; continue
        m = re.match(r"!\[[^\]]*\]\(([^)]+)\)", ln)
        if m:
            flush(); path = base / m.group(1)
            width = Inches(6.5) if path.name in ("fig1_persuasion_and_channels.png", "fig_main.png") else Inches(3.4)
            doc.add_picture(str(path), width=width)
            doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER; i += 1; continue
        if ln.startswith("|"):
            flush(); rows = []
            while i < len(lines) and lines[i].startswith("|"):
                if not re.match(r"^\|[-| ]+\|$", lines[i].strip()):
                    rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            t = doc.add_table(rows=len(rows), cols=len(rows[0]))
            t.style = "Table Grid"
            for r, row in enumerate(rows):
                for c, cell in enumerate(row):
                    cp = t.cell(r, c).paragraphs[0]
                    add_runs(cp, cell)
                    for run in cp.runs:
                        run.font.size = Pt(9)
                        run.bold = run.bold or r == 0
            doc.add_paragraph()
            continue
        if re.match(r"^(- |\d+\. )", ln):
            flush()
            item = re.sub(r"^(- |\d+\. )", "", ln)
            i += 1
            while i < len(lines) and lines[i].startswith("  ") and lines[i].strip():
                item += " " + lines[i].strip(); i += 1
            p = doc.add_paragraph(style="List Bullet" if ln.startswith("- ") else "List Number")
            add_runs(p, item)
            continue
        para.append(ln.strip()); i += 1
    flush()
    doc.save(dst)
    print("wrote", dst)


if __name__ == "__main__":
    main(*sys.argv[1:3])
