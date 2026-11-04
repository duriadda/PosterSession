"""
build_pptx.py
=============
PosterPresentations Lockwood A0 템플릿에 포스터 내용을 채워 poster.pptx 를 만든다.

[구성] 템플릿의 좌·우 두 패널을 그대로 쓰고, 섹션 헤더 위치만 내용에 맞게 다시 잡는다.
  왼쪽  : OVERVIEW → GOALS → RESULTS ① (Work A, 승환 Intent Caching)
  오른쪽: RESULTS ② (Work B, KV Caching) → CONCLUSIONS → FUTURE WORK → REFERENCES → CONTACT

  템플릿 플레이스홀더(제목·저자·소속, 헤더 5개, 본문 5개)는 그대로 쓰고,
  템플릿에 없는 헤더·본문·그림·상자는 같은 스타일의 일반 도형으로 추가한다.

실행: ~/Desktop/연구실/논문작성/시뮬레이션/.venv/bin/python build_pptx.py
      (Pillow 필요. 먼저 make_figs.py 로 figs/*.png 를 만들어 둘 것)
"""

import os
import shutil
import tempfile
import zipfile
from xml.sax.saxutils import escape

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(HERE, "..", "PosterPresentations.com-A0-Template-Lockwood.pptx")
OUT = os.path.join(HERE, "poster.pptx")
FIGS = os.path.join(HERE, "figs")

MM = 36000                      # 1 mm = 36000 EMU
NAVY = '<a:schemeClr val="accent5"><a:lumMod val="50000"/></a:schemeClr>'   # 템플릿 글자색
P1, P2, TODO = "2A78D6", "EB6834", "C0392B"

# 템플릿 패널 좌표 (mm)
LX, RX, CW = 18, 426, 397

_id = [400]


def nid():
    _id[0] += 1
    return _id[0]


# ── 텍스트 ────────────────────────────────────────────────────────────
def run(text, b=False, color=None, sz=None, font=None, i=False):
    attrs = 'lang="en-US"'
    if sz:
        attrs += ' sz="%d"' % (sz * 100)
    if b:
        attrs += ' b="1"'
    if i:
        attrs += ' i="1"'
    fill = '<a:solidFill><a:srgbClr val="%s"/></a:solidFill>' % color if color else ""
    face = ('<a:latin typeface="%s"/><a:cs typeface="%s"/>' % (font, font)) if font else ""
    sp = ' xml:space="preserve"' if text != text.strip() else ""
    return '<a:r><a:rPr %s dirty="0">%s%s</a:rPr><a:t%s>%s</a:t></a:r>' % (attrs, fill, face, sp, escape(text))


def para(runs, bullet=False, align=None, after=6, sz=None, font=None):
    """runs: 문자열 또는 (text, opts) 목록. 글머리표는 템플릿 기본이 buNone 이라 직접 지정."""
    ppr = ' algn="%s"' % align if align else ""
    if bullet:
        ppr += ' marL="457200" indent="-342900"'
        bu = '<a:buFont typeface="Arial"/><a:buChar char="&#8226;"/>'
    else:
        ppr += ' marL="0" indent="0"'
        bu = "<a:buNone/>"
    body = ""
    for r in runs:
        if isinstance(r, str):
            r = (r, {})
        o = dict(r[1])
        o.setdefault("sz", sz)
        o.setdefault("font", font)
        body += run(r[0], **o)
    return '<a:p><a:pPr%s><a:spcAft><a:spcPts val="%d"/></a:spcAft>%s</a:pPr>%s</a:p>' % (
        ppr, after * 100, bu, body)


def xfrm(x, y, w, h):
    return '<a:xfrm><a:off x="%d" y="%d"/><a:ext cx="%d" cy="%d"/></a:xfrm>' % (
        x * MM, y * MM, w * MM, h * MM)


def ph(idx, x, y, w, h, paras, autofit=True):
    """템플릿 플레이스홀더를 위치만 바꿔 채운다 (서식은 레이아웃에서 상속)."""
    i = nid()
    fit = "" if autofit else "<a:normAutofit/>"
    return ('<p:sp><p:nvSpPr><p:cNvPr id="%d" name="Placeholder %d"/><p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr>'
            '<p:nvPr><p:ph type="body" sz="quarter" idx="%d"/></p:nvPr></p:nvSpPr>'
            '<p:spPr>%s</p:spPr><p:txBody><a:bodyPr>%s</a:bodyPr><a:lstStyle/>%s</p:txBody></p:sp>') % (
        i, i, idx, xfrm(x, y, w, h), fit, "".join(paras))


def textbox(x, y, w, h, paras, name="Text", inset=6.2, anchor="t"):
    i = nid()
    ins = int(inset * MM)
    return ('<p:sp><p:nvSpPr><p:cNvPr id="%d" name="%s %d"/><p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr>'
            '<p:spPr>%s<a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:noFill/></p:spPr>'
            '<p:txBody><a:bodyPr wrap="square" lIns="%d" tIns="%d" rIns="%d" bIns="%d" anchor="%s"><a:noAutofit/></a:bodyPr>'
            '<a:lstStyle/>%s</p:txBody></p:sp>') % (i, name, i, xfrm(x, y, w, h), ins, ins, ins, ins, anchor, "".join(paras))


# 템플릿 헤더 스타일(39pt, 굵게, 밑줄, 가운데, 남색)을 일반 도형으로 재현
def header_box(x, y, text):
    i = nid()
    return ('<p:sp><p:nvSpPr><p:cNvPr id="%d" name="Section Header %d"/><p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr>'
            '<p:spPr>%s<a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:noFill/></p:spPr>'
            '<p:txBody><a:bodyPr wrap="square" lIns="89551" tIns="89551" rIns="89551" bIns="89551" anchor="ctr"><a:noAutofit/></a:bodyPr>'
            '<a:lstStyle/><a:p><a:pPr algn="ctr"><a:buNone/></a:pPr><a:r><a:rPr lang="en-US" sz="3900" b="1" u="sng" dirty="0">'
            '<a:solidFill>%s</a:solidFill></a:rPr><a:t>%s</a:t></a:r></a:p></p:txBody></p:sp>') % (
        i, i, xfrm(x, y, CW, 22), NAVY, escape(text))


def body_box(x, y, w, h, paras):
    """템플릿 본문(Times New Roman 28pt, 남색)과 같은 스타일의 일반 텍스트 상자."""
    return textbox(x, y, w, h, paras, name="Body")


def shape(x, y, w, h, paras, fill="F4F6F8", line=None, dash=False, geom="roundRect", name="Box", inset=3):
    i = nid()
    ln = ('<a:ln w="38100"><a:solidFill><a:srgbClr val="%s"/></a:solidFill>%s</a:ln>' % (
        line, '<a:prstDash val="dash"/>' if dash else "")) if line else "<a:ln><a:noFill/></a:ln>"
    fl = '<a:solidFill><a:srgbClr val="%s"/></a:solidFill>' % fill if fill else "<a:noFill/>"
    adj = '<a:gd name="adj" fmla="val 8000"/>' if geom == "roundRect" else ""
    ins = int(inset * MM)
    return ('<p:sp><p:nvSpPr><p:cNvPr id="%d" name="%s %d"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
            '<p:spPr>%s<a:prstGeom prst="%s"><a:avLst>%s</a:avLst></a:prstGeom>%s%s</p:spPr>'
            '<p:txBody><a:bodyPr wrap="square" lIns="%d" tIns="%d" rIns="%d" bIns="%d" anchor="ctr"><a:noAutofit/></a:bodyPr>'
            '<a:lstStyle/>%s</p:txBody></p:sp>') % (
        i, name, i, xfrm(x, y, w, h), geom, adj, fl, ln, ins, ins, ins, ins, "".join(paras))


# ── 그림 ──────────────────────────────────────────────────────────────
images = []      # (rId, 파일명)


def picture(fname, x, y, w, descr):
    from PIL import Image
    pw, phh = Image.open(os.path.join(FIGS, fname)).size
    h = w * phh / pw
    rid = "rIdImg%d" % (len(images) + 1)
    images.append((rid, fname))
    i = nid()
    xml = ('<p:pic><p:nvPicPr><p:cNvPr id="%d" name="Figure %d" descr="%s"/><p:cNvPicPr><a:picLocks noChangeAspect="1"/></p:cNvPicPr><p:nvPr/></p:nvPicPr>'
           '<p:blipFill><a:blip r:embed="%s"/><a:stretch><a:fillRect/></a:stretch></p:blipFill>'
           '<p:spPr><a:xfrm><a:off x="%d" y="%d"/><a:ext cx="%d" cy="%d"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></p:spPr></p:pic>') % (
        i, i, escape(descr), rid, int(x * MM), int(y * MM), int(w * MM), int(h * MM))
    return xml, h


# ── 내용 ──────────────────────────────────────────────────────────────
def build_shapes():
    S = []
    B = lambda t: (t, {"b": True})                       # noqa: E731
    C1 = lambda t: (t, {"b": True, "color": P1})         # noqa: E731
    C2 = lambda t: (t, {"b": True, "color": P2})         # noqa: E731
    T = lambda t: (t, {"b": True, "color": TODO})        # noqa: E731
    cap = dict(sz=22, after=0)

    # 제목·저자·소속
    S.append(ph(153, 114, 24, 614, 72, [para(["Keep the Right Things Close: Smarter Caching for AI Services at the Network Edge"], align="ctr", sz=80, after=0)], autofit=False))
    S.append(ph(151, 114, 98, 614, 26, [para([T("[TODO] Author 1, Seunghwan [surname], Advisor")], align="ctr", sz=50, after=0)], autofit=False))
    S.append(ph(150, 114, 126, 614, 24, [para([T("[TODO] Lab name, Dept. of ___, Jeonbuk National University")], align="ctr", sz=40, after=0)], autofit=False))

    # ── 왼쪽 패널 ──
    S.append(ph(11, LX, 186, CW, 22, [para(["OVERVIEW"], align="ctr", after=0)]))
    S.append(ph(10, LX, 206, CW, 104, [
        para(["AI services such as translation, chatbots and weather Q&A run on powerful servers in a distant ",
              B("cloud"), ". Every request travels there and waits for the model to compute an answer."]),
        para(["Many requests are ", B("repeats"), ". If a copy of the answer, or of work already done, is kept on a small ",
              B("edge server"), " near the user, the next person gets it much faster."]),
        para(["But edge servers are ", B("small"), ". The real question is: ", B("what should we keep, and where?"),
              " Keeping only \"the most popular\" items is not enough, because items differ in how much time they save and how much memory they take."], after=0),
    ]))
    xml, h = picture("fig_system.png", LX + (CW - 270) / 2, 312, 270, "Users connect to nearby edge servers, which connect to a distant cloud")
    S.append(xml)

    S.append(ph(20, LX, 482, CW, 22, [para(["GOALS"], align="ctr", after=0)]))
    S.append(ph(96, LX, 502, CW, 100, [
        para([C1("Work A · "), B("Which AI results go on which edge server?"),
              " Spread finished answers over several edge servers to minimise the average delay, accounting for distance and how costly each answer is to recompute."], bullet=True),
        para([C2("Work B · "), B("Which LLM work is worth the memory?"),
              " Cache the model's intermediate work (KV cache) for shared prompt beginnings, choosing items that give the most saving per unit of GPU memory."], bullet=True, after=0),
    ]))

    S.append(header_box(LX, 596, "RESULTS ①  ·  WORK A: WHERE TO PLACE RESULTS"))
    S.append(body_box(LX, 616, CW, 80, [
        para([B("Key idea. "), "A cheap answer (Weather, compute 1) is not worth a far server: the cloud is faster (2+2+1 = 5 < 7). "
              "An expensive one (Translation, 18) is: a far server (7) still beats the cloud (2+2+18 = 22)."], sz=28, font="Times New Roman", after=4),
        para([B("Baseline: "), "popular items, spread round-robin"], bullet=True, sz=26, font="Times New Roman", after=0),
        para([C1("Full MG: "), "each step, place the item–server pair that cuts delay the most"], bullet=True, sz=26, font="Times New Roman", after=0),
        para([C2("DW: "), "same rule, but only on the server whose turn it is (demand-weighted)"], bullet=True, sz=26, font="Times New Roman", after=0),
    ]))
    kw = (CW - 12 - 2 * 6) / 3
    for k, (v, lab, col) in enumerate([("~20%", "lower delay than Baseline (Full MG)", P1),
                                       ("< 1%", "average gap to the true optimum (MILP)", "1B1F24"),
                                       ("< ½", "compute (DW-distance), only 1–2% loss", P2)]):
        S.append(shape(LX + 6 + k * (kw + 6), 700, kw, 44, [
            para([(v, {"b": True, "color": col, "sz": 54})], align="ctr", after=0),
            para([(lab, {"color": "5D6670", "sz": 20})], align="ctr", after=0)], name="KPI"))
    S.append(shape(LX + 13, 752, CW - 26, 150, [
        para([T("[TODO] Insert poster_figs/fig1_improvement_vs_R")], align="ctr", sz=28, after=4),
        para([("Improvement over Baseline vs. number of users R  ·  Full MG best in all 60 settings (19.9–23.0% at N = 50)", {"color": "5D6670"})], align="ctr", sz=22, after=0)],
        fill=None, line=TODO, dash=True, name="Figure Placeholder"))
    xml, h = picture("fig_intent_density.png", LX + 13, 908, CW - 26, "Average delay for four user-density and capacity scenarios")
    S.append(xml)
    S.append(body_box(LX, 908 + h, CW, 40, [
        para(["Realistic case (N = 50, R = 30, users clustered 20:30:50): giving more cache to the busier server (3/5/7) gives the lowest delay; the opposite (7/5/3) is worst."], **cap)]))

    # ── 오른쪽 패널 ──
    S.append(ph(25, RX, 186, CW, 22, [para(["RESULTS ②  ·  WORK B: WHAT TO CACHE"], align="ctr", after=0)]))
    S.append(ph(26, RX, 206, CW, 112, [
        para([B("Key idea. "), "An edge GPU runs many models and precisions side by side. Two prompt prefixes of the same length can cost the ",
              B("same compute"), " but use up to ", B("9× (model) and 4× (precision) different memory"), "."], after=4),
        para([B("Baseline: "), "most popular first"], bullet=True, sz=26, after=0),
        para([C1("Proposed #1: "), "popular × costly to compute"], bullet=True, sz=26, after=0),
        para([C2("Proposed #2: "), "(popular × costly) ÷ memory used"], bullet=True, sz=26, after=0),
    ]))
    xml, h = picture("fig_kv_vs_baseline.png", RX + 13, 318, CW - 26, "Improvement over Baseline for Proposed 1 and 2")
    S.append(xml)
    y = 318 + h
    S.append(body_box(RX, y, CW, 30, [para(["20 prefixes, keep top 5, median of 50 random setups. #1 cuts delay most but uses ~1.5× memory; #2 uses less memory and saves 85% more per unit of memory."], **cap)]))
    y += 30
    xml, h = picture("fig_kv_heatmap.png", RX + 13, y, CW - 26, "Saving per unit memory of Proposed 2 over Proposed 1")
    S.append(xml)
    y += h
    S.append(body_box(RX, y, CW, 30, [para(["Saving per unit memory, #2 vs. #1 (median; wins out of 50; hatched = under 40 wins). With 100 prefixes and 20% kept: +87% (50/50), and still 10.7% faster than Baseline (49/50)."], **cap)]))

    S.append(header_box(RX, 708, "CONCLUSIONS"))
    S.append(body_box(RX, 728, CW, 62, [
        para(["\"Most popular first\" leaves a lot on the table at the edge."], bullet=True, sz=28, font="Times New Roman", after=2),
        para([C1("Work A: "), "cost- and distance-aware placement cuts delay by ~20%, within 1% of optimal."], bullet=True, sz=28, font="Times New Roman", after=2),
        para([C2("Work B: "), "need speed → #1; short on GPU memory → #2 (+85% saving per unit memory)."], bullet=True, sz=28, font="Times New Roman", after=0),
    ]))

    S.append(header_box(RX, 792, "FUTURE WORK"))
    S.append(body_box(RX, 812, CW, 58, [
        para(["More edge servers (5, 10) and requests that change over time"], bullet=True, sz=28, font="Times New Roman", after=2),
        para(["Profile real compute and memory costs on GPU serving engines"], bullet=True, sz=28, font="Times New Roman", after=0),
    ]))

    S.append(ph(27, RX, 876, CW, 22, [para(["REFERENCES"], align="ctr", after=0)]))
    refs = [
        "K. Shanmugam et al., \"FemtoCaching,\" IEEE Trans. Inf. Theory, 2013.",
        "Z. Qu et al., \"TrimCaching,\" IEEE ICDCS, 2024.",
        "L. Breslau et al., \"Web caching and Zipf-like distributions,\" IEEE INFOCOM, 1999.",
        "J. Wang et al., \"KVCache Cache in the Wild,\" USENIX ATC, 2025.",
        "L. Yang, Z. Liu, \"Spatial Prefix Caching for Wireless Edge LLM Inference.\"",
    ]
    S.append(ph(28, RX, 896, CW, 70, [para(["[%d] %s" % (k + 1, r)], sz=22, after=2) for k, r in enumerate(refs)]))

    S.append(ph(29, RX, 972, CW, 22, [para(["CONTACT"], align="ctr", after=0)]))
    S.append(shape(RX + 16, 1000, 130, 130, [para([T("[TODO]")], align="ctr", sz=26, after=0),
                                            para([("Lab website QR", {"color": TODO})], align="ctr", sz=22, after=0)],
                   fill=None, line=TODO, dash=True, geom="rect", name="QR Placeholder"))
    S.append(ph(30, RX + 152, 1020, CW - 157, 100, [
        para([B("Scan to visit our lab")], after=6),
        para([T("[TODO] Lab name")], after=2),
        para([T("[TODO] https://lab-website")], after=2),
        para([T("[TODO] email@jbnu.ac.kr")], after=0),
    ]))
    return S


SLIDE_HEAD = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
              '<p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
              'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
              'xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"><p:cSld><p:spTree>'
              '<p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>'
              '<p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>')
SLIDE_TAIL = '</p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sld>'


def main():
    shapes = build_shapes()
    tmp = tempfile.mkdtemp()
    with zipfile.ZipFile(TEMPLATE) as z:
        z.extractall(tmp)

    with open(os.path.join(tmp, "ppt", "slides", "slide1.xml"), "w", encoding="utf-8") as f:
        f.write(SLIDE_HEAD + "".join(shapes) + SLIDE_TAIL)

    rels_path = os.path.join(tmp, "ppt", "slides", "_rels", "slide1.xml.rels")
    rels = open(rels_path, encoding="utf-8").read()
    extra = ""
    for rid, fname in images:
        shutil.copy(os.path.join(FIGS, fname), os.path.join(tmp, "ppt", "media", "poster_" + fname))
        extra += ('<Relationship Id="%s" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" '
                  'Target="../media/poster_%s"/>') % (rid, fname)
    with open(rels_path, "w", encoding="utf-8") as f:
        f.write(rels.replace("</Relationships>", extra + "</Relationships>"))

    if os.path.exists(OUT):
        os.remove(OUT)
    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
        # [Content_Types].xml 을 맨 앞에 둔다
        z.write(os.path.join(tmp, "[Content_Types].xml"), "[Content_Types].xml")
        for root, _, files in os.walk(tmp):
            for fn in files:
                full = os.path.join(root, fn)
                arc = os.path.relpath(full, tmp)
                if arc != "[Content_Types].xml":
                    z.write(full, arc)
    shutil.rmtree(tmp)
    print("saved", OUT)


if __name__ == "__main__":
    main()
