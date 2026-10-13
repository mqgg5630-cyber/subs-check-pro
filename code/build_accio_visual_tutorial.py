#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build a flattened Chinese PDF + PPTX teaching deck.

The deck is intentionally image-first: every PPTX slide contains one full-slide
raster image, and the PDF consists of the same rendered pages. This makes it a
presentation/viewing deliverable instead of an editable source deck.

Sources summarized in the accompanying README:
- user-provided skills1 branch, Accio visual-optimization notes
- illustrative, AI-generated/publicly provided demo product art

The deck deliberately labels unverified Accio UI locations as "to verify" and
never presents its UI wireframes as official screenshots.
"""
from __future__ import annotations

import argparse
import os
import shutil
import textwrap
from pathlib import Path
from typing import Iterable, Sequence

from PIL import Image, ImageDraw, ImageFilter, ImageFont
from pptx import Presentation
from pptx.util import Inches

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "deliverables" / "accio_visual_optimization"
ASSETS = ROOT / "assets" / "accio_visual_tutorial"
PAGES = Path("/tmp/accio_visual_tutorial_pages")

W, H = 1920, 1080

# Palette: a restrained export/commerce visual system rather than a simulated
# official Accio product UI.
INK = "#0B1D2A"
INK_2 = "#153243"
NAVY = "#082235"
NAVY_2 = "#0D344A"
TEAL = "#45E3D3"
TEAL_2 = "#1AB7AB"
ORANGE = "#FF7A45"
GOLD = "#F5C15C"
MIST = "#EAF1F4"
PAPER = "#F8FBFC"
WHITE = "#FFFFFF"
MUTED = "#9CB4BF"
SLATE = "#54707D"
RED = "#E95F62"
GREEN = "#2FC18C"
BORDER = "#D7E3E8"


def hx(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


def alpha(hex_value: str, opacity: int) -> tuple[int, int, int, int]:
    return (*hx(hex_value), opacity)


def pick_font(filename: str, fallback: str) -> str:
    candidates = [
        Path("/tmp/noto-cjk/Sans/OTF/SimplifiedChinese") / filename,
        Path("/usr/share/fonts/truetype/dejavu") / fallback,
    ]
    for candidate in candidates:
        if candidate.exists():
            return str(candidate)
    raise RuntimeError("No font available; install Noto Sans CJK SC or DejaVu Sans.")


FONT_REG = pick_font("NotoSansCJKsc-Regular.otf", "DejaVuSans.ttf")
FONT_MED = pick_font("NotoSansCJKsc-Medium.otf", "DejaVuSans-Bold.ttf")
FONT_BOLD = pick_font("NotoSansCJKsc-Bold.otf", "DejaVuSans-Bold.ttf")


def font(kind: str, size: int) -> ImageFont.FreeTypeFont:
    mapping = {"regular": FONT_REG, "medium": FONT_MED, "bold": FONT_BOLD}
    return ImageFont.truetype(mapping[kind], size)


F = {
    "hero": font("bold", 86),
    "title": font("bold", 50),
    "section": font("bold", 34),
    "subtitle": font("regular", 24),
    "body": font("regular", 23),
    "body_small": font("regular", 19),
    "body_tiny": font("regular", 16),
    "medium": font("medium", 22),
    "medium_small": font("medium", 18),
    "eyebrow": font("medium", 16),
    "mono": font("regular", 18),
    "big_num": font("bold", 42),
}


def rgb(c: str) -> tuple[int, int, int]:
    return hx(c)


def make_bg(dark: bool = False) -> Image.Image:
    base = Image.new("RGB", (W, H), rgb(NAVY if dark else PAPER))
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    if dark:
        gd.ellipse((W - 700, -400, W + 450, 650), fill=alpha(TEAL, 70))
        gd.ellipse((-450, H - 450, 550, H + 350), fill=alpha(ORANGE, 40))
        gd.ellipse((900, 600, 1700, 1400), fill=alpha("#1C7190", 65))
    else:
        gd.ellipse((W - 450, -300, W + 350, 550), fill=alpha("#D7F8F3", 180))
        gd.ellipse((-300, H - 260, 480, H + 380), fill=alpha("#FFF0DC", 180))
        gd.ellipse((700, 720, 1450, 1350), fill=alpha("#EBF8FD", 160))
    glow = glow.filter(ImageFilter.GaussianBlur(85))
    return Image.alpha_composite(base.convert("RGBA"), glow).convert("RGB")


def shadow_box(im: Image.Image, box: tuple[int, int, int, int], radius: int = 28,
               fill: str = WHITE, shadow_opacity: int = 26, shadow_y: int = 10,
               outline: str | None = None) -> None:
    x1, y1, x2, y2 = box
    layer = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    ld.rounded_rectangle((x1, y1 + shadow_y, x2, y2 + shadow_y), radius=radius,
                         fill=(8, 34, 53, shadow_opacity))
    layer = layer.filter(ImageFilter.GaussianBlur(18))
    im.paste(layer, (0, 0), layer)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle(box, radius=radius, fill=rgb(fill), outline=rgb(outline) if outline else None,
                        width=2 if outline else 1)


def rounded_image(im: Image.Image, image: Image.Image, box: tuple[int, int, int, int], radius: int = 28) -> None:
    x1, y1, x2, y2 = box
    target_w, target_h = x2 - x1, y2 - y1
    src = image.copy().convert("RGB")
    scale = max(target_w / src.width, target_h / src.height)
    resized = src.resize((round(src.width * scale), round(src.height * scale)), Image.Resampling.LANCZOS)
    left = max(0, (resized.width - target_w) // 2)
    top = max(0, (resized.height - target_h) // 2)
    cropped = resized.crop((left, top, left + target_w, top + target_h))
    mask = Image.new("L", (target_w, target_h), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, target_w - 1, target_h - 1), radius=radius, fill=255)
    im.paste(cropped, (x1, y1), mask)


def measure(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.FreeTypeFont) -> tuple[int, int]:
    b = draw.textbbox((0, 0), text, font=fnt)
    return b[2] - b[0], b[3] - b[1]


def wrap_text(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.FreeTypeFont, width: int) -> list[str]:
    lines: list[str] = []
    for paragraph in text.split("\n"):
        if not paragraph:
            lines.append("")
            continue
        buf = ""
        for char in paragraph:
            candidate = buf + char
            if buf and measure(draw, candidate, fnt)[0] > width:
                lines.append(buf)
                buf = char
            else:
                buf = candidate
        if buf:
            lines.append(buf)
    return lines


def text_block(im: Image.Image, xy: tuple[int, int], text: str, fnt: ImageFont.FreeTypeFont,
               fill: str, width: int, line_gap: int = 10, max_lines: int | None = None) -> int:
    d = ImageDraw.Draw(im)
    lines = wrap_text(d, text, fnt, width)
    if max_lines is not None:
        lines = lines[:max_lines]
    x, y = xy
    bbox = d.textbbox((0, 0), "中", font=fnt)
    step = (bbox[3] - bbox[1]) + line_gap
    for line in lines:
        d.text((x, y), line, font=fnt, fill=rgb(fill))
        y += step
    return y


def pill(im: Image.Image, x: int, y: int, text: str, fill: str, text_color: str = NAVY,
         pad_x: int = 16, h: int = 36, fnt: ImageFont.FreeTypeFont | None = None) -> int:
    d = ImageDraw.Draw(im)
    fnt = fnt or F["eyebrow"]
    tw, _ = measure(d, text, fnt)
    width = tw + pad_x * 2
    d.rounded_rectangle((x, y, x + width, y + h), radius=h // 2, fill=rgb(fill))
    _, th = measure(d, text, fnt)
    d.text((x + pad_x, y + (h - th) // 2 - 2), text, font=fnt, fill=rgb(text_color))
    return width


def rule(im: Image.Image, x: int, y: int, width: int, color: str = BORDER) -> None:
    d = ImageDraw.Draw(im)
    d.line((x, y, x + width, y), fill=rgb(color), width=2)


def header(im: Image.Image, page: int, title: str, subtitle: str = "", dark: bool = False) -> int:
    color = WHITE if dark else INK
    mut = MUTED if dark else SLATE
    d = ImageDraw.Draw(im)
    pill(im, 100, 72, f"{page:02d}  /  VISUAL PLAYBOOK", TEAL if dark else "#DDF7F3", NAVY,
         fnt=F["eyebrow"])
    d.text((100, 135), title, font=F["title"], fill=rgb(color))
    y = 204
    if subtitle:
        y = text_block(im, (102, 209), subtitle, F["subtitle"], mut, 1420, line_gap=7)
    return y


def footer(im: Image.Image, page: int, dark: bool = False) -> None:
    d = ImageDraw.Draw(im)
    color = "#6990A1" if dark else "#6F8792"
    d.line((100, H - 72, W - 100, H - 72), fill=rgb("#2B5061" if dark else BORDER), width=2)
    d.text((100, H - 52), "Accio 视觉优化教程 + 非 Accio 复刻｜非官方教学演示", font=F["body_tiny"], fill=rgb(color))
    text = f"{page:02d}"
    tw, _ = measure(d, text, F["body_tiny"])
    d.text((W - 100 - tw, H - 52), text, font=F["body_tiny"], fill=rgb(color))


def section_label(im: Image.Image, x: int, y: int, no: str, text: str, color: str = TEAL) -> None:
    d = ImageDraw.Draw(im)
    d.ellipse((x, y, x + 38, y + 38), fill=rgb(color))
    tw, th = measure(d, no, F["eyebrow"])
    d.text((x + 19 - tw / 2, y + 18 - th / 2 - 2), no, font=F["eyebrow"], fill=rgb(NAVY))
    d.text((x + 52, y + 4), text, font=F["medium"], fill=rgb(INK))


def dot(im: Image.Image, x: int, y: int, color: str = TEAL) -> None:
    ImageDraw.Draw(im).ellipse((x, y, x + 12, y + 12), fill=rgb(color))


def small_bullet(im: Image.Image, x: int, y: int, text: str, width: int, color: str = INK,
                 bullet_color: str = TEAL, fnt: ImageFont.FreeTypeFont | None = None) -> int:
    fnt = fnt or F["body_small"]
    dot(im, x, y + 9, bullet_color)
    return text_block(im, (x + 24, y), text, fnt, color, width - 24, line_gap=8)


def crop(image: Image.Image, ratio: float, anchor: str = "center") -> Image.Image:
    im = image.convert("RGB")
    current = im.width / im.height
    if current > ratio:
        nw = int(im.height * ratio)
        if anchor == "left":
            x = 0
        elif anchor == "right":
            x = im.width - nw
        else:
            x = (im.width - nw) // 2
        return im.crop((x, 0, x + nw, im.height))
    nh = int(im.width / ratio)
    y = (im.height - nh) // 2
    return im.crop((0, y, im.width, y + nh))


def add_scribble(im: Image.Image, x: int, y: int, w: int, color: str = ORANGE) -> None:
    d = ImageDraw.Draw(im)
    d.line((x, y, x + w * .28, y - 10, x + w * .6, y + 9, x + w, y - 3), fill=rgb(color), width=7, joint="curve")


def card_title(im: Image.Image, x: int, y: int, title: str, sub: str = "", dark: bool = False) -> int:
    d = ImageDraw.Draw(im)
    d.text((x, y), title, font=F["medium"], fill=rgb(WHITE if dark else INK))
    y += 35
    if sub:
        y = text_block(im, (x, y), sub, F["body_small"], MUTED if dark else SLATE, 480, line_gap=6)
    return y


def card_number(im: Image.Image, box: tuple[int, int, int, int], number: str, title: str, body: str,
                accent: str, dark: bool = False) -> None:
    x1, y1, x2, y2 = box
    shadow_box(im, box, radius=28, fill=NAVY_2 if dark else WHITE,
               shadow_opacity=16, outline="#315567" if dark else BORDER)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((x1 + 25, y1 + 24, x1 + 88, y1 + 87), radius=18, fill=rgb(accent))
    tw, th = measure(d, number, F["big_num"])
    d.text((x1 + 56 - tw / 2, y1 + 55 - th / 2 - 3), number, font=F["big_num"], fill=rgb(NAVY))
    d.text((x1 + 112, y1 + 28), title, font=F["medium"], fill=rgb(WHITE if dark else INK))
    text_block(im, (x1 + 30, y1 + 112), body, F["body_small"], MUTED if dark else SLATE, x2 - x1 - 60, line_gap=7)


def page_cover(product: Image.Image, supply: Image.Image) -> Image.Image:
    im = make_bg(True)
    d = ImageDraw.Draw(im)
    # right-hand supply visual, intentionally framed as illustrative material.
    shadow_box(im, (1120, 0, 1920, 1080), radius=0, fill=NAVY, shadow_opacity=0)
    right = crop(supply, 800 / 1080, anchor="right")
    right = right.resize((800, 1080), Image.Resampling.LANCZOS)
    overlay = Image.new("RGBA", right.size, alpha(NAVY, 68))
    right = Image.alpha_composite(right.convert("RGBA"), overlay).convert("RGB")
    im.paste(right, (1120, 0))
    # Dark-to-transparent divider.
    band = Image.new("RGBA", (400, H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(band)
    for x in range(400):
        opacity = int(225 * (1 - x / 400))
        bd.line((x, 0, x, H), fill=alpha(NAVY, opacity))
    im.paste(band, (900, 0), band)
    pill(im, 100, 94, "ACCIO 视角 · 非官方教学演示", TEAL, NAVY, fnt=F["eyebrow"], h=42)
    d.text((100, 190), "把一张工厂图", font=F["hero"], fill=rgb(WHITE))
    d.text((100, 294), "变成一套电商视觉", font=F["hero"], fill=rgb(TEAL))
    d.text((106, 420), "Accio 视觉优化教程", font=F["section"], fill=rgb(WHITE))
    d.text((106, 467), "+ 不用 Accio 的复刻路径", font=F["section"], fill=rgb(WHITE))
    text_block(im, (106, 548), "真实输入 · 目标拆解 · 生成复核 · 批量交付\n一份先能做、再能核、最后能复用的图文工作手册", F["body"], MUTED, 700, line_gap=12)
    pill(im, 105, 717, "16:9 图文版", "#17425A", WHITE, fnt=F["eyebrow"])
    pill(im, 270, 717, "每页已扁平化", "#17425A", WHITE, fnt=F["eyebrow"])
    pill(im, 480, 717, "2026 · v1.0", "#17425A", WHITE, fnt=F["eyebrow"])
    # product card over supply image
    shadow_box(im, (1264, 605, 1764, 958), radius=32, fill=WHITE, shadow_opacity=60)
    rounded_image(im, product, (1288, 630, 1740, 868), radius=24)
    d.rounded_rectangle((1288, 884, 1740, 932), radius=16, fill=rgb("#EDF6F5"))
    d.text((1311, 898), "示例产品图 · 仅用于教学版式", font=F["body_tiny"], fill=rgb(INK_2))
    d.text((102, 988), "来源说明与未验证项见末页｜不模拟或声称官方界面", font=F["body_tiny"], fill=rgb("#7DA4B6"))
    return im


def page_scope(page: int) -> Image.Image:
    im = make_bg(False)
    header(im, page, "先看清楚：这份教程解决什么", "不是教你“随便出一张好看的图”，而是把产品图变成可检查、可复用的视觉工作流。")
    d = ImageDraw.Draw(im)
    cards = [
        ("01", "一条工作流", "从真实产品输入到导出前验收，按同一套关口往下走。", TEAL),
        ("02", "一套复刻法", "没有 Accio 时，也能把主图、场景、详情和脚本拆开完成。", ORANGE),
        ("03", "一张验收表", "先看产品一致性与平台规则，再讨论“好不好看”。", GOLD),
    ]
    for i, (n, title, body, ac) in enumerate(cards):
        x = 100 + i * 590
        card_number(im, (x, 325, x + 540, 595), n, title, body, ac)
    shadow_box(im, (100, 650, 1820, 905), radius=30, fill="#F0F7F8", shadow_opacity=10, outline="#D6EBEA")
    section_label(im, 140, 692, "!", "使用边界", ORANGE)
    small_bullet(im, 140, 758, "本材料依据用户提供的项目资料整理；没有伪造 Accio 的实时页面、账号状态或按钮名称。", 760, fnt=F["body_small"])
    small_bullet(im, 955, 758, "所有标成“待本机核对”的入口、权限和导出规格，应以你当前安装版本与平台规则为准。", 720, bullet_color=ORANGE, fnt=F["body_small"])
    text_block(im, (140, 850), "关键原则：真实产品参数优先；生成内容不替代产品合规、认证、功效证明或平台审核。", F["medium"], INK_2, 1500, line_gap=6)
    footer(im, page)
    return im


def page_pipeline(page: int) -> Image.Image:
    im = make_bg(False)
    header(im, page, "一条图像生产线，五个关口", "顺序不重要；把每一关的输出留下来，下一轮才会越做越快。")
    d = ImageDraw.Draw(im)
    stages = [
        ("01", "真实输入", "照片 + 参数 + 边界", TEAL),
        ("02", "视觉策略", "受众 + 目标 + 版式", ORANGE),
        ("03", "生成试做", "每次一种素材类型", GOLD),
        ("04", "人工复核", "一致性 + 合规 + 手机端", TEAL),
        ("05", "交付归档", "命名 + 尺寸 + SKU 台账", ORANGE),
    ]
    xs = [100, 455, 810, 1165, 1520]
    for i, (n, title, body, ac) in enumerate(stages):
        x = xs[i]
        if i < len(stages) - 1:
            d.line((x + 245, 460, xs[i + 1] - 26, 460), fill=rgb("#B5CED5"), width=5)
            d.polygon([(xs[i + 1] - 26, 448), (xs[i + 1] - 4, 460), (xs[i + 1] - 26, 472)], fill=rgb("#B5CED5"))
        shadow_box(im, (x, 315, x + 285, 605), radius=30, fill=WHITE, shadow_opacity=18, outline=BORDER)
        d.ellipse((x + 30, 348, x + 100, 418), fill=rgb(ac))
        tw, th = measure(d, n, F["medium"])
        d.text((x + 65 - tw / 2, 383 - th / 2 - 2), n, font=F["medium"], fill=rgb(NAVY))
        text_block(im, (x + 30, 447), title, F["medium"], INK, 220, line_gap=5)
        text_block(im, (x + 30, 505), body, F["body_small"], SLATE, 220, line_gap=7)
    shadow_box(im, (100, 690, 1820, 875), radius=30, fill=NAVY, shadow_opacity=30)
    pill(im, 140, 731, "别跳过第 01 和第 04 关", ORANGE, WHITE, fnt=F["eyebrow"])
    text_block(im, (140, 790), "输入不真实，后面的“精致”会放大错误；复核不严谨，生成图会在商品页、售后或平台审核时反过来制造风险。", F["body"], WHITE, 1450, line_gap=10)
    footer(im, page)
    return im


def page_inputs(page: int, product: Image.Image) -> Image.Image:
    im = make_bg(False)
    header(im, page, "01｜准备输入：先把“真实”留在前面", "模型可以帮你生成视觉，但不能替你确认产品事实。先把可验证的信息写进任务。")
    shadow_box(im, (100, 295, 788, 908), radius=34, fill=WHITE, shadow_opacity=22, outline=BORDER)
    rounded_image(im, product, (125, 320, 763, 728), radius=26)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((125, 756, 763, 847), radius=20, fill=rgb("#EFF8F7"))
    d.text((154, 777), "示例：清晰、单品、角度明确的输入图", font=F["medium_small"], fill=rgb(INK_2))
    d.text((154, 813), "不是客户实拍，不可直接当成商品宣称依据", font=F["body_tiny"], fill=rgb(SLATE))
    shadow_box(im, (840, 295, 1820, 908), radius=34, fill=WHITE, shadow_opacity=22, outline=BORDER)
    section_label(im, 885, 335, "A", "必须给到的四类信息", TEAL)
    checks = [
        ("产品照片", "至少一张清晰主视图；有结构细节、颜色差异时补特写。"),
        ("真实参数", "材质、尺寸、颜色、型号、适用范围，以及不能被改写的结构。"),
        ("使用目标", "这张图用在列表页、详情页、首页还是社媒？优先级不同。"),
        ("平台边界", "画幅、白底、禁用词、是否可加人物/道具，按当前平台规则确认。"),
    ]
    y = 408
    for idx, (name, body) in enumerate(checks, 1):
        d.ellipse((888, y + 2, 925, y + 39), fill=rgb(TEAL if idx % 2 else ORANGE))
        t = str(idx)
        tw, th = measure(d, t, F["eyebrow"])
        d.text((906.5 - tw / 2, y + 20 - th / 2 - 2), t, font=F["eyebrow"], fill=rgb(NAVY))
        d.text((946, y), name, font=F["medium"], fill=rgb(INK))
        text_block(im, (946, y + 34), body, F["body_small"], SLATE, 790, line_gap=7)
        y += 113
    d.rounded_rectangle((885, 786, 1768, 855), radius=18, fill=rgb("#FFF2EC"))
    d.text((910, 805), "红线：不能让生成图虚构认证、夸大功效、改变真实结构，或替代必要的商品证明。", font=F["body_small"], fill=rgb("#A84D34"))
    footer(im, page)
    return im


def page_prompt(page: int) -> Image.Image:
    im = make_bg(False)
    header(im, page, "02｜写出目标，而不是一句“帮我做图”", "一个可复用的任务，至少写清“做什么、给谁看、怎么摆、什么风格、什么不能变”。")
    d = ImageDraw.Draw(im)
    prompt_box = (100, 304, 1120, 872)
    shadow_box(im, prompt_box, radius=32, fill=NAVY, shadow_opacity=30)
    pill(im, 142, 345, "可复制的任务结构", TEAL, NAVY, fnt=F["eyebrow"])
    prompt = (
        "以我上传的真实产品图为主体，先复述材质、颜色与结构，\n"
        "等我确认后，再为【1688 列表页】做一张【白底主图】。\n"
        "画面要求：产品居中、轮廓清楚、留出安全边距；\n"
        "风格：干净、可信、以手机端第一眼识别为优先。\n"
        "不得改变产品结构，不添加未经确认的功能或认证信息。"
    )
    text_block(im, (145, 420), prompt, F["body"], WHITE, 925, line_gap=14)
    d.rounded_rectangle((145, 740, 1075, 817), radius=18, fill=rgb("#123F55"))
    d.text((172, 762), "先让工具“复述事实” → 再确认 → 再生成，能显著减少看起来漂亮但产品不对的首版。", font=F["body_tiny"], fill=rgb("#CBE6EA"))
    items = [
        ("产品", "真实图 + 真实参数", TEAL),
        ("目标", "主图 / 场景 / 详情 / 脚本", ORANGE),
        ("构图", "主体位置、留白、画幅", GOLD),
        ("风格", "真实感 / 氛围 / 人群", TEAL),
        ("边界", "不能改什么、不能说什么", ORANGE),
    ]
    y = 306
    for title, body, ac in items:
        shadow_box(im, (1190, y, 1818, y + 94), radius=22, fill=WHITE, shadow_opacity=12, outline=BORDER)
        d.rounded_rectangle((1220, y + 22, 1235, y + 72), radius=7, fill=rgb(ac))
        d.text((1260, y + 17), title, font=F["medium"], fill=rgb(INK))
        d.text((1260, y + 53), body, font=F["body_small"], fill=rgb(SLATE))
        y += 110
    footer(im, page)
    return im


def page_outputs(page: int) -> Image.Image:
    im = make_bg(False)
    header(im, page, "03｜先拆成四类素材，再决定先做哪一类", "同一张产品图的“好看”，在不同位置有不同职责。不要用一张图承担所有任务。")
    d = ImageDraw.Draw(im)
    cells = [
        ((100, 310, 918, 555), "主图", "列表页第一眼", "主体清楚、卖点聚焦、缩小后仍能识别", TEAL, "01"),
        ((1002, 310, 1820, 555), "场景图", "让人看到使用时刻", "场景服务产品；道具不能抢走主体", ORANGE, "02"),
        ((100, 615, 918, 860), "详情页素材", "把信息读清楚", "参数、结构、使用步骤按阅读顺序拆开", GOLD, "03"),
        ((1002, 615, 1820, 860), "视频脚本", "把静态信息变成故事", "先写镜头与卖点，再决定是否生成视频", TEAL, "04"),
    ]
    for box, title, subtitle, body, ac, no in cells:
        x1, y1, x2, y2 = box
        shadow_box(im, box, radius=32, fill=WHITE, shadow_opacity=18, outline=BORDER)
        d.rounded_rectangle((x1 + 30, y1 + 29, x1 + 92, y1 + 91), radius=18, fill=rgb(ac))
        tw, th = measure(d, no, F["medium"])
        d.text((x1 + 61 - tw / 2, y1 + 60 - th / 2 - 2), no, font=F["medium"], fill=rgb(NAVY))
        d.text((x1 + 122, y1 + 29), title, font=F["section"], fill=rgb(INK))
        d.text((x1 + 124, y1 + 80), subtitle, font=F["medium_small"], fill=rgb(ac if ac != GOLD else "#AF7710"))
        rule(im, x1 + 30, y1 + 126, x2 - x1 - 60)
        text_block(im, (x1 + 32, y1 + 153), body, F["body"], SLATE, x2 - x1 - 64, line_gap=9)
    footer(im, page)
    return im


def page_review(page: int) -> Image.Image:
    im = make_bg(False)
    header(im, page, "04｜首版生成后，先做五项质检", "视觉生成不是“看到一张图就导出”；把这些检查做成团队共同语言。")
    d = ImageDraw.Draw(im)
    tests = [
        ("一致性", "颜色、瓶盖、结构、材质是否仍是原产品？", TEAL),
        ("识别度", "缩小到手机列表里，主体能否在一眼内看清？", ORANGE),
        ("版式", "主体、留白、文字安全区是否适配目标画幅？", GOLD),
        ("合规性", "有无虚构认证、绝对化功效、未获授权的标识？", RED),
        ("可交付", "尺寸、命名、SKU 对应关系、版本号是否完整？", GREEN),
    ]
    start_x = 100
    for i, (title, body, ac) in enumerate(tests):
        x = start_x + i * 350
        shadow_box(im, (x, 340, x + 310, 695), radius=28, fill=WHITE, shadow_opacity=17, outline=BORDER)
        d.ellipse((x + 32, 374, x + 102, 444), fill=rgb(ac))
        d.text((x + 123, 378), title, font=F["medium"], fill=rgb(INK))
        # simple check glyph
        d.line((x + 51, 407, x + 64, 420, x + 86, 392), fill=rgb(NAVY), width=7, joint="curve")
        text_block(im, (x + 32, 485), body, F["body_small"], SLATE, 246, line_gap=8)
    shadow_box(im, (100, 760, 1820, 890), radius=28, fill="#EEF8F7", shadow_opacity=8, outline="#CDECE8")
    d.text((140, 790), "复核决策", font=F["medium"], fill=rgb(INK))
    pill(im, 332, 782, "通过", TEAL, NAVY, fnt=F["eyebrow"])
    d.line((460, 801, 800, 801), fill=rgb("#8AB9B8"), width=4)
    d.polygon([(800, 791), (818, 801), (800, 811)], fill=rgb("#8AB9B8"))
    d.text((844, 789), "导出并归档", font=F["medium"], fill=rgb(INK))
    pill(im, 1180, 782, "不通过", ORANGE, WHITE, fnt=F["eyebrow"])
    d.line((1328, 801, 1470, 801), fill=rgb("#D6A08A"), width=4)
    d.polygon([(1470, 791), (1488, 801), (1470, 811)], fill=rgb("#D6A08A"))
    d.text((1512, 789), "只改一个变量", font=F["medium"], fill=rgb(INK))
    footer(im, page)
    return im


def page_iterate(page: int, product: Image.Image) -> Image.Image:
    im = make_bg(False)
    header(im, page, "05｜用“只改一个变量”的方式迭代", "一次改背景、角度、文案、人物、光线，最后你无法判断是什么让结果变好或变差。")
    d = ImageDraw.Draw(im)
    # Before card
    shadow_box(im, (100, 308, 610, 860), radius=32, fill=WHITE, shadow_opacity=18, outline=BORDER)
    rounded_image(im, product, (128, 335, 582, 615), radius=22)
    pill(im, 128, 650, "版本 A", "#DDF7F3", NAVY, fnt=F["eyebrow"])
    d.text((128, 705), "白底 · 信息优先", font=F["medium"], fill=rgb(INK))
    text_block(im, (128, 748), "先确认产品结构、颜色和主体比例。", F["body_small"], SLATE, 410, line_gap=7)
    # Middle instruction
    shadow_box(im, (680, 405, 1230, 760), radius=32, fill=NAVY, shadow_opacity=25)
    pill(im, 720, 446, "只改变：使用场景", ORANGE, WHITE, fnt=F["eyebrow"])
    text_block(im, (720, 512), "“保留产品的材质、颜色、瓶盖和比例。\n仅把背景改为清晨徒步补水场景，\n产品仍为画面主体，不能遮挡瓶身。”", F["body"], WHITE, 455, line_gap=12)
    # After conceptual card
    shadow_box(im, (1300, 308, 1820, 860), radius=32, fill="#DDF0F0", shadow_opacity=18, outline="#B8E0DC")
    # constructed backdrop
    bg = Image.new("RGB", (462, 280), rgb("#E5F2EF"))
    bd = ImageDraw.Draw(bg)
    bd.ellipse((-90, 100, 300, 430), fill=rgb("#C7E4DB"))
    bd.ellipse((210, 120, 590, 450), fill=rgb("#B3D7CA"))
    bd.polygon([(0, 210), (180, 80), (350, 210)], fill=rgb("#89B9AE"))
    bd.polygon([(210, 240), (360, 120), (500, 240)], fill=rgb("#74AA9E"))
    rounded_image(im, bg, (1328, 335, 1792, 615), radius=22)
    # Overlay product in a small framed cutout to avoid claiming a real generated scene.
    product_card = crop(product, 0.72).resize((145, 202), Image.Resampling.LANCZOS)
    im.paste(product_card, (1487, 393))
    pill(im, 1328, 650, "版本 B", "#FFF0E9", "#A84D34", fnt=F["eyebrow"])
    d.text((1328, 705), "场景 · 吸引力优先", font=F["medium"], fill=rgb(INK))
    text_block(im, (1328, 748), "概念示意：仍需拿真实产品图重新生成并人工复核。", F["body_small"], SLATE, 430, line_gap=7)
    footer(im, page)
    return im


def page_batch(page: int) -> Image.Image:
    im = make_bg(False)
    header(im, page, "06｜多 SKU 不要急着批量：先立台账", "批量的核心不是“多出图”，而是让每一张图都能追溯到正确的产品、版本和用途。")
    d = ImageDraw.Draw(im)
    shadow_box(im, (100, 300, 1230, 866), radius=32, fill=WHITE, shadow_opacity=17, outline=BORDER)
    # spreadsheet header
    columns = [(130, 150, "SKU"), (280, 200, "真实输入"), (480, 200, "素材类型"), (680, 190, "版本 / 修改项"), (870, 180, "验收状态"), (1050, 150, "交付名")]
    d.rounded_rectangle((128, 340, 1202, 398), radius=16, fill=rgb(NAVY))
    for x, _, name in columns:
        d.text((x, 359), name, font=F["medium_small"], fill=rgb(WHITE))
    rows = [
        ("WB-01", "主视图 + 尺寸", "白底主图", "v01 / 背景", "待复核", "WB-01_main"),
        ("WB-01", "主视图 + 参数", "场景图", "v02 / 场景", "通过", "WB-01_scene"),
        ("WB-02", "颜色特写", "详情页", "v01 / 文案", "待复核", "WB-02_detail"),
        ("WB-03", "主视图 + 型号", "视频脚本", "v01 / 镜头", "草稿", "WB-03_script"),
        ("…", "…", "…", "…", "…", "…"),
    ]
    y = 416
    for ri, row in enumerate(rows):
        fill = "#F8FBFC" if ri % 2 == 0 else "#EFF6F8"
        d.rounded_rectangle((128, y, 1202, y + 66), radius=10, fill=rgb(fill))
        xs = [130, 280, 480, 680, 870, 1050]
        for ci, value in enumerate(row):
            color = GREEN if value == "通过" else (ORANGE if value == "待复核" else (SLATE if value not in ("草稿",) else "#AA7A21"))
            d.text((xs[ci], y + 22), value, font=F["body_tiny"], fill=rgb(color if ci == 4 else INK_2))
        y += 76
    shadow_box(im, (1290, 300, 1820, 866), radius=32, fill=NAVY, shadow_opacity=23)
    d.text((1330, 344), "批量三步", font=F["section"], fill=rgb(WHITE))
    stages = [
        ("A", "建字段", "先登记 SKU、实拍图、用途与禁改项。", TEAL),
        ("B", "小样验证", "每类产品先跑 1 个，再复制已通过的模板。", ORANGE),
        ("C", "分批复核", "把“通过 / 待改 / 弃用”写回台账。", GOLD),
    ]
    y = 440
    for letter, title, body, ac in stages:
        d.ellipse((1332, y, 1385, y + 53), fill=rgb(ac))
        tw, th = measure(d, letter, F["medium"])
        d.text((1358 - tw / 2, y + 26 - th / 2 - 2), letter, font=F["medium"], fill=rgb(NAVY))
        d.text((1410, y + 1), title, font=F["medium"], fill=rgb(WHITE))
        text_block(im, (1410, y + 34), body, F["body_small"], "#BDD7DE", 340, line_gap=7)
        y += 126
    footer(im, page)
    return im


def page_ui_checklist(page: int) -> Image.Image:
    im = make_bg(False)
    header(im, page, "Accio 实操界面：只把它当作核对清单", "我无法打开你的 Accio 实例；下图是“任务流线框”，不是官方界面截图。入口名称请在本机版本核对。")
    d = ImageDraw.Draw(im)
    # Mock app frame deliberately marked as a wireframe.
    shadow_box(im, (100, 300, 1260, 870), radius=30, fill=WHITE, shadow_opacity=25, outline=BORDER)
    d.rounded_rectangle((100, 300, 1260, 374), radius=30, fill=rgb(NAVY))
    d.rectangle((100, 342, 1260, 374), fill=rgb(NAVY))
    d.ellipse((135, 326, 150, 341), fill=rgb(ORANGE)); d.ellipse((160, 326, 175, 341), fill=rgb(GOLD)); d.ellipse((185, 326, 200, 341), fill=rgb(TEAL))
    d.text((232, 319), "任务流线框 · NOT AN OFFICIAL UI", font=F["eyebrow"], fill=rgb("#C2DCE2"))
    d.rounded_rectangle((128, 402, 382, 830), radius=18, fill=rgb("#EFF6F8"))
    for i, item in enumerate(["新建任务", "上传真实产品图", "写任务与边界", "确认计划 / 权限", "查看结果并导出"]):
        y = 430 + i * 72
        d.rounded_rectangle((150, y, 360, y + 48), radius=12, fill=rgb(TEAL if i == 0 else WHITE))
        d.text((170, y + 14), item, font=F["body_tiny"], fill=rgb(NAVY if i == 0 else INK_2))
    d.rounded_rectangle((414, 402, 1228, 830), radius=18, fill=rgb("#F8FBFC"))
    pill(im, 450, 438, "待本机核对", "#FFF0E9", "#A84D34", fnt=F["eyebrow"])
    text_block(im, (450, 500), "你要找的不是“某个神奇按钮”，而是：\n1. 能否上传真实图；2. 能否明确任务；3. 是否先展示执行计划；\n4. 涉及发布、发送或对外操作时，是否会要求你确认。", F["body"], INK, 700, line_gap=13)
    d.rounded_rectangle((450, 687, 1188, 778), radius=17, fill=rgb("#E4F5F2"))
    d.text((482, 710), "如果入口名称不同：用“视觉 / 图片 / 商品 / 任务 / 导出”等关键词搜，", font=F["body_small"], fill=rgb(INK_2))
    d.text((482, 742), "但不要跳过权限确认或直接把结果发布到商品页。", font=F["body_small"], fill=rgb(INK_2))
    shadow_box(im, (1320, 300, 1820, 870), radius=30, fill=NAVY, shadow_opacity=25)
    pill(im, 1360, 344, "人工必须把关", ORANGE, WHITE, fnt=F["eyebrow"])
    high_risk = ["发送询盘、邮件或消息", "发布 / 覆盖商品素材", "授权第三方应用", "读取或写入本地文件", "使用涉及客户数据的输入"]
    y = 425
    for text in high_risk:
        y = small_bullet(im, 1365, y, text, 395, color=WHITE, bullet_color=ORANGE, fnt=F["body_small"]) + 18
    footer(im, page)
    return im


def page_replicate(page: int, product: Image.Image) -> Image.Image:
    im = make_bg(True)
    header(im, page, "不用 Accio，也可以复刻“工作流”", "复刻的是从输入到验收的做事方式，不是对任何产品功能、界面或结果的复制。", dark=True)
    d = ImageDraw.Draw(im)
    shadow_box(im, (100, 308, 510, 866), radius=32, fill="#123A4E", shadow_opacity=25, outline="#315F71")
    rounded_image(im, product, (128, 340, 482, 575), radius=22)
    pill(im, 128, 610, "真实输入", TEAL, NAVY, fnt=F["eyebrow"])
    text_block(im, (128, 670), "实拍图\n+ 参数\n+ 使用目标", F["section"], WHITE, 300, line_gap=10)
    # Pipeline nodes
    nodes = [
        ("图像生成", "主图 / 场景概念", TEAL),
        ("图像编辑", "裁切 / 留白 / 版式", ORANGE),
        ("文案与脚本", "详情 / 镜头 / 说明", GOLD),
    ]
    y = 322
    for idx, (title, body, ac) in enumerate(nodes):
        x1, x2 = 690, 1260
        shadow_box(im, (x1, y, x2, y + 150), radius=25, fill=WHITE, shadow_opacity=18)
        d.ellipse((725, y + 40, 792, y + 107), fill=rgb(ac))
        d.text((826, y + 34), title, font=F["medium"], fill=rgb(INK))
        d.text((826, y + 78), body, font=F["body_small"], fill=rgb(SLATE))
        d.line((515, 475 if idx == 1 else y + 75, 668, y + 75), fill=rgb("#76B2B5"), width=4)
        d.polygon([(668, y + 65), (686, y + 75), (668, y + 85)], fill=rgb("#76B2B5"))
        y += 178
    shadow_box(im, (1430, 308, 1820, 866), radius=32, fill="#123A4E", shadow_opacity=25, outline="#315F71")
    pill(im, 1468, 350, "可交付素材包", ORANGE, WHITE, fnt=F["eyebrow"])
    for i, label in enumerate(["白底主图", "场景图", "详情页模块", "短视频脚本", "SKU 台账"]):
        yy = 430 + i * 68
        d.rounded_rectangle((1468, yy, 1778, yy + 45), radius=12, fill=rgb("#1A5068"))
        d.text((1493, yy + 13), label, font=F["body_tiny"], fill=rgb("#E8FAF8"))
    footer(im, page, dark=True)
    return im


def page_main_image(page: int, product: Image.Image) -> Image.Image:
    im = make_bg(False)
    header(im, page, "复刻示范 01｜主图的版式不是“越多越好”", "示例只演示视觉层级：先让产品被看清，再考虑补充信息。实际尺寸与白底规则请以目标平台为准。")
    d = ImageDraw.Draw(im)
    shadow_box(im, (100, 300, 900, 872), radius=32, fill=WHITE, shadow_opacity=20, outline=BORDER)
    # A curated product canvas
    d.rounded_rectangle((136, 340, 864, 778), radius=24, fill=rgb("#F0F2F1"))
    p = crop(product, 1.15).resize((380, 380), Image.Resampling.LANCZOS)
    im.paste(p, (310, 365))
    d.line((136, 811, 864, 811), fill=rgb(BORDER), width=2)
    d.text((164, 831), "主图示意｜主体居中 · 背景干净 · 留出安全边距", font=F["body_tiny"], fill=rgb(SLATE))
    shadow_box(im, (975, 300, 1820, 872), radius=32, fill=WHITE, shadow_opacity=20, outline=BORDER)
    section_label(im, 1020, 345, "✓", "主图四个检查点", TEAL)
    points = [
        ("主体", "产品轮廓清楚，不被文字、道具或过强阴影遮挡。"),
        ("比例", "主体占画面比例合理，缩小后仍能识别品类。"),
        ("背景", "纯色/浅色的选择、白底容差、阴影强度要按平台规范确认。"),
        ("信息", "标题、参数、认证等可写内容必须有证据，并留出手机端安全区。"),
    ]
    y = 420
    for idx, (name, body) in enumerate(points):
        d.text((1025, y), f"{idx + 1:02d}", font=F["medium"], fill=rgb(TEAL if idx % 2 == 0 else ORANGE))
        d.text((1090, y), name, font=F["medium"], fill=rgb(INK))
        y2 = text_block(im, (1090, y + 34), body, F["body_small"], SLATE, 650, line_gap=7)
        y = y2 + 20
    footer(im, page)
    return im


def page_scene_detail(page: int, product: Image.Image, supply: Image.Image) -> Image.Image:
    im = make_bg(False)
    header(im, page, "复刻示范 02｜场景、详情页、首页要各做各的事", "同一个产品可以有统一视觉语言，但不要让每一张图长得一样。")
    d = ImageDraw.Draw(im)
    cards = [
        ((100, 320, 650, 850), "场景图", "先选择一个明确使用时刻", ORANGE),
        ((685, 320, 1235, 850), "详情页", "按读图顺序拆卖点和参数", TEAL),
        ((1270, 320, 1820, 850), "首页 / 首屏", "统一颜色与信任信息", GOLD),
    ]
    for box, title, body, ac in cards:
        x1, y1, x2, y2 = box
        shadow_box(im, box, radius=30, fill=WHITE, shadow_opacity=18, outline=BORDER)
        d.rounded_rectangle((x1 + 28, y1 + 28, x1 + 128, y1 + 62), radius=14, fill=rgb(ac))
        d.text((x1 + 46, y1 + 37), title, font=F["eyebrow"], fill=rgb(NAVY))
        d.text((x1 + 28, y1 + 92), body, font=F["medium"], fill=rgb(INK))
    # first card: conceptual outdoor photo with product inner card
    backdrop = Image.new("RGB", (494, 235), rgb("#DDEFEA"))
    bd = ImageDraw.Draw(backdrop)
    bd.ellipse((-80, 100, 330, 440), fill=rgb("#C0DFD3"))
    bd.polygon([(0, 200), (160, 25), (330, 200)], fill=rgb("#8EB9A9"))
    bd.polygon([(180, 220), (365, 55), (540, 220)], fill=rgb("#77A596"))
    rounded_image(im, backdrop, (128, 453, 622, 688), radius=20)
    im.paste(crop(product, .72).resize((110, 155), Image.Resampling.LANCZOS), (315, 493))
    d.text((130, 720), "概念构图：保留产品为画面主体", font=F["body_tiny"], fill=rgb(SLATE))
    # second card: detail page blocks
    x = 713
    for idx, (k, v) in enumerate([("01", "材质 / 尺寸"), ("02", "结构 / 细节"), ("03", "使用 / 清洁")]):
        yy = 438 + idx * 91
        d.rounded_rectangle((x, yy, 1207, yy + 70), radius=14, fill=rgb("#EFF7F8" if idx % 2 == 0 else "#FFF4E9"))
        d.text((x + 20, yy + 22), k, font=F["medium_small"], fill=rgb(TEAL if idx % 2 == 0 else ORANGE))
        d.text((x + 87, yy + 21), v, font=F["medium_small"], fill=rgb(INK_2))
    d.text((713, 742), "先信息化，再装饰化", font=F["body_tiny"], fill=rgb(SLATE))
    # third card: crop supply visual as a mood panel.
    rounded_image(im, supply, (1298, 453, 1792, 650), radius=20)
    d.rounded_rectangle((1298, 681, 1792, 755), radius=14, fill=rgb("#ECF3F7"))
    d.text((1322, 704), "首屏：品牌语气 + 核心价值 + 行动入口", font=F["body_tiny"], fill=rgb(INK_2))
    footer(im, page)
    return im


def page_acceptance(page: int) -> Image.Image:
    im = make_bg(False)
    header(im, page, "交付前验收｜一张清单避免“好看但不能卖”", "把视觉检查、平台检查和文件检查放在同一张表里，交付时不靠记忆。")
    d = ImageDraw.Draw(im)
    shadow_box(im, (100, 300, 1820, 870), radius=32, fill=WHITE, shadow_opacity=20, outline=BORDER)
    # table
    cols = [100, 350, 880, 1300, 1600]
    d.rounded_rectangle((128, 338, 1792, 396), radius=15, fill=rgb(NAVY))
    headers = [(155, "关口"), (385, "检查问题"), (915, "通过标准"), (1335, "留档"), (1630, "状态")]
    for x, txt in headers:
        d.text((x, 358), txt, font=F["medium_small"], fill=rgb(WHITE))
    rows = [
        ("产品", "图中是否仍是正确型号、颜色与结构？", "与真实输入一致", "原图 / 参数", "□"),
        ("画面", "裁切、留白、比例、文字安全区是否合理？", "目标画幅可读", "版本号", "□"),
        ("宣称", "是否出现无法证明的认证、功效或比较？", "删掉或补证据", "依据", "□"),
        ("平台", "尺寸、白底、人物、禁用词规则是否核对？", "按当前规则", "链接 / 截图", "□"),
        ("文件", "SKU、用途、日期、导出尺寸是否能追溯？", "命名一致", "台账", "□"),
    ]
    y = 418
    for i, row in enumerate(rows):
        fill = "#F8FBFC" if i % 2 == 0 else "#F0F6F7"
        d.rounded_rectangle((128, y, 1792, y + 70), radius=11, fill=rgb(fill))
        xs = [155, 385, 915, 1335, 1645]
        widths = [180, 480, 360, 250, 90]
        fonts = [F["medium_small"], F["body_tiny"], F["body_tiny"], F["body_tiny"], F["medium"]]
        for x, val, fw, ft in zip(xs, row, widths, fonts):
            text_block(im, (x, y + 18), val, ft, INK if x == 155 else SLATE, fw, line_gap=3, max_lines=2)
        y += 80
    d.rounded_rectangle((128, 806, 1792, 845), radius=12, fill=rgb("#FFF2EC"))
    d.text((155, 816), "建议命名：SKU_用途_画幅_版本_日期，例如 WB-01_main_1x1_v03_20261013.jpg", font=F["body_tiny"], fill=rgb("#A84D34"))
    footer(im, page)
    return im


def page_twenty_minutes(page: int) -> Image.Image:
    im = make_bg(False)
    header(im, page, "20 分钟小练习｜只用一个 SKU 跑通第一轮", "不要一开始就要“50 个 SKU 全自动”；先证明一张图的输入、质检和归档都能闭环。")
    d = ImageDraw.Draw(im)
    steps = [
        ("00–03 分", "选一张图", "挑最清晰的主视图；列出三条不能改的真实参数。", TEAL),
        ("03–07 分", "写任务", "按“产品 / 目标 / 构图 / 风格 / 边界”写出首版任务。", ORANGE),
        ("07–12 分", "出一类素材", "先只做白底主图，不要混入场景、文案和视频。", GOLD),
        ("12–16 分", "做五项质检", "产品一致、识别度、版式、合规、文件名。", TEAL),
        ("16–20 分", "归档并复盘", "记录版本、修改项和下一步，再决定是否放大到多 SKU。", ORANGE),
    ]
    x = 100
    for i, (time, title, body, ac) in enumerate(steps):
        y = 320 + (i % 2) * 310
        if i == 3:
            x = 100
        elif i == 4:
            x = 705
        box = (x, y, x + 510, y + 235)
        shadow_box(im, box, radius=28, fill=WHITE, shadow_opacity=18, outline=BORDER)
        pill(im, x + 28, y + 28, time, ac, NAVY if ac != ORANGE else WHITE, fnt=F["eyebrow"])
        d.text((x + 28, y + 88), title, font=F["section"], fill=rgb(INK))
        text_block(im, (x + 28, y + 140), body, F["body_small"], SLATE, 440, line_gap=8)
        x += 605
    shadow_box(im, (1310, 635, 1820, 865), radius=30, fill=NAVY, shadow_opacity=24)
    pill(im, 1350, 677, "完成信号", TEAL, NAVY, fnt=F["eyebrow"])
    text_block(im, (1350, 742), "你能说清楚：\n这张图从哪里来、\n改过什么、\n为什么可以上架。", F["body"], WHITE, 400, line_gap=12)
    footer(im, page)
    return im


def page_prompt_pack(page: int) -> Image.Image:
    im = make_bg(True)
    header(im, page, "附录｜一条可复制的起步提示词", "先让工具复述真实信息；确认后才做视觉任务。下方内容可用于 Accio 或其他合规的图像工作流。", dark=True)
    d = ImageDraw.Draw(im)
    shadow_box(im, (100, 310, 1820, 870), radius=32, fill="#10344A", shadow_opacity=28, outline="#2F6072")
    pill(im, 145, 351, "COPY / PASTE", TEAL, NAVY, fnt=F["eyebrow"])
    prompt = (
        "我会上传一张真实产品图。请先只做两件事：\n"
        "1）复述你能确认的材质、颜色、结构和画面角度；\n"
        "2）列出你还缺少的尺寸、型号、目标平台和禁改项。\n\n"
        "在我确认前，不要生成、不虚构认证或功能。确认后，请为【目标平台 / 用途】\n"
        "生成【白底主图 / 场景图 / 详情页模块 / 视频脚本】中的一种。\n"
        "要求：产品结构不变；主体清楚；输出一份自检清单；每次修改只改一个变量。"
    )
    text_block(im, (148, 427), prompt, F["body"], WHITE, 1500, line_gap=14)
    d.rounded_rectangle((145, 754, 1775, 822), radius=16, fill=rgb("#174B61"))
    d.text((174, 776), "使用提醒：如工具请求发送、发布、授权、访问文件或调用外部服务，请在本机逐项阅读并确认。", font=F["body_small"], fill=rgb("#C9E5E9"))
    footer(im, page, dark=True)
    return im


def page_final(page: int, product: Image.Image) -> Image.Image:
    im = make_bg(False)
    d = ImageDraw.Draw(im)
    pill(im, 100, 76, "END / 下一步", "#DDF7F3", NAVY, fnt=F["eyebrow"])
    d.text((100, 168), "先跑完一小套，", font=F["hero"], fill=rgb(INK))
    d.text((100, 274), "再把它变成系统。", font=F["hero"], fill=rgb(TEAL_2))
    text_block(im, (106, 405), "你现在不需要更多“万能提示词”。\n你需要一张真实产品图、一份明确边界、\n以及一次完整的“生成 → 复核 → 归档”。", F["body"], SLATE, 790, line_gap=14)
    shadow_box(im, (100, 660, 890, 865), radius=30, fill=NAVY, shadow_opacity=26)
    d.text((138, 704), "来源与说明", font=F["medium"], fill=rgb(WHITE))
    text_block(im, (138, 755), "依据用户提供的 skills1 分支中的 Accio 视觉优化资料整理。\n没有接入或验证你的实时 Accio 账户；界面路径均应以本机为准。\n本材料为非官方教学演示，示例产品图不代表真实客户商品。", F["body_tiny"], "#C7DFE5", 700, line_gap=7)
    shadow_box(im, (1040, 105, 1820, 865), radius=42, fill=WHITE, shadow_opacity=28, outline=BORDER)
    rounded_image(im, product, (1090, 160, 1770, 680), radius=32)
    d.rounded_rectangle((1090, 720, 1770, 820), radius=20, fill=rgb("#EFF8F7"))
    d.text((1132, 748), "真实输入  ·  清晰目标  ·  人工验收", font=F["medium"], fill=rgb(INK_2))
    d.text((1132, 784), "从一张图开始，形成可复用的视觉工作流。", font=F["body_small"], fill=rgb(SLATE))
    footer(im, page)
    return im


def export_pdf(pages: Sequence[Image.Image], path: Path) -> None:
    rgb_pages = [p.convert("RGB") for p in pages]
    # Pillow embeds each raster page. This intentionally makes the PDF visual
    # content non-editable/selectable, as requested.
    rgb_pages[0].save(path, "PDF", save_all=True, append_images=rgb_pages[1:], resolution=144.0,
                      quality=92, optimize=True)


def export_pptx(page_files: Sequence[Path], path: Path) -> None:
    prs = Presentation()
    prs.slide_width = Inches(13.333333)
    prs.slide_height = Inches(7.5)
    blank = prs.slide_layouts[6]
    for page in page_files:
        slide = prs.slides.add_slide(blank)
        slide.shapes.add_picture(str(page), 0, 0, width=prs.slide_width, height=prs.slide_height)
    # The only per-slide object is the page image. It is viewable in PowerPoint
    # but its typography/layout are not editable as native shapes.
    prs.core_properties.title = "Accio 视觉优化教程与非 Accio 复刻指南（图文扁平版）"
    prs.core_properties.subject = "非官方教学演示；每页为单张扁平图像"
    prs.core_properties.author = "Arena Agent"
    prs.save(path)


def contact_sheet(page_files: Sequence[Path], path: Path) -> None:
    thumb_w, thumb_h = 384, 216
    cols = 4
    rows = (len(page_files) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * thumb_w + (cols + 1) * 28, rows * thumb_h + (rows + 1) * 38 + 64), rgb("#E8F0F3"))
    d = ImageDraw.Draw(sheet)
    d.text((28, 18), "Accio Visual Optimization Playbook — Flat PDF/PPTX Preview", font=font("medium", 22), fill=rgb(INK))
    for i, p in enumerate(page_files):
        im = Image.open(p).convert("RGB").resize((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        x = 28 + (i % cols) * (thumb_w + 28)
        y = 64 + (i // cols) * (thumb_h + 38)
        sheet.paste(im, (x, y))
        d.rectangle((x, y, x + thumb_w, y + thumb_h), outline=rgb("#BDCBD2"), width=2)
        d.text((x, y + thumb_h + 8), f"{i + 1:02d}", font=font("medium", 16), fill=rgb(SLATE))
    sheet.save(path, quality=88, optimize=True)


def write_readme(path: Path, page_count: int) -> None:
    text = f"""# Accio 视觉优化教程 + 非 Accio 复刻指南（图文扁平版）

## 交付文件

- `Accio_视觉优化教程与非Accio复刻指南_图文版.pdf`：{page_count} 页横版 PDF；每页为已渲染的视觉页面。
- `Accio_视觉优化教程与非Accio复刻指南_图文版.pptx`：{page_count} 页 16:9 PPTX；**每页仅一张完整页面图像**，不提供可编辑文字、图表或原生版式。
- `preview_contact_sheet.jpg`：全页缩略预览。

## 内容范围

1. 真实产品输入与边界；
2. 可复用的视觉任务写法；
3. 主图、场景、详情页、视频脚本四类输出；
4. 首版生成后的五项质检；
5. 单变量迭代、多 SKU 台账和交付验收；
6. Accio 任务流的**待本机核对**清单；
7. 不使用 Accio 时的流程复刻方法与可复制起步提示词。

## 重要说明

- 资料基于用户提供的 GitHub 项目 `shaohuawen03-cyber/skills1` 分支
  `arena/def3bdd3-skills1` 中的 `deliverable/accio_visual_case` 说明材料整理。
- 本环境没有可操作的 Accio 连接器或实时账户，因此**未打开、未验证**任何 Accio 实际界面、
  按钮名称、权限路径或当前平台规格。文中“待本机核对”项目必须在你的 Accio 与目标平台中确认。
- 本文件是非官方教学演示，不代表 Accio 官方文档、功能承诺或平台审核结论。
- 示例产品图仅用于教学版式；不得当作真实商品实拍、认证、功能或效果的证据。
- 所有商品视觉在发布前仍应由人工核验产品一致性、合规性、知识产权和平台规则。

## 生成方式

`code/build_accio_visual_tutorial.py` 将页面先渲染为图片，再写入 PDF 与 PPTX；因此 PPTX 的视觉内容
已扁平化。它仍可被另存或删除整页，这属于 Office 文件容器的正常行为，不提供密码锁定。
"""
    path.write_text(text, encoding="utf-8")


def build() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    if PAGES.exists():
        shutil.rmtree(PAGES)
    PAGES.mkdir(parents=True)
    product_path = ASSETS / "demo_product_bottle.png"
    supply_path = ASSETS / "supply_chain_ai_cover.png"
    if not product_path.exists() or not supply_path.exists():
        raise FileNotFoundError("Missing teaching assets in assets/accio_visual_tutorial")
    product = Image.open(product_path).convert("RGB")
    supply = Image.open(supply_path).convert("RGB")

    pages = [
        page_cover(product, supply),
        page_scope(2),
        page_pipeline(3),
        page_inputs(4, product),
        page_prompt(5),
        page_outputs(6),
        page_review(7),
        page_iterate(8, product),
        page_batch(9),
        page_ui_checklist(10),
        page_replicate(11, product),
        page_main_image(12, product),
        page_scene_detail(13, product, supply),
        page_acceptance(14),
        page_twenty_minutes(15),
        page_prompt_pack(16),
        page_final(17, product),
    ]
    page_files: list[Path] = []
    for no, page in enumerate(pages, 1):
        out = PAGES / f"page_{no:02d}.jpg"
        page.save(out, quality=93, optimize=True, progressive=True)
        page_files.append(out)

    pdf_path = OUT / "Accio_视觉优化教程与非Accio复刻指南_图文版.pdf"
    pptx_path = OUT / "Accio_视觉优化教程与非Accio复刻指南_图文版.pptx"
    preview_path = OUT / "preview_contact_sheet.jpg"
    export_pdf(pages, pdf_path)
    export_pptx(page_files, pptx_path)
    contact_sheet(page_files, preview_path)
    write_readme(OUT / "README.md", len(pages))

    print(f"built {pdf_path} ({pdf_path.stat().st_size:,} bytes)")
    print(f"built {pptx_path} ({pptx_path.stat().st_size:,} bytes)")
    print(f"built {preview_path} ({preview_path.stat().st_size:,} bytes)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", action="store_true", help="build all outputs (default)")
    parser.parse_args()
    build()
