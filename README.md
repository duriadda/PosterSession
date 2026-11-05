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
| PPT 포스터 (템플릿 기반) | ✅ 초안 완료 — `Work1/poster.pptx` |
| HTML 포스터 (초기 시안) | ✅ 완료 — `Work1/poster.html` → `poster.pdf` |
| Work B 그래프 2종 | ✅ 기존 측정값으로 생성 |
| Work A 시나리오 비교 그래프 | ✅ txt 8절 수치로 생성 |
| Work A 결과 그래프 | ✅ 승환이 pptx 에 직접 교체 (지연 막대그래프 · 연산량 log-log, 커밋 2f5139e) |
| 저자 | ✅ Hyeonug Jang, Seunghwan Lee (영문 표기 확인 필요) |
| 로고 | ⏳ 미입력 |
| 연구실 사이트 QR | ✅ `Work1/figs/qr_lab.png` (https://sites.google.com/view/nextlab-web/) |
| 연구실 이름·연락 이메일 | ✅ NEXT Lab · jh.sung@jbnu.ac.kr |
| 소속 학과 | ✅ Dept. of IT Intelligence Information Engineering (공식 영문명 확인 필요) |

포스터에서 빨간 `[TODO]` 로 표시된 곳이 남은 입력 항목이다.

## 사용한 수치의 출처

- **Work B 막대그래프**: 객체 20개 · 상위 5개 · 시드 50개 중앙값 (`TOPK_RESULTS.md` 4절)
  - `PRESENTATION_BRIEF.md` 의 시드 30개 값(+31.9% 등)이 아니라 더 최신인 시드 50개 값을 썼다
- **Work B 히트맵**: `analysis/results/12_fine_sweep.json` (객체 수 × 캐시 비율, Proposed #2 vs #1 메모리당 절감)
- **Work A**: `승환 Intent Caching.txt` 의 seed 1~40 평균값 그대로. 시나리오 비교 그래프는 값 차이가 1~2% 라 축을 6.30 부터 시작한다(라벨에 명시)
- 참고문헌: 승환 자료 3편 + Work B 근거 논문 2편 (Zhong et al. 은 서지정보가 불완전해 제외)

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

> ⚠️ 현재 `poster.pptx` 에는 승환의 Work A 수정(커밋 2f5139e: 그래프 교체, MILP 제거, 참고문헌 정리)이
> **pptx 에 직접** 들어가 있고 `build_pptx.py` 에는 반영되어 있지 않다. 지금은 `build_pptx.py` 를 실행하지 말고
> `poster.pptx` 를 직접 고칠 것.
