# 힘내라 고에몽 ~네오 모모야마 막부의 춤~ (N64) 비공식 한글패치

N64 일본판 **がんばれゴエモン ～ネオ桃山幕府のおどり～ (힘내라 고에몽 ~네오 모모야마 막부의 춤~, NUS-NGEJ)** 비공식 한국어 패치입니다. 이 저장소에는 제작 도구와 기술 문서만 있고, 패치 파일(xdelta)은 [Releases](../../releases)에서 받을 수 있습니다. 게임 원본·일본어 원문·번역 대본은 포함하지 않습니다.


## 적용 방법
1. 아래 해시와 일치하는 **원본 `.z64`** (빅 엔디언, No-Intro 형식)를 준비합니다. (`.n64`·`.v64` 바이트 순서 파일은 먼저 `.z64`로 바꿔야 합니다.)
   - PowerShell: `Get-FileHash -Algorithm MD5 -LiteralPath '.$J'`
2. xdeltaUI 같은 도구로 원본 `.z64` 에 `Ganbare_Goemon_Neo_Momoyama_KO_v1.0.xdelta` 를 적용합니다. (Patch = xdelta, Source File = 원본 ROM, Output File = 새 파일명)
   - 명령줄: `xdelta3 -d -s "Ganbare Goemon - Neo Momoyama Bakufu no Odori (Japan).z64" Ganbare_Goemon_Neo_Momoyama_KO_v1.0.xdelta "Ganbare Goemon - Neo Momoyama Bakufu no Odori (Korean).z64"`
3. 만들어진 `.z64` 를 Project64·Mupen64Plus(BizHawk 등) N64 에뮬레이터나 플래시 카트리지에서 실행합니다.

| 항목 | 값 |
| --- | --- |
| 원본 ROM 크기 | 16,777,216 바이트 |
| 원본 ROM MD5 | `9b929e0bf8d63e62820f2fa6257cc5cf` |
| 원본 ROM SHA-256 | `a1d288fa352ef185e0499a63b64dfc937c460da15a10456f180ee71298277413` |
| xdelta SHA-256 | `4de8b8b5cd8cdfaf5010bc059c180224687754be4118d8a30bc98e171572ef31` |
| 결과 ROM 크기 | 16,777,216 바이트 |
| 결과 ROM SHA-256 | `0dd7ebb9c5401267c291bab88606741ea0478943f247753906b1937115fc394e` |

## 주의
- 원본에서 만든 **상태저장(세이브 스테이트)** 은 불러오지 마세요. 글꼴 배치가 달라 글자가 깨집니다. 컨트롤러 팩 세이브는 그대로 쓸 수 있습니다.
- 헤더 체크섬(CRC)은 다시 계산해 두었습니다.
- xdelta는 압축하지 않은 형식(`-0`)입니다(약 230KB).

## 한글화 내용
- 대사·메뉴·아이템·상점·지명 등 텍스트 약 5,400줄(42개 텍스트 파일 + 오버레이 3개) 전수 직접 번역
- 한글 글자 1,070여 자를 ROM 끝에 추가하고, 글자 출력 루틴에 **동적 글리프 캐시**(MIPS 어셈블리)를 넣어 원래 글꼴 타일 자리에 필요할 때마다 한글을 불러옴 — 크기별 뱅크 3개(본문·중간·아주 작은 글자)
- 코드가 직접 그리는 「術」「両」 타일을 「기술」「냥」으로 교체
- 그림 글자 — 타이틀·메뉴·일시정지·여행일기 등 UI 텍스처 17종 한글화(PIC 형식 재인코딩·LZKN 재압축)
- 상점 목록 가격 줄은 원문과 같은 칸 수로 맞춤
- 글꼴: 본문 나눔스퀘어 네오 Bd, 그림 글자 나눔스퀘어 네오 Bd·Eb·Hv와 갈무리11·9, 아주 작은 글자 갈무리7(원래 크기 1:1)

## 그대로 둔 것
- 음성, KONAMI 로고, 영문 표기, 마을 배경 그림 속 간판·서예 글씨(「御宿」「火の用心」 등 배경 그림)

## 검증 범위
BizHawk(N64)에서 오프닝, 고에몽의 집, 첫 마을과 주민 대사, 잡화점 메뉴와 구매 대사, 일시정지 화면의 기술·아이템 칸을 확인했습니다. 모든 텍스트 파일을 전수 검사해 번역이 빠진 줄이 없는 것을 확인했습니다. 스테이지(오에도 성) 이후와 전체 플레이 검증은 하지 않았습니다. 문제를 발견하면 Issues에 알려 주세요.

## 문서
- [CHANGELOG.md](CHANGELOG.md) — 변경 기록
- [docs/TECHNICAL.md](docs/TECHNICAL.md) — 파일 형식과 한글화 방법
- [docs/BUILD.md](docs/BUILD.md) — 직접 빌드하는 방법
- [docs/FONT_CREDITS.md](docs/FONT_CREDITS.md) — 글꼴
- [RIGHTS.md](RIGHTS.md) — 권리 및 외부 자료
