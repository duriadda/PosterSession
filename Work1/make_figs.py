"""
make_figs.py
============
포스터(poster.html)에 들어가는 그림을 생성한다. 시뮬레이션은 다시 돌리지 않고
이미 정리된 측정값만 사용한다.

[출처]
  fig_kv_vs_baseline : 시뮬레이션/TOPK_RESULTS.md 4절 (객체 20개 · top-5 · 시드 50개 중앙값)
  fig_kv_heatmap     : 시뮬레이션/analysis/results/12_fine_sweep.json (8절 세밀 측정)
  fig_kv_eff_by_cache: 같은 파일의 객체 100개 행만 (11/07 포스터에서 히트맵 대신 사용)
  fig_kv_by_length   : 시뮬레이션/TOPK_RESULTS.md 3-4절 (prefix 길이 상한별, 11/09 이후 위 그림 대신 사용)
  fig_intent_density : 승환 Intent Caching.txt 8절 (N=50, R=30, Full MG 의 J)

승환 결과 ①②(fig1_improvement_vs_R, fig2_tradeoff)는 구간 값만 있어 여기서 그리지 않는다.
원본 poster_figs 를 받아 poster.html 의 자리표시자에 넣을 것.

실행: ~/Desktop/연구실/논문작성/시뮬레이션/.venv/bin/python make_figs.py
그림의 축·범례 라벨은 영어로 둔다.
"""

import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Rectangle

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "figs")
SWEEP = os.path.expanduser("~/Desktop/연구실/논문작성/시뮬레이션/analysis/results/12_fine_sweep.json")

INK, MUTED, GRID = "#1b1f24", "#6b7480", "#e3e6ea"
C_BASE, C_P1, C_P2 = "#9aa3ad", "#2a78d6", "#eb6834"
BLUE = LinearSegmentedColormap.from_list("blue", ["#e8f1fc", "#86b6ef", "#2a78d6", "#104281"])

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 13,
    "axes.edgecolor": MUTED,
    "axes.labelcolor": INK,
    "xtick.color": INK,
    "ytick.color": INK,
    "svg.fonttype": "path",
})


def clean(ax):
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.yaxis.grid(True, color=GRID, linewidth=1)
    ax.set_axisbelow(True)


def save(fig, name):
    # HTML 포스터용 SVG + PPT 포스터용 PNG. A0 에서 360mm 폭으로 들어가므로 450dpi 로 저장(인쇄 시 ~270dpi)
    fig.savefig(os.path.join(OUT, name + ".svg"))
    fig.savefig(os.path.join(OUT, name + ".png"), dpi=450)


def fig_kv_vs_baseline():
    # Baseline 대비 개선율 (+ 가 좋음). 사용 메모리는 '절약률'이라 + 가 덜 쓴 것.
    metrics = ["Delay\nreduction", "Memory\nsaved", "Saving per\nunit memory"]
    p1 = [28.4, -47.2, -5.2]
    p2 = [8.0, 33.3, 85.3]

    # 11/09: 글자 10% 키움. poster_edit 배치(왼쪽 아래 CONTACT)에 맞춰 높이 4.4 → 3.8
    fig, ax = plt.subplots(figsize=(8.4, 3.8))
    x = range(len(metrics))
    w = 0.36
    b1 = ax.bar([i - w / 2 for i in x], p1, w, color=C_P1, label="Proposed #1  (Popularity × Compute Cost)")
    b2 = ax.bar([i + w / 2 for i in x], p2, w, color=C_P2, label="Proposed #2  ((Popularity × Compute Cost) / Memory Usage)")
    for bars in (b1, b2):
        for b in bars:
            v = b.get_height()
            ax.text(b.get_x() + b.get_width() / 2, v + (2.5 if v >= 0 else -2.5), "%+.1f%%" % v,
                    ha="center", va="bottom" if v >= 0 else "top", fontsize=13, color=INK,
                    fontweight="bold")
    ax.axhline(0, color=INK, linewidth=1.2)
    ax.set_xticks(list(x))
    ax.set_xticklabels(metrics, fontsize=14.5)
    ax.tick_params(axis="y", labelsize=14.5)
    ax.set_ylabel("Improvement over Baseline (%)", fontsize=14.5)
    ax.set_ylim(-62, 108)
    clean(ax)
    ax.legend(frameon=False, fontsize=12.5, loc="upper left")
    fig.tight_layout()
    save(fig, "fig_kv_vs_baseline")
    plt.close(fig)


def fig_kv_heatmap():
    with open(SWEEP) as f:
        d = json.load(f)
    data, n_seed = d["grid"], d["n_seed"]
    Ns = sorted({c["n_obj"] for c in data})
    fracs = sorted({c["frac"] for c in data})
    cell = {(c["n_obj"], c["frac"]): c for c in data}
    vals = [[cell[(n, fr)]["eff"] for fr in fracs] for n in Ns]
    vmax = max(max(r) for r in vals)

    fig, ax = plt.subplots(figsize=(8.4, 3.7))
    ax.imshow(vals, cmap=BLUE, vmin=0, vmax=vmax, aspect="auto")
    for i, n in enumerate(Ns):
        for j, fr in enumerate(fracs):
            c = cell[(n, fr)]
            color = "white" if c["eff"] / vmax > 0.55 else INK
            ax.text(j, i - 0.13, "%+.0f%%" % c["eff"], ha="center", va="center",
                    fontsize=12, color=color, fontweight="bold")
            ax.text(j, i + 0.25, "%d/%d" % (c["eff_win"], n_seed), ha="center", va="center",
                    fontsize=8.5, color=color, alpha=0.85)
            # 50번 중 40번 미만이면 신뢰도 낮음 → 빗금
            if c["eff_win"] < 40:
                ax.add_patch(Rectangle((j - 0.5, i - 0.5), 1, 1, fill=False, hatch="////",
                                       edgecolor=MUTED, linewidth=0, alpha=0.55))
    ax.set_xticks(range(len(fracs)))
    ax.set_xticklabels(["%d%%" % round(fr * 100) for fr in fracs])
    ax.set_yticks(range(len(Ns)))
    ax.set_yticklabels([str(n) for n in Ns])
    ax.set_xlabel("Cache size (% of prefixes kept)")
    ax.set_ylabel("Number of prefixes")
    for sp in ax.spines.values():
        sp.set_visible(False)
    fig.tight_layout()
    save(fig, "fig_kv_heatmap")
    plt.close(fig)


def fig_kv_eff_by_cache():
    # 히트맵 단순화판: 객체 100개 한 줄만 그려 "캐시 크기와 무관하게 #2 가 #1 보다 메모리당 ~80–100% 더 절감"
    # 을 바로 읽히게 한다. 0 선 = Proposed #1 수준.
    with open(SWEEP) as f:
        d = json.load(f)
    rows = sorted((c for c in d["grid"] if c["n_obj"] == 100), key=lambda c: c["frac"])
    xs = [round(c["frac"] * 100) for c in rows]
    ys = [c["eff"] for c in rows]

    # 단순화한 그림이라 높이를 줄여 결론 칸 공간을 확보
    fig, ax = plt.subplots(figsize=(8.4, 3.0))
    ax.axhline(0, color=INK, linewidth=1.2)
    ax.text(xs[-1], 4, "Proposed #1 level", ha="right", va="bottom", fontsize=11.5, color=MUTED)
    ax.fill_between(xs, 0, ys, color=C_P2, alpha=0.12, linewidth=0)
    ax.plot(xs, ys, color=C_P2, linewidth=2.5, marker="o", markersize=9,
            markeredgecolor="white", markeredgewidth=2, zorder=3)
    for x, y in zip(xs, ys):
        ax.text(x, y + 6, "+%.0f%%" % y, ha="center", va="bottom", fontsize=12.5,
                color=INK, fontweight="bold")
    ax.set_xticks(xs)
    ax.set_xticklabels(["%d%%" % x for x in xs])
    ax.set_xlabel("Cache size (% of prefixes kept)")
    ax.set_ylabel("Extra saving per unit memory,\n#2 over #1 (%)")
    ax.set_ylim(-8, 125)
    ax.set_xlim(xs[0] - 2, xs[-1] + 2)
    clean(ax)
    fig.tight_layout()
    save(fig, "fig_kv_eff_by_cache")
    plt.close(fig)


def fig_kv_by_length():
    # Proposed #2 vs #1 을 prefix 길이 상한별로: 메모리당 절감 우위는 유지되고 지연 손해는 길이와 함께 커진다.
    # 막대그래프와 같은 조건(객체 20개 · top-5 · 시드 50개 중앙값). 출처: TOPK_RESULTS.md 3-4절
    caps = [200, 500, 999, 4000, 16000]
    eff = [75.1, 75.2, 75.3, 73.9, 59.9]
    delay = [-7.6, -15.6, -25.7, -43.1, -48.1]

    fig, ax = plt.subplots(figsize=(8.4, 3.0))
    ax.axhline(0, color=INK, linewidth=1.2)
    ax.text(caps[0], 3, "Proposed #1 level", ha="left", va="bottom", fontsize=11.5, color=MUTED)
    ax.plot(caps, eff, color=C_P2, linewidth=2.5, marker="o", markersize=9,
            markeredgecolor="white", markeredgewidth=2, zorder=3, label="Saving per unit memory")
    ax.plot(caps, delay, color=MUTED, linewidth=2.5, linestyle="--", marker="o", markersize=9,
            markeredgecolor="white", markeredgewidth=2, zorder=3, label="Delay reduction")
    for x, y in zip(caps, eff):
        ax.text(x, y + 6, "+%.0f%%" % y, ha="center", va="bottom", fontsize=12.5, color=INK, fontweight="bold")
    for x, y in zip(caps, delay):
        ax.text(x, y - 6, "%.0f%%" % y, ha="center", va="top", fontsize=12.5, color=INK, fontweight="bold")
    ax.set_xscale("log")
    ax.set_xticks(caps)
    ax.set_xticklabels(["~200", "~500", "~1k", "~4k", "~16k"])
    ax.minorticks_off()
    ax.set_xlabel("Prefix length limit (tokens, log scale)")
    ax.set_ylabel("#2 vs. #1 (%)")
    ax.set_ylim(-75, 100)
    ax.set_xlim(150, 22000)
    clean(ax)
    ax.legend(frameon=False, fontsize=11.5, loc="center right", bbox_to_anchor=(1.0, 0.62))
    fig.tight_layout()
    save(fig, "fig_kv_by_length")
    plt.close(fig)


def fig_intent_density():
    # 차이가 1~2% 수준이라 0 기준 막대로는 안 보인다 → 점 그림 + 잘린 축임을 명시
    labels = ["Uniform users\n(5/5/5)", "Clustered users\n(5/5/5)",
              "Clustered +\nmatched (3/5/7)", "Clustered +\nmismatched (7/5/3)"]
    J = [6.407, 6.412, 6.345, 6.512]
    colors = [C_BASE, C_BASE, C_P1, C_P2]

    fig, ax = plt.subplots(figsize=(8.4, 3.7))
    y = list(range(len(labels)))[::-1]
    ax.hlines(y, 6.30, J, color=GRID, linewidth=3)
    ax.scatter(J, y, s=260, color=colors, zorder=3)
    for yi, v in zip(y, J):
        ax.text(v + 0.008, yi, "%.3f" % v, va="center", fontsize=13, color=INK, fontweight="bold")
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=12)
    ax.set_xlim(6.30, 6.55)
    ax.set_xlabel("Average delay J  (relative units, lower is better; axis starts at 6.30)")
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.xaxis.grid(True, color=GRID, linewidth=1)
    ax.set_axisbelow(True)
    ax.tick_params(axis="y", length=0)
    fig.tight_layout()
    save(fig, "fig_intent_density")
    plt.close(fig)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    fig_kv_vs_baseline()
    fig_kv_heatmap()
    fig_kv_eff_by_cache()
    fig_kv_by_length()
    fig_intent_density()
    print("saved to", OUT)
