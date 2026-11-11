# 빌드 방법

번역 대본(`work/tr/`, `work/tr_ovl/`), 한글 그림 글자(`work/tex_ko/`)와 글꼴 파일은 저장소에 없으므로, 아래는 같은 자료를 갖춘 경우의 절차입니다. 도구 안의 작업 폴더 경로(`ROOT`, `R`)는 자신의 폴더로 고쳐 쓰세요.

## 준비
- Python 3.11 이상, `pip install pillow numpy`
- 원본 `Ganbare Goemon - Neo Momoyama Bakufu no Odori (Japan).z64` (README의 해시와 일치)을 작업 폴더에 둡니다.
- 글꼴: `NanumSquareNeo-cBd.ttf`, `NanumSquareNeo-dEb.ttf`, `NanumSquareNeo-eHv.ttf`, `Galmuri11.ttf`, `Galmuri9.ttf`, `Galmuri7.ttf` 를 작업 폴더에 둡니다.

## 순서
1. 파일 풀기·원문 추출: `python tools/nisi.py work/files` → `work/ja/NNNN.json` (오버레이 문자열은 `tools/ovlx.py`)
2. 번역: `work/tr/NNNN.json` (원문 배열에 `ko` 필드 추가), 오버레이는 `work/tr_ovl/`
3. 그림 글자: `tools/texdump.py` 로 `work/tex/` 에 원본 텍스처를 뽑고 `tools/texko.py` 로 `work/tex_ko/` 생성
4. 빌드: `python tools/build.py` → `Ganbare Goemon - Neo Momoyama Bakufu no Odori (Korean).z64` (CRC 자동 갱신)
5. 차분 파일: `xdelta3 -0 -e -s "Ganbare Goemon - Neo Momoyama Bakufu no Odori (Japan).z64" "Ganbare Goemon - Neo Momoyama Bakufu no Odori (Korean).z64" Ganbare_Goemon_Neo_Momoyama_KO_v1.0.xdelta`

## 확인 도구
- `emu/bridge.lua` — BizHawk Lua 브리지(버튼·스틱 입력, 스크린샷, 메모리 덤프). `tools/emu.py`, `tools/go.py`, `tools/walk.py`, `tools/seq.py` 가 이 브리지를 씁니다.
- `tools/check.py` — 태그 개수·줄 길이·쓸 수 없는 문자 검사
