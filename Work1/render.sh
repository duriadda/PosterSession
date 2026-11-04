#!/bin/bash
# poster.html → poster.pdf (A0) + 미리보기 PNG
cd "$(dirname "$0")"
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
"$CHROME" --headless=new --disable-gpu --no-pdf-header-footer \
  --print-to-pdf=poster.pdf "file://$PWD/poster.html"
# 미리보기: 841mm × 1189mm 를 96dpi 기준 픽셀로 (≈3179 × 4494)
"$CHROME" --headless=new --disable-gpu --hide-scrollbars \
  --window-size=3179,4494 --screenshot=preview.png "file://$PWD/poster.html"
