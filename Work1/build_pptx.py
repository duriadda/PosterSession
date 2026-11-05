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
LAB_NAME = "NEXT Lab"
LAB_URL = "https://sites.google.com/view/nextlab-web/"
LAB_EMAIL = "jh.sung@jbnu.ac.kr"

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
# 글자 크기 (pt). 템플릿 기본 28pt 대비 1.35배로 키웠고, 캡션·참고문헌도 같은 비율.
SCALE = 1.35
BODY = round(28 * SCALE)        # 본문
LIST = round(26 * SCALE)        # 방법 목록
CAP = round(22 * SCALE)         # 그림 캡션
REF = round(22 * SCALE)         # 참고문헌
GAP = 6                         # 블록 사이 간격 (mm)
FIG_W = 360                     # 결과 그림 폭 (mm)


def est_h(specs, w):
    """본문 상자 높이(mm) 추정 — Times New Roman 평균 글자폭 ≈ 0.45em, 줄간격 1.2."""
    import math
    h = 2 * 6.2
    for sp in specs:
        text = "".join(r if isinstance(r, str) else r[0] for r in sp["runs"])
        sz = sp.get("sz", BODY)
        usable = w - 12.4 - (12.7 if sp.get("bullet") else 0)
        per_line = usable / (sz * 0.3528 * 0.45)
        lines = max(1, math.ceil(len(text) / per_line))
        h += lines * sz * 1.2 * 0.3528 + sp.get("after", 6) * 0.3528
    return h


def block(x, y, w, specs, idx=None):
    """본문 블록. idx 가 있으면 템플릿 플레이스홀더, 없으면 같은 스타일의 일반 상자. (xml, 높이) 반환."""
    h = est_h(specs, w)
    paras = []
    for sp in specs:
        o = {k: v for k, v in sp.items() if k != "runs"}
        o.setdefault("sz", BODY)
        if idx is None:
            o.setdefault("font", "Times New Roman")
        paras.append(para(sp["runs"], **o))
    xml = ph(idx, x, y, w, h, paras) if idx is not None else body_box(x, y, w, h, paras)
    return xml, h


def build_shapes():
    S = []
    B = lambda t: (t, {"b": True})                       # noqa: E731
    C1 = lambda t: (t, {"b": True, "color": P1})         # noqa: E731
    C2 = lambda t: (t, {"b": True, "color": P2})         # noqa: E731
    T = lambda t: (t, {"b": True, "color": TODO})        # noqa: E731
    fx = lambda X: X + (CW - FIG_W) / 2                  # noqa: E731  그림 가운데 정렬

    def add(item):
        xml, h = item
        S.append(xml)
        return h

    # 제목·저자·소속
    S.append(ph(153, 114, 24, 614, 72, [para(["Keep the Right Things Close: Smarter Caching for AI Services at the Network Edge"], align="ctr", sz=80, after=0)], autofit=False))
    S.append(ph(151, 114, 98, 614, 26, [para([T("[TODO] Author 1, Seunghwan [surname], Advisor")], align="ctr", sz=50, after=0)], autofit=False))
    S.append(ph(150, 114, 126, 614, 24, [para([LAB_NAME + ", ", T("[TODO] Dept. of ___"), ", Jeonbuk National University"], align="ctr", sz=40, after=0)], autofit=False))

    # ── 왼쪽 패널 ──
    y = 186
    S.append(ph(11, LX, y, CW, 22, [para(["OVERVIEW"], align="ctr", after=0)]))
    y += 20
    y += add(block(LX, y, CW, [
        dict(runs=["AI services such as translation and chatbots run on powerful servers in a distant ", B("cloud"),
                   ". Every request travels there and waits for the answer."]),
        dict(runs=["Many requests are ", B("repeats"), ". Keeping a copy on a small ", B("edge server"),
                   " near the user makes the next answer much faster."]),
        dict(runs=["But edge servers are ", B("small"), ". So: ", B("what should we keep, and where?"),
                   " Popularity alone is not enough: items differ in time saved and memory used."], after=0),
    ], idx=10))
    y += add(picture("fig_system.png", LX + (CW - 250) / 2, y, 250, "Users connect to nearby edge servers, which connect to a distant cloud"))
    y += GAP
    S.append(ph(20, LX, y, CW, 22, [para(["GOALS"], align="ctr", after=0)]))
    y += 20
    y += add(block(LX, y, CW, [
        dict(runs=[C1("Work A · "), B("Which AI results go on which edge server?"),
                   " Place answers on several edge servers to minimise delay, using distance and recompute cost."], bullet=True),
        dict(runs=[C2("Work B · "), B("Which LLM work is worth the memory?"),
                   " Cache shared prompt work (KV cache) with the most saving per unit of GPU memory."], bullet=True, after=0),
    ], idx=96))
    y += GAP
    S.append(header_box(LX, y, "RESULTS ①  ·  WORK A: WHERE TO PLACE RESULTS"))
    y += 20
    y += add(block(LX, y, CW, [
        dict(runs=[B("Key idea. "), "A cheap answer (Weather, 1) is not worth a far server: the cloud is faster (2+2+1 = 5 < 7). "
                   "An expensive one (Translation, 18) is: far server 7 < cloud 2+2+18 = 22."], after=4),
        dict(runs=[B("Baseline: "), "popular items, round-robin"], bullet=True, sz=LIST, after=0),
        dict(runs=[C1("Full MG: "), "best item–server pair at each step"], bullet=True, sz=LIST, after=0),
        dict(runs=[C2("DW: "), "same rule, one server per turn (demand-weighted)"], bullet=True, sz=LIST, after=0),
    ]))
    kw = (CW - 12 - 2 * 6) / 3
    for k, (v, lab, col) in enumerate([("~20%", "lower delay than Baseline", P1),
                                       ("< 1%", "gap to the optimum (MILP)", "1B1F24"),
                                       ("< ½", "compute (DW), 1–2% loss", P2)]):
        S.append(shape(LX + 6 + k * (kw + 6), y, kw, 46, [
            para([(v, {"b": True, "color": col, "sz": round(54 * SCALE)})], align="ctr", after=0),
            para([(lab, {"color": "5D6670", "sz": round(20 * SCALE)})], align="ctr", after=0)], name="KPI"))
    y += 46 + GAP
    S.append(shape(fx(LX), y, FIG_W, 118, [
        para([T("[TODO] Insert poster_figs/fig1_improvement_vs_R")], align="ctr", sz=28, after=4),
        para([("Improvement over Baseline vs. number of users R · Full MG best in all 60 settings (19.9–23.0% at N = 50)", {"color": "5D6670"})], align="ctr", sz=22, after=0)],
        fill=None, line=TODO, dash=True, name="Figure Placeholder"))
    y += 118 + GAP / 2
    y += add(picture("fig_intent_density.png", fx(LX), y, FIG_W, "Average delay for four user-density and capacity scenarios"))
    add(block(LX, y, CW, [dict(runs=["N = 50, R = 30, users clustered 20:30:50. More cache for the busier server (3/5/7) gives the lowest delay; the opposite (7/5/3) is worst."], sz=CAP, after=0)]))

    # ── 오른쪽 패널 ──
    y = 186
    S.append(ph(25, RX, y, CW, 22, [para(["RESULTS ②  ·  WORK B: WHAT TO CACHE"], align="ctr", after=0)]))
    y += 20
    y += add(block(RX, y, CW, [
        dict(runs=[B("Key idea. "), "An edge GPU runs many models and precisions. Prefixes of the same length cost the ",
                   B("same compute"), " but use up to ", B("9× (model) and 4× (precision) more memory"), "."], after=4),
        dict(runs=[B("Baseline: "), "most popular first"], bullet=True, sz=LIST, after=0),
        dict(runs=[C1("Proposed #1: "), "popular × costly to compute"], bullet=True, sz=LIST, after=0),
        dict(runs=[C2("Proposed #2: "), "(popular × costly) ÷ memory used"], bullet=True, sz=LIST, after=0),
    ], idx=26))
    y += add(picture("fig_kv_vs_baseline.png", fx(RX), y, FIG_W, "Improvement over Baseline for Proposed 1 and 2"))
    y += add(block(RX, y, CW, [dict(runs=["20 prefixes, top 5 kept, median of 50 setups. #1 is fastest but uses ~1.5× memory; #2 saves 85% more per unit memory."], sz=CAP, after=0)]))
    y += add(picture("fig_kv_heatmap.png", fx(RX), y, FIG_W, "Saving per unit memory of Proposed 2 over Proposed 1"))
    y += add(block(RX, y, CW, [dict(runs=["Saving per unit memory, #2 vs. #1 (median, wins/50; hatched < 40). 100 prefixes, 20% kept: +87% (50/50), still 10.7% faster than Baseline."], sz=CAP, after=0)]))
    y += GAP
    S.append(header_box(RX, y, "CONCLUSIONS"))
    y += 20
    y += add(block(RX, y, CW, [
        dict(runs=["\"Most popular first\" leaves a lot on the table."], bullet=True, after=2),
        dict(runs=[C1("Work A: "), "~20% lower delay, within 1% of optimal."], bullet=True, after=2),
        dict(runs=[C2("Work B: "), "speed → #1; short on memory → #2 (+85% per memory)."], bullet=True, after=0),
    ]))
    y += GAP
    S.append(header_box(RX, y, "FUTURE WORK"))
    y += 20
    y += add(block(RX, y, CW, [
        dict(runs=["More edge servers (5, 10), changing requests"], bullet=True, after=2),
        dict(runs=["Real GPU profiling of compute and memory"], bullet=True, after=0),
    ]))
    y += GAP
    S.append(ph(27, RX, y, CW, 22, [para(["REFERENCES"], align="ctr", after=0)]))
    y += 20
    refs = [
        "K. Shanmugam et al., \"FemtoCaching,\" IEEE Trans. Inf. Theory, 2013.",
        "Z. Qu et al., \"TrimCaching,\" IEEE ICDCS, 2024.",
        "L. Breslau et al., \"Web caching and Zipf-like distributions,\" IEEE INFOCOM, 1999.",
        "J. Wang et al., \"KVCache Cache in the Wild,\" USENIX ATC, 2025.",
        "L. Yang, Z. Liu, \"Spatial Prefix Caching for Wireless Edge LLM Inference.\"",
    ]
    y += add(block(RX, y, CW, [dict(runs=["[%d] %s" % (k + 1, r)], sz=REF, after=2) for k, r in enumerate(refs)], idx=28))
    y += GAP
    S.append(ph(29, RX, y, CW, 22, [para(["CONTACT"], align="ctr", after=0)]))
    y += 24
    # QR 이미지(figs/qr_lab.png)는 연구실 사이트 URL 로 따로 생성해 둔다
    add(picture("qr_lab.png", RX + 16, y, 100, "QR code linking to " + LAB_URL))
    add(block(RX + 124, y + 4, CW - 129, [
        dict(runs=[B("Scan to visit our lab")], after=6),
        dict(runs=[LAB_NAME], after=2),
        dict(runs=[LAB_URL], after=2),
        dict(runs=[LAB_EMAIL], after=0),
    ], idx=30))
    print("bottom: right = %.0f mm (panel ends ~1155)" % (y + 100))
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
