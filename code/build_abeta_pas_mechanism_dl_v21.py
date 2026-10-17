#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Render the independent v2.1-format Aβ/AChE-PAS mechanism & DL addendum.

This script intentionally writes only into the dated, independent delivery
folder. It does not alter the original v2, v3, or initial literature packet.

Usage:
  PYTHONPATH=/tmp/abeta-v2-render/lib/python3.*/site-packages \
    python3 code/build_abeta_pas_mechanism_dl_v21.py
"""
from __future__ import annotations

import csv
import hashlib
import re
from pathlib import Path

from docx import Document
from docx.enum.section import WD_ORIENT
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "deliverables" / "abeta_pc12_literature_review" / "机制与深度学习补充_v2格式_20261017"
MD = OUT / "Aβ促聚集_AChE-PAS_12条对接肽_机制与深度学习补充_v2.1.md"
DOCX = OUT / "Aβ促聚集_AChE-PAS_12条对接肽_机制与深度学习补充_v2.1.docx"
REFS = OUT / "机制与模型补充文献索引_v2.1.csv"
README = OUT / "README.md"
SUMS = OUT / "SHA256SUMS.txt"

REFERENCE_ROWS = [
    ("Inestrosa1996", "Inestrosa NC et al.", "1996", "Acetylcholinesterase Accelerates Assembly of Amyloid-β-Peptides into Alzheimer's Fibrils: Possible Role of the Peripheral Site of the Enzyme", "Neuron 16:881–891", "10.1016/S0896-6273(00)80108-7", "AChE–Aβ and PAS directionality control."),
    ("DeFerrari2001", "De Ferrari GV et al.", "2001", "A structural motif of acetylcholinesterase that promotes amyloid beta-peptide fibril formation", "Biochemistry 40:10447–10457", "10.1021/bi0101392", "Direct 35-aa AChE motif evidence; not proof for arbitrary short peptides."),
    ("Hou2014", "Hou LN et al.", "2014", "A New Motif in the N-Terminal of Acetylcholinesterase Triggers Amyloid-β Aggregation and Deposition", "CNS Neurosci Ther 20:59–66", "10.1111/cns.12161", "AChE7–20 β-hairpin peptide mechanism precedent."),
    ("Tian2025", "Tian Y et al.", "2025", "The p3 peptides (Aβ17–40/42) rapidly form amyloid fibrils that cross-seed with full-length Aβ", "Nature Communications 16:2040", "10.1038/s41467-025-57341-4", "Recent, sequence/terminus-selective Aβ cross-seeding evidence."),
    ("Cruceta2023", "Cruceta L et al.", "2023", "Modulation of aggregation and structural polymorphisms of β-amyloid fibrils in cellular environments by pyroglutamate-3 variant cross-seeding", "Journal of Biological Chemistry 299:105196", "10.1016/j.jbc.2023.105196", "Cell-context cross-seeding/structural polymorphism evidence; not PC12."),
    ("Vugmeyster2021", "Vugmeyster L et al.", "2021", "Cross-Seeded Fibrillation Induced by Pyroglutamate-3 and Truncated Aβ40 Variants Leads to Aβ40 Structural Polymorphism Modulation and Elevated Toxicity", "ACS Chemical Neuroscience", "10.1021/acschemneuro.1c00341", "Earlier pyroE3/truncated Aβ cross-seed evidence."),
    ("Zhang2024", "Zhang et al.", "2024", "Exploring pathological link between antimicrobial and amyloid peptides", "Chemical Society Reviews 53:8713–8763", "10.1039/D3CS00878A", "Cross-seeding, AMP/amyloid context, and directionality review."),
    ("FoodAmyloid2023", "Klement et al.", "2023", "Food protein-derived amyloids do not accelerate amyloid β aggregation", "Scientific Reports", "10.1038/s41598-023-28147-5", "Negative control: amyloid-like material need not accelerate Aβ."),
    ("Wang2023", "Wang B, Razavi S, Gamazon ER", "2023", "Towards mechanistic models of mutational effects: Deep learning on Alzheimer’s Aβ peptide", "Computational and Structural Biotechnology Journal 21:2434–2445", "10.1016/j.csbj.2023.03.051", "Aβ42 mutation/nucleation model, not an exogenous-peptide model."),
    ("Thompson2025", "Thompson M et al.", "2025", "Massive experimental quantification allows interpretable deep learning of protein aggregation", "Science Advances 11:eadt5111", "10.1126/sciadv.adt5111", "CANYA: random 20-aa Sup35N-fusion aggregation domain."),
    ("Eschbach2026", "Eschbach E et al.", "2026", "Predicting Peptide Aggregation with Protein Language Model Embeddings", "Journal of Chemical Information and Modeling", "10.1021/acs.jcim.6c00577", "PALM: intrinsic aggregation/APR, with Aβ mutation limitations."),
    ("Perez2023", "Perez R et al.", "2023", "AggBERT: Best in Class Prediction of Hexapeptide Amyloidogenesis with a Semi-Supervised ProtBERT Model", "Journal of Chemical Information and Modeling 63:5727–5733", "10.1021/acs.jcim.3c00817", "Hexapeptide self-amyloid model; use only as a sliding-window flag."),
    ("He2025", "He W et al.", "2025", "AggNet: Advancing protein aggregation analysis through deep learning and protein language model", "Protein Science 34:e70031", "10.1002/pro.70031", "Additional intrinsic aggregation prediction baseline."),
    ("Shearman1994", "Shearman MS et al.", "1994", "Inhibition of PC12 cell redox activity is a specific, early indicator of the mechanism of beta-amyloid-mediated cell death", "PNAS 91:1470–1474", "10.1073/pnas.91.4.1470", "PC12 redox viability boundary; single viability readout is insufficient."),
    ("Rathore2025", "Rathore AS et al.", "2025", "A large language model for predicting neurotoxic peptides and neurotoxins", "Protein Science 34:e70200", "10.1002/pro.70200", "NTxPred2 is general neurotoxicity, not PC12/Aβ co-exposure."),
    ("Rathore2024", "Rathore AS, Choudhury S, Arora A, Tijare P, Raghava GPS", "2024", "ToxinPred 3.0: An improved method for predicting the toxicity of peptides", "Computers in Biology and Medicine 179:108926", "10.1016/j.compbiomed.2024.108926", "General peptide toxicity; input length fits current 7–9 aa peptides, but it is not a PC12/Aβ model."),
    ("Zhang2025ToxMSRC", "Zhang S, Ren J, Liang Y, et al.", "2025", "An innovative peptide toxicity prediction model based on multi-scale convolutional neural network and residual connection", "Bioinformatics 41:btaf462", "10.1093/bioinformatics/btaf462", "General peptide toxicity model with declared 11–50 aa length domain; exclude current 7–9 aa peptides."),
    ("PeptiTox2025", "PeptiTox authors", "2025", "Integrating Protein Language Models and Geometric Deep Learning for Peptide Toxicity Prediction", "Journal of Chemical Information and Modeling 65:7800–7810", "10.1021/acs.jcim.5c01073", "Structure-aware general peptide toxicity model; not PC12/Aβ."),
    ("BiToxNet2026", "BiToxNet authors", "2026", "BiToxNet: a deep learning framework integrating multimodal features for accurate identification of neurotoxic peptides and proteins", "BMC Biology", "10.1186/s12915-026-02508-8", "General neurotoxic peptide classifier, not PC12/Aβ."),
    ("NToxSEM2026", "NToxSEM authors", "2026", "NToxSEM: Enhancing prediction of neurotoxic peptides and neurotoxins using a stacked ensemble-based multimodal framework", "Protein Science", "10.1002/pro.70661", "General neurotoxic peptide ensemble, not PC12/Aβ."),
    ("AB2535Membrane2019", "Aβ25–35 membrane aggregation authors", "2019", "De novo aggregation of Alzheimer’s Aβ25–35 peptides in a lipid bilayer", "Scientific Reports", "10.1038/s41598-019-43685-7", "Aggregation/membrane mechanism context; not direct evidence for candidate short peptides."),
]


def clean_inline(text: str) -> str:
    """Expose Markdown link targets and strip syntax without adding scientific text."""
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1 (\2)", text)
    return text.replace("**", "").replace("`", "").strip()


def set_font(run, *, size: float, bold: bool = False, color: str = "263238") -> None:
    run.font.name = "Microsoft YaHei"
    run._element.rPr.rFonts.set(qn("w:eastAsia"), "Microsoft YaHei")
    run.font.size = Pt(size)
    run.bold = bold
    run.font.color.rgb = RGBColor.from_string(color)


def shade(cell, fill: str) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), fill)
    tc_pr.append(shd)


def set_repeat_table_header(row) -> None:
    tr_pr = row._tr.get_or_add_trPr()
    tbl_header = OxmlElement("w:tblHeader")
    tbl_header.set(qn("w:val"), "true")
    tr_pr.append(tbl_header)


def set_cell(cell, text: str, *, header: bool = False) -> None:
    cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.TOP
    cell.text = ""
    p = cell.paragraphs[0]
    p.paragraph_format.space_after = Pt(1.2)
    p.paragraph_format.line_spacing = 1.0
    run = p.add_run(clean_inline(text))
    set_font(run, size=7.1 if header else 6.8, bold=header, color="FFFFFF" if header else "263238")
    if header:
        shade(cell, "07576C")


def parse_table(lines: list[str]) -> list[list[str]]:
    rows: list[list[str]] = []
    for line in lines:
        if re.match(r"^\|\s*:?-{3,}", line):
            continue
        cells = [part.strip() for part in line.strip().split("|")[1:-1]]
        if cells:
            rows.append(cells)
    return rows


def add_table(doc: Document, raw_lines: list[str]) -> None:
    rows = parse_table(raw_lines)
    if not rows:
        return
    col_count = max(len(row) for row in rows)
    table = doc.add_table(rows=0, cols=col_count)
    table.style = "Table Grid"
    table.autofit = True
    for row_index, values in enumerate(rows):
        cells = table.add_row().cells
        for col_index in range(col_count):
            set_cell(cells[col_index], values[col_index] if col_index < len(values) else "", header=(row_index == 0))
        if row_index == 0:
            set_repeat_table_header(table.rows[0])
    doc.add_paragraph("")


def add_rule(doc: Document) -> None:
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(1)
    p.paragraph_format.space_after = Pt(3)
    run = p.add_run("─" * 120)
    set_font(run, size=5.5, color="B0BEC5")


def render_docx() -> None:
    doc = Document()
    section = doc.sections[0]
    section.orientation = WD_ORIENT.LANDSCAPE
    section.page_width, section.page_height = section.page_height, section.page_width
    section.left_margin = Inches(0.50)
    section.right_margin = Inches(0.50)
    section.top_margin = Inches(0.46)
    section.bottom_margin = Inches(0.46)

    for style_name, size in (("Normal", 8.8), ("Title", 19), ("Heading 1", 13.5), ("Heading 2", 11.0)):
        style = doc.styles[style_name]
        style.font.name = "Microsoft YaHei"
        style._element.rPr.rFonts.set(qn("w:eastAsia"), "Microsoft YaHei")
        style.font.size = Pt(size)
    doc.styles["Normal"].paragraph_format.space_after = Pt(3)

    header = section.header.paragraphs[0]
    header.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    hrun = header.add_run("独立研究备忘｜Aβ 促聚集 / AChE–PAS / PC12｜机制与深度学习补充 v2.1")
    set_font(hrun, size=7.2, color="607D8B")
    footer = section.footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    frun = footer.add_run("2026-10-17 Asia/Shanghai｜预测与 docking/MD 均是待实验检验的假说；不构成当前 12 条肽的既成机制结论")
    set_font(frun, size=7.2, color="607D8B")

    lines = MD.read_text(encoding="utf-8").splitlines()
    index = 0
    while index < len(lines):
        line = lines[index]
        if line.startswith("|"):
            table_lines: list[str] = []
            while index < len(lines) and lines[index].startswith("|"):
                table_lines.append(lines[index])
                index += 1
            add_table(doc, table_lines)
            continue
        if line.startswith("# "):
            p = doc.add_paragraph(style="Title")
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = p.add_run(clean_inline(line[2:]))
            set_font(run, size=18.5, bold=True, color="0D3443")
        elif line.startswith("## "):
            p = doc.add_paragraph(style="Heading 1")
            p.paragraph_format.space_before = Pt(7)
            run = p.add_run(clean_inline(line[3:]))
            set_font(run, size=13.4, bold=True, color="07576C")
        elif line.startswith("### "):
            p = doc.add_paragraph(style="Heading 2")
            p.paragraph_format.space_before = Pt(4)
            run = p.add_run(clean_inline(line[4:]))
            set_font(run, size=10.8, bold=True, color="A04431")
        elif line.strip() == "---":
            add_rule(doc)
        elif line.startswith("- "):
            p = doc.add_paragraph(style="List Bullet")
            p.paragraph_format.space_after = Pt(1.2)
            run = p.add_run(clean_inline(line[2:]))
            set_font(run, size=8.7)
        elif re.match(r"^\d+\. ", line):
            p = doc.add_paragraph(style="List Number")
            p.paragraph_format.space_after = Pt(1.2)
            run = p.add_run(clean_inline(re.sub(r"^\d+\. ", "", line)))
            set_font(run, size=8.7)
        elif line.strip():
            p = doc.add_paragraph()
            p.paragraph_format.space_after = Pt(2)
            run = p.add_run(clean_inline(line))
            set_font(run, size=8.7)
        index += 1
    doc.save(DOCX)


def write_references() -> None:
    with REFS.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(["cite_key", "authors", "year", "title", "venue", "doi", "doi_url", "why_used_in_v2_1"])
        for cite_key, authors, year, title, venue, doi, reason in REFERENCE_ROWS:
            writer.writerow([cite_key, authors, year, title, venue, doi, f"https://doi.org/{doi}", reason])


def write_readme() -> None:
    README.write_text(
        """# 机制与深度学习补充（v2.1 格式，独立目录）

本目录是为“Aβ 病理机制中促进 Aβ 聚集、AChE–PAS、交叉成核、PC12 损伤及可用深度学习模型”重做的**独立**交付。结构沿用既有 v2 的结论先行、数据边界、12 肽分层、计算模型适用性、可证伪实验、Go/No-go 和写作措辞；没有覆盖原始初版、既有 v2 或 v3。

## 文件

- `Aβ促聚集_AChE-PAS_12条对接肽_机制与深度学习补充_v2.1.docx`：可直接审阅/批注的 Word 版本。
- `Aβ促聚集_AChE-PAS_12条对接肽_机制与深度学习补充_v2.1.md`：同内容、可搜索且便于粘贴的 Markdown 源稿。
- `机制与模型补充文献索引_v2.1.csv`：关键机制与模型文献的 DOI 级审计索引。
- `SHA256SUMS.txt`：最终交付文件的完整性校验；本地同步后可用 `sha256sum -c SHA256SUMS.txt`（或同等工具）复核。
- `code/build_abeta_pas_mechanism_dl_v21.py`：独立渲染脚本（位于仓库 `code/`）。

## 重要边界

1. AChE 35-aa motif、AChE7–20、p3、pyroE3/ΔE3-Aβ 是有证据的机制先例/阳性对照框架，**不是**当前 12 条 7–9 aa 肽已经生效的证据。
2. PALM/CANYA/AggBERT/AggNet 预测的是自身聚集或局部 amyloidogenicity；Wang 2023 是 Aβ42 单点变体模型；这些不是“外源肽促进 Aβ”预测器。
3. NTxPred2/BiToxNet/NToxSEM 是一般神经毒性预测器；ToxinPred3/PeptiTox 是一般肽毒性预测器；它们都**不是** Aβ 共暴露下的 PC12 CCK-8、LDH、ROS、线粒体膜电位或凋亡预测器。ToxMSRC 仅覆盖 11–50 aa，故不适用于当前 7–9 aa 候选。
4. 计算输出应保留为独立旗标，不能相加成“促 Aβ/促 PC12 总分”。
5. `E:\\0github\\git-sync\\...` 不是本沙箱可直接写入的位置；本目录已写入仓库工作区。是否同步到 Windows 硬盘应以用户本地同步回执为准。

## 重建

```bash
python3 -m venv /tmp/abeta-v2-render
/tmp/abeta-v2-render/bin/pip install python-docx
/tmp/abeta-v2-render/bin/python code/build_abeta_pas_mechanism_dl_v21.py
```

渲染脚本只会生成本目录的 DOCX、CSV 与 README。
""",
        encoding="utf-8",
    )


def write_checksums() -> None:
    """Write checksums only after all final delivery files are complete."""
    delivery_files = (DOCX, MD, REFS, README)
    lines = []
    for path in delivery_files:
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        lines.append(f"{digest}  {path.name}")
    SUMS.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    if not MD.exists():
        raise FileNotFoundError(MD)
    OUT.mkdir(parents=True, exist_ok=True)
    render_docx()
    write_references()
    write_readme()
    write_checksums()
    for path in (DOCX, REFS, README, SUMS):
        print(f"built {path.relative_to(ROOT)} ({path.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
