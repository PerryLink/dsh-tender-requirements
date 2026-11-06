#!/usr/bin/env python3
"""README visuals for dsh-tender-requirements, drawn from the shipped pipeline.

The figures are read off `src/model.ts`, `src/requirements.ts`, `src/index.ts`
and one real quickstart run of `samples/quickstart/input/tender-sample.docx`
(6 found, 3 missing, 6 composition entries, queues a=8 b=2 c=1,
deliverable=false, coverage 6 hit / 4 miss).  They are not generic checker art.

  hero 1440x576  (Pillow; zh/en x light/dark -> four WebP files)
      Left column: kicker / wordmark / two value lines / subtitle / meta /
      footer.  Right side: the synthetic sample's two-column front appendix
      with its six real key-value rows, and the three evidence queues that the
      run produced.  Queue C carries the one real hedged clause and the
      deliverable=false gate.

  flow 1100x660  (hand-written SVG, light/dark)
      Grammar: a two-reader intake feeding a nine-item structural grid and a
      six-family wording classifier; the wording stream descends two evidence
      gates (verbatim + no hedge, then binding section) while the front-appendix
      keys take a dashed bypass; both land in the A/B/C queue scoreboard.  A
      ten-cell COV-01..COV-10 coverage ribbon closes the figure.  No row of five
      boxes and arrows.

Every label is measured with the same font file before it is drawn; a label
that would overflow aborts the run instead of shipping clipped text.

Run once:  python scripts/gen-readme-assets.py
Requires:  Pillow, and the Windows fonts msyh.ttc / msyhbd.ttc / consola.ttf.
"""
from __future__ import annotations

import os
from html import escape

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs", "assets")
NAME = "dsh-tender-requirements"

FONT_FILES = {
    "cjk": r"C:\Windows\Fonts\msyh.ttc",
    "cjk_bold": r"C:\Windows\Fonts\msyhbd.ttc",
    "mono": r"C:\Windows\Fonts\consola.ttf",
    "mono_bold": r"C:\Windows\Fonts\consolab.ttf",
}
for _kind, _path in FONT_FILES.items():
    if not os.path.exists(_path):
        raise SystemExit(f"FATAL: font missing: {_path}")
os.makedirs(OUT, exist_ok=True)

RADIUS = 20
SHADOW = 24

SKIN = {
    "light": dict(
        bg_from="#f9f6fd", bg_to="#e4eaf8",
        card="#ffffff", edge="#e6e2ef",
        text="#141419", sub="#4d5261", faint="#8f94a4",
        accent="#4B67B4", pill="#ece7f9", band="#f5f2fb",
        grid="#e7e4f0", mark="#b45309", mark_bg="#fdf3e9",
        ok="#15803d", ok_bg="#eaf6ee",
        shadow=(38, 30, 72), glow=34,
    ),
    "dark": dict(
        bg_from="#131a2a", bg_to="#0c1016",
        card="#1b2231", edge="#2e374b",
        text="#f0f3f9", sub="#a8b1c4", faint="#737b8d",
        accent="#8496f5", pill="#242d42", band="#202839",
        grid="#262f42", mark="#d9a441", mark_bg="#2a2216",
        ok="#3fb950", ok_bg="#16281c",
        shadow=(0, 0, 0), glow=48,
    ),
}


def font(size: float, kind: str = "cjk") -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_FILES[kind], int(round(size)))


def hx(color: str) -> tuple[int, int, int]:
    color = color.lstrip("#")
    return tuple(int(color[i:i + 2], 16) for i in (0, 2, 4))


_MEASURE = ImageDraw.Draw(Image.new("RGB", (8, 8)))


def measure(text: str, size: float, kind: str = "cjk") -> float:
    return _MEASURE.textlength(text, font=font(size, kind))


def require_w(text: str, size: float, kind: str, max_w: float,
              what: str) -> None:
    got = measure(text, size, kind)
    if got > max_w + 0.6:
        raise SystemExit(f"FATAL: {what} overflows: {text!r} needs "
                         f"{got:.1f}px > {max_w:.0f}px")


def fit(text: str, kind: str, max_w: float, start: int, minimum: int) -> int:
    size = start
    while size > minimum:
        if measure(text, size, kind) <= max_w:
            return size
        size -= 1
    raise SystemExit(f"FATAL: text does not fit {max_w}px at >= {minimum}px: "
                     f"{text!r}")


def fit_lines(lines: list[str], kind: str, max_w: float, start: int,
              minimum: int) -> int:
    return min(fit(t, kind, max_w, start, minimum) for t in lines)


def gradient(w: int, h: int, top: str, bottom: str) -> Image.Image:
    base = Image.new("RGB", (w, h))
    draw = ImageDraw.Draw(base)
    a, b = hx(top), hx(bottom)
    for y in range(h):
        t = 0.12 * (y / h) + 0.88 * (y / h) ** 1.3
        draw.line([(0, y), (w, y)],
                  fill=tuple(int(p + (q - p) * t) for p, q in zip(a, b)))
    return base


def glow(img: Image.Image, cx: int, cy: int, r: int, color: str,
         alpha: int) -> Image.Image:
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    rgb = hx(color)
    for i in range(10, 0, -1):
        rr = r * i / 10
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr],
                  fill=rgb + (int(alpha * (1 - i / 11)),))
    return Image.alpha_composite(img.convert("RGBA"),
                                 layer.filter(ImageFilter.GaussianBlur(26))
                                 ).convert("RGB")


def card(img: Image.Image, box: tuple[int, int, int, int], s: dict,
         radius: int = RADIUS, shadow: int = SHADOW,
         fill: str | None = None, edge: str | None = None,
         width: int = 2) -> Image.Image:
    x0, y0, x1, y1 = box
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)
    for i in range(shadow, 0, -2):
        sd.rounded_rectangle([x0 - i // 6, y0 + i // 2, x1 + i // 6, y1 + i],
                             radius=radius + i // 6,
                             fill=s["shadow"] + (int(11 * (1 - i / shadow)),))
    base = Image.alpha_composite(img.convert("RGBA"),
                                 sh.filter(ImageFilter.GaussianBlur(11)))
    d = ImageDraw.Draw(base)
    d.rounded_rectangle(box, radius=radius, fill=hx(fill or s["card"]),
                        outline=hx(edge or s["edge"]), width=width)
    return base.convert("RGB")


def pill(img: Image.Image, xy: tuple[int, int], text: str, s: dict,
         size: int = 16, fg: str | None = None, bg: str | None = None,
         kind: str = "cjk_bold", pad: int = 15) -> int:
    d = ImageDraw.Draw(img)
    f = font(size, kind)
    w = d.textlength(text, font=f)
    x, y = xy
    h = size + 20
    d.rounded_rectangle([x, y, x + w + 2 * pad, y + h], radius=h // 2,
                        fill=hx(bg or s["pill"]))
    d.text((x + pad, y + h / 2), text, font=f, fill=hx(fg or s["accent"]),
           anchor="lm")
    return int(x + w + 2 * pad)


def chip_right(img: Image.Image, right: int, y: int, text: str, fg: str,
               bg: str, size: float = 11, height: int = 20,
               kind: str = "cjk_bold") -> int:
    d = ImageDraw.Draw(img)
    w = d.textlength(text, font=font(size, kind)) + 18
    x = right - w
    d.rounded_rectangle([x, y, right, y + height], radius=height / 2,
                        fill=hx(bg))
    d.text((x + 9, y + height / 2), text, font=font(size, kind),
           fill=hx(fg), anchor="lm")
    return int(x)


# --------------------------------------------------------------------------- hero
# All six rows are the synthetic quickstart front appendix verbatim; the C
# clause is the one queue-C quote that run actually produced.
HERO = {
    "zh": dict(
        kicker="DeepSeek Harness 插件 · 招标要点抽取",
        value=["把招标文件拆成可复核的要点清单。",
               "每项都写清检索到什么、还缺什么。"],
        sub="只读、离线、可复跑；抽取不是合规判定。",
        meta="tender_requirements · 九项 · 六族 · A 8 / B 2 / C 1 · COV-01…10",
        foot="Apache-2.0 · 无网络 · 无模型调用 · 无遥测",
        doc_title="投标人须知前附表",
        doc_chip="恰好两列",
        doc_meta="tender-sample.docx · 合成样例",
        headers=["条款号", "编列内容"],
        rows=[
            ["投标截止时间", "2026年11月20日 9时30分"],
            ["投标保证金", "人民币伍万元整（¥50,000.00）"],
            ["投标有效期", "投标截止之日起 90 日历天"],
            ["最高限价", "人民币贰佰万元整"],
            ["密封要求", "应密封并在封口处加盖公章"],
            ["投标文件份数", "正本一份，副本四份"],
        ],
        doc_foot="9 项：6 检索到 · 3 未检索到（仍逐行打印）",
        tiers=["A 交付", "B 待确认", "C 必须处理"],
        a_detail=["6 前附表键值 · 逐字来自表格",
                  "2 条款 · 逐字 + 约束章节 + 无修饰"],
        b_detail=["逐字可引，但无章节定位线索"],
        c_reason="含修饰词「原则上」→ 非绝对表述",
        c_chip="未完成体检",
        gate="C ≠ 0 → deliverable: false",
        ids=["TRQ-REJ-002/003 · TRQ-HDR-006…011",
             "TRQ-REJ-001 · TRQ-REJ-004"],
        provenance="observed from samples/quickstart",
    ),
    "en": dict(
        kicker="DeepSeek Harness plugin · tender extraction",
        value=["One tender .docx, one reviewable list.",
               "Every item: found, or why it is missing."],
        sub="Read-only, offline, repeatable — not a compliance verdict.",
        meta="tender_requirements · 9 items · 6 families · A 8 / B 2 / C 1",
        foot="Apache-2.0 · no network · no model call · no telemetry",
        doc_title="Front appendix",
        doc_chip="exactly 2 cols",
        doc_meta="tender-sample.docx · synthetic sample",
        headers=["clause", "content"],
        rows=[
            ["Deadline", "20 Nov 2026, 09:30"],
            ["Deposit", "CNY 50,000 (¥50,000.00)"],
            ["Validity", "90 days from deadline"],
            ["Ceiling", "CNY 2,000,000"],
            ["Sealing", "sealed + stamp on the seal"],
            ["Copies", "1 original, 4 copies"],
        ],
        doc_foot="9 items: 6 retrieved · 3 not retrieved (still printed)",
        tiers=["A delivered", "B needs review", "C must handle"],
        a_detail=["6 front-appendix keys · verbatim",
                  "2 clauses · verbatim + binding + no hedge"],
        b_detail=["Quotable, but no section anchor"],
        c_reason="hedged by 原则上 — not absolute",
        c_chip="check incomplete",
        gate="C ≠ 0 → deliverable: false",
        ids=["TRQ-REJ-002/003 · TRQ-HDR-006…011",
             "TRQ-REJ-001 · TRQ-REJ-004"],
        provenance="observed from samples/quickstart",
    ),
}


def hero(lang: str, skin: str) -> None:
    s = SKIN[skin]
    h = HERO[lang]
    W, H = 1440, 576
    img = gradient(W, H, s["bg_from"], s["bg_to"])
    img = glow(img, 1140, 88, 360, s["accent"], s["glow"])
    img = glow(img, 130, 558, 300, s["accent"], max(8, s["glow"] // 3))

    # very light dot texture, kept away from text by low alpha
    dots = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dd = ImageDraw.Draw(dots)
    for x in range(18, W, 34):
        for y in range(18, H, 34):
            dd.ellipse([x, y, x + 1.3, y + 1.3], fill=hx(s["grid"]) + (60,))
    img = Image.alpha_composite(img.convert("RGBA"), dots).convert("RGB")

    d = ImageDraw.Draw(img)
    m = 56
    col_w = 640

    # ---- left column --------------------------------------------------------
    pill(img, (m, 54), h["kicker"], s, size=16)
    version = "v0.2.4"
    vw = measure(version, 12, "mono_bold") + 26
    pill(img, (m + col_w - int(vw), 56), version, s, size=12,
         kind="mono_bold", pad=13)
    d = ImageDraw.Draw(img)

    title_size = fit(NAME, "mono_bold", col_w, 52, 48)
    d.text((m - 1, 118), NAME, font=font(title_size, "mono_bold"),
           fill=hx(s["text"]))
    require_w(NAME, title_size, "mono_bold", col_w, "hero title")

    value_size = fit_lines(h["value"], "cjk_bold", col_w,
                           34 if lang == "zh" else 30, 26)
    for i, line in enumerate(h["value"]):
        d.text((m, 220 + i * 54), line, font=font(value_size, "cjk_bold"),
               fill=hx(s["text"]))
        require_w(line, value_size, "cjk_bold", col_w, "hero value line")

    sub_size = 22 if lang == "zh" else fit(h["sub"], "cjk", col_w, 21, 18)
    require_w(h["sub"], sub_size, "cjk", col_w, "hero subtitle")
    d.text((m, 342), h["sub"], font=font(sub_size, "cjk"), fill=hx(s["sub"]))

    meta_size = 19 if lang == "zh" else 18
    require_w(h["meta"], meta_size, "cjk", col_w, "hero meta")
    d.text((m + 1, 396), h["meta"], font=font(meta_size, "cjk"),
           fill=hx(s["faint"]))

    d.line([m + 1, 444, m + col_w - 4, 444], fill=hx(s["grid"]), width=2)
    require_w(h["foot"], 16, "cjk", col_w, "hero footer")
    d.text((m + 1, 462), h["foot"], font=font(16, "cjk"), fill=hx(s["faint"]))

    # ---- front appendix card ------------------------------------------------
    img = card(img, (700, 64, 1032, 456), s, radius=20, shadow=26)
    d = ImageDraw.Draw(img)
    d.text((700, 44), "allTablesOf → frontRowsOf → buildPack",
           font=font(11, "mono"), fill=hx(s["accent"]))
    require_w("allTablesOf → frontRowsOf → buildPack", 11, "mono", 330,
              "pipeline label")

    d.rounded_rectangle([716, 80, 752, 116], radius=10, fill=hx(s["pill"]))
    d.text((734, 98), ".docx", font=font(11, "mono_bold"),
           fill=hx(s["accent"]), anchor="mm")
    d.text((764, 97), h["doc_title"], font=font(15, "cjk_bold"),
           fill=hx(s["text"]), anchor="lm")
    require_w(h["doc_title"], 15, "cjk_bold", 176, "doc title")
    chip_right(img, 1016, 81, h["doc_chip"], s["accent"], s["pill"],
               size=11)
    d = ImageDraw.Draw(img)
    d.text((716, 128), h["doc_meta"], font=font(12, "cjk"),
           fill=hx(s["sub"]), anchor="lm")
    require_w(h["doc_meta"], 12, "cjk", 300, "doc meta")

    x0, x1 = 716, 1016
    label_x, value_x = 728, 828
    d.rounded_rectangle([x0 - 4, 146, x1 + 4, 174], radius=8,
                        fill=hx(s["band"]))
    for i, head in enumerate(h["headers"]):
        x = label_x if i == 0 else value_x
        limit = 96 if i == 0 else 186
        require_w(head, 11.5, "cjk_bold", limit, "table header")
        d.text((x, 160), head, font=font(11.5, "cjk_bold"),
               fill=hx(s["sub"]), anchor="lm")

    for i, (label, value) in enumerate(h["rows"]):
        y = 176 + i * 38
        require_w(label, 12, "cjk_bold", 96, "front row label")
        require_w(value, 12, "cjk", 184, "front row value")
        d.text((label_x, y + 19), label, font=font(12, "cjk_bold"),
               fill=hx(s["text"]), anchor="lm")
        d.text((value_x, y + 19), value, font=font(12, "cjk"),
               fill=hx(s["text"]), anchor="lm")
        d.line([x0 - 4, y + 38, x1 + 4, y + 38], fill=hx(s["grid"]),
               width=1)

    require_w(h["doc_foot"], 11.5, "cjk", 300, "doc footer")
    d.text((716, 420), h["doc_foot"], font=font(11.5, "cjk"),
           fill=hx(s["faint"]), anchor="lm")

    # ---- three evidence queues ---------------------------------------------
    qx0, qx1 = 1052, 1384
    ix0, ix1 = 1068, 1368

    def queue(card_box, title, count, colour, detail, ids,
              warn: bool = False) -> None:
        nonlocal img
        img = card(img, card_box, s, radius=20, shadow=24,
                   edge=s["mark"] if warn else None)
        dd = ImageDraw.Draw(img)
        x0, y0, x1, y1 = card_box
        dd.rounded_rectangle([x0 + 2, y0 + 16, x0 + 6, y1 - 16], radius=2,
                             fill=hx(colour))
        dd.text((x0 + 16, y0 + 28), title, font=font(15, "cjk_bold"),
               fill=hx(s["text"]), anchor="lm")
        require_w(title, 15, "cjk_bold", 190, "queue title")
        dd.text((x1 - 16, y0 + 30), count, font=font(26, "mono_bold"),
               fill=hx(colour), anchor="rm")
        return None

    # A
    queue((qx0, 64, qx1, 186), h["tiers"][0], "8", s["accent"],
          h["a_detail"], h["ids"][0])
    d = ImageDraw.Draw(img)
    require_w(h["a_detail"][0], 12, "cjk", 292, "A detail 1")
    require_w(h["a_detail"][1], 12, "cjk", 292, "A detail 2")
    d.text((ix0, 116), h["a_detail"][0], font=font(12, "cjk"),
           fill=hx(s["sub"]), anchor="lm")
    d.text((ix0, 138), h["a_detail"][1], font=font(12, "cjk"),
           fill=hx(s["sub"]), anchor="lm")
    require_w(h["ids"][0], 11.5, "mono", 300, "A ids")
    d.text((ix0, 162), h["ids"][0], font=font(11.5, "mono"),
           fill=hx(s["faint"]), anchor="lm")

    # B
    queue((qx0, 202, qx1, 302), h["tiers"][1], "2", s["faint"],
          h["b_detail"], h["ids"][1])
    d = ImageDraw.Draw(img)
    require_w(h["b_detail"][0], 12, "cjk", 292, "B detail")
    d.text((ix0, 254), h["b_detail"][0], font=font(12, "cjk"),
           fill=hx(s["sub"]), anchor="lm")
    require_w(h["ids"][1], 11.5, "mono", 300, "B ids")
    d.text((ix0, 278), h["ids"][1], font=font(11.5, "mono"),
           fill=hx(s["faint"]), anchor="lm")

    # C
    img = card(img, (qx0, 318, qx1, 456), s, radius=20, shadow=24,
               edge=s["mark"], width=2)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([qx0 + 2, 334, qx0 + 6, 440], radius=2,
                        fill=hx(s["mark"]))
    d.text((ix0, 342), h["tiers"][2], font=font(15, "cjk_bold"),
           fill=hx(s["text"]), anchor="lm")
    require_w(h["tiers"][2], 15, "cjk_bold", 190, "C title")
    d.text((ix1, 344), "1", font=font(26, "mono_bold"), fill=hx(s["mark"]),
           anchor="rm")
    chip_right(img, 1340, 330, h["c_chip"], s["mark"], s["mark_bg"], size=11)
    d = ImageDraw.Draw(img)

    d.rounded_rectangle([ix0, 354, ix1, 392], radius=10, fill=hx(s["mark_bg"]))
    quote = "原则上，投标有效期不足的按无效投标处理。"
    require_w(quote, 12, "cjk", 284, "C quote")
    d.text((ix0 + 12, 376), quote, font=font(12, "cjk"),
           fill=hx(s["mark"]), anchor="lm")
    require_w(h["c_reason"], 12, "cjk", 292, "C reason")
    d.text((ix0, 412), h["c_reason"], font=font(12, "cjk"),
           fill=hx(s["sub"]), anchor="lm")

    gate_size = 12
    require_w(h["gate"], gate_size, "cjk_bold", 260, "C gate")
    d.rounded_rectangle([ix0, 424, ix1, 448], radius=12, fill=hx(s["mark_bg"]))
    d.text((ix0 + 12, 436), h["gate"], font=font(gate_size, "cjk_bold"),
           fill=hx(s["mark"]), anchor="lm")

    require_w(h["provenance"], 11, "mono", 330, "provenance")
    d.text((qx1, 492), h["provenance"], font=font(11, "mono"),
           fill=hx(s["faint"]), anchor="rm")

    target = os.path.join(OUT, f"{NAME}-hero-{lang}-{skin}.webp")
    img.save(target, "WEBP", quality=90, method=6)
    print(f"wrote {os.path.relpath(target, ROOT)}")


# --------------------------------------------------------------------------- SVG
FAM = {
    "sans": "'Microsoft YaHei','Segoe UI','PingFang SC','Noto Sans CJK SC',sans-serif",
    "mono": "Consolas,'Microsoft YaHei',ui-monospace,monospace",
}


def svg_font_kind(family: str, weight: int) -> str:
    if family == "mono":
        return "mono_bold" if weight >= 600 else "mono"
    return "cjk_bold" if weight >= 600 else "cjk"


def svg_text(x: float, y: float, text: str, size: float, fill: str,
             family: str = "sans", weight: int = 400, anchor: str = "start",
             max_w: float | None = None, opacity: float | None = None,
             letter_spacing: float | None = None) -> str:
    kind = svg_font_kind(family, weight)
    if max_w is not None:
        require_w(text, size, kind, max_w, f"flow text {text!r}")
    attrs = [f'x="{x:g}"', f'y="{y:g}"', f'fill="{fill}"',
             f'font-family="{FAM[family]}"', f'font-size="{size:g}"']
    if weight != 400:
        attrs.append(f'font-weight="{weight}"')
    if anchor != "start":
        attrs.append(f'text-anchor="{anchor}"')
    if opacity is not None:
        attrs.append(f'opacity="{opacity:g}"')
    if letter_spacing is not None:
        attrs.append(f'letter-spacing="{letter_spacing:g}"')
    return f'<text {" ".join(attrs)}>{escape(text)}</text>'


def rrect(x: float, y: float, w: float, h: float, r: float, fill: str,
          stroke: str | None = None, sw: float = 1.4,
          shadow: bool = False) -> str:
    attrs = [f'x="{x:g}"', f'y="{y:g}"', f'width="{w:g}"', f'height="{h:g}"',
             f'rx="{r:g}"', f'fill="{fill}"']
    if stroke is not None:
        attrs.append(f'stroke="{stroke}"')
        attrs.append(f'stroke-width="{sw:g}"')
    if shadow:
        attrs.append('filter="url(#soft)"')
    return f'<rect {" ".join(attrs)}/>'


def arrow(points: list[tuple[float, float]], colour: str, marker: str,
          dashed: bool = False, sw: float = 1.7) -> str:
    d = "M" + " L".join(f"{x:g} {y:g}" for x, y in points)
    dash = ' stroke-dasharray="5 4"' if dashed else ""
    return (f'<path d="{d}" fill="none" stroke="{colour}" '
            f'stroke-width="{sw:g}" stroke-linecap="round" '
            f'stroke-linejoin="round"{dash} marker-end="url(#{marker})"/>')


def flow(skin: str) -> None:
    s = SKIN[skin]
    parts: list[str] = []
    parts.append('<svg xmlns="http://www.w3.org/2000/svg" width="1100" '
                 'height="660" viewBox="0 0 1100 660" role="img" '
                 'aria-labelledby="figTitle figDesc">')
    parts.append('<title id="figTitle">dsh-tender-requirements structure: '
                 'two readers, a nine-item grid and six wording families, two '
                 'evidence gates, and the A/B/C queue scoreboard above a '
                 'ten-cell coverage net</title>')
    parts.append('<desc id="figDesc">A .docx is read twice: every table '
                 'through allTablesOf and the paragraphs through ingestDocx. '
                 'The table channel keeps exactly two-column tables and yields '
                 'six front-appendix key rows for the nine-item grid (6 of 9 '
                 'retrieved) plus the composition list and copy counts. The '
                 'paragraph channel splits sentences into six rejection '
                 'families. A clause passes gate one only when it is verbatim '
                 'and unhedged; gate two decides A when it sits in a binding '
                 'section, otherwise B. Hedged or unlocated clauses go to C. '
                 'Front-appendix keys bypass both gates into A. The run gives '
                 'A 8, B 2, C 1; because C is non-empty deliverable is false. '
                 'The COV-01 to COV-10 ribbon reports 6 hit and 4 miss, and a '
                 'miss means not retrieved, never absent.</desc>')
    parts.append('<defs>')
    parts.append('<linearGradient id="bg" x1="0" y1="0" x2="0.25" y2="1">'
                 f'<stop offset="0" stop-color="{s["bg_from"]}"/>'
                 f'<stop offset="1" stop-color="{s["bg_to"]}"/></linearGradient>')
    dot = "#cfc8e2" if skin == "light" else "#2b3446"
    parts.append('<pattern id="dots" width="28" height="28" '
                 'patternUnits="userSpaceOnUse">'
                 f'<circle cx="1.2" cy="1.2" r="1.2" fill="{dot}"/></pattern>')
    flood = "#2b2440" if skin == "light" else "#000000"
    opacity = "0.12" if skin == "light" else "0.5"
    parts.append('<filter id="soft" x="-30%" y="-30%" width="170%" '
                 'height="185%">'
                 f'<feDropShadow dx="0" dy="7" stdDeviation="10" '
                 f'flood-color="{flood}" flood-opacity="{opacity}"/>'
                 '</filter>')
    marker_specs = {
        "arr": s["accent"], "arrfaint": s["faint"], "arrwarn": s["mark"],
        "arrok": s["ok"],
    }
    for name, colour in marker_specs.items():
        parts.append(
            f'<marker id="{name}" viewBox="0 0 10 10" refX="9" refY="5" '
            'markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
            f'<path d="M0 0 L10 5 L0 10 z" fill="{colour}"/></marker>')
    parts.append('</defs>')
    parts.append(rrect(0, 0, 1100, 660, 22, "url(#bg)"))
    parts.append('<rect width="1100" height="660" rx="22" fill="url(#dots)" '
                 'opacity="0.35"/>')

    # ---- header -------------------------------------------------------------
    parts.append(svg_text(38, 40, "STRUCTURE · DSH TENDER REQUIREMENTS", 11,
                          s["accent"], "sans", 700, letter_spacing=1.2,
                          max_w=600))
    parts.append(svg_text(38, 72,
                          "Two readers, two evidence gates, three queues", 23,
                          s["text"], "sans", 700, max_w=900))
    parts.append(svg_text(38, 96,
                          "A tier is evidence strength, not priority — a "
                          "non-empty C sets deliverable = false.", 12,
                          s["sub"], "sans", 400, max_w=900))
    parts.append(svg_text(1062, 40, "v0.2.4 · tender_requirements", 11,
                          s["faint"], "mono", 400, anchor="end",
                          max_w=260))
    parts.append(f'<line x1="36" y1="112" x2="1064" y2="112" '
                 f'stroke="{s["grid"]}" stroke-width="1"/>')

    # ---- left: one document, two readers -----------------------------------
    parts.append(rrect(36, 132, 264, 82, 18, s["card"], s["edge"], 1.4, True))
    parts.append(rrect(50, 147, 36, 36, 10, s["pill"]))
    parts.append(svg_text(68, 169, ".docx", 11, s["accent"], "mono", 700,
                          anchor="middle", max_w=32))
    parts.append(svg_text(96, 157, "tender .docx", 14, s["text"], "sans", 700,
                          max_w=120))
    parts.append(rrect(226, 140, 66, 20, 10, s["pill"]))
    parts.append(svg_text(259, 154, "read-only", 11, s["accent"], "sans", 700,
                          anchor="middle", max_w=58))
    parts.append(svg_text(96, 177, "tender_requirements", 11, s["sub"], "mono",
                          400, max_w=170))
    parts.append(svg_text(50, 203, "samples/quickstart · sample", 11,
                          s["faint"], "mono", 400, max_w=236))

    parts.append(arrow([(168, 214), (168, 224)], s["faint"], "arrfaint"))
    parts.append(arrow([(100, 224), (100, 240)], s["faint"], "arrfaint"))
    parts.append(arrow([(236, 224), (236, 240)], s["faint"], "arrfaint"))

    parts.append(rrect(36, 244, 264, 100, 18, s["card"], s["edge"], 1.4, True))
    parts.append(svg_text(50, 266, "table reader", 13, s["text"], "sans", 700,
                          max_w=160))
    parts.append(svg_text(50, 286, "allTablesOf", 12, s["accent"], "mono", 700,
                          max_w=160))
    parts.append(svg_text(50, 306, "every table · exactly 2 columns", 11,
                          s["sub"], "sans", 400, max_w=186))
    parts.append(svg_text(50, 324, "0 tables → TenderError", 11, s["mark"],
                          "mono", 400, max_w=186))
    # mini two-column table icon
    ix, iy = 246, 262
    parts.append(rrect(ix, iy, 40, 58, 6, s["band"], s["grid"], 1))
    parts.append(f'<line x1="{ix}" y1="{iy + 14}" x2="{ix + 40}" '
                 f'y2="{iy + 14}" stroke="{s["grid"]}" stroke-width="1"/>')
    parts.append(f'<line x1="{ix + 16}" y1="{iy}" x2="{ix + 16}" '
                 f'y2="{iy + 58}" stroke="{s["grid"]}" stroke-width="1"/>')
    for k in (28, 42):
        parts.append(f'<line x1="{ix}" y1="{iy + k}" x2="{ix + 40}" '
                     f'y2="{iy + k}" stroke="{s["grid"]}" stroke-width="0.8"/>')
    parts.append(f'<rect x="{ix + 2}" y="{iy + 2}" width="12" height="10" '
                 f'fill="{s["accent"]}" opacity="0.35"/>')

    parts.append(rrect(36, 364, 264, 100, 18, s["card"], s["edge"], 1.4, True))
    parts.append(svg_text(50, 386, "paragraph reader", 13, s["text"], "sans",
                          700, max_w=180))
    parts.append(svg_text(50, 406, "ingestDocx", 12, s["accent"], "mono", 700,
                          max_w=160))
    parts.append(svg_text(50, 426, "composition · copies · sentences", 11,
                          s["sub"], "sans", 400, max_w=190))
    parts.append(svg_text(50, 444, "≥3 consecutive entries", 11, s["sub"],
                          "sans", 400, max_w=190))
    # mini paragraph-lines icon
    lx, ly = 252, 382
    for k, length in enumerate((34, 30, 34, 24)):
        parts.append(f'<rect x="{lx}" y="{ly + k * 14}" width="{length}" '
                     f'height="4" rx="2" fill="{s["accent"]}" '
                     f'opacity="{0.55 - k * 0.1:g}"/>')

    parts.append(svg_text(38, 492,
                          "main file only · amendments not merged", 11,
                          s["faint"], "sans", 400, max_w=264))
    parts.append(svg_text(38, 510,
                          "no network · no model call · no second copy", 11,
                          s["faint"], "sans", 400, max_w=264))

    # ---- center top: nine structural items ---------------------------------
    parts.append(svg_text(330, 136, "STRUCTURE · nine items", 12, s["text"],
                          "sans", 700, max_w=300))
    parts.append(svg_text(730, 136, "6 / 9 retrieved", 11, s["faint"], "sans",
                          400, anchor="end", max_w=160))

    labels = ["Deadline", "Opening", "Deposit", "Validity", "Ceiling",
              "Copies", "Sealing", "Site visit", "Clarify"]
    found = [True, True, True, True, True, False, True, False, False]
    for i, (label, hit) in enumerate(zip(labels, found)):
        col, row = i % 3, i // 3
        x = 330 + col * 138
        y = 150 + row * 46
        parts.append(rrect(x, y, 124, 38, 12, s["card"], s["grid"], 1.1))
        if hit:
            parts.append(f'<circle cx="{x + 13}" cy="{y + 19}" r="4.2" '
                         f'fill="{s["ok"]}"/>')
            colour = s["text"]
        else:
            parts.append(f'<circle cx="{x + 13}" cy="{y + 19}" r="3.8" '
                         f'fill="none" stroke="{s["mark"]}" stroke-width="1.6"/>')
            colour = s["mark"]
        parts.append(svg_text(x + 25, y + 24, label, 13, colour, "sans",
                              700 if hit else 400, max_w=92))

    parts.append(svg_text(
        330, 298,
        "frontRowsOf 6 keys · compositionOf 6 entries · readCopies 1/4",
        11, s["faint"], "mono", 400, max_w=400))

    # ---- center bottom: six families, two gates ----------------------------
    parts.append(svg_text(330, 326,
                          "WORDING · six families → evidence gates", 12,
                          s["text"], "sans", 700, max_w=400))

    families = [("refuse", "拒收"), ("invalid", "无效投标"),
                ("reject", "否决·废标"), ("disqualify", "取消资格"),
                ("deviation", "重大偏差"), ("postAward", "取消中标")]
    for i, (code, word) in enumerate(families):
        col, row = i % 2, i // 2
        x = 330 + col * 96
        y = 338 + row * 46
        parts.append(rrect(x, y, 88, 40, 12, s["card"], s["grid"], 1.1))
        parts.append(svg_text(x + 44, y + 15, code, 11, s["accent"], "mono",
                              700, anchor="middle", max_w=80))
        parts.append(svg_text(x + 44, y + 32, word, 13, s["text"], "sans",
                              400, anchor="middle", max_w=80))

    parts.append(arrow([(514, 358), (532, 358)], s["accent"], "arr"))

    parts.append(rrect(536, 338, 194, 64, 14, s["card"], s["edge"], 1.4, True))
    parts.append(svg_text(550, 358, "① verbatim + no hedge?", 13, s["text"],
                          "sans", 700, max_w=170))
    parts.append(svg_text(550, 378, "no → C", 11, s["mark"], "sans", 700,
                          max_w=60))
    parts.append(svg_text(606, 378, "yes ↓", 11, s["accent"], "sans", 700,
                          max_w=44))
    parts.append(svg_text(550, 394, "quoteVerified · HEDGES", 11, s["faint"],
                          "mono", 400, max_w=170))

    parts.append(rrect(536, 414, 194, 64, 14, s["card"], s["edge"], 1.4, True))
    parts.append(svg_text(550, 434, "② binding section?", 13, s["text"],
                          "sans", 700, max_w=170))
    parts.append(svg_text(550, 454, "yes → A · no → B", 11, s["accent"],
                          "sans", 700, max_w=170))
    parts.append(svg_text(550, 470, "投标人须知/评标办法/废标", 11, s["faint"],
                          "sans", 400, max_w=170))

    parts.append(arrow([(633, 402), (633, 412)], s["accent"], "arr"))
    parts.append(arrow([(730, 370), (740, 370), (740, 210), (756, 210)],
                       s["mark"], "arrwarn"))
    parts.append(arrow([(730, 434), (746, 434), (746, 350), (756, 350)],
                       s["accent"], "arr"))
    parts.append(arrow([(730, 462), (756, 462)], s["faint"], "arrfaint"))
    parts.append(arrow([(730, 280), (736, 288), (790, 288), (790, 294)],
                       s["accent"], "arr", dashed=True))

    # ---- right: queue scoreboard -------------------------------------------
    parts.append(svg_text(1064, 140, "report order C → A → B", 11,
                          s["faint"], "sans", 400, anchor="end", max_w=180))
    parts.append(rrect(760, 150, 304, 130, 18, s["card"], s["mark"], 2, True))
    parts.append(svg_text(776, 176, "C 必须处理", 15, s["text"], "sans", 700,
                          max_w=190))
    parts.append(svg_text(1048, 178, "1", 26, s["mark"], "mono", 700,
                          anchor="end", max_w=40))
    parts.append(rrect(776, 188, 272, 36, 10, s["mark_bg"]))
    parts.append(svg_text(788, 210, "原则上，投标有效期不足的按无效投标处理。",
                          12, s["mark"], "sans", 400, max_w=252))
    parts.append(svg_text(776, 244, "hedged by 原则上 → not absolute", 11.5,
                          s["sub"], "sans", 400, max_w=272))
    parts.append(rrect(776, 254, 272, 22, 11, s["mark_bg"]))
    parts.append(svg_text(788, 269, "C ≠ 0 → deliverable: false", 12,
                          s["mark"], "sans", 700, max_w=252))

    parts.append(rrect(760, 296, 304, 102, 18, s["card"], s["edge"], 1.4,
                       True))
    parts.append(svg_text(776, 320, "A 交付", 15, s["text"], "sans", 700,
                          max_w=140))
    parts.append(svg_text(1048, 322, "8", 26, s["accent"], "mono", 700,
                          anchor="end", max_w=40))
    parts.append(svg_text(776, 342, "6 front-appendix keys · verbatim", 11.5,
                          s["sub"], "sans", 400, max_w=272))
    parts.append(svg_text(776, 362, "2 clauses · verbatim + binding + no hedge",
                          11.5, s["sub"], "sans", 400, max_w=272))
    parts.append(svg_text(776, 382, "TRQ-HDR-006…011 · TRQ-REJ-002/003", 11,
                          s["faint"], "mono", 400, max_w=272))

    parts.append(rrect(760, 412, 304, 100, 18, s["card"], s["edge"], 1.4,
                       True))
    parts.append(svg_text(776, 436, "B 待确认", 15, s["text"], "sans", 700,
                          max_w=140))
    parts.append(svg_text(1048, 438, "2", 26, s["faint"], "mono", 700,
                          anchor="end", max_w=40))
    parts.append(svg_text(776, 460, "verbatim, but no section anchor", 11.5,
                          s["sub"], "sans", 400, max_w=272))
    parts.append(svg_text(776, 482, "TRQ-REJ-001 · TRQ-REJ-004", 11,
                          s["faint"], "mono", 400, max_w=272))

    parts.append(svg_text(776, 530,
                          "out · markdown · resultJson · requirementsPack",
                          11, s["faint"], "mono", 400, max_w=288))

    # ---- coverage ribbon ----------------------------------------------------
    parts.append(rrect(36, 548, 1028, 88, 18, s["card"], s["edge"], 1.4,
                       True))
    parts.append(svg_text(52, 570, "COVERAGE · COV-01…10", 12, s["text"],
                          "sans", 700, max_w=180))
    parts.append(svg_text(52, 590, "6 hit · 4 miss", 11, s["ok"], "sans", 700,
                          max_w=180))
    parts.append(svg_text(52, 608, "miss ≠ absent", 11, s["mark"], "sans",
                          700, max_w=180))

    misses = {"COV-04", "COV-07", "COV-08", "COV-10"}
    for i in range(10):
        cid = f"COV-{i + 1:02d}"
        x = 240 + i * 82
        miss = cid in misses
        fill = s["mark_bg"] if miss else s["ok_bg"]
        stroke = s["mark"] if miss else s["ok"]
        parts.append(rrect(x, 558, 74, 40, 10, fill, stroke, 1.1))
        parts.append(svg_text(x + 37, 574, cid, 11,
                              s["mark"] if miss else s["ok"], "mono", 700,
                              anchor="middle", max_w=62))
        parts.append(svg_text(x + 37, 590, "miss" if miss else "hit", 11,
                              s["mark"] if miss else s["ok"], "sans", 600,
                              anchor="middle", max_w=62))

    parts.append(svg_text(
        240, 620,
        "COV-04 / 07 / 08 / 10 not retrieved — retrieval, not legal "
        "completeness", 11, s["faint"], "sans", 400, max_w=780))
    parts.append(svg_text(1064, 620, "no verdict", 11, s["faint"], "sans",
                          700, anchor="end", max_w=90))
    parts.append('</svg>')

    target = os.path.join(OUT, f"{NAME}-flow-v5-{skin}.svg")
    with open(target, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(parts) + "\n")
    print(f"wrote {os.path.relpath(target, ROOT)}")


def main() -> None:
    for skin in ("light", "dark"):
        for lang in ("zh", "en"):
            hero(lang, skin)
    for skin in ("light", "dark"):
        flow(skin)
    print("4 hero WebP + 2 flow SVG written to docs/assets/")


if __name__ == "__main__":
    main()
