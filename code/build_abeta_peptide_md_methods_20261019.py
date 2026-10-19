#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Render the SCI-style MD protocol document for candidate-peptide-promoted Aβ aggregation.

Run with a Python environment containing python-docx, e.g.:
  PYTHONPATH=/tmp/arena-docx python3 code/build_abeta_peptide_md_methods_20261019.py

The Google Drive upload is intentionally not performed by this renderer.
"""
from __future__ import annotations

from pathlib import Path

from docx import Document
from docx.enum.section import WD_ORIENT
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "deliverables" / "abeta_pc12_literature_review" / "MD动力学方案_20261019"
DOCX = OUT / "Aβ促聚集_候选短肽_MD动力学方案_参数与文献支持_20261019.docx"

# Palette chosen to make published precedent, proposed parameters, and limitations visibly distinct.
NAVY = "0B3954"
TEAL = "0A6974"
SLATE = "34495E"
BLUE = "1F5A94"
GREEN = "1B6B4D"
RED = "9E2A2B"
PALE_BLUE = "EAF3F8"
PALE_GREEN = "EAF5EE"
PALE_RED = "FCEDEC"
PALE_GREY = "F4F6F7"
WHITE = "FFFFFF"


def font(run, size: float = 8.7, bold: bool = False, color: str = SLATE,
         italic: bool = False) -> None:
    run.font.name = "Arial"
    run._element.rPr.rFonts.set(qn("w:eastAsia"), "Microsoft YaHei")
    run._element.rPr.rFonts.set(qn("w:ascii"), "Arial")
    run._element.rPr.rFonts.set(qn("w:hAnsi"), "Arial")
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    run.font.color.rgb = RGBColor.from_string(color)


def shade(cell, fill: str) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), fill)
    tc_pr.append(shd)


def set_cell_border(cell, **kwargs) -> None:
    """Set cell borders; kwargs side -> {val, sz, color, space}."""
    tc = cell._tc
    tc_pr = tc.get_or_add_tcPr()
    tc_borders = tc_pr.first_child_found_in("w:tcBorders")
    if tc_borders is None:
        tc_borders = OxmlElement("w:tcBorders")
        tc_pr.append(tc_borders)
    for edge, data in kwargs.items():
        tag = "w:" + edge
        element = tc_borders.find(qn(tag))
        if element is None:
            element = OxmlElement(tag)
            tc_borders.append(element)
        for key, value in data.items():
            element.set(qn("w:" + key), str(value))


def set_repeat_table_header(row) -> None:
    tr_pr = row._tr.get_or_add_trPr()
    header = OxmlElement("w:tblHeader")
    header.set(qn("w:val"), "true")
    tr_pr.append(header)


def set_cell_text(cell, text: str, *, header: bool = False, size: float = 7.1,
                  color: str | None = None, fill: str | None = None,
                  bold: bool | None = None) -> None:
    cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.TOP
    cell.text = ""
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(1.0)
    p.paragraph_format.line_spacing = 1.0
    r = p.add_run(text)
    font(r, size=size, bold=header if bold is None else bold,
         color=WHITE if header and color is None else (color or SLATE))
    if fill:
        shade(cell, fill)
    elif header:
        shade(cell, NAVY)
    set_cell_border(cell,
                    top={"val": "single", "sz": "3", "color": "D5DDE2"},
                    bottom={"val": "single", "sz": "3", "color": "D5DDE2"},
                    left={"val": "single", "sz": "3", "color": "D5DDE2"},
                    right={"val": "single", "sz": "3", "color": "D5DDE2"})


def paragraph(doc: Document, text: str = "", *, size: float = 8.7, bold: bool = False,
              color: str = SLATE, italic: bool = False, align=None,
              before: float = 0, after: float = 2.2, line: float = 1.05,
              style: str | None = None):
    p = doc.add_paragraph(style=style)
    if align is not None:
        p.alignment = align
    p.paragraph_format.space_before = Pt(before)
    p.paragraph_format.space_after = Pt(after)
    p.paragraph_format.line_spacing = line
    r = p.add_run(text)
    font(r, size=size, bold=bold, color=color, italic=italic)
    return p


def heading(doc: Document, text: str, level: int = 1) -> None:
    if level == 1:
        size, color, before = 13.2, NAVY, 9
    elif level == 2:
        size, color, before = 10.7, TEAL, 6
    else:
        size, color, before = 9.4, BLUE, 4
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(before)
    p.paragraph_format.space_after = Pt(2.8)
    p.paragraph_format.keep_with_next = True
    r = p.add_run(text)
    font(r, size=size, bold=True, color=color)


def bullet(doc: Document, text: str, *, level: int = 0, size: float = 8.35,
           color: str = SLATE) -> None:
    p = doc.add_paragraph(style="List Bullet" if level == 0 else "List Bullet 2")
    p.paragraph_format.space_after = Pt(0.9)
    p.paragraph_format.line_spacing = 1.0
    r = p.add_run(text)
    font(r, size=size, color=color)


def numbered(doc: Document, text: str, *, size: float = 8.35) -> None:
    p = doc.add_paragraph(style="List Number")
    p.paragraph_format.space_after = Pt(1.0)
    p.paragraph_format.line_spacing = 1.0
    r = p.add_run(text)
    font(r, size=size, color=SLATE)


def rule(doc: Document) -> None:
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(1)
    p.paragraph_format.space_after = Pt(3)
    r = p.add_run("─" * 175)
    font(r, size=4.5, color="B9C4CA")


def label(doc: Document, title: str, text: str, *, kind: str) -> None:
    if kind == "published":
        border, fill = BLUE, PALE_BLUE
    elif kind == "proposed":
        border, fill = GREEN, PALE_GREEN
    else:
        border, fill = RED, PALE_RED
    table = doc.add_table(rows=1, cols=1)
    table.autofit = False
    table.columns[0].width = Cm(26.6)
    cell = table.cell(0, 0)
    shade(cell, fill)
    set_cell_border(cell,
                    top={"val": "single", "sz": "9", "color": border},
                    bottom={"val": "single", "sz": "4", "color": border},
                    left={"val": "single", "sz": "9", "color": border},
                    right={"val": "single", "sz": "4", "color": border})
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(1.6)
    p.paragraph_format.space_after = Pt(1.8)
    p.paragraph_format.line_spacing = 1.02
    r = p.add_run(title + "  ")
    font(r, size=8.1, bold=True, color=border)
    r = p.add_run(text)
    font(r, size=8.05, color=SLATE)
    paragraph(doc, "", size=2.0, after=1.2)


def table(doc: Document, headers: list[str], rows: list[list[str]], widths: list[float] | None = None,
          font_size: float = 6.85) -> None:
    t = doc.add_table(rows=1, cols=len(headers))
    t.style = "Table Grid"
    t.autofit = False
    if widths:
        for col, width in zip(t.columns, widths):
            col.width = Cm(width)
    for i, head in enumerate(headers):
        set_cell_text(t.rows[0].cells[i], head, header=True, size=font_size + 0.15)
    set_repeat_table_header(t.rows[0])
    for ridx, values in enumerate(rows):
        cells = t.add_row().cells
        for i, value in enumerate(values):
            fill = PALE_GREY if ridx % 2 else WHITE
            set_cell_text(cells[i], value, size=font_size, fill=fill)
    paragraph(doc, "", size=2.0, after=1.4)


def page_break(doc: Document) -> None:
    p = doc.add_paragraph()
    p.add_run().add_break(WD_BREAK.PAGE)


def configure(doc: Document) -> None:
    sec = doc.sections[0]
    sec.orientation = WD_ORIENT.LANDSCAPE
    sec.page_width, sec.page_height = sec.page_height, sec.page_width
    sec.left_margin = Cm(1.20)
    sec.right_margin = Cm(1.20)
    sec.top_margin = Cm(1.10)
    sec.bottom_margin = Cm(1.10)
    sec.header_distance = Cm(0.55)
    sec.footer_distance = Cm(0.55)

    normal = doc.styles["Normal"]
    normal.font.name = "Arial"
    normal._element.rPr.rFonts.set(qn("w:eastAsia"), "Microsoft YaHei")
    normal.font.size = Pt(8.7)
    normal.paragraph_format.space_after = Pt(2.2)

    # Create two list styles deterministically because templates vary across installations.
    for name, left in (("List Bullet", 0.45), ("List Bullet 2", 0.90), ("List Number", 0.45)):
        try:
            style = doc.styles[name]
        except KeyError:
            style = doc.styles.add_style(name, WD_STYLE_TYPE.PARAGRAPH)
        style.font.name = "Arial"
        style._element.rPr.rFonts.set(qn("w:eastAsia"), "Microsoft YaHei")
        style.paragraph_format.left_indent = Cm(left)
        style.paragraph_format.first_line_indent = Cm(-0.30)

    header = sec.header.paragraphs[0]
    header.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    header.paragraph_format.space_after = Pt(0)
    r = header.add_run("Aβ 促聚集候选短肽｜MD 动力学方案、定量终点与文献支持｜2026-10-19")
    font(r, size=7.0, color="607D8B")

    footer = sec.footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = footer.add_run("仅方法学文件；“候选肽促 Aβ 聚集”在本项目中是待检验假说，除非另有实验/动力学证据。")
    font(r, size=7.0, color="607D8B")

    props = doc.core_properties
    props.title = "Aβ促聚集候选短肽：MD动力学方案、参数与文献支持"
    props.subject = "SCI-style molecular-dynamics methods for peptide-promoted Aβ aggregation"
    props.author = "Arena.ai Agent Mode"
    props.keywords = "Aβ, amyloid aggregation, molecular dynamics, cross-seeding, AChE, kinetics"


def title_page(doc: Document) -> None:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(7)
    p.paragraph_format.space_after = Pt(5)
    r = p.add_run("候选短肽促进 Aβ 聚集的分子动力学方案")
    font(r, size=20.0, bold=True, color=NAVY)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(8)
    r = p.add_run("具体实施、模拟参数、可量化终点、判定规则与逐项文献支持")
    font(r, size=11.0, bold=True, color=TEAL)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(6)
    r = p.add_run("SCI 方法学写法｜适用于既有 12 条 7–9 aa AChE 对接候选肽｜2026-10-19")
    font(r, size=8.5, color="607D8B")
    rule(doc)
    paragraph(doc,
              "范围：本文件只规定“肽促进 Aβ 聚集”假说的 MD/动力学检验路径。它不把 AChE–PAS docking、短肽自身 APR、单次结合或增强采样轨迹误写为候选肽已促进 Aβ 聚集。",
              size=8.5, bold=True, color=SLATE, align=WD_ALIGN_PARAGRAPH.CENTER, after=4)

    table(doc,
          ["证据层级", "可作出的陈述", "本项目 12 条 7–9 aa 候选肽的含义"],
          [
              ["直接机制正例", "Aβ16–22 预形成纤维能表面催化 Aβ40 二级成核；可溶 IAPP 能促 Aβ42 共聚集；IAPP 纤维可催化 Aβ 成核；p3 与 C 端长度匹配的 Aβ 发生交叉播种 [1–4]。", "这些文献证明“肽/肽纤维可以促进 Aβ 聚集”这一机制类别真实存在，但不证明任一当前候选肽有效。"],
              ["方法与参数先例", "全原子 cMD、多拷贝 DMD/REXDMD、种子表面/端部 DMD、AChE–Aβ aMD、CG one-pot MD、REST2、WTMetaD、WE 与 MSM 均有对应文献依据 [1,2,5–15]。", "可复制其体系逻辑或参数量级；替换为候选序列后的结果仍为新数据。"],
              ["不可替代的证据", "增强采样的平衡 FES/PMF ≠ 真实 lag time；AChE PAS 占位 ≠ 促聚集；CG 轨迹时间 ≠ 生理物理时间。", "只有经过无偏/速率框架验证的事件统计，外加独立实验动力学，才可支持“促进”的因果性表述。"],
          ],
          widths=[4.1, 12.4, 11.1], font_size=7.05)


def shared_design(doc: Document) -> None:
    heading(doc, "1. 共同设计、体系定义与最小质量控制", 1)
    table(doc,
          ["项目", "固定或推荐设定", "参数来源/用途"],
          [
              ["Aβ 构型", "早期异源共聚集、AChE 三元体系优先 Aβ42；复现实验证实的表面二级成核优先 Aβ40。Aβ N 端 NH3+、C 端 COO−，pH 7.4；若使用实际封端/修饰肽，必须用其真实端基。", "Bunce 的直接表面催化正例为 Aβ40 [1]；Ge、Wu、Fan 的异源早期聚集均包含 Aβ42 [2,5,6]。"],
              ["候选肽", "12 条 7–9 aa 肽逐条建模；每一条均设 Aβ 单独、候选肽单独、Aβ+候选肽、Aβ+组成相同乱序肽（可合成时）四类。乱序肽不作为 AChE docking 对照，只作为序列依赖的共聚集负对照。", "本项目推荐；防止把非特异性拥挤或自聚集误判为 Aβ 促进。"],
              ["显式水全原子基线", "GROMACS；CHARMM36m 蛋白力场/CHARMM-modified TIP3P 水；0.15 M NaCl；PBC；310 K、1 bar；2 fs；PME；库仑与 LJ 截断 1.2 nm；LINCS；v-rescale τT=1 ps；Parrinello–Rahman τP=5 ps。命中体系以 a99SB-disp 及其匹配水模型复算。", "CHARMM36m 与 a99SB-disp 都针对 IDP/无序肽校准 [9,10]。具体 GROMACS 细节是本项目推荐；Wu 的 Aβ 多拷贝显式水 MD 提供 GROMACS/AMBER99SB-ILDN/OPC/310 K/1 atm/2 fs 的独立先例 [6]。"],
              ["初始条件与重复", "每一条件至少 5 个独立随机位置/朝向 × 独立速度种子；初始任意两肽表面距离 ≥1.2 nm（无偏全原子）或按文献 DMD 要求放置。轨迹、随机种子、拓扑与分析脚本全量保存。", "本项目推荐；避免单一预组装接触主导结论。"],
              ["统一结构定义", "重原子接触：最小距离 <0.55 nm；骨架氢键：N···O ≤0.35 nm、N–H···O ≥120°（DMD 文献定义）。β 含量用 DSSP；簇以至少一个跨肽接触连通。", "Fan 的原始分析定义 [5]；全原子体系同阈值便于跨方法比较。"],
              ["统计单位", "独立重复（而非单帧）是统计单位。报告每重复末 20% 平稳窗口与全时程；95% bootstrap CI；12 肽同时筛选时用 Benjamini–Hochberg FDR q<0.10。", "本项目推荐；防止伪重复。"],
          ],
          widths=[4.0, 13.9, 9.7], font_size=6.65)
    label(doc, "术语限制", "本文把“动力学”限定为可定义的首达时间、通量、MFPT、速率常数或经验证的 MSM/iMetaD 结果。T-REMD/REST2、常规 WTMetaD、umbrella sampling 输出的是平衡构象、FES 或 PMF；除非另行通过速率框架验证，绝不将其时间轴报作聚集速率。", kind="limit")


def protocol_1(doc: Document) -> None:
    heading(doc, "2. 方法 1：多拷贝无偏早期异源共聚集（DMD 初筛 + 显式水全原子复核）", 1)
    paragraph(doc, "目的：在不预设候选肽纤维的前提下，检验候选单体是否提高 Aβ–Aβ 接触、β 富集异源簇或早期 Aβ 低聚事件的概率。该方法检验的是早期机制，而不是宏观 ThT lag time。", size=8.45)
    label(doc, "已发表原始参数", "Fan 等：3 Aβ42 + 3 hIAPP，10.0 nm 立方盒，60 条独立 atomistic-DMD 轨迹，每条 0.60 μs，300 K，Medusa/EEF1、Debye 长度约 10 Å、Andersen thermostat；用 DSSP、接触、骨架氢键、最大簇和二维 FES 分析 [5]。Wu 等还给出 8 Aβ + 8 环肽、约 4 mM、显式水全原子多拷贝 MD 的互补先例 [6]。", kind="published")
    label(doc, "当前项目推荐参数", "阶段 1（12 肽全筛）：每条候选肽采用 3 Aβ42 + 3 候选肽、10.0 nm 立方盒、300 K、60 × 0.60 μs atomistic-DMD；Aβ 单独、候选单独和 Aβ+乱序肽采用相同重复。阶段 2（仅通过阶段 1 的候选）：4 Aβ42 + 4 候选肽于 11.0 nm 立方盒（每种约 5 mM），显式水全原子 10 × 1.0 μs；另以 18.8 nm 立方盒（每种约 1 mM）进行 5 × 2.0 μs 确认。", kind="proposed")
    table(doc,
          ["操作顺序", "实施细节", "量化终点与判定"],
          [
              ["体系建立", "Aβ42 与候选肽均从 ≥3 个独立初始构象随机旋转/平移；不得以 docking pose 作为唯一共聚集起点。显式水体系先最小化、100 ps NVT、1 ns NPT，再无约束生产。", "记录每次初始坐标和种子；若初始即有跨肽接触，该重复无效并重建。"],
              ["轨迹分析", "每 100 ps（全原子）或文献相容间隔（DMD）计算：最大 Aβ-containing cluster (Nmax,Aβ)、Aβ–Aβ/ Aβ–肽接触数、跨种骨架氢键、Aβ β 比例、Aβ16–22 的二级结构、疏水 SASA 与 residue-pair contact map。", "主要响应：P[含 ≥3 条 Aβ 的 β-rich 簇]、Nmax,Aβ、Aβ–Aβ 氢键数、异源/同源接触比和 tFPT(预定义早期事件)。"],
              ["事件定义", "β-rich Aβ 簇 = ≥3 条 Aβ 连通，至少 4 个 Aβ–Aβ 骨架氢键，且该状态连续保持 ≥10 ns（全原子）；DMD 使用等价连续事件窗口并同时报原始分布。", "tFPT 只用于同体积/同浓度条件下的相对首达时间；不得换算为细胞或生理浓度 lag time。"],
              ["促进判据（项目操作性）", "相对 Aβ 单独和 Aβ+乱序肽，候选体系同时满足：β-rich Aβ 簇概率绝对增加 ≥0.15、95% bootstrap CI 不跨 0；median tFPT 至少缩短 30%；显式水全原子复核的效应方向一致。", "满足后报告为“在该高浓度模拟体系中促进早期 Aβ 关联/β 富集的候选”；不报告为“已证明促纤维化”。"],
          ], widths=[4.0, 13.0, 10.6], font_size=6.75)
    label(doc, "不可宣称的结论", "单个 0.1–1 μs 轨迹中看到结合、簇更大、或候选肽自身先聚集，都不足以证明候选肽加快 Aβ 宏观聚集。Aβ42–SST14 的实例尤其表明：异源聚集、紧致簇与最终促聚集可并不等价 [6]。", kind="limit")


def protocol_2(doc: Document) -> None:
    heading(doc, "3. 方法 2：候选肽诱导的 Aβ 构象预激活（DMD/REXDMD；平衡机制）", 1)
    paragraph(doc, "目的：检验候选肽是否使 Aβ 的中央疏水核心（CHC；Aβ16–22）从螺旋/紧致状态转向延展、β 易感状态。该方案直接对应可溶 IAPP 促进 Aβ42 的已报道机制，但不假定 12 条候选肽必然采用同一路径。", size=8.45)
    label(doc, "已发表原始参数", "Ge 等：2 Aβ42 + 2 IAPP（50 × 200 ns）和 4 + 4（20 × 100 ns）atomistic DMD；83 Å 立方盒、PBC、300 K、Debye 长度约 10 Å。单体/二体构象分析为 20 × 600 ns；REXDMD 采用 275–355 K 的 5 或 8 replicas 和 WHAM [2]。其 ThT 与 DMD 支持 IAPP 通过 Aβ16–22 helix-to-extended 转换降低聚集构象障碍。", kind="published")
    label(doc, "当前项目推荐参数", "全 12 肽：2 Aβ42 + 2 候选肽，83 Å 立方盒，50 × 0.20 μs DMD。进入阶段 2 的候选：4 + 4，40 × 0.50 μs DMD；以及 8 replicas（275、285、296、307、319、331、343、355 K），每 replica 0.60 μs、3 组独立 REXDMD ladder，交换接受率目标 20–35%。", kind="proposed")
    table(doc,
          ["分析对象", "计算方法", "主要终点 / 判定规则"],
          [
              ["CHC 二级结构", "DSSP 逐残基统计 Aβ16–22 的 helix、extended/β、coil 占比；以每条独立轨迹的时间平均为样本。", "ΔPextended,16–22 = Pmix − Pcontrol；并报告 95% CI 与 FDR q。仅在 Aβ+候选相对 Aβ+乱序肽同向时视为序列依赖。"],
              ["构象自由能", "以 CHC extended fraction 与 Aβ–候选接触数构建二维 P(x,y)，F=−RT lnP；REXDMD 用 WHAM 回投至 300 K。", "ΔΔGopen = ΔGopen,mix − ΔGopen,control。负值表示候选稳定开放/延展状态；它是热力学可及性而非速率常数。"],
              ["异源二聚体界面", "计算 Aβ–候选 residue-pair contact probability、跨种骨架氢键、CHC 与 C 端的接触寿命；抽取高占有簇并于显式水 3 × 0.50 μs 复核。", "若 Aβ16–22 的构象改变只出现在候选强自聚簇内部，需作为“共聚集伴随效应”而非直接构象催化报告。"],
          ], widths=[4.0, 13.0, 10.6], font_size=6.8)
    label(doc, "不可宣称的结论", "REXDMD 的 replica 交换与高温 replica 只用于恢复平衡分布。任何“从交换轨迹读出的转变时间”均不是真实 300 K Aβ 聚集动力学。", kind="limit")


def protocol_3(doc: Document) -> None:
    heading(doc, "4. 方法 3：预形成候选肽纤维的表面催化二级成核（直接机制优先方案）", 1)
    paragraph(doc, "适用条件：候选肽先在方法 1 的候选单独体系中形成稳定 β-rich 聚集体，且至少两个独立初始纤维样多晶型在无偏轨迹中保持稳定；若有实验 CD/TEM/衍射结构，应以实验结构优先。此门槛防止把任意 7–9 aa 排列伪装成已存在的纤维。", size=8.45)
    label(doc, "已发表原始参数", "Bunce 等直接证明 Aβ16–22 预形成 protofilament 可表面催化 Aβ40 二级成核。其 PRIME20/DMD 模拟用 6 条 Aβ40，或加入 6 条 Aβ16–22 单体，或加入含 21、42、71 条 Aβ16–22 的二/三/四 β-sheet protofilament；总肽浓度 1 或 5 mM；NVT，T*=0.20（文中映射为约 342 K），Andersen thermostat，每体系 3–10 条独立重复 [1]。", kind="published")
    label(doc, "当前项目推荐参数", "以候选肽预形成 seed 替换 Aβ16–22 seed；保留 6 Aβ40、1 与 5 mM、NVT、T*=0.20 的文献可比性。种子大小不按“链数”强行等同，而按暴露 β-sheet 面积匹配文献的低/中/高三级（目标约 10/20/40 nm²）；每个种子多晶型、每个浓度、每种表面积均做 10 个独立 DMD 重复。对命中表面以显式水 CHARMM36m 体系做 5 × 1.0 μs 验证。", kind="proposed")
    table(doc,
          ["步骤", "具体实施", "可量化终点与机制判定"],
          [
              ["种子建立与负对照", "候选肽 seed 至少包括两个稳定 β-sheet 多晶型；每一个都量化暴露面、端面数和可接触残基。并行运行：无 seed；等摩尔候选单体；候选 seed；表面被惰性 cap 覆盖的同一 seed。", "只有“候选 seed”比候选单体与 cap-seed 显示额外效应时，才将效应归因于暴露表面，而不是候选肽总量。"],
              ["表面定位", "每帧计算 Aβ40 到 seed 最近距离、seed 面上二维停留密度、Aβ–seed 接触寿命、Aβ 局部浓度与 seed 表面 1.0 nm 壳层内 Aβ 数。", "表面富集因子 ESurf = ρAβ,surface/ρAβ,bulk；同时应观察到 Aβ–Aβ（而非仅 Aβ–seed）接触/氢键提升。"],
              ["二级核事件", "定义 surface nucleus：至少 3 条 Aβ40 在 seed 1.0 nm 壳层内，形成 ≥4 个 Aβ–Aβ 骨架氢键及延展/β 构象；记录形成、存活与是否脱离表面。", "报告 Psurface-nucleus、tFPT,surface-nucleus、Aβ–Aβ H-bond distribution、seed-adjacent contact map。若核只与 seed 形成氢键而没有 Aβ–Aβ β 配对，不称二级成核。"],
              ["尺寸/浓度依赖", "对三级表面积和 1/5 mM 进行趋势检验；使用种子总暴露面积而非总链数作横轴。", "支持性证据：在可比浓度下 ESurf 与 Psurface-nucleus 随有效表面积升高而增加，并跨 seed 多晶型可重现。"],
          ], widths=[4.0, 13.0, 10.6], font_size=6.74)
    label(doc, "不可宣称的结论", "候选肽自组装模型若未由稳定性/实验锚定，最多是“假设纤维表面的机制测试”。一条 seed 轨迹的 Aβ 吸附或 Aβ–seed 氢键增加，不足以证明表面催化二级成核。", kind="limit")


def protocol_4(doc: Document) -> None:
    heading(doc, "5. 方法 4：端面与侧表面交叉播种的判别（轴向延伸 vs 表面催化）", 1)
    paragraph(doc, "目的：明确候选肽 seed 的作用是让 Aβ 直接在异源纤维端部注册式延伸，还是只在端部/侧表面富集并促进 Aβ–Aβ 自身成核。两种机制必须分开报告。", size=8.45)
    label(doc, "已发表原始参数", "Fan 等：20 链 Aβ 或 hIAPP fibril seed + 1 条异源单体，12.0 nm 立方盒，50 × 0.60 μs DMD，300 K [5]。Song 等：Aβ + IAPP fibril 置于 13×13×19.5 nm 盒，16 replicas、275–425 K、1.5 μs/replica；二 Aβ + IAPP fibril 为 24 replicas、1.5 μs/replica。其结论是 IAPP seed 可催化 Aβ 成核，但不应把端部结合等同于稳定的异源轴向生长 [3]。", kind="published")
    label(doc, "当前项目推荐参数", "先使用 20 链候选 seed + 1 Aβ42（12.0 nm 立方盒，50 × 0.60 μs DMD）分别测试端面和侧面；再使用候选 seed + 2 Aβ42（13×13×19.5 nm 盒，24 replicas，275–425 K rxDMD，1.5 μs/replica）测试表面局部双体成核。端面起始位点距最外层 β-sheet 1.5 nm；侧面位点距侧面法线 1.5 nm，且距任一端 ≥2.0 nm。", kind="proposed")
    table(doc,
          ["机制臂", "判定变量", "预注册判定规则"],
          [
              ["端部直接轴向延伸", "Pbound,end；单体到端部的停留时间；跨 seed–Aβ 的 backbone H-bond 数；Aβ β-strand 与 seed chain 的平行性、层间距离和沿纤维轴注册。", "只有在 ≥4 个跨界 backbone H-bond、平行 in-register 构型持续 ≥20 ns（或 DMD 等价窗口），且重复间复现时，称“支持端部直接延伸”。单纯端部停留不够。"],
              ["侧表面富集", "Pbound,side；ESurf；侧面附近 Aβ 二体/三体的 Pβ-nucleus；Aβ–Aβ vs Aβ–seed H-bond 比。", "若侧面/端面均富集，但形成的是 Aβ–Aβ β 核、非稳定 seed–Aβ 注册界面，则称“表面局部浓缩/催化成核”。"],
              ["异源选择性", "端/侧的 ΔGbind、接触图和事件频率与 Aβ40/42 自身 seed 正对照、候选单体及 cap-seed 对照比较。", "若 Aβ 自身 seed 显示轴向延伸而候选 seed 不显示，则应保留“异源结构不匹配，非直接模板延伸”的结论。"],
          ], widths=[4.0, 13.0, 10.6], font_size=6.75)
    label(doc, "关键解释边界", "IAPP–Aβ 已提供“结合端面却未必稳定直接轴向生长”的反例 [3]。因此，对任一 7–9 aa 候选肽，端部亲和力、docking 分数或一张末帧结构都不能替代注册几何和 Aβ–Aβ 成核事件统计。", kind="limit")


def protocol_5(doc: Document) -> None:
    heading(doc, "6. 方法 5：AChE–Aβ–候选肽三元体系（PAS 招募/桥连机制，不直接报聚集速率）", 1)
    paragraph(doc, "目的：检验 PAS 对接候选肽是阻断、无影响，还是通过稳定 AChE–Aβ–肽三元接触提高 Aβ 在 AChE 表面的局部停留与 β 易感性。该体系用于机制分流，不能单独证明全溶液促聚集。", size=8.45)
    label(doc, "已发表原始参数与机制基础", "AChE 能促进 Aβ 纤维组装，且 PAS 被认为参与该过程 [17]。Lushchekina 等用 accelerated MD 显示 Aβ 被 AChE 表面吸引并形成稳定复合物，提出 AChE 可作成核中心 [7]。这些是 AChE–Aβ 的依据，不是当前任意短肽的直接促聚集证据。", kind="published")
    label(doc, "当前项目推荐参数", "从去配体 human AChE 结构（例如已有对接采用的 4EY6 模板，删除共结晶配体并完成 pH 7.4 质子化）开始。对每条候选的 3 个 PAS pose cluster：AChE+Aβ42、AChE+候选、AChE+Aβ42+候选与 AChE+Aβ42+乱序肽各 5 × 1.0 μs 显式水全原子轨迹。三元体系为 1 AChE + 2 Aβ42 + 2 候选肽，14×14×18 nm 盒、0.15 M NaCl、310 K、1 bar；Aβ 初始距 PAS ≥3 nm。对有稳定桥连的体系再加 3 × 0.50 μs 双 boost GaMD 探索替代姿势（先 50 ns 无偏预跑，随后 20 ns 统计势能分布；σ0P=6、σ0D=6 kcal mol−1）。", kind="proposed")
    table(doc,
          ["读出", "具体计算", "解释/判定"],
          [
              ["PAS 占位", "候选与 Tyr72、Asp74、Tyr124、Trp286、Tyr341 的重原子接触概率、驻留时间、RMSD 聚类和 MM/PBSA（仅作相对排序）。", "候选 PAS 稳定占位本身不等于促进；它可与 Aβ 竞争而抑制招募。"],
              ["Aβ 招募", "Aβ 到 PAS/全 AChE 表面的最小距离、表面驻留时间、接触面积、Aβ 在 1.0 nm AChE 壳层内的概率和 CHC/C 端二级结构。", "相对 AChE+Aβ 与乱序肽，三元体系若提高 Aβ 表面驻留和 Aβ–Aβ 接触，才支持 AChE 介导的局部浓缩假说。"],
              ["三元桥连", "定义 bridge = 候选同时与 AChE 和 Aβ 各有 ≥3 个重原子接触；统计 Pbridge、bridge 持续时间和桥连构型簇。", "Pbridge 高且 Aβ–Aβ β 接触增加：优先进入方法 1/3/7 的验证；Pbridge 高而 Aβ 被 PAS 排斥：提示抑制/竞争机制。"],
              ["增强采样用途", "GaMD/aMD 只用来扩大 AChE 表面探索并选择 cMD/WE 起始盆地；对每个被采样盆地以无偏 cMD 复核。", "不得将 aMD/GaMD 轨迹事件数、加速时间或势能重加权直接写成 Aβ 聚集速率。"],
          ], widths=[4.0, 13.0, 10.6], font_size=6.74)
    label(doc, "不可宣称的结论", "AChE docking pose、MM/PBSA、PAS 接触概率或 aMD 看到的吸附，均不能代替 Aβ–Aβ 成核/速率证据。AChE 三元体系须与无 AChE 的候选体系并列，不能把 AChE 模板效应误归给候选肽。", kind="limit")


def protocol_6(doc: Document) -> None:
    heading(doc, "7. 方法 6：增强采样与自由能（REST2、umbrella、WTMetaD；仅用于平衡量）", 1)
    paragraph(doc, "目的：定量候选肽–Aβ 结合、构象预激活和端/侧表面偏好所对应的自由能，而不是从偏置时间轴导出动力学。各子方案只能在其 CV 能完整描述目标过程时使用。", size=8.45)
    label(doc, "文献方法基础", "REST2 通过缩放溶质作用降低显式水体系的交换数需求 [11]；well-tempered metadynamics 用可控自适应偏置收敛自由能 [14]。Ge 的 Aβ–IAPP REXDMD/WHAM 是 Aβ 异源构象自由能的直接应用先例 [2]。", kind="published")
    table(doc,
          ["子方案", "当前项目的具体参数", "输出、收敛与禁止解释"],
          [
              ["REST2：单体/异二体构象系综", "1 Aβ42 + 1 候选肽于 9.0 nm 立方显式水盒；16 replicas，物理温度 310 K、有效溶质温度 ladder 310、321、333、345、357、369、382、395、408、422、436、451、466、482、498、515 K；每 1 ps 尝试交换；每 replica 0.50 μs；3 套独立 ladder。", "输出 310 K 的 P(CHC-extended)、Pβ、接触簇及 F=−RTlnP。相邻 exchange acceptance 目标 20–35%，并检查前三/后二分之一 FES 的差异 <1 kJ mol−1。无物理 kinetic time。"],
              ["Umbrella：一条主导结合路径的 PMF", "先由 REST2/cMD 证明存在单一主导界面。CV 为 Aβ CHC 与候选肽的最小重原子距离 rmin；0.35–2.50 nm、0.10 nm 间隔（22 windows）；k=1000 kJ mol−1 nm−2；每 window 3 × 100 ns，前 20 ns 丢弃；WHAM+bootstrap。", "输出 ΔGPMF、结合盆地位置与解离势垒。要求相邻 window overlap；加标准态修正时明确几何/Jacobian 假设。多姿势 IDP 体系若 overlap 或收敛失败，不报单一 ΔGbind。"],
              ["WTMetaD：结合–构象耦合 FES", "CV1=连续 Aβ–候选接触数（0.45 nm switching）；CV2=Aβ16–22 extended/β fraction。4 walkers × 0.50 μs，3 个独立 ensembles，310 K；初始 Gaussian 1.2 kJ mol−1，每 1 ps 沉积，bias factor 12，σCV1=0.25、σCV2=0.08。", "输出二维 FES、最小自由能路径和候选诱导的状态占比。需检查不同 walkers/重复的 basin 深度在 1–2 kJ mol−1 内一致。禁止把 deposition time、walker 时间或 crossing counts 报作真实速率。"],
              ["端/侧偏好 PMF", "对方法 4 的 candidate seed，CV 为 Aβ COM 到端面/侧面的距离；各几何单独做 r=0.5–3.0 nm umbrella（0.1 nm，k=1000 kJ mol−1 nm−2，3×100 ns/window）。", "比较 ΔGbind,end 与 ΔGbind,side；亲和力差仅说明平衡占位偏好，是否延伸/成核仍以方法 4 的结构事件判定。"],
          ], widths=[4.2, 13.2, 10.2], font_size=6.55)
    label(doc, "不可宣称的结论", "WTMetaD/umbrella/REST2 可以说明“哪个盆地更稳定、障碍在所选 CV 上多高”，但不能说明“该候选使 Aβ 聚集快 x 倍”。只有方法 7 的 WE、经验证 iMetaD 或充分无偏 MSM 才可处理速率问题。", kind="limit")


def protocol_7(doc: Document) -> None:
    heading(doc, "8. 方法 7：可获得真实事件动力学的路径（WE、无偏 MSM 与经验证 iMetaD）", 1)
    paragraph(doc, "目的：针对一个严格定义的微观事件（例如 Aβ–候选异二体形成，或 seed 表面 Aβ–Aβ 核形成）获得 MFPT/通量/速率。不得把宏观 fibrillation lag time 与小体系首达时间混为同一量。", size=8.45)
    label(doc, "文献方法基础", "WE 是保留统计权重的并行路径采样，可估计稀有事件速率 [15]。Aβ 的无偏全原子 MD 已可用 MSM 得到单体构象动力学，但研究显示收敛需要约 20–30 μs 级采样，另有 315 μs Aβ42 kinetic ensemble 的实例 [12,13]。iMetaD 只有在偏置不扰动过渡态、首达时间检验通过时才可重建速率 [16]。", kind="published")
    table(doc,
          ["速率路线", "具体执行参数", "验证与报告规则"],
          [
              ["Weighted ensemble（首选）", "从未结合盆地启动：rmin(Aβ,候选)>1.4 nm、跨肽骨架 H-bond=0。二维 bin：rmin 0.30–2.00 nm（0.20 nm）× NHB(0,1,2,3,≥4)；每 bin 目标 4 walkers、最多 96 walkers；τresample=20 ps；2,500 cycles/ensemble；10 个独立 ensembles。目标态：rmin<0.45 nm、NHB≥4，且无偏持续 10 ns。对 seed 成核，将第二轴改为 N(Aβ–Aβ backbone H-bond)，目标为 ≥4（≥3 Aβ）或预注册更严格核定义。", "以稳态加权通量/未到达概率计算 k 与 MFPT；分别报告 10 个 ensemble 的分布和 95% CI。只报告所定义、高模拟浓度盒中的微观事件速率；不外推至体内或 ThT lag time。"],
              ["无偏 cMD → MSM", "对通过方法 1 的候选，至少 100 条独立 1.0 μs 无偏显式水轨迹；输入特征：Aβ–候选最小接触、Aβ–Aβ 接触、CHC/C 端构象、骨架氢键与 Rg。TICA/可逆 MSM；扫描 lag 5–50 ns；以 implied-timescale plateau 与 Chapman–Kolmogorov test 选 lag。", "报告状态定义、转移矩阵、MFPT 和 bootstrap CI。若 ITS 无平台、CK 失败、或数据长度小于慢过程量级，不报动力学数值，仅报构象聚类。"],
              ["Infrequent MetaD（仅可验证的一步事件）", "只用于已由 cMD/WE 证明为单一、清晰屏障的二体结合或解离；选择不含过渡态信息的 CV；30–40 个独立 first-passage trajectories；Gaussian 0.5 kJ mol−1、每 100 ps 沉积、bias factor 10；达到预定义目标即停止。", "逐条轨迹用 α=⟨exp[βV(s,t)]⟩ 重标 FPT；重标 FPT 的指数分布 KS p>0.05，且改变 deposition stride 后 k 不变，才报告速率。任何一项失败即撤回 rate claim。"],
          ], widths=[4.2, 13.2, 10.2], font_size=6.56)
    label(doc, "不可宣称的结论", "“有 30 条偏置轨迹”本身不保证速率可靠；“一个 MSM 画出来了”也不保证满足 Markov 性。尤其对于多肽成核，CV 漏掉隐含慢变量时，iMetaD/MetaD 的动力学将被污染。", kind="limit")


def protocol_8(doc: Document) -> None:
    heading(doc, "9. 方法 8：粗粒化大体系与浓度/种子表面积扫描（机制筛选，不作绝对时间映射）", 1)
    paragraph(doc, "目的：将方法 3–4 中不可承受的种子数、单体数、浓度和表面积组合扩展到大体系，识别“局部富集—小寡聚体—脱附/表面停留”的统计模式，并挑选回到全原子验证的条件。", size=8.45)
    label(doc, "已发表原始参数", "Xu 等的一锅式 CG-MD 在 220 Å 立方盒中放置 5 个 Aβ fibril seeds 与 50 个 Aβ 单体，运行 2–5 μs，直接研究 seed 表面的单体/寡聚体组装 [8]。Bunce 的 PRIME20/DMD 以 1/5 mM 和多种 protofilament 大小扫描表面二级成核 [1]。", kind="published")
    label(doc, "当前项目推荐参数", "使用经方法 3 结构稳定性筛选的候选 seed 模型。体系：5 个候选 seed + 50 个 Aβ40（及相同总量的候选单体、无 seed、cap-seed 对照）置于 22.0 nm 立方盒；每条件 20 重复、每条 10 μs CG。浓度扫描以盒长 18、22、28 nm 三档实施；种子表面积扫描为每个 seed 的 10/20/40 nm² 三档。若采用 MARTINI 类模型，必须报告版本、肽映射、二级结构约束和蛋白–水修正，并用方法 1/3 的全原子结果校准。", kind="proposed")
    table(doc,
          ["输出", "具体量", "筛选/回流规则"],
          [
              ["表面富集", "每个 seed 的 Aβ surface-shell occupancy、ESurf、驻留/脱附事件、Aβ 沿端/侧面的二维占有图。", "选择 ESurf 与 seed 面积呈可重复正相关，且 cap-seed 失效的条件回流到方法 3–4。"],
              ["寡聚体统计", "Aβ 最大簇、簇大小分布、Aβ–Aβ 接触网络、seed-bound 与 free Aβ oligomer 的分布、候选单体/seed 的竞争。", "仅将跨 20 重复、跨浓度保持的相对富集/簇概率作为筛选信号；不得将 CG μs 写作真实 Aβ fibrillation 时间。"],
              ["敏感性", "以两个候选 seed 多晶型、1–2 个 CG 参数化/二级结构约束方案交叉检查。", "若机制结论依赖某一个 seed 多晶型或 CG 参数集，结果标为模型依赖并不进入因果结论。"],
          ], widths=[4.0, 13.0, 10.6], font_size=6.75)
    label(doc, "不可宣称的结论", "CG 的时间、β-sheet 注册与绝对浓度效应均高度依赖模型。它用于提名体系和比较相对趋势；候选肽“促进”的最终判断必须回到显式水全原子重复和外部动力学实验。", kind="limit")


def decisions_and_benchmarks(doc: Document) -> None:
    heading(doc, "10. 跨方法量化终点、结论门槛与外部动力学锚点", 1)
    table(doc,
          ["拟声明的结论", "最低 MD 证据组合", "不得替代它的结果"],
          [
              ["候选肽促进早期 Aβ 关联/β 富集", "方法 1：与 Aβ 单独及乱序对照相比，Pβ-rich、Aβ–Aβ H-bond 或相对 tFPT 的重复间效应满足预注册阈值；并有显式水全原子同向复核。", "单一可视化轨迹、docking score、候选自身 APR、Aβ–候选结合能。"],
              ["候选肽诱导 Aβ 构象预激活", "方法 2/6：CHC extended/β 状态人口和 ΔΔGopen 具有重复/重加权收敛，且与相同序列乱序对照比较。", "高温 replica 的轨迹次序或 WTMetaD crossing time。"],
              ["候选肽纤维表面催化二级成核", "方法 3：经稳定性锚定的 seed；表面富集 + Aβ–Aβ β 核 + cap/单体对照 + 面积/浓度趋势；至少一种显式水复核。", "Aβ 吸附或 seed–Aβ 接触本身。"],
              ["候选肽与 Aβ 交叉播种端部延伸", "方法 4：端部稳定 in-register cross-β 几何、跨界 H-bond 阈值、重复统计，并以 Aβ self-seed 和侧面机制作区分。", "端面亲和力、端部停留或一帧轴向排布。"],
              ["候选肽提高某一微观事件速率", "方法 7：WE 通量/MFPT，或通过 ITS/CK 验证的无偏 MSM，或通过 KS/deposition 检验的 iMetaD；报告定义事件、浓度、CI。", "常规 REMD/REST2、WTMetaD、umbrella、aMD/GaMD 的时间轴。"],
          ], widths=[5.0, 12.3, 10.3], font_size=6.75)

    heading(doc, "10.1 用于 MD 外部比对的已发表交叉播种动力学条件", 2)
    table(doc,
          ["已发表阳性体系", "实验条件", "MD 结果可怎样与其对应"],
          [
              ["p340/42 → 匹配全长 Aβ40/42 [4]", "10 μM Aβ 单体、20 μM ThT、30 mM phosphate pH 7.4、30 °C、静置；预形成 p3 fibril seed 1 μM（10%）。匹配 C 端长度时交叉播种缩短 lag time。", "用于验证“端/表面机制需要序列/末端结构兼容性”；不能被直接移植为 7–9 aa 候选肽的必然阳性对照。"],
              ["Aβ16–22 fibril → Aβ40 [1]", "Bunce 用实验动力学与 DMD 联合证明表面催化二级成核。", "是方法 3 的直接机制正对照：MD 应区分表面核形成与单纯吸附。"],
              ["soluble IAPP → Aβ42 [2]", "Ge 的 ThT 体系与 DMD 支持可溶 IAPP 促进 Aβ42 共聚集及 CHC helix-unfolding。", "是方法 2 的构象预激活正对照：FES 变化仍需另行用速率或 ThT 验证。"],
          ], widths=[5.0, 12.3, 10.3], font_size=6.75)
    label(doc, "最终措辞规则", "在没有外部 kinetics/形态学验证前，推荐写法是：“候选肽在预定义的高浓度 MD 体系中增加了 Aβ 早期 β-rich 关联/降低了所选构象盆地的自由能/提高了 WE 定义微观事件的通量。”禁止写成：“该肽已促进 Aβ 病理性纤维化”或“该肽提高了细胞内聚集速率”。", kind="limit")


def references(doc: Document) -> None:
    heading(doc, "11. 逐项参考文献（按方案中首次出现顺序）", 1)
    refs = [
        "[1] Bunce, S. J.; Wang, Y.; Stewart, K. L.; et al. Molecular insights into the surface-catalyzed secondary nucleation of amyloid-β40 (Aβ40) by the peptide fragment Aβ16–22. Science Advances 2019, 5, eaav8216. https://doi.org/10.1126/sciadv.aav8216. 直接促聚集/表面二级成核正例；PRIME20/DMD、1/5 mM、种子尺寸先例。",
        "[2] Ge, X.; Yang, Y.; Sun, Y.; Cao, W.; Ding, F. Islet Amyloid Polypeptide Promotes Amyloid-Beta Aggregation by Binding-Induced Helix-Unfolding of the Amyloidogenic Core. ACS Chemical Neuroscience 2018, 9, 967–975. https://doi.org/10.1021/acschemneuro.7b00396. 可溶 IAPP 促 Aβ42 正例；DMD/REXDMD 与 CHC 构象机制。",
        "[3] Song, Z.; Tang, H.; Gatch, A.; Sun, Y.; Ding, F. Islet amyloid polypeptide fibril catalyzes amyloid-β aggregation by promoting fibril nucleation rather than direct axial growth. International Journal of Biological Macromolecules 2024, 279, 135137. https://doi.org/10.1016/j.ijbiomac.2024.135137. IAPP seed 的端/侧面与非直接轴向生长判别先例。",
        "[4] Tian, Y.; Torres-Flores, A. P.; Shang, Q.; et al. The p3 peptides (Aβ17–40/42) rapidly form amyloid fibrils that cross-seed with full-length Aβ. Nature Communications 2025, 16, 2040. https://doi.org/10.1038/s41467-025-57341-4. 实验性、末端长度选择性交叉播种和外部动力学条件。",
        "[5] Fan, X.; Zhang, X.; Yan, J.; et al. Computational Investigation of Coaggregation and Cross-Seeding between Aβ and hIAPP Underpinning the Crosstalk in Alzheimer’s Disease and Type-2 Diabetes. Journal of Chemical Information and Modeling 2024, 64, 5303–5316. https://doi.org/10.1021/acs.jcim.4c00859. 3+3 DMD、20-chain seed/12 nm、60/50 个重复及分析阈值先例。",
        "[6] Wu, M.; Dorosh, L.; Schmitt-Ulms, G.; Wille, H.; Stepanova, M. Aggregation of Aβ40/42 chains in the presence of cyclic neuropeptides investigated by molecular dynamics simulations. PLoS Computational Biology 2021, 17, e1008771. https://doi.org/10.1371/journal.pcbi.1008771. 多拷贝显式水全原子异源早期聚集与“异源结合不等于促纤维化”反例。",
        "[7] Lushchekina, S. V.; Kots, E. D.; Novichkova, D. A.; et al. Role of Acetylcholinesterase in β-Amyloid Aggregation Studied by Accelerated Molecular Dynamics. BioNanoScience 2017, 7, 396–402. https://doi.org/10.1007/s12668-016-0375-x. AChE–Aβ 吸附/aMD 机制先例。",
        "[8] Xu, L.; Chen, Y.; Wang, X. Assembly of Amyloid β Peptides in the Presence of Fibril Seeds: One-Pot Coarse-Grained Molecular Dynamics Simulations. Journal of Physical Chemistry B 2014, 118, 9238–9246. https://doi.org/10.1021/jp505551m. 5 seeds + 50 monomers 的 CG one-pot/表面寡聚化先例。",
        "[9] Huang, J.; Rauscher, S.; Nawrocki, G.; et al. CHARMM36m: an improved force field for folded and intrinsically disordered proteins. Nature Methods 2017, 14, 71–73. https://doi.org/10.1038/nmeth.4067. 显式水 IDP 力场依据。",
        "[10] Robustelli, P.; Piana, S.; Shaw, D. E. Developing a molecular dynamics force field for both folded and disordered protein states. Proceedings of the National Academy of Sciences USA 2018, 115, E4758–E4766. https://doi.org/10.1073/pnas.1800690115. a99SB-disp 命中体系交叉力场复核依据。",
        "[11] Wang, L.; Friesner, R. A.; Berne, B. J. Replica Exchange with Solute Scaling: A More Efficient Version of Replica Exchange with Solute Tempering (REST2). Journal of Physical Chemistry B 2011, 115, 9431–9438. https://doi.org/10.1021/jp204407d. REST2 方法依据。",
        "[12] Paul, A.; Samantray, S.; Anteghini, M.; Khaled, M.; Strodel, B. Thermodynamics and kinetics of the amyloid-β peptide revealed by Markov state models based on MD data in agreement with experiment. Chemical Science 2021, 12, 6652–6669. https://doi.org/10.1039/D0SC04657D. Aβ 无偏 MD/MSM 收敛与动力学分析依据。",
        "[13] Löhr, T.; Kohlhoff, K.; Heller, G. T.; Camilloni, C.; Vendruscolo, M. A kinetic ensemble of the Alzheimer’s Aβ peptide. Nature Computational Science 2021, 1, 71–78. https://doi.org/10.1038/s43588-020-00003-w. Aβ42 long-timescale kinetic ensemble/MSM 依据。",
        "[14] Barducci, A.; Bussi, G.; Parrinello, M. Well-Tempered Metadynamics: A Smoothly Converging and Tunable Free-Energy Method. Physical Review Letters 2008, 100, 020603. https://doi.org/10.1103/PhysRevLett.100.020603. WTMetaD 平衡自由能方法依据。",
        "[15] Zuckerman, D. M.; Chong, L. T. Weighted Ensemble Simulation: Review of Methodology, Applications, and Software. Annual Review of Biophysics 2017, 46, 43–57. https://doi.org/10.1146/annurev-biophys-070816-033834. WE 稀有事件速率估计依据。",
        "[16] Tiwary, P.; Parrinello, M. From Metadynamics to Dynamics. Physical Review Letters 2013, 111, 230602. https://doi.org/10.1103/PhysRevLett.111.230602. iMetaD 速率重建及其条件依据。",
        "[17] Inestrosa, N. C.; Alvarez, A.; Pérez, C. A.; et al. Acetylcholinesterase Accelerates Assembly of Amyloid-β-Peptides into Alzheimer’s Fibrils: Possible Role of the Peripheral Site of the Enzyme. Neuron 1996, 16, 881–891. https://doi.org/10.1016/S0896-6273(00)80108-7. AChE 促进 Aβ 组装与 PAS 机制基础。",
    ]
    for ref in refs:
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(2.0)
        p.paragraph_format.line_spacing = 1.0
        p.paragraph_format.left_indent = Cm(0.25)
        p.paragraph_format.first_line_indent = Cm(-0.25)
        r = p.add_run(ref)
        font(r, size=7.4, color=SLATE)


def build() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    doc = Document()
    configure(doc)
    title_page(doc)
    shared_design(doc)
    page_break(doc)
    protocol_1(doc)
    protocol_2(doc)
    page_break(doc)
    protocol_3(doc)
    protocol_4(doc)
    page_break(doc)
    protocol_5(doc)
    protocol_6(doc)
    page_break(doc)
    protocol_7(doc)
    protocol_8(doc)
    page_break(doc)
    decisions_and_benchmarks(doc)
    page_break(doc)
    references(doc)
    doc.save(DOCX)
    print(DOCX)


if __name__ == "__main__":
    build()
