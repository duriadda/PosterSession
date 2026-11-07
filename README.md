# 연구실 포스터 세션 (2026년 11월)

두 연구를 묶어 **네트워크 분야를 모르는 사람도 이해할 수 있는** A0 한 장짜리 포스터를 만든다.

| 구분 | 연구 | 자료 |
|---|---|---|
| Work A | 엣지 서버 여러 대에 추론 결과를 배치 (Intent Caching, 승환) | `승환 Intent Caching.txt` |
| Work B | 엣지 LLM Prefix KV 캐싱 (본인) | `~/Desktop/연구실/논문작성/시뮬레이션` (README·PROGRESS·TOPK_RESULTS) |

## 포스터 구성

- 형식: **A0 세로 한 장**, 영어. 템플릿은 `PosterPresentations.com-A0-Template-Lockwood.pptx`
- 왼쪽 패널: Overview → Goals → Results ① (Work A)
- 오른쪽 패널: Results ② (Work B) → Conclusions → Future Work → References → Contact(연구실 QR)
- 각 Results 칸에 실험 그래프를 넣는다

## 현재 상태

| 항목 | 상태 |
|---|---|
| PPT 포스터 (템플릿 기반) | ✅ 교수님 피드백 1~7번·기타 반영 완료 — `Work1/poster.pptx` |
| HTML 포스터 (초기 시안) | ✅ 완료 — `Work1/poster.html` → `poster.pdf` (피드백 미반영, 참고용) |
| Work A 결과 그래프 | ✅ 승환이 pptx 에 직접 교체 (지연 막대그래프 · 연산량 log-log) |
| Work B 그래프 | ✅ 막대그래프 + 히트맵을 단순화한 꺾은선(`fig_kv_eff_by_cache`) |
| 저자·소속 | ✅ Hyeon Uk Jang, Seung Hwan Lee, and Ji Hoon Sung (Advisor) · NEXT Lab, Dept. of IT Intelligence Information Engineering |
| 연구실 사이트 QR·연락처 | ✅ `Work1/figs/qr_lab.png` · jh.sung@jbnu.ac.kr |
| 템플릿 QUICK START GUIDE | ✅ 슬라이드 마스터에서 삭제 |
| 로고 | ⏳ 미입력 (필요 시) |

### A0 크기 점검 (1189 × 841 mm, 1~2 m 거리 기준)

| 요소 | 크기 | 판단 |
|---|---|---|
| 제목 / 저자 / 소속 | 80 / 50 / 40 pt | 충분 |
| 섹션 헤더 · 본문 | 39 · 35~38 pt | 충분 (A0 권장 본문 ≥ 24~32 pt) |
| 캡션 · 참고문헌 | 30 pt | 적당 |
| KPI 숫자 / 설명 | 60 / 26 pt | 설명은 22 → 26 pt 로 키움 |
| 그래프 내부 글자 | Work B ≈ 19~22 pt, Work A(승환) ≈ 17~18 pt | 가장 작음. 읽을 수는 있으나 원본 그림을 다시 뽑을 수 있다면 Work A 축·범례를 키우는 것을 권장 |
| 그림 해상도 (인쇄 기준) | Work B 270 dpi, Work A 310 dpi, 시스템 그림 210 dpi, QR 390 dpi | 모두 A0 인쇄에 충분 (≥ 150 dpi) |

## 사용한 수치의 출처

- **Work B 막대그래프**: 객체 20개 · 상위 5개 · 시드 50개 중앙값 (`TOPK_RESULTS.md` 4절)
  - `PRESENTATION_BRIEF.md` 의 시드 30개 값(+31.9% 등)이 아니라 더 최신인 시드 50개 값을 썼다
- **Work B 꺾은선 그래프**: `analysis/results/12_fine_sweep.json` 의 객체 100개 행 (캐시 비율별 Proposed #2 vs #1 메모리당 절감). 같은 파일 전체로 그린 히트맵은 HTML 시안에만 남아 있다
- **Work A**: `승환 Intent Caching.txt` 의 seed 1~40 평균값 그대로. 시나리오 비교 그래프는 값 차이가 1~2% 라 축을 6.30 부터 시작한다(라벨에 명시)
- 참고문헌 4편: Wang et al. (ATC'25), Regmi & Pun (arXiv'24), Tian et al. (ATC'25), Gao et al. (INFOCOM'25 — `논문작성/참고논문/` PDF 로 서지 확인)

## 파일 구성

```
포스터세션/
├── README.md
├── PosterPresentations.com-A0-Template-Lockwood.pptx   포스터 템플릿
├── 승환 Intent Caching.txt                              Work A 내용 정리
└── Work1/
    ├── poster.pptx      ★ 최종 작업본 (템플릿 기반)
    ├── build_pptx.py    템플릿에 내용·그림을 채워 poster.pptx 생성
    ├── make_figs.py     그래프 생성 (figs/*.svg, *.png)
    ├── figs/            그래프 + 시스템 그림
    ├── poster.html      HTML 시안
    ├── render.sh        poster.html → poster.pdf, preview.png
    └── poster.pdf, preview.png
```

## 다시 만들기

```bash
cd Work1
~/Desktop/연구실/논문작성/시뮬레이션/.venv/bin/python make_figs.py   # 그래프
~/Desktop/연구실/논문작성/시뮬레이션/.venv/bin/python build_pptx.py  # poster.pptx
```

`build_pptx.py` 를 다시 실행하면 `poster.pptx` 를 **덮어쓴다**. PowerPoint 에서 직접 고친 내용이
있다면 먼저 다른 이름으로 저장해 둘 것.

> ⚠️ 현재 `poster.pptx` 에는 승환의 Work A 수정, 교수님 피드백 반영, QUICK START GUIDE 삭제가
> **pptx 에 직접** 들어가 있고 `build_pptx.py` 에는 반영되어 있지 않다. `build_pptx.py` 는 실행하지 말고
> `poster.pptx` 를 직접 고칠 것. 그래프를 다시 뽑았다면 pptx 안의 해당 그림만 바꿔 끼운다.


## 교수님 피드백

### 1. 전체 구성 및 저자 정보
- 포스터 좌우에 표시되는 **QUICK START GUIDE**는 뭔지?
- 상단 이름에 and Jihoon Sung (Advisor) 추가

### 2. Overview
- Network for AI라는 키워드가 드러나도록 도입부 문장을 다음과 같이 수정하면 좋을 듯
  > Network for AI aims to make AI services faster and more efficient through network and edge resources. Many AI services, such as translation and chatbots, rely on powerful cloud servers, leading to long response times.

- 그림에서 두 연구의 캐싱 대상이 명확히 드러나도록 수정
  - Work A: Inference-Result Cache
  - Work B: Prefix KV Cache
- 현재 'AI Model'과 'Cache' 표기만으로는 무엇을 캐싱하는지 불분명하고, AI 모델 자체를 캐싱하는 것으로 오해할 소지도 있어, 오해소지 없도록 수정 필요
- 'Cache hit → fast' 문구가 화살표와 겹쳐 있어 오해의 소지가 있으므로 위치 조정
- Work A와 Work B를 간략히 소개하는 부분에도 각각 Inference-Result Caching, Prefix KV Caching이라는 키워드가 드러나도록 수정

### 3. RESULT: Work A – Inference-Result Caching
- Key Idea 설명에서 'Weather', 'Translation' 앞에 각각 e.g., 추가
- '60 / 60 settings: Full MG lowest' → 이게 무슨 의미인지 모호하여 수정 필요
- '< ½ compute (DW), ≤ 2.2% loss' → '2.2% loss'가 어떤 성능 지표를 기준으로 한 것인지 명확히 설명할 필요가 있음

### 4. Work B – Prefix KV Caching
- 두 제안 기법이 모두 모든 지표에서 우수하다는 식으로 설명하기보다는, 서로 다른 성능–메모리 trade-off를 제공한다는 점이 드러나도록 수정하면 좋겠음
- 제안 기법 설명에서 'costly'라는 표현은 다소 모호하므로 다음과 같이 수정하는 것을 추천
  - Proposed #1: Popularity × Compute Cost
  - Proposed #2: (Popularity × Compute Cost) / Memory Usage
- 마지막 히트맵은 정보가 많아 처음 보는 사람이 해석하기 어려울 듯함. 그래프를 좀 더 단순화하거나, 핵심 결과가 직관적으로 드러나도록 수정하면 좋겠음
- 특히 다음 설명이 무엇을 의미하는지 명확하지 않음
  > Saving per unit memory, #2 vs. #1 (median, wins/50; hatched < 40). 100 prefixes, 20% kept: +87% (50/50)

### 5. Conclusions
- 'Work B: speed → #1; short on memory → #2 (+85% per memory).'
  - '+85% per memory'는 무엇이 85% 개선되었다는 것인지 모호함
  - 단위 메모리당 절감 효과를 의미한다면, 해당 지표와 비교 기준이 명확히 드러나도록 수정

### 6. Future Work
- 첫 번째 항목을 다음과 같이 수정
  - More edge servers (5, 10), changing requests -> Larger edge networks and dynamic request patterns
- 다음 항목 신규 추가.
  - RL(Reinforcement Learning)-based adaptive cache placement
- 기존 GPU profiling 관련 항목은 유지.

### 7. References
- 현재 References가 미완성인 것 같은데, 이전에 각자 살펴보라고 했던 관련 논문을 중심으로 2편 정도 추가하면 좋겠음



### 기타

- 내용적인 부분과 무관하게 A0 사이즈를 고려할 때 폰트 크기나 그림 크기 등 적절한지도 가능하다면 툴 등을 활용해서 확인해보면 좋을 것 같음
===============================