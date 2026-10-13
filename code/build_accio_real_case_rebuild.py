#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build a source-grounded Accio Work case-study / visual-rebuild deck.

This is deliberately different from the generic first deck:
- separates online reporting and official documentation from original teaching work;
- documents the concrete Clawesome lobster Shopify case reported online;
- turns that case into an explicitly labelled, original product/landing-page rebuild;
- does not use fabricated official screenshots or represent conceptual visuals as
  the original store/assets.

All PPTX slides are flattened page images.  See SOURCES_AND_BOUNDARIES.md.
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path
from typing import Sequence

from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "code"))
from build_accio_visual_tutorial import (  # noqa: E402
    W, H, F, FONT_REG, FONT_MED, FONT_BOLD, rgb, alpha, font,
    make_bg, shadow_box, rounded_image, measure, wrap_text, text_block,
    pill, rule, header, footer, section_label, small_bullet, crop,
    export_pdf, export_pptx, contact_sheet,
    NAVY, NAVY_2, INK, INK_2, TEAL, TEAL_2, ORANGE, GOLD, MIST,
    PAPER, WHITE, MUTED, SLATE, RED, GREEN, BORDER,
)

OUT = ROOT / "deliverables" / "accio_real_case_rebuild_v2"
PAGES = Path("/tmp/accio_real_case_rebuild_v2_pages")

# The actual products and screenshots from the reported cases are not reproduced.
# This visual system is an original teaching reconstruction.
CORAL = "#F04B2F"
CORAL_DARK = "#A52E2A"
CREAM = "#FFF8EE"
COBALT = "#173B66"
INKBLUE = "#0B1930"
SKY = "#BCEBE7"
LIME = "#CBE96A"
PINK = "#FFD7CF"

OFFICIAL_WORK = "https://www.accio-ai.com/work"
QUICKSTART = "https://www.accio-ai.com/work/documents/zh/quickstart.html"
PLUGINS = "https://www.accio-ai.com/work/documents/zh/help-plugins.html"
CLAWESOME_REPORT = "https://www.guancha.cn/economy/2026_03_27_811682.shtml"
VISUAL_WORKFLOW_REPORT = "https://www.10100.com/article/128143741"


def dark_bg() -> Image.Image:
    im = Image.new("RGB", (W, H), rgb(INKBLUE))
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    d.ellipse((-360, -320, 720, 680), fill=alpha(CORAL, 100))
    d.ellipse((1280, 520, 2300, 1500), fill=alpha(TEAL, 105))
    d.ellipse((680, -420, 1640, 280), fill=alpha(COBALT, 130))
    ov = ov.filter(ImageFilter.GaussianBlur(110))
    return Image.alpha_composite(im.convert("RGBA"), ov).convert("RGB")


def case_header(im: Image.Image, page: int, title: str, subtitle: str = "", dark: bool = False) -> int:
    color = WHITE if dark else INKBLUE
    sub_color = "#C5DBE5" if dark else SLATE
    d = ImageDraw.Draw(im)
    pill(im, 92, 58, f"CASE STUDY  /  {page:02d}", CORAL if dark else PINK, WHITE if dark else CORAL_DARK, fnt=F["eyebrow"], h=38)
    d.text((92, 118), title, font=F["title"], fill=rgb(color))
    if subtitle:
        text_block(im, (95, 190), subtitle, F["subtitle"], sub_color, 1515, line_gap=7)
    return 270


def case_footer(im: Image.Image, page: int, source: str = "", dark: bool = False) -> None:
    d = ImageDraw.Draw(im)
    color = "#A8C0CE" if dark else "#6D808C"
    line = "#365368" if dark else BORDER
    d.line((92, H - 64, W - 92, H - 64), fill=rgb(line), width=2)
    label = "Accio Work 真实案例拆解 + 原创视觉复刻｜v2"
    d.text((92, H - 46), label, font=F["body_tiny"], fill=rgb(color))
    if source:
        max_width = 1310
        text = f"来源：{source}"
        lines = wrap_text(d, text, F["body_tiny"], max_width)
        d.text((370, H - 46), lines[0], font=F["body_tiny"], fill=rgb(color))
    no = f"{page:02d}"
    tw, _ = measure(d, no, F["body_tiny"])
    d.text((W - 92 - tw, H - 46), no, font=F["body_tiny"], fill=rgb(color))


def evidence_tag(im: Image.Image, x: int, y: int, text: str, kind: str = "fact") -> int:
    configs = {
        "fact": ("#DDF6F2", "#08776E"),
        "report": ("#FFF0E8", "#A5492F"),
        "rebuild": ("#E9E5FF", "#5845B9"),
        "verify": ("#FFF8D7", "#94701A"),
    }
    bg, fg = configs[kind]
    return pill(im, x, y, text, bg, fg, fnt=F["eyebrow"], h=34, pad_x=13)


def draw_lobster(im: Image.Image, cx: int, cy: int, scale: float = 1.0, color: str = CORAL,
                 accent: str = CREAM, line: str = INKBLUE) -> None:
    """An original abstract lobster mark—never an official asset or logo."""
    d = ImageDraw.Draw(im)
    def e(box, fill, outline=None, width=1):
        box = tuple(int(v) for v in box)
        d.ellipse(box, fill=rgb(fill), outline=rgb(outline) if outline else None, width=width)
    def rr(box, r, fill, outline=None, width=1):
        box = tuple(int(v) for v in box)
        d.rounded_rectangle(box, radius=int(r), fill=rgb(fill), outline=rgb(outline) if outline else None, width=width)
    def ln(points, fill, width=1):
        d.line([(int(x), int(y)) for x, y in points], fill=rgb(fill), width=max(1, int(width)), joint="curve")
    s = scale
    # tail/body
    e((cx - 35*s, cy - 50*s, cx + 35*s, cy + 58*s), color)
    e((cx - 28*s, cy + 42*s, cx + 28*s, cy + 98*s), color)
    # tail segments
    for offs in (-17, 0, 17):
        ln([(cx + offs*s, cy + 52*s), (cx + offs*.8*s, cy + 88*s)], accent, 3*s)
    # head / eyes
    e((cx - 42*s, cy - 93*s, cx + 42*s, cy - 25*s), color)
    e((cx - 23*s, cy - 70*s, cx - 12*s, cy - 59*s), accent)
    e((cx + 12*s, cy - 70*s, cx + 23*s, cy - 59*s), accent)
    e((cx - 19*s, cy - 67*s, cx - 15*s, cy - 63*s), line)
    e((cx + 15*s, cy - 67*s, cx + 19*s, cy - 63*s), line)
    # antennae
    ln([(cx - 18*s, cy - 86*s), (cx - 65*s, cy - 132*s)], color, 4*s)
    ln([(cx + 18*s, cy - 86*s), (cx + 65*s, cy - 132*s)], color, 4*s)
    # arms / claws
    ln([(cx - 31*s, cy - 38*s), (cx - 75*s, cy - 18*s), (cx - 100*s, cy - 48*s)], color, 15*s)
    ln([(cx + 31*s, cy - 38*s), (cx + 75*s, cy - 18*s), (cx + 100*s, cy - 48*s)], color, 15*s)
    e((cx - 135*s, cy - 83*s, cx - 87*s, cy - 30*s), color)
    e((cx + 87*s, cy - 83*s, cx + 135*s, cy - 30*s), color)
    # legs
    for oy in (0, 23, 45):
        ln([(cx - 28*s, cy + oy*s), (cx - 65*s, cy + (oy+20)*s)], color, 8*s)
        ln([(cx + 28*s, cy + oy*s), (cx + 65*s, cy + (oy+20)*s)], color, 8*s)


def draw_tshirt(im: Image.Image, box: tuple[int, int, int, int], shirt: str = "#FAF5ED",
                print_color: str = CORAL, label: str = "") -> None:
    x1, y1, x2, y2 = box
    d = ImageDraw.Draw(im)
    w, h = x2 - x1, y2 - y1
    # Shirt silhouette
    poly = [
        (x1 + int(.32*w), y1 + int(.08*h)), (x1 + int(.12*w), y1 + int(.19*h)),
        (x1 + int(.02*w), y1 + int(.37*h)), (x1 + int(.22*w), y1 + int(.48*h)),
        (x1 + int(.29*w), y2), (x1 + int(.71*w), y2), (x1 + int(.78*w), y1 + int(.48*h)),
        (x1 + int(.98*w), y1 + int(.37*h)), (x1 + int(.88*w), y1 + int(.19*h)),
        (x1 + int(.68*w), y1 + int(.08*h)),
    ]
    d.polygon(poly, fill=rgb(shirt), outline=rgb("#D4CBC1"))
    d.arc((x1 + int(.40*w), y1 + int(.07*h), x1 + int(.60*w), y1 + int(.22*h)), 0, 180, fill=rgb("#D4CBC1"), width=3)
    draw_lobster(im, x1 + w//2, y1 + int(.48*h), min(w, h)/420, color=print_color, accent=CREAM, line=INKBLUE)
    if label:
        tw, _ = measure(d, label, F["body_tiny"])
        d.text((x1 + w/2 - tw/2, y2 - 30), label, font=F["body_tiny"], fill=rgb(INKBLUE))


def draw_mug(im: Image.Image, box: tuple[int, int, int, int], color: str = CREAM, print_color: str = CORAL) -> None:
    x1, y1, x2, y2 = box
    d = ImageDraw.Draw(im)
    w, h = x2-x1, y2-y1
    d.rounded_rectangle((x1 + .08*w, y1 + .18*h, x1 + .75*w, y1 + .85*h), radius=int(.08*w), fill=rgb(color), outline=rgb("#D4CBC1"), width=3)
    d.arc((x1 + .60*w, y1 + .32*h, x1 + 1.03*w, y1 + .70*h), 270, 90, fill=rgb("#D4CBC1"), width=12)
    draw_lobster(im, int(x1 + .42*w), int(y1 + .52*h), min(w, h)/420, color=print_color, accent=CREAM)
    d.ellipse((x1+.13*w, y1+.08*h, x1+.70*w, y1+.24*h), fill=rgb("#44312B"))


def draw_keychain(im: Image.Image, box: tuple[int, int, int, int], body: str = CORAL) -> None:
    x1, y1, x2, y2 = box
    d = ImageDraw.Draw(im)
    w, h = x2-x1, y2-y1
    d.ellipse((x1+.27*w, y1+.08*h, x1+.73*w, y1+.54*h), outline=rgb("#B7C4CC"), width=12)
    d.line((int(x1+.50*w), int(y1+.50*h), int(x1+.50*w), int(y1+.60*h)), fill=rgb("#B7C4CC"), width=8)
    d.rounded_rectangle((x1+.19*w, y1+.54*h, x1+.81*w, y1+.96*h), radius=int(.12*w), fill=rgb(body))
    draw_lobster(im, int(x1+.50*w), int(y1+.76*h), min(w,h)/450, color=CREAM, accent=body, line=INKBLUE)


def promo_card(im: Image.Image, box: tuple[int, int, int, int], label: str, title: str, kind: str) -> None:
    x1, y1, x2, y2 = box
    shadow_box(im, box, radius=26, fill=WHITE, shadow_opacity=18, outline="#E8DCD3")
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((x1 + 20, y1 + 20, x2 - 20, y1 + 178), radius=18, fill=rgb("#F4E5D7"))
    art = (x1+45, y1+36, x2-45, y1+160)
    if kind == "tshirt":
        draw_tshirt(im, art, shirt="#1B3150", print_color=CORAL)
    elif kind == "mug":
        draw_mug(im, art, color=CREAM, print_color=CORAL)
    else:
        draw_keychain(im, art, body=CORAL)
    evidence_tag(im, x1+22, y1+204, label, "rebuild")
    text_block(im, (x1+22, y1+250), title, F["medium_small"], INKBLUE, x2-x1-44, line_gap=5)


def insight_card(im: Image.Image, box: tuple[int, int, int, int], title: str, body: str, marker: str,
                 color: str = CORAL, dark: bool = False) -> None:
    x1, y1, x2, y2 = box
    shadow_box(im, box, radius=27, fill="#173048" if dark else WHITE, shadow_opacity=18,
               outline="#34566C" if dark else BORDER)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((x1+25, y1+25, x1+84, y1+84), radius=16, fill=rgb(color))
    tw, th = measure(d, marker, F["medium"])
    d.text((x1+54-tw/2, y1+55-th/2-2), marker, font=F["medium"], fill=rgb(WHITE if color == CORAL else INKBLUE))
    d.text((x1+110, y1+28), title, font=F["medium"], fill=rgb(WHITE if dark else INKBLUE))
    text_block(im, (x1+30, y1+112), body, F["body_small"], "#C0D5DE" if dark else SLATE, x2-x1-60, line_gap=7)


def page_cover() -> Image.Image:
    im = dark_bg()
    d = ImageDraw.Draw(im)
    pill(im, 92, 80, "REAL CASE → ORIGINAL REBUILD", CORAL, WHITE, fnt=F["eyebrow"], h=42)
    d.text((92, 182), "有证据的案例拆解", font=font("bold", 74), fill=rgb(WHITE))
    d.text((92, 275), "不是把同一张图换个背景。", font=font("bold", 54), fill=rgb("#FFDCCD"))
    text_block(im, (98, 376), "Accio Work × Clawesome 线上案例\n从报道证据到：产品介绍、首屏、详情页与上架素材的原创复刻", F["body"], "#C9DCE3", 840, line_gap=13)
    evidence_tag(im, 98, 548, "线上案例可追溯", "fact")
    evidence_tag(im, 305, 548, "教学复刻明确标注", "rebuild")
    evidence_tag(im, 550, 548, "不冒充官方截图", "verify")
    # Big original lobster visual and collection objects.
    d.ellipse((1140, 110, 1840, 810), fill=rgb("#FADFD3"))
    draw_lobster(im, 1470, 405, 2.1, color=CORAL, accent=CREAM, line=INKBLUE)
    shadow_box(im, (1055, 666, 1342, 935), radius=28, fill="#F7EEE7", shadow_opacity=45)
    draw_tshirt(im, (1117, 698, 1280, 900), shirt="#193A57", print_color=CORAL)
    shadow_box(im, (1384, 666, 1660, 935), radius=28, fill="#F7EEE7", shadow_opacity=45)
    draw_mug(im, (1438, 716, 1610, 888), color=CREAM, print_color=CORAL)
    shadow_box(im, (1690, 666, 1858, 935), radius=28, fill="#F7EEE7", shadow_opacity=45)
    draw_keychain(im, (1714, 715, 1834, 884), body=CORAL)
    d.text((97, 949), "v2 · 线上资料检索后重制｜2026-10-13", font=F["body_tiny"], fill=rgb("#9BC3D2"))
    return im


def page_correction(page: int) -> Image.Image:
    im = make_bg(False)
    case_header(im, page, "先把边界说清：证据、推断与复刻分开", "这一次不再把“抽象方法论”当案例，也不把原创示意图当成网上的真实页面。")
    d = ImageDraw.Draw(im)
    boxes = [
        ((92, 333, 641, 808), "真实来源", "能写进事实卡的内容", "公开网页里的任务、产品品类、流程叙述、公开用户案例与官方文档步骤。", "E", "fact", TEAL),
        ((685, 333, 1234, 808), "教学推断", "为了做事而补齐的框架", "例如：什么先做、怎样拆素材、怎样验收。它来自工作方法，不等同于来源对原案例的披露。", "P", "verify", GOLD),
        ((1278, 333, 1828, 808), "原创复刻", "我重新设计的商品与页面", "品牌视觉、商品卡、首屏和详情页模块均为原创演示；不是原案例店铺截图或商品。", "R", "rebuild", CORAL),
    ]
    for box, title, sub, body, marker, kind, accent in boxes:
        x1,y1,x2,y2=box
        shadow_box(im, box, radius=30, fill=WHITE, shadow_opacity=18, outline=BORDER)
        evidence_tag(im, x1+30, y1+30, kind.upper(), kind)
        d.rounded_rectangle((x1+30, y1+95, x1+100, y1+165), radius=20, fill=rgb(accent))
        tw, th = measure(d, marker, F["section"])
        d.text((x1+65-tw/2, y1+130-th/2-2), marker, font=F["section"], fill=rgb(WHITE if accent == CORAL else INKBLUE))
        d.text((x1+30, y1+202), title, font=F["section"], fill=rgb(INKBLUE))
        text_block(im, (x1+30, y1+253), sub, F["medium_small"], CORAL_DARK if kind == "report" else SLATE, x2-x1-60, line_gap=6)
        rule(im, x1+30, y1+318, x2-x1-60)
        text_block(im, (x1+30, y1+347), body, F["body_small"], SLATE, x2-x1-60, line_gap=8)
    d.rounded_rectangle((92, 862, 1828, 930), radius=18, fill=rgb("#FFF0E9"))
    d.text((124, 884), "读者规则：看到“案例事实”才可当成来源陈述；看到“原创复刻”只可当作你自己的素材规划参考。", font=F["body_small"], fill=rgb(CORAL_DARK))
    case_footer(im, page)
    return im


def page_source_map(page: int) -> Image.Image:
    im = make_bg(False)
    case_header(im, page, "我实际查到的线上材料", "用来源分层，而不是靠“听说它能做什么”来拼一份教程。")
    d = ImageDraw.Draw(im)
    sources = [
        ("01", "官方产品页", "公开用户案例：张乾超、温杰等；以及工作方式、任务进度与授权说明。", "官方一手产品/案例陈述", "fact", TEAL),
        ("02", "官方快速入门", "界面概览、Agents、功能、连接器、新消息等可导航路径。", "官方操作文档", "fact", TEAL),
        ("03", "官方插件文档", "插件频道、安装 “+”、账号授权、新消息中的插件图标与发品示例。", "官方操作文档", "fact", TEAL),
        ("04", "第三方案例报道", "Clawesome 龙虾品牌 Shopify 建站流程；保温杯与技术包/寻源的案例叙述。", "需标记为媒体报道，未独立验证", "report", ORANGE),
        ("05", "原创教学复刻", "本交付中的商品结构、视觉、详情页和任务书，供你改成自己的产品资料。", "不等同于原案例素材", "rebuild", CORAL),
    ]
    y=308
    for no,title,body,note,kind,accent in sources:
        shadow_box(im,(92,y,1828,y+105),radius=22,fill=WHITE,shadow_opacity=12,outline=BORDER)
        d.rounded_rectangle((118,y+23, y*0+176, y+81), radius=16, fill=rgb(accent))
        tw, th = measure(d,no,F["medium"])
        d.text((147-tw/2,y+52-th/2-2),no,font=F["medium"],fill=rgb(WHITE if accent==CORAL else INKBLUE))
        d.text((208,y+20),title,font=F["medium"],fill=rgb(INKBLUE))
        d.text((208,y+58),body,font=F["body_tiny"],fill=rgb(SLATE))
        evidence_tag(im,1370,y+35,note,kind)
        y += 121
    case_footer(im, page, "完整 URL 与访问日期见第 16 页")
    return im


def page_clawesome_case(page: int) -> Image.Image:
    im = make_bg(False)
    case_header(im, page, "线上具体案例 #1｜Clawesome 龙虾周边 Shopify 店", "它不是“一个水杯换背景”的例子，而是一条从业务目标到选品、视觉、定价、详情页和发布的完整链路。")
    d=ImageDraw.Draw(im)
    evidence_tag(im,92,286,"媒体报道案例 / 未独立验证", "report")
    # Structured evidence timeline
    facts=[
        ("用户任务", "“为 OpenClaw 龙虾周边品牌 Clawesome 搭建一个完整 Shopify 商店”", "01"),
        ("报道的选品", "龙虾帽子、钥匙扣、T 恤等品类的策略选择", "02"),
        ("报道的执行", "市场分析 → 品牌视觉 → 定价 → 商品详情页 → Shopify Admin API 发布", "03"),
        ("报道的时长", "报道写为 30 分钟完成；这是报道中的陈述，不是本交付的实测结论", "04"),
    ]
    x=92
    for i,(title,body,no) in enumerate(facts):
        if i==2: x=92; y=600
        else: y=344 if i<2 else 600
        card=(x,y,x+817,y+210)
        shadow_box(im,card,radius=28,fill=WHITE,shadow_opacity=16,outline=BORDER)
        d.rounded_rectangle((x+28,y+27,x+87,y+86),radius=16,fill=rgb(CORAL if i%2==0 else TEAL))
        tw,th=measure(d,no,F["medium"])
        d.text((x+57-tw/2,y+56-th/2-2),no,font=F["medium"],fill=rgb(WHITE if i%2==0 else INKBLUE))
        d.text((x+114,y+30),title,font=F["medium"],fill=rgb(INKBLUE))
        text_block(im,(x+31,y+100),body,F["body_small"],SLATE,740,line_gap=8)
        x += 859
    shadow_box(im,(1455,292,1828,522),radius=28,fill=INKBLUE,shadow_opacity=25)
    draw_lobster(im,1640,405,1.2,color=CORAL,accent=CREAM,line=INKBLUE)
    d.text((1492,472),"案例关键词",font=F["body_tiny"],fill=rgb("#A9C9D5"))
    d.text((1492,498),"业务目标，不是单图生成",font=F["body_tiny"],fill=rgb(WHITE))
    case_footer(im,page,"观察者网，2026-03-27；具体原文/链接见第 16 页")
    return im


def page_bottle_case(page: int) -> Image.Image:
    im=make_bg(False)
    case_header(im,page,"线上具体案例 #2｜保温杯：从想法 → 技术包 → 供应商", "这个案例与“产品介绍拆解”更接近，但公开报道没有披露完整商品规格或原始视觉稿，因此不能假装复刻原图。")
    d=ImageDraw.Draw(im)
    evidence_tag(im,92,284,"媒体报道案例 / 未独立验证", "report")
    # blueprint / tech pack visual (not a recreated source screenshot)
    shadow_box(im,(92,340,810,870),radius=32,fill=INKBLUE,shadow_opacity=25)
    d.text((132,382),"IDEA → TECH PACK",font=F["eyebrow"],fill=rgb("#A9CBD7"))
    # bottle technical drawing
    d.rounded_rectangle((335,458,535,735),radius=74,outline=rgb("#BEE9E4"),width=8)
    d.rounded_rectangle((360,412,510,481),radius=22,outline=rgb("#BEE9E4"),width=8)
    d.line((435,390,435,758),fill=rgb("#BEE9E4"),width=2)
    d.line((259,588,610,588),fill=rgb("#BEE9E4"),width=2)
    d.text((173,785),"尺寸 / 材料 / 结构 / 包装",font=F["medium"],fill=rgb(WHITE))
    d.text((173,823),"示意图，不是报道原始技术包",font=F["body_tiny"],fill=rgb("#A9CBD7"))
    cards=[
        ("报道事实", "madrilfinds 被报道为：用 Accio 设计一款保温杯，获得技术包后由工具协助在多平台寻源，用户再一键发送询盘。", "F", TEAL),
        ("不能擅自补的", "容量、钢材牌号、保温时长、认证、原始产品图与报价都没有在该报道中完整披露。", "!", ORANGE),
        ("教学复刻正确做法", "保留“需求 → 技术信息 → 供应商筛选 → 人工确认”的链路；让真实产品参数进入每一页，而不是拿通用水杯图重复铺版。", "R", CORAL),
    ]
    y=340
    for title,body,m,accent in cards:
        insight_card(im,(878,y,1828,y+154),title,body,m,accent)
        y+=178
    case_footer(im,page,"观察者网，2026-03-27；内容是报道摘要，不构成实测或功能保证")
    return im


def page_real_ui(page: int) -> Image.Image:
    im=make_bg(False)
    case_header(im,page,"官方文档能确认的操作路径", "这部分来自 Accio Work 快速入门与插件文档；它比我之前凭空画“界面流程”更具体，也更可核对。")
    d=ImageDraw.Draw(im)
    left=(92,320,1185,870)
    shadow_box(im,left,radius=32,fill=WHITE,shadow_opacity=20,outline=BORDER)
    d.rounded_rectangle((92,320,1185,384),radius=32,fill=rgb(INKBLUE));d.rectangle((92,352,1185,384),fill=rgb(INKBLUE))
    d.text((128,341),"从官方文档提取的导航词（非截图）",font=F["eyebrow"],fill=rgb("#C9DDE5"))
    steps=[
        ("1", "侧边栏 → Agents → 创建 Agent", "快速入门说明：先创建/打开 Agent，再在主区发送任务。", TEAL),
        ("2", "侧边栏 → 功能 → 连接器", "官方文档将连接器作为功能中心的一部分；账号关联要在此处完成。", ORANGE),
        ("3", "插件频道 → “+” 安装 → 账号授权", "插件文档明确给出此顺序；安装时不要跳过关联授权的审阅。", GOLD),
        ("4", "新消息 → 输入框中的插件图标", "插件文档说明可在任务执行前从此处唤醒所需插件。", TEAL),
    ]
    y=423
    for no,title,body,ac in steps:
        d.ellipse((130,y+4,178,y+52),fill=rgb(ac))
        tw,th=measure(d,no,F["medium"]); d.text((154-tw/2,y+28-th/2-2),no,font=F["medium"],fill=rgb(INKBLUE))
        d.text((205,y),title,font=F["medium"],fill=rgb(INKBLUE))
        text_block(im,(205,y+35),body,F["body_small"],SLATE,840,line_gap=6)
        y += 104
    shadow_box(im,(1245,320,1828,870),radius=32,fill=INKBLUE,shadow_opacity=25)
    evidence_tag(im,1285,360,"执行前的真实检查", "verify")
    checks=["当前版本是否真的有该插件", "账号权限是否已正确关联", "任务会不会先给预览 / 草稿", "任何发布、发送、覆盖操作是否都需人工确认", "平台规则与素材规格是否仍是最新"]
    y=438
    for check in checks:
        y=small_bullet(im,1290,y,check,470,color=WHITE,bullet_color=CORAL,fnt=F["body_small"])+17
    case_footer(im,page,"官方快速入门 + 官方插件文档；URL 见第 16 页")
    return im


def page_case_to_system(page: int) -> Image.Image:
    im=make_bg(False)
    case_header(im,page,"把“案例故事”变成可执行的素材系统", "案例告诉我们链路；真正落地还要把每一种输出、责任和验收点拆开。")
    d=ImageDraw.Draw(im)
    pipeline=[
        ("真实业务目标", "卖什么？卖给谁？先卖哪一款？", CORAL),
        ("商品资料包", "图片、规格、SKU、品牌/版权边界", TEAL),
        ("内容资产矩阵", "首图、场景、详情、标题、FAQ、视频脚本", GOLD),
        ("草稿 / 预览", "先审产品一致与平台规则", ORANGE),
        ("发布后复盘", "点击、转化、退货/咨询信号", LIME),
    ]
    x=92
    for i,(title,body,ac) in enumerate(pipeline):
        if i<4:
            d.line((x+284,473,x+336,473),fill=rgb("#B7CDD5"),width=5)
            d.polygon([(x+336,463),(x+354,473),(x+336,483)],fill=rgb("#B7CDD5"))
        shadow_box(im,(x,338,x+284,677),radius=28,fill=WHITE,shadow_opacity=16,outline=BORDER)
        d.rounded_rectangle((x+25,365,x+90,430),radius=18,fill=rgb(ac))
        d.text((x+111,372),f"0{i+1}",font=F["medium"],fill=rgb(INKBLUE))
        text_block(im,(x+25,470),title,F["medium_small"],INKBLUE,230,line_gap=5)
        text_block(im,(x+25,540),body,F["body_tiny"],SLATE,230,line_gap=6)
        x += 365
    shadow_box(im,(92,750,1828,905),radius=30,fill="#FFF0E9",shadow_opacity=10,outline="#F6D8C8")
    d.text((132,790),"关键变化",font=F["section"],fill=rgb(CORAL_DARK))
    text_block(im,(132,842),"“优化”不等于单张图变漂亮，而是让业务目标、真实商品信息、视觉资产和最终发布动作能被逐一核对。",F["body"],INKBLUE,1500,line_gap=9)
    case_footer(im,page)
    return im


def page_product_breakdown(page: int) -> Image.Image:
    im=make_bg(False)
    case_header(im,page,"产品介绍拆解｜从龙虾周边案例到一套可卖的商品组合", "报道仅披露帽子、钥匙扣、T 恤等选品方向；下方是原创的“商品角色”复刻，不是原店商品。")
    d=ImageDraw.Draw(im)
    evidence_tag(im,92,284,"报道披露：品类方向", "report")
    evidence_tag(im,330,284,"原创：商品角色与视觉", "rebuild")
    products=[
        ((92,344,638,860),"T 恤｜主打款","用最大面积承接品牌语言；首图应先看清剪裁、印花位置、颜色和尺码信息。","tshirt",CORAL),
        ((687,344,1233,860),"马克杯｜客单扩展","桌面/礼品场景更重要；要补充容量、材质、包装和清洗限制等真实信息。","mug",TEAL),
        ((1282,344,1828,860),"钥匙扣｜低门槛款","承担低价入门、加购和礼物属性；需要近景、尺寸参照与五金细节。","key",GOLD),
    ]
    for box,title,body,kind,ac in products:
        x1,y1,x2,y2=box
        shadow_box(im,box,radius=30,fill=WHITE,shadow_opacity=18,outline=BORDER)
        d.rounded_rectangle((x1+25,y1+25,x1+128,y1+59),radius=14,fill=rgb(ac))
        d.text((x1+43,y1+34),"原创复刻",font=F["eyebrow"],fill=rgb(INKBLUE))
        if kind=="tshirt": draw_tshirt(im,(x1+155,y1+84,x1+390,y1+305),shirt="#1B3150",print_color=CORAL)
        if kind=="mug": draw_mug(im,(x1+154,y1+103,x1+384,y1+292),color=CREAM,print_color=CORAL)
        if kind=="key": draw_keychain(im,(x1+180,y1+85,x1+366,y1+299),body=CORAL)
        d.text((x1+28,y1+340),title,font=F["medium"],fill=rgb(INKBLUE))
        text_block(im,(x1+28,y1+385),body,F["body_small"],SLATE,x2-x1-56,line_gap=8)
        d.rounded_rectangle((x1+28,y1+468,x2-28,y2-27),radius=16,fill=rgb("#F4F7F8"))
        d.text((x1+46,y1+486),"上架前必须补齐",font=F["body_tiny"],fill=rgb(CORAL_DARK))
        text_block(im,(x1+46,y1+518),"真实规格 · 权利/授权 · 真实交期 · 平台所需属性",F["body_tiny"],INKBLUE,x2-x1-92,line_gap=5)
    case_footer(im,page)
    return im


def page_visual_system(page: int) -> Image.Image:
    im=dark_bg()
    case_header(im,page,"原创视觉复刻｜先建立“卖什么”的视觉语气", "这不是原案例店铺的还原，而是示范：怎样把一个品类故事变成可扩展的色彩、字重、图形与首图规则。",dark=True)
    d=ImageDraw.Draw(im)
    # Brand strip
    shadow_box(im,(92,320,660,850),radius=34,fill="#FFF8EE",shadow_opacity=30)
    d.text((132,365),"CLAWESOME",font=font("bold",46),fill=rgb(INKBLUE))
    d.text((134,425),"MAKE SOME NOISE.",font=F["medium"],fill=rgb(CORAL))
    draw_lobster(im,376,602,1.3,color=CORAL,accent=CREAM,line=INKBLUE)
    d.text((132,756),"原创教学品牌板",font=F["body_tiny"],fill=rgb(SLATE))
    d.text((132,790),"不代表原案例视觉资产",font=F["body_tiny"],fill=rgb(SLATE))
    # System columns
    cols=[
        ("色彩",[(CORAL,"行动 / 主张"),(INKBLUE,"秩序 / 对比"),(CREAM,"留白 / 触感")]),
        ("图像",[("首图", "产品先清楚"),("场景", "先讲使用时刻"),("细节", "再讲材料/尺寸")]),
        ("语气",[("短", "先给一句主张"),("实", "规格不编造"),("可核", "每个卖点有依据")]),
    ]
    x=730
    for title,items in cols:
        shadow_box(im,(x,320,x+340,850),radius=30,fill="#163852",shadow_opacity=22,outline="#37677E")
        d.text((x+30,360),title,font=F["section"],fill=rgb(WHITE))
        y=435
        for a,b in items:
            if a.startswith("#"):
                d.rounded_rectangle((x+30,y,x+78,y+48),radius=12,fill=rgb(a))
                d.text((x+98,y+7),b,font=F["body_small"],fill=rgb("#CBE0E8"))
            else:
                pill(im,x+30,y,a,"#244E65",WHITE,fnt=F["eyebrow"],h=32,pad_x=12)
                text_block(im,(x+30,y+45),b,F["body_small"],"#CBE0E8",265,line_gap=6)
            y+=125
        x+=368
    case_footer(im,page,dark=True)
    return im


def page_before_after(page: int) -> Image.Image:
    im=make_bg(False)
    case_header(im,page,"首图优化不是“把背景换掉”", "下面是一个原创对比：左边没有商品层级，右边把主体、品类、卖点和行动路径分开。")
    d=ImageDraw.Draw(im)
    # Before generic raw product card
    shadow_box(im,(92,333,850,875),radius=32,fill="#F1F2F2",shadow_opacity=18,outline="#D8DDE0")
    evidence_tag(im,126,370,"低信息密度示意", "verify")
    draw_tshirt(im,(285,442,638,770),shirt="#193A57",print_color=CORAL)
    d.text((126,795),"问题：只看见“图案”，看不见它卖给谁、\n是什么品类、怎样继续了解。",font=F["body_small"],fill=rgb(SLATE))
    # After designed hero
    shadow_box(im,(940,333,1828,875),radius=32,fill=INKBLUE,shadow_opacity=25)
    d.ellipse((1300,385,1930,1015),fill=rgb("#264B6D"))
    d.text((982,386),"LOBSTER ENERGY",font=F["eyebrow"],fill=rgb("#F1C6B9"))
    d.text((982,430),"Wear the\nconversation starter.",font=font("bold",42),fill=rgb(WHITE))
    pill(im,984,590,"ORIGINAL REBUILD",CORAL,WHITE,fnt=F["eyebrow"],h=34)
    d.rounded_rectangle((984,658,1260,711),radius=15,fill=rgb(CREAM))
    d.text((1012,674),"Shop the collection  →",font=F["medium_small"],fill=rgb(INKBLUE))
    draw_tshirt(im,(1372,425,1710,770),shirt=CREAM,print_color=CORAL)
    d.text((982,800),"优化点：先让人知道这是哪一类产品，再给单一动作；\n规格、尺码、材质等真实信息进入后续商品页。",font=F["body_small"],fill=rgb("#CBE0E8"))
    case_footer(im,page)
    return im


def page_homepage(page: int) -> Image.Image:
    im=make_bg(False)
    case_header(im,page,"原创复刻：主页首屏要解决三件事", "不是把产品堆在一张海报上，而是回答：这是什么、有什么吸引力、我下一步点哪里。")
    d=ImageDraw.Draw(im)
    shadow_box(im,(92,330,1828,870),radius=34,fill=INKBLUE,shadow_opacity=25)
    d.text((137,382),"CLAWESOME",font=F["medium"],fill=rgb(CREAM))
    d.text((137,438),"Loud color.\nSmall ritual.\nBig smile.",font=font("bold",54),fill=rgb(WHITE))
    pill(im,140,650,"Shop main pieces",CORAL,WHITE,fnt=F["medium_small"],h=48,pad_x=22)
    d.text((141,727),"首屏只放一个主张 + 一个动作",font=F["body_small"],fill=rgb("#BFD7E2"))
    # product detail cards internal
    shadow_box(im,(1035,402,1295,790),radius=25,fill="#F6EDE2",shadow_opacity=20)
    draw_tshirt(im,(1073,447,1255,710),shirt="#193A57",print_color=CORAL)
    shadow_box(im,(1330,402,1585,790),radius=25,fill="#F6EDE2",shadow_opacity=20)
    draw_mug(im,(1360,465,1555,700),color=CREAM,print_color=CORAL)
    shadow_box(im,(1620,402,1785,790),radius=25,fill="#F6EDE2",shadow_opacity=20)
    draw_keychain(im,(1640,478,1765,690),body=CORAL)
    # annotations below
    labels=[("一句主张","解释品牌，不解释所有产品"),("主视觉","一次只突出一个明星品"),("商品群","快速让用户理解可买的范围"),("单一 CTA","不让用户猜你希望他做什么")]
    x=92
    y=914
    for title,body in labels:
        d.rounded_rectangle((x,y,x+408,y+64),radius=15,fill=rgb("#EDF5F6"))
        d.text((x+18,y+13),title,font=F["medium_small"],fill=rgb(INKBLUE))
        d.text((x+18,y+38),body,font=F["body_tiny"],fill=rgb(SLATE))
        x+=435
    case_footer(im,page)
    return im


def page_detail_page(page: int) -> Image.Image:
    im=make_bg(False)
    case_header(im,page,"产品详情页拆解｜把“好看”变成“能决策”", "详情页里最容易被忽略的不是配色，而是每个模块是否替用户消除了一个真实疑问。")
    d=ImageDraw.Draw(im)
    # left visual Product / hero
    shadow_box(im,(92,330,650,874),radius=32,fill="#F6EEE6",shadow_opacity=18,outline="#E4D5C9")
    draw_tshirt(im,(200,418,542,718),shirt="#193A57",print_color=CORAL)
    d.text((133,762),"图 01｜商品实拍/渲染",font=F["body_tiny"],fill=rgb(SLATE))
    d.text((133,795),"主图下方先给：名称、价格、可选项与主动作。",font=F["body_tiny"],fill=rgb(INKBLUE))
    # right 6 modules
    modules=[
        ("01", "一句价值主张", "解释这件商品适合谁、用在什么场景。", CORAL),
        ("02", "真实规格", "材质、尺寸、颜色、包装、交期——只写有依据的信息。", TEAL),
        ("03", "图案/结构细节", "局部放大、工艺与使用方式，不拿装饰图替代细节。", GOLD),
        ("04", "尺码 / 容量 / 兼容", "用表格或清晰参照，减少下单后的猜测。", ORANGE),
        ("05", "故事与信任", "品牌故事、售后、FAQ、运输，和“喜欢”之外的决策理由。", TEAL),
        ("06", "单一行动", "购买、询盘或保存草稿；不要在未经审核时自动发布。", CORAL),
    ]
    # Keep every module inside the right-hand pane: three compact columns by two rows.
    module_x, module_y, module_w, module_h, gap_x, gap_y = 690, 330, 348, 235, 28, 47
    for i,(no,title,body,ac) in enumerate(modules):
        x = module_x + (i % 3) * (module_w + gap_x)
        y = module_y + (i // 3) * (module_h + gap_y)
        shadow_box(im,(x,y,x+module_w,y+module_h),radius=24,fill=WHITE,shadow_opacity=14,outline=BORDER)
        d.rounded_rectangle((x+21,y+21,x+70,y+70),radius=14,fill=rgb(ac))
        tw,th=measure(d,no,F["eyebrow"]);d.text((x+45-tw/2,y+45-th/2-2),no,font=F["eyebrow"],fill=rgb(WHITE if ac in (CORAL,ORANGE) else INKBLUE))
        text_block(im,(x+91,y+23),title,F["medium_small"],INKBLUE,module_w-115,line_gap=4,max_lines=2)
        text_block(im,(x+23,y+103),body,F["body_tiny"],SLATE,module_w-46,line_gap=6,max_lines=4)
    case_footer(im,page)
    return im


def page_asset_matrix(page: int) -> Image.Image:
    im=make_bg(False)
    case_header(im,page,"一件商品，不是一张图｜资产矩阵才是“优化”的结果", "以原创 T 恤主打款为例：每张图服务一个决策动作；不能用同一张正面图反复充数。")
    d=ImageDraw.Draw(im)
    cells=[
        ((92,340,498,640),"01 正面白底","列表页识别","tshirt",TEAL),
        ((526,340,932,640),"02 背面 / 版型","消除外观疑问","tshirt",ORANGE),
        ((960,340,1366,640),"03 穿着场景","建立使用想象","tshirt",GOLD),
        ((1394,340,1828,640),"04 印花细节","展示工艺与局部","tshirt",CORAL),
        ((92,680,498,900),"05 尺码说明","降低选错成本","sheet",TEAL),
        ((526,680,932,900),"06 材质 / 养护","让规格可核","sheet",ORANGE),
        ((960,680,1366,900),"07 FAQ / 物流","减少下单阻力","sheet",GOLD),
        ((1394,680,1828,900),"08 视频脚本","把卖点变成镜头","sheet",CORAL),
    ]
    for box,title,sub,kind,ac in cells:
        x1,y1,x2,y2=box
        shadow_box(im,box,radius=24,fill=WHITE,shadow_opacity=14,outline=BORDER)
        if kind=="tshirt":
            d.rounded_rectangle((x1+20,y1+20,x2-20,y1+138),radius=16,fill=rgb("#F5E7D9"))
            # alternate styling by cell
            shirt="#193A57" if title.startswith("01") or title.startswith("03") else CREAM
            draw_tshirt(im,(x1+128,y1+30,x1+278,y1+138),shirt=shirt,print_color=CORAL)
        else:
            d.rounded_rectangle((x1+20,y1+20,x2-20,y1+54),radius=10,fill=rgb(ac))
            d.text((x1+34,y1+29),"内容模块",font=F["eyebrow"],fill=rgb(INKBLUE if ac!=CORAL else WHITE))
            d.line((x1+25,y1+90,x2-25,y1+90),fill=rgb("#DDE7EA"),width=5)
            d.line((x1+25,y1+112,x2-90,y1+112),fill=rgb("#DDE7EA"),width=5)
        d.text((x1+22,y2-76),title,font=F["medium_small"],fill=rgb(INKBLUE))
        d.text((x1+22,y2-43),sub,font=F["body_tiny"],fill=rgb(SLATE))
    case_footer(im,page)
    return im


def page_plugin_flow(page: int) -> Image.Image:
    im=make_bg(False)
    case_header(im,page,"从 ZIP 素材包到“草稿”的正确任务流", "官方插件文档给过“基于我上传的 ZIP 素材包，帮我发品到国际站”的示例。以下补上人工验收关口，避免直接发布。")
    d=ImageDraw.Draw(im)
    evidence_tag(im,92,283,"官方插件文档：示例任务", "fact")
    stages=[
        ("A", "装插件 + 授权", "插件频道点击 “+”，完成账号关联；先核对所授权限。", TEAL),
        ("B", "新消息中启用插件", "从输入框的插件图标选择业务插件；明确本次任务只做“草稿”。", ORANGE),
        ("C", "上传素材包", "ZIP 内按 SKU 放真实图、规格、标题草稿、权利/认证证明。", GOLD),
        ("D", "先要执行计划", "要求列出要生成的商品、字段、图组和缺失信息，等待确认。", TEAL),
        ("E", "草稿 + 人审", "逐项核产品、规格、平台规则；通过后再决定是否发布。", CORAL),
    ]
    x=92
    for i,(letter,title,body,ac) in enumerate(stages):
        y=350 if i<3 else 650
        if i==3: x=360
        shadow_box(im,(x,y,x+300,y+230),radius=25,fill=WHITE,shadow_opacity=15,outline=BORDER)
        d.rounded_rectangle((x+25,y+24,x+76,y+75),radius=15,fill=rgb(ac))
        tw,th=measure(d,letter,F["medium"]);d.text((x+50-tw/2,y+50-th/2-2),letter,font=F["medium"],fill=rgb(WHITE if ac in (CORAL,ORANGE) else INKBLUE))
        d.text((x+25,y+104),title,font=F["medium_small"],fill=rgb(INKBLUE))
        text_block(im,(x+25,y+143),body,F["body_tiny"],SLATE,250,line_gap=6)
        if i==2: x=1080
        else: x+=330
    d.rounded_rectangle((1035,650,1828,880),radius=28,fill=rgb(INKBLUE))
    evidence_tag(im,1075,692,"推荐追加的安全语句", "verify")
    text_block(im,(1075,748),"“先生成商品和素材清单、缺失字段清单与草稿预览；\n不要发送、不要发布、不要覆盖现有商品。\n我确认每个 SKU 后，再执行下一步。”",F["body"],WHITE,680,line_gap=11)
    case_footer(im,page,"官方插件文档（上传 ZIP 素材包 → 发品）+ 原创的草稿/人审控制点")
    return im


def page_task_spec(page: int) -> Image.Image:
    im=dark_bg()
    case_header(im,page,"一份真正可用的任务书｜不是“帮我优化一下”", "下面的任务格式可以套入你的真实产品；方括号里必须替换成可验证的信息。",dark=True)
    d=ImageDraw.Draw(im)
    shadow_box(im,(92,316,1208,884),radius=32,fill="#13364C",shadow_opacity=26,outline="#32657B")
    evidence_tag(im,132,356,"可复制模板", "rebuild")
    prompt=(
        "任务：基于我上传的 [SKU/产品名] 素材包，生成【仅草稿】的商品内容。\n\n"
        "已确认事实：材质 [ ]；尺寸/容量 [ ]；颜色 [ ]；型号 [ ]；\n"
        "不能改写： [结构/认证/商标/功效/使用限制]。\n\n"
        "需要的资产：\n"
        "- 1 张白底首图（画幅 [ ]，不加未经确认文案）\n"
        "- 3 张详情页模块图（结构/尺寸/使用或养护）\n"
        "- 标题、短描述、FAQ 草稿；所有卖点标注其事实来源。\n\n"
        "先输出：缺失信息表 + 执行计划 + 每个 SKU 的交付清单。\n"
        "未经我确认，不发送、不发布、不覆盖线上商品。"
    )
    text_block(im,(134,418),prompt,F["body"],WHITE,1020,line_gap=11)
    shadow_box(im,(1260,316,1828,884),radius=32,fill="#F8EFE5",shadow_opacity=24)
    d.text((1300,365),"为什么这份任务书有用？",font=F["medium"],fill=rgb(INKBLUE))
    items=[
        ("事实字段", "让“好看”不覆盖真实规格。"),
        ("素材清单", "避免同一图被重复用作所有模块。"),
        ("先计划", "缺什么先问，不足的信息不硬编。"),
        ("草稿边界", "把发布动作留给人审，而不是默认自动执行。"),
    ]
    y=435
    for i,(a,b) in enumerate(items,1):
        d.ellipse((1300,y,1340,y+40),fill=rgb(CORAL if i%2 else TEAL))
        d.text((1358,y-1),a,font=F["medium_small"],fill=rgb(INKBLUE))
        text_block(im,(1358,y+29),b,F["body_tiny"],SLATE,405,line_gap=5)
        y+=104
    case_footer(im,page,dark=True)
    return im


def page_qc(page: int) -> Image.Image:
    im=make_bg(False)
    case_header(im,page,"上架前的“真实优化”验收表", "如果做完后只剩一堆漂亮图，而你答不上“产品是否准确、内容能否发布”，那不叫优化。")
    d=ImageDraw.Draw(im)
    checks=[
        ("产品一致", "画面、型号、颜色、结构与真实输入是否相符？", "人工比对原图/样品", TEAL),
        ("产品介绍", "标题、卖点、规格、FAQ 是否都能回到证据？", "标注来源/删除无法证实项", CORAL),
        ("视觉资产", "首图、细节、尺寸、场景是否各自承担不同任务？", "资产矩阵完整而不重复", GOLD),
        ("版权与合规", "品牌、图案、人物、认证、绝对化用语是否有授权/依据？", "权利/规则复核", ORANGE),
        ("系统权限", "是草稿还是发布？发送/覆盖/授权是否由人确认？", "操作日志 + 人审", TEAL),
        ("效果复盘", "上线后看哪些数据？什么情况下迭代？", "预设点击/转化/咨询指标", LIME),
    ]
    y=315
    for no,(title,q,action,ac) in enumerate(checks,1):
        shadow_box(im,(92,y,1828,y+87),radius=20,fill=WHITE,shadow_opacity=12,outline=BORDER)
        d.rounded_rectangle((120,y+18,169,y+67),radius=14,fill=rgb(ac))
        t=f"{no:02d}";tw,th=measure(d,t,F["eyebrow"]);d.text((144.5-tw/2,y+42-th/2-2),t,font=F["eyebrow"],fill=rgb(INKBLUE))
        d.text((195,y+17),title,font=F["medium_small"],fill=rgb(INKBLUE))
        d.text((422,y+20),q,font=F["body_tiny"],fill=rgb(SLATE))
        d.rounded_rectangle((1380,y+20,1779,y+67),radius=13,fill=rgb("#EFF6F7"))
        d.text((1401,y+35),action,font=F["body_tiny"],fill=rgb(INKBLUE))
        y+=101
    case_footer(im,page)
    return im


def page_sources(page: int) -> Image.Image:
    im=make_bg(False)
    case_header(im,page,"来源、链接与本版做了什么修正", "网页内容会变化；以下为本次检索时使用的来源与在本材料中的用途。")
    d=ImageDraw.Draw(im)
    refs=[
        ("[1] 官方产品页", OFFICIAL_WORK, "公开用户案例、任务执行/权限与产品能力描述", "fact"),
        ("[2] 官方快速入门", QUICKSTART, "Agents、功能、连接器、新消息等界面导航", "fact"),
        ("[3] 官方插件文档", PLUGINS, "插件频道、“+” 安装、账号授权、输入框插件图标、ZIP 发品示例", "fact"),
        ("[4] 观察者网，2026-03-27", CLAWESOME_REPORT, "Clawesome、保温杯、技术包/寻源等案例报道", "report"),
        ("[5] 大数跨境，2026-04-22", VISUAL_WORKFLOW_REPORT, "视觉统一工作流、草稿/人审建议与任务示例（第三方报道）", "report"),
    ]
    y=300
    for title,url,use,kind in refs:
        shadow_box(im,(92,y,1828,y+107),radius=20,fill=WHITE,shadow_opacity=11,outline=BORDER)
        evidence_tag(im,120,y+21,kind.upper(),kind)
        d.text((245,y+18),title,font=F["medium_small"],fill=rgb(INKBLUE))
        d.text((245,y+48),url,font=F["body_tiny"],fill=rgb(CORAL_DARK))
        d.text((245,y+75),f"本材料用途：{use}",font=F["body_tiny"],fill=rgb(SLATE))
        y+=123
    d.rounded_rectangle((92,925,1828,977),radius=15,fill=rgb("#FFF0E9"))
    d.text((120,941),"本版修正：用真实线上案例 + 官方文档取代空泛描述；所有商品/页面视觉均显式标注为原创教学复刻。",font=F["body_tiny"],fill=rgb(CORAL_DARK))
    case_footer(im,page)
    return im


def page_close(page: int) -> Image.Image:
    im=dark_bg()
    d=ImageDraw.Draw(im)
    pill(im,92,86,"NEXT / 用你的真实产品替换概念图",CORAL,WHITE,fnt=F["eyebrow"],h=42)
    d.text((92,195),"现在，才开始做你的产品。",font=font("bold",64),fill=rgb(WHITE))
    text_block(im,(98,300),"先选一个真实 SKU；准备产品图、规格、品牌授权与目标平台；\n然后跑一次“草稿 → 人审 → 小范围发布 → 复盘”。\n你需要优化的不是一张图片，而是一条能被验证的商品内容链路。",F["body"],"#C9DCE3",900,line_gap=14)
    # Final checklist
    shadow_box(im,(92,590,900,865),radius=30,fill="#173048",shadow_opacity=28,outline="#416D80")
    d.text((132,632),"你下一次真正要上传的东西",font=F["medium"],fill=rgb(WHITE))
    list_items=["真实商品图片（含细节）", "规格 / 型号 / 颜色 / 证据", "目标平台与上架边界", "可接受的草稿与发布流程"]
    y=690
    for item in list_items:
        y=small_bullet(im,136,y,item,650,color=WHITE,bullet_color=CORAL,fnt=F["body_small"])+10
    # object scene right
    d.ellipse((1140,135,1850,845),fill=rgb("#F9D4C7"))
    draw_lobster(im,1500,400,2.25,color=CORAL,accent=CREAM,line=INKBLUE)
    shadow_box(im,(1250,655,1700,892),radius=26,fill=CREAM,shadow_opacity=30)
    d.text((1290,695),"FACT",font=F["eyebrow"],fill=rgb(CORAL_DARK))
    d.text((1290,737),"真实资料进入任务",font=F["medium"],fill=rgb(INKBLUE))
    d.text((1290,779),"REBUILD",font=F["eyebrow"],fill=rgb(CORAL_DARK))
    d.text((1290,821),"原创视觉进入草稿",font=F["medium"],fill=rgb(INKBLUE))
    case_footer(im,page,dark=True)
    return im


def sources_markdown(path: Path) -> None:
    path.write_text(f"""# 来源与边界说明｜Accio Work 真实案例拆解 + 原创视觉复刻 v2

## 本次线上检索来源

1. **Accio Work 官方产品页**  
   {OFFICIAL_WORK}  
   用途：官方公开的用户案例（张乾超、温杰等）、工作方式、权限和任务进度的产品描述。

2. **Accio Work 官方快速入门**  
   {QUICKSTART}  
   用途：官方界面导航术语：侧边栏、新消息、Agents、功能、连接器、主区域。

3. **Accio Work 官方插件文档**  
   {PLUGINS}  
   用途：插件频道、点击“+”安装、账号授权、新消息输入框插件图标；并提供“基于我上传的 ZIP 素材包，帮我发品到国际站”的官方示例。

4. **观察者网：〈用这个中国AI工具，老外正在批量开“一人跨国公司”〉，2026-03-27**  
   {CLAWESOME_REPORT}  
   用途：第三方报道中的 Clawesome 龙虾周边 Shopify 案例，以及保温杯“概念—技术包—寻源”案例。  
   **边界：** 这是媒体报道，页面中的具体过程/时长/结果没有由本交付独立复验。

5. **大数跨境：〈深度拆解 Accio Work：外贸全自动 AI 时代的操作指南〉，2026-04-22**  
   {VISUAL_WORKFLOW_REPORT}  
   用途：第三方文章中的视觉统一任务示例和草稿/人审建议。  
   **边界：** 第三方文章中的功能描述应以官方当前版本为准。

## 本版如何区分内容

| 标记 | 意义 | 能否当作事实 |
|---|---|---|
| `FACT` | 官方产品页或官方文档中可直接定位到的描述 | 可以，仍建议在本机版本核对 |
| `REPORT` | 第三方报道中的案例或步骤 | 只能当作报道陈述，不能当成独立验证结果 |
| `VERIFY` | 要在用户本机 Accio / 目标平台中核对的路径或规则 | 不可当作已验证事实 |
| `REBUILD` | 本次新做的商品、页面、视觉和任务模板 | 原创教学示意，不是原案例素材、截图或官方文件 |

## 交付形式

- PDF 与 PPTX 都是扁平图文版。
- PPTX 每页只含一张全页图片；不含可编辑的文字、表格或原生版式。
- 所有商品/页面视觉为原创演示；没有复用原案例店铺截图或把报道图片当作自己的输出。
""",encoding="utf-8")


def write_readme(path: Path, page_count: int) -> None:
    path.write_text(f"""# Accio Work 真实案例拆解与视觉复刻 v2

这是对上一版抽象教程的**重制版**：它以线上可追溯案例和官方文档为起点，明确区分案例事实、第三方报道、待本机核对项与原创教学复刻。

## 文件

- `Accio_Work_Clawesome真实案例拆解与视觉复刻_v2.pdf`：{page_count} 页扁平图文 PDF。
- `Accio_Work_Clawesome真实案例拆解与视觉复刻_v2.pptx`：{page_count} 页 16:9 PPTX，每页只有 1 张全页图像。
- `preview_contact_sheet_v2.jpg`：所有页面缩略预览。
- `SOURCES_AND_BOUNDARIES.md`：网页来源、用途与证据边界。

## 本版新增

- 具体线上案例：Clawesome 龙虾周边 Shopify 建站流程；保温杯从技术包到寻源的报道案例。
- 官方文档操作路径：Agents、连接器、插件频道、插件安装/授权和新消息中的插件入口。
- 产品介绍拆解：T 恤、马克杯、钥匙扣三个商品角色；首页首屏、详情页模块、素材矩阵与上架前验收。
- 原创视觉复刻：所有商品与页面是新做的概念设计，并在页面中标识为原创复刻，不冒充原案例截图。

请先读 `SOURCES_AND_BOUNDARIES.md` 再用于培训或对外分享。
""",encoding="utf-8")


def build() -> None:
    OUT.mkdir(parents=True,exist_ok=True)
    if PAGES.exists(): shutil.rmtree(PAGES)
    PAGES.mkdir(parents=True)
    pages=[
        page_cover(),
        page_correction(2),
        page_source_map(3),
        page_clawesome_case(4),
        page_bottle_case(5),
        page_real_ui(6),
        page_case_to_system(7),
        page_product_breakdown(8),
        page_visual_system(9),
        page_before_after(10),
        page_homepage(11),
        page_detail_page(12),
        page_asset_matrix(13),
        page_plugin_flow(14),
        page_task_spec(15),
        page_qc(16),
        page_sources(17),
        page_close(18),
    ]
    page_files=[]
    for n, page in enumerate(pages,1):
        file=PAGES/f"case_page_{n:02d}.jpg"
        page.save(file,quality=94,optimize=True,progressive=True)
        page_files.append(file)
    pdf=OUT/"Accio_Work_Clawesome真实案例拆解与视觉复刻_v2.pdf"
    pptx=OUT/"Accio_Work_Clawesome真实案例拆解与视觉复刻_v2.pptx"
    contact=OUT/"preview_contact_sheet_v2.jpg"
    export_pdf(pages,pdf)
    export_pptx(page_files,pptx)
    contact_sheet(page_files,contact)
    sources_markdown(OUT/"SOURCES_AND_BOUNDARIES.md")
    write_readme(OUT/"README.md",len(pages))
    print(f"built {pdf} ({pdf.stat().st_size:,} bytes)")
    print(f"built {pptx} ({pptx.stat().st_size:,} bytes)")
    print(f"built {contact} ({contact.stat().st_size:,} bytes)")


if __name__=="__main__":
    build()
