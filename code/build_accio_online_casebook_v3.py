#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build a cited, flattened visual benchmark deck from six online ecommerce cases.

This is a research / critique artifact.  It deliberately uses low-resolution
reference excerpts with a visible source trail instead of inventing another
fictional product case.  All conclusions are practical visual observations;
the deck does not claim brand endorsement, performance guarantees, access to
Accio, or reproduction of a live Accio workflow.

Each PPTX slide is one full-slide raster image.  The matching PDF pages are
also raster images, so the delivery is presentation-ready rather than editable.
"""
from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from PIL import Image, ImageDraw, ImageFilter, ImageFont
from pptx import Presentation
from pptx.util import Inches

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "deliverables" / "accio_online_visual_casebook_v3"
ASSETS = ROOT / "assets" / "accio_online_case_research_v3"
PAGES = Path("/tmp/accio_online_casebook_v3_pages")
W, H = 1920, 1080

# Fonts are installed by the existing render toolchain.  The DejaVu fallback
# is only for a degraded environment; it does not cover all Chinese glyphs.
def pick_font(filename: str, fallback: str) -> str:
    for p in (
        Path("/tmp/noto-cjk/Sans/OTF/SimplifiedChinese") / filename,
        Path("/usr/share/fonts/truetype/dejavu") / fallback,
    ):
        if p.exists():
            return str(p)
    raise RuntimeError("No usable Chinese font found.")


FONT_REG = pick_font("NotoSansCJKsc-Regular.otf", "DejaVuSans.ttf")
FONT_MED = pick_font("NotoSansCJKsc-Medium.otf", "DejaVuSans-Bold.ttf")
FONT_BOLD = pick_font("NotoSansCJKsc-Bold.otf", "DejaVuSans-Bold.ttf")


def f(kind: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(
        {"regular": FONT_REG, "medium": FONT_MED, "bold": FONT_BOLD}[kind], size
    )


F = {
    "hero": f("bold", 74),
    "title": f("bold", 48),
    "title_small": f("bold", 38),
    "subtitle": f("regular", 25),
    "body": f("regular", 24),
    "body_small": f("regular", 20),
    "body_tiny": f("regular", 16),
    "medium": f("medium", 25),
    "medium_small": f("medium", 20),
    "eyebrow": f("medium", 16),
    "number": f("bold", 42),
}

# Neutral support colors. Per-case pages use their own stronger palette.
INK = "#102033"
SLATE = "#5F7080"
PAPER = "#F6F5F1"
WHITE = "#FFFFFF"
BORDER = "#DEE4E7"
MIST = "#E7EEF0"
DARK = "#0F1D2D"

CASE_DATA = [
    {
        "brand": "Magic Spoon",
        "cn": "Magic Spoon｜包装就是页面的第一语言",
        "category": "高饱和食品 / 订阅组合",
        "asset": "magic_spoon_home.jpg",
        "color": "#6D14ED",
        "tint": "#EBD9FF",
        "ink": "#FFFFFF",
        "visual_source": "Luna Templates 的公开页面截图",
        "visual_url": "https://lunatemplates.co/blogs/shopify-website-inspiration/magic-spoon",
        "analysis_source": "Shopify：亮色、动效、UGC 与 BYOB 筛选案例",
        "analysis_url": "https://www.shopify.com/blog/11863377-30-beautiful-and-creative-ecommerce-website-designs",
        "takeaway": "包装色、口味、卖点不是三个版块；它们共同构成第一屏的记忆点。",
        "observations": [
            ("先让人停住", "用高饱和底色、夸张包装与短句，把产品从货架感拉进内容感。"),
            ("再减少选择焦虑", "公开案例说明其组合页使用筛选与“best seller”标签来辅助决定。"),
            ("最后给证据", "评论 / UGC 不应藏在页底，而应成为色彩节奏的一部分。"),
        ],
        "apply": "适合：口味、颜色、套装、订阅等“选择本身很有趣”的品类。",
    },
    {
        "brand": "De La Calle",
        "cn": "De La Calle｜先卖身份与场景，再解释成分",
        "category": "饮料 / 生活方式视频首屏",
        "asset": "de_la_calle_home.png",
        "color": "#E82C20",
        "tint": "#FFE0D8",
        "ink": "#FFFFFF",
        "visual_source": "Shopify 公开案例截图",
        "visual_url": "https://www.shopify.com/blog/11863377-30-beautiful-and-creative-ecommerce-website-designs",
        "analysis_source": "Shopify：价值主张在首屏、属性在下一层",
        "analysis_url": "https://www.shopify.com/blog/11863377-30-beautiful-and-creative-ecommerce-website-designs",
        "takeaway": "先让用户感到“这是谁的饮料”，再让用户阅读糖分、营养、配方。",
        "observations": [
            ("首屏只做一件事", "把“现代墨西哥汽水”放在最大文字位；不是同时塞满所有卖点。"),
            ("人先于瓶", "聚会、拿起、碰杯等动作给了商品社交语境。"),
            ("属性有次序", "健康属性以图形叠加进入下一层，而不是破坏第一眼的气氛。"),
        ],
        "apply": "适合：饮料、香氛、服饰、礼盒等购买动机带有身份和氛围的品类。",
    },
    {
        "brand": "Graza",
        "cn": "Graza｜把“用途”做成 SKU 名字与画面",
        "category": "食品 / 用途型 SKU 架构",
        "asset": "graza_home.jpg",
        "color": "#C5D91D",
        "tint": "#F2F6C8",
        "ink": "#102033",
        "visual_source": "I Love Creatives 的公开站点截图",
        "visual_url": "https://ilovecreatives.com/internet-gem-websites/graza",
        "analysis_source": "Shopify：色彩、烹饪场景、mini cart 与套装/订阅选择",
        "analysis_url": "https://www.shopify.com/blog/11863377-30-beautiful-and-creative-ecommerce-website-designs",
        "takeaway": "优秀的 SKU 不是“橄榄油 A / B”，而是“这个该怎么用”。",
        "observations": [
            ("命名即导购", "把 Drizzle / Sizzle 等使用语境写进产品语言，先消除“买哪瓶”。"),
            ("图像解释动作", "食物、倒油、餐桌比包装静物更快解释产品在生活中出现的位置。"),
            ("加购要顺手", "公开案例提到 mini cart、组合容器与订阅选择；视觉不止用于好看。"),
        ],
        "apply": "适合：同材质、多用途、多规格的产品；先按“任务”组织，再按参数细分。",
    },
    {
        "brand": "Vacation Inc.",
        "cn": "Vacation Inc.｜复古不是滤镜，是整套世界观",
        "category": "防晒 / 复古高级产品叙事",
        "asset": "vacation_product.png",
        "color": "#006C6A",
        "tint": "#D9EFEC",
        "ink": "#FFFFFF",
        "visual_source": "PR Daily 公开产品新闻图",
        "visual_url": "https://www.prdaily.com/how-orange-gelee-sunscreen-made-a-comeback-with-retro-chic-flair/",
        "analysis_source": "Shopify / Sitebuilder Report：复古色彩、颗粒影像、极简产品页",
        "analysis_url": "https://www.shopify.com/blog/11863377-30-beautiful-and-creative-ecommerce-website-designs",
        "takeaway": "如果“氛围”是卖点，包装、背景、字体、摄影颗粒必须像来自同一个世界。",
        "observations": [
            ("用有限色板", "低饱和蓝绿与橙红让包装成为主角；不靠堆积装饰制造高级感。"),
            ("产品像道具", "单支产品拥有明确的摄影位置、材质对比和阴影，而不是被图案淹没。"),
            ("信息分层", "氛围负责吸引；SPF、容量、用法、信任信息再承担购买判断。"),
        ],
        "apply": "适合：美妆、香氛、个护、家居；先定义可执行的摄影 / 字体 / 色板规则。",
    },
    {
        "brand": "Fenty Beauty",
        "cn": "Fenty Beauty｜色号不是表格，是可浏览的内容",
        "category": "美妆 / 质地、色号与选择体验",
        "asset": "fenty_product.jpg",
        "color": "#612936",
        "tint": "#F0E3E1",
        "ink": "#FFFFFF",
        "visual_source": "Fenty Beauty 官方公开产品图",
        "visual_url": "https://fentybeauty.com/",
        "analysis_source": "第三方 PDP 研究：粗体视觉、色号选择、利益导向信息",
        "analysis_url": "https://www.creativecorner.studio/blog/product-page-examples",
        "takeaway": "多变体页面不能只给 SKU 编号；每一个色号都应该带来可感知的视觉差异。",
        "observations": [
            ("先看质感", "近景光影与真实材质优先，让用户在文字之前理解颜色和妆感。"),
            ("再选变体", "色号、试色、适用场景应与购买动作保持同一视线范围。"),
            ("最后补信任", "成分、使用方法、对比和用户图像应回答“适不适合我”。"),
        ],
        "apply": "适合：颜色、面料、款式、香型差异大的 SKU；变体需要“看得见”的证据。",
    },
    {
        "brand": "Stanley Quencher",
        "cn": "Stanley Quencher｜颜色、价格、CTA 的一条直线",
        "category": "耐用品 / 变体与规格清晰表达",
        "asset": "stanley_variants.jpg",
        "color": "#1B75BB",
        "tint": "#DDEFFC",
        "ink": "#FFFFFF",
        "visual_source": "AL.com 公开新闻产品图",
        "visual_url": "https://www.al.com/shopping/2024/07/stanley-surprise-drops-2-new-quencher-tumbler-colors-indigo-and-seafoam.html",
        "analysis_source": "WiserNotify PDP 案例：图像 → 变体 → 价格 → 按钮",
        "analysis_url": "https://wisernotify.com/blog/product-page/",
        "takeaway": "干净不是“信息少”，而是用户的眼睛不需要猜下一步在哪里。",
        "observations": [
            ("商品图必须精确", "颜色、表面、把手、吸管等影响选择的部分要一眼可见。"),
            ("变体紧贴图像", "不要让用户在看完图以后再翻半页找颜色、容量或价格。"),
            ("CTA 不抢戏但不丢失", "唯一主按钮与规格、配送、退换等决策信息组成一个稳定区块。"),
        ],
        "apply": "适合：杯壶、数码、工具、家居等规格明确、颜色会改变购买决定的耐用品。",
    },
]


# ---------------------------------------------------------------------------
# Transparent AI-assisted recreation example
# ---------------------------------------------------------------------------
# This is deliberately an auditable *workflow demonstration*, not a claim that
# Accio was run. The S0 image below was generated in this workspace with an
# Arena image model from the recorded prompt. S1 is a manual, original layout
# rebuilt by this renderer after a human-style review. Neither is a sellable
# product image or a verified SKU.
AI_DEMO_ASSET = "ai_assisted_demo_tide_cup.png"
AI_IMAGE_PROMPT = (
    "A polished 4 by 5 ecommerce concept visual for an entirely fictional, "
    "unbranded product called Tide Cup Demo 01. A clean original cobalt blue "
    "insulated tumbler with a round handle and a straight straw, centered and "
    "clearly silhouetted. Set it on an abstract coral paper backdrop with a "
    "seafoam circular shadow and a few simple geometric color swatches. High "
    "end studio product photography, crisp edges, soft natural shadow, modern "
    "editorial color blocking. Absolutely no text, lettering, logos, trademarks, "
    "packaging labels, or resemblance to any existing brand or product design. "
    "This is an original fictional product concept for a transparent AI assisted "
    "workflow demonstration, not a real commercial item."
)
AI_DEMO_FACTS = [
    ("用途", "仅用于教学：展示“提示词 → 草稿 → 人审 → 重建”的可追溯链路。"),
    ("商品身份", "虚构的 Tide Cup Demo 01；不是一个待上架的真实 SKU。"),
    ("允许复用", "只抽取“单品清晰、色块对比、变体靠近商品”的视觉语法。"),
    ("禁止复用", "品牌、logo、包装、文案、具体产品结构、页面截图、营销主张。"),
]
AI_REVIEW_LOG = [
    ("R-01", "轮廓过近", "带把手 + 吸管的主轮廓仍容易让人联想到参考商品。", "删除把手和吸管；换为封闭旋盖与斜向硅胶环。", "人审", "阻断"),
    ("R-02", "商品事实", "虚构示范没有真实材质、容量、保温或交期证明。", "不写任何性能、认证、价格或配送主张。", "人审", "阻断"),
    ("R-03", "UI 边界", "主视觉里不能烘焙“立即购买”、价格或可点击控件。", "把 CTA 留给真实 PDP 的可访问 DOM / 组件。", "人审", "通过"),
    ("R-04", "版权 / 商标", "参考只用于研究，不可把来源产品认作生成依据或商品素材。", "保存 URL；写清“抽取规则、不复制身份”。", "人审", "通过"),
]


def hx(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


def rgba(value: str, alpha: int) -> tuple[int, int, int, int]:
    return (*hx(value), alpha)


def measure(d: ImageDraw.ImageDraw, text: str, ft: ImageFont.FreeTypeFont) -> tuple[int, int]:
    x1, y1, x2, y2 = d.textbbox((0, 0), text, font=ft)
    return x2 - x1, y2 - y1


def wrap(d: ImageDraw.ImageDraw, text: str, ft: ImageFont.FreeTypeFont, width: int) -> list[str]:
    lines: list[str] = []
    for paragraph in text.split("\n"):
        if not paragraph:
            lines.append("")
            continue
        buf = ""
        for char in paragraph:
            trial = buf + char
            if buf and measure(d, trial, ft)[0] > width:
                lines.append(buf)
                buf = char
            else:
                buf = trial
        if buf:
            lines.append(buf)
    return lines


def textblock(im: Image.Image, xy: tuple[int, int], text: str, ft: ImageFont.FreeTypeFont,
              color: str, width: int, gap: int = 8, max_lines: int | None = None) -> int:
    d = ImageDraw.Draw(im)
    lines = wrap(d, text, ft, width)
    if max_lines is not None:
        lines = lines[:max_lines]
    y = xy[1]
    for line in lines:
        d.text((xy[0], y), line, font=ft, fill=hx(color))
        y += measure(d, line or "A", ft)[1] + gap
    return y


def new_bg(color: str = PAPER, accent: str | None = None) -> Image.Image:
    im = Image.new("RGB", (W, H), hx(color))
    if accent:
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        d.ellipse((W - 480, -340, W + 360, 440), fill=rgba(accent, 45))
        d.ellipse((-360, H - 330, 480, H + 400), fill=rgba(accent, 28))
        layer = layer.filter(ImageFilter.GaussianBlur(95))
        im = Image.alpha_composite(im.convert("RGBA"), layer).convert("RGB")
    return im


def panel(im: Image.Image, box: tuple[int, int, int, int], fill: str = WHITE,
          outline: str | None = None, radius: int = 26, shadow: bool = True) -> None:
    x1, y1, x2, y2 = box
    if shadow:
        layer = Image.new("RGBA", im.size, (0, 0, 0, 0))
        ld = ImageDraw.Draw(layer)
        ld.rounded_rectangle((x1, y1 + 12, x2, y2 + 12), radius=radius,
                             fill=(16, 32, 51, 22))
        layer = layer.filter(ImageFilter.GaussianBlur(18))
        im.paste(layer, (0, 0), layer)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle(box, radius=radius, fill=hx(fill),
                        outline=hx(outline) if outline else None, width=2)


def paste_cover(im: Image.Image, src: Image.Image, box: tuple[int, int, int, int],
                radius: int = 22, shade: int = 0) -> None:
    x1, y1, x2, y2 = box
    tw, th = x2 - x1, y2 - y1
    src = src.convert("RGB")
    scale = max(tw / src.width, th / src.height)
    resized = src.resize((round(src.width * scale), round(src.height * scale)), Image.Resampling.LANCZOS)
    left = max(0, (resized.width - tw) // 2)
    top = max(0, (resized.height - th) // 2)
    cropped = resized.crop((left, top, left + tw, top + th))
    if shade:
        tint = Image.new("RGBA", cropped.size, (0, 0, 0, shade))
        cropped = Image.alpha_composite(cropped.convert("RGBA"), tint).convert("RGB")
    mask = Image.new("L", (tw, th), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, tw - 1, th - 1), radius=radius, fill=255)
    im.paste(cropped, (x1, y1), mask)


def pill(im: Image.Image, x: int, y: int, label: str, bg: str, fg: str, h: int = 34) -> int:
    d = ImageDraw.Draw(im)
    tw, _ = measure(d, label, F["eyebrow"])
    w = tw + 28
    d.rounded_rectangle((x, y, x + w, y + h), radius=h // 2, fill=hx(bg))
    d.text((x + 14, y + 8), label, font=F["eyebrow"], fill=hx(fg))
    return w


def rule(im: Image.Image, y: int, color: str = BORDER) -> None:
    ImageDraw.Draw(im).line((74, y, W - 74, y), fill=hx(color), width=2)


def short_url(url: str, max_chars: int = 54) -> str:
    """Keep source-slide labels readable; full links remain in the companion MD."""
    value = url.removeprefix("https://").removeprefix("http://").removeprefix("www.").rstrip("/")
    return value if len(value) <= max_chars else value[: max_chars - 1] + "…"


def footer(im: Image.Image, page: int, timestamp: str, source: str = "") -> None:
    d = ImageDraw.Draw(im)
    rule(im, H - 63, "#CEDADE")
    d.text((76, H - 45), "公开在线案例研究｜Accio / 非 Accio 视觉复刻参考｜v3", font=F["body_tiny"], fill=hx(SLATE))
    if source:
        textblock(im, (490, H - 45), source, F["body_tiny"], SLATE, 1180, gap=0, max_lines=1)
    n = f"{page:02d}"
    tw, _ = measure(d, n, F["body_tiny"])
    d.text((W - 78 - tw, H - 45), n, font=F["body_tiny"], fill=hx(SLATE))


def page_header(im: Image.Image, page: int, title: str, subtitle: str, tag: str = "ONLINE CASEBOOK") -> None:
    d = ImageDraw.Draw(im)
    pill(im, 76, 55, tag, "#E5EFF2", "#256270", h=35)
    d.text((76, 114), title, font=F["title"], fill=hx(INK))
    textblock(im, (80, 180), subtitle, F["subtitle"], SLATE, 1550, gap=8, max_lines=2)


def label_number(im: Image.Image, x: int, y: int, n: int, color: str, dark: bool = False) -> None:
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((x, y, x + 56, y + 56), radius=18, fill=hx(color))
    s = f"{n:02d}"
    tw, th = measure(d, s, F["eyebrow"])
    d.text((x + 28 - tw / 2, y + 28 - th / 2 - 2), s, font=F["eyebrow"],
           fill=hx(WHITE if dark else INK))


def case_page(case: dict, page: int, timestamp: str) -> Image.Image:
    im = new_bg("#F7F8F8", case["tint"])
    d = ImageDraw.Draw(im)
    pill(im, 76, 55, f"公开在线案例  /  {case['brand'].upper()}", case["tint"], INK, h=35)
    d.text((76, 112), case["cn"], font=F["title"], fill=hx(INK))
    d.text((80, 178), case["category"], font=F["subtitle"], fill=hx(SLATE))
    src = Image.open(ASSETS / case["asset"]).convert("RGB")
    # A large, explicitly attributed research excerpt.
    panel(im, (76, 255, 1040, 906), fill=WHITE, outline="#E4E8EA", radius=28)
    paste_cover(im, src, (100, 279, 1016, 795), radius=20)
    pill(im, 103, 817, "公开图像摘录 / 研究引用", "#F0F3F3", "#52626A", h=31)
    d.text((103, 859), case["visual_source"], font=F["body_tiny"], fill=hx(SLATE))

    # right hierarchy card
    panel(im, (1080, 255, 1844, 906), fill=case["color"], radius=30, shadow=False)
    pill(im, 1120, 294, "核心拆解", "#FFFFFF", case["color"], h=34)
    textblock(im, (1120, 357), case["takeaway"], F["title_small"], case["ink"], 646, gap=10, max_lines=3)
    y = 525
    for idx, (head, body) in enumerate(case["observations"], 1):
        label_number(im, 1120, y, idx, "#FFFFFF", dark=False)
        d.text((1200, y + 2), head, font=F["medium"], fill=hx(case["ink"]))
        textblock(im, (1200, y + 37), body, F["body_small"], case["ink"], 555, gap=6, max_lines=2)
        y += 116
    # bottom takeaway band
    panel(im, (76, 928, 1844, 997), fill="#F0F5F5", radius=18, shadow=False)
    pill(im, 101, 946, "可迁移，不可照抄", case["color"], case["ink"], h=32)
    d.text((372, 950), case["apply"], font=F["body_small"], fill=hx(INK))
    footer(im, page, timestamp, f"视觉图源：{case['visual_url']}｜分析：{case['analysis_url']}")
    return im


def page_cover(timestamp: str) -> Image.Image:
    im = Image.new("RGB", (W, H), hx("#111B2B"))
    # A 3×2 matrix made from the actual online research excerpts.
    locations = [
        (1080, 0, 1500, 360), (1500, 0, 1920, 360), (1080, 360, 1500, 720),
        (1500, 360, 1920, 720), (1080, 720, 1500, 1080), (1500, 720, 1920, 1080),
    ]
    for case, box in zip(CASE_DATA, locations):
        paste_cover(im, Image.open(ASSETS / case["asset"]), box, radius=0, shade=25)
    overlay = Image.new("RGBA", im.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    od.rectangle((0, 0, 1080, H), fill=(15, 29, 45, 245))
    od.rectangle((1035, 0, 1080, H), fill=(15, 29, 45, 110))
    im = Image.alpha_composite(im.convert("RGBA"), overlay).convert("RGB")
    d = ImageDraw.Draw(im)
    pill(im, 82, 84, "NO MORE FAKE CASES", "#F6D84A", INK, h=40)
    d.text((82, 182), "好看的案例，", font=F["hero"], fill=hx(WHITE))
    d.text((82, 272), "先来自真的产品。", font=F["hero"], fill=hx("#F6D84A"))
    textblock(im, (87, 410), "6 个公开在线电商案例的视觉拆解\n用真实页面、真实产品、真实选择逻辑回答：\n什么值得借鉴，什么绝不能照抄。", F["body"], "#C9D7DF", 800, gap=12)
    d.text((87, 655), "MAGIC SPOON · DE LA CALLE · GRAZA", font=F["eyebrow"], fill=hx("#B9CCD7"))
    d.text((87, 689), "VACATION · FENTY BEAUTY · STANLEY", font=F["eyebrow"], fill=hx("#B9CCD7"))
    panel(im, (82, 803, 910, 915), fill="#1B344A", outline="#33566C", radius=22, shadow=False)
    d.text((111, 826), "不是“换背景”教程", font=F["medium"], fill=hx(WHITE))
    d.text((111, 868), "而是：定位 → 资产角色 → 首屏 → PDP → 购买决策。", font=F["body_small"], fill=hx("#C0D4DE"))
    d.text((82, 982), f"生成时间（Asia/Shanghai）：{timestamp}", font=F["body_tiny"], fill=hx("#9AB1BE"))
    return im


def page_boundaries(page: int, timestamp: str) -> Image.Image:
    im = new_bg("#F7F8F8", "#B8E2DF")
    page_header(im, page, "先把证据和边界说清楚", "这本不是品牌授权画册，也不是 Accio 实机界面；它是带来源链接的案例研究与视觉任务拆解。")
    cards = [
        ("01", "真图源", "六张视觉摘录来自公开网页 / 新闻图 / 官方营销图。每页标出图源和分析源。", "#47CFC4"),
        ("02", "真案例", "品牌与页面模式来自公开案例文章或官方页面，不把第三方评价写成品牌保证。", "#FF8B5A"),
        ("03", "真拆解", "每页回答：谁被吸引、靠什么看懂、下一步怎么选、还缺什么证据。", "#F3C951"),
        ("04", "不做的事", "不复制商标、文案、摄影、专有页面；不声称这些是 Accio 输出或官方背书。", "#7A77E8"),
    ]
    for i, (no, title, body, accent) in enumerate(cards):
        x = 76 + (i % 2) * 886
        y = 290 + (i // 2) * 276
        panel(im, (x, y, x + 840, y + 228), fill=WHITE, outline=BORDER)
        pill(im, x + 28, y + 27, no, accent, INK, h=34)
        d = ImageDraw.Draw(im)
        d.text((x + 28, y + 85), title, font=F["medium"], fill=hx(INK))
        textblock(im, (x + 28, y + 125), body, F["body_small"], SLATE, 770, gap=7, max_lines=3)
    panel(im, (76, 867, 1844, 954), fill="#102033", radius=23, shadow=False)
    d = ImageDraw.Draw(im)
    d.text((108, 891), "使用准则：提炼“结构 / 角色 / 决策顺序”，不复制“品牌外观 / 商标 / 原始视觉资产”。", font=F["medium"], fill=hx(WHITE))
    footer(im, page, timestamp, "详细来源、图像使用边界见第 15 页与 SOURCES_AND_USAGE_BOUNDARIES.md")
    return im


def page_gallery(page: int, timestamp: str) -> Image.Image:
    im = new_bg("#F7F8F8", "#F2D557")
    page_header(im, page, "六个案例，不是六种“好看”", "把它们放到同一张图里，先看各自解决哪种购买阻力：记忆、身份、用途、氛围、变体或规格。")
    d = ImageDraw.Draw(im)
    card_w, card_h = 540, 292
    for idx, case in enumerate(CASE_DATA):
        col, row = idx % 3, idx // 3
        x, y = 76 + col * 588, 285 + row * 332
        panel(im, (x, y, x + card_w, y + card_h), fill=WHITE, outline=BORDER, radius=25)
        paste_cover(im, Image.open(ASSETS / case["asset"]), (x + 15, y + 15, x + 190, y + card_h - 15), radius=16)
        pill(im, x + 212, y + 28, f"{idx + 1:02d}", case["tint"], INK, h=29)
        d.text((x + 212, y + 75), case["brand"], font=F["medium"], fill=hx(INK))
        textblock(im, (x + 212, y + 116), case["category"], F["body_tiny"], SLATE, 295, gap=5, max_lines=2)
        d.line((x + 212, y + 181, x + 505, y + 181), fill=hx(BORDER), width=2)
        textblock(im, (x + 212, y + 201), case["takeaway"], F["body_tiny"], INK, 292, gap=5, max_lines=3)
    footer(im, page, timestamp, "每张图为低分辨率研究摘录；逐页来源链接见第 4—9 页")
    return im


def page_matrix(page: int, timestamp: str) -> Image.Image:
    im = new_bg("#F7F8F8", "#BFC4FF")
    page_header(im, page, "真正可复用的是“视觉角色表”，不是某个配色", "六个案例表面差异很大，但都在第一屏和详情页中让一个具体问题得到回答。")
    cols = ["要先解决的\n购买问题", "首屏视觉角色", "PDP 关键模块", "不该照搬的东西"]
    rows = [
        ("Magic Spoon", "选择太多", "包装 + 色彩 + 口味", "组合筛选 + UGC", "紫色、卡通、原文案"),
        ("De La Calle", "这是谁的品牌", "人物动作 + 一句话", "属性图形 + 购买入口", "特定文化符号与拍摄"),
        ("Graza", "我该买哪一瓶", "用餐情境 + 用途命名", "用途对比 + 套装", "产品名 / 专有插画"),
        ("Vacation", "为什么要相信这个氛围", "摄影规则 + 有限色板", "规格 + 质感 + 用法", "复古元素的逐像素复制"),
        ("Fenty", "哪个变体适合我", "色彩 / 质地近景", "试色 + 使用 + 成分", "色号体系、营销主张"),
        ("Stanley", "这个颜色 / 规格是什么", "准确商品图", "变体 + 价格 + CTA", "商标、畅销 / 爆款暗示"),
    ]
    x0, y0 = 76, 285
    widths = [280, 340, 420, 610]
    heights = 82
    x = x0
    for col, width in zip(cols, widths):
        panel(im, (x, y0, x + width, y0 + 70), fill="#102033", radius=14, shadow=False)
        textblock(im, (x + 18, y0 + 16), col, F["eyebrow"], WHITE, width - 32, gap=3, max_lines=2)
        x += width + 12
    for r, row in enumerate(rows):
        x = x0
        y = y0 + 84 + r * heights
        bg = "#FFFFFF" if r % 2 == 0 else "#F1F6F7"
        for cell, width in zip(row, widths):
            panel(im, (x, y, x + width, y + 70), fill=bg, outline="#E0E7E9", radius=13, shadow=False)
            textblock(im, (x + 18, y + 16), cell, F["body_tiny"], INK if x == x0 else SLATE, width - 30, gap=3, max_lines=2)
            x += width + 12
    panel(im, (76, 902, 1844, 972), fill="#FFF7D5", radius=18, shadow=False)
    d = ImageDraw.Draw(im)
    d.text((104, 924), "判断是否“可借鉴”的问题：它有没有替顾客减少一个猜测？如果没有，可能只是漂亮，不是商品视觉。", font=F["medium_small"], fill=hx(INK))
    footer(im, page, timestamp, "表中为本报告的分析归纳；不是各品牌的官方策略表述")
    return im


def page_product_intro(page: int, timestamp: str) -> Image.Image:
    im = new_bg("#FCFBF8", "#FFCC9E")
    page_header(im, page, "先拆产品，才有资格谈“做图”", "这也是上一版缺掉的步骤：没有产品介绍、真实规格和 SKU 关系，视觉只能变成空洞换背景。")
    d = ImageDraw.Draw(im)
    questions = [
        ("01", "这是什么？", "一句话品类 + 一个可验证的核心构造 / 功能。", "#E6462F"),
        ("02", "给谁、在什么时候用？", "明确的购买者、使用者、场景、频率和替代方案。", "#E88B3B"),
        ("03", "不同 SKU 到底差什么？", "颜色、香型、尺寸、容量、材料、套装与兼容性。", "#4FCFC6"),
        ("04", "哪些话能说？", "来源、认证、性能、成分、交期、售后——缺证据的先留空。", "#7C78E9"),
        ("05", "用户下单前还会问什么？", "尺度、手感、使用步骤、包装、配送、退换、适配风险。", "#BECC25"),
    ]
    for i, (n, title, body, color) in enumerate(questions):
        y = 285 + i * 120
        panel(im, (76, y, 1844, y + 96), fill=WHITE, outline=BORDER, radius=20)
        pill(im, 101, y + 30, n, color, INK, h=34)
        d.text((205, y + 24), title, font=F["medium"], fill=hx(INK))
        textblock(im, (520, y + 29), body, F["body_small"], SLATE, 1220, gap=5, max_lines=2)
    panel(im, (76, 922, 1844, 990), fill="#102033", radius=19, shadow=False)
    d.text((105, 944), "输出物不是一句“帮我做一张好看的主图”，而是一张可核对的「商品事实表 + 素材缺口表 + 页面决策表」。", font=F["medium_small"], fill=hx(WHITE))
    footer(im, page, timestamp, "这页是可直接复用的产品介绍 / 视觉策略起点")
    return im


def page_asset_roles(page: int, timestamp: str) -> Image.Image:
    im = new_bg("#F8F9F8", "#B2E7E2")
    page_header(im, page, "一套图不是多张“主图”，而是六种不同的决策证据", "把案例的视觉做法翻译成一个可以交给摄影、设计或 AI 工作流执行的资产角色表。")
    d = ImageDraw.Draw(im)
    cells = [
        ("01", "识别图", "白底 / 干净背景\n让人一眼认出款式与颜色", "Stanley", "#55D0C8"),
        ("02", "氛围图", "人物 / 场景 / 情绪\n让人想进入这个世界", "De La Calle", "#EF553E"),
        ("03", "用途图", "产品正在解决任务\n把“为什么买”拍出来", "Graza", "#C7DC21"),
        ("04", "质地图", "近景、材料、印花、成分\n让感受可被相信", "Fenty", "#8E5963"),
        ("05", "变体图", "颜色 / 尺寸 / 套装差异\n让选择不用猜", "Magic Spoon", "#7A31E8"),
        ("06", "信任图", "尺寸参照、流程、评价、物流\n消除最后一厘米", "PDP 通用", "#F2AA3E"),
    ]
    for i, (no, title, body, ref, color) in enumerate(cells):
        col, row = i % 3, i // 3
        x, y = 76 + col * 592, 300 + row * 294
        panel(im, (x, y, x + 548, y + 245), fill=WHITE, outline=BORDER, radius=25)
        d.rounded_rectangle((x + 24, y + 24, x + 134, y + 134), radius=20, fill=hx(color))
        d.text((x + 47, y + 42), no, font=F["number"], fill=hx(INK if color != "#7A31E8" else WHITE))
        d.text((x + 165, y + 34), title, font=F["medium"], fill=hx(INK))
        textblock(im, (x + 165, y + 81), body, F["body_small"], SLATE, 330, gap=6, max_lines=3)
        pill(im, x + 165, y + 180, f"参考：{ref}", "#EEF3F4", "#47636D", h=30)
    footer(im, page, timestamp, "同一张“漂亮正面图”不能同时承担这六个任务")
    return im


def page_pdp(page: int, timestamp: str) -> Image.Image:
    im = new_bg("#F8F9FA", "#C7C6FA")
    page_header(im, page, "PDP 首屏要让眼睛走一条不绕路的线", "Stanley 的“图像 → 变体 → 价格 → 按钮”是最直接的结构；其他案例只是给这条线加入各自的品牌语气。")
    d = ImageDraw.Draw(im)
    # Original wireframe—intentionally neither a live product screen nor a brand clone.
    panel(im, (76, 294, 1844, 852), fill="#FFFFFF", outline=BORDER, radius=28)
    d.rounded_rectangle((112, 334, 912, 778), radius=20, fill=hx("#EAF4FF"))
    d.ellipse((361, 407, 651, 697), fill=hx("#86C5F2"))
    d.rounded_rectangle((470, 384, 610, 718), radius=48, fill=hx("#2C6FA1"))
    d.rectangle((470, 427, 610, 451), fill=hx("#D8E8EF"))
    d.rounded_rectangle((456, 350, 624, 410), radius=20, fill=hx("#C9E7F6"))
    d.text((148, 800), "原创结构示意，不是任何品牌 / Accio 界面截图", font=F["body_tiny"], fill=hx(SLATE))
    d.text((1002, 340), "产品名 / 一句价值主张", font=F["medium"], fill=hx(INK))
    d.text((1002, 387), "¥  / 评分 / 发货与退换", font=F["body_small"], fill=hx(SLATE))
    d.line((1002, 440, 1746, 440), fill=hx(BORDER), width=2)
    d.text((1002, 470), "颜色 / 香型 / 容量", font=F["medium_small"], fill=hx(INK))
    for i, c in enumerate(["#276FA1", "#A7D7C8", "#F2BD68", "#D66A68"]):
        d.ellipse((1002 + i * 66, 514, 1048 + i * 66, 560), fill=hx(c), outline=hx("#102033") if i == 0 else None, width=3)
    d.text((1002, 593), "关键承诺（3 条以内）", font=F["medium_small"], fill=hx(INK))
    for i in range(3):
        d.rounded_rectangle((1002, 630 + i * 35, 1720, 653 + i * 35), radius=9, fill=hx("#EDF3F5"))
    d.rounded_rectangle((1002, 755, 1515, 812), radius=17, fill=hx("#E84E36"))
    d.text((1197, 772), "加入购物车 / 获取报价", font=F["medium_small"], fill=hx(WHITE))
    arrows = [
        ("① 看清商品", 235, 892), ("② 选变体", 681, 892), ("③ 看价格与承诺", 1124, 892), ("④ 行动", 1582, 892),
    ]
    for label, x, y in arrows:
        d.ellipse((x - 24, y - 24, x + 24, y + 24), fill=hx("#DDE8EB"))
        tw, _ = measure(d, label, F["medium_small"])
        d.text((x - tw / 2, y + 38), label, font=F["medium_small"], fill=hx(INK))
    footer(im, page, timestamp, "结构参考：Stanley PDP 的第三方案例描述；画面为原创教学示意")
    return im


def page_brief(page: int, timestamp: str) -> Image.Image:
    im = new_bg("#102033", "#2C8A88")
    d = ImageDraw.Draw(im)
    pill(im, 76, 55, "HANDOFF / 可执行任务书", "#F0D548", INK, h=36)
    d.text((76, 118), "给 AI、摄影或设计师的任务，不能只写“优化一下”。", font=F["title"], fill=hx(WHITE))
    textblock(im, (80, 186), "把案例的好看变成可验证的交付条件：先给事实，再指定资产角色、视觉方向、禁区和验收口。", F["subtitle"], "#BFD4DD", 1570, gap=8)
    panel(im, (76, 290, 1160, 869), fill="#19394D", outline="#356176", radius=30, shadow=False)
    task = (
        "任务：基于已上传的【SKU / 产品名】真实素材，生成“仅草稿”的视觉方案。\n\n"
        "已确认事实：材质【 】；尺寸 / 容量【 】；颜色 / 变体【 】；\n"
        "不可改写：认证【 】；性能【 】；交期【 】；售后【 】。\n\n"
        "需要的资产：\n"
        "- 1 张识别图：真实形态、真实变体；\n"
        "- 1 张场景图：明确的【使用者 / 时刻 / 动作】；\n"
        "- 2 张细节图：分别证明【构造】和【材料 / 使用】；\n"
        "- 1 张选择图：用【颜色 / 尺寸 / 套装】解释差异；\n"
        "- PDP 模块草稿：价值主张、规格、使用、FAQ、配送。\n\n"
        "输出前先列“素材缺口与风险”，不发送、不发布、不覆盖现有商品。"
    )
    textblock(im, (112, 327), task, F["body"], "#EAF2F5", 1012, gap=11, max_lines=17)
    panel(im, (1210, 290, 1844, 869), fill="#F8F3E9", radius=30, shadow=False)
    d.text((1250, 334), "验收口", font=F["title_small"], fill=hx(INK))
    gates = [
        ("真实性", "是否用真实 SKU、真实结构与真实规格？"),
        ("角色性", "每张图是否解决一个不同的购买问题？"),
        ("一致性", "包装、色板、字体、摄影是否服务同一定位？"),
        ("可买性", "变体、价格、交付、退换、CTA 是否清楚？"),
        ("边界", "所有待确认字段、所有发布动作是否保留给人？"),
    ]
    y = 421
    for idx, (head, body) in enumerate(gates, 1):
        d.ellipse((1253, y, 1285, y + 32), fill=hx(["#E84932", "#48CFC4", "#F2C64E", "#7C78E9", "#9ACA3C"][idx - 1]))
        d.text((1310, y - 2), head, font=F["medium_small"], fill=hx(INK))
        textblock(im, (1310, y + 29), body, F["body_tiny"], SLATE, 470, gap=3, max_lines=2)
        y += 86
    footer(im, page, timestamp, "页面为原创任务书；不假定 Accio 的具体 UI、权限或自动发布行为")
    return im


def page_workflow(page: int, timestamp: str) -> Image.Image:
    im = new_bg("#F7F8F8", "#CDEEF0")
    page_header(im, page, "Accio / 不用 Accio：核心不是工具，而是人审前的素材与判断", "公开文档可支持 Agent、连接器 / 插件、素材 ZIP 等高层流程；任何当前账号权限、按钮和发布动作都必须在实际环境验证。")
    d = ImageDraw.Draw(im)
    steps = [
        ("A", "收集", "真实 SKU、包装、实拍、规格、渠道规则、禁用词", "#50CBC3"),
        ("B", "拆解", "产品介绍表 → 用户 / 场景 → SKU 关系 → 素材缺口", "#F38B59"),
        ("C", "创作草稿", "按资产角色生成 / 拍摄 / 编排；不得补造规格", "#F3C852"),
        ("D", "人审", "事实、品牌、合规、图片真实性、平台规则、交付语境", "#7C78E9"),
        ("E", "小范围验证", "仅在确认后测试首屏、素材组、文案与变体路径", "#A9C73A"),
    ]
    x = 76
    for idx, (letter, title, body, color) in enumerate(steps):
        w = 320 if idx < 4 else 380
        panel(im, (x, 335, x + w, 687), fill=WHITE, outline=BORDER, radius=28)
        d.rounded_rectangle((x + 28, 363, x + 92, 427), radius=20, fill=hx(color))
        d.text((x + 49, 374), letter, font=F["medium"], fill=hx(INK))
        d.text((x + 30, 464), title, font=F["medium"], fill=hx(INK))
        textblock(im, (x + 30, 513), body, F["body_small"], SLATE, w - 60, gap=7, max_lines=4)
        if idx < 4:
            d.polygon([(x + w + 8, 490), (x + w + 30, 505), (x + w + 8, 520)], fill=hx("#97AAB1"))
        x += w + 45
    panel(im, (76, 750, 1844, 915), fill="#FFF7DC", radius=25, shadow=False)
    d.text((108, 783), "关键控制语句", font=F["medium"], fill=hx(INK))
    quote = "“先输出素材清单、缺失字段、草稿预览和每个 SKU 的交付项；未经我确认，不发送、不发布、不覆盖现有商品。”"
    textblock(im, (108, 830), quote, F["body"], "#5A4B24", 1580, gap=8, max_lines=2)
    footer(im, page, timestamp, "官方文档入口：Accio Work Quickstart / 插件文档；具体 UI 与权限须实机验证")
    return im


def page_sources(page: int, timestamp: str) -> Image.Image:
    im = new_bg("#F9F9F7", "#F1D0C6")
    page_header(im, page, "来源索引与使用边界", "所有案例都有“视觉图源”和“分析图源”。AI 示范的提示词、工件与边界在随附文件中记录；这份文件只保留低清研究摘录。")
    d = ImageDraw.Draw(im)
    y = 279
    for i, case in enumerate(CASE_DATA, 1):
        panel(im, (76, y, 1844, y + 104), fill=WHITE, outline=BORDER, radius=18, shadow=False)
        pill(im, 100, y + 32, f"{i:02d}", case["color"], case["ink"], h=34)
        d.text((170, y + 22), case["brand"], font=F["medium_small"], fill=hx(INK))
        d.text((430, y + 22), case["visual_source"], font=F["body_tiny"], fill=hx(SLATE))
        d.text((430, y + 51), short_url(case["visual_url"]), font=F["body_tiny"], fill=hx("#2A7183"))
        d.text((1130, y + 22), case["analysis_source"], font=F["body_tiny"], fill=hx(SLATE))
        d.text((1130, y + 51), short_url(case["analysis_url"]), font=F["body_tiny"], fill=hx("#2A7183"))
        y += 116
    panel(im, (76, 972, 1844, 1028), fill="#102033", radius=16, shadow=False)
    d.text((104, 989), "图像 / 商标 / 截图权利归相应权利人；仅作研究、评论和来源定位。AI 的 S0 为原创虚构概念图、非 Accio；不能将任何素材直接用于商业店铺。", font=F["body_tiny"], fill=hx("#D6E4EA"))
    footer(im, page, timestamp, "完整说明：SOURCES_AND_USAGE_BOUNDARIES.md")
    return im


def page_close(page: int, timestamp: str) -> Image.Image:
    im = Image.new("RGB", (W, H), hx("#101E2E"))
    # Reuse only the source thumbnails as an ending wall; overlay remains clearly a research deck.
    for idx, case in enumerate(CASE_DATA):
        x = 1100 + (idx % 2) * 400
        y = 80 + (idx // 2) * 315
        paste_cover(im, Image.open(ASSETS / case["asset"]), (x, y, x + 340, y + 260), radius=20, shade=35)
    d = ImageDraw.Draw(im)
    pill(im, 78, 78, "NEXT STEP", "#F0D548", INK, h=38)
    d.text((78, 182), "不是复制一个品牌，", font=F["hero"], fill=hx(WHITE))
    d.text((78, 274), "而是复制一条清晰的购买路径。", font=F["title"], fill=hx("#F0D548"))
    textblock(im, (83, 382), "选定一个案例方向后，回到你的真实产品：\n1. 完成商品事实表；2. 排出六类视觉资产；\n3. 生成草稿；4. 用人审与小范围测试决定是否上线。", F["body"], "#C6D6DE", 860, gap=13)
    panel(im, (78, 632, 920, 777), fill="#1B3C50", outline="#36657A", radius=24, shadow=False)
    d.text((112, 663), "本册产出", font=F["medium"], fill=hx(WHITE))
    d.text((112, 708), "6 个可追溯案例 + 资产角色表 + PDP 骨架 + 人审任务书", font=F["body_small"], fill=hx("#C9DAE2"))
    d.text((78, 981), f"生成时间（Asia/Shanghai）：{timestamp}", font=F["body_tiny"], fill=hx("#8FACB9"))
    return im



def demo_asset() -> Image.Image:
    """Load the actual image-generator output used only as the visible S0 draft."""
    return Image.open(ASSETS / AI_DEMO_ASSET).convert("RGB")


def draw_manual_rebuild(im: Image.Image, box: tuple[int, int, int, int], label: bool = True) -> None:
    """Draw a deliberately distinct, original S1 product layout.

    This is a manual graphic reconstruction in the renderer—not a model output,
    a product photograph, or a verified product design.
    """
    x1, y1, x2, y2 = box
    w, h = x2 - x1, y2 - y1
    d = ImageDraw.Draw(im)
    # Original, abstracted art direction: a closed-cap bottle rather than the
    # reference / S0 handled straw tumbler silhouette.
    d.rounded_rectangle((x1, y1, x2, y2), radius=26, fill=hx("#F46F59"))
    d.ellipse((x1 + int(.08*w), y1 + int(.68*h), x2 - int(.06*w), y2 + int(.94*h)), fill=hx("#9CD9C9"))
    d.ellipse((x1 + int(.12*w), y1 + int(.06*h), x1 + int(.42*w), y1 + int(.36*h)), fill=hx("#FFCE57"))
    d.rounded_rectangle((x1 + int(.59*w), y1 + int(.15*h), x1 + int(.83*w), y1 + int(.80*h)), radius=int(.10*w), fill=hx("#143C76"))
    # Cap and asymmetric shoulders establish a different object geometry.
    d.rounded_rectangle((x1 + int(.61*w), y1 + int(.09*h), x1 + int(.81*w), y1 + int(.20*h)), radius=int(.03*w), fill=hx("#0E2A58"))
    d.rounded_rectangle((x1 + int(.64*w), y1 + int(.05*h), x1 + int(.78*w), y1 + int(.12*h)), radius=int(.025*w), fill=hx("#0A2043"))
    d.polygon([(x1 + int(.59*w), y1 + int(.22*h)), (x1 + int(.83*w), y1 + int(.22*h)),
               (x1 + int(.80*w), y1 + int(.31*h)), (x1 + int(.62*w), y1 + int(.31*h))], fill=hx("#174A8B"))
    # A diagonal silicone band, no handle and no straw.
    d.polygon([(x1 + int(.58*w), y1 + int(.48*h)), (x1 + int(.83*w), y1 + int(.40*h)),
               (x1 + int(.83*w), y1 + int(.51*h)), (x1 + int(.58*w), y1 + int(.59*h))], fill=hx("#79CAB8"))
    # Short horizontal grip marks keep the product geometry distinct from a handle.
    for offset in (0.36, 0.43, 0.50):
        d.rounded_rectangle((x1 + int(.65*w), y1 + int(offset*h), x1 + int(.77*w), y1 + int((offset + .028)*h)), radius=max(3, int(.012*w)), fill=hx("#2B64AD"))
    # Soft light / shadow signals depth but keeps it clearly an illustration.
    d.ellipse((x1 + int(.54*w), y1 + int(.73*h), x1 + int(.89*w), y1 + int(.86*h)), fill=hx("#2A4C60"))
    d.ellipse((x1 + int(.56*w), y1 + int(.70*h), x1 + int(.87*w), y1 + int(.82*h)), fill=hx("#7ED2C0"))
    if label:
        d.rounded_rectangle((x1 + 18, y1 + 18, x1 + 235, y1 + 50), radius=15, fill=hx("#102033"))
        d.text((x1 + 33, y1 + 26), "S1 / 人工重建草图", font=F["eyebrow"], fill=hx(WHITE))


def status_pill(im: Image.Image, x: int, y: int, label: str, state: str) -> int:
    palette = {
        "阻断": ("#FFE0DB", "#A62C1C"),
        "通过": ("#D8F2E7", "#146B4F"),
        "草稿": ("#E9E5FF", "#493DA4"),
        "非 Accio": ("#FFF2BE", "#805600"),
    }
    bg, fg = palette[state]
    return pill(im, x, y, label, bg, fg, h=31)


def page_ai_trace_intro(page: int, timestamp: str) -> Image.Image:
    im = new_bg("#F8F7F3", "#FFD4C6")
    page_header(
        im, page, "从提示词开始的 AI 辅助复刻：把过程做成可审计证据",
        "这一段补上“AI 实际做了什么、哪里必须人审”的可见链路。S0 是本工作区实际生成的原始 AI 图像；没有运行或声称运行 Accio。",
        tag="AI TRACE / TRANSPARENT TEMPLATE",
    )
    d = ImageDraw.Draw(im)
    # Source excerpt
    panel(im, (76, 282, 520, 770), fill=WHITE, outline=BORDER, radius=26)
    paste_cover(im, Image.open(ASSETS / "stanley_variants.jpg"), (102, 309, 494, 548), radius=18)
    pill(im, 105, 571, "公开来源图摘录 / 只作研究", "#F1F3F2", "#52626A", h=30)
    d.text((106, 623), "我们只抽取的视觉规则", font=F["medium_small"], fill=hx(INK))
    source_rules = ["单个商品主体要一眼清楚", "变体 / 颜色不应离商品太远", "颜色、价格、CTA 应有单一阅读路径"]
    yy = 660
    for r in source_rules:
        d.ellipse((110, yy + 8, 120, yy + 18), fill=hx("#2B7D84"))
        d.text((134, yy), r, font=F["body_tiny"], fill=hx(SLATE))
        yy += 32
    # Conversion boundary
    panel(im, (558, 282, 1009, 770), fill="#102033", radius=26, shadow=False)
    pill(im, 588, 312, "不等于复制品牌", "#F0D548", INK, h=30)
    d.text((588, 369), "抽取规则，不继承身份", font=F["title_small"], fill=hx(WHITE))
    textblock(im, (590, 429), "参考图中的品牌、产品结构、图像、Logo、营销用语都不进入生成输入。\n\n只把可迁移的“信息层级”翻译成一个原创、虚构商品的草稿任务。", F["body"], "#C9DCE3", 370, gap=12, max_lines=7)
    rule_y = 657
    d.line((589, rule_y, 972, rule_y), fill=hx("#3D6374"), width=2)
    d.text((590, 684), "边界：示范资产 ≠ 可上架商品。", font=F["body_small"], fill=hx("#F0D548"))
    # Actual S0 asset
    panel(im, (1047, 282, 1844, 770), fill=WHITE, outline=BORDER, radius=26)
    paste_cover(im, demo_asset(), (1074, 309, 1478, 704), radius=18)
    d.text((1510, 328), "S0 / AI 图像草稿", font=F["medium"], fill=hx(INK))
    status_pill(im, 1510, 373, "Arena 图像模型", "非 Accio")
    textblock(im, (1510, 430), "来自下一页记录的真实提示词。它只是一张虚构品类的概念图：\n\n• 无真实 SKU\n• 无验证性能\n• 无发布权限\n• 必须经过人工审查与重建", F["body_small"], SLATE, 284, gap=9, max_lines=9)
    # Trace timeline
    steps = [("I", "来源 / 事实表"), ("P", "提示词 v1"), ("S0", "AI 草稿"), ("R", "人工审核"), ("S1", "人工重建"), ("A", "批准 / 发布")]
    x = 97
    for idx, (letter, title) in enumerate(steps):
        is_last = idx == len(steps) - 1
        color = "#F46F59" if idx < 3 else ("#2B7D84" if idx < 5 else "#C9D2D6")
        d.ellipse((x, 836, x + 68, 904), fill=hx(color))
        tw, th = measure(d, letter, F["medium_small"])
        d.text((x + 34 - tw/2, 858 - th/2), letter, font=F["medium_small"], fill=hx(INK if idx != 4 else WHITE))
        d.text((x - 15, 920), title, font=F["body_tiny"], fill=hx(INK))
        if not is_last:
            d.line((x + 76, 870, x + 226, 870), fill=hx("#8FA5AD"), width=3)
            d.polygon([(x + 226, 870), (x + 213, 861), (x + 213, 879)], fill=hx("#8FA5AD"))
        x += 298
    panel(im, (76, 979, 1844, 1028), fill="#FFF1BE", radius=16, shadow=False)
    d.text((102, 993), "透明声明：这里记录的是“可复制的工作证据链”；最终“批准 / 发布”在本示范中故意保留为灰色，因为没有真实商品事实或 Accio 实机验证。", font=F["body_tiny"], fill=hx("#5E4911"))
    footer(im, page, timestamp, "来源图：Stanley Quencher（AL.com 公开产品图）；AI 草稿与提示词记录：本工作区，非 Accio")
    return im


def page_ai_trace_prompt(page: int, timestamp: str) -> Image.Image:
    im = new_bg("#102033", "#1E7180")
    d = ImageDraw.Draw(im)
    pill(im, 76, 55, "TRACE 01 / PROMPT", "#F0D548", INK, h=35)
    d.text((76, 114), "输入不能只有“做一张好看的图”。", font=F["title"], fill=hx(WHITE))
    textblock(im, (80, 183), "一条可审计的提示词至少要同时声明：事实来源、可迁移规则、禁止复制项、输出限制与待人审字段。", F["subtitle"], "#C5D8DF", 1500, gap=8)
    # Left: fact / boundary stack
    panel(im, (76, 294, 620, 904), fill="#17394B", outline="#356176", radius=28, shadow=False)
    d.text((112, 336), "冻结输入（示范）", font=F["title_small"], fill=hx(WHITE))
    y = 409
    for head, body in AI_DEMO_FACTS:
        d.text((114, y), head, font=F["medium_small"], fill=hx("#F0D548"))
        y = textblock(im, (114, y + 31), body, F["body_small"], "#D8E8ED", 455, gap=5, max_lines=3) + 20
    # Center: actual prompt excerpt
    panel(im, (657, 294, 1844, 784), fill="#F6F1E8", radius=28, shadow=False)
    pill(im, 693, 327, "实际调用的 S0 提示词（完整文本见随附 .txt）", "#E6D8FF", "#4C3C93", h=31)
    prompt_excerpt = (
        "A polished 4 by 5 ecommerce concept visual for an entirely fictional, unbranded product.\n"
        "Product: Tide Cup Demo 01; a cobalt-blue tumbler, centered and clearly silhouetted.\n"
        "Abstract coral backdrop; seafoam circular shadow; simple geometric color swatches.\n\n"
        "Absolutely no text, lettering, logos, trademarks, labels, or resemblance to an existing brand / product.\n"
        "A fictional concept for a transparent AI-assisted workflow demonstration — not a real commercial item."
    )
    textblock(im, (696, 389), prompt_excerpt, F["body_small"], INK, 1088, gap=12, max_lines=10)
    # Output contract
    panel(im, (657, 813, 1844, 904), fill="#EAF4F1", radius=22, shadow=False)
    d.text((693, 835), "输出契约", font=F["medium_small"], fill=hx("#1A665A"))
    d.text((850, 835), "只产生“无文字、无 Logo 的概念主视觉”；不自动写规格、价格、CTA，也不决定“可发布”。", font=F["body_small"], fill=hx(INK))
    footer(im, page, timestamp, "可移植到 Accio / 其他工具的不是一句提示词，而是“输入字段 + 禁区 + 输出契约 + 人审门”。")
    return im


def page_ai_trace_draft(page: int, timestamp: str) -> Image.Image:
    im = new_bg("#F7F8F8", "#D2E9EF")
    page_header(im, page, "S0：让 AI 草稿与来源参照并排，而不是只展示“看起来不错的成品”", "AI 图像可用于发散方向；它不能自己证明结构原创、商品真实、权利清晰或可发布。这里故意把问题暴露出来。", tag="TRACE 02 / SOURCE ↔ S0")
    d = ImageDraw.Draw(im)
    # reference, S0 and issue column
    panel(im, (76, 284, 518, 838), fill=WHITE, outline=BORDER, radius=26)
    paste_cover(im, Image.open(ASSETS / "stanley_variants.jpg"), (103, 314, 491, 558), radius=18)
    pill(im, 105, 579, "来源参照", "#EAF0F1", "#4D676F", h=30)
    textblock(im, (107, 632), "只比对：\n• 单品清晰度\n• 变体邻近性\n• 视觉阅读顺序\n\n不比对：产品轮廓、颜色命名、品牌身份或页面 UI。", F["body_small"], SLATE, 360, gap=9, max_lines=9)
    panel(im, (551, 284, 1125, 838), fill=WHITE, outline=BORDER, radius=26)
    paste_cover(im, demo_asset(), (579, 314, 1097, 760), radius=18)
    pill(im, 580, 780, "S0 / 实际 AI 输出，尚未批准", "#FFE0DB", "#A62C1C", h=31)
    panel(im, (1158, 284, 1844, 838), fill="#102033", radius=26, shadow=False)
    d.text((1194, 325), "人审发现的风险", font=F["title_small"], fill=hx(WHITE))
    risks = [
        ("01", "轮廓风险", "带把手 + 吸管的强特征仍与参考品类过近；不能把“非复制”只交给模型。"),
        ("02", "商品风险", "它是虚构概念图，不能补写材质、容量、保温、认证、库存或价格。"),
        ("03", "素材风险", "看似真实的光影不等于真实 SKU 实拍；不得作为商品事实证据。"),
        ("04", "发布风险", "没有渠道规则、权利确认、责任人和批准记录；发布门必须关闭。"),
    ]
    y = 396
    for num, head, body in risks:
        d.ellipse((1195, y, 1231, y + 36), fill=hx("#F46F59"))
        d.text((1204, y + 7), num, font=F["eyebrow"], fill=hx(INK))
        d.text((1253, y - 2), head, font=F["medium_small"], fill=hx("#F5F9FA"))
        textblock(im, (1253, y + 28), body, F["body_tiny"], "#C1D4DC", 530, gap=5, max_lines=3)
        y += 104
    panel(im, (76, 875, 1844, 974), fill="#FFF1BE", radius=22, shadow=False)
    d.text((108, 898), "为什么这一页重要？", font=F["medium"], fill=hx(INK))
    textblock(im, (108, 936), "如果报告只放最终图，AI 的失败模式会被隐藏。把来源、提示词、S0 和风险并排，团队才能复现判断，而不是复刻表面。", F["body_small"], "#5E4911", 1600, gap=6, max_lines=2)
    footer(im, page, timestamp, "S0 为本工作区的 Arena 图像模型生成结果；不代表 Accio 输出，也不是商品实拍。")
    return im


def page_ai_trace_review(page: int, timestamp: str) -> Image.Image:
    im = new_bg("#F9F8F5", "#EFE1B2")
    page_header(im, page, "R：人工审核不是“改得更漂亮”，而是逐项决定什么可以留下、什么必须阻断", "审查记录要能回答：谁发现了什么？依据是什么？删改什么？下一版本允许做什么？这里的责任人是示范角色，不是对真实商品的批准。", tag="TRACE 03 / HUMAN REVIEW")
    d = ImageDraw.Draw(im)
    # table header
    panel(im, (76, 281, 1844, 802), fill=WHITE, outline=BORDER, radius=26)
    cols = [76, 177, 394, 862, 1392, 1570, 1718, 1844]
    headers = ["ID", "问题", "发现 / 依据", "改动指令", "所有者", "状态"]
    for x in cols[1:-1]:
        d.line((x, 330, x, 775), fill=hx("#E2E8EA"), width=1)
    d.rectangle((102, 308, 1818, 355), fill=hx("#102033"))
    header_x = [124, 197, 420, 888, 1418, 1594]
    for x, header in zip(header_x, headers):
        d.text((x, 322), header, font=F["eyebrow"], fill=hx(WHITE))
    y = 378
    for i, (rid, issue, found, change, owner, state) in enumerate(AI_REVIEW_LOG):
        if i:
            d.line((102, y - 12, 1818, y - 12), fill=hx("#E7ECEE"), width=1)
        d.text((124, y), rid, font=F["body_tiny"], fill=hx("#2E7582"))
        d.text((197, y), issue, font=F["body_tiny"], fill=hx(INK))
        textblock(im, (420, y), found, F["body_tiny"], SLATE, 415, gap=3, max_lines=3)
        textblock(im, (888, y), change, F["body_tiny"], SLATE, 472, gap=3, max_lines=3)
        d.text((1418, y), owner, font=F["body_tiny"], fill=hx(INK))
        status_pill(im, 1581, y - 6, state, state)
        y += 98
    # patched prompt
    panel(im, (76, 838, 1110, 982), fill="#102033", radius=25, shadow=False)
    d.text((110, 865), "提示词补丁 v2（人工批准后才允许重做）", font=F["medium_small"], fill=hx("#F0D548"))
    patched = "保留“单品清晰 + 色块对比 + 变体靠近”的结构；删除把手、吸管、任何品牌联想；改为封闭旋盖、斜向硅胶环的原创瓶形。绝不添加性能、材质、价格、CTA 或认证文字。输出仅为无字结构草图。"
    textblock(im, (110, 906), patched, F["body_small"], "#D5E3E7", 950, gap=6, max_lines=3)
    panel(im, (1140, 838, 1844, 982), fill="#EAF4F1", radius=25, shadow=False)
    d.text((1174, 865), "真正商品上线前还缺什么？", font=F["medium_small"], fill=hx("#1A665A"))
    missing = "真实 SKU 实拍与规格源｜权利 / 商标确认｜平台政策检查｜业务负责人审批｜版本 ID 与发布记录"
    textblock(im, (1174, 906), missing, F["body_small"], INK, 620, gap=7, max_lines=3)
    footer(im, page, timestamp, "这张审核表是可复制模板；其中角色与状态均为示范，不是任何真实业务的审批记录。")
    return im


def page_ai_trace_final(page: int, timestamp: str) -> Image.Image:
    im = new_bg("#F7F8F8", "#CBE5DD")
    page_header(im, page, "S1：把允许保留的“视觉规则”重建成独立画面，再让人决定能否进入下一关", "S1 由本渲染器人工绘制，特意与来源及 S0 的“带把手 + 吸管”轮廓拉开距离。它仍只是教学结构草图，不是假装成真实商品图。", tag="TRACE 04 / MANUAL REBUILD")
    d = ImageDraw.Draw(im)
    panel(im, (76, 282, 1028, 850), fill=WHITE, outline=BORDER, radius=28)
    draw_manual_rebuild(im, (105, 312, 999, 820))
    panel(im, (1061, 282, 1844, 850), fill="#102033", radius=28, shadow=False)
    pill(im, 1095, 313, "S1 / 人工重建", "#F0D548", INK, h=31)
    d.text((1095, 370), "留下的是信息层级，\n舍弃的是商品身份。", font=F["title_small"], fill=hx(WHITE))
    ledger = [
        ("保留", "单品为画面主体；高对比背景；视觉焦点不分裂。"),
        ("保留", "颜色提示靠近物体，但不假装成网页可交互组件。"),
        ("替换", "闭合旋盖、斜向硅胶环、无把手无吸管的原创结构。"),
        ("删除", "来源产品的品牌、命名、产品结构、价格、CTA、性能暗示。"),
    ]
    y = 501
    for head, body in ledger:
        pill(im, 1095, y, head, "#275265" if head == "保留" else "#6A3944", WHITE, h=28)
        textblock(im, (1183, y + 1), body, F["body_tiny"], "#D0E0E6", 575, gap=3, max_lines=2)
        y += 73
    panel(im, (76, 883, 1844, 981), fill="#FFF1BE", radius=22, shadow=False)
    d.text((108, 906), "状态不是“可发布”", font=F["medium"], fill=hx(INK))
    textblock(im, (108, 943), "S1 只通过了“示范的视觉 / 边界复审”；真实商品还必须用真实照片和已核资料替换，再经品牌、合规、渠道与业务负责人批准。", F["body_small"], "#5E4911", 1600, gap=5, max_lines=2)
    footer(im, page, timestamp, "S1 为 code/build_accio_online_casebook_v3.py 绘制的原创教学示意；没有生成、出版或上架任何真实商品。")
    return im


def page_ai_trace_evidence(page: int, timestamp: str) -> Image.Image:
    im = new_bg("#102033", "#346E82")
    d = ImageDraw.Draw(im)
    pill(im, 76, 55, "TRACE 05 / EVIDENCE LEDGER", "#F0D548", INK, h=35)
    d.text((76, 114), "把“AI 做了什么”与“人必须验证什么”分开记账。", font=F["title"], fill=hx(WHITE))
    textblock(im, (80, 182), "下面不是漂亮的流程图，而是一个真实执行时应保留的最小证据包。没有这些，最终图的来源、改动和责任都不可追溯。", F["subtitle"], "#C5D8DF", 1520, gap=8)
    # left evidence records
    panel(im, (76, 293, 1032, 878), fill="#17394B", outline="#356176", radius=28, shadow=False)
    d.text((112, 331), "应留存的工件", font=F["title_small"], fill=hx(WHITE))
    evidence = [
        ("01", "来源索引", "公开 URL、截图日期、允许抽取的规则 / 不可复制项。"),
        ("02", "事实表", "真实 SKU 的图片、规格、声明证据、缺失字段与责任人。"),
        ("03", "提示词版本", "v1 / v2、模型或工具、时间、输入文件、输出 ID。"),
        ("04", "草稿与差异", "S0 / S1、问题单、修改理由、哪些像素或文案被人工替换。"),
        ("05", "批准门", "品牌、合规、渠道、业务负责人；发布前后版本与撤回路径。"),
    ]
    y = 409
    for num, head, body in evidence:
        d.rounded_rectangle((112, y, 158, y + 46), radius=14, fill=hx("#F0D548"))
        d.text((122, y + 12), num, font=F["eyebrow"], fill=hx(INK))
        d.text((180, y - 1), head, font=F["medium_small"], fill=hx(WHITE))
        textblock(im, (180, y + 29), body, F["body_tiny"], "#C5D8DF", 785, gap=3, max_lines=2)
        y += 86
    # right responsibility table
    panel(im, (1065, 293, 1844, 878), fill="#F8F4EA", radius=28, shadow=False)
    d.text((1101, 331), "责任分工", font=F["title_small"], fill=hx(INK))
    rows = [
        ("AI 可协助", "从事实表组织提示词；生成 S0 草图；列出素材缺口；比较布局规则；形成修改候选。", "#E5D9FF"),
        ("人必须验证", "真实规格与声明、视觉相似性 / 权利、品牌语气、平台规则、最终图片真实性。", "#FFE0DB"),
        ("人必须控制", "批准、发布、覆盖线上内容、预算、对外承诺、撤回与事故响应。", "#D8F2E7"),
    ]
    y = 401
    for head, body, color in rows:
        d.rounded_rectangle((1101, y, 1807, y + 118), radius=18, fill=hx(color))
        d.text((1126, y + 20), head, font=F["medium_small"], fill=hx(INK))
        textblock(im, (1126, y + 52), body, F["body_tiny"], "#374C56", 638, gap=4, max_lines=3)
        y += 139
    panel(im, (76, 916, 1844, 1018), fill="#FFF1BE", radius=21, shadow=False)
    d.text((108, 940), "本册能够诚实证明的范围", font=F["medium"], fill=hx(INK))
    textblock(im, (108, 977), "已记录：S0 的实际 Arena 图像生成、提示词和手工 S1 重建。未声称：Accio 执行、真实 SKU 核实、任何自动发布或商业成效。", F["body_small"], "#5E4911", 1600, gap=4, max_lines=2)
    footer(im, page, timestamp, "随附 AI_ASSISTED_RECREATION_TEMPLATE.md、ai_recreation_prompt_used.txt 与 recreation_review_log.csv。")
    return im


def export_pdf(pages: list[Image.Image], path: Path) -> None:
    pages[0].save(path, "PDF", resolution=150.0, save_all=True, append_images=pages[1:])


def export_pptx(page_paths: list[Path], path: Path, timestamp: str) -> None:
    prs = Presentation()
    prs.slide_width = Inches(13.333333)
    prs.slide_height = Inches(7.5)
    blank = prs.slide_layouts[6]
    for image_path in page_paths:
        slide = prs.slides.add_slide(blank)
        slide.shapes.add_picture(str(image_path), 0, 0, width=prs.slide_width, height=prs.slide_height)
    props = prs.core_properties
    props.title = "爆款电商视觉案例库｜公开在线案例｜v3"
    props.subject = "Visual reference research; flattened delivery"
    props.author = "Arena.ai Agent Mode"
    props.comments = f"Generated {timestamp}; source and usage boundaries are documented in the companion Markdown."
    now = datetime.now()
    props.created = now
    props.modified = now
    prs.save(path)


def make_contact_sheet(paths: list[Path], path: Path) -> None:
    thumb_w, thumb_h = 384, 216
    cols = 3
    rows = (len(paths) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * thumb_w + (cols + 1) * 26, rows * thumb_h + (rows + 1) * 60 + 80), hx("#E7EFF2"))
    d = ImageDraw.Draw(sheet)
    d.text((26, 25), "Online Ecommerce Visual Casebook — v3 preview", font=F["medium"], fill=hx(INK))
    for i, p in enumerate(paths):
        image = Image.open(p).convert("RGB").resize((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        x = 26 + (i % cols) * (thumb_w + 26)
        y = 82 + (i // cols) * (thumb_h + 60)
        sheet.paste(image, (x, y))
        d.rectangle((x, y, x + thumb_w, y + thumb_h), outline=hx("#AFC2C9"), width=2)
        d.text((x, y + thumb_h + 14), f"{i + 1:02d}", font=F["eyebrow"], fill=hx(SLATE))
    sheet.save(path, quality=92)


def write_docs(timestamp: str) -> None:
    sources = "\n".join(
        f"{i}. **{c['brand']}**<br>\n"
        f"   - 视觉摘录：[{c['visual_source']}]({c['visual_url']})<br>\n"
        f"   - 案例 / 结构分析：[{c['analysis_source']}]({c['analysis_url']})"
        for i, c in enumerate(CASE_DATA, 1)
    )
    (OUT / "README.md").write_text(
        f"""# 爆款电商视觉案例库｜公开在线案例｜v3

**生成时间：{timestamp}（Asia/Shanghai）**<br>
注意：这表示沙箱构建时间；复制到 Windows 后的文件创建 / 修改时间由本机文件系统决定。

## 交付内容

- `爆款电商视觉案例库_公开在线案例_Accio视觉复刻参考_v3.pdf` — 23 页、已扁平化的案例研究 PDF
- `爆款电商视觉案例库_公开在线案例_Accio视觉复刻参考_v3.pptx` — 23 页、每页仅一张完整图片的 PPTX
- `preview_contact_sheet_v3.jpg` — 全页预览
- `SOURCES_AND_USAGE_BOUNDARIES.md` — 视觉图源、分析图源和使用边界
- `AI_ASSISTED_RECREATION_TEMPLATE.md` — AI 示范的真实边界、工件清单与迁移清单
- `ai_recreation_prompt_used.txt` — S0 实际调用提示词原文（Arena 图像模型；非 Accio）
- `recreation_review_log.csv` — 人工审核风险与改动模板

## 这版解决的问题

上一版用了自创龙虾周边来说明流程，视觉与真实产品案例的距离过大。本版不再把原创示意当主案例：

1. 选用 6 个公开在线、具有明确视觉语言的电商案例；
2. 每个案例分开“视觉图源”和“分析图源”；
3. 从每个案例提炼一条具体购买决策逻辑，而不是只评价“好看”；
4. 把案例翻译成产品介绍问题、资产角色表、PDP 首屏结构和可执行任务书；
5. 所有图片均作为低分辨率研究摘录，明确不是可商用素材、品牌授权或 Accio 实机输出。
6. 新增 6 页透明的 AI 辅助复刻示范：来源规则 → 实际提示词 → Arena 的 S0 概念图 → 人审风险单 → S1 人工重建 → 证据账本。它明确不是 Accio 实机运行。

## 公开来源

{sources}

## 运行

```bash
PYTHONPATH=/tmp/accio-deps python3 code/build_accio_online_casebook_v3.py
```

需要 `Pillow` 与 `python-pptx`。渲染源图位于 `assets/accio_online_case_research_v3/`，仅用于该研究型交付的低清引述与来源定位。
""",
        encoding="utf-8",
    )
    (OUT / "SOURCES_AND_USAGE_BOUNDARIES.md").write_text(
        f"""# Sources and usage boundaries — v3

**Rendered: {timestamp} (Asia/Shanghai)**

## What this deliverable is

This is a Chinese-language visual-analysis and workflow-reference deck. It is **not** a brand partnership, an approved marketing asset pack, a live storefront export, an Accio Work screen capture, or a promise of sales / CTR / conversion results.

## Image excerpts

The deck includes low-resolution online image excerpts solely to identify and critique the cited ecommerce visual patterns. Product photography, logos, trademarks, page screenshots, brand names and copy remain the property of their respective owners. Do **not** extract, republish, use in paid ads, put into a storefront, or present them as original / licensed assets.

For commercial production, replace every referenced image and brand mark with original photography, original design, or appropriately licensed assets.

## AI-assisted demo assets

The visual labeled **S0** in pages 16–18 is a fictional concept image actually generated in this workspace using Arena's image generator, with the prompt preserved in `ai_recreation_prompt_used.txt`. It was **not** generated in Accio, does not depict a real SKU, and cannot substantiate a product fact or commercial claim. The visual labeled **S1** is a manual, original teaching graphic drawn by the build script after the documented review; it is also not a commercial product asset. The workflow evidence and review template are documented in `AI_ASSISTED_RECREATION_TEMPLATE.md` and `recreation_review_log.csv`.

## Case sources

{sources}

## Interpretation limits

- The listed design takeaways are this report's analytical observations, not statements by the brands unless explicitly described as such in the cited source.
- Where third-party case roundups describe UX or performance, they are used as references, not independently verified experimental findings.
- Accio Work documentation can support a high-level “Agent / connector / task / human review” framing. The current account UI, permissions, available plugins and publishing behavior were not live-verified in this environment and are never depicted as fact here.
- Human review is required before any draft becomes a customer-facing listing, product claim, ad or published store content.
""",
        encoding="utf-8",
    )
    (OUT / "AI_ASSISTED_RECREATION_TEMPLATE.md").write_text(
        f"""# 透明 AI 辅助复刻示范｜证据包说明

**构建时间：{timestamp}（Asia/Shanghai）**

## 这是 / 不是

- **这是**：一个可审计的、从提示词到人工审核与手工重建的示范模板；第 16–21 页对应本文件、提示词文本与审核 CSV。
- **这是**：一次真实的 Arena 图像生成调用留下的 S0 概念图，保存在 `assets/accio_online_case_research_v3/{AI_DEMO_ASSET}`。
- **不是**：Accio 的屏幕录像、Accio 任务历史、Accio 生成输出，或对 Accio 当前功能、权限、发布能力的声明。
- **不是**：真实商品、真实 SKU、商业主图、经核实的产品性能或可以上架的广告资产。

## 端到端链路

1. **来源与边界**：公开来源只用来抽取“单品清晰 / 变体邻近 / 阅读顺序”的抽象规则。品牌、Logo、具体产品结构、页面与主张不进入生成输入。
2. **S0 提示词**：完整原文见 `ai_recreation_prompt_used.txt`。它要求一个无文字、无 Logo、虚构的非商用概念图。
3. **S0 实际图像**：由 Arena 图片工具生成；这份案例库把它明确标为“Arena 图像模型 / 非 Accio”。
4. **人工审核**：`recreation_review_log.csv` 记录四项风险与改动决策。最关键的是阻断“把手 + 吸管”的近似轮廓及任何未经核验的事实主张。
5. **S1 人工重建**：PDF 第 20 页与构建脚本的 `draw_manual_rebuild` 函数生成。它改成封闭旋盖、斜向硅胶环、无把手无吸管的教学草图；它也**不是**可上架的产品图。
6. **发布门**：故意未被打开。真实执行仍需要 SKU 实拍、规格证据、权利确认、品牌 / 合规 / 渠道 / 业务审批及可撤回的版本记录。

## 工件清单

| 工件 | 作用 | 真实性边界 |
|---|---|---|
| `ai_recreation_prompt_used.txt` | S0 实际调用的提示词原文 | 可复现提示词，不证明商品事实 |
| `{AI_DEMO_ASSET}` | Arena 图像模型实际输出的 S0 | 虚构概念图；非 Accio、非真实商品 |
| `recreation_review_log.csv` | 人审问题、处理与状态 | 模板性角色，不是实际业务审批 |
| `code/build_accio_online_casebook_v3.py` | S1 的人工重建逻辑和页面编排 | 教学示意，不生成真实商品证据 |

## 迁移到真实项目 / Accio 前的最小替换清单

- 用真实 SKU 图片、规格来源、品牌资产及渠道规则替换虚构事实表；
- 保存实际工具、帐号权限、生成时间、输入文件和输出 ID；
- 让负责人逐项批准主张、权利、品牌与发布；
- 把“草稿”和“可发布”分离，不允许工具自动发布或覆盖线上商品。
""",
        encoding="utf-8",
    )
    (OUT / "ai_recreation_prompt_used.txt").write_text(
        "S0 actual image-generation prompt\n"
        "================================\n\n"
        + AI_IMAGE_PROMPT + "\n\n"
        "Transparency note: This prompt was executed with Arena's image generator in this workspace. It was not executed in Accio. "
        "The generated visual is a fictional concept, not a verified product image or a commercial asset.\n",
        encoding="utf-8",
    )
    csv_rows = ["review_id,issue,observation,required_change,owner,status"]
    for row in AI_REVIEW_LOG:
        csv_rows.append(",".join('"' + value.replace('"', '""') + '"' for value in row))
    (OUT / "recreation_review_log.csv").write_text("\n".join(csv_rows) + "\n", encoding="utf-8")


def main() -> None:
    missing = [c["asset"] for c in CASE_DATA if not (ASSETS / c["asset"]).exists()]
    if not (ASSETS / AI_DEMO_ASSET).exists():
        missing.append(AI_DEMO_ASSET)
    if missing:
        raise FileNotFoundError(f"Missing reference image(s): {', '.join(missing)}")
    timestamp = datetime.now(ZoneInfo("Asia/Shanghai")).strftime("%Y-%m-%d %H:%M") + " Asia/Shanghai"
    OUT.mkdir(parents=True, exist_ok=True)
    if PAGES.exists():
        shutil.rmtree(PAGES)
    PAGES.mkdir(parents=True)

    pages = [
        page_cover(timestamp),
        page_boundaries(2, timestamp),
        page_gallery(3, timestamp),
    ]
    pages.extend(case_page(case, 4 + idx, timestamp) for idx, case in enumerate(CASE_DATA))
    pages.extend([
        page_matrix(10, timestamp),
        page_product_intro(11, timestamp),
        page_asset_roles(12, timestamp),
        page_pdp(13, timestamp),
        page_brief(14, timestamp),
        page_workflow(15, timestamp),
        page_ai_trace_intro(16, timestamp),
        page_ai_trace_prompt(17, timestamp),
        page_ai_trace_draft(18, timestamp),
        page_ai_trace_review(19, timestamp),
        page_ai_trace_final(20, timestamp),
        page_ai_trace_evidence(21, timestamp),
        page_sources(22, timestamp),
        page_close(23, timestamp),
    ])

    page_paths: list[Path] = []
    for n, image in enumerate(pages, 1):
        target = PAGES / f"casebook_{n:02d}.jpg"
        image.save(target, quality=95, subsampling=0)
        page_paths.append(target)
    pdf = OUT / "爆款电商视觉案例库_公开在线案例_Accio视觉复刻参考_v3.pdf"
    pptx = OUT / "爆款电商视觉案例库_公开在线案例_Accio视觉复刻参考_v3.pptx"
    preview = OUT / "preview_contact_sheet_v3.jpg"
    export_pdf([Image.open(p).convert("RGB") for p in page_paths], pdf)
    export_pptx(page_paths, pptx, timestamp)
    make_contact_sheet(page_paths, preview)
    write_docs(timestamp)
    print(f"built {pdf} ({pdf.stat().st_size:,} bytes)")
    print(f"built {pptx} ({pptx.stat().st_size:,} bytes)")
    print(f"built {preview} ({preview.stat().st_size:,} bytes)")
    print(f"pages={len(page_paths)}; timestamp={timestamp}")


if __name__ == "__main__":
    main()
